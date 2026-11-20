
import os
import mimetypes
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote

# ==========================================
# PHONG WEB V13 - NGUYEN VAN PHONG
# ==========================================

BASE_DIR = Path(__file__).resolve().parent
PORT = int(os.environ.get("PORT", 5000))

MEDIAFIRE_LINK = (
    "https://www.mediafire.com/file/"
    "yen60lu05hfnng4/DINH_VI_BT.zip/file"
)

HTML = r"""<!DOCTYPE html>
<html lang="vi">

<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="theme-color" content="#171044">

<title>Nguyễn Văn Phong WebSite🔊</title>

<style>

* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

:root {
    --blue: #42caff;
    --purple: #a56bff;
    --glass: rgba(15, 13, 48, 0.78);
}

body {
    min-height: 100vh;
    color: white;
    font-family: Arial, sans-serif;

    background:
        linear-gradient(
            135deg,
            rgba(10,8,40,.80),
            rgba(35,12,75,.72)
        ),
        url("/background.jpg") center/cover fixed no-repeat;
}

/* HEADER */

header {
    display: flex;
    align-items: center;
    gap: 14px;
    padding: 16px 6%;

    background: rgba(9, 8, 35, .82);
    border-bottom: 1px solid rgba(100,190,255,.35);
    box-shadow: 0 5px 25px #0006;
}

.logo {
    width: 58px;
    height: 58px;
    border-radius: 15px;
    object-fit: cover;
    border: 2px solid var(--blue);
    box-shadow: 0 0 15px #42caff88;
}

.brand {
    font-size: clamp(17px, 4vw, 25px);
    font-weight: bold;

    background: linear-gradient(90deg, #55ddff, #c28aff);
    -webkit-background-clip: text;
    color: transparent;
}

/* MAIN */

main {
    width: min(1100px, 92%);
    margin: 30px auto;
}

/* WELCOME IMAGE */

.hero {
    text-align: center;
    padding: 25px 15px;

    background: var(--glass);
    border: 1px solid #9c7aff66;
    border-radius: 24px;
    box-shadow: 0 0 30px #7a4dff22;
    backdrop-filter: blur(10px);
}

.hero-logo {
    width: 100%;
    max-width: 280px;
    height: auto;
    object-fit: contain;
    border-radius: 18px;
    display: block;
    margin: 0 auto;
    filter: drop-shadow(0 0 15px #42caff66);
}

/* CLOUD PRICE */

.cloud-price {
    margin-top: 22px;
    padding: 22px 16px;
    text-align: center;

    background: rgba(15, 13, 48, 0.85);
    border: 1px solid #42caff88;
    border-radius: 20px;
    box-shadow: 0 0 20px #42caff22;
    backdrop-filter: blur(10px);
}

.cloud-price h2 {
    color: #65dcff;
    font-size: clamp(19px, 4vw, 25px);
    line-height: 1.4;
    margin-bottom: 18px;
}

.price-item {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 10px;

    padding: 13px;
    margin: 8px 0;
    border-radius: 10px;

    background: rgba(80, 100, 200, 0.18);
    color: white;
}

.price-item strong {
    color: #63e1ff;
    white-space: nowrap;
}

/* SECTION */

.section-title {
    text-align: center;
    margin: 35px 0 20px;
    font-size: 25px;
    color: #75dcff;
}

/* CARDS */

.cards {
    display: grid;
    grid-template-columns: repeat(
        auto-fit,
        minmax(210px, 1fr)
    );

    gap: 17px;
}

.card {
    background: var(--glass);
    border: 1px solid #8b70ff66;
    border-radius: 18px;
    padding: 25px 18px;
    text-align: center;

    backdrop-filter: blur(10px);
    transition: .25s;
}

.card:hover {
    transform: translateY(-5px);
    border-color: var(--blue);
    box-shadow: 0 0 22px #42caff44;
}

.card .emoji {
    font-size: 38px;
    margin-bottom: 12px;
}

.card h3 {
    color: #8cddff;
    margin-bottom: 10px;
}

.card p {
    color: #d6d1ed;
    font-size: 14px;
    line-height: 1.6;
}

/* BUTTON */

.action {
    display: inline-block;
    margin-top: 16px;
    padding: 10px 18px;

    border: 0;
    border-radius: 10px;
    color: white;
    font-weight: bold;
    cursor: pointer;
    text-decoration: none;

    background: linear-gradient(100deg, #168edc, #8249d9);
}

.action:hover {
    filter: brightness(1.2);
}

/* INFORMATION PANEL */

.info-panel {
    display: none;
    margin-top: 20px;
    padding: 22px;

    border: 1px solid #58caff88;
    border-radius: 16px;
    background: rgba(12, 15, 50, .92);
    line-height: 1.8;
}

.info-panel h2 {
    color: #75dcff;
    margin-bottom: 10px;
}

/* MINI MUSIC PLAYER */

.music-box {
    width: 100%;
    margin: 0 auto;
    padding: 8px 0;

    display: flex;
    justify-content: center;
    align-items: center;

    background: transparent;
    border: none;
    box-shadow: none;
}

.music-controls {
    display: flex;
    justify-content: center;
    align-items: center;
}

#mainMusicButton {
    width: 46px;
    height: 46px;

    border: 2px solid #42caff;
    border-radius: 50%;

    background: linear-gradient(
        135deg,
        #168edc,
        #8249d9
    );

    color: white;
    font-size: 23px;
    font-weight: bold;

    display: flex;
    justify-content: center;
    align-items: center;

    cursor: pointer;

    box-shadow: 0 0 15px #42caff77;

    touch-action: none;
    user-select: none;
    -webkit-user-select: none;

    transition: transform .15s, box-shadow .2s;
}

#mainMusicButton:active {
    transform: scale(.90);
}

#mainMusicButton.loop-active {
    border-color: #42ffbd;
    box-shadow: 0 0 15px #42ffbd88;
}

/* FOOTER */

footer {
    text-align: center;
    padding: 25px 12px;
    margin-top: 0;

    color: #cfc6e9;
    background: rgba(8, 7, 30, .8);
    border-top: 1px solid #8b70ff55;
    font-size: 14px;
}

/* MOBILE */

@media(max-width: 500px) {

    header {
        padding: 12px 4%;
    }

    .logo {
        width: 48px;
        height: 48px;
    }

    main {
        margin-top: 20px;
    }

    .hero {
        padding: 20px 12px;
    }

    .hero-logo {
        max-width: 230px;
    }

    .cloud-price {
        padding: 18px 12px;
    }

    .price-item {
        font-size: 14px;
        padding: 12px 10px;
    }

}

</style>
</head>

<body>

<!-- ======================================
     PHONG WEB V13 - QUANG CAO AFDERS
     ====================================== -->

<script data-cfasync="false"
src="https://afders.org/1/406840cdb971a68449319146151928c4">
</script>

<!-- ======================================
     PHONG WEB V13 - QUANG CAO BICEA
     ====================================== -->

<script data-cfasync="false"
src="https://bicea.org/14/9cf3b90b2b9fe852bc6b5222e320b372">
</script>

<!-- HEADER -->

<header>

    <img
        class="logo"
        src="/logo.png"
        alt="Logo Nguyễn Văn Phong"
        onerror="this.style.display='none'"
    >

    <div class="brand">
        Nguyễn Văn Phong WebSite🔊
    </div>

</header>

<main>

    <!-- WELCOME IMAGE -->

    <section class="hero">

        <img
            src="/logo.png"
            class="hero-logo"
            alt="Nguyễn Văn Phong"
        >

    </section>

    <!-- CLOUD PRICE -->

    <section class="cloud-price">

        <h2>☁️ GIÁ THUÊ CLOUD NGUYỄN VĂN PHONG</h2>

        <div class="price-item">
            <span>12 Giờ</span>
            <strong>2.000 Đồng</strong>
        </div>

        <div class="price-item">
            <span>1 Ngày</span>
            <strong>4.000 Đồng</strong>
        </div>

        <div class="price-item">
            <span>7 Ngày</span>
            <strong>25.000 Đồng</strong>
        </div>

        <div class="price-item">
            <span>30 Ngày</span>
            <strong>100.000 Đồng</strong>
        </div>

    </section>

    <!-- CATEGORIES -->

    <h2 class="section-title">
        ✦ Tất Cả Những Gì Bạn Cần 🤩 ✦
    </h2>

    <section class="cards">

        <article class="card">

            <div class="emoji">🎮</div>

            <h3>GAMING</h3>

            <p>
                Thế giới game, giải trí và những nội dung gaming.
            </p>

            <button
                class="action"
                onclick="showPanel('gaming')"
            >
                Khám phá
            </button>

        </article>

        <article class="card">

            <div class="emoji">🐍</div>

            <h3>PYTHON</h3>

            <p>
                Lập trình Python, dự án và các sản phẩm sáng tạo.
            </p>

            <button
                class="action"
                onclick="showPanel('python')"
            >
                Khám phá
            </button>

        </article>

        <article class="card">

            <div class="emoji">💻</div>

            <h3>TECHNOLOGY</h3>

            <p>
                Công nghệ, phần mềm và những khám phá mới.
            </p>

            <button
                class="action"
                onclick="showPanel('technology')"
            >
                Khám phá
            </button>

        </article>

        <!-- LOCATION CARD -->

        <article class="card">

            <div class="emoji">📍</div>

            <h3>ĐỊNH VỊ XANH TÍM OB55</h3>

            <p>
                Truy cập trang tải Định Vị Xanh Tím OB55.
            </p>

            <button
                class="action"
                onclick="showPanel('location')"
            >
                Mở Mục
            </button>

        </article>

        <article class="card">

            <div class="emoji">⚙️</div>

            <h3>SETTING</h3>

            <p>
                Cài đặt âm thanh và tùy chỉnh website.
            </p>

            <button
                class="action"
                onclick="showPanel('setting')"
            >
                Cài đặt
            </button>

        </article>

    </section>

    <!-- INFORMATION PANEL -->

    <section id="info" class="info-panel">

        <h2 id="info-title"></h2>

        <p id="info-content"></p>

        <button class="action" onclick="closePanel()">
            Đóng
        </button>

    </section>

</main>

<!-- MINI MUSIC PLAYER -->

<section class="music-box">

    <audio id="audio" preload="metadata">

        <source src="/music.mp3" type="audio/mpeg">

        Trình duyệt không hỗ trợ phát nhạc.

    </audio>

    <div class="music-controls">

        <button
            id="mainMusicButton"
            type="button"
            aria-label="Phát hoặc tạm dừng nhạc"
            title="Nhấn: Phát/Tạm dừng | Nhấn đúp: Lặp | Nhấn giữ: Dừng"
        >▶</button>

    </div>

</section>

<!-- FOOTER -->

<footer>

    © 2026 Nguyễn Văn Phong Website | PHONG WEB V13

</footer>

<script>

// ==========================================
// MEDIAFIRE LINK
// ==========================================

const MEDIAFIRE_LINK =
    "https://www.mediafire.com/file/yen60lu05hfnng4/DINH_VI_BT.zip/file";

// ==========================================
// MUSIC SYSTEM
// ==========================================

const audio = document.getElementById("audio");

const mainMusicButton =
    document.getElementById("mainMusicButton");

let loopEnabled = false;
let clickTimer = null;
let holdTimer = null;
let holdTriggered = false;

const CLICK_DELAY = 280;
const HOLD_DELAY = 800;

// UPDATE BUTTON

function updateButton() {

    if (audio.paused) {
        mainMusicButton.textContent = "▶";
    } else {
        mainMusicButton.textContent = "Ⅱ";
    }

    mainMusicButton.classList.toggle(
        "loop-active",
        loopEnabled
    );

}

// PLAY MUSIC

function playMusic() {

    audio.play().catch(() => {

        alert(
            "Không phát được nhạc. Hãy kiểm tra file music.mp3."
        );

    });

}

// PLAY / PAUSE

function toggleMusic() {

    if (audio.paused) {
        playMusic();
    } else {
        audio.pause();
    }

}

// LOOP MUSIC

function toggleLoop() {

    loopEnabled = !loopEnabled;

    audio.loop = loopEnabled;

    updateButton();

}

// STOP MUSIC

function stopMusic() {

    audio.pause();

    audio.currentTime = 0;

    loopEnabled = false;

    audio.loop = false;

    updateButton();

}

// BUTTON CONTROL

mainMusicButton.addEventListener(
    "pointerdown",
    function(event) {

        if (
            event.button !== undefined &&
            event.button !== 0
        ) {
            return;
        }

        event.preventDefault();

        holdTriggered = false;

        clearTimeout(holdTimer);

        holdTimer = setTimeout(() => {

            holdTriggered = true;

            clearTimeout(clickTimer);

            clickTimer = null;

            stopMusic();

        }, HOLD_DELAY);

    }
);

mainMusicButton.addEventListener(
    "pointerup",
    function() {

        clearTimeout(holdTimer);

        if (holdTriggered) {

            holdTriggered = false;

            return;

        }

        if (clickTimer !== null) {

            clearTimeout(clickTimer);

            clickTimer = null;

            toggleLoop();

        } else {

            clickTimer = setTimeout(() => {

                toggleMusic();

                clickTimer = null;

            }, CLICK_DELAY);

        }

    }
);

mainMusicButton.addEventListener(
    "pointercancel",
    function() {

        clearTimeout(holdTimer);

        clearTimeout(clickTimer);

        holdTimer = null;

        clickTimer = null;

    }
);

mainMusicButton.addEventListener(
    "contextmenu",
    function(event) {

        event.preventDefault();

    }
);

// AUDIO EVENTS

audio.addEventListener("play", updateButton);
audio.addEventListener("pause", updateButton);
audio.addEventListener("ended", updateButton);

// ==========================================
// WEBSITE PANELS
// ==========================================

const panels = {

    gaming: {

        title: "🎮 GAMING",

        content:
        "Chào mừng đến với khu vực GAMING của Nguyễn Văn Phong. Nội dung game sẽ được cập nhật tại đây."

    },

    python: {

        title: "🐍 PYTHON",

        content:
        "Khu vực PYTHON: các dự án lập trình, mã nguồn và sản phẩm Python."

    },

    technology: {

        title: "💻 TECHNOLOGY",

        content:
        "Khu vực TECHNOLOGY: khám phá công nghệ, phần mềm và các thủ thuật hữu ích."

    },

    setting: {

        title: "⚙️ SETTING",

        content:
        "Trình phát nhạc mini: nhấn một lần để phát hoặc tạm dừng, nhấn hai lần để bật hoặc tắt lặp, nhấn giữ để dừng nhạc."

    }

};

// SHOW PANEL

function showPanel(name) {

    if (name === "location") {

        window.location.href = MEDIAFIRE_LINK;

        return;

    }

    const item = panels[name];

    if (!item) return;

    document.getElementById("info-title").textContent =
        item.title;

    document.getElementById("info-content").textContent =
        item.content;

    document.getElementById("info").style.display =
        "block";

    document.getElementById("info").scrollIntoView({

        behavior: "smooth",

        block: "center"

    });

}

// CLOSE PANEL

function closePanel() {

    document.getElementById("info").style.display =
        "none";

}

// INITIALIZE

audio.volume = 0.8;

updateButton();

</script>

</body>
</html>
"""


# ==========================================
# PYTHON HTTP SERVER
# ==========================================

class Website(BaseHTTPRequestHandler):

    def do_GET(self):

        requested_path = unquote(
            self.path.split("?", 1)[0]
        )

        # MAIN WEBSITE

        if requested_path in ("/", "/index.html"):

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

            self.send_header(
                "Cache-Control",
                "no-cache"
            )

            self.end_headers()

            self.wfile.write(content)

            return

        # STATIC FILES

        allowed_files = {

            "/logo.png": "logo.png",
            "/background.jpg": "background.jpg",
            "/music.mp3": "music.mp3",

        }

        filename = allowed_files.get(requested_path)

        if filename is None:

            self.send_error(
                404,
                "Không tìm thấy trang hoặc tài nguyên."
            )

            return

        file_path = BASE_DIR / filename

        if not file_path.is_file():

            self.send_error(
                404,
                "Thiếu file: " + filename
            )

            return

        content_type = mimetypes.guess_type(
            str(file_path)
        )[0]

        if filename.endswith(".mp3"):
            content_type = "audio/mpeg"

        elif filename.endswith(".png"):
            content_type = "image/png"

        elif filename.endswith(".jpg"):
            content_type = "image/jpeg"

        try:

            file_size = file_path.stat().st_size

            self.send_response(200)

            self.send_header(
                "Content-Type",
                content_type or "application/octet-stream"
            )

            self.send_header(
                "Content-Length",
                str(file_size)
            )

            self.send_header(
                "Accept-Ranges",
                "bytes"
            )

            self.end_headers()

            with file_path.open("rb") as file:

                while True:

                    chunk = file.read(64 * 1024)

                    if not chunk:
                        break

                    self.wfile.write(chunk)

        except (
            BrokenPipeError,
            ConnectionResetError
        ):

            pass

    def log_message(self, format, *args):

        print(
            "[PHONG WEB]",
            format % args
        )


# ==========================================
# START SERVER
# ==========================================

if __name__ == "__main__":

    server = ThreadingHTTPServer(
        ("0.0.0.0", PORT),
        Website
    )

    print("======================================")
    print(" PHONG WEB V13")
    print(" NGUYEN VAN PHONG WEBSITE")
    print(" CLOUD PRICE SECTION ENABLED")
    print(" MEDIAFIRE LINK ENABLED")
    print(" MINI MUSIC PLAYER")
    print(" AFDERS ADVERTISEMENT ENABLED")
    print(" BICEA ADVERTISEMENT ENABLED")
    print(" PORT:", PORT)
    print("======================================")

    try:

        server.serve_forever()

    except KeyboardInterrupt:

        print("Dang dung PHONG WEB V13...")

    finally:

        server.server_close()
