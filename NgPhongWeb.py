
import os
import mimetypes
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote

# ==================================================
# PHONG WEB V15
# XOA GIA THUE CLOUD
# 5 MUC TI LE 3:1
# ==================================================

BASE_DIR = Path(__file__).resolve().parent
PORT = int(os.environ.get("PORT", 5000))

MEDIAFIRE_LINK = "https://www.mediafire.com/file/yen60lu05hfnng4/DINH_VI_BT.zip/file"

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

:root {
    --blue: #35d9ff;
    --purple: #a66bff;
    --glass: rgba(8, 15, 48, 0.88);
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
    border-bottom: 2px solid var(--blue);
    box-shadow: 0 0 18px #007bff;
}

.header-logo {
    width: 55px;
    height: 55px;
    object-fit: cover;
    border-radius: 12px;
    border: 2px solid var(--blue);
    box-shadow: 0 0 12px var(--blue);
}

.header-title {
    color: var(--blue);
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
    text-shadow: 0 0 12px var(--blue);
    margin: 10px 0;
}

.subtitle {
    margin: 12px 0 25px;
    font-size: 15px;
    line-height: 1.8;
    color: #d7eaff;
}

/* FIVE MAIN CARDS */

.cards {
    display: grid;
    grid-template-columns: repeat(2, minmax(0, 1fr));
    gap: 12px;
    margin-top: 25px;
}

.card {
    width: 100%;
    aspect-ratio: 3 / 1;
    background: var(--glass);
    border: 1px solid #8b70ff66;
    border-radius: 14px;
    padding: 7px;

    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    gap: 3px;

    text-align: center;
    backdrop-filter: blur(10px);
    -webkit-backdrop-filter: blur(10px);

    transition: .25s;
    overflow: hidden;
}

.card:hover {
    transform: translateY(-3px);
    border-color: var(--blue);
    box-shadow: 0 0 16px #168cff88;
}

.card .emoji {
    font-size: 21px;
    line-height: 1.1;
}

.card h3 {
    color: #8cddff;
    font-size: 12px;
    line-height: 1.2;
    margin: 0;
}

.card p {
    display: none;
}

.action {
    margin-top: 3px;
    padding: 5px 11px;
    border: none;
    border-radius: 7px;
    background: linear-gradient(90deg, #087dff, #8c42ff);
    color: white;
    font-size: 11px;
    font-weight: bold;
    cursor: pointer;
}

.action:hover {
    filter: brightness(1.2);
}

/* LINKS */

.card-link {
    display: block;
    color: white;
    text-decoration: none;
    min-width: 0;
}

.card-link .card {
    height: 100%;
}

.card-link.ob55 .card {
    border-color: #a64dff;
}

.card-link.setting .card {
    border-color: #b04cff;
}

/* INFORMATION PANEL */

.info-panel {
    display: none;
    margin-top: 22px;
    padding: 20px;
    background: rgba(5, 12, 42, 0.95);
    border: 1px solid #4d9cff;
    border-radius: 14px;
    box-shadow: 0 0 18px #286dff66;
    text-align: left;
    animation: appear .25s ease;
}

.info-panel.show {
    display: block;
}

.info-panel h2 {
    color: var(--blue);
    margin-bottom: 12px;
    font-size: 20px;
}

.info-panel p {
    line-height: 1.8;
    color: #e2eaff;
    white-space: pre-line;
}

.close-button {
    margin-top: 15px;
    padding: 9px 17px;
    color: white;
    background: #653bdb;
    border: none;
    border-radius: 8px;
    cursor: pointer;
}

@keyframes appear {
    from {
        opacity: 0;
        transform: translateY(8px);
    }
    to {
        opacity: 1;
        transform: translateY(0);
    }
}

/* MUSIC PLAYER */

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
    border: 2px solid var(--blue);
    color: white;
    background: linear-gradient(135deg, #087dff, #8c42ff);
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
    color: var(--blue);
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

    .cards {
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 10px;
    }

    .card {
        aspect-ratio: 3 / 1;
        border-radius: 12px;
        padding: 5px;
    }

    .card .emoji {
        font-size: 19px;
    }

    .card h3 {
        font-size: 11px;
    }

    .action {
        font-size: 10px;
        padding: 4px 9px;
    }

    .header-logo {
        width: 45px;
        height: 45px;
    }
}
</style>
</head>

<body>

<header>
    <img class="header-logo" src="/logo.png" alt="Logo">
    <div class="header-title">
        NGUYỄN VĂN PHONG WEBSITE
    </div>
</header>

<main class="container">

    <img class="hero-logo" src="/logo.png" alt="PHONG WEB">

    <h1>WELCOME TO PHONG WEB</h1>

    <div class="subtitle">
        Chào mừng bạn đến với website của Nguyễn Văn Phong.
        <br>
        Khám phá Gaming, Python và công nghệ tại đây!
    </div>

    <!-- FIVE MAIN CATEGORIES -->

    <section class="cards">

        <div class="card">
            <div class="emoji">🎮</div>
            <h3>GAMING</h3>
            <button class="action"
                onclick="showPanel('gaming')">
                Khám phá
            </button>
        </div>

        <div class="card">
            <div class="emoji">🐍</div>
            <h3>PYTHON</h3>
            <button class="action"
                onclick="showPanel('python')">
                Khám phá
            </button>
        </div>

        <div class="card">
            <div class="emoji">💻</div>
            <h3>TECHNOLOGY</h3>
            <button class="action"
                onclick="showPanel('technology')">
                Khám phá
            </button>
        </div>

        <a class="card-link ob55"
           href="https://www.mediafire.com/file/yen60lu05hfnng4/DINH_VI_BT.zip/file"
           target="_blank"
           rel="noopener noreferrer">

            <div class="card">
                <div class="emoji">📍</div>
                <h3>ĐỊNH VỊ XANH TÍM OB55</h3>
                <span class="action">Mở Mục</span>
            </div>
        </a>

        <div class="card-link setting"
             onclick="showPanel('setting')">

            <div class="card">
                <div class="emoji">⚙️</div>
                <h3>SETTING</h3>
                <button class="action" type="button">
                    Cài đặt
                </button>
            </div>
        </div>

    </section>

    <!-- INFORMATION PANEL -->

    <section class="info-panel" id="info">
        <h2 id="infoTitle"></h2>
        <p id="infoContent"></p>

        <button class="close-button"
            onclick="closePanel()">
            Đóng mục
        </button>
    </section>

    <!-- MUSIC -->

    <div class="music-control">

        <button
            class="music-button"
            id="mainMusicButton"
            aria-label="Điều khiển nhạc">
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
    PHONG WEB V15
</footer>

<script>

/* INFORMATION CONTENT */

const panelData = {
    gaming: {
        title: "🎮 GAMING",
        content:
            "Chào mừng đến với Gaming Zone!\\n\\n" +
            "Khám phá các nội dung Roblox, Free Fire " +
            "và những trò chơi hấp dẫn."
    },

    python: {
        title: "🐍 PYTHON",
        content:
            "Khu vực lập trình Python.\\n\\n" +
            "Chia sẻ code, dự án Python và các kiến thức " +
            "lập trình."
    },

    technology: {
        title: "💻 TECHNOLOGY",
        content:
            "Khám phá công nghệ hiện đại.\\n\\n" +
            "Cập nhật các kiến thức công nghệ và kỹ thuật số."
    },

    setting: {
        title: "⚙️ SETTING",
        content:
            "Khu vực cài đặt.\\n\\n" +
            "Bạn có thể khám phá các nội dung Setting " +
            "được chia sẻ trên PHONG WEB."
    }
};

function showPanel(name) {
    const data = panelData[name];

    if (!data) return;

    document.getElementById("infoTitle").textContent =
        data.title;

    document.getElementById("infoContent").textContent =
        data.content.replace(/\\n/g, "\n");

    const panel = document.getElementById("info");

    panel.classList.add("show");

    panel.scrollIntoView({
        behavior: "smooth",
        block: "nearest"
    });
}

function closePanel() {
    document.getElementById("info").classList.remove("show");
}

/* MUSIC PLAYER */

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

musicButton.addEventListener("pointerdown", function(event) {
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
    print("       PHONG WEB V15")
    print("====================================")
    print("Server running on port:", PORT)
    print("Cloud pricing section: REMOVED")
    print("Five main cards: ASPECT RATIO 3:1")
    print("Advertisement scripts: REMOVED")
    print("====================================")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n[PHONG WEB] Server stopped.")
    finally:
        server.server_close()
