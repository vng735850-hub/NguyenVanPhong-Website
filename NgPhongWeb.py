
import os
import json
import mimetypes
import urllib.request
import urllib.error
import secrets
import time
import threading

from pathlib import Path
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import (
    urlencode,
    urlsplit,
    unquote,
    parse_qs,
    quote
)

# ==========================================
# PHONG WEB V25
# VUOTNHANH DEVELOPERS API + LINK4M API
# LINK4M RETURN CONFIRMATION
# ==========================================

BASE_DIR = Path(__file__).resolve().parent
PORT = int(os.environ.get("PORT", 5000))

# VUOTNHANH DEVELOPERS API
API_KEY = os.environ.get("VUOTNHANH_API_KEY", "").strip()
VUOTNHANH_ENDPOINT = "https://vuotnhanh.com/api"

# LINK4M API
LINK4M_API_TOKEN = os.environ.get(
    "LINK4M_API_TOKEN", ""
).strip()

LINK4M_ENDPOINT = "https://link4m.co/api-shorten/v2"

# WEBSITE URL
SITE_URL = os.environ.get(
    "SITE_URL",
    "https://nvp-com.onrender.com"
).strip().rstrip("/")

# MEDIAFIRE
MEDIAFIRE_LINK = (
    "https://www.mediafire.com/file/"
    "yen60lu05hfnng4/DINH_VI_BT.zip/file"
)

# LINK4M SESSION
SESSION_TTL = 30 * 60
link4m_sessions = {}
session_lock = threading.Lock()


def clean_sessions():
    """Xóa các phiên Link4M đã hết hạn."""
    now = time.time()

    with session_lock:
        expired = [
            token
            for token, data in link4m_sessions.items()
            if now - data["created"] > SESSION_TTL
        ]

        for token in expired:
            link4m_sessions.pop(token, None)


def create_link4m_session():
    clean_sessions()

    token = secrets.token_urlsafe(32)

    with session_lock:
        link4m_sessions[token] = {
            "created": time.time(),
            "returned": False
        }

    return token


def mark_link4m_returned(token):
    clean_sessions()

    if not token:
        return False

    with session_lock:
        session = link4m_sessions.get(token)

        if not session:
            return False

        if time.time() - session["created"] > SESSION_TTL:
            link4m_sessions.pop(token, None)
            return False

        session["returned"] = True
        return True


def check_link4m_session(token):
    clean_sessions()

    if not token:
        return False

    with session_lock:
        session = link4m_sessions.get(token)

        if not session:
            return False

        return (
            session["returned"]
            and time.time() - session["created"] <= SESSION_TTL
        )


# ==========================================
# HTML - GIỮ NGUYÊN GIAO DIỆN V24
# ==========================================

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

/* MENU */

.menu-container {
    width: 100%;
    max-width: 700px;
    margin: 25px auto;
}

.menu-card {
    padding: 25px 15px;
    border-radius: 18px;
    background: linear-gradient(135deg, #252b65, #532b91);
    border: 1px solid rgba(255,255,255,0.2);
    box-shadow: 0 8px 25px rgba(0,0,0,0.3);
}

.menu-card h2 {
    font-size: 20px;
    margin: 5px 0 20px;
}

.open-menu-button {
    display: inline-block;
    padding: 12px 35px;
    border: none;
    border-radius: 25px;
    background: white;
    color: #5632a8;
    font-weight: bold;
    font-size: 15px;
    cursor: pointer;
}

.open-menu-button:hover {
    box-shadow: 0 0 20px #a98aff;
}

/* LINK PAGE */

.link-page {
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

.link-page h2 {
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

.status {
    margin-top: 18px;
    color: #ffe28a;
    font-size: 14px;
    line-height: 1.6;
}

/* SUCCESS PAGE */

.success-icon {
    font-size: 75px;
    color: #42e99a;
}

.success-title {
    color: #66efa8;
    font-size: 27px;
    font-weight: bold;
    line-height: 1.5;
    margin: 20px 0;
}

.success-description {
    color: #d2dcff;
    line-height: 1.8;
    margin-bottom: 25px;
}

.download-button {
    display: inline-block;
    width: 100%;
    max-width: 350px;
    padding: 16px 25px;
    border-radius: 30px;
    background: linear-gradient(135deg, #10b96e, #087cba);
    color: white;
    font-size: 18px;
    font-weight: bold;
    text-decoration: none;
    box-shadow: 0 5px 20px rgba(0,220,140,0.3);
}

.download-button:active {
    transform: scale(0.98);
}

.result-error {
    color: #ffb1b1;
    line-height: 1.7;
    margin-top: 20px;
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

    .link-page h2 {
        font-size: 21px;
    }

    .menu-card h2 {
        font-size: 17px;
    }

    .success-title {
        font-size: 23px;
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

    <img class="hero-logo" src="/logo.png" alt="PHONG WEB">

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
                    <span class="location-button">MỞ MỤC</span>
                </div>
            </div>
        </a>
    </section>

    <section class="menu-container">
        <div class="menu-card">
            <h2>🔐 DETA IPA CRACK NOKЕY</h2>
            <button
                class="open-menu-button"
                id="openMenuButton"
                type="button"
            >
                MỞ MENU
            </button>
        </div>
    </section>

</div>

<!-- VUOTNHANH PAGE -->

<div id="locationPage" class="link-page">

    <div class="link-icon">📍</div>

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
        id="vuotNhanhButton"
        type="button"
    >
        🔓 VƯỢT LINK
    </button>

    <div class="status" id="locationStatus"></div>

    <br>

    <a class="back-button" href="/">
        ← QUAY LẠI TRANG CHỦ
    </a>

</div>

<!-- LINK4M PAGE -->

<div id="menuPage" class="link-page">

    <div class="link-icon">🔐</div>

    <h2>
        BẠN CẦN VƯỢT LINK ĐỂ LẤY FILE MEDIAFIRE
    </h2>

    <div class="link-description">
        Nhấn nút bên dưới để tạo đường dẫn Link4M.
        <br>
        Sau khi hoàn thành, bạn sẽ được chuyển về PHONG WEB.
    </div>

    <button
        class="cross-link-button"
        id="link4mButton"
        type="button"
    >
        🔓 VƯỢT LINK
    </button>

    <div class="status" id="link4mStatus"></div>

    <br>

    <a class="back-button" href="/">
        ← QUAY LẠI TRANG CHỦ
    </a>

</div>

<!-- LINK4M SUCCESS PAGE -->

<div id="resultPage" class="link-page">

    <div class="success-icon">✓</div>

    <div class="success-title">
        VƯỢT LINK THÀNH CÔNG
    </div>

    <h2>Bạn đã quay lại PHONG WEB!</h2>

    <div class="success-description">
        Cảm ơn bạn đã hoàn thành bước vượt Link4M.
        <br>
        Nhấn nút bên dưới để tiếp tục đến trang tải file.
    </div>

    <a
        class="download-button"
        id="downloadButton"
        href="#"
    >
        📥 TẢI FILE
    </a>

    <div class="result-error" id="resultError"></div>

    <br>

    <a class="back-button" href="/menu">
        ← QUAY LẠI VÀ THỬ LẠI
    </a>

</div>

</main>

<!-- MUSIC BUTTON -->

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
    PHONG WEB V25
</footer>

<script>

// ==========================================
// PAGE NAVIGATION
// ==========================================

const homePage = document.getElementById("homePage");
const locationPage = document.getElementById("locationPage");
const menuPage = document.getElementById("menuPage");
const resultPage = document.getElementById("resultPage");

function hideAllPages() {
    homePage.style.display = "none";
    locationPage.style.display = "none";
    menuPage.style.display = "none";
    resultPage.style.display = "none";
}

function showPage() {

    const path = window.location.pathname;
    const params = new URLSearchParams(window.location.search);

    hideAllPages();

    if (path === "/dinh-vi") {
        locationPage.style.display = "block";

    } else if (path === "/menu") {
        menuPage.style.display = "block";

    } else if (
        path === "/" &&
        params.get("link4m") === "success"
    ) {
        resultPage.style.display = "block";
        verifyReturnAndShowDownload();

    } else {
        homePage.style.display = "block";
    }
}

function navigate(path) {
    history.pushState({}, "", path);
    showPage();
    window.scrollTo(0, 0);
}

window.addEventListener("popstate", showPage);

document.querySelector(".location-link")
.addEventListener("click", function(e) {
    e.preventDefault();
    navigate("/dinh-vi");
});

document.getElementById("openMenuButton")
.addEventListener("click", function() {
    navigate("/menu");
});


// ==========================================
// LINK4M RETURN VERIFICATION
// ==========================================

async function verifyReturnAndShowDownload() {

    const params = new URLSearchParams(window.location.search);
    const token = params.get("token");

    const downloadButton =
        document.getElementById("downloadButton");

    const resultError =
        document.getElementById("resultError");

    downloadButton.style.display = "none";
    resultError.textContent = "Đang xác nhận lượt quay lại...";

    if (!token) {
        resultError.textContent =
            "Không tìm thấy thông tin xác nhận. Vui lòng vượt link lại.";
        return;
    }

    try {

        const response = await fetch(
            "/check-link4m?token=" + encodeURIComponent(token),
            {
                method: "GET",
                cache: "no-store"
            }
        );

        const data = await response.json();

        if (!response.ok || !data.success) {
            throw new Error(
                data.message || "Không thể xác nhận lượt quay lại."
            );
        }

        downloadButton.href =
            "/download?token=" + encodeURIComponent(token);

        downloadButton.style.display = "inline-block";
        resultError.textContent = "";

    } catch(error) {

        resultError.textContent =
            "Chưa xác nhận được: " + error.message +
            " Vui lòng quay lại mục DETA và thử lại.";
    }
}


// ==========================================
// VUOTNHANH DEVELOPERS API
// GIỮ NGUYÊN V24
// ==========================================

const vuotNhanhButton =
document.getElementById("vuotNhanhButton");

const locationStatus =
document.getElementById("locationStatus");

vuotNhanhButton.addEventListener("click", async function() {

    vuotNhanhButton.disabled = true;

    locationStatus.textContent =
        "Đang tạo đường dẫn Vượt Nhanh Developers API...";

    try {

        const response = await fetch("/create-link", {
            method: "GET",
            cache: "no-store"
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
            throw new Error(
                data.message || "Không thể tạo link Vượt Nhanh."
            );
        }

        locationStatus.textContent =
            "Đang chuyển đến Vượt Nhanh...";

        window.location.href = data.url;

    } catch(error) {

        locationStatus.textContent =
            "Lỗi: " + error.message;

        vuotNhanhButton.disabled = false;
    }

});


// ==========================================
// LINK4M API
// ==========================================

const link4mButton =
document.getElementById("link4mButton");

const link4mStatus =
document.getElementById("link4mStatus");

link4mButton.addEventListener("click", async function() {

    link4mButton.disabled = true;

    link4mStatus.textContent =
        "Đang tạo đường dẫn Link4M...";

    try {

        const response = await fetch("/create-link4m", {
            method: "GET",
            cache: "no-store"
        });

        const data = await response.json();

        if (!response.ok || !data.success) {
            throw new Error(
                data.message || "Không thể tạo link Link4M."
            );
        }

        link4mStatus.textContent =
            "Đang chuyển đến Link4M...";

        window.location.href = data.url;

    } catch(error) {

        link4mStatus.textContent =
            "Lỗi: " + error.message;

        link4mButton.disabled = false;
    }

});


// ==========================================
// MUSIC CONTROL - GIỮ NGUYÊN V24
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


// ==========================================
// INITIALIZE
// ==========================================

showPage();

</script>

</body>
</html>
"""


# ==========================================
# HELPER: VALIDATE SHORTENED URL
# ==========================================

def validate_shortened_url(value):

    if not isinstance(value, str):
        return None

    value = value.strip()

    if not value or len(value) > 4096:
        return None

    if any(char.isspace() for char in value):
        return None

    try:

        parsed = urlsplit(value)

        if parsed.scheme not in ("https", "http"):
            return None

        if not parsed.hostname:
            return None

        if parsed.username or parsed.password:
            return None

        if parsed.port is not None and not (
            1 <= parsed.port <= 65535
        ):
            return None

        return value

    except ValueError:
        return None


# ==========================================
# WEBSITE SERVER
# ==========================================

class Website(BaseHTTPRequestHandler):

    def send_json(self, status, data):

        content = json.dumps(
            data,
            ensure_ascii=False
        ).encode("utf-8")

        self.send_response(status)

        self.send_header(
            "Content-Type",
            "application/json; charset=utf-8"
        )

        self.send_header(
            "Content-Length",
            str(len(content))
        )

        self.send_header("Cache-Control", "no-store")

        self.end_headers()

        try:
            self.wfile.write(content)

        except (BrokenPipeError, ConnectionResetError):
            pass


    def send_redirect(self, url):

        self.send_response(302)
        self.send_header("Location", url)
        self.send_header("Cache-Control", "no-store")
        self.end_headers()


    # ======================================
    # MAIN ROUTES
    # ======================================

    def do_GET(self):

        parsed_request = urlsplit(self.path)
        path = unquote(parsed_request.path)
        query = parse_qs(parsed_request.query)


        # ======================================
        # HOME AND PAGES
        # ======================================

        if path in (
            "/",
            "/index.html",
            "/dinh-vi",
            "/menu"
        ):

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


        # ======================================
        # VUOTNHANH DEVELOPERS API - GIỮ NGUYÊN
        # ======================================

        if path == "/create-link":

            if not API_KEY:

                self.send_json(500, {
                    "success": False,
                    "message": "Chưa cấu hình VUOTNHANH_API_KEY trên Render."
                })

                return

            if not SITE_URL.startswith("https://"):

                self.send_json(500, {
                    "success": False,
                    "message": "SITE_URL phải là địa chỉ HTTPS."
                })

                return

            return_url = SITE_URL + "/complete"

            try:

                params = urlencode({
                    "api": API_KEY,
                    "url": return_url
                })

                api_url = VUOTNHANH_ENDPOINT + "?" + params

                request = urllib.request.Request(
                    api_url,
                    headers={
                        "User-Agent": "Mozilla/5.0 PHONG-WEB/25",
                        "Accept": "application/json"
                    },
                    method="GET"
                )

                with urllib.request.urlopen(
                    request,
                    timeout=25
                ) as response:

                    response_body = response.read().decode(
                        "utf-8",
                        errors="replace"
                    )

                    http_status = response.status

                print(
                    "[PHONG WEB] VuotNhanh Developers HTTP:",
                    http_status
                )

                try:
                    result = json.loads(response_body)

                except json.JSONDecodeError:

                    print(
                        "[PHONG WEB] VuotNhanh invalid JSON:",
                        response_body[:500]
                    )

                    self.send_json(502, {
                        "success": False,
                        "message": "Vượt Nhanh không trả về JSON hợp lệ."
                    })

                    return

                if not isinstance(result, dict):

                    self.send_json(502, {
                        "success": False,
                        "message": "Dữ liệu Developers API không đúng định dạng."
                    })

                    return

                if result.get("status") != "success":

                    error_message = result.get(
                        "message",
                        "Vượt Nhanh không xác nhận tạo link thành công."
                    )

                    self.send_json(502, {
                        "success": False,
                        "message": "Vượt Nhanh: " + str(error_message)[:300]
                    })

                    return

                shortened_url = result.get("shortenedUrl")

                valid_url = validate_shortened_url(
                    shortened_url
                )

                if not valid_url:

                    self.send_json(502, {
                        "success": False,
                        "message": "Developers API báo thành công nhưng shortenedUrl không hợp lệ."
                    })

                    return

                self.send_json(200, {
                    "success": True,
                    "url": valid_url
                })

                print(
                    "[PHONG WEB] VuotNhanh Developers link created."
                )

            except urllib.error.HTTPError as error:

                error_body = error.read().decode(
                    "utf-8",
                    errors="replace"
                )

                print(
                    "[PHONG WEB] VuotNhanh HTTP error:",
                    error.code
                )

                try:
                    error_data = json.loads(error_body)

                    if isinstance(error_data, dict):
                        error_message = error_data.get(
                            "message",
                            error_body[:300]
                        )
                    else:
                        error_message = error_body[:300]

                except json.JSONDecodeError:
                    error_message = error_body[:300]

                if not error_message:
                    error_message = "API từ chối yêu cầu."

                self.send_json(502, {
                    "success": False,
                    "message": (
                        "Vượt Nhanh HTTP "
                        + str(error.code)
                        + ": "
                        + str(error_message)[:300]
                    )
                })

            except urllib.error.URLError as error:

                print(
                    "[PHONG WEB] VuotNhanh connection error:",
                    str(error.reason)
                )

                self.send_json(502, {
                    "success": False,
                    "message": "Không thể kết nối máy chủ Vượt Nhanh."
                })

            except TimeoutError:

                self.send_json(504, {
                    "success": False,
                    "message": "Vượt Nhanh phản hồi quá lâu. Vui lòng thử lại."
                })

            except Exception as error:

                print(
                    "[PHONG WEB] VuotNhanh internal error:",
                    type(error).__name__,
                    str(error)[:300]
                )

                self.send_json(500, {
                    "success": False,
                    "message": "Lỗi xử lý Vượt Nhanh: "
                    + type(error).__name__
                })

            return


        # ======================================
        # VUOTNHANH RETURN - GIỮ NGUYÊN
        # ======================================

        if path == "/complete":

            self.send_redirect(MEDIAFIRE_LINK)

            print("[PHONG WEB] VuotNhanh return")

            return


        # ======================================
        # LINK4M API - TẠO LINK VỚI CALLBACK
        # ======================================

        if path == "/create-link4m":

            if not LINK4M_API_TOKEN:

                self.send_json(500, {
                    "success": False,
                    "message": "Chưa cấu hình LINK4M_API_TOKEN trên Render."
                })

                return

            if not SITE_URL.startswith("https://"):

                self.send_json(500, {
                    "success": False,
                    "message": "SITE_URL phải là địa chỉ HTTPS."
                })

                return

            # Tạo mã phiên riêng cho từng lượt vượt link.
            session_token = secrets.token_urlsafe(32)

            # Đây là URL đích Link4M sẽ mở sau khi người dùng hoàn thành.
            callback_url = (
                SITE_URL
                + "/link4m-return?token="
                + quote(session_token, safe="")
            )

            try:

                params = urlencode({
                    "api": LINK4M_API_TOKEN,
                    "url": callback_url
                })

                api_url = LINK4M_ENDPOINT + "?" + params

                request = urllib.request.Request(
                    api_url,
                    headers={
                        "User-Agent": "Mozilla/5.0 PHONG-WEB/25",
                        "Accept": "application/json"
                    },
                    method="GET"
                )

                with urllib.request.urlopen(
                    request,
                    timeout=25
                ) as response:

                    response_body = response.read().decode(
                        "utf-8",
                        errors="replace"
                    )

                    http_status = response.status

                print(
                    "[PHONG WEB] Link4M HTTP status:",
                    http_status
                )

                try:
                    result = json.loads(response_body)

                except json.JSONDecodeError:

                    print(
                        "[PHONG WEB] Link4M invalid JSON:",
                        response_body[:500]
                    )

                    self.send_json(502, {
                        "success": False,
                        "message": "Link4M không trả về JSON hợp lệ."
                    })

                    return

                if not isinstance(result, dict):

                    self.send_json(502, {
                        "success": False,
                        "message": "Dữ liệu Link4M không đúng định dạng."
                    })

                    return

                print(
                    "[PHONG WEB] Link4M status:",
                    result.get("status", "unknown")
                )

                if result.get("status") != "success":

                    error_message = result.get(
                        "message",
                        "Link4M không xác nhận tạo link thành công."
                    )

                    self.send_json(502, {
                        "success": False,
                        "message": "Link4M: " + str(error_message)[:300]
                    })

                    return

                shortened_url = result.get("shortenedUrl")

                if not shortened_url:
                    shortened_url = result.get("shortened_url")

                if not shortened_url:
                    shortened_url = result.get("short_url")

                valid_url = validate_shortened_url(
                    shortened_url
                )

                if not valid_url:

                    print(
                        "[PHONG WEB] Link4M returned invalid URL format."
                    )

                    self.send_json(502, {
                        "success": False,
                        "message": "Link4M báo thành công nhưng không trả về URL HTTP/HTTPS hợp lệ."
                    })

                    return

                # Chỉ lưu phiên sau khi Link4M tạo link thành công.
                clean_sessions()

                with session_lock:
                    link4m_sessions[session_token] = {
                        "created": time.time(),
                        "returned": False
                    }

                self.send_json(200, {
                    "success": True,
                    "url": valid_url
                })

                print(
                    "[PHONG WEB] Link4M link created successfully."
                )

            except urllib.error.HTTPError as error:

                error_body = error.read().decode(
                    "utf-8",
                    errors="replace"
                )

                print(
                    "[PHONG WEB] Link4M HTTP error:",
                    error.code
                )

                print(
                    "[PHONG WEB] Link4M response:",
                    error_body[:500]
                )

                try:
                    error_data = json.loads(error_body)

                    if isinstance(error_data, dict):
                        error_message = error_data.get(
                            "message",
                            error_body[:300]
                        )
                    else:
                        error_message = error_body[:300]

                except json.JSONDecodeError:
                    error_message = error_body[:300]

                if not error_message:
                    error_message = "API từ chối yêu cầu."

                self.send_json(502, {
                    "success": False,
                    "message": (
                        "Link4M HTTP "
                        + str(error.code)
                        + ": "
                        + str(error_message)[:300]
                    )
                })

            except urllib.error.URLError as error:

                print(
                    "[PHONG WEB] Link4M connection error:",
                    str(error.reason)
                )

                self.send_json(502, {
                    "success": False,
                    "message": "Không thể kết nối máy chủ Link4M."
                })

            except TimeoutError:

                self.send_json(504, {
                    "success": False,
                    "message": "Link4M phản hồi quá lâu. Vui lòng thử lại."
                })

            except Exception as error:

                print(
                    "[PHONG WEB] Link4M internal error:",
                    type(error).__name__,
                    str(error)[:300]
                )

                self.send_json(500, {
                    "success": False,
                    "message": "Lỗi xử lý Link4M: "
                    + type(error).__name__
                })

            return


        # ======================================
        # LINK4M CALLBACK
        # ======================================

        if path == "/link4m-return":

            token_values = query.get("token", [])
            token = token_values[0] if token_values else ""

            if not mark_link4m_returned(token):

                print(
                    "[PHONG WEB] Link4M callback invalid or expired."
                )

                self.send_redirect(
                    SITE_URL + "/?link4m=failed"
                )

                return

            print(
                "[PHONG WEB] Link4M user returned successfully."
            )

            # Quay về trang chủ và hiển thị giao diện thành công.
            self.send_redirect(
                SITE_URL
                + "/?link4m=success&token="
                + quote(token, safe="")
            )

            return


        # ======================================
        # CHECK LINK4M RETURN
        # ======================================

        if path == "/check-link4m":

            token_values = query.get("token", [])
            token = token_values[0] if token_values else ""

            if not check_link4m_session(token):

                self.send_json(403, {
                    "success": False,
                    "message": "Phiên vượt link không hợp lệ hoặc đã hết hạn."
                })

                return

            self.send_json(200, {
                "success": True,
                "message": "Đã xác nhận người dùng quay lại từ Link4M."
            })

            return


        # ======================================
        # DOWNLOAD BUTTON
        # ======================================

        if path == "/download":

            token_values = query.get("token", [])
            token = token_values[0] if token_values else ""

            if not check_link4m_session(token):

                self.send_response(403)
                self.send_header(
                    "Content-Type",
                    "text/html; charset=utf-8"
                )
                self.send_header("Cache-Control", "no-store")
                self.end_headers()

                message = """
                <!DOCTYPE html>
                <html lang="vi">
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1">
                <title>Chưa hoàn thành vượt link</title>
                <body style="background:#101a35;color:white;
                font-family:Arial;text-align:center;padding:50px 15px">
                    <h2>Không thể tải file</h2>
                    <p>Bạn chưa hoàn thành bước quay lại từ Link4M
                    hoặc phiên đã hết hạn.</p>
                    <a href="/menu" style="color:#8db8ff">
                    Quay lại và thử lại</a>
                </body>
                </html>
                """

                try:
                    self.wfile.write(message.encode("utf-8"))
                except (BrokenPipeError, ConnectionResetError):
                    pass

                return

            print(
                "[PHONG WEB] Authorized download redirect."
            )

            # Chuyển đến trang tải file MediaFire.
            self.send_redirect(MEDIAFIRE_LINK)

            return


        # ======================================
        # STATIC FILES - GIỮ NGUYÊN
        # ======================================

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

            self.send_header(
                "Content-Type",
                content_type
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
                str(error)
            )


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

    print("====================================")
    print("          PHONG WEB V25")
    print("====================================")

    print("Server port:", PORT)

    print(
        "VuotNhanh Developers API:",
        "ENABLED" if API_KEY else "MISSING API KEY"
    )

    print(
        "Link4M API:",
        "ENABLED" if LINK4M_API_TOKEN else "MISSING API TOKEN"
    )

    print("Location route: /dinh-vi")
    print("Menu route: /menu")
    print("VuotNhanh endpoint: /create-link")
    print("VuotNhanh API: https://vuotnhanh.com/api")
    print("Link4M endpoint: /create-link4m")
    print("Link4M callback: /link4m-return")
    print("Link4M check: /check-link4m")
    print("Download route: /download")

    print("MediaFire destination: ENABLED")
    print("Music button: ENABLED")
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
