
from flask import Flask

app = Flask(__name__)

@app.route("/")
def home():
    return """
    <!DOCTYPE html>
    <html lang="th">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1">
        <title>Panorama 360</title>
    </head>
    <body style="font-family:Arial;text-align:center;padding:50px">
        <h1>Panorama 360</h1>
        <h2>เว็บไซต์ออนไลน์สำเร็จแล้ว!</h2>
        <p>ระบบพร้อมสำหรับพัฒนาต่อ</p>
    </body>
    </html>
    """

if __name__ == "__main__":
    app.run()
