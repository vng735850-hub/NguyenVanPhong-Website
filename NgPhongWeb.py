
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

# =========================================================
# PHONG WEB V2.0.0
# LINK4M ONLY
# LOCATION + DETA + PROXY + MIZZE + THANK YOU + MUSIC
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
PORT = int(os.environ.get("PORT", 5000))

# =========================================================
# LINK4M API
# =========================================================

LINK4M_API_TOKEN = os.environ.get("LINK4M_API_TOKEN", "").strip()
LINK4M_ENDPOINT = "https://link4m.co/api-shorten/v2"

# =========================================================
# WEBSITE
# =========================================================

SITE_URL = os.environ.get(
    "SITE_URL",
    "https://nvp-com.onrender.com"
).strip().rstrip("/")

# =========================================================
# MEDIAFIRE LINKS
# =========================================================

MEDIAFIRE_LINK = (
    "https://www.mediafire.com/file/"
    "yen60lu05hfnng4/DINH_VI_BT.zip/file"
)

DETA_MEDIAFIRE_LINK = (
    "https://www.mediafire.com/file/"
    "wohet4glfwyn5j0/Deta_Crack.7z/file"
)

PROXY_MEDIAFIRE_LINK = (
    "https://www.mediafire.com/file/"
    "zdoapnkcx9v70gq/PROXY+MOD+ALEN+Crack.zip/file"
)

MIZZE_MEDIAFIRE_LINK = (
    "https://www.mediafire.com/file/"
    "2plraqmzcl7gk4m/mizze+crack+adr+chs+ff+india.zip/file"
)

DESTINATIONS = {
    "location": MEDIAFIRE_LINK,
    "deta": DETA_MEDIAFIRE_LINK,
    "proxy": PROXY_MEDIAFIRE_LINK,
    "mizze": MIZZE_MEDIAFIRE_LINK
}

DESTINATION_NAMES = {
    "location": "Định Vị",
    "deta": "Deta",
    "proxy": "Proxy Mod Alen Crack",
    "mizze": "Menu Mizze Crack"
}

DESTINATION_ROUTES = {
    "location": "/dinh-vi",
    "deta": "/menu",
    "proxy": "/proxy-mod-alen-crack",
    "mizze": "/mizze-crack"
}

DOWNLOAD_ROUTES = {
    "location": "/download-location",
    "deta": "/download-deta",
    "proxy": "/download-proxy",
    "mizze": "/download-mizze"
}

SESSIONS = {}
SESSIONS_LOCK = threading.Lock()
SESSION_TTL = 30 * 60


# =========================================================
# HTML
# =========================================================

HTML = r"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<meta name="theme-color" content="#080d20">
<title>NGUYỄN VĂN PHONG WEBSITE</title>

<style>
*{box-sizing:border-box}
html{scroll-behavior:smooth}

body{
    margin:0;
    min-height:100vh;
    font-family:Arial,Helvetica,sans-serif;
    color:white;
    background:
        linear-gradient(rgba(3,7,25,.82),rgba(3,7,25,.88)),
        url('/background.jpg') center center/cover fixed no-repeat;
    background-color:#080d20;
}

header{
    position:relative;
    z-index:1000;
    width:100%;
    min-height:75px;
    display:flex;
    align-items:center;
    justify-content:center;
    gap:13px;
    padding:12px 15px;
    background:rgba(4,10,30,.88);
    border-bottom:1px solid rgba(65,165,255,.5);
    box-shadow:0 4px 20px rgba(0,0,0,.3);
}

.hamburger-button{
    width:43px;height:43px;flex-shrink:0;
    display:flex;align-items:center;justify-content:center;
    border:1px solid #55baff;border-radius:10px;
    background:rgba(0,120,255,.2);
    color:white;font-size:25px;cursor:pointer;
}
.hamburger-button:hover{background:#087ce5}

.header-title{
    font-size:clamp(15px,3vw,24px);
    font-weight:900;text-align:center;letter-spacing:1px;
    color:white;text-shadow:0 0 8px #168cff,0 0 15px #168cff;
}

.side-menu{
    display:none;position:absolute;top:67px;left:12px;
    width:200px;padding:9px;
    background:rgba(5,14,38,.98);
    border:1px solid #299cff;border-radius:12px;
    box-shadow:0 8px 25px rgba(0,0,0,.5);
}
.side-menu.show{display:block}
.side-menu a{
    display:block;padding:13px;color:white;
    text-decoration:none;font-weight:bold;border-radius:8px;
}
.side-menu a:hover{background:#087ce5}

.container{
    width:min(900px,92%);
    margin:25px auto;text-align:center;
}

.hero-logo{
    display:block;width:125px;height:125px;
    object-fit:contain;margin:20px auto;
    border-radius:50%;filter:drop-shadow(0 0 15px #168cff);
}

h1{
    font-size:clamp(23px,5vw,34px);
    font-weight:900;color:white;text-shadow:0 0 15px #168cff;
}

.subtitle{
    color:#d2e7ff;font-size:14px;line-height:1.8;
    margin:15px auto 25px;
}

.location-container,.menu-container{margin:18px auto}

.location-link{display:block;color:inherit;text-decoration:none}

.location-card{
    display:flex;align-items:center;justify-content:center;gap:20px;
    padding:22px 15px;background:rgba(10,27,60,.88);
    border:1px solid #459fff;border-radius:15px;
    box-shadow:0 0 18px rgba(0,130,255,.18);
    transition:.2s;
}
.location-card:hover,.menu-card:hover{
    transform:translateY(-3px);border-color:#8bd4ff;
    box-shadow:0 0 25px rgba(0,140,255,.4);
}
.location-emoji{font-size:43px}
.location-info{text-align:left}
.location-info h2{margin:0 0 9px;font-size:19px}
.location-info p{margin:0 0 12px;color:#c6e1ff;font-size:13px}
.location-button{
    display:inline-block;padding:9px 17px;
    background:linear-gradient(120deg,#0877e8,#12a8ff);
    color:white;font-weight:bold;font-size:12px;border-radius:8px;
}

.menu-card{
    padding:23px 15px;background:rgba(9,24,55,.9);
    border:1px solid rgba(64,157,255,.65);border-radius:15px;
    box-shadow:0 0 17px rgba(0,110,255,.15);transition:.2s;
}
.menu-card h2{margin:0 0 17px;font-size:18px}

.open-menu-button{
    padding:12px 25px;color:white;font-weight:bold;font-size:13px;
    background:linear-gradient(120deg,#0877e8,#12a8ff);
    border:none;border-radius:9px;cursor:pointer;
}
.open-menu-button:hover{filter:brightness(1.2)}

.page{display:none}
.page.active{display:block}

.link-box{
    max-width:570px;margin:35px auto;padding:28px 20px;
    background:rgba(7,21,49,.94);
    border:1px solid #399cff;border-radius:17px;
    box-shadow:0 0 25px rgba(0,110,255,.2);
}
.link-icon{font-size:48px;margin-bottom:12px}
.link-box h2{color:#8acaff;font-size:20px;line-height:1.5}
.link-description{
    color:#d1e5ff;font-size:14px;line-height:1.8;
    margin:15px auto 22px;
}

.cross-link-button{
    display:inline-block;padding:14px 25px;color:white;
    font-size:14px;font-weight:bold;text-decoration:none;
    background:linear-gradient(120deg,#0877e8,#12a8ff);
    border:none;border-radius:10px;cursor:pointer;
    box-shadow:0 4px 15px rgba(0,120,255,.3);transition:.2s;
}
.cross-link-button:hover{filter:brightness(1.2);transform:translateY(-2px)}
.cross-link-button:disabled{opacity:.6;cursor:wait;transform:none}

.back-button{
    display:inline-block;padding:11px 18px;color:white;
    font-size:13px;font-weight:bold;text-decoration:none;
    background:rgba(20,65,120,.8);
    border:1px solid #4caeff;border-radius:9px;
}
.back-button:hover{background:#126fc4}

.status{
    min-height:24px;margin:17px auto;color:#ffe18b;
    font-size:13px;line-height:1.7;overflow-wrap:anywhere;
}
.status.error{color:#ff7777}
.status.success{color:#5dffac;font-weight:bold}

.result-action{
    display:inline-block;margin:12px auto;padding:14px 30px;
    color:white;font-weight:bold;font-size:15px;text-decoration:none;
    background:linear-gradient(120deg,#08a75d,#16d68b);
    border-radius:10px;box-shadow:0 0 18px rgba(0,220,130,.3);
    border:0;cursor:pointer;
}
.result-action:hover{filter:brightness(1.15)}
.hidden{display:none!important}

/* THANK YOU IMAGE BUTTON */

.thank-image-button{
    display:block;
    width:min(260px,90%);
    margin:20px auto;
    padding:0;
    border:2px solid #55baff;
    border-radius:12px;
    overflow:hidden;
    background:rgba(0,100,220,.2);
    cursor:pointer;
    box-shadow:0 0 18px rgba(0,145,255,.35);
}
.thank-image-button img{
    display:block;width:100%;height:auto;min-height:65px;
    object-fit:contain;
}
.thank-image-button:hover{filter:brightness(1.2)}

.music-mini{
    position:relative;display:flex;
    align-items:center;justify-content:center;
    margin:25px auto 15px;
}
.music-mini button{
    width:53px;height:53px;
    display:flex;align-items:center;justify-content:center;
    border:2px solid #75caff;border-radius:50%;
    color:white;background:linear-gradient(135deg,#086de0,#13b5ff);
    font-size:21px;cursor:pointer;
    box-shadow:0 0 18px rgba(0,145,255,.55);
}
.music-mini button.playing{animation:musicPulse 1.4s infinite}
@keyframes musicPulse{
    0%,100%{box-shadow:0 0 10px #159dff}
    50%{box-shadow:0 0 28px #36caff}
}

footer{
    width:100%;padding:18px 10px 22px;text-align:center;
    color:#c1dcff;font-size:13px;line-height:1.9;
    background:rgba(3,8,23,.9);
    border-top:1px solid rgba(80,170,255,.3);
}
footer strong{color:#55baff;letter-spacing:1px}

@media(max-width:600px){
    header{justify-content:flex-start}
    .header-title{flex:1;font-size:15px;text-align:center}
    .location-card{gap:12px}
    .location-info h2{font-size:16px}
    .link-box{margin:22px auto;padding:23px 15px}
}
</style>
</head>

<body>

<header>
    <button class="hamburger-button" id="hamburgerButton"
        type="button" aria-label="Mở menu">☰</button>
    <div class="header-title">NGUYỄN VĂN PHONG WEBSITE</div>
    <nav class="side-menu" id="sideMenu">
        <a href="/" id="homeMenuButton">🏠 TRANG CHỦ</a>
    </nav>
</header>

<main class="container">

<!-- HOME -->

<section class="page" id="homePage">
    <img class="hero-logo" src="/logo.png" alt="PHONG WEB">
    <h1>WELCOME TO PHONG WEB</h1>

    <div class="subtitle">
        Chào mừng bạn đến với website của Nguyễn Văn Phong.
        <br>📍 ĐỊNH VỊ XANH TÍM OB55
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
            <button class="open-menu-button" id="openMenuButton"
                type="button">MỞ MENU</button>
        </div>
    </section>

    <section class="menu-container">
        <div class="menu-card">
            <h2>🌐 PROXY MOD ALEN CRACK</h2>
            <button class="open-menu-button" id="openProxyButton"
                type="button">MỞ MỤC</button>
        </div>
    </section>

    <section class="menu-container">
        <div class="menu-card">
            <h2>🎮 MENU MIZZE CRACK</h2>
            <button class="open-menu-button" id="openMizzeButton"
                type="button">MỞ MỤC</button>
        </div>
    </section>
</section>

<!-- LOCATION -->

<section class="page" id="locationPage">
    <div class="link-box">
        <div class="link-icon">📍</div>
        <h2>BẠN CẦN VƯỢT LINK ĐỂ LẤY FILE MEDIAFIRE</h2>
        <div class="link-description">
            Nhấn nút bên dưới để tạo liên kết vượt.
            <br>Sau khi hoàn thành Link4M, bạn sẽ quay lại PHONG WEB.
        </div>
        <button class="cross-link-button" id="locationCrossButton"
            type="button">🔓 VƯỢT LINK</button>
        <div class="status" id="locationStatus"></div>
        <br><a class="back-button" href="/">← QUAY LẠI TRANG CHỦ</a>
    </div>
</section>

<!-- DETA -->

<section class="page" id="detaPage">
    <div class="link-box">
        <div class="link-icon">🔐</div>
        <h2>BẠN CẦN VƯỢT LINK ĐỂ LẤY FILE DETA</h2>
        <div class="link-description">
            Nhấn nút bên dưới để tạo liên kết vượt.
            <br>Sau khi hoàn thành Link4M, bạn sẽ quay lại PHONG WEB.
        </div>
        <button class="cross-link-button" id="detaCrossButton"
            type="button">🔓 VƯỢT LINK</button>
        <div class="status" id="detaStatus"></div>
        <br><a class="back-button" href="/">← QUAY LẠI TRANG CHỦ</a>
    </div>
</section>

<!-- PROXY -->

<section class="page" id="proxyPage">
    <div class="link-box">
        <div class="link-icon">🌐</div>
        <h2>BẠN CẦN VƯỢT LINK ĐỂ LẤY FILE PROXY MOD ALEN CRACK</h2>
        <div class="link-description">
            Nhấn nút bên dưới để tạo liên kết vượt.
            <br>Sau khi hoàn thành Link4M, bạn sẽ quay lại PHONG WEB.
        </div>
        <button class="cross-link-button" id="proxyCrossButton"
            type="button">🔓 VƯỢT LINK</button>
        <div class="status" id="proxyStatus"></div>
        <br><a class="back-button" href="/">← QUAY LẠI TRANG CHỦ</a>
    </div>
</section>

<!-- MIZZE -->

<section class="page" id="mizzePage">
    <div class="link-box">
        <div class="link-icon">🎮</div>
        <h2>BẠN CẦN VƯỢT LINK ĐỂ LẤY FILE MENU MIZZE CRACK</h2>
        <div class="link-description">
            Nhấn nút bên dưới để tạo liên kết vượt.
            <br>Sau khi hoàn thành Link4M, bạn sẽ quay lại PHONG WEB.
        </div>
        <button class="cross-link-button" id="mizzeCrossButton"
            type="button">🔓 VƯỢT LINK</button>
        <div class="status" id="mizzeStatus"></div>
        <br><a class="back-button" href="/">← QUAY LẠI TRANG CHỦ</a>
    </div>
</section>

<!-- THANK YOU PAGE -->

<section class="page" id="thankPage">
    <div class="link-box">
        <div class="link-icon">💙</div>
        <h2>Cảm Ơn Vì Đã Ủng Hộ Cho Phong</h2>

        <div class="link-description">
            Phong chân thành cảm ơn bạn đã dành thời gian ủng hộ website.
            <br>Nhấn vào hình bên dưới để nghe lời cảm ơn nhé!
        </div>

        <button class="thank-image-button" id="thankAudioButton"
            type="button" aria-label="Phát lời cảm ơn">
            <img src="/cam-on-tu-phong.png"
                alt="Cảm Ơn Từ Phong">
        </button>

        <div class="status" id="thankStatus">
            🔊 Nhấn vào ảnh để phát âm thanh cảm ơn.
        </div>

        <button class="cross-link-button" id="continueButton"
            type="button">TIẾP THEO →</button>

        <audio id="thankAudio" src="/cam-on-tu-phong.mp3"
            preload="none"></audio>
    </div>
</section>

<!-- SUCCESS / FAILURE PAGE -->

<section class="page" id="resultPage">
    <div class="link-box">
        <div class="link-icon" id="resultIcon">✅</div>
        <h2 id="resultTitle">Vượt Link Thành Công</h2>

        <div class="link-description" id="resultDescription"></div>

        <a class="result-action hidden" id="resultAction"
            href="/">LẤY FILE</a>

        <button class="cross-link-button hidden" id="retryButton"
            type="button">🔄 VƯỢT LINK MỚI</button>

        <div class="status" id="resultStatus"></div>
        <br>
        <a class="back-button" id="resultBack" href="/">
            ← QUAY LẠI TRANG CHỦ
        </a>
    </div>
</section>

</main>

<div class="music-mini">
    <button id="musicButton" aria-label="Bật hoặc tắt nhạc"
        title="Bật / Tắt nhạc" type="button">
        <span id="musicIcon">▶</span>
    </button>
</div>

<audio id="backgroundMusic" src="/music.mp3" loop></audio>

<footer>
    © 2026 Nguyễn Văn Phong Website
    <br><strong>PHONG WEB V2.0.0</strong>
</footer>

<script>
/* =====================================================
   ELEMENTS
===================================================== */

const pages = {
    home: document.getElementById("homePage"),
    location: document.getElementById("locationPage"),
    deta: document.getElementById("detaPage"),
    proxy: document.getElementById("proxyPage"),
    mizze: document.getElementById("mizzePage"),
    thank: document.getElementById("thankPage"),
    result: document.getElementById("resultPage")
};

const hamburgerButton = document.getElementById("hamburgerButton");
const sideMenu = document.getElementById("sideMenu");
const homeMenuButton = document.getElementById("homeMenuButton");

const musicButton = document.getElementById("musicButton");
const musicIcon = document.getElementById("musicIcon");
const backgroundMusic = document.getElementById("backgroundMusic");

const thankAudio = document.getElementById("thankAudio");
const thankAudioButton = document.getElementById("thankAudioButton");
const thankStatus = document.getElementById("thankStatus");
const continueButton = document.getElementById("continueButton");

const resultIcon = document.getElementById("resultIcon");
const resultTitle = document.getElementById("resultTitle");
const resultDescription = document.getElementById("resultDescription");
const resultAction = document.getElementById("resultAction");
const resultStatus = document.getElementById("resultStatus");
const retryButton = document.getElementById("retryButton");

const destinationRoutes = {
    location: "/dinh-vi",
    deta: "/menu",
    proxy: "/proxy-mod-alen-crack",
    mizze: "/mizze-crack"
};

const downloadRoutes = {
    location: "/download-location",
    deta: "/download-deta",
    proxy: "/download-proxy",
    mizze: "/download-mizze"
};

/* =====================================================
   PAGE NAVIGATION
===================================================== */

function hideAllPages() {
    Object.values(pages).forEach(page => {
        page.classList.remove("active");
    });
}

function showPage() {
    hideAllPages();

    const params = new URLSearchParams(location.search);
    const result = params.get("result");

    if (result === "thanks") {
        pages.thank.classList.add("active");
        return;
    }

    if (result === "success" || result === "failed") {
        pages.result.classList.add("active");
        checkResult();
        return;
    }

    const routes = {
        "/": pages.home,
        "/index.html": pages.home,
        "/dinh-vi": pages.location,
        "/menu": pages.deta,
        "/proxy-mod-alen-crack": pages.proxy,
        "/mizze-crack": pages.mizze
    };

    (routes[location.pathname] || pages.home).classList.add("active");
}

function navigate(path) {
    history.pushState({}, "", path);
    showPage();
    window.scrollTo(0, 0);
}

window.addEventListener("popstate", showPage);

/* =====================================================
   HOME BUTTONS
===================================================== */

document.getElementById("openMenuButton").addEventListener(
    "click", () => navigate("/menu")
);

document.getElementById("openProxyButton").addEventListener(
    "click", () => navigate("/proxy-mod-alen-crack")
);

document.getElementById("openMizzeButton").addEventListener(
    "click", () => navigate("/mizze-crack")
);

/* =====================================================
   CREATE LINK
===================================================== */

async function createShortLink(destination, button, status) {
    button.disabled = true;
    button.textContent = "ĐANG XỬ LÝ...";
    status.className = "status";
    status.textContent = "Đang kết nối API LINK4M...";

    try {
        const response = await fetch(
            "/create-short-link?destination=" +
            encodeURIComponent(destination),
            {cache: "no-store"}
        );

        const data = await response.json();

        if (!response.ok || !data.success) {
            throw new Error(data.message || "Không thể tạo link.");
        }

        if (!data.url) {
            throw new Error("Link4M không trả về URL.");
        }

        status.textContent = "Đang chuyển đến Link4M...";
        window.location.href = data.url;

    } catch (error) {
        status.className = "status error";
        status.textContent = "LỖI: " + error.message;
        button.disabled = false;
        button.textContent = "🔓 THỬ LẠI";
    }
}

function setupCrossButton(destination, buttonId, statusId) {
    const button = document.getElementById(buttonId);
    const status = document.getElementById(statusId);

    button.addEventListener("click", () => {
        createShortLink(destination, button, status);
    });
}

setupCrossButton("location", "locationCrossButton", "locationStatus");
setupCrossButton("deta", "detaCrossButton", "detaStatus");
setupCrossButton("proxy", "proxyCrossButton", "proxyStatus");
setupCrossButton("mizze", "mizzeCrossButton", "mizzeStatus");

/* =====================================================
   THANK YOU AUDIO
===================================================== */

thankAudioButton.addEventListener("click", async () => {
    try {
        if (thankAudio.paused) {
            await thankAudio.play();
            thankStatus.className = "status success";
            thankStatus.textContent = "🎵 Đang phát lời cảm ơn từ Phong...";
        } else {
            thankAudio.pause();
            thankStatus.className = "status";
            thankStatus.textContent = "Đã tạm dừng âm thanh.";
        }
    } catch (error) {
        thankStatus.className = "status error";
        thankStatus.textContent =
            "Không thể phát âm thanh. Hãy kiểm tra file cam-on-tu-phong.mp3.";
    }
});

thankAudio.addEventListener("ended", () => {
    thankStatus.className = "status success";
    thankStatus.textContent = "💙 Cảm ơn bạn đã lắng nghe!";
});

/* =====================================================
   CONTINUE TO SUCCESS PAGE
===================================================== */

continueButton.addEventListener("click", async () => {
    const params = new URLSearchParams(location.search);
    const token = params.get("token");
    const destination = params.get("destination");

    if (!token || !destination || !destinationRoutes[destination]) {
        showFailure("Không tìm thấy thông tin phiên vượt link.", destination);
        return;
    }

    continueButton.disabled = true;
    continueButton.textContent = "ĐANG KIỂM TRA...";

    try {
        const response = await fetch(
            "/check-session?token=" + encodeURIComponent(token),
            {cache: "no-store"}
        );

        const data = await response.json();

        if (!response.ok || !data.success || !data.returned) {
            throw new Error(data.message || "Phiên chưa được xác nhận.");
        }

        if (data.destination !== destination) {
            throw new Error("Thông tin mục vượt link không khớp.");
        }

        history.pushState(
            {},
            "",
            "/?result=success&destination=" +
            encodeURIComponent(destination) +
            "&token=" + encodeURIComponent(token)
        );

        showPage();
        window.scrollTo(0, 0);

    } catch (error) {
        showFailure(error.message, destination);
    } finally {
        continueButton.disabled = false;
        continueButton.textContent = "TIẾP THEO →";
    }
});

/* =====================================================
   RESULT PAGE
===================================================== */

function showFailure(message, destination) {
    hideAllPages();
    pages.result.classList.add("active");

    resultIcon.textContent = "❌";
    resultTitle.textContent = "Vượt Link Không Thành Công";
    resultDescription.textContent =
        "Phiên vượt link chưa được xác nhận hoặc đã hết hạn.";

    resultStatus.className = "status error";
    resultStatus.textContent = message || "Vui lòng thử vượt link mới.";

    resultAction.classList.add("hidden");
    retryButton.classList.remove("hidden");

    retryButton.onclick = () => {
        const route = destinationRoutes[destination] || "/";
        history.pushState({}, "", route);
        showPage();
        window.scrollTo(0, 0);
    };

    document.getElementById("resultBack").href = "/";
}

async function checkResult() {
    const params = new URLSearchParams(location.search);

    const result = params.get("result");
    const destination = params.get("destination");
    const token = params.get("token");

    resultAction.classList.add("hidden");
    retryButton.classList.add("hidden");
    resultStatus.className = "status";
    resultStatus.textContent = "";

    if (result === "failed") {
        showFailure(
            "Không nhận được callback hợp lệ từ Link4M.",
            destination
        );
        return;
    }

    if (result !== "success" || !token ||
        !destination || !downloadRoutes[destination]) {
        showFailure(
            "Không tìm thấy thông tin phiên vượt link.",
            destination
        );
        return;
    }

    resultIcon.textContent = "⏳";
    resultTitle.textContent = "ĐANG KIỂM TRA";
    resultDescription.textContent =
        "Đang kiểm tra phiên quay lại từ Link4M...";

    try {
        const response = await fetch(
            "/check-session?token=" + encodeURIComponent(token),
            {cache: "no-store"}
        );

        const data = await response.json();

        if (!response.ok || !data.success || !data.returned) {
            throw new Error(data.message || "Phiên không hợp lệ.");
        }

        if (data.destination !== destination) {
            throw new Error("Thông tin mục vượt link không khớp.");
        }

        resultIcon.textContent = "✅";
        resultTitle.textContent = "Vượt Link Thành Công";

        resultDescription.textContent =
            "Bạn đã quay lại PHONG WEB. Nhấn LẤY FILE để mở MediaFire.";

        resultStatus.className = "status success";
        resultStatus.textContent =
            "Đã nhận callback cho mục " + destination + ".";

        resultAction.href =
            downloadRoutes[destination] +
            "?token=" + encodeURIComponent(token);

        resultAction.classList.remove("hidden");

    } catch (error) {
        showFailure(error.message, destination);
    }
}

/* =====================================================
   HAMBURGER MENU
===================================================== */

hamburgerButton.addEventListener("click", event => {
    event.stopPropagation();
    sideMenu.classList.toggle("show");
});

homeMenuButton.addEventListener("click", event => {
    event.preventDefault();
    sideMenu.classList.remove("show");
    navigate("/");
});

document.addEventListener("click", event => {
    if (
        !sideMenu.contains(event.target) &&
        !hamburgerButton.contains(event.target)
    ) {
        sideMenu.classList.remove("show");
    }
});

/* =====================================================
   BACKGROUND MUSIC
===================================================== */

musicButton.addEventListener("click", async () => {
    try {
        if (backgroundMusic.paused) {
            await backgroundMusic.play();
            musicIcon.textContent = "Ⅱ";
            musicButton.classList.add("playing");
        } else {
            backgroundMusic.pause();
            musicIcon.textContent = "▶";
            musicButton.classList.remove("playing");
        }
    } catch (error) {
        alert("Không thể phát nhạc. Kiểm tra file music.mp3.");
    }
});

/* =====================================================
   START
===================================================== */

showPage();
</script>

</body>
</html>
"""


# =========================================================
# URL VALIDATION
# =========================================================

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


# =========================================================
# SESSION HELPERS
# =========================================================

def cleanup_sessions():
    now = time.time()

    with SESSIONS_LOCK:
        expired = [
            token for token, session in SESSIONS.items()
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


# =========================================================
# API REQUEST HELPERS
# =========================================================

def api_request(url):
    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/131.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json, text/plain, */*",
        "Cache-Control": "no-cache"
    }

    request = urllib.request.Request(
        url,
        headers=headers,
        method="GET"
    )

    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            return response.read().decode(
                "utf-8",
                errors="replace"
            )

    except urllib.error.HTTPError as error:
        error_body = error.read().decode(
            "utf-8",
            errors="replace"
        )

        print("[LINK4M HTTP ERROR]", error.code, error_body[:400])

        raise ValueError(
            "Link4M HTTP " + str(error.code) + ": " +
            error_body[:250]
        )

    except urllib.error.URLError as error:
        raise ValueError(
            "Không thể kết nối Link4M: " + str(error.reason)
        )


def read_api_json(url):
    body = api_request(url)

    try:
        result = json.loads(body)
    except json.JSONDecodeError:
        print("[LINK4M INVALID JSON]", body[:500])
        raise ValueError("Link4M không trả về JSON hợp lệ.")

    if not isinstance(result, dict):
        raise ValueError("Link4M trả về dữ liệu không đúng định dạng.")

    return result


# =========================================================
# LINK4M API
# =========================================================

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
    result = read_api_json(api_url)

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


# =========================================================
# WEBSITE SERVER
# =========================================================

class Website(BaseHTTPRequestHandler):

    server_version = "PhongWeb/2.0.0"

    # -----------------------------------------------------
    # JSON RESPONSE
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # HTML RESPONSE
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # REDIRECT
    # -----------------------------------------------------

    def redirect(self, location):
        self.send_response(302)
        self.send_header("Location", location)
        self.send_header("Cache-Control", "no-store")
        self.end_headers()

    # -----------------------------------------------------
    # STATIC FILES
    # -----------------------------------------------------

    def send_static_file(self, path):
        allowed_files = {
            "/logo.png",
            "/background.jpg",
            "/music.mp3",
            "/cam-on-tu-phong.png",
            "/cam-on-tu-phong.mp3"
        }

        if path not in allowed_files:
            self.send_error(404, "File not found")
            return

        file_path = BASE_DIR / path.lstrip("/")

        if not file_path.is_file():
            self.send_error(404, "Asset not found")
            return

        content_type = (
            mimetypes.guess_type(str(file_path))[0]
            or "application/octet-stream"
        )

        try:
            file_size = file_path.stat().st_size

            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(file_size))
            self.send_header("Cache-Control", "public, max-age=3600")
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
            print("[PHONG WEB] FILE ERROR:", str(error))

    # =====================================================
    # MAIN ROUTES
    # =====================================================

    def do_GET(self):
        parsed_request = urlsplit(self.path)
        path = unquote(parsed_request.path)

        query = parse_qs(parsed_request.query)

        # -------------------------------------------------
        # WEBSITE PAGES
        # -------------------------------------------------

        if path in (
            "/",
            "/index.html",
            "/dinh-vi",
            "/menu",
            "/proxy-mod-alen-crack",
            "/mizze-crack"
        ):
            self.send_html_page()
            return

        # -------------------------------------------------
        # CREATE SHORT LINK
        # -------------------------------------------------

        if path == "/create-short-link":
            provider = query.get("provider", ["link4m"])[0].lower()
            destination = query.get("destination", [""])[0].lower()

            if provider != "link4m":
                self.send_json(400, {
                    "success": False,
                    "message": "PHONG WEB V2.0.0 chỉ hỗ trợ Link4M."
                })
                return

            if destination not in DESTINATIONS:
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

            if not LINK4M_API_TOKEN:
                self.send_json(500, {
                    "success": False,
                    "message": "Chưa cấu hình LINK4M_API_TOKEN trên Render."
                })
                return

            token = secrets.token_urlsafe(32)

            callback_url = (
                SITE_URL
                + "/provider-return?token="
                + quote(token, safe="")
            )

            try:
                shortened_url = create_link4m_url(callback_url)

                cleanup_sessions()

                with SESSIONS_LOCK:
                    SESSIONS[token] = {
                        "created": time.time(),
                        "returned": False,
                        "provider": "link4m",
                        "destination": destination
                    }

                self.send_json(200, {
                    "success": True,
                    "url": shortened_url,
                    "provider": "link4m",
                    "destination": destination
                })

                print(
                    "[PHONG WEB V2.0.0] CREATED:",
                    "link4m",
                    destination
                )

            except urllib.error.URLError as error:
                print("[PHONG WEB] CONNECTION ERROR:", str(error.reason))

                self.send_json(502, {
                    "success": False,
                    "message": "Không thể kết nối API LINK4M."
                })

            except TimeoutError:
                self.send_json(504, {
                    "success": False,
                    "message": "Link4M phản hồi quá lâu. Vui lòng thử lại."
                })

            except ValueError as error:
                print("[PHONG WEB] API ERROR:", str(error))

                self.send_json(502, {
                    "success": False,
                    "message": str(error)
                })

            except Exception as error:
                print(
                    "[PHONG WEB] CREATE ERROR:",
                    type(error).__name__,
                    str(error)[:300]
                )

                self.send_json(500, {
                    "success": False,
                    "message": "Lỗi xử lý API: " + type(error).__name__
                })

            return

        # -------------------------------------------------
        # LINK4M CALLBACK
        # -------------------------------------------------

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
                self.redirect(
                    "/?result=failed&destination=deta"
                )
                return

            print(
                "[PHONG WEB V2.0.0] CALLBACK:",
                "link4m",
                destination
            )

            # Tất cả 4 mục đều chuyển đến trang cảm ơn.

            self.redirect(
                "/?result=thanks"
                "&destination="
                + quote(destination, safe="")
                + "&token="
                + quote(token, safe="")
            )

            return

        # -------------------------------------------------
        # CHECK SESSION
        # -------------------------------------------------

        if path == "/check-session":
            token = query.get("token", [""])[0]
            session = get_session(token)

            if session and session.get("returned"):
                self.send_json(200, {
                    "success": True,
                    "returned": True,
                    "destination": session.get("destination"),
                    "provider": session.get("provider"),
                    "message": "Đã nhận callback từ Link4M."
                })
            else:
                self.send_json(403, {
                    "success": False,
                    "returned": False,
                    "message": (
                        "Phiên vượt link không hợp lệ hoặc đã hết hạn."
                    )
                })

            return

        # -------------------------------------------------
        # DOWNLOAD ROUTES - ALL 4 DESTINATIONS
        # -------------------------------------------------

        download_routes = {
            "/download-location": "location",
            "/download-deta": "deta",
            "/download-proxy": "proxy",
            "/download-mizze": "mizze"
        }

        if path in download_routes:
            destination = download_routes[path]
            token = query.get("token", [""])[0]

            if not check_session(token, destination):
                self.send_json(403, {
                    "success": False,
                    "message": (
                        "Bạn chưa hoàn thành bước quay lại từ Link4M cho mục "
                        + DESTINATION_NAMES[destination]
                        + "."
                    )
                })
                return

            print(
                "[PHONG WEB V2.0.0] DOWNLOAD:",
                destination
            )

            self.redirect(DESTINATIONS[destination])
            return

        # -------------------------------------------------
        # LEGACY ROUTES
        # -------------------------------------------------

        if path == "/create-link":
            self.redirect("/dinh-vi")
            return

        if path == "/create-link4m":
            self.redirect("/menu")
            return

        if path == "/complete":
            self.redirect("/")
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

        # -------------------------------------------------
        # STATIC FILES
        # -------------------------------------------------

        if path in (
            "/logo.png",
            "/background.jpg",
            "/music.mp3",
            "/cam-on-tu-phong.png",
            "/cam-on-tu-phong.mp3"
        ):
            self.send_static_file(path)
            return

        # -------------------------------------------------
        # NOT FOUND
        # -------------------------------------------------

        self.send_error(404, "File not found")

    # =====================================================
    # LOG
    # =====================================================

    def log_message(self, format, *args):
        print("[PHONG WEB V2.0.0]", format % args)


# =========================================================
# START SERVER
# =========================================================

if __name__ == "__main__":
    server = ThreadingHTTPServer(
        ("0.0.0.0", PORT),
        Website
    )

    print("====================================")
    print("       NGUYEN VAN PHONG WEBSITE")
    print("              V2.0.0")
    print("====================================")

    print("Server port:", PORT)

    print(
        "Link4M API:",
        "ENABLED" if LINK4M_API_TOKEN else "MISSING API TOKEN"
    )

    print("Layma API: REMOVED")
    print("YeuMoney API: REMOVED")

    print("Location route: /dinh-vi")
    print("Deta route: /menu")
    print("Proxy route: /proxy-mod-alen-crack")
    print("Mizze route: /mizze-crack")

    print("Providers: Link4M ONLY")
    print("Create endpoint: /create-short-link")
    print("Callback endpoint: /provider-return")
    print("Session check: /check-session")

    print("Location download: /download-location")
    print("Deta download: /download-deta")
    print("Proxy download: /download-proxy")
    print("Mizze download: /download-mizze")

    print("Thank-you page: ENABLED")
    print("Thank-you audio: /cam-on-tu-phong.mp3")
    print("Thank-you image: /cam-on-tu-phong.png")

    print("Background image: /background.jpg")
    print("Background music: /music.mp3")
    print("Music button: ENABLED")

    print("PHONG WEB VERSION: V2.0.0")
    print("====================================")

    try:
        server.serve_forever()

    except KeyboardInterrupt:
        print("\n[PHONG WEB] Server stopped.")

    finally:
        server.server_close()
