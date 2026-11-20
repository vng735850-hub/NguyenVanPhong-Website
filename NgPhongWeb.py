
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
from urllib.parse import urlencode, urlsplit, unquote, parse_qs, quote

# ==========================================
# PHONG WEB V28
# LINK4M + VUOTNHANH + YEUMONEY
# LOCATION VIEW RESULT PAGE
# DETA DOWNLOAD + MUSIC
# ==========================================

BASE_DIR = Path(__file__).resolve().parent
PORT = int(os.environ.get("PORT", 5000))

API_KEY = os.environ.get("VUOTNHANH_API_KEY", "").strip()
LINK4M_API_TOKEN = os.environ.get("LINK4M_API_TOKEN", "").strip()
YEUMONEY_API_TOKEN = os.environ.get("YEUMONEY_API_TOKEN", "").strip()

VUOTNHANH_ENDPOINT = "https://vuotnhanh.com/api"
LINK4M_ENDPOINT = "https://link4m.co/api-shorten/v2"
YEUMONEY_ENDPOINT = "https://yeumoney.com/QL_api.php"

SITE_URL = os.environ.get(
    "SITE_URL",
    "https://nvp-com.onrender.com"
).strip().rstrip("/")

MEDIAFIRE_LINK = (
    "https://www.mediafire.com/file/"
    "yen60lu05hfnng4/DINH_VI_BT.zip/file"
)

DETA_MEDIAFIRE_LINK = (
    "https://www.mediafire.com/file/"
    "wohet4glfwyn5j0/Deta_Crack.7z/file"
)

SESSIONS = {}
SESSIONS_LOCK = threading.Lock()
SESSION_TTL = 30 * 60


# ==========================================
# HTML
# ==========================================

HTML = r"""
<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>NGUYỄN VĂN PHONG WEBSITE</title>

<style>
* { box-sizing: border-box; }

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

main { padding: 25px 15px; }

.hero-logo {
    width: 130px;
    height: 130px;
    object-fit: contain;
    border-radius: 20px;
    margin-top: 15px;
}

h1 { font-size: 27px; margin-top: 20px; }

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

.location-emoji { font-size: 45px; }

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

/* PAGES */

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

.link-icon { font-size: 65px; }

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

.provider-box {
    max-width: 360px;
    margin: 22px auto;
    text-align: left;
}

.provider-box label {
    display: block;
    margin-bottom: 10px;
    color: #e3eaff;
    font-size: 14px;
    font-weight: bold;
}

.provider-select {
    width: 100%;
    padding: 14px 15px;
    border-radius: 12px;
    border: 1px solid rgba(255,255,255,0.35);
    background: #17234c;
    color: white;
    font-size: 16px;
    outline: none;
    cursor: pointer;
}

.provider-select option {
    background: #17234c;
    color: white;
}

.provider-note {
    margin-top: 9px;
    color: #aebfe9;
    font-size: 12px;
    line-height: 1.5;
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

/* RESULT STATUS */

.result-success {
    border: 1px solid rgba(0,230,150,0.4);
    box-shadow: 0 0 25px rgba(0,220,150,0.12);
}

.result-failed {
    border: 1px solid rgba(255,75,90,0.45);
    box-shadow: 0 0 25px rgba(255,50,70,0.12);
}

.result-success .link-icon { color: #00e69a; }
.result-failed .link-icon { color: #ff5365; }

.result-success .cross-link-button {
    background: linear-gradient(135deg, #00b879, #087dca);
}

.result-failed .cross-link-button {
    background: linear-gradient(135deg, #ff5365, #c52c65);
}

/* MUSIC */

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

.music-mini .music-icon { pointer-events: none; }

footer {
    padding: 25px 10px;
    color: #9eafd8;
    font-size: 12px;
}

@media(max-width: 500px) {
    header { font-size: 18px; }
    h1 { font-size: 22px; }
    .location-emoji { font-size: 30px; }
    .location-info h2 { font-size: 14px; }
    .location-info p { font-size: 10px; }
    .location-button { padding: 6px 15px; font-size: 11px; }
    .link-page h2 { font-size: 21px; }
    .menu-card h2 { font-size: 17px; }
}
</style>
</head>

<body>

<header>NGUYỄN VĂN PHONG WEBSITE</header>

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
            <button class="open-menu-button" id="openMenuButton" type="button">
                MỞ MENU
            </button>
        </div>
    </section>

</div>

<!-- LOCATION PAGE -->

<div id="locationPage" class="link-page">

    <div class="link-icon">📍</div>

    <h2>BẠN CẦN VƯỢT LINK ĐỂ LẤY FILE MEDIAFIRE</h2>

    <div class="link-description">
        Chọn dịch vụ vượt link bên dưới.
        <br>
        Sau khi hoàn thành, hệ thống sẽ kiểm tra trạng thái xác nhận.
    </div>

    <div class="provider-box">
        <label for="locationProvider">CHỌN DỊCH VỤ VƯỢT LINK</label>
        <select class="provider-select" id="locationProvider">
            <option value="link4m">Link4M</option>
            <option value="vuotnhanh">VuotNhanh</option>
            <option value="yeumoney">YeuMoney</option>
        </select>
        <div class="provider-note">
            Bạn có thể thay đổi dịch vụ trước khi nhấn Vượt Link.
        </div>
    </div>

    <button class="cross-link-button" id="locationCrossButton" type="button">
        🔓 VƯỢT LINK
    </button>

    <div class="status" id="locationStatus"></div>

    <br>
    <a class="back-button" href="/">← QUAY LẠI TRANG CHỦ</a>

</div>

<!-- DETA PAGE -->

<div id="menuPage" class="link-page">

    <div class="link-icon">🔐</div>

    <h2>BẠN CẦN VƯỢT LINK ĐỂ LẤY FILE DETA</h2>

    <div class="link-description">
        Chọn dịch vụ vượt link bên dưới.
        <br>
        Sau khi hoàn thành, bạn sẽ quay lại PHONG WEB.
        <br>
        Tại đó, nhấn nút LẤY FILE để mở MediaFire.
    </div>

    <div class="provider-box">
        <label for="detaProvider">CHỌN DỊCH VỤ VƯỢT LINK</label>
        <select class="provider-select" id="detaProvider">
            <option value="link4m">Link4M</option>
            <option value="vuotnhanh">VuotNhanh</option>
            <option value="yeumoney">YeuMoney</option>
        </select>
        <div class="provider-note">
            Bạn có thể thay đổi dịch vụ trước khi nhấn Vượt Link.
        </div>
    </div>

    <button class="cross-link-button" id="detaCrossButton" type="button">
        🔓 VƯỢT LINK
    </button>

    <div class="status" id="detaStatus"></div>

    <br>
    <a class="back-button" href="/">← QUAY LẠI TRANG CHỦ</a>

</div>

<!-- RESULT PAGE -->

<div id="resultPage" class="link-page">

    <div class="link-icon" id="resultIcon">✅</div>

    <h2 id="resultTitle">Vượt Link</h2>

    <div class="link-description" id="resultDescription"></div>

    <a class="cross-link-button" id="resultAction" href="/menu">
        LẤY FILE
    </a>

    <div class="status" id="resultStatus"></div>

    <br>
    <a class="back-button" id="resultBack" href="/">← QUAY LẠI</a>

</div>

</main>

<button class="music-mini" id="musicButton"
    aria-label="Bật hoặc tắt nhạc"
    title="Bật / Tắt nhạc" type="button">
    <span class="music-icon" id="musicIcon">▶</span>
</button>

<audio id="audio" preload="metadata">
    <source src="/music.mp3" type="audio/mpeg">
</audio>

<footer>
    © 2026 Nguyễn Văn Phong Website
    <br><br>
    PHONG WEB V28
</footer>

<script>

// ==========================================
// PAGE NAVIGATION
// ==========================================

const homePage = document.getElementById("homePage");
const locationPage = document.getElementById("locationPage");
const menuPage = document.getElementById("menuPage");
const resultPage = document.getElementById("resultPage");

const resultTitle = document.getElementById("resultTitle");
const resultDescription = document.getElementById("resultDescription");
const resultAction = document.getElementById("resultAction");
const resultStatus = document.getElementById("resultStatus");
const resultIcon = document.getElementById("resultIcon");
const resultBack = document.getElementById("resultBack");

function hideAllPages() {
    homePage.style.display = "none";
    locationPage.style.display = "none";
    menuPage.style.display = "none";
    resultPage.style.display = "none";
}

async function showResultPage() {

    const params = new URLSearchParams(window.location.search);
    const state = params.get("result");

    if (state !== "success" && state !== "failed") {
        return false;
    }

    const destination =
        params.get("destination") === "location"
        ? "location"
        : "deta";

    const token = params.get("token") || "";

    hideAllPages();
    resultPage.style.display = "block";

    resultBack.href = destination === "location"
        ? "/dinh-vi"
        : "/menu";

    resultPage.classList.remove("result-success", "result-failed");

    // ======================================
    // LOCATION: FAILED WHEN NOT VERIFIED
    // ======================================

    if (destination === "location") {

        let sessionReturned = false;

        if (token) {
            try {
                const response = await fetch(
                    "/check-session?token=" +
                    encodeURIComponent(token),
                    { cache: "no-store" }
                );

                const data = await response.json();

                sessionReturned =
                    response.ok &&
                    data.success &&
                    data.destination === "location" &&
                    data.returned === true;

            } catch (error) {
                sessionReturned = false;
            }
        }

        resultPage.classList.add("result-failed");
        resultIcon.textContent = "❌";
        resultTitle.textContent = "Vượt Link Không Thành Công!";

        if (sessionReturned) {
            resultDescription.textContent =
                "Bạn đã quay lại website, nhưng nhà cung cấp chưa gửi dữ liệu xác nhận View tăng. Vui lòng vượt lại link.";
        } else {
            resultDescription.textContent =
                "Không xác nhận được phiên vượt link. Vui lòng quay lại mục Định Vị và thử lại.";
        }

        resultAction.href = "/dinh-vi";
        resultAction.textContent = "↻ VƯỢT LẠI LINK";
        resultBack.href = "/";
        resultStatus.textContent = "";

        return true;
    }

    // ======================================
    // DETA: KEEP OLD SUCCESS FLOW
    // ======================================

    if (state === "failed") {

        resultPage.classList.add("result-failed");
        resultIcon.textContent = "❌";
        resultTitle.textContent = "Vượt Link Chưa Thành Công";
        resultDescription.textContent =
            "Không xác nhận được phiên vượt link. Vui lòng thử lại.";

        resultAction.href = "/menu";
        resultAction.textContent = "↻ THỬ LẠI";
        resultStatus.textContent = "";

        return true;
    }

    resultStatus.textContent = "Đang xác nhận phiên vượt link...";

    try {

        const response = await fetch(
            "/check-session?token=" +
            encodeURIComponent(token),
            { cache: "no-store" }
        );

        const data = await response.json();

        if (!response.ok || !data.success ||
            data.destination !== "deta") {
            throw new Error("Phiên không hợp lệ.");
        }

        resultPage.classList.add("result-success");
        resultIcon.textContent = "✅";
        resultTitle.textContent = "Vượt Link Thành Công!";
        resultDescription.textContent =
            "Bạn đã hoàn thành bước vượt link Deta. Nhấn nút bên dưới để lấy file.";

        resultAction.href =
            "/download-deta?token=" + encodeURIComponent(token);

        resultAction.textContent = "⬇ LẤY FILE DETA";
        resultStatus.textContent = "";

    } catch (error) {

        resultPage.classList.add("result-failed");
        resultIcon.textContent = "❌";
        resultTitle.textContent = "Xác Nhận Thất Bại";
        resultDescription.textContent =
            "Phiên vượt link không hợp lệ hoặc đã hết hạn. Vui lòng thử lại.";

        resultAction.href = "/menu";
        resultAction.textContent = "↻ THỬ LẠI";
        resultStatus.textContent = "";
    }

    return true;
}

async function showPage() {

    const path = window.location.pathname;

    hideAllPages();

    if (path === "/dinh-vi") {
        locationPage.style.display = "block";
    } else if (path === "/menu") {
        menuPage.style.display = "block";
    } else if (path === "/") {

        const showingResult = await showResultPage();

        if (!showingResult) {
            homePage.style.display = "block";
        }

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

showPage();


// ==========================================
// LINK CREATION
// ==========================================

async function createShortLink(provider, destination, button, status) {

    button.disabled = true;

    const providerNames = {
        link4m: "Link4M",
        vuotnhanh: "VuotNhanh",
        yeumoney: "YeuMoney"
    };

    const providerName = providerNames[provider] || provider;

    status.textContent =
        "Đang sử dụng API " + providerName + " để tạo link...";

    try {

        const params = new URLSearchParams({
            provider: provider,
            destination: destination
        });

        const response = await fetch(
            "/create-short-link?" + params.toString(),
            {
                method: "GET",
                cache: "no-store"
            }
        );

        const data = await response.json();

        if (!response.ok || !data.success) {
            throw new Error(data.message || "Không thể tạo link.");
        }

        if (!data.url) {
            throw new Error("API không trả về đường dẫn hợp lệ.");
        }

        status.textContent =
            "Đang chuyển đến " + providerName + "...";

        window.location.href = data.url;

    } catch (error) {

        status.textContent = "Lỗi: " + error.message;
        button.disabled = false;
    }
}


// LOCATION BUTTON

const locationCrossButton =
    document.getElementById("locationCrossButton");

const locationStatus =
    document.getElementById("locationStatus");

locationCrossButton.addEventListener("click", function() {

    const provider =
        document.getElementById("locationProvider").value;

    createShortLink(
        provider,
        "location",
        locationCrossButton,
        locationStatus
    );
});


// DETA BUTTON

const detaCrossButton =
    document.getElementById("detaCrossButton");

const detaStatus =
    document.getElementById("detaStatus");

detaCrossButton.addEventListener("click", function() {

    const provider =
        document.getElementById("detaProvider").value;

    createShortLink(
        provider,
        "deta",
        detaCrossButton,
        detaStatus
    );
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


# ==========================================
# URL VALIDATION
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
# SESSION HELPERS
# ==========================================

def cleanup_sessions():

    now = time.time()

    with SESSIONS_LOCK:

        expired = [
            token
            for token, session in SESSIONS.items()
            if now - session["created"] > SESSION_TTL
        ]

        for token in expired:
            SESSIONS.pop(token, None)


def get_session(token):

    if not token:
        return None

    now = time.time()

    with SESSIONS_LOCK:

        session = SESSIONS.get(token)

        if not session:
            return None

        if now - session["created"] > SESSION_TTL:
            SESSIONS.pop(token, None)
            return None

        return dict(session)


def check_session(token, destination=None):

    session = get_session(token)

    if not session:
        return False

    if not session.get("returned"):
        return False

    if destination and session.get("destination") != destination:
        return False

    return True


# ==========================================
# API REQUEST HELPERS
# ==========================================

def read_api_json(url, user_agent):

    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": user_agent,
            "Accept": "application/json"
        },
        method="GET"
    )

    with urllib.request.urlopen(request, timeout=25) as response:
        body = response.read().decode(
            "utf-8",
            errors="replace"
        )

    try:
        result = json.loads(body)

    except json.JSONDecodeError:
        raise ValueError("API không trả về JSON hợp lệ.")

    if not isinstance(result, dict):
        raise ValueError("Dữ liệu API không đúng định dạng.")

    return result


def create_vuotnhanh_url(callback_url):

    if not API_KEY:
        raise ValueError(
            "Chưa cấu hình VUOTNHANH_API_KEY trên Render."
        )

    params = urlencode({
        "api": API_KEY,
        "url": callback_url
    })

    api_url = VUOTNHANH_ENDPOINT + "?" + params

    result = read_api_json(
        api_url,
        "Mozilla/5.0 PHONG-WEB/28"
    )

    if result.get("status") != "success":

        raise ValueError(
            "VuotNhanh: " + str(
                result.get(
                    "message",
                    "Không xác nhận tạo link thành công."
                )
            )[:250]
        )

    valid_url = validate_shortened_url(
        result.get("shortenedUrl")
    )

    if not valid_url:
        raise ValueError(
            "VuotNhanh không trả về shortenedUrl hợp lệ."
        )

    return valid_url


def create_link4m_url(callback_url):

    if not LINK4M_API_TOKEN:
        raise ValueError(
            "Chưa cấu hình LINK4M_API_TOKEN trên Render."
        )

    params = urlencode({
        "api": LINK4M_API_TOKEN,
        "url": callback_url
    })

    api_url = LINK4M_ENDPOINT + "?" + params

    result = read_api_json(
        api_url,
        "Mozilla/5.0 PHONG-WEB/28"
    )

    if result.get("status") != "success":

        raise ValueError(
            "Link4M: " + str(
                result.get(
                    "message",
                    "Không xác nhận tạo link thành công."
                )
            )[:250]
        )

    shortened_url = (
        result.get("shortenedUrl")
        or result.get("shortened_url")
        or result.get("short_url")
    )

    valid_url = validate_shortened_url(shortened_url)

    if not valid_url:
        raise ValueError(
            "Link4M không trả về URL HTTP/HTTPS hợp lệ."
        )

    return valid_url


def create_yeumoney_url(callback_url):

    if not YEUMONEY_API_TOKEN:
        raise ValueError(
            "Chưa cấu hình YEUMONEY_API_TOKEN trên Render."
        )

    params = urlencode({
        "token": YEUMONEY_API_TOKEN,
        "format": "json",
        "url": callback_url
    })

    api_url = YEUMONEY_ENDPOINT + "?" + params

    result = read_api_json(
        api_url,
        "Mozilla/5.0 PHONG-WEB/28"
    )

    if result.get("status") != "success":

        error_message = (
            result.get("message")
            or result.get("status")
            or "Không xác nhận tạo link thành công."
        )

        raise ValueError(
            "YeuMoney: " + str(error_message)[:250]
        )

    valid_url = validate_shortened_url(
        result.get("shortenedUrl")
    )

    if not valid_url:
        raise ValueError(
            "YeuMoney không trả về shortenedUrl HTTP/HTTPS hợp lệ."
        )

    return valid_url


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
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()

        try:
            self.wfile.write(content)

        except (BrokenPipeError, ConnectionResetError):
            pass


    def send_html_page(self, status=200):

        content = HTML.encode("utf-8")

        self.send_response(status)
        self.send_header(
            "Content-Type",
            "text/html; charset=utf-8"
        )
        self.send_header("Content-Length", str(len(content)))
        self.send_header("Cache-Control", "no-cache")
        self.end_headers()

        try:
            self.wfile.write(content)

        except (BrokenPipeError, ConnectionResetError):
            pass


    def redirect(self, location):

        self.send_response(302)
        self.send_header("Location", location)
        self.send_header("Cache-Control", "no-store")
        self.end_headers()


    # ======================================
    # MAIN ROUTES
    # ======================================

    def do_GET(self):

        parsed_request = urlsplit(self.path)
        path = unquote(parsed_request.path)
        query = parse_qs(parsed_request.query)

        # HOME AND PAGES

        if path in (
            "/",
            "/index.html",
            "/dinh-vi",
            "/menu"
        ):
            self.send_html_page()
            return


        # ======================================
        # CREATE SHORT LINK
        # ======================================

        if path == "/create-short-link":

            provider = query.get("provider", [""])[0].lower()
            destination = query.get("destination", [""])[0].lower()

            if provider not in (
                "link4m",
                "vuotnhanh",
                "yeumoney"
            ):

                self.send_json(400, {
                    "success": False,
                    "message": "Dịch vụ vượt link không hợp lệ."
                })

                return

            if destination not in ("location", "deta"):

                self.send_json(400, {
                    "success": False,
                    "message": "Mục đích vượt link không hợp lệ."
                })

                return

            if not SITE_URL.startswith("https://"):

                self.send_json(500, {
                    "success": False,
                    "message": "SITE_URL phải là địa chỉ HTTPS."
                })

                return

            token = secrets.token_urlsafe(32)

            callback_url = (
                SITE_URL
                + "/provider-return?token="
                + quote(token, safe="")
            )

            try:

                if provider == "link4m":
                    shortened_url = create_link4m_url(callback_url)

                elif provider == "vuotnhanh":
                    shortened_url = create_vuotnhanh_url(callback_url)

                else:
                    shortened_url = create_yeumoney_url(callback_url)

                cleanup_sessions()

                with SESSIONS_LOCK:

                    SESSIONS[token] = {
                        "created": time.time(),
                        "returned": False,
                        "provider": provider,
                        "destination": destination,

                        # Callback không đồng nghĩa View đã tăng.
                        # Chỉ bật True khi có xác nhận chính thức.
                        "view_confirmed": False
                    }

                self.send_json(200, {
                    "success": True,
                    "url": shortened_url,
                    "provider": provider,
                    "destination": destination
                })

                print(
                    "[PHONG WEB V28] Created:",
                    provider,
                    destination
                )

            except urllib.error.HTTPError as error:

                error_body = error.read().decode(
                    "utf-8",
                    errors="replace"
                )

                print(
                    "[PHONG WEB V28] API HTTP error:",
                    provider,
                    error.code,
                    error_body[:400]
                )

                try:

                    error_data = json.loads(error_body)

                    message = (
                        error_data.get("message", error_body[:250])
                        if isinstance(error_data, dict)
                        else error_body[:250]
                    )

                except json.JSONDecodeError:
                    message = error_body[:250]

                self.send_json(502, {
                    "success": False,
                    "message": (
                        provider
                        + " HTTP "
                        + str(error.code)
                        + ": "
                        + str(message)[:250]
                    )
                })

            except urllib.error.URLError as error:

                print(
                    "[PHONG WEB V28] Connection error:",
                    provider,
                    str(error.reason)
                )

                self.send_json(502, {
                    "success": False,
                    "message": "Không thể kết nối máy chủ " + provider + "."
                })

            except TimeoutError:

                self.send_json(504, {
                    "success": False,
                    "message": provider + " phản hồi quá lâu. Vui lòng thử lại."
                })

            except ValueError as error:

                self.send_json(502, {
                    "success": False,
                    "message": str(error)
                })

            except Exception as error:

                print(
                    "[PHONG WEB V28] Create link error:",
                    type(error).__name__,
                    str(error)[:300]
                )

                self.send_json(500, {
                    "success": False,
                    "message": "Lỗi xử lý API: " + type(error).__name__
                })

            return


        # ======================================
        # PROVIDER CALLBACK
        # ======================================

        if path == "/provider-return":

            token = query.get("token", [""])[0]

            cleanup_sessions()

            destination = None
            valid = False

            with SESSIONS_LOCK:

                session = SESSIONS.get(token)

                if session:
                    session["returned"] = True
                    destination = session.get("destination")
                    valid = True

            if not valid:

                print("[PHONG WEB V28] Invalid callback")

                self.redirect(
                    "/?result=failed&destination=location"
                )

                return

            print(
                "[PHONG WEB V28] Callback received:",
                destination
            )

            # LOCATION:
            # Chưa có API xác nhận View nên không báo thành công.
            if destination == "location":

                self.redirect(
                    "/?result=failed"
                    "&destination=location"
                    "&token="
                    + quote(token, safe="")
                )

                return

            # DETA: giữ nguyên luồng V27.
            self.redirect(
                "/?result=success"
                "&destination=deta"
                "&token="
                + quote(token, safe="")
            )

            return


        # ======================================
        # CHECK SESSION
        # ======================================

        if path == "/check-session":

            token = query.get("token", [""])[0]
            session = get_session(token)

            if session and session.get("returned"):

                self.send_json(200, {
                    "success": True,
                    "returned": True,
                    "view_confirmed": bool(
                        session.get("view_confirmed", False)
                    ),
                    "destination": session.get("destination"),
                    "message": "Đã nhận callback từ nhà cung cấp."
                })

            else:

                self.send_json(403, {
                    "success": False,
                    "returned": False,
                    "view_confirmed": False,
                    "message": "Phiên vượt link không hợp lệ hoặc đã hết hạn."
                })

            return


        # ======================================
        # DOWNLOAD LOCATION
        # Chỉ cho phép nếu View được xác nhận.
        # Hiện tại chưa có API xác nhận nên mặc định khóa.
        # ======================================

        if path == "/download-location":

            token = query.get("token", [""])[0]
            session = get_session(token)

            if (
                not session
                or not session.get("returned")
                or session.get("destination") != "location"
                or not session.get("view_confirmed", False)
            ):

                self.send_json(403, {
                    "success": False,
                    "message": (
                        "Chưa có xác nhận View thành công từ nhà cung cấp."
                    )
                })

                return

            print("[PHONG WEB V28] Location download redirect")
            self.redirect(MEDIAFIRE_LINK)

            return


        # ======================================
        # DOWNLOAD DETA
        # ======================================

        if path == "/download-deta":

            token = query.get("token", [""])[0]

            if not check_session(token, "deta"):

                self.send_json(403, {
                    "success": False,
                    "message": "Bạn chưa hoàn thành bước vượt link Deta."
                })

                return

            print("[PHONG WEB V28] Deta download redirect")
            self.redirect(DETA_MEDIAFIRE_LINK)

            return


        # ======================================
        # LEGACY ROUTES
        # ======================================

        if path == "/create-link":

            self.redirect("/dinh-vi")
            return

        if path == "/create-link4m":

            self.redirect("/menu")
            return

        if path == "/complete":

            self.redirect(MEDIAFIRE_LINK)
            return

        if path == "/link4m-return":

            token = query.get("token", [""])[0]

            self.redirect(
                "/provider-return?token=" + quote(token, safe="")
            )

            return

        if path == "/check-link4m":

            token = query.get("token", [""])[0]

            if check_session(token, "deta"):

                self.send_json(200, {
                    "success": True,
                    "message": "Đã xác nhận phiên."
                })

            else:

                self.send_json(403, {
                    "success": False,
                    "message": "Phiên không hợp lệ."
                })

            return


        # ======================================
        # STATIC FILES
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

            print(
                "[PHONG WEB V28] File error:",
                str(error)
            )


    def log_message(self, format, *args):

        print(
            "[PHONG WEB V28]",
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
    print("          PHONG WEB V28")
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

    print(
        "YeuMoney Developers API:",
        "ENABLED" if YEUMONEY_API_TOKEN else "MISSING API TOKEN"
    )

    print("Location route: /dinh-vi")
    print("Deta route: /menu")
    print("Provider selector: Link4M / VuotNhanh / YeuMoney")
    print("Create endpoint: /create-short-link")
    print("Callback endpoint: /provider-return")
    print("Session check: /check-session")
    print("Location download: /download-location")
    print("Deta download: /download-deta")
    print("Location View verification: NOT CONFIGURED")
    print("Music button: ENABLED")
    print("Music looping: ENABLED")
    print("PHONG WEB VERSION: V28")

    print("====================================")

    try:

        server.serve_forever()

    except KeyboardInterrupt:

        print("\n[PHONG WEB] Server stopped.")

    finally:

        server.server_close()
