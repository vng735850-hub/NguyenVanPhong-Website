import os
import json
import time
import secrets
import hashlib
import threading
import mimetypes
import urllib.request
import urllib.error

from pathlib import Path
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlencode, urlsplit, quote, parse_qs

# =========================================================
# PHONG WEB V2.2.2
# LINK4M ONLY | LOCATION + DETA + PROXY + MIZZE
# ADMIN | JSON STORAGE | ONLINE + DEVICE STATISTICS
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
PORT = int(os.environ.get("PORT", 5000))

DATA_FILE = BASE_DIR / "data.json"

SITE_URL = os.environ.get(
    "SITE_URL", "https://nvp-com.onrender.com"
).strip().rstrip("/")

LINK4M_API_TOKEN = os.environ.get(
    "LINK4M_API_TOKEN", ""
).strip()

LINK4M_ENDPOINT = "https://link4m.co/api-shorten/v2"

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "152012")

SESSION_TTL = 30 * 60
VISITOR_TIMEOUT = 120
ADMIN_TTL = 8 * 60 * 60

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

DEFAULT_DESTINATIONS = {
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
ADMIN_SESSIONS = {}
RATE_LIMITS = {}

LOCK = threading.RLock()
JSON_LOCK = threading.RLock()


# =========================================================
# JSON DATABASE
# =========================================================

DEFAULT_DATA = {
    "settings": {},
    "visitors": {},
    "visitor_devices": {},
    "stats": {
        "total": 0,
        "android": 0,
        "iphone": 0
    }
}

for key, value in DEFAULT_DESTINATIONS.items():
    DEFAULT_DATA["settings"]["url_" + key] = value
    DEFAULT_DATA["settings"]["enabled_" + key] = "1"


def safe_count(value):
    try:
        return max(0, int(value))
    except (ValueError, TypeError, OverflowError):
        return 0


def save_data_unlocked(data):
    """Ghi JSON an toàn bằng file tạm rồi thay thế file chính."""
    temp_file = DATA_FILE.with_suffix(".tmp")

    try:
        with open(temp_file, "w", encoding="utf-8") as file:
            json.dump(
                data,
                file,
                ensure_ascii=False,
                indent=4
            )
            file.flush()
            os.fsync(file.fileno())

        os.replace(temp_file, DATA_FILE)

    except OSError:
        try:
            if temp_file.exists():
                temp_file.unlink()
        except OSError:
            pass
        raise


def load_data_unlocked():
    """Đọc JSON. Phải được gọi khi đang giữ JSON_LOCK."""

    try:
        if DATA_FILE.is_file():
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)

            if not isinstance(data, dict):
                raise ValueError("JSON data không hợp lệ.")

            if not isinstance(data.get("settings"), dict):
                data["settings"] = {}

            if not isinstance(data.get("visitors"), dict):
                data["visitors"] = {}

            if not isinstance(data.get("visitor_devices"), dict):
                data["visitor_devices"] = {}

            if not isinstance(data.get("stats"), dict):
                data["stats"] = {}

            # Bổ sung thiết lập mặc định.
            for key, value in DEFAULT_DATA["settings"].items():
                data["settings"].setdefault(key, value)

            # Bổ sung bộ đếm thống kê nếu thiếu.
            for key, value in DEFAULT_DATA["stats"].items():
                data["stats"][key] = safe_count(
                    data["stats"].get(key, value)
                )

            return data

    except (OSError, ValueError, json.JSONDecodeError) as error:
        print("[JSON WARNING]", str(error))

    data = {
        "settings": dict(DEFAULT_DATA["settings"]),
        "visitors": {},
        "visitor_devices": {},
        "stats": dict(DEFAULT_DATA["stats"])
    }

    save_data_unlocked(data)
    return data


def load_data():
    with JSON_LOCK:
        return load_data_unlocked()


def save_data(data):
    with JSON_LOCK:
        save_data_unlocked(data)


def init_data():
    """Khởi tạo data.json và giữ lại dữ liệu cũ nếu file hợp lệ."""

    with JSON_LOCK:
        data = load_data_unlocked()

        for key, value in DEFAULT_DATA["settings"].items():
            data["settings"].setdefault(key, value)

        if not isinstance(data.get("visitors"), dict):
            data["visitors"] = {}

        if not isinstance(data.get("visitor_devices"), dict):
            data["visitor_devices"] = {}

        if not isinstance(data.get("stats"), dict):
            data["stats"] = {}

        for key, value in DEFAULT_DATA["stats"].items():
            data["stats"][key] = safe_count(
                data["stats"].get(key, value)
            )

        save_data_unlocked(data)

    print("[JSON] DATA FILE:", DATA_FILE)


def setting(key, default=""):
    with JSON_LOCK:
        data = load_data_unlocked()
        return data["settings"].get(key, default)


def set_setting(key, value):
    with JSON_LOCK:
        data = load_data_unlocked()
        data["settings"][key] = str(value)
        save_data_unlocked(data)


def get_destination_links():
    return {
        key: setting("url_" + key, value)
        for key, value in DEFAULT_DESTINATIONS.items()
    }


def destination_enabled(key):
    return setting("enabled_" + key, "1") == "1"


# =========================================================
# DEVICE DETECTION
# =========================================================

def detect_device(user_agent):
    """
    Nhận diện thiết bị bằng User-Agent.
    Kết quả: android, iphone hoặc other.
    """

    ua = str(user_agent or "").lower()

    if "iphone" in ua:
        return "iphone"

    if "android" in ua:
        return "android"

    return "other"


# =========================================================
# ONLINE + VISITOR STATISTICS
# =========================================================

def register_visit(visitor_id, user_agent=""):
    """
    Cập nhật người đang online.

    Chỉ tính tổng khách một lần cho mỗi visitor cookie:
    - total: tất cả khách duy nhất.
    - android: khách Android duy nhất.
    - iphone: khách iPhone duy nhất.
    """

    if not valid_token(visitor_id):
        return

    now = time.time()
    device = detect_device(user_agent)

    with JSON_LOCK:
        data = load_data_unlocked()

        visitors = data.get("visitors", {})
        visitor_devices = data.get("visitor_devices", {})
        stats = data.get("stats", {})

        if not isinstance(visitors, dict):
            visitors = {}

        if not isinstance(visitor_devices, dict):
            visitor_devices = {}

        if not isinstance(stats, dict):
            stats = {}

        # Chỉ tăng tổng khi gặp visitor ID lần đầu.
        if visitor_id not in visitor_devices:
            visitor_devices[visitor_id] = device

            stats["total"] = safe_count(
                stats.get("total", 0)
            ) + 1

            if device == "android":
                stats["android"] = safe_count(
                    stats.get("android", 0)
                ) + 1

            elif device == "iphone":
                stats["iphone"] = safe_count(
                    stats.get("iphone", 0)
                ) + 1

        # Xóa khách đã hết thời gian online.
        expired = []

        for visitor, last_seen in visitors.items():
            try:
                if now - float(last_seen) > VISITOR_TIMEOUT:
                    expired.append(visitor)
            except (ValueError, TypeError):
                expired.append(visitor)

        for visitor in expired:
            visitors.pop(visitor, None)

        # Cập nhật hoạt động hiện tại.
        visitors[visitor_id] = now

        data["visitors"] = visitors
        data["visitor_devices"] = visitor_devices
        data["stats"] = stats

        save_data_unlocked(data)


def get_statistics():
    """
    Trả về:
    online  = số khách đang online.
    total   = tổng khách duy nhất.
    android = khách Android duy nhất.
    iphone  = khách iPhone duy nhất.
    """

    now = time.time()

    with JSON_LOCK:
        data = load_data_unlocked()

        visitors = data.get("visitors", {})
        stats = data.get("stats", {})

        online_visitors = {}

        for visitor, last_seen in visitors.items():
            try:
                last_seen = float(last_seen)

                if now - last_seen <= VISITOR_TIMEOUT:
                    online_visitors[visitor] = last_seen

            except (ValueError, TypeError):
                continue

        data["visitors"] = online_visitors

        result = {
            "online": len(online_visitors),
            "total": safe_count(stats.get("total", 0)),
            "android": safe_count(stats.get("android", 0)),
            "iphone": safe_count(stats.get("iphone", 0))
        }

        save_data_unlocked(data)

        return result


# =========================================================
# SECURITY HELPERS
# =========================================================

def hash_text(value):
    return hashlib.sha256(value.encode()).hexdigest()


def valid_token(token):
    return (
        isinstance(token, str)
        and 30 <= len(token) <= 100
        and all(c.isalnum() or c in "-_" for c in token)
    )


def validate_http_url(value):
    if not isinstance(value, str):
        return False

    value = value.strip()

    if not value or len(value) > 4096:
        return False

    try:
        parsed = urlsplit(value)

        return (
            parsed.scheme in ("https", "http")
            and bool(parsed.hostname)
            and not parsed.username
            and not parsed.password
            and parsed.port in (None, 80, 443)
        )

    except ValueError:
        return False


def validate_mediafire_url(value):
    if not validate_http_url(value):
        return False

    parsed = urlsplit(value)

    return (
        parsed.scheme == "https"
        and parsed.hostname.lower() in (
            "www.mediafire.com",
            "mediafire.com"
        )
    )


def cleanup_sessions():
    now = time.time()

    with LOCK:
        for token in list(SESSIONS):
            if now - SESSIONS[token]["created"] > SESSION_TTL:
                SESSIONS.pop(token, None)

        for token in list(ADMIN_SESSIONS):
            if now - ADMIN_SESSIONS[token]["created"] > ADMIN_TTL:
                ADMIN_SESSIONS.pop(token, None)

        for ip in list(RATE_LIMITS):
            RATE_LIMITS[ip] = [
                t for t in RATE_LIMITS[ip] if now - t < 60
            ]

            if not RATE_LIMITS[ip]:
                RATE_LIMITS.pop(ip, None)


def rate_limited(ip, limit=8):
    now = time.time()

    with LOCK:
        values = RATE_LIMITS.setdefault(ip, [])
        values[:] = [t for t in values if now - t < 60]

        if len(values) >= limit:
            return True

        values.append(now)
        return False


def get_session(token):
    if not valid_token(token):
        return None

    with LOCK:
        session = SESSIONS.get(token)

        if not session:
            return None

        if time.time() - session["created"] > SESSION_TTL:
            SESSIONS.pop(token, None)
            return None

        return dict(session)


def check_session(token, destination=None):
    session = get_session(token)

    if not session or not session.get("returned"):
        return False

    if destination and session.get("destination") != destination:
        return False

    return True


# =========================================================
# LINK4M API
# =========================================================

def api_request(url):
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 PHONG-WEB/2.2.2",
            "Accept": "application/json",
            "Cache-Control": "no-cache"
        },
        method="GET"
    )

    try:
        with urllib.request.urlopen(request, timeout=25) as response:
            return response.read().decode(
                "utf-8",
                errors="replace"
            )

    except urllib.error.HTTPError as error:
        body = error.read().decode(
            "utf-8",
            errors="replace"
        )

        raise ValueError(
            "Link4M HTTP " + str(error.code) + ": " + body[:180]
        )

    except urllib.error.URLError as error:
        raise ValueError(
            "Không thể kết nối Link4M: " + str(error.reason)
        )


def create_link4m_url(callback_url):
    if not LINK4M_API_TOKEN:
        raise ValueError(
            "Chưa cấu hình LINK4M_API_TOKEN trên Render."
        )

    api_url = LINK4M_ENDPOINT + "?" + urlencode({
        "api": LINK4M_API_TOKEN,
        "url": callback_url
    })

    try:
        result = json.loads(api_request(api_url))

    except json.JSONDecodeError:
        raise ValueError(
            "Link4M không trả về JSON hợp lệ."
        )

    if not isinstance(result, dict):
        raise ValueError("Dữ liệu Link4M không hợp lệ.")

    if result.get("status") != "success":
        raise ValueError(
            "Link4M: " +
            str(result.get("message", "Tạo link thất bại"))[:180]
        )

    url = (
        result.get("shortenedUrl")
        or result.get("shortened_url")
        or result.get("short_url")
    )

    if not validate_http_url(url):
        raise ValueError(
            "Link4M trả về URL không hợp lệ."
        )

    return url


# =========================================================
# WEBSITE HTML
# =========================================================

HTML = r"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<meta name="theme-color" content="#080d20">
<title>NGUYỄN VĂN PHONG WEBSITE</title>
<style>
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{
 margin:0;min-height:100vh;font-family:Arial,sans-serif;color:white;
 background:linear-gradient(rgba(3,7,25,.84),rgba(3,7,25,.9)),
 url('/background.jpg') center/cover fixed no-repeat,#080d20;
 overflow-x:hidden
}
body:before{
 content:"";position:fixed;inset:-50%;z-index:-1;pointer-events:none;
 background:
 radial-gradient(circle at 20% 30%,rgba(0,130,255,.2),transparent 28%),
 radial-gradient(circle at 80% 60%,rgba(0,210,255,.13),transparent 30%);
 animation:glowMove 13s ease-in-out infinite alternate
}
@keyframes glowMove{
 from{transform:translate(-3%,-2%) rotate(0deg)}
 to{transform:translate(3%,2%) rotate(8deg)}
}
header{
 position:relative;z-index:20;width:100%;min-height:75px;
 display:grid;grid-template-columns:43px minmax(0,1fr) 105px;
 align-items:center;gap:10px;padding:10px 15px;
 background:rgba(4,10,30,.91);
 border-bottom:1px solid #299cff;
 box-shadow:0 0 22px rgba(0,130,255,.22)
}
.hamburger-button{
 width:43px;height:43px;border:1px solid #55baff;border-radius:10px;
 background:rgba(0,120,255,.2);color:white;font-size:25px;cursor:pointer
}
.header-title{
 min-width:0;text-align:center;font-size:clamp(11px,3vw,23px);
 font-weight:900;letter-spacing:1px;text-shadow:0 0 12px #168cff;
 white-space:nowrap;overflow:hidden;text-overflow:ellipsis
}
.clock-box{
 width:105px;height:43px;display:flex;align-items:center;
 justify-content:center;background:rgba(0,120,255,.2);
 border:1px solid #55baff;border-radius:10px;
 box-shadow:0 0 12px #168cff;font-family:monospace;
 font-size:14px;font-weight:900;white-space:nowrap
}
.side-menu{
 display:none;position:absolute;top:67px;left:12px;width:200px;
 padding:9px;background:rgba(5,14,38,.98);
 border:1px solid #299cff;border-radius:12px
}
.side-menu.show{display:block}
.side-menu a{display:block;padding:13px;color:white;text-decoration:none}
.side-menu a:hover{background:#087ce5;border-radius:8px}
.container{width:min(900px,92%);margin:25px auto;text-align:center}
.page{display:none;animation:pageIn .38s ease both}
.page.active{display:block}
@keyframes pageIn{
 from{opacity:0;transform:translateY(12px)}
 to{opacity:1;transform:translateY(0)}
}
.hero-logo{
 width:125px;height:125px;object-fit:contain;margin:20px auto;
 border-radius:50%;filter:drop-shadow(0 0 17px #168cff)
}
h1{font-size:clamp(23px,5vw,34px);text-shadow:0 0 15px #168cff}
.subtitle{color:#d2e7ff;font-size:14px;line-height:1.8;margin:15px auto 25px}
.location-container,.menu-container{margin:18px auto}
.location-link{display:block;color:inherit;text-decoration:none}
.location-card{
 display:flex;align-items:center;justify-content:center;gap:20px;
 padding:22px 15px;background:rgba(10,27,60,.9);
 border:1px solid #459fff;border-radius:15px;
 box-shadow:0 0 18px rgba(0,130,255,.18);transition:.25s
}
.location-card:hover,.menu-card:hover,.link-box:hover{
 transform:translateY(-3px);box-shadow:0 0 28px rgba(0,140,255,.4)
}
.location-emoji{font-size:43px}
.location-info{text-align:left}
.location-info h2{margin:0 0 9px;font-size:19px}
.location-info p{margin:0 0 12px;color:#c6e1ff;font-size:13px}
.location-button,.open-menu-button,.cross-link-button{
 display:inline-block;padding:12px 22px;color:white;font-weight:bold;
 background:linear-gradient(120deg,#0877e8,#12a8ff);
 border:0;border-radius:9px;cursor:pointer;text-decoration:none;
 box-shadow:0 0 13px rgba(0,130,255,.22);transition:.2s
}
.menu-card{
 padding:23px 15px;background:rgba(9,24,55,.9);
 border:1px solid rgba(64,157,255,.65);border-radius:15px;transition:.25s
}
.menu-card h2{font-size:18px;margin:0 0 17px}
.link-box{
 max-width:570px;margin:35px auto;padding:28px 20px;
 background:rgba(7,21,49,.96);border:1px solid #399cff;
 border-radius:17px;box-shadow:0 0 25px rgba(0,110,255,.2);
 transition:.25s
}
.link-icon{font-size:48px;margin-bottom:12px}
.link-box h2{color:#8acaff;font-size:20px;line-height:1.5}
.link-description{color:#d1e5ff;font-size:14px;line-height:1.8;margin:15px auto 22px}
.cross-link-button{padding:14px 25px}
.cross-link-button:disabled{opacity:.6;cursor:wait}
.back-button{
 display:inline-block;padding:11px 18px;color:white;font-size:13px;
 font-weight:bold;text-decoration:none;background:rgba(20,65,120,.8);
 border:1px solid #4caeff;border-radius:9px
}
.status{min-height:24px;margin:17px auto;color:#ffe18b;font-size:13px;line-height:1.7;overflow-wrap:anywhere}
.status.error{color:#ff7777}.status.success{color:#5dffac;font-weight:bold}
.result-action{
 display:inline-block;margin:12px auto;padding:14px 30px;color:white;
 font-weight:bold;text-decoration:none;background:linear-gradient(120deg,#08a75d,#16d68b);
 border-radius:10px;cursor:pointer
}
.hidden{display:none!important}
.thank-image-button{
 display:block;width:min(260px,90%);margin:20px auto;padding:0;
 border:2px solid #55baff;border-radius:12px;overflow:hidden;
 background:rgba(0,100,220,.2);cursor:pointer;box-shadow:0 0 18px #168cff
}
.thank-image-button img{display:block;width:100%;height:auto;object-fit:contain}
.music-mini{display:flex;justify-content:center;margin:25px auto 15px}
.music-mini button{
 width:53px;height:53px;border:2px solid #75caff;border-radius:50%;
 color:white;background:linear-gradient(135deg,#086de0,#13b5ff);
 font-size:21px;cursor:pointer;box-shadow:0 0 18px #168cff
}
.music-mini button.playing{animation:pulse 1.4s infinite}
@keyframes pulse{50%{box-shadow:0 0 30px #36caff}}
footer{
 padding:18px 10px 22px;text-align:center;color:#c1dcff;
 font-size:13px;line-height:1.9;background:rgba(3,8,23,.9);
 border-top:1px solid rgba(80,170,255,.3)
}
footer strong{color:#55baff;letter-spacing:1px}
#toast{
 position:fixed;z-index:10000;top:88px;left:50%;
 transform:translate(-50%,-15px);opacity:0;pointer-events:none;
 width:min(90%,430px);padding:14px 17px;border-radius:11px;
 background:rgba(5,22,52,.97);border:1px solid #48baff;
 box-shadow:0 0 22px rgba(0,140,255,.4);text-align:center;
 transition:.25s;font-size:14px
}
#toast.show{opacity:1;transform:translate(-50%,0)}
#toast.bad{border-color:#ff6565}
#toast.good{border-color:#48e8a0}
.stats-bar{
 display:flex;justify-content:center;gap:10px;flex-wrap:wrap;
 margin:15px auto;color:#cce8ff;font-size:12px
}
.stats-bar span{
 padding:10px 13px;border:1px solid rgba(75,165,255,.5);
 border-radius:9px;background:rgba(4,20,48,.75);
 min-width:145px
}
.stats-bar b{color:#fff;font-size:14px}
@media(max-width:600px){
 header{grid-template-columns:40px minmax(0,1fr) 95px;gap:6px;padding:8px;min-height:65px}
 .hamburger-button{width:40px;height:43px;font-size:23px}
 .header-title{font-size:clamp(10px,3.2vw,15px);letter-spacing:0}
 .clock-box{width:95px;height:41px;font-size:12px}
 .side-menu{top:60px}.location-card{gap:12px}
 .location-info h2{font-size:16px}
 .link-box{margin:22px auto;padding:23px 15px}
 .stats-bar span{flex:1 1 145px}
}
</style>
</head>
<body>

<div id="toast"></div>

<header>
 <button class="hamburger-button" id="hamburgerButton">☰</button>
 <div class="header-title">NGUYỄN VĂN PHONG WEBSITE</div>
 <div class="clock-box"><span id="liveClock">🌙 00:00:00</span></div>
 <nav class="side-menu" id="sideMenu">
  <a href="/" id="homeMenuButton">🏠 TRANG CHỦ</a>
  <a href="/admin">⚙️ QUẢN TRỊ</a>
 </nav>
</header>

<main class="container">

<section class="page" id="homePage">
 <img class="hero-logo" src="/logo.png" alt="PHONG WEB">
 <h1>WELCOME TO PHONG WEB</h1>
 <div class="subtitle">
  Chào mừng bạn đến với website của Nguyễn Văn Phong.
  <br>📍 ĐỊNH VỊ XANH TÍM OB55
 </div>

 <div class="stats-bar">
  <span>🟢 Đang truy cập: <b id="onlineCount">...</b></span>
  <span>👁 Tổng số người truy cập: <b id="totalCount">...</b></span>
  <span>🤖 Android: <b id="androidCount">...</b></span>
  <span>🍎 iPhone: <b id="iphoneCount">...</b></span>
 </div>

 <section class="location-container" id="card-location">
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

 <section class="menu-container" id="card-deta">
  <div class="menu-card"><h2>🔐 DETA IPA CRACK NOKЕY</h2>
   <button class="open-menu-button" onclick="navigate('/menu')">MỞ MENU</button>
  </div>
 </section>

 <section class="menu-container" id="card-proxy">
  <div class="menu-card"><h2>🌐 PROXY MOD ALEN CRACK</h2>
   <button class="open-menu-button" onclick="navigate('/proxy-mod-alen-crack')">MỞ MỤC</button>
  </div>
 </section>

 <section class="menu-container" id="card-mizze">
  <div class="menu-card"><h2>🎮 MENU MIZZE CRACK</h2>
   <button class="open-menu-button" onclick="navigate('/mizze-crack')">MỞ MỤC</button>
  </div>
 </section>
</section>

<section class="page" id="locationPage">
 <div class="link-box"><div class="link-icon">📍</div>
  <h2>BẠN CẦN VƯỢT LINK ĐỂ LẤY FILE MEDIAFIRE</h2>
  <div class="link-description">Nhấn nút bên dưới để tạo liên kết vượt.<br>Sau khi hoàn thành Link4M, bạn sẽ quay lại PHONG WEB.</div>
  <button class="cross-link-button" id="locationCrossButton">🔓 VƯỢT LINK</button>
  <div class="status" id="locationStatus"></div><br>
  <a class="back-button" href="/">← QUAY LẠI TRANG CHỦ</a>
 </div>
</section>

<section class="page" id="detaPage">
 <div class="link-box"><div class="link-icon">🔐</div>
  <h2>BẠN CẦN VƯỢT LINK ĐỂ LẤY FILE DETA</h2>
  <div class="link-description">Nhấn nút bên dưới để tạo liên kết vượt.<br>Sau khi hoàn thành Link4M, bạn sẽ quay lại PHONG WEB.</div>
  <button class="cross-link-button" id="detaCrossButton">🔓 VƯỢT LINK</button>
  <div class="status" id="detaStatus"></div><br>
  <a class="back-button" href="/">← QUAY LẠI TRANG CHỦ</a>
 </div>
</section>

<section class="page" id="proxyPage">
 <div class="link-box"><div class="link-icon">🌐</div>
  <h2>BẠN CẦN VƯỢT LINK ĐỂ LẤY FILE PROXY MOD ALEN CRACK</h2>
  <div class="link-description">Nhấn nút bên dưới để tạo liên kết vượt.<br>Sau khi hoàn thành Link4M, bạn sẽ quay lại PHONG WEB.</div>
  <button class="cross-link-button" id="proxyCrossButton">🔓 VƯỢT LINK</button>
  <div class="status" id="proxyStatus"></div><br>
  <a class="back-button" href="/">← QUAY LẠI TRANG CHỦ</a>
 </div>
</section>

<section class="page" id="mizzePage">
 <div class="link-box"><div class="link-icon">🎮</div>
  <h2>BẠN CẦN VƯỢT LINK ĐỂ LẤY FILE MENU MIZZE CRACK</h2>
  <div class="link-description">Nhấn nút bên dưới để tạo liên kết vượt.<br>Sau khi hoàn thành Link4M, bạn sẽ quay lại PHONG WEB.</div>
  <button class="cross-link-button" id="mizzeCrossButton">🔓 VƯỢT LINK</button>
  <div class="status" id="mizzeStatus"></div><br>
  <a class="back-button" href="/">← QUAY LẠI TRANG CHỦ</a>
 </div>
</section>

<section class="page" id="thankPage">
 <div class="link-box"><div class="link-icon">💙</div>
  <h2>Cảm Ơn Vì Đã Ủng Hộ Cho Phong</h2>
  <div class="link-description">Phong chân thành cảm ơn bạn đã dành thời gian ủng hộ website.<br>Nhấn vào hình bên dưới để nghe lời cảm ơn nhé!</div>
  <button class="thank-image-button" id="thankAudioButton">
   <img src="/cam-on-tu-phong.png" alt="Cảm Ơn Từ Phong">
  </button>
  <div class="status" id="thankStatus">🔊 Nhấn vào ảnh để phát âm thanh cảm ơn.</div>
  <button class="cross-link-button" id="continueButton">TIẾP THEO →</button>
  <audio id="thankAudio" src="/cam-on-tu-phong.mp3" preload="none"></audio>
 </div>
</section>

<section class="page" id="resultPage">
 <div class="link-box"><div class="link-icon" id="resultIcon">✅</div>
  <h2 id="resultTitle">Vượt Link Thành Công</h2>
  <div class="link-description" id="resultDescription"></div>
  <a class="result-action hidden" id="resultAction" href="/">LẤY FILE</a>
  <button class="cross-link-button hidden" id="retryButton">🔄 VƯỢT LINK MỚI</button>
  <div class="status" id="resultStatus"></div><br>
  <a class="back-button" id="resultBack" href="/">← QUAY LẠI TRANG CHỦ</a>
 </div>
</section>

</main>

<div class="music-mini">
 <button id="musicButton"><span id="musicIcon">▶</span></button>
</div>

<audio id="backgroundMusic" src="/music.mp3" loop></audio>

<footer>
 © 2026 Nguyễn Văn Phong Website<br>
 <strong>PHONG WEB V2.2.2</strong>
</footer>

<script>
const pages={
 home:document.getElementById("homePage"),
 location:document.getElementById("locationPage"),
 deta:document.getElementById("detaPage"),
 proxy:document.getElementById("proxyPage"),
 mizze:document.getElementById("mizzePage"),
 thank:document.getElementById("thankPage"),
 result:document.getElementById("resultPage")
};

const destinationRoutes={
 location:"/dinh-vi",
 deta:"/menu",
 proxy:"/proxy-mod-alen-crack",
 mizze:"/mizze-crack"
};

const downloadRoutes={
 location:"/download-location",
 deta:"/download-deta",
 proxy:"/download-proxy",
 mizze:"/download-mizze"
};

function toast(message,type="good"){
 const el=document.getElementById("toast");
 el.textContent=message;
 el.className="show "+type;
 clearTimeout(window.toastTimer);
 window.toastTimer=setTimeout(()=>el.className="",3500);
}

// =====================================================
// CLOCK - VIETNAM TIME + DAY ICON
// =====================================================

function updateClock(){
 const now=new Date();

 const parts=new Intl.DateTimeFormat("en-GB",{
  timeZone:"Asia/Ho_Chi_Minh",
  hour:"2-digit",
  minute:"2-digit",
  second:"2-digit",
  hourCycle:"h23"
 }).formatToParts(now);

 const values={};

 parts.forEach(part=>{
  values[part.type]=part.value;
 });

 const hour=Number(values.hour);

 let icon="🌙";

 if(hour>=6 && hour<13){
  icon="🌅";
 }else if(hour>=13 && hour<19){
  icon="☀️";
 }else{
  icon="🌙";
 }

 document.getElementById("liveClock").textContent=
  icon+" "+values.hour+":"+values.minute+":"+values.second;
}

updateClock();
setInterval(updateClock,1000);


// =====================================================
// PAGE NAVIGATION
// =====================================================

function hideAllPages(){
 Object.values(pages).forEach(p=>p.classList.remove("active"));
}

function navigate(path){
 history.pushState({},"",path);
 showPage();
 window.scrollTo(0,0);
}

function showPage(){
 hideAllPages();

 const q=new URLSearchParams(location.search);
 const result=q.get("result");

 if(result==="thanks"){
  pages.thank.classList.add("active");
  return;
 }

 if(result==="success"||result==="failed"){
  pages.result.classList.add("active");
  checkResult();
  return;
 }

 const routes={
  "/":pages.home,
  "/index.html":pages.home,
  "/dinh-vi":pages.location,
  "/menu":pages.deta,
  "/proxy-mod-alen-crack":pages.proxy,
  "/mizze-crack":pages.mizze
 };

 (routes[location.pathname]||pages.home).classList.add("active");
}

window.addEventListener("popstate",showPage);


// =====================================================
// ONLINE + TOTAL + DEVICE STATISTICS
// =====================================================

async function refreshStats(){
 try{
  const r=await fetch("/stats",{cache:"no-store"});
  const d=await r.json();

  if(!r.ok||!d.success){
   return;
  }

  document.getElementById("onlineCount").textContent=
   Number(d.online||0).toLocaleString("vi-VN");

  document.getElementById("totalCount").textContent=
   Number(d.total||0).toLocaleString("vi-VN");

  document.getElementById("androidCount").textContent=
   Number(d.android||0).toLocaleString("vi-VN");

  document.getElementById("iphoneCount").textContent=
   Number(d.iphone||0).toLocaleString("vi-VN");

 }catch(e){}
}

setInterval(refreshStats,15000);
refreshStats();


// =====================================================
// PUBLIC SETTINGS
// =====================================================

async function refreshCards(){
 try{
  const r=await fetch("/public-settings",{cache:"no-store"});
  const d=await r.json();

  for(const key of ["location","deta","proxy","mizze"]){
   const card=document.getElementById("card-"+key);

   if(card){
    card.style.display=d[key]?"":"none";
   }
  }
 }catch(e){}
}

refreshCards();


// =====================================================
// CREATE SHORT LINK
// =====================================================

async function createShortLink(destination,button,status){
 button.disabled=true;
 button.textContent="ĐANG XỬ LÝ...";

 status.className="status";
 status.textContent="Đang kết nối API LINK4M...";

 try{
  const response=await fetch(
   "/create-short-link?destination="+
   encodeURIComponent(destination),
   {cache:"no-store"}
  );

  const data=await response.json();

  if(!response.ok||!data.success){
   throw new Error(data.message||"Không thể tạo link.");
  }

  if(!data.url){
   throw new Error("Link4M không trả về URL.");
  }

  status.className="status success";
  status.textContent=
   "Tạo link thành công! Đang chuyển đến Link4M...";

  toast("Tạo link thành công! Đang chuyển hướng.","good");

  window.location.href=data.url;

 }catch(error){
  status.className="status error";
  status.textContent="LỖI: "+error.message;

  toast("Tạo link thất bại: "+error.message,"bad");

  button.disabled=false;
  button.textContent="🔓 THỬ LẠI";
 }
}

function setupCrossButton(key){
 const button=document.getElementById(key+"CrossButton");
 const status=document.getElementById(key+"Status");

 button.addEventListener("click",()=>{
  createShortLink(key,button,status);
 });
}

["location","deta","proxy","mizze"].forEach(setupCrossButton);


// =====================================================
// THANK YOU AUDIO
// =====================================================

const thankAudio=document.getElementById("thankAudio");

document.getElementById("thankAudioButton").addEventListener("click",async()=>{
 const status=document.getElementById("thankStatus");

 try{
  if(thankAudio.paused){
   await thankAudio.play();

   status.className="status success";
   status.textContent="🎵 Đang phát lời cảm ơn từ Phong...";

  }else{
   thankAudio.pause();
   status.textContent="Đã tạm dừng âm thanh.";
  }

 }catch(e){
  status.className="status error";
  status.textContent="Không thể phát âm thanh. Kiểm tra file MP3.";
 }
});

thankAudio.addEventListener("ended",()=>{
 document.getElementById("thankStatus").textContent=
  "💙 Cảm ơn bạn đã lắng nghe!";
});


// =====================================================
// CONTINUE AFTER LINK4M
// =====================================================

document.getElementById("continueButton").addEventListener("click",async()=>{
 const q=new URLSearchParams(location.search);

 const token=q.get("token");
 const destination=q.get("destination");

 if(!token||!destination||!destinationRoutes[destination]){
  showFailure("Không tìm thấy thông tin phiên vượt link.",destination);
  return;
 }

 const button=document.getElementById("continueButton");

 button.disabled=true;
 button.textContent="ĐANG KIỂM TRA...";

 try{
  const r=await fetch(
   "/check-session?token="+encodeURIComponent(token),
   {cache:"no-store"}
  );

  const d=await r.json();

  if(!r.ok||!d.success||!d.returned){
   throw new Error(d.message||"Phiên chưa được xác nhận.");
  }

  if(d.destination!==destination){
   throw new Error("Thông tin mục vượt link không khớp.");
  }

  history.pushState(
   {},
   "",
   "/?result=success&destination="+
   encodeURIComponent(destination)+
   "&token="+encodeURIComponent(token)
  );

  showPage();
  window.scrollTo(0,0);

 }catch(e){
  showFailure(e.message,destination);

 }finally{
  button.disabled=false;
  button.textContent="TIẾP THEO →";
 }
});


// =====================================================
// FAILURE PAGE
// =====================================================

function showFailure(message,destination){
 hideAllPages();
 pages.result.classList.add("active");

 document.getElementById("resultIcon").textContent="❌";

 document.getElementById("resultTitle").textContent=
  "Vượt Link Không Thành Công";

 document.getElementById("resultDescription").textContent=
  "Phiên vượt link chưa được xác nhận hoặc đã hết hạn.";

 const status=document.getElementById("resultStatus");

 status.className="status error";
 status.textContent=message||"Vui lòng thử vượt link mới.";

 document.getElementById("resultAction").classList.add("hidden");

 const retry=document.getElementById("retryButton");

 retry.classList.remove("hidden");

 retry.onclick=()=>{
  navigate(destinationRoutes[destination]||"/");
 };
}


// =====================================================
// CHECK RESULT
// =====================================================

async function checkResult(){
 const q=new URLSearchParams(location.search);

 const result=q.get("result");
 const destination=q.get("destination");
 const token=q.get("token");

 const action=document.getElementById("resultAction");
 const retry=document.getElementById("retryButton");

 action.classList.add("hidden");
 retry.classList.add("hidden");

 document.getElementById("resultStatus").textContent="";

 if(result==="failed"){
  showFailure("Không nhận được callback hợp lệ từ Link4M.",destination);
  return;
 }

 if(result!=="success"||!token||!downloadRoutes[destination]){
  showFailure("Không tìm thấy thông tin phiên vượt link.",destination);
  return;
 }

 document.getElementById("resultIcon").textContent="⏳";

 document.getElementById("resultTitle").textContent=
  "ĐANG KIỂM TRA";

 document.getElementById("resultDescription").textContent=
  "Đang kiểm tra phiên quay lại từ Link4M...";

 try{
  const r=await fetch(
   "/check-session?token="+encodeURIComponent(token),
   {cache:"no-store"}
  );

  const d=await r.json();

  if(!r.ok||!d.success||!d.returned){
   throw new Error(d.message||"Phiên không hợp lệ.");
  }

  if(d.destination!==destination){
   throw new Error("Thông tin mục vượt link không khớp.");
  }

  document.getElementById("resultIcon").textContent="✅";

  document.getElementById("resultTitle").textContent=
   "Vượt Link Thành Công";

  document.getElementById("resultDescription").textContent=
   "Bạn đã quay lại PHONG WEB. Nhấn LẤY FILE để mở MediaFire.";

  const status=document.getElementById("resultStatus");

  status.className="status success";
  status.textContent="Đã xác nhận phiên Link4M.";

  action.href=
   downloadRoutes[destination]+"?token="+encodeURIComponent(token);

  action.classList.remove("hidden");

 }catch(e){
  showFailure(e.message,destination);
 }
}


// =====================================================
// HAMBURGER MENU
// =====================================================

const hamburger=document.getElementById("hamburgerButton");
const menu=document.getElementById("sideMenu");

hamburger.addEventListener("click",e=>{
 e.stopPropagation();
 menu.classList.toggle("show");
});

document.getElementById("homeMenuButton").addEventListener("click",e=>{
 e.preventDefault();
 menu.classList.remove("show");
 navigate("/");
});

document.addEventListener("click",e=>{
 if(!menu.contains(e.target)&&!hamburger.contains(e.target)){
  menu.classList.remove("show");
 }
});


// =====================================================
// BACKGROUND MUSIC
// =====================================================

const music=document.getElementById("backgroundMusic");
const musicButton=document.getElementById("musicButton");

musicButton.addEventListener("click",async()=>{
 try{
  if(music.paused){
   await music.play();

   document.getElementById("musicIcon").textContent="Ⅱ";
   musicButton.classList.add("playing");

  }else{
   music.pause();

   document.getElementById("musicIcon").textContent="▶";
   musicButton.classList.remove("playing");
  }

 }catch(e){
  toast("Không thể phát nhạc. Kiểm tra music.mp3.","bad");
 }
});

showPage();
</script>
</body>
</html>
"""


# =========================================================
# ADMIN HTML
# =========================================================

ADMIN_HTML = r"""<!DOCTYPE html>
<html lang="vi">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>PHONG WEB - ADMIN</title>
<style>
*{box-sizing:border-box}
body{
 margin:0;padding:20px;background:#071022;color:white;
 font-family:Arial,sans-serif
}
main{max-width:760px;margin:25px auto}
.panel{
 margin:15px 0;padding:20px;background:#0d1d3a;
 border:1px solid #299cff;border-radius:14px;
 box-shadow:0 0 18px #073c70
}
h1,h2{color:#70c5ff}
input{
 width:100%;padding:12px;margin:8px 0;
 border-radius:8px;border:1px solid #398ddd;
 background:#07152d;color:white
}
button{
 padding:12px 18px;border:0;border-radius:8px;
 color:white;background:#087ce5;font-weight:bold;cursor:pointer
}
button.danger{background:#b52c42}
button.good{background:#078653}
label{display:block;margin:12px 0}
.small{color:#b9d7f7;font-size:13px;line-height:1.7}
.hidden{display:none}
.row{display:flex;gap:10px;flex-wrap:wrap;align-items:center}
.row button{margin:5px 0}
#message{margin:12px 0;color:#74ffc0;overflow-wrap:anywhere}
a{color:#7bcaff}
.stat-grid{
 display:grid;grid-template-columns:repeat(2,minmax(0,1fr));
 gap:10px;margin:15px 0
}
.stat-card{
 padding:15px;background:#07152d;
 border:1px solid #398ddd;border-radius:10px;
 line-height:1.8
}
.stat-card b{display:block;color:#fff;font-size:25px}
.stat-card span{color:#b9d7f7;font-size:13px}
@media(max-width:450px){
 body{padding:10px}
 .stat-grid{grid-template-columns:1fr}
}
</style>
</head>
<body>
<main>

<h1>⚙️ PHONG WEB V2.2.2 - QUẢN TRỊ</h1>
<p class="small">Trang quản trị riêng của Nguyễn Văn Phong.</p>

<section class="panel" id="loginPanel">
<h2>🔐 ĐĂNG NHẬP QUẢN TRỊ</h2>
<input id="password" type="password" placeholder="Nhập mật khẩu quản trị">
<button onclick="login()">ĐĂNG NHẬP</button>
<div id="loginMessage" class="small"></div>
</section>

<div id="dashboard" class="hidden">

<section class="panel">
<h2>📊 THỐNG KÊ WEBSITE</h2>

<div class="stat-grid">
 <div class="stat-card">
  🟢 Đang truy cập
  <b id="online">...</b>
  <span>Người đang online</span>
 </div>

 <div class="stat-card">
  👁 Tổng số người truy cập
  <b id="total">...</b>
  <span>Tổng khách duy nhất</span>
 </div>

 <div class="stat-card">
  🤖 Điện thoại Android
  <b id="android">...</b>
  <span>Khách Android duy nhất</span>
 </div>

 <div class="stat-card">
  🍎 Điện thoại iPhone
  <b id="iphone">...</b>
  <span>Khách iPhone duy nhất</span>
 </div>
</div>

<button onclick="loadStats()">LÀM MỚI THỐNG KÊ</button>
</section>

<section class="panel">
<h2>🗂️ QUẢN LÝ CÁC MỤC</h2>
<p class="small">Bật/tắt từng mục và thay đổi đường dẫn MediaFire.</p>
<div id="items"></div>
<button class="good" onclick="saveSettings()">LƯU THAY ĐỔI</button>
</section>

<section class="panel">
<h2>🔒 BẢO MẬT</h2>
<p class="small">
Phiên vượt link hết hạn sau 30 phút.
Trang quản trị tự đăng xuất sau thời gian không hoạt động.
Không chia sẻ mật khẩu quản trị.
</p>
<button class="danger" onclick="logout()">ĐĂNG XUẤT</button>
</section>

</div>

<div id="message"></div>
<p><a href="/">← Quay lại website</a></p>

</main>

<script>
let config={};

async function api(path,body){
 const options={
  method:body?"POST":"GET",
  headers:{}
 };

 if(body){
  options.headers["Content-Type"]="application/json";
  options.body=JSON.stringify(body);
 }

 const r=await fetch(path,options);
 const d=await r.json();

 if(!r.ok||!d.success){
  throw new Error(d.message||"Có lỗi xảy ra.");
 }

 return d;
}

async function login(){
 const msg=document.getElementById("loginMessage");

 try{
  await api("/admin/login",{
   password:document.getElementById("password").value
  });

  document.getElementById("loginPanel").classList.add("hidden");
  document.getElementById("dashboard").classList.remove("hidden");

  msg.textContent="";

  await loadAll();

 }catch(e){
  msg.textContent=e.message;
 }
}

async function loadStats(){
 const d=await api("/admin/stats");

 document.getElementById("online").textContent=
  Number(d.online||0).toLocaleString("vi-VN");

 document.getElementById("total").textContent=
  Number(d.total||0).toLocaleString("vi-VN");

 document.getElementById("android").textContent=
  Number(d.android||0).toLocaleString("vi-VN");

 document.getElementById("iphone").textContent=
  Number(d.iphone||0).toLocaleString("vi-VN");
}

async function loadAll(){
 await loadStats();

 const d=await api("/admin/settings");

 config=d.items;

 const root=document.getElementById("items");
 root.innerHTML="";

 for(const [key,item] of Object.entries(config)){
  const box=document.createElement("div");
  box.className="panel";

  const title=document.createElement("h3");
  title.textContent=item.name;

  const check=document.createElement("input");
  check.type="checkbox";
  check.checked=item.enabled;
  check.id="enabled-"+key;

  const label=document.createElement("label");
  label.textContent="Hiển thị mục này";
  label.prepend(check);

  const url=document.createElement("input");
  url.type="url";
  url.id="url-"+key;
  url.value=item.url;
  url.placeholder="https://www.mediafire.com/...";

  box.append(title,label,url);
  root.append(box);
 }
}

async function saveSettings(){
 try{
  const items={};

  for(const key of Object.keys(config)){
   items[key]={
    enabled:document.getElementById("enabled-"+key).checked,
    url:document.getElementById("url-"+key).value.trim()
   };
  }

  await api("/admin/settings",{items});

  document.getElementById("message").textContent=
   "Đã lưu thiết lập thành công.";

  await loadAll();

 }catch(e){
  document.getElementById("message").textContent=e.message;
 }
}

async function logout(){
 try{
  await api("/admin/logout",{});
 }catch(e){}

 location.reload();
}

async function checkAdmin(){
 try{
  const d=await api("/admin/me");

  if(d.success){
   document.getElementById("loginPanel").classList.add("hidden");
   document.getElementById("dashboard").classList.remove("hidden");
   await loadAll();
  }
 }catch(e){}
}

checkAdmin();
</script>
</body>
</html>
"""


# =========================================================
# HTTP SERVER
# =========================================================

class Website(BaseHTTPRequestHandler):

    server_version = "PhongWeb/2.2.2"
    sys_version = ""

    def client_ip(self):
        return self.client_address[0]

    def send_security_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")

        self.send_header(
            "Referrer-Policy",
            "strict-origin-when-cross-origin"
        )

        self.send_header(
            "Content-Security-Policy",
            "default-src 'self' https: data:; "
            "script-src 'self' 'unsafe-inline'; "
            "style-src 'self' 'unsafe-inline'; "
            "img-src 'self' https: data:; "
            "media-src 'self'; frame-ancestors 'none'"
        )

    def send_json(self, status, data, extra_headers=None):
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
        self.send_security_headers()

        if extra_headers:
            for key, value in extra_headers.items():
                self.send_header(key, value)

        self.end_headers()

        try:
            self.wfile.write(content)

        except (BrokenPipeError, ConnectionResetError):
            pass

    def send_html(self, content, status=200):
        data = content.encode("utf-8")

        self.send_response(status)

        self.send_header(
            "Content-Type",
            "text/html; charset=utf-8"
        )

        self.send_header(
            "Content-Length",
            str(len(data))
        )

        self.send_header("Cache-Control", "no-store")
        self.send_security_headers()

        self.end_headers()

        try:
            self.wfile.write(data)

        except (BrokenPipeError, ConnectionResetError):
            pass

    def redirect(self, location):
        self.send_response(302)
        self.send_header("Location", location)
        self.send_header("Cache-Control", "no-store")
        self.send_security_headers()
        self.end_headers()

    def read_json(self):
        try:
            length = int(
                self.headers.get("Content-Length", "0")
            )

        except ValueError:
            return None

        if length <= 0 or length > 20000:
            return None

        try:
            raw = self.rfile.read(length)

            value = json.loads(
                raw.decode("utf-8")
            )

            return value if isinstance(value, dict) else None

        except (ValueError, UnicodeDecodeError):
            return None

    def get_cookie(self, name):
        cookie = SimpleCookie()

        try:
            cookie.load(
                self.headers.get("Cookie", "")
            )

            morsel = cookie.get(name)

            return morsel.value if morsel else ""

        except Exception:
            return ""

    def admin_token(self):
        return self.get_cookie("ph_admin")

    def is_admin(self):
        token = self.admin_token()

        if not valid_token(token):
            return False

        with LOCK:
            session = ADMIN_SESSIONS.get(token)

            if not session:
                return False

            if time.time() - session["created"] > ADMIN_TTL:
                ADMIN_SESSIONS.pop(token, None)
                return False

            session["created"] = time.time()
            return True

    def require_admin(self):
        if not self.is_admin():
            self.send_json(401, {
                "success": False,
                "message": "Bạn cần đăng nhập quản trị."
            })

            return False

        return True

    # =====================================================
    # GET ROUTES
    # =====================================================

    def do_GET(self):
        cleanup_sessions()

        parsed = urlsplit(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        # -------------------- PAGES --------------------

        if path in (
            "/", "/index.html", "/dinh-vi", "/menu",
            "/proxy-mod-alen-crack", "/mizze-crack"
        ):
            visitor = self.get_cookie("ph_visitor")
            headers = {}

            if not valid_token(visitor):
                visitor = secrets.token_urlsafe(24)

                secure = (
                    "; Secure"
                    if SITE_URL.startswith("https://")
                    else ""
                )

                headers["Set-Cookie"] = (
                    "ph_visitor=" + visitor +
                    "; Path=/; Max-Age=31536000"
                    "; SameSite=Lax; HttpOnly" + secure
                )

            register_visit(
                visitor,
                self.headers.get("User-Agent", "")
            )

            self.send_html_with_cookie(HTML, headers)
            return

        if path == "/admin":
            self.send_html(ADMIN_HTML)
            return

        # -------------------- PUBLIC STATISTICS --------------------

        if path == "/stats":
            # Dùng request thống kê làm heartbeat để duy trì online.
            visitor = self.get_cookie("ph_visitor")

            if valid_token(visitor):
                register_visit(
                    visitor,
                    self.headers.get("User-Agent", "")
                )

            self.send_json(200, {
                "success": True,
                **get_statistics()
            })
            return

        # -------------------- PUBLIC SETTINGS --------------------

        if path == "/public-settings":
            self.send_json(200, {
                key: destination_enabled(key)
                for key in DEFAULT_DESTINATIONS
            })
            return

        # -------------------- CREATE SHORT LINK --------------------

        if path == "/create-short-link":
            ip = self.client_ip()

            if rate_limited(ip, 8):
                self.send_json(429, {
                    "success": False,
                    "message": "Bạn thao tác quá nhanh. Hãy thử lại sau."
                })
                return

            provider = query.get(
                "provider", ["link4m"]
            )[0].lower()

            destination = query.get(
                "destination", [""]
            )[0].lower()

            if provider != "link4m":
                self.send_json(400, {
                    "success": False,
                    "message": "PHONG WEB V2.2.2 chỉ hỗ trợ Link4M."
                })
                return

            if destination not in DEFAULT_DESTINATIONS:
                self.send_json(400, {
                    "success": False,
                    "message": "Mục đích vượt link không hợp lệ."
                })
                return

            if not destination_enabled(destination):
                self.send_json(403, {
                    "success": False,
                    "message": "Mục này hiện đang tạm khóa."
                })
                return

            if not SITE_URL.startswith("https://"):
                self.send_json(500, {
                    "success": False,
                    "message": "SITE_URL phải là HTTPS."
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
                SITE_URL + "/provider-return?token=" +
                quote(token, safe="")
            )

            try:
                shortened_url = create_link4m_url(callback_url)

                with LOCK:
                    SESSIONS[token] = {
                        "created": time.time(),
                        "returned": False,
                        "provider": "link4m",
                        "destination": destination
                    }

                print(
                    "[V2.2.2] LINK CREATED:",
                    destination
                )

                self.send_json(200, {
                    "success": True,
                    "url": shortened_url,
                    "provider": "link4m",
                    "destination": destination
                })

            except Exception as error:
                print(
                    "[LINK4M ERROR]",
                    str(error)[:300]
                )

                self.send_json(502, {
                    "success": False,
                    "message": str(error)[:220]
                })

            return

        # -------------------- LINK4M CALLBACK --------------------

        if path == "/provider-return":
            token = query.get("token", [""])[0]

            if not valid_token(token):
                self.redirect("/?result=failed")
                return

            destination = None

            with LOCK:
                session = SESSIONS.get(token)

                if (
                    session
                    and time.time() - session["created"] <= SESSION_TTL
                ):
                    session["returned"] = True
                    session["returned_at"] = time.time()

                    destination = session["destination"]

            if not destination:
                self.redirect("/?result=failed")
                return

            print(
                "[V2.2.2] CALLBACK:",
                destination
            )

            self.redirect(
                "/?result=thanks&destination=" +
                quote(destination, safe="") +
                "&token=" + quote(token, safe="")
            )

            return

        # -------------------- CHECK SESSION --------------------

        if path == "/check-session":
            token = query.get("token", [""])[0]

            session = get_session(token)

            if session and session.get("returned"):
                self.send_json(200, {
                    "success": True,
                    "returned": True,
                    "destination": session["destination"],
                    "provider": session["provider"],
                    "message": "Đã nhận callback từ Link4M."
                })

            else:
                self.send_json(403, {
                    "success": False,
                    "returned": False,
                    "message": "Phiên vượt link không hợp lệ hoặc đã hết hạn."
                })

            return

        # -------------------- DOWNLOAD --------------------

        download_routes = {
            route: key
            for key, route in DOWNLOAD_ROUTES.items()
        }

        if path in download_routes:
            destination = download_routes[path]

            token = query.get("token", [""])[0]

            if not destination_enabled(destination):
                self.send_json(403, {
                    "success": False,
                    "message": "Mục tải file hiện đang bị khóa."
                })
                return

            if not check_session(token, destination):
                self.send_json(403, {
                    "success": False,
                    "message": (
                        "Bạn chưa hoàn thành vượt link cho mục " +
                        DESTINATION_NAMES[destination] + "."
                    )
                })
                return

            target = setting(
                "url_" + destination,
                DEFAULT_DESTINATIONS[destination]
            )

            if not validate_mediafire_url(target):
                self.send_json(500, {
                    "success": False,
                    "message": "Đường dẫn MediaFire chưa hợp lệ."
                })
                return

            print(
                "[V2.2.2] DOWNLOAD:",
                destination
            )

            self.redirect(target)
            return

        # -------------------- ADMIN STATUS --------------------

        if path == "/admin/me":
            self.send_json(200, {
                "success": self.is_admin()
            })
            return

        # -------------------- ADMIN STATISTICS --------------------

        if path == "/admin/stats":
            if not self.require_admin():
                return

            self.send_json(200, {
                "success": True,
                **get_statistics()
            })

            return

        # -------------------- ADMIN SETTINGS --------------------

        if path == "/admin/settings":
            if not self.require_admin():
                return

            items = {}

            for key in DEFAULT_DESTINATIONS:
                items[key] = {
                    "name": DESTINATION_NAMES[key],
                    "enabled": destination_enabled(key),
                    "url": setting(
                        "url_" + key,
                        DEFAULT_DESTINATIONS[key]
                    )
                }

            self.send_json(200, {
                "success": True,
                "items": items
            })

            return

        # -------------------- STATIC FILES --------------------

        allowed = {
            "/logo.png",
            "/background.jpg",
            "/music.mp3",
            "/cam-on-tu-phong.png",
            "/cam-on-tu-phong.mp3"
        }

        if path in allowed:
            self.send_static_file(path)
            return

        # -------------------- LEGACY ROUTES --------------------

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
                "/provider-return?token=" +
                quote(token, safe="")
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

        self.send_json(404, {
            "success": False,
            "message": "Không tìm thấy đường dẫn."
        })

    # =====================================================
    # HTML WITH COOKIE
    # =====================================================

    def send_html_with_cookie(self, html, headers):
        data = html.encode("utf-8")

        self.send_response(200)

        self.send_header(
            "Content-Type",
            "text/html; charset=utf-8"
        )

        self.send_header(
            "Content-Length",
            str(len(data))
        )

        self.send_header("Cache-Control", "no-store")
        self.send_security_headers()

        for key, value in headers.items():
            self.send_header(key, value)

        self.end_headers()

        try:
            self.wfile.write(data)

        except (BrokenPipeError, ConnectionResetError):
            pass

    # =====================================================
    # STATIC FILES
    # =====================================================

    def send_static_file(self, path):
        allowed = {
            "/logo.png",
            "/background.jpg",
            "/music.mp3",
            "/cam-on-tu-phong.png",
            "/cam-on-tu-phong.mp3"
        }

        if path not in allowed:
            self.send_json(404, {
                "success": False
            })
            return

        file_path = BASE_DIR / path.lstrip("/")

        if not file_path.is_file():
            self.send_json(404, {
                "success": False,
                "message": "Không tìm thấy file tài nguyên."
            })
            return

        content_type = (
            mimetypes.guess_type(str(file_path))[0]
            or "application/octet-stream"
        )

        try:
            size = file_path.stat().st_size

            self.send_response(200)

            self.send_header(
                "Content-Type",
                content_type
            )

            self.send_header(
                "Content-Length",
                str(size)
            )

            self.send_header(
                "Cache-Control",
                "public, max-age=3600"
            )

            self.send_security_headers()
            self.end_headers()

            with open(file_path, "rb") as file:
                while True:
                    chunk = file.read(65536)

                    if not chunk:
                        break

                    self.wfile.write(chunk)

        except (
            BrokenPipeError,
            ConnectionResetError,
            OSError
        ) as error:

            print("[STATIC ERROR]", str(error))

    # =====================================================
    # POST ROUTES
    # =====================================================

    def do_POST(self):
        path = urlsplit(self.path).path

        data = self.read_json()

        if data is None:
            self.send_json(400, {
                "success": False,
                "message": "Dữ liệu gửi lên không hợp lệ."
            })
            return

        # -------------------- ADMIN LOGIN --------------------

        if path == "/admin/login":
            ip = self.client_ip()

            if rate_limited("admin:" + ip, 5):
                self.send_json(429, {
                    "success": False,
                    "message": "Quá nhiều lần đăng nhập. Hãy thử lại sau."
                })
                return

            password = data.get("password", "")

            if not isinstance(password, str) or not secrets.compare_digest(
                hash_text(password),
                hash_text(ADMIN_PASSWORD)
            ):
                self.send_json(401, {
                    "success": False,
                    "message": "Mật khẩu quản trị không chính xác."
                })
                return

            token = secrets.token_urlsafe(36)

            with LOCK:
                ADMIN_SESSIONS[token] = {
                    "created": time.time()
                }

            secure = (
                "; Secure"
                if SITE_URL.startswith("https://")
                else ""
            )

            self.send_json(200, {
                "success": True,
                "message": "Đăng nhập thành công."
            }, {
                "Set-Cookie": (
                    "ph_admin=" + token +
                    "; Path=/; HttpOnly; SameSite=Strict" +
                    "; Max-Age=" + str(ADMIN_TTL) + secure
                )
            })

            return

        # -------------------- ADMIN LOGOUT --------------------

        if path == "/admin/logout":
            token = self.admin_token()

            with LOCK:
                ADMIN_SESSIONS.pop(token, None)

            self.send_json(200, {
                "success": True,
                "message": "Đã đăng xuất."
            }, {
                "Set-Cookie": (
                    "ph_admin=; Path=/; HttpOnly; "
                    "SameSite=Strict; Max-Age=0"
                )
            })

            return

        # -------------------- ADMIN SAVE SETTINGS --------------------

        if path == "/admin/settings":
            if not self.require_admin():
                return

            items = data.get("items")

            if not isinstance(items, dict):
                self.send_json(400, {
                    "success": False,
                    "message": "Thiếu dữ liệu thiết lập."
                })
                return

            for key in DEFAULT_DESTINATIONS:
                item = items.get(key)

                if not isinstance(item, dict):
                    self.send_json(400, {
                        "success": False,
                        "message": "Thiếu cấu hình mục " + key
                    })
                    return

                url = item.get("url")
                enabled = item.get("enabled")

                if not validate_mediafire_url(url):
                    self.send_json(400, {
                        "success": False,
                        "message": (
                            "Link của " + DESTINATION_NAMES[key] +
                            " phải là đường dẫn MediaFire HTTPS hợp lệ."
                        )
                    })
                    return

                if not isinstance(enabled, bool):
                    self.send_json(400, {
                        "success": False,
                        "message": "Trạng thái bật/tắt không hợp lệ."
                    })
                    return

            with JSON_LOCK:
                stored = load_data_unlocked()

                for key in DEFAULT_DESTINATIONS:
                    item = items[key]

                    stored["settings"]["url_" + key] = (
                        item["url"].strip()
                    )

                    stored["settings"]["enabled_" + key] = (
                        "1" if item["enabled"] else "0"
                    )

                save_data_unlocked(stored)

            print("[V2.2.2] ADMIN UPDATED JSON SETTINGS")

            self.send_json(200, {
                "success": True,
                "message": "Đã lưu thiết lập thành công."
            })

            return

        self.send_json(404, {
            "success": False,
            "message": "Không tìm thấy API."
        })

    def log_message(self, fmt, *args):
        print(
            "[PHONG WEB V2.2.2]",
            fmt % args
        )


# =========================================================
# START SERVER
# =========================================================

if __name__ == "__main__":

    init_data()

    server = ThreadingHTTPServer(
        ("0.0.0.0", PORT),
        Website
    )

    server.daemon_threads = True

    print("======================================")
    print("       NGUYEN VAN PHONG WEBSITE")
    print("              V2.2.2")
    print("======================================")

    print("Port:", PORT)
    print("JSON:", DATA_FILE)

    print(
        "Link4M:",
        "ENABLED" if LINK4M_API_TOKEN else "MISSING API TOKEN"
    )

    print("Admin page: /admin")
    print("Admin password: Set by ADMIN_PASSWORD or default")

    print("Storage: JSON")
    print("SQLite: DISABLED")
    print("Persistent Disk: NOT REQUIRED")

    print("Statistics: ONLINE + TOTAL + ANDROID + IPHONE")
    print("Online timeout:", VISITOR_TIMEOUT, "seconds")
    print("Session TTL:", SESSION_TTL, "seconds")

    print("Clock: VIETNAM TIME + DAY ICON")

    print("Location: /dinh-vi")
    print("Deta: /menu")
    print("Proxy: /proxy-mod-alen-crack")
    print("Mizze: /mizze-crack")

    print("Callback: /provider-return")
    print("Session check: /check-session")
    print("Admin settings: /admin/settings")

    print("Providers: LINK4M ONLY")

    print("======================================")

    try:
        server.serve_forever()

    except KeyboardInterrupt:
        print("[PHONG WEB] Server stopped.")

    finally:
        server.server_close()