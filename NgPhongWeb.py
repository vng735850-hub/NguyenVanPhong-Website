
import os
import mimetypes
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote

# ==========================================
# PHONG WEB V16
# CHI GIU LAI MUC DINH VI
# TI LE DINH VI 7:2
# ==========================================

BASE_DIR = Path(__file__).resolve().parent
PORT = int(os.environ.get("PORT", 5000))

MEDIAFIRE_LINK = (
    "https://www.mediafire.com/file/"
    "yen60lu05hfnng4/DINH_VI_BT.zip/file"
)

HTML = r"""
<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="theme-color" content="#080d2b">

<title>Nguyễn Văn Phong WebSite</title>

<style>
* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: Arial, sans-serif;
    color: white;
    min-height: 100vh;

    background:
        linear-gradient(
            rgba(0, 0, 25, 0.45),
            rgba(0, 0, 30, 0.82)
        ),
        url('/background.jpg');

    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    background-repeat: no-repeat;
}

/* HEADER */

header {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 12px;
    padding: 12px;

    background: rgba(0, 0, 30, 0.92);
    border-bottom: 2px solid #35d9ff;
    box-shadow: 0 0 18px #007bff;
}

.header-logo {
    width: 55px;
    height: 55px;
    object-fit: cover;
    border-radius: 12px;
    border: 2px solid #35d9ff;
    box-shadow: 0 0 12px #35d9ff;
}

.header-title {
    color: #35d9ff;
    font-size: clamp(17px, 4vw, 25px);
    font-weight: bold;
    text-shadow: 0 0 12px #008cff;
}

/* MAIN */

.container {
    max-width: 900px;
    margin: auto;
    padding: 30px 15px;
    text-align: center;
}

.hero-logo {
    width: min(220px, 65%);
    max-height: 180px;
    object-fit: contain;
    margin: 15px auto;
    filter: drop-shadow(0 0 15px #008cff);
}

h1 {
    font-size: clamp(23px, 5vw, 34px);
    color: white;
    text-shadow: 0 0 12px #35d9ff;
    margin: 10px 0;
}

.subtitle {
    margin: 12px 0 25px;
    font-size: 15px;
    line-height: 1.8;
    color: #d7eaff;
}

/* DINH VI CARD 7:2 */

.location-container {
    width: 100%;
    margin: 25px auto;
}

.location-link {
    display: block;
    width: 100%;
    color: white;
    text-decoration: none;
}

.location-card {
    width: 100%;
    aspect-ratio: 7 / 2;

    display: flex;
    flex-direction: row;
    align-items: center;
    justify-content: center;
    gap: 12px;

    padding: 12px;
    overflow: hidden;

    background: rgba(8, 15, 48, 0.90);
    border: 2px solid #a66bff;
    border-radius: 15px;

    box-shadow:
        0 0 15px #8c38ff,
        inset 0 0 15px #5e24aa33;

    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);

    transition: .25s;
}

.location-card:hover {
    transform: translateY(-3px);
    border-color: #35d9ff;
    box-shadow:
        0 0 22px #8c38ff,
        0 0 12px #35d9ff;
}

.location-emoji {
    font-size: clamp(25px, 6vw, 42px);
    flex-shrink: 0;
}

.location-info {
    display: flex;
    flex-direction: column;
    align-items: flex-start;
    justify-content: center;
    gap: 7px;
    text-align: left;
}

.location-info h2 {
    color: #d5a5ff;
    font-size: clamp(13px, 3vw, 21px);
    line-height: 1.3;
}

.location-info p {
    color: #dceaff;
    font-size: clamp(10px, 2vw, 14px);
}

.location-button {
    display: inline-block;
    margin-top: 2px;
    padding: 7px 16px;

    border: none;
    border-radius: 8px;

    color: white;
    background: linear-gradient(
        90deg,
        #087dff,
        #8c42ff
    );

    font-size: 12px;
    font-weight: bold;
}

/* MUSIC */

.music-control {
    margin: 28px auto 10px;
    display: flex;
    justify-content: center;
    align-items: center;
    gap: 12px;
}

.music-button {
    width: 46px;
    height: 46px;
    border-radius: 50%;
    border: 2px solid #35d9ff;
    color: white;

    background: linear-gradient(
        135deg,
        #087dff,
        #8c42ff
    );

    box-shadow: 0 0 15px #168cff99;
    font-size: 19px;
    cursor: pointer;
    user-select: none;
    -webkit-user-select: none;
    touch-action: manipulation;
}

.music-status {
    font-size: 12px;
    color: #c6eaff;
    text-align: left;
    line-height: 1.6;
}

.music-status strong {
    color: #35d9ff;
}

/* FOOTER */

footer {
    margin-top: 35px;
    padding: 20px 10px;
    text-align: center;

    background: rgba(0, 0, 20, 0.85);
    border-top: 1px solid #526dff66;

    color: #b9dcff;
    font-size: 12px;
    line-height: 1.8;
}

/* MOBILE */

@media (max-width: 500px) {
    .container {
        padding: 22px 12px;
    }

    .header-logo {
        width: 45px;
        height: 45px;
    }

    .location-card {
        aspect-ratio: 7 / 2;
        gap: 8px;
        padding: 8px;
        border-radius: 12px;
    }

    .location-info {
        gap: 4px;
    }

    .location-button {
        padding: 5px 11px;
        font-size: 10px;
    }
}
</style>
</head>

<body>

<header>
    <img
        class="header-logo"
        src="/logo.png"
        alt="Logo"
    >

    <div class="header-title">
        NGUYỄN VĂN PHONG WEBSITE
    </div>
</header>

<main class="container">

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

</main>

<footer>
    © 2026 Nguyễn Văn Phong Website
    <br>
    PHONG WEB V16
</footer>

<script>
const audio = document.getElementById("audio");
const musicButton = document.getElementById("mainMusicButton");

const musicStatus = document.getElementById("musicStatus");
const loopStatus = document.getElementById("loopStatus");

audio.volume = 0.8;

let pressTimer = null;
let clickTimer = null;
let isHolding = false;
let isLoop = false;

function updateMusicUI() {
    if (audio.paused) {
        musicButton.textContent = "▶";
        musicStatus.textContent = "Nhấn để phát nhạc";
    } else {
        musicButton.textContent = "Ⅱ";
        musicStatus.textContent = "Đang phát nhạc";
    }

    loopStatus.textContent =
        "Lặp lại: " + (isLoop ? "Bật" : "Tắt");
}

async function togglePlay() {
    if (audio.paused) {
        try {
            await audio.play();
        } catch (error) {
            musicStatus.textContent =
                "Không thể phát. Kiểm tra file music.mp3";
        }
    } else {
        audio.pause();
    }

    updateMusicUI();
}

function toggleLoop() {
    isLoop = !isLoop;
    audio.loop = isLoop;
    updateMusicUI();
}

function stopMusic() {
    audio.pause();
    audio.currentTime = 0;
    updateMusicUI();
    musicStatus.textContent = "Đã dừng nhạc";
}

musicButton.addEventListener("pointerdown", function() {
    isHolding = false;

    pressTimer = setTimeout(function() {
        isHolding = true;
        clearTimeout(clickTimer);
        stopMusic();
    }, 800);
});

musicButton.addEventListener("pointerup", function() {
    clearTimeout(pressTimer);
});

musicButton.addEventListener("pointerleave", function() {
    clearTimeout(pressTimer);
});

musicButton.addEventListener("pointercancel", function() {
    clearTimeout(pressTimer);
});

musicButton.addEventListener("click", function(event) {
    if (isHolding) {
        isHolding = false;
        return;
    }

    if (event.detail >= 2) {
        clearTimeout(clickTimer);
        toggleLoop();
        return;
    }

    clearTimeout(clickTimer);

    clickTimer = setTimeout(function() {
        togglePlay();
    }, 280);
});

audio.addEventListener("play", updateMusicUI);
audio.addEventListener("pause", updateMusicUI);
audio.addEventListener("ended", updateMusicUI);

updateMusicUI();
</script>

</body>
</html>
"""


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


if __name__ == "__main__":

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
