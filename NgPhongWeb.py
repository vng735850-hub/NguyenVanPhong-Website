
import os
import mimetypes
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote

# ==========================================
# PHONG WEB V18
# MUSIC BUTTON MINI CIRCLE
# ==========================================

BASE_DIR = Path(__file__).resolve().parent
PORT = int(os.environ.get("PORT", 5000))

MEDIAFIRE_LINK = "https://www.mediafire.com/file/yen60lu05hfnng4/DINH_VI_BT.zip/file"
LINK4M_LINK = "https://link4m.net/lbatN"

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
    padding-bottom: 90px;
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

/* LINK4M PAGE */

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
    border-radius: 30px;
    background: linear-gradient(135deg, #1685ff, #7139df);
    color: white;
    font-size: 18px;
    font-weight: bold;
    text-decoration: none;
    box-shadow: 0 5px 20px rgba(0,100,255,0.4);
}

.cross-link-button:hover {
    transform: scale(1.05);
}

.back-button {
    display: inline-block;
    margin-top: 25px;
    color: #cbd8ff;
    text-decoration: none;
    font-size: 14px;
}

/* MINI MUSIC BUTTON */

.music-mini {
    position: fixed;
    bottom: 18px;
    left: 50%;
    transform: translateX(-50%);
    width: 58px;
    height: 58px;
    border-radius: 50%;
    border: 2px solid rgba(255,255,255,0.8);
    background: linear-gradient(135deg, #1685ff, #7736d5);
    color: white;
    font-size: 25px;
    display: flex;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    z-index: 9999;
    box-shadow: 0 0 18px rgba(40,120,255,0.6);
    transition: 0.2s;
    -webkit-tap-highlight-color: transparent;
}

.music-mini:active {
    transform: translateX(-50%) scale(0.9);
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

    .music-mini {
        width: 54px;
        height: 54px;
        bottom: 15px;
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

<!-- INTERMEDIATE PAGE -->

<div id="linkPage">

    <div class="link-icon">🔐</div>

    <h2>
        BẠN CẦN VƯỢT LINK ĐỂ LẤY FILE MEDIAFIRE
    </h2>

    <div class="link-description">
        Vui lòng nhấn nút bên dưới để tiến hành vượt link.
        <br>
        Sau khi hoàn thành, bạn sẽ tiếp tục đến bước nhận file.
    </div>

    <a
        class="cross-link-button"
        href="https://link4m.net/lbatN"
        target="_blank"
        rel="noopener noreferrer"
    >
        🔓 VƯỢT LINK
    </a>

    <br>

    <a class="back-button" href="/">
        ← QUAY LẠI TRANG CHỦ
    </a>

</div>

</main>

<!-- MINI MUSIC PLAYER -->

<button
    class="music-mini"
    id="musicButton"
    aria-label="Bật hoặc tắt nhạc"
    title="Bật / Tắt nhạc"
>
    <span class="music-icon" id="musicIcon">▶</span>
</button>

<audio id="audio" preload="metadata">
    <source src="/music.mp3" type="audio/mpeg">
</audio>

<footer>
    © 2026 Nguyễn Văn Phong Website
    <br><br>
    PHONG WEB V18
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
// MUSIC ON / OFF
// ON  = PLAY MUSIC + LOOP
// OFF = STOP MUSIC + DISABLE LOOP
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

            // Turn ON music and looping together
            audio.loop = true;

            await audio.play();

            isPlaying = true;

        } catch(error) {

            audio.loop = false;
            isPlaying = false;

            console.log("Music error:", error);

        }

    } else {

        // Turn OFF music and looping together
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

    def do_GET(self):

        path = unquote(self.path.split("?")[0])

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
    print("          PHONG WEB V18")
    print("====================================")
    print("Server running on port:", PORT)
    print("Link4m intermediate page: ENABLED")
    print("Mini circular music button: ENABLED")
    print("Music looping: AUTO ON/OFF")
    print("Location aspect ratio: 7:2")
    print("Advertisements: REMOVED")
    print("====================================")

    try:
        server.serve_forever()

    except KeyboardInterrupt:
        print("\n[PHONG WEB] Server stopped.")

    finally:
        server.server_close()
