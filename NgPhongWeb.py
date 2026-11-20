
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
# PHONG WEB V33
# LINK4M + LAYMA
# LOCATION + DETA + PROXY + MIZZE
# MUSIC
# ==========================================

BASE_DIR = Path(__file__).resolve().parent
PORT = int(os.environ.get("PORT", 5000))

# LINK4M
LINK4M_API_TOKEN = os.environ.get(
    "LINK4M_API_TOKEN", ""
).strip()

LINK4M_ENDPOINT = "https://link4m.co/api-shorten/v2"

# LAYMA
LAYMA_API_TOKEN = os.environ.get(
    "LAYMA_API_TOKEN", ""
).strip()

LAYMA_ENDPOINT = (
    "https://api.layma.net/api/admin/shortlink/quicklink"
)

# WEBSITE
SITE_URL = os.environ.get(
    "SITE_URL",
    "https://nvp-com.onrender.com"
).strip().rstrip("/")


# ==========================================
# MEDIAFIRE LINKS
# ==========================================

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
    background: radial-gradient(
        circle at top,
        #253d91,
        #080d22 70%
    );
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
    background: linear-gradient(
        135deg,
        #1769e0,
        #7736c8
    );
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


/* MENU CARDS */

.menu-container {
    width: 100%;
    max-width: 700px;
    margin: 25px auto;
}

.menu-card {
    padding: 25px 15px;
    border-radius: 18px;
    background: linear-gradient(
        135deg,
        #252b65,
        #532b91
    );
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

.proxy-card {
    background: linear-gradient(
        135deg,
        #075b70,
        #263c91
    );
}

.proxy-card .open-menu-button {
    color: #075b70;
}

.mizze-card {
    background: linear-gradient(
        135deg,
        #8b267c,
        #402b91
    );
}

.mizze-card .open-menu-button {
    color: #742b9a;
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


/* PROVIDER SELECT */

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

.provider-note {
    margin-top: 9px;
    color: #aebfe9;
    font-size: 12px;
    line-height: 1.5;
}


/* CROSS BUTTON */

.cross-link-button {
    display: inline-block;
    padding: 15px 45px;
    border: none;
    border-radius: 30px;
    background: linear-gradient(
        135deg,
        #1685ff,
        #7139df
    );
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


/* RESULT */

.result-success {
    border: 1px solid rgba(0,230,150,0.4);
    box-shadow: 0 0 25px rgba(0,220,150,0.12);
}

.result-failed {
    border: 1px solid rgba(255,75,90,0.45);
    box-shadow: 0 0 25px rgba(255,50,70,0.12);
}

.result-success .link-icon {
    color: #00e69a;
}

.result-failed .link-icon {
    color: #ff5365;
}

.result-success .cross-link-button {
    background: linear-gradient(
        135deg,
        #00b879,
        #087dca
    );
}

.result-failed .cross-link-button {
    background: linear-gradient(
        135deg,
        #ff5365,
        #c52c65
    );
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
    background: linear-gradient(
        135deg,
        #1685ff,
        #7736d5
    );
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
    background: linear-gradient(
        135deg,
        #00c98b,
        #087dca
    );
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
}

</style>
</head>


<body>

<header>NGUYỄN VĂN PHONG WEBSITE</header>

<main>


<!-- HOME -->

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


    <!-- LOCATION -->

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


    <!-- DETA -->

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


    <!-- PROXY -->

    <section class="menu-container">

        <div class="menu-card proxy-card">

            <h2>🌐 PROXY MOD ALEN CRACK</h2>

            <button
                class="open-menu-button"
                id="openProxyButton"
                type="button"
            >
                MỞ MỤC
            </button>

        </div>

    </section>


    <!-- MIZZE -->

    <section class="menu-container">

        <div class="menu-card mizze-card">

            <h2>🎮 MENU MIZZE CRACK</h2>

            <button
                class="open-menu-button"
                id="openMizzeButton"
                type="button"
            >
                MỞ MỤC
            </button>

        </div>

    </section>

</div>


<!-- LOCATION PAGE -->

<div id="locationPage" class="link-page">

    <div class="link-icon">📍</div>

    <h2>BẠN CẦN VƯỢT LINK ĐỂ LẤY FILE MEDIAFIRE</h2>

    <div class="link-description">
        Chọn nhà cung cấp và nhấn nút bên dưới.
        <br>
        Sau khi hoàn thành, hệ thống sẽ kiểm tra phiên vượt link.
    </div>

    <div class="provider-box">

        <label for="locationProvider">
            CHỌN NHÀ CUNG CẤP API
        </label>

        <select class="provider-select" id="locationProvider">
            <option value="link4m">Link4M</option>
            <option value="layma">Layma</option>
        </select>

        <div class="provider-note">
            Chọn Link4M hoặc Layma để tạo link vượt.
        </div>

    </div>

    <button
        class="cross-link-button"
        id="locationCrossButton"
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


<!-- DETA PAGE -->

<div id="menuPage" class="link-page">

    <div class="link-icon">🔐</div>

    <h2>BẠN CẦN VƯỢT LINK ĐỂ LẤY FILE DETA</h2>

    <div class="link-description">
        Chọn nhà cung cấp và nhấn nút bên dưới.
        <br>
        Sau khi hoàn thành, bạn sẽ quay lại PHONG WEB.
        <br>
        Nhấn nút LẤY FILE để mở MediaFire.
    </div>

    <div class="provider-box">

        <label for="detaProvider">
            CHỌN NHÀ CUNG CẤP API
        </label>

        <select class="provider-select" id="detaProvider">
            <option value="link4m">Link4M</option>
            <option value="layma">Layma</option>
        </select>

        <div class="provider-note">
            Chọn Link4M hoặc Layma để tạo link vượt.
        </div>

    </div>

    <button
        class="cross-link-button"
        id="detaCrossButton"
        type="button"
    >
        🔓 VƯỢT LINK
    </button>

    <div class="status" id="detaStatus"></div>

    <br>

    <a class="back-button" href="/">
        ← QUAY LẠI TRANG CHỦ
    </a>

</div>


<!-- PROXY PAGE -->

<div id="proxyPage" class="link-page">

    <div class="link-icon">🌐</div>

    <h2>BẠN CẦN VƯỢT LINK ĐỂ LẤY FILE PROXY MOD ALEN CRACK</h2>

    <div class="link-description">
        Chọn nhà cung cấp và nhấn nút bên dưới.
        <br>
        Sau khi hoàn thành, bạn sẽ quay lại PHONG WEB.
        <br>
        Nhấn nút LẤY FILE để mở MediaFire.
    </div>

    <div class="provider-box">

        <label for="proxyProvider">
            CHỌN NHÀ CUNG CẤP API
        </label>

        <select class="provider-select" id="proxyProvider">
            <option value="link4m">Link4M</option>
            <option value="layma">Layma</option>
        </select>

        <div class="provider-note">
            Chọn Link4M hoặc Layma để tạo link vượt.
        </div>

    </div>

    <button
        class="cross-link-button"
        id="proxyCrossButton"
        type="button"
    >
        🔓 VƯỢT LINK
    </button>

    <div class="status" id="proxyStatus"></div>

    <br>

    <a class="back-button" href="/">
        ← QUAY LẠI TRANG CHỦ
    </a>

</div>


<!-- MIZZE PAGE -->

<div id="mizzePage" class="link-page">

    <div class="link-icon">🎮</div>

    <h2>BẠN CẦN VƯỢT LINK ĐỂ LẤY FILE MENU MIZZE CRACK</h2>

    <div class="link-description">
        Chọn nhà cung cấp và nhấn nút bên dưới.
        <br>
        Sau khi hoàn thành, bạn sẽ quay lại PHONG WEB.
        <br>
        Nhấn nút LẤY FILE để tải Menu Mizze Crack.
    </div>

    <div class="provider-box">

        <label for="mizzeProvider">
            CHỌN NHÀ CUNG CẤP API
        </label>

        <select class="provider-select" id="mizzeProvider">
            <option value="link4m">Link4M</option>
            <option value="layma">Layma</option>
        </select>

        <div class="provider-note">
            Chọn Link4M hoặc Layma để tạo link vượt.
        </div>

    </div>

    <button
        class="cross-link-button"
        id="mizzeCrossButton"
        type="button"
    >
        🔓 VƯỢT LINK
    </button>

    <div class="status" id="mizzeStatus"></div>

    <br>

    <a class="back-button" href="/">
        ← QUAY LẠI TRANG CHỦ
    </a>

</div>


<!-- RESULT PAGE -->

<div id="resultPage" class="link-page">

    <div class="link-icon" id="resultIcon">✅</div>

    <h2 id="resultTitle">Vượt Link</h2>

    <div
        class="link-description"
        id="resultDescription"
    ></div>

    <a
        class="cross-link-button"
        id="resultAction"
        href="/"
    >
        LẤY FILE
    </a>

    <div class="status" id="resultStatus"></div>

    <br>

    <a
        class="back-button"
        id="resultBack"
        href="/"
    >
        ← QUAY LẠI
    </a>

</div>


</main>


<!-- MUSIC -->

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
    PHONG WEB V33
</footer>


<script>

// ==========================================
// PAGE NAVIGATION
// ==========================================

const homePage = document.getElementById("homePage");
const locationPage = document.getElementById("locationPage");
const menuPage = document.getElementById("menuPage");
const proxyPage = document.getElementById("proxyPage");
const mizzePage = document.getElementById("mizzePage");
const resultPage = document.getElementById("resultPage");

const resultTitle = document.getElementById("resultTitle");
const resultDescription = document.getElementById("resultDescription");
const resultAction = document.getElementById("resultAction");
const resultStatus = document.getElementById("resultStatus");
const resultIcon = document.getElementById("resultIcon");
const resultBack = document.getElementById("resultBack");


const PAGE_PATHS = {
    location: "/dinh-vi",
    deta: "/menu",
    proxy: "/proxy-mod-alen-crack",
    mizze: "/mizze-crack"
};


const DOWNLOAD_PATHS = {
    location: "/download-location",
    deta: "/download-deta",
    proxy: "/download-proxy",
    mizze: "/download-mizze"
};


const DESTINATION_NAMES = {
    location: "Định Vị",
    deta: "Deta",
    proxy: "Proxy Mod Alen Crack",
    mizze: "Menu Mizze Crack"
};


function destinationPage(destination) {
    return PAGE_PATHS[destination] || "/";
}


function hideAllPages() {

    homePage.style.display = "none";
    locationPage.style.display = "none";
    menuPage.style.display = "none";
    proxyPage.style.display = "none";
    mizzePage.style.display = "none";
    resultPage.style.display = "none";
}


// ==========================================
// RESULT PAGE
// ==========================================

async function showResultPage() {

    const params = new URLSearchParams(
        window.location.search
    );

    const state = params.get("result");

    if (
        state !== "success" &&
        state !== "failed"
    ) {
        return false;
    }

    const destination = params.get("destination") || "";
    const token = params.get("token") || "";

    if (!PAGE_PATHS[destination]) {
        return false;
    }

    hideAllPages();

    resultPage.style.display = "block";

    resultBack.href = destinationPage(destination);

    resultPage.classList.remove(
        "result-success",
        "result-failed"
    );


    // LOCATION

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

        resultTitle.textContent =
            "Vượt Link Chưa Xác Nhận View!";

        resultDescription.textContent =
            sessionReturned
            ? "Bạn đã quay lại website, nhưng hệ thống chưa có API xác nhận View tăng. Vui lòng thử lại."
            : "Không xác nhận được phiên vượt link. Vui lòng thử lại.";

        resultAction.href = "/dinh-vi";

        resultAction.textContent = "↻ VƯỢT LẠI LINK";

        resultBack.href = "/";

        resultStatus.textContent = "";

        return true;
    }


    // FAILED

    if (state === "failed") {

        resultPage.classList.add("result-failed");

        resultIcon.textContent = "❌";

        resultTitle.textContent =
            "Vượt Link Chưa Thành Công";

        resultDescription.textContent =
            "Không xác nhận được phiên vượt link. Vui lòng thử lại.";

        resultAction.href = destinationPage(destination);

        resultAction.textContent = "↻ VƯỢT LẠI LINK";

        resultStatus.textContent = "";

        return true;
    }


    // SUCCESS

    resultStatus.textContent =
        "Đang xác nhận phiên vượt link...";

    try {

        if (!token) {
            throw new Error("Thiếu mã phiên.");
        }

        const response = await fetch(
            "/check-session?token=" +
            encodeURIComponent(token),
            { cache: "no-store" }
        );

        const data = await response.json();

        if (
            !response.ok ||
            !data.success ||
            data.returned !== true ||
            data.destination !== destination
        ) {
            throw new Error("Phiên không hợp lệ.");
        }

        resultPage.classList.add("result-success");

        resultIcon.textContent = "✅";

        resultTitle.textContent =
            "Vượt Link Thành Công!";

        resultDescription.textContent =
            "Bạn đã hoàn thành bước vượt link " +
            DESTINATION_NAMES[destination] +
            ". Nhấn nút bên dưới để lấy file.";

        resultAction.textContent =
            "⬇ LẤY FILE " +
            DESTINATION_NAMES[destination].toUpperCase();

        resultAction.href =
            DOWNLOAD_PATHS[destination] +
            "?token=" +
            encodeURIComponent(token);

        resultStatus.textContent = "";

    } catch (error) {

        resultPage.classList.add("result-failed");

        resultIcon.textContent = "❌";

        resultTitle.textContent =
            "Xác Nhận Thất Bại";

        resultDescription.textContent =
            "Phiên vượt link không hợp lệ hoặc đã hết hạn. Vui lòng thử lại.";

        resultAction.href =
            destinationPage(destination);

        resultAction.textContent =
            "↻ VƯỢT LẠI LINK";

        resultStatus.textContent = "";
    }

    return true;
}


// ==========================================
// SHOW PAGE
// ==========================================

async function showPage() {

    const path = window.location.pathname;

    hideAllPages();

    if (path === "/dinh-vi") {

        locationPage.style.display = "block";

    } else if (path === "/menu") {

        menuPage.style.display = "block";

    } else if (path === "/proxy-mod-alen-crack") {

        proxyPage.style.display = "block";

    } else if (path === "/mizze-crack") {

        mizzePage.style.display = "block";

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
.addEventListener("click", function(event) {

    event.preventDefault();

    navigate("/dinh-vi");
});


document.getElementById("openMenuButton")
.addEventListener("click", function() {
    navigate("/menu");
});


document.getElementById("openProxyButton")
.addEventListener("click", function() {
    navigate("/proxy-mod-alen-crack");
});


document.getElementById("openMizzeButton")
.addEventListener("click", function() {
    navigate("/mizze-crack");
});


showPage();


// ==========================================
// CREATE SHORT LINK
// LINK4M + LAYMA
// ==========================================

async function createShortLink(
    destination,
    provider,
    button,
    status
) {

    button.disabled = true;

    status.textContent =
        "Đang kết nối API " +
        provider.toUpperCase() +
        "...";

    try {

        const params = new URLSearchParams({
            provider: provider,
            destination: destination
        });

        const response = await fetch(
            "/create-short-link?" +
            params.toString(),
            {
                method: "GET",
                cache: "no-store"
            }
        );

        const data = await response.json();

        if (!response.ok || !data.success) {

            throw new Error(
                data.message || "Không thể tạo link."
            );
        }

        if (!data.url) {

            throw new Error(
                "API không trả về đường dẫn hợp lệ."
            );
        }

        status.textContent =
            "Đang chuyển đến " +
            provider.toUpperCase() +
            "...";

        window.location.href = data.url;

    } catch (error) {

        status.textContent =
            "Lỗi: " + error.message;

        button.disabled = false;
    }
}


// ==========================================
// BUTTON HELPER
// ==========================================

function setupCrossButton(
    destination,
    buttonId,
    providerId,
    statusId
) {

    const button = document.getElementById(buttonId);

    const provider = document.getElementById(providerId);

    const status = document.getElementById(statusId);

    button.addEventListener("click", function() {

        const selectedProvider = provider.value;

        createShortLink(
            destination,
            selectedProvider,
            button,
            status
        );
    });
}


// LOCATION

setupCrossButton(
    "location",
    "locationCrossButton",
    "locationProvider",
    "locationStatus"
);


// DETA

setupCrossButton(
    "deta",
    "detaCrossButton",
    "detaProvider",
    "detaStatus"
);


// PROXY

setupCrossButton(
    "proxy",
    "proxyCrossButton",
    "proxyProvider",
    "proxyStatus"
);


// MIZZE

setupCrossButton(
    "mizze",
    "mizzeCrossButton",
    "mizzeProvider",
    "mizzeStatus"
);


// ==========================================
// MUSIC CONTROL
// ==========================================

const audio = document.getElementById("audio");

const musicButton =
    document.getElementById("musicButton");

const musicIcon =
    document.getElementById("musicIcon");

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

    if (
        destination
        and session.get("destination") != destination
    ):
        return False

    return True


# ==========================================
# API REQUEST HELPERS
# ==========================================

def api_request(url, provider):

    headers = {
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
            "AppleWebKit/537.36 (KHTML, like Gecko) "
            "Chrome/131.0.0.0 Safari/537.36"
        ),
        "Accept": "application/json, text/plain, */*",
        "Cache-Control": "no-cache"
    }

    if provider == "layma":

        headers["Referer"] = "https://layma.net/"

    request = urllib.request.Request(
        url,
        headers=headers,
        method="GET"
    )

    try:

        with urllib.request.urlopen(
            request,
            timeout=30
        ) as response:

            body = response.read().decode(
                "utf-8",
                errors="replace"
            )

            return body

    except urllib.error.HTTPError as error:

        error_body = error.read().decode(
            "utf-8",
            errors="replace"
        )

        if provider == "layma":

            cf_ray = error.headers.get("CF-Ray", "")

            server = error.headers.get("Server", "")

            print(
                "[LAYMA HTTP ERROR]",
                error.code,
                "SERVER:",
                server,
                "CF-RAY:",
                cf_ray,
                "BODY:",
                error_body[:500]
            )

            if error.code == 403:

                raise ValueError(
                    "LAYMA HTTP 403: Máy chủ Layma/Cloudflare "
                    "đang từ chối kết nối từ Render. "
                    "API chưa trả về JSON. "
                    "Cần Layma kiểm tra quyền truy cập hoặc IP Render."
                )

        print(
            "[" + provider.upper() + " HTTP ERROR]",
            error.code,
            error_body[:400]
        )

        raise ValueError(
            provider.upper()
            + " HTTP "
            + str(error.code)
            + ": "
            + error_body[:250]
        )

    except urllib.error.URLError as error:

        raise ValueError(
            "Không thể kết nối "
            + provider.upper()
            + ": "
            + str(error.reason)
        )


def read_api_json(url, provider):

    body = api_request(url, provider)

    try:

        result = json.loads(body)

    except json.JSONDecodeError:

        print(
            "[" + provider.upper() + " INVALID JSON]",
            body[:500]
        )

        raise ValueError(
            provider.upper()
            + " không trả về JSON hợp lệ."
        )

    if not isinstance(result, dict):

        raise ValueError(
            provider.upper()
            + " trả về dữ liệu không đúng định dạng."
        )

    return result


# ==========================================
# LINK4M API
# ==========================================

def create_link4m_url(callback_url):

    if not LINK4M_API_TOKEN:

        raise ValueError(
            "Chưa cấu hình LINK4M_API_TOKEN trên Render."
        )

    params = urlencode({
        "api": LINK4M_API_TOKEN,
        "url": callback_url
    })

    api_url = (
        LINK4M_ENDPOINT
        + "?"
        + params
    )

    result = read_api_json(
        api_url,
        "link4m"
    )

    if result.get("status") != "success":

        raise ValueError(
            "Link4M: "
            + str(
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

    valid_url = validate_shortened_url(
        shortened_url
    )

    if not valid_url:

        raise ValueError(
            "Link4M không trả về URL HTTP/HTTPS hợp lệ."
        )

    return valid_url


# ==========================================
# LAYMA API
# ==========================================

def create_layma_url(callback_url):

    if not LAYMA_API_TOKEN:

        raise ValueError(
            "Chưa cấu hình LAYMA_API_TOKEN trên Render."
        )

    params = urlencode({
        "tokenUser": LAYMA_API_TOKEN,
        "format": "json",
        "url": callback_url
    })

    api_url = (
        LAYMA_ENDPOINT
        + "?"
        + params
    )

    result = read_api_json(
        api_url,
        "layma"
    )

    if result.get("success") is not True:

        raise ValueError(
            "Layma không tạo được link. "
            "Kiểm tra API Token và URL."
        )

    shortened_url = result.get("html")

    valid_url = validate_shortened_url(
        shortened_url
    )

    if not valid_url:

        raise ValueError(
            "Layma trả về URL không hợp lệ hoặc bị trống."
        )

    return valid_url


# ==========================================
# PROVIDER DISPATCH
# ==========================================

def create_provider_url(provider, callback_url):

    if provider == "link4m":

        return create_link4m_url(callback_url)

    if provider == "layma":

        return create_layma_url(callback_url)

    raise ValueError(
        "Nhà cung cấp API không hợp lệ."
    )


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

        self.send_header(
            "Cache-Control",
            "no-store"
        )

        self.end_headers()

        try:

            self.wfile.write(content)

        except (
            BrokenPipeError,
            ConnectionResetError
        ):

            pass


    def send_html_page(self, status=200):

        content = HTML.encode("utf-8")

        self.send_response(status)

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

        try:

            self.wfile.write(content)

        except (
            BrokenPipeError,
            ConnectionResetError
        ):

            pass


    def redirect(self, location):

        self.send_response(302)

        self.send_header(
            "Location",
            location
        )

        self.send_header(
            "Cache-Control",
            "no-store"
        )

        self.end_headers()


    # ======================================
    # MAIN ROUTES
    # ======================================

    def do_GET(self):

        parsed_request = urlsplit(self.path)

        path = unquote(parsed_request.path)

        query = parse_qs(
            parsed_request.query
        )


        # HOME AND PAGES

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


        # ======================================
        # CREATE SHORT LINK
        # LINK4M + LAYMA
        # ======================================

        if path == "/create-short-link":

            provider = query.get(
                "provider",
                ["link4m"]
            )[0].lower()

            destination = query.get(
                "destination",
                [""]
            )[0].lower()


            if provider not in (
                "link4m",
                "layma"
            ):

                self.send_json(
                    400,
                    {
                        "success": False,
                        "message": "Nhà cung cấp API không hợp lệ."
                    }
                )

                return


            if destination not in DESTINATIONS:

                self.send_json(
                    400,
                    {
                        "success": False,
                        "message": "Mục đích vượt link không hợp lệ."
                    }
                )

                return


            if not SITE_URL.startswith("https://"):

                self.send_json(
                    500,
                    {
                        "success": False,
                        "message": "SITE_URL phải là địa chỉ HTTPS."
                    }
                )

                return


            if provider == "link4m" and not LINK4M_API_TOKEN:

                self.send_json(
                    500,
                    {
                        "success": False,
                        "message": "Chưa cấu hình LINK4M_API_TOKEN trên Render."
                    }
                )

                return


            if provider == "layma" and not LAYMA_API_TOKEN:

                self.send_json(
                    500,
                    {
                        "success": False,
                        "message": "Chưa cấu hình LAYMA_API_TOKEN trên Render."
                    }
                )

                return


            token = secrets.token_urlsafe(32)

            callback_url = (
                SITE_URL
                + "/provider-return?token="
                + quote(token, safe="")
            )


            try:

                shortened_url = create_provider_url(
                    provider,
                    callback_url
                )


                cleanup_sessions()

                with SESSIONS_LOCK:

                    SESSIONS[token] = {
                        "created": time.time(),
                        "returned": False,
                        "provider": provider,
                        "destination": destination,
                        "view_confirmed": False
                    }


                self.send_json(
                    200,
                    {
                        "success": True,
                        "url": shortened_url,
                        "provider": provider,
                        "destination": destination
                    }
                )


                print(
                    "[PHONG WEB V33] CREATED:",
                    provider,
                    destination
                )


            except urllib.error.URLError as error:

                print(
                    "[PHONG WEB V33] CONNECTION ERROR:",
                    provider,
                    str(error.reason)
                )

                self.send_json(
                    502,
                    {
                        "success": False,
                        "message": (
                            "Không thể kết nối API "
                            + provider.upper()
                            + "."
                        )
                    }
                )


            except TimeoutError:

                self.send_json(
                    504,
                    {
                        "success": False,
                        "message": (
                            provider.upper()
                            + " phản hồi quá lâu. Vui lòng thử lại."
                        )
                    }
                )


            except ValueError as error:

                print(
                    "[PHONG WEB V33] API ERROR:",
                    provider,
                    str(error)
                )

                self.send_json(
                    502,
                    {
                        "success": False,
                        "message": str(error)
                    }
                )


            except Exception as error:

                print(
                    "[PHONG WEB V33] CREATE ERROR:",
                    provider,
                    type(error).__name__,
                    str(error)[:300]
                )

                self.send_json(
                    500,
                    {
                        "success": False,
                        "message": (
                            "Lỗi xử lý API: "
                            + type(error).__name__
                        )
                    }
                )

            return


        # ======================================
        # PROVIDER CALLBACK
        # ======================================

        if path == "/provider-return":

            token = query.get(
                "token",
                [""]
            )[0]

            cleanup_sessions()

            destination = None
            provider = None
            valid = False


            with SESSIONS_LOCK:

                session = SESSIONS.get(token)

                if session:

                    session["returned"] = True

                    destination = session.get(
                        "destination"
                    )

                    provider = session.get(
                        "provider"
                    )

                    valid = True


            if not valid:

                print(
                    "[PHONG WEB V33] INVALID CALLBACK"
                )

                self.redirect(
                    "/?result=failed&destination=deta"
                )

                return


            print(
                "[PHONG WEB V33] CALLBACK:",
                provider,
                destination
            )


            # LOCATION: CHƯA CÓ API XÁC NHẬN VIEW

            if destination == "location":

                self.redirect(
                    "/?result=failed"
                    "&destination=location"
                    "&token="
                    + quote(token, safe="")
                )

                return


            # DETA / PROXY / MIZZE

            self.redirect(
                "/?result=success"
                "&destination="
                + quote(destination, safe="")
                + "&token="
                + quote(token, safe="")
            )

            return


        # ======================================
        # CHECK SESSION
        # ======================================

        if path == "/check-session":

            token = query.get(
                "token",
                [""]
            )[0]

            session = get_session(token)


            if session and session.get("returned"):

                self.send_json(
                    200,
                    {
                        "success": True,
                        "returned": True,
                        "view_confirmed": bool(
                            session.get(
                                "view_confirmed",
                                False
                            )
                        ),
                        "destination": session.get(
                            "destination"
                        ),
                        "provider": session.get(
                            "provider"
                        ),
                        "message": "Đã nhận callback từ nhà cung cấp."
                    }
                )

            else:

                self.send_json(
                    403,
                    {
                        "success": False,
                        "returned": False,
                        "view_confirmed": False,
                        "message": "Phiên vượt link không hợp lệ hoặc đã hết hạn."
                    }
                )

            return


        # ======================================
        # DOWNLOAD ROUTES
        # ======================================

        download_routes = {
            "/download-location": "location",
            "/download-deta": "deta",
            "/download-proxy": "proxy",
            "/download-mizze": "mizze"
        }


        if path in download_routes:

            destination = download_routes[path]

            token = query.get(
                "token",
                [""]
            )[0]


            # LOCATION: REQUIRE VIEW CONFIRMATION

            if destination == "location":

                session = get_session(token)

                if (
                    not session
                    or not session.get("returned")
                    or session.get("destination") != "location"
                    or not session.get("view_confirmed", False)
                ):

                    self.send_json(
                        403,
                        {
                            "success": False,
                            "message": (
                                "Chưa có xác nhận View thành công "
                                "từ nhà cung cấp."
                            )
                        }
                    )

                    return


            elif not check_session(
                token,
                destination
            ):

                self.send_json(
                    403,
                    {
                        "success": False,
                        "message": (
                            "Bạn chưa hoàn thành bước vượt link "
                            + DESTINATION_NAMES[destination]
                            + "."
                        )
                    }
                )

                return


            self.redirect(
                DESTINATIONS[destination]
            )

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

            token = query.get(
                "token",
                [""]
            )[0]

            self.redirect(
                "/provider-return?token="
                + quote(token, safe="")
            )

            return


        if path == "/check-link4m":

            token = query.get(
                "token",
                [""]
            )[0]

            if check_session(token, "deta"):

                self.send_json(
                    200,
                    {
                        "success": True,
                        "message": "Đã xác nhận phiên."
                    }
                )

            else:

                self.send_json(
                    403,
                    {
                        "success": False,
                        "message": "Phiên không hợp lệ."
                    }
                )

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

            self.send_error(
                404,
                "File not found"
            )

            return


        file_path = (
            BASE_DIR / path.lstrip("/")
        )


        if not file_path.is_file():

            self.send_error(
                404,
                "Asset not found"
            )

            return


        content_type = (
            mimetypes.guess_type(
                str(file_path)
            )[0]
            or "application/octet-stream"
        )


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


        except (
            BrokenPipeError,
            ConnectionResetError
        ):

            pass


        except OSError as error:

            print(
                "[PHONG WEB V33] FILE ERROR:",
                str(error)
            )


    def log_message(self, format, *args):

        print(
            "[PHONG WEB V33]",
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
    print("          PHONG WEB V33")
    print("====================================")

    print(
        "Server port:",
        PORT
    )

    print(
        "Link4M API:",
        "ENABLED" if LINK4M_API_TOKEN else "MISSING API TOKEN"
    )

    print(
        "Layma API:",
        "ENABLED" if LAYMA_API_TOKEN else "MISSING API TOKEN"
    )

    print("YeuMoney API: REMOVED")

    print("Location route: /dinh-vi")
    print("Deta route: /menu")
    print("Proxy route: /proxy-mod-alen-crack")
    print("Mizze route: /mizze-crack")

    print("Providers: Link4M + Layma")

    print("Create endpoint: /create-short-link")
    print("Callback endpoint: /provider-return")
    print("Session check: /check-session")

    print("Location download: /download-location")
    print("Deta download: /download-deta")
    print("Proxy download: /download-proxy")
    print("Mizze download: /download-mizze")

    print("Music button: ENABLED")
    print("Music looping: ENABLED")

    print("PHONG WEB VERSION: V33")

    print("====================================")


    try:

        server.serve_forever()

    except KeyboardInterrupt:

        print(
            "\n[PHONG WEB] Server stopped."
        )

    finally:

        server.server_close()
