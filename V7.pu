
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

# ==========================================
# NGUYEN VAN PHONG WEBSITE V7
# ==========================================

HTML = r"""
<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
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
        linear-gradient(rgba(0,0,20,.35), rgba(0,0,20,.78)),
        url('/background.jpg');
    background-size: cover;
    background-position: center top;
    background-attachment: fixed;
    background-repeat: no-repeat;
}

/* HEADER */

header {
    display: flex;
    align-items: center;
    justify-content: flex-start;
    gap: 12px;
    padding: 12px 15px;
    min-height: 88px;
    background: rgba(0,0,30,.92);
    border-bottom: 2px solid #00c8ff;
    box-shadow: 0 0 18px #007bff;
}

.header-logo {
    width: 66px;
    height: 66px;
    flex: 0 0 66px;
    object-fit: cover;
    object-position: center;
    border: 2px solid #35d9ff;
    border-radius: 12px;
    box-shadow: 0 0 10px #00c8ff, 0 0 18px #9b35ff;
}

.header-title {
    color: #35d9ff;
    font-size: clamp(18px, 5vw, 27px);
    font-weight: 900;
    line-height: 1.2;
    text-shadow: 0 0 8px #008cff, 0 0 15px #7b2cff;
}

/* MAIN */

.container {
    max-width: 900px;
    margin: auto;
    padding: 40px 15px;
    text-align: center;
}

h1 {
    font-size: 32px;
    text-shadow: 0 0 12px #00c8ff;
}

.subtitle {
    margin: 20px 0 30px;
    font-size: 17px;
    line-height: 1.8;
}

/* CARDS */

.cards {
    display: grid;
    grid-template-columns: repeat(2, minmax(0,1fr));
    gap: 15px;
    margin-top: 30px;
}

.card {
    background: rgba(0,10,35,.92);
    border: 2px solid #00c8ff;
    border-radius: 15px;
    padding: 25px 10px;
    min-height: 130px;
    box-shadow: 0 0 15px #008cff;
    transition: .3s;
}

.card:hover {
    transform: translateY(-5px);
    box-shadow: 0 0 25px #00c8ff;
}

.card h2 {
    color: #36d9ff;
    font-size: 19px;
    margin-bottom: 12px;
}

.card p {
    font-size: 14px;
    line-height: 1.7;
}

.folder-link {
    display: block;
    color: white;
    text-decoration: none;
}

/* OB55 */

.ob55 .card {
    border-color: #a64dff;
    box-shadow: 0 0 15px #8c38ff;
}

.ob55 h2 {
    color: #d5a5ff;
}

/* SETTING */

.setting .card {
    border-color: #b04cff;
    box-shadow: 0 0 15px #a000ff;
}

.setting h2 {
    color: #d69aff;
}

/* MUSIC */

.music-folder {
    cursor: pointer;
    color: white;
    text-decoration: none;
}

.music-folder .card {
    border-color: #ff45d4;
    background: rgba(35,0,45,.94);
    box-shadow: 0 0 15px #d000ff;
}

.music-folder h2 {
    color: #ff9bea;
}

.music-folder.active .card {
    border-color: #ff00dd;
    box-shadow: 0 0 30px #ff00dd;
}

/* MUSIC PLAYER */

.player {
    display: none;
    margin-top: 25px;
    padding: 22px;
    background: rgba(25,0,45,.95);
    border: 2px solid #ff45d4;
    border-radius: 18px;
    box-shadow: 0 0 20px #d000ff;
}

.player.show {
    display: block;
}

.player h2 {
    color: #ff9bea;
    margin-bottom: 10px;
}

.player button {
    border: 0;
    border-radius: 25px;
    background: linear-gradient(90deg,#a000ff,#ff35cb);
    color: white;
    padding: 12px 25px;
    margin: 12px;
    font-size: 16px;
    font-weight: bold;
}

.player input {
    width: 100%;
    accent-color: #ff35cb;
    margin: 12px 0;
}

.time {
    display: flex;
    justify-content: space-between;
    font-size: 12px;
    color: #ffc5f4;
}

#status {
    color: #ffc5f4;
    font-size: 13px;
    margin-top: 8px;
}

/* BUTTON */

button.main-button {
    margin-top: 35px;
    padding: 15px 30px;
    background: linear-gradient(90deg,#006aff,#00d9ff);
    color: white;
    border: 2px solid white;
    border-radius: 30px;
    font-size: 17px;
    font-weight: bold;
    box-shadow: 0 0 20px #00aaff;
}

/* FOOTER */

footer {
    margin-top: 50px;
    padding: 25px;
    text-align: center;
    background: rgba(0,0,20,.92);
    color: #b9dcff;
    line-height: 2;
}

/* MOBILE */

@media(max-width:500px) {
    h1 {
        font-size: 26px;
    }

    .cards {
        grid-template-columns: 1fr;
    }

    .header-logo {
        width: 58px;
        height: 58px;
        flex-basis: 58px;
    }

    header {
        gap: 10px;
        padding: 10px;
    }
}
</style>
</head>

<body>

<!-- HEADER: ANH FREE FIRE + TEN WEBSITE -->

<header>
    <img
        class="header-logo"
        src="/logo.png"
        alt="Ảnh Nguyễn Văn Phong"
        onerror="this.style.display='none'"
    >

    <div class="header-title">
        Nguyễn Văn Phong WebSite🔊
    </div>
</header>

<!-- NOI DUNG CHINH -->

<div class="container">

    <h1>NGUYỄN VĂN PHONG</h1>

    <div class="subtitle">
        WELCOME TO MY WEBSITE
        <br>
        🔥 GAMING - PYTHON - TECHNOLOGY 🔥
    </div>

    <div class="cards">

        <!-- GAMING -->

        <div class="card">
            <h2>🎮 GAMING</h2>
            <p>Roblox - Free Fire</p>
            <p>Gaming Zone</p>
        </div>

        <!-- PYTHON -->

        <div class="card">
            <h2>💻 PYTHON</h2>
            <p>Lập trình Python</p>
            <p>Code &amp; Development</p>
        </div>

        <!-- TECHNOLOGY -->

        <div class="card">
            <h2>🚀 TECHNOLOGY</h2>
            <p>Công nghệ hiện đại</p>
            <p>Digital Technology</p>
        </div>

        <!-- DINH VI OB55 -->

        <a
            class="folder-link ob55"
            href="https://www.mediafire.com/file/yen60lu05hfnng4/DINH_VI_BT.zip/file"
            target="_blank"
            rel="noopener"
        >
            <div class="card">
                <h2>📁 ĐỊNH VỊ</h2>
                <p>ĐỊNH VỊ XANH TÍM OB55</p>
                <p>💜 NHẤN ĐỂ TẢI</p>
            </div>
        </a>

        <!-- SETTING -->

        <a
            class="folder-link setting"
            href="https://fnote.net/notes/4fRaV9"
            target="_blank"
            rel="noopener"
        >
            <div class="card">
                <h2>📁 SETTING</h2>
                <p>SETTING TREO CUỐI MAP</p>
                <p>⚡ NHẤN ĐỂ TRUY CẬP</p>
            </div>
        </a>

        <!-- MUSIC -->

        <div
            class="music-folder"
            id="musicFolder"
            onclick="toggleMusic()"
        >
            <div class="card">
                <h2>🎵 ÂM NHẠC</h2>
                <p>THƯƠNG NHAU ĐẾN THẾ</p>
                <p id="folderStatus">💗 NHẤN ĐỂ NGHE NHẠC</p>
            </div>
        </div>

    </div>

    <!-- MUSIC PLAYER -->

    <div class="player" id="player">

        <h2>🎵 THƯƠNG NHAU ĐẾN THẾ</h2>

        <p>Đang phát nhạc trên PHONG WEB</p>

        <audio id="audio" preload="metadata">
            <source src="/music.mp3" type="audio/mpeg">
            Trình duyệt không hỗ trợ audio.
        </audio>

        <button onclick="playPause()" id="playBtn">
            ▶ PHÁT NHẠC
        </button>

        <div class="time">
            <span id="current">00:00</span>
            <span id="duration">00:00</span>
        </div>

        <input
            type="range"
            id="progress"
            value="0"
            min="0"
            max="100"
            oninput="seekMusic()"
        >

        <p>🔊 Âm lượng</p>

        <input
            type="range"
            id="volume"
            min="0"
            max="1"
            step="0.01"
            value="0.8"
            oninput="changeVolume()"
        >

        <p id="status">Sẵn sàng phát nhạc</p>

    </div>

    <button class="main-button" onclick="welcome()">
        KHÁM PHÁ NGAY 🚀
    </button>

</div>

<!-- FOOTER -->

<footer>
    👑 © 2026 NGUYỄN VĂN PHONG
    <br>
    All Rights Reserved
    <br>
    PHONG WEB VERSION 7.0
</footer>

<script>

const audio = document.getElementById("audio");
const player = document.getElementById("player");
const folder = document.getElementById("musicFolder");
const playBtn = document.getElementById("playBtn");
const statusText = document.getElementById("status");

audio.volume = 0.8;

// MO THU MUC AM NHAC

function toggleMusic() {

    player.classList.add("show");

    if (audio.paused) {
        startMusic();
    } else {
        audio.pause();
    }
}

// PHAT NHAC

function startMusic() {

    audio.play().then(() => {

        folder.classList.add("active");

        playBtn.innerText = "⏸ TẠM DỪNG";

        document.getElementById("folderStatus").innerText =
            "🎶 ĐANG PHÁT NHẠC";

        statusText.innerText = "Đang phát nhạc";

    }).catch((error) => {

        console.error("Audio play error:", error);

        statusText.innerText =
            "Không phát được nhạc. Kiểm tra file music.mp3.";

    });
}

// PHAT / TAM DUNG

function playPause() {

    if (audio.paused) {
        startMusic();
    } else {
        audio.pause();
    }
}

// SU KIEN TAM DUNG

audio.addEventListener("pause", () => {

    folder.classList.remove("active");

    playBtn.innerText = "▶ PHÁT NHẠC";

    document.getElementById("folderStatus").innerText =
        "💗 ĐÃ TẠM DỪNG";

});

// SU KIEN PHAT

audio.addEventListener("play", () => {

    folder.classList.add("active");

    playBtn.innerText = "⏸ TẠM DỪNG";

    document.getElementById("folderStatus").innerText =
        "🎶 ĐANG PHÁT NHẠC";

});

// CAP NHAT THOI GIAN

audio.addEventListener("timeupdate", () => {

    if (audio.duration) {

        document.getElementById("progress").value =
            (audio.currentTime / audio.duration) * 100;

        document.getElementById("current").innerText =
            formatTime(audio.currentTime);

        document.getElementById("duration").innerText =
            formatTime(audio.duration);

    }
});

// NHAC KET THUC

audio.addEventListener("ended", () => {

    playBtn.innerText = "▶ PHÁT LẠI";

    document.getElementById("folderStatus").innerText =
        "🎵 NHẠC ĐÃ KẾT THÚC";

});

// BAO LOI

audio.addEventListener("error", () => {

    statusText.innerText =
        "Lỗi tải nhạc: hãy kiểm tra music.mp3.";

});

// TUA NHAC

function seekMusic() {

    if (audio.duration) {

        audio.currentTime =
            audio.duration *
            document.getElementById("progress").value / 100;

    }
}

// CHINH AM LUONG

function changeVolume() {

    audio.volume =
        document.getElementById("volume").value;

}

// DINH DANG THOI GIAN

function formatTime(seconds) {

    const min = Math.floor(seconds / 60);

    const sec = Math.floor(seconds % 60);

    return String(min).padStart(2,"0") + ":" +
           String(sec).padStart(2,"0");

}

// NUT KHAM PHA

function welcome() {

    alert("Chào mừng bạn đến với Nguyễn Văn Phong WebSite!");

}

</script>

</body>
</html>
"""

# ==========================================
# TIM ANH, NHAC, LOGO
# ==========================================

def find_asset(filename):

    base_dir = Path(__file__).resolve().parent

    folders = [
        base_dir,
        base_dir / "assets",
        base_dir / "static",
        base_dir / "Web",
        base_dir / "web"
    ]

    for folder in folders:

        candidate = folder / filename

        if candidate.is_file():
            return candidate

    return None


# ==========================================
# WEB SERVER
# ==========================================

class Website(BaseHTTPRequestHandler):

    def send_bytes(self, data, content_type, status=200):

        self.send_response(status)

        self.send_header(
            "Content-Type",
            content_type
        )

        self.send_header(
            "Content-Length",
            str(len(data))
        )

        self.send_header(
            "Cache-Control",
            "no-cache"
        )

        self.end_headers()

        self.wfile.write(data)

    def do_GET(self):

        path = self.path.split("?", 1)[0]

        # TRANG CHU

        if path == "/":

            self.send_bytes(
                HTML.encode("utf-8"),
                "text/html; charset=utf-8"
            )

            return

        # CAC FILE MEDIA

        assets = {

            "/background.jpg": (
                "background.jpg",
                "image/jpeg"
            ),

            "/music.mp3": (
                "music.mp3",
                "audio/mpeg"
            ),

            "/logo.png": (
                "logo.png",
                "image/png"
            )

        }

        if path in assets:

            filename, content_type = assets[path]

            file_path = find_asset(filename)

            if file_path is None:

                self.send_error(
                    404,
                    "Khong tim thay " + filename +
                    ". Hay dat file canh app_v7.py hoac trong thu muc assets/"
                )

                return

            try:

                data = file_path.read_bytes()

                self.send_bytes(
                    data,
                    content_type
                )

            except OSError as error:

                self.send_error(
                    500,
                    "Khong doc duoc file: " + str(error)
                )

            return

        # FAVICON

        if path == "/favicon.ico":

            self.send_response(204)

            self.end_headers()

            return

        self.send_error(
            404,
            "Duong dan khong ton tai: " + path
        )

    def log_message(self, format, *args):

        print("[WEB]", format % args)


# ==========================================
# KHOI DONG WEBSITE
# ==========================================

print("================================")
print("NGUYEN VAN PHONG WEBSITE V7")
print("http://127.0.0.1:5000")
print("================================")

print("KIEM TRA ANH, NHAC VA LOGO:")

for asset_name in (
    "background.jpg",
    "music.mp3",
    "logo.png"
):

    asset_path = find_asset(asset_name)

    if asset_path:

        print("[OK] " + asset_name)

    else:

        print("[THIEU] " + asset_name)

print("================================")

server = ThreadingHTTPServer(
    ("0.0.0.0", 5000),
    Website
)

try:

    print("Website dang chay!")

    print("Mo Chrome:")
    print("http://127.0.0.1:5000")

    print("================================")

    server.serve_forever()

except KeyboardInterrupt:

    print("Dang dung website...")

finally:

    server.server_close()

    print("Da dung PHONG WEB V7!")
