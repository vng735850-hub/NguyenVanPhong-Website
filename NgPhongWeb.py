
import os
import json
import mimetypes
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlencode, urlsplit, unquote

# ==========================================
# PHONG WEB V20
# VUOTNHANH QUICK LINK API
# ==========================================

BASE_DIR = Path(__file__).resolve().parent
PORT = int(os.environ.get("PORT", 5000))

# API KEY: Cấu hình trong Environment Variables trên Render
API_KEY = os.environ.get("VUOTNHANH_API_KEY", "").strip()

# Địa chỉ website đang chạy trên Render
SITE_URL = os.environ.get(
    "SITE_URL",
    "https://phong-web.onrender.com"
).rstrip("/")

MEDIAFIRE_LINK = (
    "https://www.mediafire.com/file/"
    "yen60lu05hfnng4/DINH_VI_BT.zip/file"
)

VUOTNHANH_ENDPOINT = "https://vuotnhanh.com/zVOM"

HTML = r"""
<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>NGUYỄN VĂN PHONG WEBSITE</title>

<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    min-height: 100vh;
    padding-bottom: 100px;
    font-family: Arial, sans-serif;
    color: white;
    text-align: center;
    background: radial-gradient(circle at top, #253d91, #080d22 70%);
}

header {
    padding: 22px 10px;
    font-size: 23px;
    font-weight: bold;
    background: rgba(0,0,0,0.3);
    letter-spacing: 1px;
}

main {
    padding: 25px 15px;
}

.hero-logo {
    width: 130px;
    height: 130px;
    object-fit: contain;
    border-radius: 20px;
    margin-top: 15px;
}

h1 {
    font-size: 27px;
    margin-top: 20px;
}

.subtitle {
    color: #cbd8ff;
    line-height: 1.7;
    margin: 15px auto 30px;
    max-width: 600px;
}

/* LOCATION CARD */

.location-container {
    width: 100%;
    max-width: 700px;
    aspect-ratio: 7 / 2;
    margin: 25px auto;
}

.location-link {
    display: block;
    width: 100%;
    height: 100%;
    text-decoration: none;
    color: white;
}

.location-card {
    width: 100%;
    height: 100%;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 18px;
    padding: 15px;
    border-radius: 18px;
    background: linear-gradient(135deg, #1769e0, #7736c8);
    border: 1px solid rgba(255,255,255,0.25);
    box-shadow: 0 8px 25px rgba(0,0,0,0.3);
    transition: 0.25s;
}

.location-card:hover {
    transform: scale(1.025);
    box-shadow: 0 0 25px #488dff;
}

.location-emoji {
    font-size: 45px;
}

.location-info h2 {
    font-size: 19px;
    margin: 5px;
}

.location-info p {
    font-size: 13px;
    color: #e1eaff;
}

.location-button {
    display: inline-block;
    margin-top: 5px;
    background: white;
    color: #1859c9;
    padding: 9px 25px;
    border-radius: 20px;
    font-weight: bold;
    font-size: 13px;
}

/* LINK PAGE */

#linkPage {
    display: none;
    max-width: 600px;
    margin: 55px auto;
    padding: 35px 20px;
    background: rgba(255,255,255,0.08);
    border: 1px solid rgba(255,255,255,0.18);
    border-radius: 20px;
    box-shadow: 0 10px 35px rgba(0,0,0,0.3);
}

.link-icon {
    font-size: 65px;
}

#linkPage h2 {
    font-size: 25px;
    line-height: 1.5;
    margin: 20px 0;
}

.link-description {
    color: #d2dcff;
    line-height: 1.7;
    margin-bottom: 25px;
}

.cross-link-button {
    display: inline-block;
    padding: 15px 45px;
    border: none;
    border-radius: 30px;
    background: linear-gradient(135deg, #1685ff, #7139df);
    color: white;
    font-size: 18px;
    font-weight: bold;
    text-decoration: none;
    box-shadow: 0 5px 20px rgba(0,100,255,0.4);
    cursor: pointer;
}

.cross-link-button:disabled {
    opacity: 0.6;
    cursor: wait;
}

.back-button {
    display: inline-block;
    margin-top: 25px;
    color: #cbd8ff;
    text-decoration: none;
    font-size: 14px;
}

#status {
    margin-top: 18px;
    color: #ffe28a;
    font-size: 14px;
    line-height: 1.6;
}

/* MUSIC BUTTON */

.music-mini {
    position: fixed !important;
    bottom: 15px !important;
    left: 50% !important;
    right: auto !important;
    top: auto !important;
    margin: 0 !important;
    transform: translateX(-50%) !important;

    width: 55px;
    height: 55px;
    min-width: 55px;
    min-height: 55px;

    border-radius: 50%;
    border: 2px solid rgba(255,255,255,0.8);
    background: linear-gradient(135deg, #1685ff, #7736d5);
    color: white;
    font-size: 25px;

    display: flex;
    align-items: center;
    justify-content: center;

    cursor: pointer;
    z-index: 99999;
    box-shadow: 0 0 18px rgba(40,120,255,0.6);
    transition: background 0.2s, box-shadow 0.2s;
    -webkit-tap-highlight-color: transparent;
    outline: none;
}

.music-mini:active {
    transform: translateX(-50%) !important;
}

.music-mini.playing {
    background: linear-gradient(135deg, #00c98b, #087dca);
    box-shadow: 0 0 22px rgba(0,220,160,0.7);
}

.music-mini .music-icon {
    pointer-events: none;
}

footer {
    padding: 25px 10px;
    color: #9eafd8;
    font-size: 12px;
}

@media(max-width: 500px) {
    header {
        font-size: 18px;
    }

    h1 {
        font-size: 22px;
    }

    .location-emoji {
        font-size: 30px;
    }

    .location-info h2 {
        font-size: 14px;
    }

    .location-info p {
        font-size: 10px;
    }

    .location-button {
        padding: 6px 15px;
        font-size: 11px;
    }

    #linkPage h2 {
        font-size: 21px;
    }
}
</style>
</head>

<body>

<header>
    NGUYỄN VĂN PHONG WEBSITE
</header>

<main>

<div id="homePage">

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

    <section class="location-container">

        <a class="location-link" href="/dinh-vi">

            <div class="location-card">

                <div class="location-emoji">📍</div>

                <div class="location-info">

                    <h2>ĐỊNH VỊ XANH TÍM OB55</h2>

                    <p>Nhấn vào đây để tiếp tục</p>

                    <span class="location-button">
                        MỞ MỤC
                    </span>

                </div>

            </div>

        </a>

    </section>

</div>

<div id="linkPage">

    <div class="link-icon">🔐</div>

    <h2>
        BẠN CẦN VƯỢT LINK ĐỂ LẤY FILE MEDIAFIRE
    </h2>

    <div class="link-description">
        Nhấn nút bên dưới để tạo đường dẫn vượt link.
        <br>
        Sau khi hoàn thành, bạn sẽ quay lại PHONG WEB.
    </div>

    <button
        class="cross-link-button"
        id="crossLinkButton"
        type="button"
    >
        🔓 VƯỢT LINK
    </button>

    <div id="status"></div>

    <br>

    <a class="back-button" href="/">
        ← QUAY LẠI TRANG CHỦ
    </a>

</div>

</main>

<button
    class="music-mini"
    id="musicButton"
    aria-label="Bật hoặc tắt nhạc"
    title="Bật / Tắt nhạc"
    type="button"
>
    <span class="music-icon" id="musicIcon">▶</span>
</button>

<audio id="audio" preload="metadata">
    <source src="/music.mp3" type="audio/mpeg">
</audio>

<footer>
    © 2026 Nguyễn Văn Phong Website
    <br><br>
    PHONG WEB V20
</footer>

<script>

// ==========================================
// PAGE NAVIGATION
// ==========================================

const homePage = document.getElementById("homePage");
const linkPage = document.getElementById("linkPage");

function showPage() {

    if (window.location.pathname === "/dinh-vi") {
        homePage.style.display = "none";
        linkPage.style.display = "block";
    } else {
        homePage.style.display = "block";
        linkPage.style.display = "none";
    }
}

window.addEventListener("popstate", showPage);

document.querySelector(".location-link").addEventListener("click", function(e) {
    e.preventDefault();

    history.pushState({}, "", "/dinh-vi");

    showPage();
    window.scrollTo(0, 0);
});

showPage();


// ==========================================
// VUOTNHANH QUICK LINK
// ==========================================

const crossLinkButton = document.getElementById("crossLinkButton");
const statusText = document.getElementById("status");

crossLinkButton.addEventListener("click", async function() {

    crossLinkButton.disabled = true;
    statusText.textContent = "Đang tạo đường dẫn vượt link...";

    try {

        const response = await fetch("/create-link", {
            method: "GET",
            cache: "no-store"
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
            throw new Error(data.message || "Không thể tạo link.");
        }

        statusText.textContent = "Đang chuyển đến Vượt Nhanh...";

        window.location.href = data.url;

    } catch(error) {

        statusText.textContent = "Lỗi: " + error.message;
        crossLinkButton.disabled = false;

    }

});


// ==========================================
// MUSIC CONTROL
// ==========================================

const audio = document.getElementById("audio");
const musicButton = document.getElementById("musicButton");
const musicIcon = document.getElementById("musicIcon");

let isPlaying = false;

function updateMusicButton() {

    if (isPlaying) {
        musicButton.classList.add("playing");
        musicIcon.textContent = "♫";
    } else {
        musicButton.classList.remove("playing");
        musicIcon.textContent = "▶";
    }
}

musicButton.addEventListener("click", async function() {

    if (!isPlaying) {

        try {

            audio.loop = true;
            await audio.play();
            isPlaying = true;

        } catch(error) {

            audio.loop = false;
            isPlaying = false;

            console.log("Music error:", error);
        }

    } else {

        audio.pause();
        audio.currentTime = 0;
        audio.loop = false;

        isPlaying = false;
    }

    updateMusicButton();

});

audio.addEventListener("pause", function() {

    if (isPlaying) {
        isPlaying = false;
        audio.loop = false;
        updateMusicButton();
    }

});

audio.addEventListener("error", function() {

    isPlaying = false;
    audio.loop = false;
    updateMusicButton();

    console.log("Không tìm thấy music.mp3");

});

</script>

</body>
</html>
"""


class Website(BaseHTTPRequestHandler):

    def send_json(self, status, data):

        content = json.dumps(data).encode("utf-8")

        self.send_response(status)
        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8"
        )
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()

        try:
            self.wfile.write(content)
        except (BrokenPipeError, ConnectionResetError):
            pass

    def do_GET(self):

        path = unquote(urlsplit(self.path).path)

        # HOME AND LINK PAGE

        if path in ("/", "/index.html", "/dinh-vi"):

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

        # CREATE VUOTNHANH LINK

        if path == "/create-link":

            if not API_KEY:
                self.send_json(500, {
                    "success": False,
                    "message": "Chưa cấu hình Vượt Nhanh API Key trên Render."
                })
                return

            if not SITE_URL.startswith("https://"):
                self.send_json(500, {
                    "success": False,
                    "message": "SITE_URL phải là địa chỉ HTTPS."
                })
                return

            # Sau khi người dùng vượt link, Vượt Nhanh
            # sẽ đưa họ về địa chỉ này.
            return_url = SITE_URL + "/complete"

            # Tạo URL Quick Link theo tài liệu bạn cung cấp.
            query = urlencode({
                "api": API_KEY,
                "url": return_url
            })

            quick_link = VUOTNHANH_ENDPOINT + "?" + query

            self.send_json(200, {
                "success": True,
                "url": quick_link
            })

            print("[PHONG WEB] Created Vượt Nhanh link")

            return

        # RETURN PAGE

        if path == "/complete":

            # Đây chỉ là trang nhận chuyển hướng.
            # Chưa phải xác minh hoàn thành vượt link.
            self.send_response(302)
            self.send_header("Location", MEDIAFIRE_LINK)
            self.send_header("Cache-Control", "no-store")
            self.end_headers()

            print("[PHONG WEB] Visitor returned to completion URL")

            return

        # STATIC FILES

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


if __name__ == "__main__":

    server = ThreadingHTTPServer(
        ("0.0.0.0", PORT),
        Website
    )

    print("====================================")
    print("          PHONG WEB V20")
    print("====================================")
    print("Server running on port:", PORT)
    print("Vuotnhanh Quick Link:", "ENABLED" if API_KEY else "MISSING API KEY")
    print("Return URL:", SITE_URL + "/complete")
    print("MediaFire redirect: ENABLED")
    print("Fixed music button: ENABLED")
    print("Music looping: ENABLED")
    print("Location aspect ratio: 7:2")
    print("Advertisements: REMOVED")
    print("====================================")

    try:
        server.serve_forever()

    except KeyboardInterrupt:
        print("\n[PHONG WEB] Server stopped.")

    finally:
        server.server_close()
