
import os
import mimetypes
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse
from html import escape

# ==========================================
# PHONG WEB V17
# TRANG VUOT LINK + TAI FILE MEDIAFIRE
# ==========================================

BASE_DIR = Path(__file__).resolve().parent
PORT = int(os.environ.get("PORT", 5000))

SHORT_LINK = "https://link4m.net/lbatN"

MEDIAFIRE_LINK = (
    "https://www.mediafire.com/file/"
    "yen60lu05hfnng4/DINH_VI_BT.zip/file"
)

RETURN_PATH = "/link-return"

# ==========================================
# CSS GIAO DIEN
# ==========================================

STYLE = """
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    min-height: 100vh;
    padding: 20px;
    font-family: Arial, sans-serif;
    color: white;
    background:
        radial-gradient(circle at top, #294b91,
        #101a35 55%, #080d1c);
    display: flex;
    justify-content: center;
    align-items: center;
}

.container {
    width: 100%;
    max-width: 680px;
}

.brand {
    text-align: center;
    font-size: 14px;
    letter-spacing: 3px;
    color: #b8d4ff;
    margin-bottom: 20px;
}

.card {
    background: rgba(16, 29, 58, 0.95);
    border: 1px solid rgba(133, 174, 255, 0.3);
    border-radius: 22px;
    padding: 30px 24px;
    text-align: center;
    box-shadow: 0 18px 60px rgba(0,0,0,0.35);
}

.logo {
    width: 110px;
    height: 110px;
    object-fit: contain;
    margin-bottom: 15px;
}

h1 {
    font-size: 27px;
    line-height: 1.4;
    margin: 12px 0;
}

p {
    color: #c3d2ef;
    line-height: 1.7;
}

.btn {
    display: block;
    width: 100%;
    padding: 17px;
    margin-top: 22px;
    border-radius: 13px;
    text-decoration: none;
    font-weight: bold;
    letter-spacing: 1px;
    color: white;
    background: linear-gradient(110deg, #2463eb, #7949db);
}

.btn-green {
    background: linear-gradient(110deg, #159957, #38b66b);
}

.btn:hover {
    opacity: 0.9;
}

.status {
    color: #66e59a;
    font-size: 19px;
    font-weight: bold;
}

.back {
    display: inline-block;
    color: #a9c8ff;
    margin-top: 22px;
    text-decoration: none;
}

.music {
    border-top: 1px solid #34466c;
    margin-top: 28px;
    padding-top: 20px;
}

audio {
    width: 100%;
}

.footer {
    text-align: center;
    margin-top: 20px;
    font-size: 12px;
    color: #91a5c9;
}
"""

# ==========================================
# HÀM TẠO TRANG HTML
# ==========================================

def make_page(title, content):

    return f"""
<!DOCTYPE html>
<html lang="vi">

<head>
<meta charset="UTF-8">

<meta name="viewport"
content="width=device-width, initial-scale=1.0">

<meta name="theme-color" content="#101a35">

<title>{escape(title)} - PHONG WEB</title>

<style>
{STYLE}
</style>

</head>

<body>

<div class="container">

<div class="brand">
NGUYỄN VĂN PHONG WEBSITE
</div>

<div class="card">

{content}

</div>

<div class="footer">
© 2026 Nguyễn Văn Phong Website
<br>
PHONG WEB V17
</div>

</div>

</body>
</html>
"""


# ==========================================
# TRANG CHỦ
# ==========================================

HOME_HTML = """
<img
    class="logo"
    src="/logo.png"
    alt="PHONG WEB"
    onerror="this.style.display='none'"
>

<h1>WELCOME TO PHONG WEB</h1>

<p>
Chào mừng bạn đến với website của Nguyễn Văn Phong.
<br><br>
📍 ĐỊNH VỊ XANH TÍM OB55
</p>

<a class="btn" href="/location">
MỞ MỤC
</a>

<div class="music">

<strong>🎵 THƯƠNG NHAU ĐẾN THẾ</strong>

<p>Nhấn phát để nghe nhạc</p>

<audio controls loop preload="metadata">

<source src="/music.mp3" type="audio/mpeg">

Trình duyệt không hỗ trợ phát nhạc.

</audio>

</div>
"""


# ==========================================
# TRANG VƯỢT LINK
# ==========================================

LOCATION_HTML = f"""
<h1>
BẠN CẦN VƯỢT LINK ĐỂ LẤY FILE MEDIAFIRE
</h1>

<p>
Vui lòng nhấn nút bên dưới để chuyển đến
trang vượt link.
</p>

<a
    class="btn"
    href="{SHORT_LINK}"
    rel="noopener noreferrer"
>
VƯỢT LINK
</a>

<a class="back" href="/">
← QUAY LẠI TRANG CHỦ
</a>
"""


# ==========================================
# TRANG VƯỢT LINK THÀNH CÔNG
# ==========================================

SUCCESS_HTML = f"""
<div style="font-size:55px;">
✓
</div>

<div class="status">
VƯỢT LINK THÀNH CÔNG
</div>

<h1>
BẠN ĐÃ QUAY LẠI PHONG WEB
</h1>

<p>
Bạn đã trở lại website.
Nhấn nút bên dưới để tải file.
</p>

<a
    class="btn btn-green"
    href="{MEDIAFIRE_LINK}"
    target="_blank"
    rel="noopener noreferrer"
>
TẢI FILE
</a>

<a class="back" href="/">
← QUAY LẠI TRANG CHỦ
</a>
"""


# ==========================================
# SERVER
# ==========================================

class Website(BaseHTTPRequestHandler):

    def send_html(self, content, status=200):

        data = content.encode("utf-8")

        self.send_response(status)

        self.send_header(
            "Content-Type",
            "text/html; charset=utf-8"
        )

        self.send_header(
            "Content-Length",
            str(len(data))
        )

        self.send_header(
            "Cache-Control",
            "no-store"
        )

        self.end_headers()

        try:
            self.wfile.write(data)

        except (BrokenPipeError, ConnectionResetError):
            pass


    def do_GET(self):

        path = urlparse(self.path).path

        # TRANG CHỦ
        if path in ("/", "/index.html"):

            self.send_html(
                make_page(
                    "Trang chủ",
                    HOME_HTML
                )
            )

            return


        # TRANG ĐỊNH VỊ
        if path == "/location":

            self.send_html(
                make_page(
                    "Vượt link",
                    LOCATION_HTML
                )
            )

            return


        # TRANG QUAY LẠI SAU KHI VƯỢT LINK
        if path == RETURN_PATH:

            self.send_html(
                make_page(
                    "Vượt link thành công",
                    SUCCESS_HTML
                )
            )

            return


        # FILE TĨNH
        allowed_files = {
            "/logo.png",
            "/background.jpg",
            "/music.mp3"
        }

        if path in allowed_files:

            file_path = BASE_DIR / path.lstrip("/")

            if not file_path.is_file():

                self.send_error(
                    404,
                    "Không tìm thấy file"
                )

                return

            content_type = (
                mimetypes.guess_type(str(file_path))[0]
                or "application/octet-stream"
            )

            try:

                file_size = file_path.stat().st_size

                self.send_response(200)

                self.send_header(
                    "Content-Type",
                    content_type
                )

                self.send_header(
                    "Content-Length",
                    str(file_size)
                )

                self.send_header(
                    "Cache-Control",
                    "public, max-age=3600"
                )

                self.end_headers()

                with open(file_path, "rb") as file:

                    while True:

                        chunk = file.read(64 * 1024)

                        if not chunk:
                            break

                        self.wfile.write(chunk)

            except (BrokenPipeError, ConnectionResetError):
                pass

            except OSError as error:

                print(
                    "[PHONG WEB] File error:",
                    error
                )

            return


        # KHÔNG TÌM THẤY
        self.send_error(
            404,
            "Trang không tồn tại"
        )


    def log_message(self, format, *args):

        print(
            "[PHONG WEB]",
            format % args
        )


# ==========================================
# KHỞI ĐỘNG
# ==========================================

if __name__ == "__main__":

    server = ThreadingHTTPServer(
        ("0.0.0.0", PORT),
        Website
    )

    print("====================================")
    print("          PHONG WEB V17")
    print("====================================")

    print("Server running on port:", PORT)

    print("Trang chủ: /")

    print("Trang định vị: /location")

    print("Trang thành công: /link-return")

    print("====================================")

    try:

        server.serve_forever()

    except KeyboardInterrupt:

        print("\n[PHONG WEB] Server stopped.")

    finally:

        server.server_close()
