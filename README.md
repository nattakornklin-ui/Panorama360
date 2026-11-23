# Panorama 360 Studio

เว็บแอป Flask สำหรับอัปโหลดภาพหลายภาพ เชื่อมภาพด้วย OpenCV สร้าง QR Code และเปิดดูภาพผ่านหน้า Panorama Viewer

## คุณสมบัติ
- อัปโหลด JPG/JPEG/PNG ได้ 3–20 ภาพ
- Preview ภาพก่อนส่งประมวลผล และ Drag & Drop
- เชื่อมภาพด้วย OpenCV Stitcher
- สร้าง QR Code และ URL สำหรับแชร์
- Viewer ด้วย Pannellum พร้อมเมาส์/สัมผัส/ซูม/Fullscreen
- จำกัด 20 MB ต่อภาพ และ 100 MB ต่อคำขอ
- Health check ที่ `/health`

## ติดตั้งในเครื่อง

แนะนำ Python 3.11

```bash
python -m venv .venv
# Windows:
.venv\\Scripts\\activate
# macOS/Linux:
source .venv/bin/activate

pip install -r requirements.txt
```

ตั้งค่า Secret Key (ควรตั้งค่าใหม่ทุก environment):

```bash
# macOS/Linux
export SECRET_KEY="ใส่ค่าสุ่มที่ยาวและคาดเดายาก"
# Windows PowerShell
$env:SECRET_KEY="ใส่ค่าสุ่มที่ยาวและคาดเดายาก"
```

รัน:

```bash
python app.py
```

เปิด `http://127.0.0.1:5000`

## Deploy บน Render
1. Push โฟลเดอร์นี้ขึ้น GitHub
2. Render → New → Blueprint แล้วเลือก repository
3. Render จะอ่าน `render.yaml` และติดตั้ง dependencies
4. ตรวจสอบ Environment ว่ามี `SECRET_KEY` ถูกสร้างอัตโนมัติ
5. Deploy และทดสอบ `/health`

## ข้อจำกัดสำคัญของการ Deploy
Render Web Service แบบ filesystem ชั่วคราวอาจลบไฟล์ภาพและ QR ที่สร้างไว้เมื่อมีการ redeploy/restart หรือย้าย instance ได้ หากต้องการเก็บผลงานถาวร ให้ต่อ Object Storage เช่น S3-compatible storage หรือใช้ Persistent Disk ที่เหมาะสม และแก้เส้นทางบันทึก/อ่านไฟล์ให้ใช้ storage นั้น

ตัวอย่างนี้ยังไม่มีระบบสมาชิก, ฐานข้อมูล, การลบไฟล์อัตโนมัติ หรือระบบคิวงาน การประมวลผลภาพขนาดใหญ่ใช้ CPU/RAM มาก ควรจำกัดจำนวนผู้ใช้งานพร้อมกันและพิจารณา background worker เมื่อใช้งานจริงในวงกว้าง

## หมายเหตุเกี่ยวกับภาพ 360°
OpenCV Stitcher สร้างภาพพาโนรามาแบบ projection ที่เหมาะกับการเชื่อมภาพ แต่ไม่ได้รับประกันว่าไฟล์ผลลัพธ์จะเป็น equirectangular 2:1 ที่สมบูรณ์ทุกชุดภาพ ขณะที่ Pannellum ต้องการภาพ equirectangular สำหรับโหมด 360° เต็มรูปแบบ ภาพที่ไม่ตรงรูปแบบอาจแสดงผลผิดสัดส่วนหรือมีรอยต่อ ควรทดสอบด้วยชุดภาพจริง และหากต้องการผลลัพธ์ 360° ที่แม่นยำ ควรเพิ่มขั้นตอนแปลง projection/ตรวจสอบสัดส่วนก่อนส่งเข้า Viewer

## โครงสร้าง
```text
Panorama360/
├── app.py
├── requirements.txt
├── Procfile
├── render.yaml
├── templates/
│   ├── base.html
│   ├── index.html
│   └── viewer.html
└── static/
    ├── css/style.css
    ├── js/app.js
    ├── panoramas/
    └── qr/
```
