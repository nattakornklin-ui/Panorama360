import os
import re
import uuid
import logging
from pathlib import Path

import cv2
import numpy as np
import qrcode
from flask import Flask, render_template, request, url_for, abort, flash, redirect
from werkzeug.utils import secure_filename
from werkzeug.exceptions import RequestEntityTooLarge

BASE_DIR = Path(__file__).resolve().parent
PANORAMA_DIR = BASE_DIR / "static" / "panoramas"
QR_DIR = BASE_DIR / "static" / "qr"
for directory in (PANORAMA_DIR, QR_DIR):
    directory.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png"}
MAX_FILES = 20
MAX_FILE_BYTES = 20 * 1024 * 1024
MAX_TOTAL_BYTES = 100 * 1024 * 1024

app = Flask(__name__)
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "change-this-secret-key")
app.config["MAX_CONTENT_LENGTH"] = MAX_TOTAL_BYTES
app.config["MAX_FILES"] = MAX_FILES
app.logger.setLevel(logging.INFO)


def valid_image_upload(upload):
    """Validate extension, byte size, and actual decodability."""
    safe_name = secure_filename(upload.filename or "")
    ext = Path(safe_name).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise ValueError(f"ไฟล์ {safe_name or 'ไม่ทราบชื่อ'} ไม่รองรับ")
    data = upload.read(MAX_FILE_BYTES + 1)
    upload.seek(0)
    if not data or len(data) > MAX_FILE_BYTES:
        raise ValueError(f"ไฟล์ {safe_name} ว่างหรือมีขนาดเกิน 20 MB")
    image = cv2.imdecode(np.frombuffer(data, dtype=np.uint8), cv2.IMREAD_COLOR)
    if image is None:
        raise ValueError(f"ไม่สามารถอ่านไฟล์ {safe_name} ได้")
    h, w = image.shape[:2]
    if w < 200 or h < 200:
        raise ValueError(f"ภาพ {safe_name} มีความละเอียดต่ำเกินไป")
    return image, len(data)


@app.errorhandler(RequestEntityTooLarge)
def handle_too_large(_error):
    flash("ขนาดไฟล์รวมเกิน 100 MB กรุณาลดขนาดหรือจำนวนภาพ", "error")
    return redirect(url_for("index")), 413


@app.route("/", methods=["GET", "POST"])
def index():
    result = None
    error = None
    if request.method == "POST":
        uploads = [f for f in request.files.getlist("images") if f and f.filename]
        if len(uploads) < 3:
            error = "กรุณาเลือกภาพอย่างน้อย 3 ภาพ"
        elif len(uploads) > MAX_FILES:
            error = f"เลือกภาพได้ไม่เกิน {MAX_FILES} ภาพต่อครั้ง"
        else:
            try:
                images, total_bytes = [], 0
                for upload in uploads:
                    image, size = valid_image_upload(upload)
                    total_bytes += size
                    if total_bytes > MAX_TOTAL_BYTES:
                        raise ValueError("ขนาดไฟล์รวมเกิน 100 MB")
                    images.append(image)

                # OpenCV's panorama mode works best with consecutive photos
                # that have substantial overlap and consistent exposure.
                stitcher = cv2.Stitcher_create(cv2.Stitcher_PANORAMA)
                stitcher.setPanoConfidenceThresh(0.6)
                status, panorama = stitcher.stitch(images)

                if status != cv2.Stitcher_OK or panorama is None:
                    raise ValueError(
                        "เชื่อมภาพไม่สำเร็จ กรุณาใช้ภาพที่ถ่ายต่อเนื่อง "
                        "มีส่วนซ้อนทับกันประมาณ 30–50% และหลีกเลี่ยงภาพที่สั่นหรือแตกต่างกันมาก"
                    )

                image_id = uuid.uuid4().hex
                output_path = PANORAMA_DIR / f"{image_id}.jpg"
                ok = cv2.imwrite(
                    str(output_path), panorama,
                    [cv2.IMWRITE_JPEG_QUALITY, 94]
                )
                if not ok:
                    raise RuntimeError("ไม่สามารถบันทึกภาพ Panorama ได้")

                viewer_url = url_for("view", image_id=image_id, _external=True)
                qr_path = QR_DIR / f"{image_id}.png"
                qr = qrcode.QRCode(
                    version=None, error_correction=qrcode.constants.ERROR_CORRECT_M,
                    box_size=8, border=3
                )
                qr.add_data(viewer_url)
                qr.make(fit=True)
                qr.make_image(fill_color="black", back_color="white").save(qr_path)

                result = {
                    "id": image_id,
                    "url": viewer_url,
                    "qr": url_for("static", filename=f"qr/{image_id}.png")
                }
            except ValueError as exc:
                error = str(exc)
            except Exception:
                app.logger.exception("Panorama processing failed")
                error = "เกิดข้อผิดพลาดระหว่างประมวลผล กรุณาลองใหม่อีกครั้ง"

    return render_template("index.html", result=result, error=error)


@app.route("/view/<image_id>")
def view(image_id):
    if not re.fullmatch(r"[a-f0-9]{32}", image_id):
        abort(404)
    filename = f"{image_id}.jpg"
    if not (PANORAMA_DIR / filename).is_file():
        abort(404)
    image_url = url_for("static", filename=f"panoramas/{filename}")
    return render_template("viewer.html", image_url=image_url, image_id=image_id)


@app.route("/health")
def health():
    return {"status": "ok"}, 200


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
