
import os
import mimetypes
from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import unquote

# ==========================================
# PHONG WEB V7 - LOOP MUSIC EDITION
# Nguyen Van Phong Website
# ==========================================

BASE_DIR = Path(__file__).resolve().parent
PORT = int(os.environ.get("PORT", 5000))

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
        linear-gradient(135deg, rgba(10,8,40,.80), rgba(35,12,75,.72)),
        url("/background.jpg") center/cover fixed no-repeat;
}

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

main {
    width: min(1100px, 92%);
    margin: 35px auto;
}

.hero {
    text-align: center;
    padding: 45px 15px;
    background: var(--glass);
    border: 1px solid #9c7aff66;
    border-radius: 24px;
    box-shadow: 0 0 30px #7a4dff22;
    backdrop-filter: blur(10px);
}

.hero h1 {
    font-size: clamp(28px, 7vw, 48px);
    margin-bottom: 14px;
    background: linear-gradient(90deg, #43d9ff, #c28aff);
    -webkit-background-clip: text;
    color: transparent;
}

.hero p {
    color: #ded9ff;
    line-height: 1.7;
}

.section-title {
    text-align: center;
    margin: 35px 0 20px;
    font-size: 25px;
    color: #75dcff;
}

.cards {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(210px, 1fr));
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

.music-box {
    margin-top: 28px;
    padding: 24px;
    text-align: center;
    background: var(--glass);
    border: 1px solid #8b70ff77;
    border-radius: 20px;
    backdrop-filter: blur(10px);
}

.music-box h2 {
    color: #8bdfff;
    margin-bottom: 8px;
}

.song-name {
    color: #e6d9ff;
    margin: 12px 0 18px;
}

.music-controls {
    display: flex;
    justify-content: center;
    align-items: center;
    flex-wrap: wrap;
    gap: 12px;
}

.music-controls button {
    border: 0;
    padding: 12px 22px;
    border-radius: 30px;
    color: white;
    font-weight: bold;
    background: linear-gradient(100deg, #168edc, #8249d9);
    cursor: pointer;
    transition: .2s;
}

.music-controls button:hover {
    filter: brightness(1.2);
    transform: scale(1.04);
}

.music-controls button.active {
    background: linear-gradient(100deg, #00b894, #168edc);
    box-shadow: 0 0 15px #42caff66;
}

input[type="range"] {
    accent-color: #66d7ff;
    cursor: pointer;
}

#seek {
    width: min(400px, 90%);
    margin-top: 18px;
}

.volume-row {
    margin-top: 14px;
    color: #ddd;
}

#volume {
    width: 120px;
    vertical-align: middle;
}

#time {
    margin-top: 8px;
    font-size: 13px;
    color: #cfc5ed;
}

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

footer {
    text-align: center;
    padding: 25px 12px;
    margin-top: 40px;
    color: #cfc6e9;
    background: rgba(8, 7, 30, .8);
    border-top: 1px solid #8b70ff55;
    font-size: 14px;
}

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
        padding: 35px 14px;
    }
}
</style>
</head>

<body>

<header>
    <img class="logo" src="/logo.png"
         alt="Logo Nguyễn Văn Phong"
         onerror="this.style.display='none'">

    <div class="brand">Nguyễn Văn Phong WebSite🔊</div>
</header>

<main>

    <section class="hero">
        <h1>WELCOME TO PHONG WEB</h1>
        <p>
            Chào mừng bạn đến với website của Nguyễn Văn Phong.<br>
            Khám phá Gaming, Python và công nghệ tại đây!
        </p>
    </section>

    <h2 class="section-title">✦ DANH MỤC ✦</h2>

    <section class="cards">

        <article class="card">
            <div class="emoji">🎮</div>
            <h3>GAMING</h3>
            <p>Thế giới game, giải trí và những nội dung gaming.</p>
            <button class="action"
                    onclick="showPanel('gaming')">
                Khám phá
            </button>
        </article>

        <article class="card">
            <div class="emoji">🐍</div>
            <h3>PYTHON</h3>
            <p>Lập trình Python, dự án và các sản phẩm sáng tạo.</p>
            <button class="action"
                    onclick="showPanel('python')">
                Khám phá
            </button>
        </article>

        <article class="card">
            <div class="emoji">💻</div>
            <h3>TECHNOLOGY</h3>
            <p>Công nghệ, phần mềm và những khám phá mới.</p>
            <button class="action"
                    onclick="showPanel('technology')">
                Khám phá
            </button>
        </article>

        <article class="card">
            <div class="emoji">📍</div>
            <h3>ĐỊNH VỊ XANH TÍM OB55</h3>
            <p>Mở mục Định Vị Xanh Tím OB55.</p>
            <button class="action"
                    onclick="showPanel('location')">
                Mở mục
            </button>
        </article>

        <article class="card">
            <div class="emoji">⚙️</div>
            <h3>SETTING</h3>
            <p>Cài đặt âm thanh và tùy chỉnh website.</p>
            <button class="action"
                    onclick="showPanel('setting')">
                Cài đặt
            </button>
        </article>

    </section>

    <section id="info" class="info-panel">
        <h2 id="info-title"></h2>
        <p id="info-content"></p>
        <button class="action" onclick="closePanel()">
            Đóng
        </button>
    </section>

    <!-- MUSIC PLAYER -->

    <section class="music-box">

        <h2>🎵 MUSIC PLAYER</h2>

        <div class="song-name">
            THƯƠNG NHAU ĐẾN THẾ
        </div>

        <audio id="audio" preload="metadata">
            <source src="/music.mp3" type="audio/mpeg">
            Trình duyệt của bạn không hỗ trợ phát nhạc.
        </audio>

        <div class="music-controls">

            <button id="playButton"
                    onclick="toggleMusic()">
                ▶ PHÁT NHẠC
            </button>

            <button onclick="stopMusic()">
                ■ DỪNG
            </button>

            <button id="loopButton"
                    onclick="toggleLoop()">
                🔁 LẶP: TẮT
            </button>

        </div>

        <div>
            <input id="seek"
                   type="range"
                   min="0"
                   max="100"
                   value="0"
                   step="0.1">
        </div>

        <div id="time">
            00:00 / 00:00
        </div>

        <div class="volume-row">
            Âm lượng:

            <input id="volume"
                   type="range"
                   min="0"
                   max="1"
                   value="0.8"
                   step="0.01">
        </div>

    </section>

</main>

<footer>
    © 2026 Nguyễn Văn Phong Website | PHONG WEB V7
</footer>

<script>

const audio = document.getElementById("audio");
const playButton = document.getElementById("playButton");
const loopButton = document.getElementById("loopButton");
const seek = document.getElementById("seek");
const volume = document.getElementById("volume");
const timeLabel = document.getElementById("time");

// ==========================================
// MUSIC PLAYER
// ==========================================

let loopEnabled = false;

function formatTime(seconds) {

    if (!Number.isFinite(seconds)) {
        return "00:00";
    }

    const minutes = Math.floor(seconds / 60);
    const secs = Math.floor(seconds % 60);

    return String(minutes).padStart(2, "0") + ":" +
           String(secs).padStart(2, "0");
}

// PHÁT / TẠM DỪNG

function toggleMusic() {

    if (audio.paused) {

        audio.play().then(() => {

            playButton.textContent = "⏸ TẠM DỪNG";

        }).catch(() => {

            alert("Không phát được nhạc. Hãy kiểm tra file music.mp3.");

        });

    } else {

        audio.pause();

        playButton.textContent = "▶ PHÁT NHẠC";

    }
}

// DỪNG NHẠC VÀ TẮT LOOP

function stopMusic() {

    audio.pause();
    audio.currentTime = 0;

    loopEnabled = false;
    audio.loop = false;

    loopButton.textContent = "🔁 LẶP: TẮT";
    loopButton.classList.remove("active");

    playButton.textContent = "▶ PHÁT NHẠC";

    updateTime();
}

// BẬT / TẮT LẶP NHẠC

function toggleLoop() {

    loopEnabled = !loopEnabled;

    audio.loop = loopEnabled;

    if (loopEnabled) {

        loopButton.textContent = "🔁 LẶP: BẬT";
        loopButton.classList.add("active");

    } else {

        loopButton.textContent = "🔁 LẶP: TẮT";
        loopButton.classList.remove("active");

    }

}

// CẬP NHẬT NÚT PHÁT NHẠC

audio.addEventListener("play", () => {

    playButton.textContent = "⏸ TẠM DỪNG";

});

audio.addEventListener("pause", () => {

    playButton.textContent = "▶ PHÁT NHẠC";

});

audio.addEventListener("ended", () => {

    if (!loopEnabled) {

        playButton.textContent = "▶ PHÁT NHẠC";

    }

});

// CẬP NHẬT THỜI GIAN

audio.addEventListener("loadedmetadata", updateTime);

audio.addEventListener("timeupdate", () => {

    if (
        Number.isFinite(audio.duration) &&
        audio.duration > 0
    ) {

        seek.value =
            (audio.currentTime / audio.duration) * 100;

    }

    updateTime();

});

function updateTime() {

    timeLabel.textContent =
        formatTime(audio.currentTime) + " / " +
        formatTime(audio.duration);

}

// TUA NHẠC

seek.addEventListener("input", () => {

    if (
        Number.isFinite(audio.duration) &&
        audio.duration > 0
    ) {

        audio.currentTime =
            (Number(seek.value) / 100) * audio.duration;

    }

});

// ĐIỀU CHỈNH ÂM LƯỢNG

volume.addEventListener("input", () => {

    audio.volume = Number(volume.value);

});

audio.volume = Number(volume.value);

// ==========================================
// WEBSITE PANELS
// ==========================================

const panels = {

    gaming: {
        title: "🎮 GAMING",
        content: "Chào mừng đến với khu vực GAMING của Nguyễn Văn Phong. Nội dung game sẽ được cập nhật tại đây."
    },

    python: {
        title: "🐍 PYTHON",
        content: "Khu vực PYTHON: các dự án lập trình, mã nguồn và sản phẩm Python."
    },

    technology: {
        title: "💻 TECHNOLOGY",
        content: "Khu vực TECHNOLOGY: khám phá công nghệ, phần mềm và các thủ thuật hữu ích."
    },

    location: {
        title: "📍 ĐỊNH VỊ XANH TÍM OB55",
        content: "Bạn đã mở mục ĐỊNH VỊ XANH TÍM OB55. Hãy bổ sung đường dẫn hoặc nội dung dịch vụ của bạn tại đây khi có."
    },

    setting: {
        title: "⚙️ SETTING",
        content: "Cài đặt âm thanh: sử dụng thanh âm lượng trong mục Music Player để điều chỉnh nhạc. Bạn cũng có thể bật hoặc tắt chế độ lặp nhạc liên tục."
    }

};

function showPanel(name) {

    const item = panels[name];

    if (!item) return;

    document.getElementById("info-title").textContent =
        item.title;

    document.getElementById("info-content").textContent =
        item.content;

    document.getElementById("info").style.display = "block";

    document.getElementById("info").scrollIntoView({

        behavior: "smooth",
        block: "center"

    });

}

function closePanel() {

    document.getElementById("info").style.display = "none";

}

</script>

</body>
</html>
"""


class Website(BaseHTTPRequestHandler):

    def do_GET(self):

        requested_path = unquote(
            self.path.split("?", 1)[0]
        )

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

        # CHỈ CHO PHÉP CÁC FILE TÀI NGUYÊN

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


if __name__ == "__main__":

    server = ThreadingHTTPServer(
        ("0.0.0.0", PORT),
        Website
    )

    print("======================================")
    print(" PHONG WEB V7 - LOOP MUSIC EDITION")
    print(" Port:", PORT)
    print("======================================")

    try:

        server.serve_forever()

    except KeyboardInterrupt:

        print("Dang dung PHONG WEB V7...")

    finally:

        server.server_close()
