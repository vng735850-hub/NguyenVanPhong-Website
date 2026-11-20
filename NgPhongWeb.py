import os
import mimetypes
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote

==========================================

PHONG WEB V16

CHI GIU LAI MUC DINH VI

TI LE DINH VI 7:2

==========================================

BASE_DIR = Path(file).resolve().parent
PORT = int(os.environ.get("PORT", 5000))

MEDIAFIRE_LINK = (
"https://www.mediafire.com/file/"
"yen60lu05hfnng4/DINH_VI_BT.zip/file"
)

HTML = r"""
Nguyễn Văn Phong WebSite                   Logo

<div class="header-title">    
    NGUYỄN VĂN PHONG WEBSITE    
</div>

<img    
    class="hero-logo"    
    src="/logo.png"    
    alt="PHONG WEB"    
>    
  
<h1>WELCOME TO PHONG WEB</h1>    
  
<div class="subtitle">    
    Chào mừng bạn đến với website của Nguyễn Văn Phong.    
    <br>    
    📍 ĐỊNH VỊ XANH TÍM OB55    
</div>    
  
<!-- ONLY LOCATION CARD -->    
  
<section class="location-container">    
  
    <a    
        class="location-link"    
        href="https://www.mediafire.com/file/yen60lu05hfnng4/DINH_VI_BT.zip/file"    
        target="_blank"    
        rel="noopener noreferrer"    
    >    
  
        <div class="location-card">    
  
            <div class="location-emoji">    
                📍    
            </div>    
  
            <div class="location-info">    
  
                <h2>ĐỊNH VỊ XANH TÍM OB55</h2>    
  
                <p>Nhấn vào đây để tải xuống</p>    
  
                <span class="location-button">    
                    MỞ MỤC    
                </span>    
  
            </div>    
  
        </div>    
  
    </a>    
  
</section>    
  
<!-- MUSIC PLAYER -->    
  
<div class="music-control">    
  
    <button    
        class="music-button"    
        id="mainMusicButton"    
        aria-label="Điều khiển nhạc"    
    >    
        ▶    
    </button>    
  
    <div class="music-status">    
        <strong>🎵 THƯƠNG NHAU ĐẾN THẾ</strong>    
        <div id="musicStatus">Nhấn để phát nhạc</div>    
        <div id="loopStatus">Lặp lại: Tắt</div>    
    </div>    
  
</div>    
  
<audio id="audio" preload="metadata">    
    <source src="/music.mp3" type="audio/mpeg">    
    Trình duyệt không hỗ trợ phát nhạc.    
</audio>

© 2026 Nguyễn Văn Phong Website         
   PHONG WEB V16            """

class Website(BaseHTTPRequestHandler):

def do_GET(self):    
    path = unquote(self.path.split("?")[0])    
  
    if path in ("/", "/index.html"):    
        content = HTML.encode("utf-8")    
  
        self.send_response(200)    
        self.send_header(    
            "Content-Type",    
            "text/html; charset=utf-8"    
        )    
        self.send_header(    
            "Content-Length",    
            str(len(content))    
        )    
        self.send_header("Cache-Control", "no-cache")    
        self.end_headers()    
  
        try:    
            self.wfile.write(content)    
        except (BrokenPipeError, ConnectionResetError):    
            pass    
  
        return    
  
    allowed_files = {    
        "/logo.png",    
        "/background.jpg",    
        "/music.mp3"    
    }    
  
    if path not in allowed_files:    
        self.send_error(404, "File not found")    
        return    
  
    file_path = BASE_DIR / path.lstrip("/")    
  
    if not file_path.is_file():    
        self.send_error(404, "Asset not found")    
        return    
  
    content_type = mimetypes.guess_type(    
        str(file_path)    
    )[0] or "application/octet-stream"    
  
    try:    
        file_size = file_path.stat().st_size    
  
        self.send_response(200)    
        self.send_header("Content-Type", content_type)    
        self.send_header("Content-Length", str(file_size))    
        self.send_header("Accept-Ranges", "bytes")    
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
        print("[PHONG WEB] File error:", error)    
  
def log_message(self, format, *args):    
    print("[PHONG WEB]", format % args)

if name == "main":

server = ThreadingHTTPServer(    
    ("0.0.0.0", PORT),    
    Website    
)    
  
print("====================================")    
print("          PHONG WEB V16")    
print("====================================")    
print("Server running on port:", PORT)    
print("Only location section remains")    
print("Location aspect ratio: 7:2")    
print("Cloud pricing: REMOVED")    
print("Advertisement scripts: REMOVED")    
print("====================================")    
  
try:    
    server.serve_forever()    
except KeyboardInterrupt:    
    print("\n[PHONG WEB] Server stopped.")    
finally:    
    server.server_close()