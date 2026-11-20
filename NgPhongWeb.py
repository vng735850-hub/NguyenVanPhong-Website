
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

# =========================================================
# PHONG WEB V1.0.0
# LINK4M ONLY
# LOCATION + DETA + PROXY + MIZZE + MUSIC
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
PORT = int(os.environ.get("PORT", 5000))

# =========================================================
# LINK4M API
# =========================================================

LINK4M_API_TOKEN = os.environ.get(
    "LINK4M_API_TOKEN", ""
).strip()

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

* {
    box-sizing: border-box;
}

html {
    scroll-behavior: smooth;
}

body {
    margin: 0;
    min-height: 100vh;
    font-family: Arial, Helvetica, sans-serif;
    color: #ffffff;

    background:
        linear-gradient(
            rgba(3, 7, 25, 0.82),
            rgba(3, 7, 25, 0.88)
        ),
        url('/background.jpg') center center / cover fixed no-repeat;

    background-color: #080d20;
}

/* =====================================================
   HEADER
===================================================== */

header {
    position: relative;
    z-index: 1000;

    width: 100%;
    min-height: 75px;

    display: flex;
    align-items: center;
    justify-content: center;
    gap: 13px;

    padding: 12px 15px;

    background: rgba(4, 10, 30, 0.88);

    border-bottom: 1px solid rgba(65, 165, 255, 0.5);

    box-shadow: 0 4px 20px rgba(0, 0, 0, 0.3);
}

.hamburger-button {
    width: 43px;
    height: 43px;

    flex-shrink: 0;

    display: flex;
    align-items: center;
    justify-content: center;

    border: 1px solid #55baff;
    border-radius: 10px;

    background: rgba(0, 120, 255, 0.2);

    color: #ffffff;
    font-size: 25px;

    cursor: pointer;
}

.hamburger-button:hover {
    background: #087ce5;
}

.header-title {
    font-size: clamp(15px, 3vw, 24px);
    font-weight: 900;

    text-align: center;
    letter-spacing: 1px;

    color: #ffffff;

    text-shadow:
        0 0 8px #168cff,
        0 0 15px #168cff;
}

/* =====================================================
   HAMBURGER MENU
===================================================== */

.side-menu {
    display: none;

    position: absolute;
    top: 67px;
    left: 12px;

    width: 200px;

    padding: 9px;

    background: rgba(5, 14, 38, 0.98);

    border: 1px solid #299cff;
    border-radius: 12px;

    box-shadow: 0 8px 25px rgba(0, 0, 0, 0.5);
}

.side-menu.show {
    display: block;
}

.side-menu a {
    display: block;

    padding: 13px;

    color: #ffffff;
    text-decoration: none;
    font-weight: bold;

    border-radius: 8px;
}

.side-menu a:hover {
    background: #087ce5;
}

/* =====================================================
   MAIN CONTAINER
===================================================== */

.container {
    width: min(900px, 92%);
    margin: 25px auto;
    text-align: center;
}

.hero-logo {
    display: block;

    width: 125px;
    height: 125px;

    object-fit: contain;

    margin: 20px auto;

    border-radius: 50%;

    filter: drop-shadow(0 0 15px #168cff);
}

h1 {
    font-size: clamp(23px, 5vw, 34px);
    font-weight: 900;

    color: #ffffff;

    text-shadow: 0 0 15px #168cff;
}

.subtitle {
    color: #d2e7ff;
    font-size: 14px;
    line-height: 1.8;

    margin: 15px auto 25px;
}

/* =====================================================
   LOCATION CARD
===================================================== */

.location-container {
    margin: 20px auto;
}

.location-link {
    display: block;

    color: inherit;
    text-decoration: none;
}

.location-card {
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 20px;

    padding: 22px 15px;

    background: rgba(10, 27, 60, 0.88);

    border: 1px solid #459fff;
    border-radius: 15px;

    box-shadow: 0 0 18px rgba(0, 130, 255, 0.18);

    transition: 0.2s;
}

.location-card:hover {
    transform: translateY(-3px);

    border-color: #8bd4ff;

    box-shadow: 0 0 25px rgba(0, 140, 255, 0.4);
}

.location-emoji {
    font-size: 43px;
}

.location-info {
    text-align: left;
}

.location-info h2 {
    margin: 0 0 9px;
    font-size: 19px;
}

.location-info p {
    margin: 0 0 12px;

    color: #c6e1ff;
    font-size: 13px;
}

.location-button {
    display: inline-block;

    padding: 9px 17px;

    background: linear-gradient(120deg, #0877e8, #12a8ff);

    color: #ffffff;
    font-weight: bold;
    font-size: 12px;

    border-radius: 8px;
}

/* =====================================================
   MENU CARDS
===================================================== */

.menu-container {
    margin: 18px auto;
}

.menu-card {
    padding: 23px 15px;

    background: rgba(9, 24, 55, 0.9);

    border: 1px solid rgba(64, 157, 255, 0.65);
    border-radius: 15px;

    box-shadow: 0 0 17px rgba(0, 110, 255, 0.15);

    transition: 0.2s;
}

.menu-card:hover {
    transform: translateY(-3px);

    border-color: #8bd4ff;

    box-shadow: 0 0 22px rgba(0, 140, 255, 0.3);
}

.menu-card h2 {
    margin: 0 0 17px;
    font-size: 18px;
}

.open-menu-button {
    padding: 12px 25px;

    color: white;
    font-weight: bold;
    font-size: 13px;

    background: linear-gradient(120deg, #0877e8, #12a8ff);

    border: none;
    border-radius: 9px;

    cursor: pointer;
}

.open-menu-button:hover {
    filter: brightness(1.2);
}

/* =====================================================
   SUB PAGES
===================================================== */

.page {
    display: none;
}

.page.active {
    display: block;
}

.link-box {
    max-width: 570px;

    margin: 35px auto;
    padding: 28px 20px;

    background: rgba(7, 21, 49, 0.94);

    border: 1px solid #399cff;
    border-radius: 17px;

    box-shadow: 0 0 25px rgba(0, 110, 255, 0.2);
}

.link-icon {
    font-size: 48px;
    margin-bottom: 12px;
}

.link-box h2 {
    color: #8acaff;
    font-size: 20px;
    line-height: 1.5;
}

.link-description {
    color: #d1e5ff;
    font-size: 14px;
    line-height: 1.8;

    margin: 15px auto 22px;
}

/* =====================================================
   BUTTONS
===================================================== */

.cross-link-button {
    display: inline-block;

    padding: 14px 25px;

    color: #ffffff;
    font-size: 14px;
    font-weight: bold;

    text-decoration: none;

    background: linear-gradient(120deg, #0877e8, #12a8ff);

    border: none;
    border-radius: 10px;

    cursor: pointer;

    box-shadow: 0 4px 15px rgba(0, 120, 255, 0.3);

    transition: 0.2s;
}

.cross-link-button:hover {
    filter: brightness(1.2);
    transform: translateY(-2px);
}

.cross-link-button:disabled {
    opacity: 0.6;
    cursor: wait;
    transform: none;
}

.back-button {
    display: inline-block;

    padding: 11px 18px;

    color: #ffffff;
    font-size: 13px;
    font-weight: bold;

    text-decoration: none;

    background: rgba(20, 65, 120, 0.8);

    border: 1px solid #4caeff;
    border-radius: 9px;
}

.back-button:hover {
    background: #126fc4;
}

.status {
    min-height: 24px;

    margin: 17px auto;

    color: #ffe18b;
    font-size: 13px;
    line-height: 1.7;

    overflow-wrap: anywhere;
}

.status.error {
    color: #ff7777;
}

.status.success {
    color: #5dffac;
    font-weight: bold;
}

/* =====================================================
   RESULT PAGE
===================================================== */

.result-action {
    display: inline-block;

    margin: 12px auto;

    padding: 14px 30px;

    color: #ffffff;
    font-weight: bold;
    font-size: 15px;

    text-decoration: none;

    background: linear-gradient(120deg, #08a75d, #16d68b);

    border-radius: 10px;

    box-shadow: 0 0 18px rgba(0, 220, 130, 0.3);
}

.result-action:hover {
    filter: brightness(1.15);
}

.hidden {
    display: none !important;
}

/* =====================================================
   MUSIC BUTTON
===================================================== */

.music-mini {
    position: relative;

    display: flex;
    align-items: center;
    justify-content: center;

    margin: 25px auto 15px;
}

.music-mini button {
    width: 53px;
    height: 53px;

    display: flex;
    align-items: center;
    justify-content: center;

    border: 2px solid #75caff;
    border-radius: 50%;

    color: #ffffff;
    background: linear-gradient(135deg, #086de0, #13b5ff);

    font-size: 21px;

    cursor: pointer;

    box-shadow: 0 0 18px rgba(0, 145, 255, 0.55);
}

.music-mini button.playing {
    animation: musicPulse 1.4s infinite;
}

@keyframes musicPulse {
    0%, 100% {
        box-shadow: 0 0 10px #159dff;
    }

    50% {
        box-shadow: 0 0 28px #36caff;
    }
}

/* =====================================================
   FOOTER
===================================================== */

footer {
    width: 100%;

    padding: 18px 10px 22px;

    text-align: center;

    color: #c1dcff;
    font-size: 13px;
    line-height: 1.9;

    background: rgba(3, 8, 23, 0.9);

    border-top: 1px solid rgba(80, 170, 255, 0.3);
}

footer strong {
    color: #55baff;
    letter-spacing: 1px;
}

/* =====================================================
   MOBILE
===================================================== */

@media (max-width: 600px) {

    header {
        justify-content: flex-start;
    }

    .header-title {
        flex: 1;
        font-size: 15px;
        text-align: center;
    }

    .location-card {
        gap: 12px;
    }

    .location-info h2 {
        font-size: 16px;
    }

    .link-box {
        margin: 22px auto;
        padding: 23px 15px;
    }
}

</style>
</head>

<body>

<!-- =====================================================
     HEADER
===================================================== -->

<header>

    <button
        class="hamburger-button"
        id="hamburgerButton"
        type="button"
        aria-label="Mở menu"
    >☰</button>

    <div class="header-title">
        NGUYỄN VĂN PHONG WEBSITE
    </div>

    <nav class="side-menu" id="sideMenu">

        <a href="/" id="homeMenuButton">
            🏠 TRANG CHỦ
        </a>

    </nav>

</header>


<!-- =====================================================
     MAIN CONTAINER
===================================================== -->

<main class="container">


<!-- =====================================================
     HOME PAGE
===================================================== -->

<section class="page" id="homePage">

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

</section>


<!-- =====================================================
     LOCATION PAGE
===================================================== -->

<section class="page" id="locationPage">

    <div class="link-box">

        <div class="link-icon">📍</div>

        <h2>
            BẠN CẦN VƯỢT LINK ĐỂ LẤY FILE MEDIAFIRE
        </h2>

        <div class="link-description">
            Nhấn nút bên dưới để tạo liên kết vượt.
            <br>
            Sau khi hoàn thành, hệ thống sẽ kiểm tra phiên.
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

</section>


<!-- =====================================================
     DETA PAGE
===================================================== -->

<section class="page" id="detaPage">

    <div class="link-box">

        <div class="link-icon">🔐</div>

        <h2>
            BẠN CẦN VƯỢT LINK ĐỂ LẤY FILE DETA
        </h2>

        <div class="link-description">
            Nhấn nút bên dưới để tạo liên kết vượt.
            <br>
            Sau khi hoàn thành, bạn sẽ quay lại PHONG WEB.
            <br>
            Nhấn nút LẤY FILE để mở MediaFire.
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

</section>


<!-- =====================================================
     PROXY PAGE
===================================================== -->

<section class="page" id="proxyPage">

    <div class="link-box">

        <div class="link-icon">🌐</div>

        <h2>
            BẠN CẦN VƯỢT LINK ĐỂ LẤY FILE PROXY MOD ALEN CRACK
        </h2>

        <div class="link-description">
            Nhấn nút bên dưới để tạo liên kết vượt.
            <br>
            Sau khi hoàn thành, bạn sẽ quay lại PHONG WEB.
            <br>
            Nhấn nút LẤY FILE để mở MediaFire.
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

</section>


<!-- =====================================================
     MIZZE PAGE
===================================================== -->

<section class="page" id="mizzePage">

    <div class="link-box">

        <div class="link-icon">🎮</div>

        <h2>
            BẠN CẦN VƯỢT LINK ĐỂ LẤY FILE MENU MIZZE CRACK
        </h2>

        <div class="link-description">
            Nhấn nút bên dưới để tạo liên kết vượt.
            <br>
            Sau khi hoàn thành, bạn sẽ quay lại PHONG WEB.
            <br>
            Nhấn nút LẤY FILE để tải Menu Mizze Crack.
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

</section>


<!-- =====================================================
     RESULT PAGE
===================================================== -->

<section class="page" id="resultPage">

    <div class="link-box">

        <div class="link-icon" id="resultIcon">✅</div>

        <h2 id="resultTitle">Vượt Link</h2>

        <div
            class="link-description"
            id="resultDescription"
        ></div>

        <a
            class="result-action hidden"
            id="resultAction"
            href="/"
            target="_blank"
            rel="noopener noreferrer"
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

</section>


</main>


<!-- =====================================================
     MUSIC BUTTON - ABOVE FOOTER
===================================================== -->

<div class="music-mini">

    <button
        id="musicButton"
        aria-label="Bật hoặc tắt nhạc"
        title="Bật / Tắt nhạc"
        type="button"
    >
        <span id="musicIcon">▶</span>
    </button>

</div>

<audio id="backgroundMusic" src="/music.mp3" loop></audio>


<!-- =====================================================
     FOOTER
===================================================== -->

<footer>

    © 2026 Nguyễn Văn Phong Website

    <br>

    <strong>PHONG WEB V1.0.0</strong>

</footer>


<!-- =====================================================
     JAVASCRIPT
===================================================== -->

<script>

/* =====================================================
   ELEMENTS
===================================================== */

const homePage = document.getElementById("homePage");
const locationPage = document.getElementById("locationPage");
const detaPage = document.getElementById("detaPage");
const proxyPage = document.getElementById("proxyPage");
const mizzePage = document.getElementById("mizzePage");
const resultPage = document.getElementById("resultPage");

const hamburgerButton = document.getElementById("hamburgerButton");
const sideMenu = document.getElementById("sideMenu");
const homeMenuButton = document.getElementById("homeMenuButton");

const musicButton = document.getElementById("musicButton");
const musicIcon = document.getElementById("musicIcon");
const backgroundMusic = document.getElementById("backgroundMusic");


/* =====================================================
   PAGE ROUTES
===================================================== */

const pageRoutes = {
    "/": homePage,
    "/index.html": homePage,

    "/dinh-vi": locationPage,
    "/menu": detaPage,

    "/proxy-mod-alen-crack": proxyPage,
    "/mizze-crack": mizzePage
};

function hideAllPages() {

    document.querySelectorAll(".page").forEach(page => {
        page.classList.remove("active");
    });

}

function showPage() {

    hideAllPages();

    const path = window.location.pathname;

    if (path === "/") {

        homePage.classList.add("active");

        return;
    }

    if (path === "/complete") {

        resultPage.classList.add("active");

        checkResult();

        return;
    }

    const page = pageRoutes[path];

    if (page) {

        page.classList.add("active");

        return;
    }

    homePage.classList.add("active");

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
    "click",
    function() {
        navigate("/menu");
    }
);

document.getElementById("openProxyButton").addEventListener(
    "click",
    function() {
        navigate("/proxy-mod-alen-crack");
    }
);

document.getElementById("openMizzeButton").addEventListener(
    "click",
    function() {
        navigate("/mizze-crack");
    }
);


/* =====================================================
   CREATE SHORT LINK - LINK4M ONLY
===================================================== */

async function createShortLink(destination, button, status) {

    button.disabled = true;
    button.textContent = "ĐANG XỬ LÝ...";

    status.className = "status";
    status.textContent = "Đang kết nối API LINK4M...";

    try {

        const response = await fetch(
            "/create-short-link?destination=" +
            encodeURIComponent(destination)
        );

        let data;

        try {

            data = await response.json();

        } catch (error) {

            throw new Error("Máy chủ trả về dữ liệu không hợp lệ.");

        }

        if (!response.ok || !data.success) {

            throw new Error(
                data.message || "Không thể tạo link vượt."
            );

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


/* =====================================================
   BUTTON CONFIGURATION
===================================================== */

function setupCrossButton(
    destination,
    buttonId,
    statusId
) {

    const button = document.getElementById(buttonId);
    const status = document.getElementById(statusId);

    button.addEventListener("click", function() {

        createShortLink(
            destination,
            button,
            status
        );

    });

}

setupCrossButton(
    "location",
    "locationCrossButton",
    "locationStatus"
);

setupCrossButton(
    "deta",
    "detaCrossButton",
    "detaStatus"
);

setupCrossButton(
    "proxy",
    "proxyCrossButton",
    "proxyStatus"
);

setupCrossButton(
    "mizze",
    "mizzeCrossButton",
    "mizzeStatus"
);


/* =====================================================
   RESULT PAGE
===================================================== */

async function checkResult() {

    const params = new URLSearchParams(window.location.search);

    const result = params.get("result");
    const destination = params.get("destination");
    const token = params.get("token");

    const resultIcon = document.getElementById("resultIcon");
    const resultTitle = document.getElementById("resultTitle");

    const resultDescription = document.getElementById(
        "resultDescription"
    );

    const resultAction = document.getElementById("resultAction");
    const resultStatus = document.getElementById("resultStatus");

    resultAction.classList.add("hidden");

    resultStatus.className = "status";
    resultStatus.textContent = "";

    if (result === "failed") {

        resultIcon.textContent = "❌";
        resultTitle.textContent = "CHƯA HOÀN THÀNH";

        if (destination === "location") {

            resultDescription.textContent =
                "Hệ thống chưa nhận được xác nhận View thành công. " +
                "Mục Định Vị hiện chưa có API xác nhận View.";

        } else {

            resultDescription.textContent =
                "Phiên vượt link không hợp lệ hoặc chưa hoàn thành.";

        }

        resultStatus.className = "status error";

        resultStatus.textContent =
            "Vui lòng quay lại và thử lại.";

        return;

    }

    if (result !== "success" || !token || !destination) {

        resultIcon.textContent = "❌";
        resultTitle.textContent = "KHÔNG TÌM THẤY PHIÊN";

        resultDescription.textContent =
            "Không tìm thấy thông tin phiên vượt link.";

        resultStatus.className = "status error";

        return;

    }

    resultIcon.textContent = "⏳";
    resultTitle.textContent = "ĐANG KIỂM TRA";

    resultDescription.textContent =
        "Đang xác nhận phiên vượt link của bạn...";

    try {

        const response = await fetch(
            "/check-session?token=" +
            encodeURIComponent(token)
        );

        const data = await response.json();

        if (!response.ok || !data.success || !data.returned) {

            throw new Error(
                data.message || "Không thể xác nhận phiên."
            );

        }

        if (data.destination !== destination) {

            throw new Error("Thông tin mục vượt link không khớp.");

        }

        if (destination === "location") {

            resultIcon.textContent = "❌";
            resultTitle.textContent = "CHƯA XÁC NHẬN VIEW";

            resultDescription.textContent =
                "Nhà cung cấp đã chuyển hướng về website, " +
                "nhưng chưa có xác nhận View thành công.";

            resultStatus.className = "status error";

            resultStatus.textContent =
                "Mục Định Vị cần API xác nhận View riêng.";

            return;

        }

        resultIcon.textContent = "✅";
        resultTitle.textContent = "VƯỢT LINK THÀNH CÔNG";

        resultDescription.textContent =
            "Bạn đã quay lại PHONG WEB thành công. " +
            "Nhấn LẤY FILE để mở MediaFire.";

        resultStatus.className = "status success";

        resultStatus.textContent =
            "Đã xác nhận phiên " + data.destination + ".";

        const downloadRoutes = {
            "deta": "/download-deta",
            "proxy": "/download-proxy",
            "mizze": "/download-mizze"
        };

        const downloadPath = downloadRoutes[destination];

        if (!downloadPath) {

            throw new Error("Không tìm thấy đường dẫn tải file.");

        }

        resultAction.href =
            downloadPath + "?token=" + encodeURIComponent(token);

        resultAction.classList.remove("hidden");

    } catch (error) {

        resultIcon.textContent = "❌";
        resultTitle.textContent = "XÁC NHẬN THẤT BẠI";

        resultDescription.textContent =
            "Không thể xác nhận trạng thái vượt link.";

        resultStatus.className = "status error";

        resultStatus.textContent = error.message;

    }

}


/* =====================================================
   HAMBURGER MENU
===================================================== */

hamburgerButton.addEventListener("click", function(event) {

    event.stopPropagation();

    sideMenu.classList.toggle("show");

});

homeMenuButton.addEventListener("click", function(event) {

    event.preventDefault();

    sideMenu.classList.remove("show");

    navigate("/");

});

document.addEventListener("click", function(event) {

    if (
        !sideMenu.contains(event.target) &&
        !hamburgerButton.contains(event.target)
    ) {

        sideMenu.classList.remove("show");

    }

});


/* =====================================================
   MUSIC BUTTON
===================================================== */

musicButton.addEventListener("click", async function() {

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

        musicIcon.textContent = "▶";

        alert(
            "Không thể phát nhạc. " +
            "Vui lòng kiểm tra file music.mp3."
        );

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

        print(
            "[LINK4M HTTP ERROR]",
            error.code,
            error_body[:400]
        )

        raise ValueError(
            "Link4M HTTP "
            + str(error.code)
            + ": "
            + error_body[:250]
        )

    except urllib.error.URLError as error:

        raise ValueError(
            "Không thể kết nối Link4M: "
            + str(error.reason)
        )


def read_api_json(url):

    body = api_request(url)

    try:

        result = json.loads(body)

    except json.JSONDecodeError:

        print(
            "[LINK4M INVALID JSON]",
            body[:500]
        )

        raise ValueError(
            "Link4M không trả về JSON hợp lệ."
        )

    if not isinstance(result, dict):

        raise ValueError(
            "Link4M trả về dữ liệu không đúng định dạng."
        )

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

    api_url = (
        LINK4M_ENDPOINT
        + "?"
        + params
    )

    result = read_api_json(api_url)

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

    server_version = "PhongWeb/1.0.0"

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

    # -----------------------------------------------------
    # REDIRECT
    # -----------------------------------------------------

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

    # -----------------------------------------------------
    # STATIC FILES
    # -----------------------------------------------------

    def send_static_file(self, path):

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

        file_path = BASE_DIR / path.lstrip("/")

        if not file_path.is_file():

            self.send_error(
                404,
                "Asset not found"
            )

            return

        content_type = (
            mimetypes.guess_type(str(file_path))[0]
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
                "Cache-Control",
                "public, max-age=3600"
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
                "[PHONG WEB] FILE ERROR:",
                str(error)
            )

    # =====================================================
    # MAIN ROUTES
    # =====================================================

    def do_GET(self):

        parsed_request = urlsplit(self.path)

        path = unquote(parsed_request.path)

        query = parse_qs(
            parsed_request.query
        )

        # -------------------------------------------------
        # HOME AND PAGES
        # -------------------------------------------------

        if path in (
            "/",
            "/index.html",
            "/dinh-vi",
            "/menu",
            "/proxy-mod-alen-crack",
            "/mizze-crack",
            "/complete"
        ):

            self.send_html_page()

            return

        # -------------------------------------------------
        # CREATE SHORT LINK - LINK4M ONLY
        # -------------------------------------------------

        if path == "/create-short-link":

            provider = query.get(
                "provider",
                ["link4m"]
            )[0].lower()

            destination = query.get(
                "destination",
                [""]
            )[0].lower()

            if provider != "link4m":

                self.send_json(
                    400,
                    {
                        "success": False,
                        "message": (
                            "PHONG WEB V1.0.0 chỉ hỗ trợ Link4M."
                        )
                    }
                )

                return

            if destination not in DESTINATIONS:

                self.send_json(
                    400,
                    {
                        "success": False,
                        "message": (
                            "Mục đích vượt link không hợp lệ."
                        )
                    }
                )

                return

            if not SITE_URL.startswith("https://"):

                self.send_json(
                    500,
                    {
                        "success": False,
                        "message": (
                            "SITE_URL phải là địa chỉ HTTPS."
                        )
                    }
                )

                return

            if not LINK4M_API_TOKEN:

                self.send_json(
                    500,
                    {
                        "success": False,
                        "message": (
                            "Chưa cấu hình LINK4M_API_TOKEN trên Render."
                        )
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

                shortened_url = create_link4m_url(
                    callback_url
                )

                cleanup_sessions()

                with SESSIONS_LOCK:

                    SESSIONS[token] = {
                        "created": time.time(),
                        "returned": False,
                        "provider": "link4m",
                        "destination": destination,
                        "view_confirmed": False
                    }

                self.send_json(
                    200,
                    {
                        "success": True,
                        "url": shortened_url,
                        "provider": "link4m",
                        "destination": destination
                    }
                )

                print(
                    "[PHONG WEB V1.0.0] CREATED:",
                    "link4m",
                    destination
                )

            except urllib.error.URLError as error:

                print(
                    "[PHONG WEB] CONNECTION ERROR:",
                    str(error.reason)
                )

                self.send_json(
                    502,
                    {
                        "success": False,
                        "message": (
                            "Không thể kết nối API LINK4M."
                        )
                    }
                )

            except TimeoutError:

                self.send_json(
                    504,
                    {
                        "success": False,
                        "message": (
                            "Link4M phản hồi quá lâu. Vui lòng thử lại."
                        )
                    }
                )

            except ValueError as error:

                print(
                    "[PHONG WEB] API ERROR:",
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
                    "[PHONG WEB] CREATE ERROR:",
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

        # -------------------------------------------------
        # PROVIDER CALLBACK
        # -------------------------------------------------

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
                    "[PHONG WEB V1.0.0] INVALID CALLBACK"
                )

                self.redirect(
                    "/?result=failed&destination=deta"
                )

                return

            print(
                "[PHONG WEB V1.0.0] CALLBACK:",
                provider,
                destination
            )

            # LOCATION:
            # Chưa có API xác nhận View riêng.
            # Giữ nguyên điều kiện bảo vệ của V33.

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

        # -------------------------------------------------
        # CHECK SESSION
        # -------------------------------------------------

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
                        "message": (
                            "Đã nhận callback từ nhà cung cấp."
                        )
                    }
                )

            else:

                self.send_json(
                    403,
                    {
                        "success": False,
                        "returned": False,
                        "view_confirmed": False,
                        "message": (
                            "Phiên vượt link không hợp lệ hoặc đã hết hạn."
                        )
                    }
                )

            return

        # -------------------------------------------------
        # DOWNLOAD ROUTES
        # -------------------------------------------------

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

            # DETA / PROXY / MIZZE

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

        # -------------------------------------------------
        # STATIC FILES
        # -------------------------------------------------

        if path in (
            "/logo.png",
            "/background.jpg",
            "/music.mp3"
        ):

            self.send_static_file(path)

            return

        # -------------------------------------------------
        # NOT FOUND
        # -------------------------------------------------

        self.send_error(
            404,
            "File not found"
        )

    # =====================================================
    # LOG
    # =====================================================

    def log_message(self, format, *args):

        print(
            "[PHONG WEB V1.0.0]",
            format % args
        )


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
    print("              V1.0.0")
    print("====================================")

    print(
        "Server port:",
        PORT
    )

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

    print("Background image: /background.jpg")
    print("Music button: ENABLED")
    print("Music looping: ENABLED")

    print("PHONG WEB VERSION: V1.0.0")

    print("====================================")

    try:

        server.serve_forever()

    except KeyboardInterrupt:

        print(
            "\n[PHONG WEB] Server stopped."
        )

    finally:

        server.server_close()
