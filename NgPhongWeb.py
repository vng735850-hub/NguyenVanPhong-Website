
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
from datetime import datetime, timedelta, timezone
from http.cookies import SimpleCookie
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlencode, urlsplit, quote, parse_qs

# =========================================================
# PHONG WEB V2.3.1
# LINK4M ONLY | LOCATION + DETA + PROXY + MIZZE
# ADVANCED ADMIN | JSON ANALYTICS | SECURITY | CSRF
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
PORT = int(os.environ.get("PORT", 5000))
DATA_FILE = BASE_DIR / "data.json"

SITE_URL = os.environ.get(
    "SITE_URL", "https://nvp-com.onrender.com"
).strip().rstrip("/")

LINK4M_API_TOKEN = os.environ.get("LINK4M_API_TOKEN", "").strip()
LINK4M_ENDPOINT = "https://link4m.co/api-shorten/v2"

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "152012")

SESSION_TTL = 30 * 60
VISITOR_TIMEOUT = 120
ADMIN_TTL = 8 * 60 * 60

MAX_HISTORY = 2000
MAX_LOGIN_ATTEMPTS = 5
MAX_LINK_REQUESTS = 8
MAX_API_REQUESTS = 20

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

DEFAULT_FILES = {
    "location": {
        "name": "DINH_VI_BT.zip",
        "size": "",
        "status": "available",
        "image": "/logo.png"
    },
    "deta": {
        "name": "Deta_Crack.7z",
        "size": "",
        "status": "available",
        "image": "/logo.png"
    },
    "proxy": {
        "name": "PROXY MOD ALEN Crack.zip",
        "size": "",
        "status": "available",
        "image": "/logo.png"
    },
    "mizze": {
        "name": "Menu Mizze Crack",
        "size": "",
        "status": "available",
        "image": "/logo.png"
    }
}

SESSIONS = {}
ADMIN_SESSIONS = {}
RATE_LIMITS = {}
API_RATE_LIMITS = {}

LOCK = threading.RLock()
JSON_LOCK = threading.RLock()

# =========================================================
# TIME
# =========================================================

def vietnam_now():
    return datetime.now(
        timezone(timedelta(hours=7))
    )


def vietnam_date():
    return vietnam_now().strftime("%Y-%m-%d")


def safe_count(value):
    try:
        return max(0, int(value))
    except (ValueError, TypeError, OverflowError):
        return 0


def safe_text(value, maximum=300):
    if not isinstance(value, str):
        return ""
    return value.strip()[:maximum]


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
        "iphone": 0,
        "success": 0,
        "failed": 0,
        "downloads": 0
    },
    "daily": {},
    "history": [],
    "files": {},
    "announcement": {
        "enabled": False,
        "message": ""
    },
    "maintenance": {
        "enabled": False,
        "message": "Website đang bảo trì. Vui lòng quay lại sau."
    },
    "admin_logs": []
}

for key, value in DEFAULT_DESTINATIONS.items():
    DEFAULT_DATA["settings"]["url_" + key] = value
    DEFAULT_DATA["settings"]["enabled_" + key] = "1"

for key, value in DEFAULT_FILES.items():
    DEFAULT_DATA["files"][key] = dict(value)


def save_data_unlocked(data):
    temp_file = DATA_FILE.with_suffix(".tmp")

    try:
        with open(temp_file, "w", encoding="utf-8") as file:
            json.dump(
                data,
                file,
                ensure_ascii=False,
                indent=2
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
    data = None

    try:
        if DATA_FILE.is_file():
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)

            if not isinstance(data, dict):
                raise ValueError("JSON không hợp lệ.")

    except (OSError, ValueError, json.JSONDecodeError) as error:
        print("[JSON WARNING]", str(error))
        data = None

    if not isinstance(data, dict):
        data = {}

    # Giữ dữ liệu cũ và bổ sung cấu trúc mới.
    for key in (
        "settings", "visitors", "visitor_devices",
        "stats", "daily", "files", "announcement",
        "maintenance"
    ):
        if not isinstance(data.get(key), dict):
            data[key] = {}

    if not isinstance(data.get("history"), list):
        data["history"] = []

    if not isinstance(data.get("admin_logs"), list):
        data["admin_logs"] = []

    for key, value in DEFAULT_DATA["settings"].items():
        data["settings"].setdefault(key, value)

    for key, value in DEFAULT_DATA["stats"].items():
        data["stats"][key] = safe_count(
            data["stats"].get(key, value)
        )

    for key, value in DEFAULT_DATA["files"].items():
        if not isinstance(data["files"].get(key), dict):
            data["files"][key] = dict(value)
        else:
            for field, default in value.items():
                data["files"][key].setdefault(field, default)

    for key, value in DEFAULT_DATA["announcement"].items():
        data["announcement"].setdefault(key, value)

    for key, value in DEFAULT_DATA["maintenance"].items():
        data["maintenance"].setdefault(key, value)

    data["history"] = data["history"][-MAX_HISTORY:]
    data["admin_logs"] = data["admin_logs"][-500:]

    return data


def load_data():
    with JSON_LOCK:
        return load_data_unlocked()


def save_data(data):
    with JSON_LOCK:
        save_data_unlocked(data)


def init_data():
    with JSON_LOCK:
        data = load_data_unlocked()
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
# SECURITY HELPERS
# =========================================================

def hash_text(value):
    return hashlib.sha256(
        str(value).encode("utf-8")
    ).hexdigest()


def valid_token(token):
    return (
        isinstance(token, str)
        and 30 <= len(token) <= 120
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


def validate_image_url(value):
    if not isinstance(value, str):
        return False

    value = value.strip()

    if value.startswith("/"):
        return value in (
            "/logo.png",
            "/background.jpg",
            "/cam-on-tu-phong.png"
        )

    if not validate_http_url(value):
        return False

    return urlsplit(value).scheme == "https"


def detect_device(user_agent):
    ua = str(user_agent or "").lower()

    if "iphone" in ua:
        return "iphone"

    if "android" in ua:
        return "android"

    return "other"


def cleanup_sessions():
    now = time.time()

    with LOCK:
        for token in list(SESSIONS):
            if now - SESSIONS[token]["created"] > SESSION_TTL:
                SESSIONS.pop(token, None)

        for token in list(ADMIN_SESSIONS):
            if now - ADMIN_SESSIONS[token]["created"] > ADMIN_TTL:
                ADMIN_SESSIONS.pop(token, None)

        for table in (RATE_LIMITS, API_RATE_LIMITS):
            for ip in list(table):
                table[ip] = [
                    t for t in table[ip] if now - t < 60
                ]
                if not table[ip]:
                    table.pop(ip, None)


def rate_limited(ip, limit=8, table=RATE_LIMITS):
    now = time.time()

    with LOCK:
        values = table.setdefault(ip, [])
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
# HISTORY + ANALYTICS
# =========================================================

def add_history(event, destination="", detail="", ip=""):
    record = {
        "time": vietnam_now().strftime("%Y-%m-%d %H:%M:%S"),
        "date": vietnam_date(),
        "event": safe_text(event, 40),
        "destination": safe_text(destination, 40),
        "name": DESTINATION_NAMES.get(destination, destination),
        "detail": safe_text(detail, 250),
        "ip": safe_text(ip, 80)
    }

    with JSON_LOCK:
        data = load_data_unlocked()
        data["history"].append(record)
        data["history"] = data["history"][-MAX_HISTORY:]
        save_data_unlocked(data)


def record_event_counter(event, destination="", detail="", ip=""):
    with JSON_LOCK:
        data = load_data_unlocked()

        if event == "success":
            data["stats"]["success"] += 1

        elif event == "failed":
            data["stats"]["failed"] += 1

        elif event == "download":
            data["stats"]["downloads"] += 1
            data["files"][destination]["downloads"] = (
                safe_count(
                    data["files"][destination].get("downloads", 0)
                ) + 1
            )

        data["history"].append({
            "time": vietnam_now().strftime("%Y-%m-%d %H:%M:%S"),
            "date": vietnam_date(),
            "event": event,
            "destination": destination,
            "name": DESTINATION_NAMES.get(destination, destination),
            "detail": safe_text(detail, 250),
            "ip": safe_text(ip, 80)
        })

        data["history"] = data["history"][-MAX_HISTORY:]
        save_data_unlocked(data)


def register_visit(visitor_id, user_agent=""):
    if not valid_token(visitor_id):
        return

    now = time.time()
    device = detect_device(user_agent)
    today = vietnam_date()

    with JSON_LOCK:
        data = load_data_unlocked()

        visitors = data["visitors"]
        visitor_devices = data["visitor_devices"]
        stats = data["stats"]

        if visitor_id not in visitor_devices:
            visitor_devices[visitor_id] = device
            stats["total"] += 1

            if device == "android":
                stats["android"] += 1
            elif device == "iphone":
                stats["iphone"] += 1

        expired = []

        for visitor, last_seen in visitors.items():
            try:
                if now - float(last_seen) > VISITOR_TIMEOUT:
                    expired.append(visitor)
            except (ValueError, TypeError):
                expired.append(visitor)

        for visitor in expired:
            visitors.pop(visitor, None)

        visitors[visitor_id] = now

        day = data["daily"].setdefault(
            today,
            {"visits": 0, "visitors": []}
        )

        if not isinstance(day, dict):
            day = {"visits": 0, "visitors": []}
            data["daily"][today] = day

        day_visitors = day.get("visitors", [])

        if not isinstance(day_visitors, list):
            day_visitors = []

        # Đếm lượt truy cập duy nhất mỗi ngày theo cookie.
        if visitor_id not in day_visitors:
            day_visitors.append(visitor_id)
            day["visits"] = safe_count(day.get("visits", 0)) + 1

        day["visitors"] = day_visitors[-10000:]

        data["visitors"] = visitors
        data["visitor_devices"] = visitor_devices
        data["stats"] = stats

        # Giữ dữ liệu thống kê tối đa 400 ngày.
        for date_key in sorted(data["daily"])[:-400]:
            data["daily"].pop(date_key, None)

        save_data_unlocked(data)


def get_statistics():
    now = time.time()

    with JSON_LOCK:
        data = load_data_unlocked()

        online = {}

        for visitor, last_seen in data["visitors"].items():
            try:
                if now - float(last_seen) <= VISITOR_TIMEOUT:
                    online[visitor] = last_seen
            except (ValueError, TypeError):
                continue

        data["visitors"] = online

        downloads = {
            key: safe_count(
                data["files"][key].get("downloads", 0)
            )
            for key in DEFAULT_DESTINATIONS
        }

        popular = max(
            downloads,
            key=downloads.get
        ) if downloads else ""

        result = {
            "online": len(online),
            "total": safe_count(data["stats"].get("total")),
            "android": safe_count(data["stats"].get("android")),
            "iphone": safe_count(data["stats"].get("iphone")),
            "success": safe_count(data["stats"].get("success")),
            "failed": safe_count(data["stats"].get("failed")),
            "downloads": safe_count(data["stats"].get("downloads")),
            "popular": popular,
            "popular_name": DESTINATION_NAMES.get(popular, "Chưa có dữ liệu")
        }

        save_data_unlocked(data)
        return result


def get_daily_statistics(days=7):
    days = 30 if days == 30 else 7

    with JSON_LOCK:
        data = load_data_unlocked()
        result = []

        for offset in range(days - 1, -1, -1):
            date_value = (
                vietnam_now() - timedelta(days=offset)
            ).strftime("%Y-%m-%d")

            item = data["daily"].get(
                date_value,
                {"visits": 0}
            )

            result.append({
                "date": date_value,
                "visits": safe_count(item.get("visits", 0))
            })

        return result


def get_file_settings():
    with JSON_LOCK:
        data = load_data_unlocked()
        result = {}

        for key in DEFAULT_DESTINATIONS:
            item = dict(data["files"].get(key, {}))
            item["downloads"] = safe_count(item.get("downloads", 0))
            result[key] = item

        return result


# =========================================================
# ADMIN LOGS
# =========================================================

def add_admin_log(action, ip="", detail=""):
    with JSON_LOCK:
        data = load_data_unlocked()

        data["admin_logs"].append({
            "time": vietnam_now().strftime("%Y-%m-%d %H:%M:%S"),
            "action": safe_text(action, 100),
            "ip": safe_text(ip, 80),
            "detail": safe_text(detail, 200)
        })

        data["admin_logs"] = data["admin_logs"][-500:]
        save_data_unlocked(data)


# =========================================================
# LINK4M API
# =========================================================

def api_request(url):
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Mozilla/5.0 PHONG-WEB/2.3",
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
        raise ValueError("Link4M không trả về JSON hợp lệ.")

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
        raise ValueError("Link4M trả về URL không hợp lệ.")

    return url


# =========================================================
# PUBLIC WEBSITE HTML
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
 overflow-x:hidden;transition:background .3s,color .3s
}
body.light{
 color:#10203c;
 background:linear-gradient(rgba(224,241,255,.9),rgba(235,247,255,.94)),
 url('/background.jpg') center/cover fixed no-repeat,#e8f4ff
}
body:before{
 content:"";position:fixed;inset:-50%;z-index:-2;pointer-events:none;
 background:
 radial-gradient(circle at 20% 30%,rgba(0,130,255,.2),transparent 28%),
 radial-gradient(circle at 80% 60%,rgba(0,210,255,.13),transparent 30%);
 animation:glowMove 13s ease-in-out infinite alternate
}
@keyframes glowMove{
 from{transform:translate(-3%,-2%) rotate(0deg)}
 to{transform:translate(3%,2%) rotate(8deg)}
}
#particles{
 position:fixed;inset:0;width:100%;height:100%;
 pointer-events:none;z-index:-1
}
header{
 position:relative;z-index:20;width:100%;min-height:75px;
 display:grid;grid-template-columns:43px minmax(0,1fr) 105px 42px;
 align-items:center;gap:8px;padding:10px 15px;
 background:rgba(4,10,30,.91);
 border-bottom:1px solid #299cff;
 box-shadow:0 0 22px rgba(0,130,255,.22)
}
body.light header{background:rgba(230,244,255,.95);color:#10203c}
.hamburger-button,.theme-button{
 width:43px;height:43px;border:1px solid #55baff;border-radius:10px;
 background:rgba(0,120,255,.2);color:inherit;font-size:23px;cursor:pointer
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
 display:none;position:absolute;top:67px;left:12px;width:220px;
 padding:9px;background:rgba(5,14,38,.98);
 border:1px solid #299cff;border-radius:12px;
 box-shadow:0 0 20px #073c70
}
.side-menu.show{display:block;animation:pageIn .2s ease}
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
body.light .subtitle{color:#274768}
.location-container,.menu-container{margin:18px auto}
.location-link{display:block;color:inherit;text-decoration:none}
.location-card{
 display:flex;align-items:center;justify-content:center;gap:20px;
 padding:22px 15px;background:rgba(10,27,60,.9);
 border:1px solid #459fff;border-radius:15px;
 box-shadow:0 0 18px rgba(0,130,255,.18);transition:.25s
}
body.light .location-card,body.light .menu-card,body.light .link-box{
 background:rgba(255,255,255,.9);color:#10203c
}
.location-card:hover,.menu-card:hover,.link-box:hover{
 transform:translateY(-3px);box-shadow:0 0 28px rgba(0,140,255,.4)
}
.location-emoji{font-size:43px}
.location-info{text-align:left}
.location-info h2{margin:0 0 9px;font-size:19px}
.location-info p{margin:0 0 12px;color:#c6e1ff;font-size:13px}
body.light .location-info p{color:#365979}
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
body.light .link-box h2{color:#0877c9}
.link-description{color:#d1e5ff;font-size:14px;line-height:1.8;margin:15px auto 22px}
body.light .link-description{color:#274768}
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
.music-mini{display:flex;justify-content:center;align-items:center;margin:25px auto 15px}
.music-control{
 display:flex;align-items:center;justify-content:center;gap:14px;
 min-width:190px;min-height:58px;padding:8px 17px;
 border:1px solid #62c5ff;border-radius:13px;
 background:linear-gradient(120deg,rgba(5,54,119,.96),rgba(4,126,210,.96));
 box-shadow:0 0 18px rgba(22,140,255,.35);
}
.music-bars{height:30px;display:flex;align-items:center;justify-content:center;gap:4px}
.music-bars span{
 display:block;width:4px;height:6px;border-radius:5px;
 background:#8ee7ff;box-shadow:0 0 8px #39caff;
 transform-origin:center;animation:none
}
.music-control.playing .music-bars span{animation:musicBeat .65s ease-in-out infinite alternate}
.music-control.playing .music-bars span:nth-child(1){animation-delay:-.48s}
.music-control.playing .music-bars span:nth-child(2){animation-delay:-.30s}
.music-control.playing .music-bars span:nth-child(3){animation-delay:-.12s}
.music-control.playing .music-bars span:nth-child(4){animation-delay:-.38s}
@keyframes musicBeat{
 0%{height:5px;opacity:.65}
 50%{height:19px;opacity:1}
 100%{height:29px;opacity:.8}
}
.music-toggle{
 min-width:112px;min-height:40px;padding:9px 14px;
 border:1px solid #9bdcff;border-radius:9px;
 color:white;background:linear-gradient(135deg,#0875df,#10aaf5);
 font-size:14px;font-weight:800;letter-spacing:.4px;
 cursor:pointer;box-shadow:0 0 12px rgba(40,170,255,.25);
 transition:transform .18s,filter .18s
}
.music-toggle:hover{filter:brightness(1.12);transform:translateY(-1px)}
.music-toggle:active{transform:scale(.97)}
.music-toggle:disabled{opacity:.65;cursor:wait}
.music-control.playing{box-shadow:0 0 24px rgba(30,190,255,.5)}
body.light .music-control{background:linear-gradient(120deg,#d7efff,#a7dcff)}
body.light .music-toggle{color:#fff}
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
 transition:.25s;font-size:14px;color:white
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
 border-radius:9px;background:rgba(4,20,48,.75);min-width:140px
}
.stats-bar b{color:#fff;font-size:14px}
.announcement{
 margin:15px auto;padding:13px;border:1px solid #50baff;
 border-radius:10px;background:rgba(0,100,220,.16);
 line-height:1.7
}
#loadingOverlay{
 position:fixed;inset:0;z-index:9999;background:rgba(2,8,25,.9);
 display:none;align-items:center;justify-content:center;flex-direction:column;
 color:white;text-align:center
}
#loadingOverlay.show{display:flex}
.spinner{
 width:55px;height:55px;border:5px solid rgba(255,255,255,.2);
 border-top-color:#29aaff;border-radius:50%;animation:spin .8s linear infinite;
 margin-bottom:17px
}
@keyframes spin{to{transform:rotate(360deg)}}
.maintenance{
 max-width:650px;margin:40px auto;padding:25px;
 border:1px solid #ffb84d;border-radius:16px;
 background:rgba(70,40,0,.45);line-height:1.8
}
@media(max-width:600px){
 header{grid-template-columns:40px minmax(0,1fr) 90px 38px;gap:5px;padding:8px;min-height:65px}
 .hamburger-button,.theme-button{width:38px;height:41px;font-size:20px}
 .header-title{font-size:clamp(10px,3vw,15px);letter-spacing:0}
 .clock-box{width:90px;height:41px;font-size:11px}
 .side-menu{top:60px}.location-card{gap:12px}
 .location-info h2{font-size:16px}
 .link-box{margin:22px auto;padding:23px 15px}
 .stats-bar span{flex:1 1 135px}
}
@media(prefers-reduced-motion:reduce){
 *,*:before,*:after{animation-duration:.01ms!important;transition-duration:.01ms!important}
}
</style>
</head>
<body>

<canvas id="particles"></canvas>
<div id="toast"></div>

<div id="loadingOverlay">
 <div class="spinner"></div>
 <b id="loadingText">Đang xử lý...</b>
</div>

<header>
 <button class="hamburger-button" id="hamburgerButton">☰</button>
 <div class="header-title">NGUYỄN VĂN PHONG WEBSITE</div>
 <div class="clock-box"><span id="liveClock">🌙 00:00:00</span></div>
 <button class="theme-button" id="themeButton" title="Đổi giao diện">☀️</button>
 <nav class="side-menu" id="sideMenu">
  <a href="/" id="homeMenuButton">🏠 TRANG CHỦ</a>
  <a href="/admin">⚙️ QUẢN TRỊ</a>
 </nav>
</header>

<main class="container">

<section class="page" id="homePage">
 <div id="maintenanceBox" class="maintenance hidden"></div>
 <div id="normalHome">
  <img class="hero-logo" src="/logo.png" alt="PHONG WEB">
  <h1>WELCOME TO PHONG WEB</h1>
  <div class="subtitle">
   Chào mừng bạn đến với website của Nguyễn Văn Phong.
   <br>📍 ĐỊNH VỊ XANH TÍM OB55
  </div>

  <div id="announcement" class="announcement hidden"></div>

  <div class="stats-bar">
   <span>🟢 Online: <b id="onlineCount">...</b></span>
   <span>👁 Tổng truy cập: <b id="totalCount">...</b></span>
   <span>🤖 Android: <b id="androidCount">...</b></span>
   <span>🍎 iPhone: <b id="iphoneCount">...</b></span>
  </div>

  <div class="stats-bar">
   <span>✅ Vượt link thành công: <b id="successCount">...</b></span>
   <span>❌ Vượt link thất bại: <b id="failedCount">...</b></span>
   <span>📥 Lượt lấy file: <b id="downloadCount">...</b></span>
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
 </div>
</section>

<section class="page" id="locationPage">
 <div class="link-box">
  <div class="link-icon">📍</div>
  <h2>BẠN CẦN VƯỢT LINK ĐỂ LẤY FILE MEDIAFIRE</h2>
  <div class="link-description" id="locationFileInfo"></div>
  <button class="cross-link-button" id="locationCrossButton">🔓 VƯỢT LINK</button>
  <div class="status" id="locationStatus"></div><br>
  <a class="back-button" href="/">← QUAY LẠI TRANG CHỦ</a>
 </div>
</section>

<section class="page" id="detaPage">
 <div class="link-box">
  <div class="link-icon">🔐</div>
  <h2>BẠN CẦN VƯỢT LINK ĐỂ LẤY FILE DETA</h2>
  <div class="link-description" id="detaFileInfo"></div>
  <button class="cross-link-button" id="detaCrossButton">🔓 VƯỢT LINK</button>
  <div class="status" id="detaStatus"></div><br>
  <a class="back-button" href="/">← QUAY LẠI TRANG CHỦ</a>
 </div>
</section>

<section class="page" id="proxyPage">
 <div class="link-box">
  <div class="link-icon">🌐</div>
  <h2>BẠN CẦN VƯỢT LINK ĐỂ LẤY FILE PROXY MOD ALEN CRACK</h2>
  <div class="link-description" id="proxyFileInfo"></div>
  <button class="cross-link-button" id="proxyCrossButton">🔓 VƯỢT LINK</button>
  <div class="status" id="proxyStatus"></div><br>
  <a class="back-button" href="/">← QUAY LẠI TRANG CHỦ</a>
 </div>
</section>

<section class="page" id="mizzePage">
 <div class="link-box">
  <div class="link-icon">🎮</div>
  <h2>BẠN CẦN VƯỢT LINK ĐỂ LẤY FILE MENU MIZZE CRACK</h2>
  <div class="link-description" id="mizzeFileInfo"></div>
  <button class="cross-link-button" id="mizzeCrossButton">🔓 VƯỢT LINK</button>
  <div class="status" id="mizzeStatus"></div><br>
  <a class="back-button" href="/">← QUAY LẠI TRANG CHỦ</a>
 </div>
</section>

<section class="page" id="thankPage">
 <div class="link-box">
  <div class="link-icon">💙</div>
  <h2>Cảm Ơn Vì Đã Ủng Hộ Cho Phong</h2>
  <div class="link-description">
   Phong chân thành cảm ơn bạn đã dành thời gian ủng hộ website.
   <br>Nhấn vào hình bên dưới để nghe lời cảm ơn nhé!
  </div>
  <button class="thank-image-button" id="thankAudioButton">
   <img src="/cam-on-tu-phong.png" alt="Cảm Ơn Từ Phong">
  </button>
  <div class="status" id="thankStatus">🔊 Nhấn vào ảnh để phát âm thanh cảm ơn.</div>
  <button class="cross-link-button" id="continueButton">TIẾP THEO →</button>
  <audio id="thankAudio" src="/cam-on-tu-phong.mp3" preload="none"></audio>
 </div>
</section>

<section class="page" id="resultPage">
 <div class="link-box">
  <div class="link-icon" id="resultIcon">✅</div>
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
 <div class="music-control" id="musicControl">
  <div class="music-bars" aria-hidden="true">
   <span></span><span></span><span></span><span></span>
  </div>
  <button class="music-toggle" id="musicButton" type="button"
          aria-label="Bật nhạc" aria-pressed="false">
   <span id="musicIcon">▶</span>
   <span id="musicLabel"> BẬT NHẠC</span>
  </button>
 </div>
</div>

<audio id="backgroundMusic" src="/music.mp3" preload="none"
       loop playsinline></audio>

<footer>
 © 2026 Nguyễn Văn Phong Website<br>
 <strong>PHONG WEB V2.3.1</strong>
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
 location:"/dinh-vi",deta:"/menu",
 proxy:"/proxy-mod-alen-crack",mizze:"/mizze-crack"
};

const downloadRoutes={
 location:"/download-location",deta:"/download-deta",
 proxy:"/download-proxy",mizze:"/download-mizze"
};

function toast(message,type="good"){
 const el=document.getElementById("toast");
 el.textContent=message;
 el.className="show "+(type==="bad"?"bad":"good");
 clearTimeout(window.toastTimer);
 window.toastTimer=setTimeout(()=>el.className="",3800);
}

function loading(show,message="Đang xử lý..."){
 document.getElementById("loadingText").textContent=message;
 document.getElementById("loadingOverlay").classList.toggle("show",show);
}

// Theme sáng/tối.
const themeButton=document.getElementById("themeButton");
function applyTheme(theme){
 document.body.classList.toggle("light",theme==="light");
 themeButton.textContent=theme==="light"?"🌙":"☀️";
 try{localStorage.setItem("phong_theme",theme)}catch(e){}
}
let savedTheme="dark";
try{savedTheme=localStorage.getItem("phong_theme")||"dark"}catch(e){}
applyTheme(savedTheme);
themeButton.addEventListener("click",()=>{
 applyTheme(document.body.classList.contains("light")?"dark":"light");
});

// Nền hạt ánh sáng xanh.
(function(){
 const canvas=document.getElementById("particles");
 const ctx=canvas.getContext("2d");
 let w=0,h=0,particles=[];
 function resize(){
  w=canvas.width=window.innerWidth;
  h=canvas.height=window.innerHeight;
  const count=Math.min(65,Math.floor(w*h/18000));
  particles=Array.from({length:count},()=>({
   x:Math.random()*w,y:Math.random()*h,
   r:Math.random()*2+0.5,
   vx:(Math.random()-.5)*.35,
   vy:(Math.random()-.5)*.35
  }));
 }
 function draw(){
  ctx.clearRect(0,0,w,h);
  for(const p of particles){
   p.x+=p.vx;p.y+=p.vy;
   if(p.x<0||p.x>w)p.vx*=-1;
   if(p.y<0||p.y>h)p.vy*=-1;
   ctx.beginPath();
   ctx.arc(p.x,p.y,p.r,0,Math.PI*2);
   ctx.fillStyle="rgba(70,175,255,.65)";
   ctx.fill();
  }
  requestAnimationFrame(draw);
 }
 resize();draw();
 window.addEventListener("resize",resize);
})();

// Đồng hồ Việt Nam.
function updateClock(){
 const parts=new Intl.DateTimeFormat("en-GB",{
  timeZone:"Asia/Ho_Chi_Minh",
  hour:"2-digit",minute:"2-digit",second:"2-digit",
  hourCycle:"h23"
 }).formatToParts(new Date());

 const values={};
 parts.forEach(p=>values[p.type]=p.value);

 const hour=Number(values.hour);
 let icon="🌙";
 if(hour>=6&&hour<13)icon="🌅";
 else if(hour>=13&&hour<19)icon="☀️";

 document.getElementById("liveClock").textContent=
  icon+" "+values.hour+":"+values.minute+":"+values.second;
}
updateClock();
setInterval(updateClock,1000);

// Chuyển trang.
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
  pages.thank.classList.add("active");return;
 }
 if(result==="success"||result==="failed"){
  pages.result.classList.add("active");checkResult();return;
 }

 const routes={
  "/":pages.home,"/index.html":pages.home,
  "/dinh-vi":pages.location,"/menu":pages.deta,
  "/proxy-mod-alen-crack":pages.proxy,
  "/mizze-crack":pages.mizze
 };
 (routes[location.pathname]||pages.home).classList.add("active");
}
window.addEventListener("popstate",showPage);

// Thống kê.
async function refreshStats(){
 try{
  const r=await fetch("/stats",{cache:"no-store"});
  const d=await r.json();
  if(!r.ok||!d.success)return;

  const fields={
   online:"onlineCount",total:"totalCount",
   android:"androidCount",iphone:"iphoneCount",
   success:"successCount",failed:"failedCount",
   downloads:"downloadCount"
  };
  for(const [key,id] of Object.entries(fields)){
   const el=document.getElementById(id);
   if(el)el.textContent=Number(d[key]||0).toLocaleString("vi-VN");
  }
 }catch(e){}
}
setInterval(refreshStats,15000);
refreshStats();

// Cài đặt và thông báo công khai.
async function refreshPublic(){
 try{
  const r=await fetch("/public-settings",{cache:"no-store"});
  const d=await r.json();

  for(const key of ["location","deta","proxy","mizze"]){
   const card=document.getElementById("card-"+key);
   if(card)card.style.display=d[key]?"":"none";

   const info=document.getElementById(key+"FileInfo");
   const file=d.files&&d.files[key];

   if(info&&file){
    info.textContent=
     "Tên file: "+(file.name||"Chưa cập nhật")+
     (file.size?" | Dung lượng: "+file.size:"")+
     " | Trạng thái: "+(file.status==="available"?"Sẵn sàng":"Tạm ngưng");
   }
  }

  const announcement=document.getElementById("announcement");
  if(d.announcement&&d.announcement.enabled&&d.announcement.message){
   announcement.textContent=d.announcement.message;
   announcement.classList.remove("hidden");
  }

  if(d.maintenance&&d.maintenance.enabled){
   document.getElementById("normalHome").classList.add("hidden");
   const box=document.getElementById("maintenanceBox");
   box.textContent=d.maintenance.message||"Website đang bảo trì.";
   box.classList.remove("hidden");
  }
 }catch(e){}
}
refreshPublic();

// Tạo link.
async function createShortLink(destination,button,status){
 button.disabled=true;
 const oldText=button.textContent;
 button.textContent="ĐANG XỬ LÝ...";
 status.className="status";
 status.textContent="Đang kết nối API LINK4M...";
 loading(true,"Đang tạo liên kết vượt...");

 try{
  const response=await fetch(
   "/create-short-link?destination="+encodeURIComponent(destination),
   {cache:"no-store"}
  );
  const data=await response.json();

  if(!response.ok||!data.success){
   throw new Error(data.message||"Không thể tạo link.");
  }
  if(!data.url)throw new Error("Link4M không trả về URL.");

  status.className="status success";
  status.textContent="Tạo link thành công! Đang chuyển đến Link4M...";
  toast("Tạo link thành công!","good");
  window.location.href=data.url;

 }catch(error){
  status.className="status error";
  status.textContent="LỖI: "+error.message;
  toast("Tạo link thất bại: "+error.message,"bad");
  button.disabled=false;
  button.textContent="🔓 THỬ LẠI";
 }finally{
  loading(false);
  if(!button.disabled)button.textContent=oldText;
 }
}
function setupCrossButton(key){
 const button=document.getElementById(key+"CrossButton");
 const status=document.getElementById(key+"Status");
 button.addEventListener("click",()=>createShortLink(key,button,status));
}
["location","deta","proxy","mizze"].forEach(setupCrossButton);

// Âm thanh cảm ơn.
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
 document.getElementById("thankStatus").textContent="💙 Cảm ơn bạn đã lắng nghe!";
});

// Xác nhận phiên.
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
 loading(true,"Đang xác nhận phiên vượt link...");

 try{
  const r=await fetch("/check-session?token="+encodeURIComponent(token),{
   cache:"no-store"
  });
  const d=await r.json();

  if(!r.ok||!d.success||!d.returned){
   throw new Error(d.message||"Phiên chưa được xác nhận.");
  }
  if(d.destination!==destination){
   throw new Error("Thông tin mục vượt link không khớp.");
  }

  history.pushState({},"",
   "/?result=success&destination="+encodeURIComponent(destination)+
   "&token="+encodeURIComponent(token)
  );
  showPage();
  window.scrollTo(0,0);
 }catch(e){
  showFailure(e.message,destination);
 }finally{
  loading(false);
  button.disabled=false;
  button.textContent="TIẾP THEO →";
 }
});

function showFailure(message,destination){
 hideAllPages();
 pages.result.classList.add("active");
 document.getElementById("resultIcon").textContent="❌";
 document.getElementById("resultTitle").textContent="Vượt Link Không Thành Công";
 document.getElementById("resultDescription").textContent=
  "Phiên vượt link chưa được xác nhận hoặc đã hết hạn.";

 const status=document.getElementById("resultStatus");
 status.className="status error";
 status.textContent=message||"Vui lòng thử vượt link mới.";

 document.getElementById("resultAction").classList.add("hidden");
 const retry=document.getElementById("retryButton");
 retry.classList.remove("hidden");
 retry.onclick=()=>navigate(destinationRoutes[destination]||"/");
}

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
 document.getElementById("resultTitle").textContent="ĐANG KIỂM TRA";
 document.getElementById("resultDescription").textContent=
  "Đang kiểm tra phiên quay lại từ Link4M...";

 try{
  const r=await fetch("/check-session?token="+encodeURIComponent(token),{
   cache:"no-store"
  });
  const d=await r.json();

  if(!r.ok||!d.success||!d.returned){
   throw new Error(d.message||"Phiên không hợp lệ.");
  }
  if(d.destination!==destination){
   throw new Error("Thông tin mục vượt link không khớp.");
  }

  document.getElementById("resultIcon").textContent="✅";
  document.getElementById("resultTitle").textContent="Vượt Link Thành Công";
  document.getElementById("resultDescription").textContent=
   "Bạn đã quay lại PHONG WEB. Nhấn LẤY FILE để mở MediaFire.";

  const status=document.getElementById("resultStatus");
  status.className="status success";
  status.textContent="Đã xác nhận phiên Link4M.";

  action.href=downloadRoutes[destination]+"?token="+encodeURIComponent(token);
  action.classList.remove("hidden");
 }catch(e){
  showFailure(e.message,destination);
 }
}

// Menu.
const hamburger=document.getElementById("hamburgerButton");
const menu=document.getElementById("sideMenu");
hamburger.addEventListener("click",e=>{
 e.stopPropagation();menu.classList.toggle("show");
});
document.getElementById("homeMenuButton").addEventListener("click",e=>{
 e.preventDefault();menu.classList.remove("show");navigate("/");
});
document.addEventListener("click",e=>{
 if(!menu.contains(e.target)&&!hamburger.contains(e.target)){
  menu.classList.remove("show");
 }
});

// Nhạc nền V2.3.1: nút chữ nhật + 4 thanh nhịp + lặp lại bài nhạc.
const music=document.getElementById("backgroundMusic");
const musicButton=document.getElementById("musicButton");
const musicControl=document.getElementById("musicControl");
const musicIcon=document.getElementById("musicIcon");
const musicLabel=document.getElementById("musicLabel");

music.loop=true;

function updateMusicUI(isPlaying){
 musicControl.classList.toggle("playing",isPlaying);
 musicIcon.textContent=isPlaying?"Ⅱ":"▶";
 musicLabel.textContent=isPlaying?" TẮT NHẠC":" BẬT NHẠC";
 musicButton.setAttribute("aria-label",isPlaying?"Tắt nhạc":"Bật nhạc");
 musicButton.setAttribute("aria-pressed",isPlaying?"true":"false");
}

music.addEventListener("play",()=>updateMusicUI(true));
music.addEventListener("pause",()=>updateMusicUI(false));
music.addEventListener("ended",()=>{
 // Bảo đảm phát lại từ đầu nếu trình duyệt không tự xử lý loop.
 if(music.loop){
  music.currentTime=0;
  music.play().catch(()=>updateMusicUI(false));
 }
});
music.addEventListener("error",()=>{
 updateMusicUI(false);
 toast("Không tải được /music.mp3. Hãy kiểm tra file music.mp3 nằm cùng thư mục app.py.","bad");
});

musicButton.addEventListener("click",async()=>{
 if(musicButton.disabled)return;

 if(!music.paused){
  music.pause();
  updateMusicUI(false);
  return;
 }

 musicButton.disabled=true;
 musicLabel.textContent=" ĐANG TẢI...";
 try{
  // Gọi play trực tiếp từ thao tác chạm/click để tương thích chính sách mobile.
  await music.play();
  updateMusicUI(true);
 }catch(error){
  updateMusicUI(false);
  let message="Không thể phát nhạc.";
  if(error&&error.name==="NotAllowedError"){
   message="Trình duyệt chặn phát nhạc. Hãy chạm nút BẬT NHẠC lần nữa.";
  }else if(error&&error.name==="NotSupportedError"){
   message="File music.mp3 không đúng định dạng hoặc không được hỗ trợ.";
  }else if(!navigator.onLine){
   message="Thiết bị đang ngoại tuyến, không tải được nhạc.";
  }else{
   message="Không phát được nhạc. Kiểm tra file music.mp3 và thử tải lại trang.";
  }
  toast(message,"bad");
 }finally{
  musicButton.disabled=false;
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
<title>PHONG WEB V2.3.1 ADMIN</title>
<style>
*{box-sizing:border-box}
body{margin:0;padding:15px;background:#071022;color:white;font-family:Arial,sans-serif}
main{max-width:1050px;margin:20px auto}
.panel{margin:15px 0;padding:18px;background:#0d1d3a;border:1px solid #299cff;border-radius:14px;box-shadow:0 0 18px #073c70}
h1,h2,h3{color:#70c5ff}
input,select,textarea{
 width:100%;padding:11px;margin:7px 0;border-radius:8px;
 border:1px solid #398ddd;background:#07152d;color:white
}
textarea{min-height:85px;resize:vertical}
button{
 padding:11px 16px;border:0;border-radius:8px;color:white;
 background:#087ce5;font-weight:bold;cursor:pointer;margin:4px 3px
}
button.danger{background:#b52c42}
button.good{background:#078653}
button.warning{background:#a56b08}
label{display:block;margin:10px 0}
.small{color:#b9d7f7;font-size:13px;line-height:1.7}
.hidden{display:none!important}
.row{display:flex;gap:10px;flex-wrap:wrap;align-items:center}
.row>*{flex:1}
#message{margin:12px 0;color:#74ffc0;overflow-wrap:anywhere}
a{color:#7bcaff}
.grid{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px}
.stat-card{padding:14px;background:#07152d;border:1px solid #398ddd;border-radius:10px;line-height:1.8}
.stat-card b{display:block;color:#fff;font-size:25px}
.stat-card span{color:#b9d7f7;font-size:13px}
.tabs{display:flex;flex-wrap:wrap;gap:6px;margin:15px 0}
.tabs button{background:#18375e}
.tabs button.active{background:#087ce5}
.table-wrap{overflow-x:auto}
table{border-collapse:collapse;width:100%;min-width:650px;font-size:13px}
td,th{padding:9px;border-bottom:1px solid #29466b;text-align:left}
th{color:#80caff}
canvas.chart{width:100%;height:230px;background:#07152d;border-radius:10px}
.item{padding:12px;margin:10px 0;border:1px solid #285b91;border-radius:10px}
@media(max-width:650px){
 body{padding:8px}.grid{grid-template-columns:repeat(2,minmax(0,1fr))}
 .panel{padding:12px}
}
@media(max-width:390px){.grid{grid-template-columns:1fr}}
</style>
</head>
<body>
<main>
<h1>⚙️ PHONG WEB V2.3.1 - ADMIN</h1>
<p class="small">Quản lý website, thống kê, lịch sử và bảo mật.</p>

<section class="panel" id="loginPanel">
<h2>🔐 ĐĂNG NHẬP QUẢN TRỊ</h2>
<input id="password" type="password" placeholder="Nhập mật khẩu quản trị">
<button onclick="login()">ĐĂNG NHẬP</button>
<div id="loginMessage" class="small"></div>
</section>

<div id="dashboard" class="hidden">
<div class="tabs">
 <button class="active" onclick="tab('overview',this)">📊 Tổng quan</button>
 <button onclick="tab('files',this)">📁 Quản lý file</button>
 <button onclick="tab('history',this)">📜 Lịch sử</button>
 <button onclick="tab('notice',this)">📢 Thông báo</button>
 <button onclick="tab('security',this)">🔐 Bảo mật</button>
</div>

<section class="tabpage" id="overview">
 <div class="panel">
  <h2>📊 THỐNG KÊ WEBSITE</h2>
  <div class="grid">
   <div class="stat-card">🟢 Online<b id="online">...</b><span>Đang truy cập</span></div>
   <div class="stat-card">👁 Tổng truy cập<b id="total">...</b><span>Khách duy nhất</span></div>
   <div class="stat-card">🤖 Android<b id="android">...</b><span>Thiết bị Android</span></div>
   <div class="stat-card">🍎 iPhone<b id="iphone">...</b><span>Thiết bị iPhone</span></div>
   <div class="stat-card">✅ Thành công<b id="success">...</b><span>Vượt link</span></div>
   <div class="stat-card">❌ Thất bại<b id="failed">...</b><span>Vượt link</span></div>
   <div class="stat-card">📥 Lượt lấy file<b id="downloads">...</b><span>Tổng cộng</span></div>
   <div class="stat-card">🏆 Phổ biến<b id="popular">...</b><span>Mục được lấy nhiều</span></div>
  </div>
  <button onclick="loadStats()">LÀM MỚI</button>
 </div>

 <div class="panel">
  <h2>📈 BIỂU ĐỒ LƯỢT TRUY CẬP</h2>
  <select id="chartDays" onchange="loadChart()">
   <option value="7">7 ngày gần nhất</option>
   <option value="30">30 ngày gần nhất</option>
  </select>
  <canvas id="chart" class="chart" width="900" height="260"></canvas>
 </div>
</section>

<section class="tabpage hidden" id="files">
 <div class="panel">
  <h2>🗂️ QUẢN LÝ CÁC MỤC TẢI FILE</h2>
  <p class="small">Bật/tắt, sửa link MediaFire và cập nhật thông tin file.</p>
  <div id="items"></div>
  <button class="good" onclick="saveSettings()">LƯU THAY ĐỔI</button>
 </div>
</section>

<section class="tabpage hidden" id="history">
 <div class="panel">
  <h2>📜 LỊCH SỬ HOẠT ĐỘNG</h2>
  <div class="row">
   <input id="historySearch" placeholder="Tìm theo IP, tên mục, nội dung...">
   <select id="historyEvent">
    <option value="">Tất cả sự kiện</option>
    <option value="success">Vượt link thành công</option>
    <option value="failed">Vượt link thất bại</option>
    <option value="download">Lấy file</option>
    <option value="create">Tạo link</option>
   </select>
   <button onclick="loadHistory()">TÌM KIẾM</button>
  </div>
  <div class="table-wrap">
   <table>
    <thead><tr><th>Thời gian</th><th>Sự kiện</th><th>Mục</th><th>Chi tiết</th><th>IP</th></tr></thead>
    <tbody id="historyRows"></tbody>
   </table>
  </div>
 </div>
</section>

<section class="tabpage hidden" id="notice">
 <div class="panel">
  <h2>📢 THÔNG BÁO TRANG CHỦ</h2>
  <label><input type="checkbox" id="announcementEnabled"> Hiển thị thông báo</label>
  <textarea id="announcementMessage" placeholder="Nội dung thông báo..."></textarea>
  <button class="good" onclick="saveAnnouncement()">LƯU THÔNG BÁO</button>
 </div>
 <div class="panel">
  <h2>🛠️ CHẾ ĐỘ BẢO TRÌ</h2>
  <label><input type="checkbox" id="maintenanceEnabled"> Bật chế độ bảo trì</label>
  <textarea id="maintenanceMessage" placeholder="Thông báo bảo trì..."></textarea>
  <button class="warning" onclick="saveMaintenance()">LƯU BẢO TRÌ</button>
 </div>
</section>

<section class="tabpage hidden" id="security">
 <div class="panel">
  <h2>🔑 ĐỔI MẬT KHẨU ADMIN</h2>
  <input type="password" id="oldPassword" placeholder="Mật khẩu hiện tại">
  <input type="password" id="newPassword" placeholder="Mật khẩu mới (ít nhất 8 ký tự)">
  <input type="password" id="confirmPassword" placeholder="Nhập lại mật khẩu mới">
  <button class="good" onclick="changePassword()">ĐỔI MẬT KHẨU</button>
 </div>
 <div class="panel">
  <h2>🧹 QUẢN LÝ DỮ LIỆU THỐNG KÊ</h2>
  <p class="small">Xóa lịch sử và bộ đếm thống kê. Thao tác này không xóa URL hoặc cấu hình file.</p>
  <button class="danger" onclick="resetStats()">XÓA DỮ LIỆU THỐNG KÊ</button>
 </div>
 <div class="panel">
  <h2>🔐 NHẬT KÝ ĐĂNG NHẬP ADMIN</h2>
  <div class="table-wrap">
   <table><thead><tr><th>Thời gian</th><th>Hoạt động</th><th>IP</th><th>Chi tiết</th></tr></thead>
   <tbody id="adminLogRows"></tbody></table>
  </div>
  <button onclick="loadAdminLogs()">LÀM MỚI NHẬT KÝ</button>
 </div>
 <div class="panel">
  <h2>⏱️ PHIÊN QUẢN TRỊ</h2>
  <p class="small">Phiên đăng nhập hết hạn sau 8 giờ. Trình duyệt tự kiểm tra trạng thái đăng nhập.</p>
  <button class="danger" onclick="logout()">ĐĂNG XUẤT</button>
 </div>
</section>
</div>

<div id="message"></div>
<p><a href="/">← Quay lại website</a></p>
</main>

<script>
let config={};
let csrfToken="";
let adminTimer=null;

function message(text,bad=false){
 const el=document.getElementById("message");
 el.textContent=text;
 el.style.color=bad?"#ff8585":"#74ffc0";
}

function tab(name,button){
 document.querySelectorAll(".tabpage").forEach(x=>x.classList.add("hidden"));
 document.getElementById(name).classList.remove("hidden");
 document.querySelectorAll(".tabs button").forEach(x=>x.classList.remove("active"));
 button.classList.add("active");
}

async function api(path,body,method){
 const options={method:method||(body?"POST":"GET"),headers:{}};

 if(body){
  options.headers["Content-Type"]="application/json";
  options.headers["X-CSRF-Token"]=csrfToken;
  options.body=JSON.stringify(body);
 }

 const r=await fetch(path,options);
 const d=await r.json();

 if(r.status===401){
  logoutLocal();
  throw new Error("Phiên quản trị hết hạn. Vui lòng đăng nhập lại.");
 }
 if(!r.ok||!d.success){
  throw new Error(d.message||"Có lỗi xảy ra.");
 }
 return d;
}

async function login(){
 const msg=document.getElementById("loginMessage");
 try{
  const r=await fetch("/admin/login",{
   method:"POST",
   headers:{"Content-Type":"application/json"},
   body:JSON.stringify({password:document.getElementById("password").value})
  });
  const d=await r.json();
  if(!r.ok||!d.success)throw new Error(d.message||"Đăng nhập thất bại.");

  await startDashboard();
 }catch(e){
  msg.textContent=e.message;
 }
}

async function startDashboard(){
 const d=await api("/admin/csrf");
 csrfToken=d.csrf;
 document.getElementById("loginPanel").classList.add("hidden");
 document.getElementById("dashboard").classList.remove("hidden");
 await loadAll();

 clearInterval(adminTimer);
 adminTimer=setInterval(async()=>{
  try{await api("/admin/me");}
  catch(e){logoutLocal();}
 },60000);
}

function logoutLocal(){
 clearInterval(adminTimer);
 csrfToken="";
 document.getElementById("dashboard").classList.add("hidden");
 document.getElementById("loginPanel").classList.remove("hidden");
}

async function loadAll(){
 await Promise.all([
  loadStats(),loadSettings(),loadNotice(),
  loadHistory(),loadAdminLogs(),loadChart()
 ]);
}

async function loadStats(){
 const d=await api("/admin/stats");
 for(const key of ["online","total","android","iphone","success","failed","downloads"]){
  document.getElementById(key).textContent=
   Number(d[key]||0).toLocaleString("vi-VN");
 }
 document.getElementById("popular").textContent=d.popular_name||"Chưa có dữ liệu";
}

async function loadChart(){
 const days=Number(document.getElementById("chartDays").value||7);
 const d=await api("/admin/daily?days="+days,null,"GET");
 drawChart(d.items||[]);
}

function drawChart(items){
 const canvas=document.getElementById("chart");
 const ctx=canvas.getContext("2d");
 const w=canvas.width,h=canvas.height;
 ctx.clearRect(0,0,w,h);

 const max=Math.max(1,...items.map(x=>Number(x.visits||0)));
 const left=45,right=15,top=20,bottom=45;
 const graphW=w-left-right,graphH=h-top-bottom;

 ctx.strokeStyle="#29466b";
 ctx.fillStyle="#b9d7f7";
 ctx.font="12px Arial";

 for(let i=0;i<=4;i++){
  const y=top+graphH*i/4;
  ctx.beginPath();ctx.moveTo(left,y);ctx.lineTo(w-right,y);ctx.stroke();
  ctx.fillText(String(Math.round(max*(4-i)/4)),5,y+4);
 }

 const step=graphW/Math.max(1,items.length);
 ctx.strokeStyle="#27aaff";ctx.lineWidth=3;ctx.beginPath();

 items.forEach((item,i)=>{
  const x=left+step*(i+.5);
  const y=top+graphH-(Number(item.visits||0)/max)*graphH;
  if(i===0)ctx.moveTo(x,y);else ctx.lineTo(x,y);
  ctx.fillStyle="#8bd5ff";
  ctx.fillText(String(item.visits||0),x-7,y-9);
  if(items.length<=10||i%5===0||i===items.length-1){
   ctx.fillText(String(item.date||"").slice(5),x-17,h-17);
  }
 });
 ctx.stroke();
}

async function loadSettings(){
 const d=await api("/admin/settings");
 config=d.items;
 const files=d.files||{};
 const root=document.getElementById("items");
 root.innerHTML="";

 for(const [key,item] of Object.entries(config)){
  const file=files[key]||{};
  const box=document.createElement("div");
  box.className="item";

  const title=document.createElement("h3");
  title.textContent=item.name;

  const enabled=document.createElement("input");
  enabled.type="checkbox";
  enabled.checked=item.enabled;
  enabled.id="enabled-"+key;

  const label=document.createElement("label");
  label.textContent="Hiển thị mục này";
  label.prepend(enabled);

  const url=document.createElement("input");
  url.type="url";url.id="url-"+key;
  url.value=item.url;url.placeholder="https://www.mediafire.com/...";

  const fileName=document.createElement("input");
  fileName.id="file-name-"+key;
  fileName.value=file.name||"";
  fileName.placeholder="Tên file";

  const size=document.createElement("input");
  size.id="file-size-"+key;
  size.value=file.size||"";
  size.placeholder="Dung lượng (nếu biết, ví dụ 25 MB)";

  const status=document.createElement("select");
  status.id="file-status-"+key;
  for(const [value,text] of [["available","Sẵn sàng"],["unavailable","Tạm ngưng"]]){
   const option=document.createElement("option");
   option.value=value;option.textContent=text;
   status.append(option);
  }
  status.value=file.status||"available";

  const image=document.createElement("input");
  image.id="file-image-"+key;
  image.value=file.image||"/logo.png";
  image.placeholder="Ảnh đại diện: /logo.png hoặc URL HTTPS";

  box.append(title,label);
  const l1=document.createElement("label");l1.textContent="Link MediaFire";l1.append(url);
  const l2=document.createElement("label");l2.textContent="Tên file";l2.append(fileName);
  const l3=document.createElement("label");l3.textContent="Dung lượng";l3.append(size);
  const l4=document.createElement("label");l4.textContent="Trạng thái";l4.append(status);
  const l5=document.createElement("label");l5.textContent="Ảnh đại diện";l5.append(image);

  box.append(l1,l2,l3,l4,l5);
  const count=document.createElement("p");
  count.className="small";
  count.textContent="Lượt lấy file: "+Number(file.downloads||0);
  box.append(count);
  root.append(box);
 }
}

async function saveSettings(){
 try{
  const items={},files={};

  for(const key of Object.keys(config)){
   items[key]={
    enabled:document.getElementById("enabled-"+key).checked,
    url:document.getElementById("url-"+key).value.trim()
   };
   files[key]={
    name:document.getElementById("file-name-"+key).value.trim(),
    size:document.getElementById("file-size-"+key).value.trim(),
    status:document.getElementById("file-status-"+key).value,
    image:document.getElementById("file-image-"+key).value.trim()
   };
  }

  await api("/admin/settings",{items,files});
  message("Đã lưu thiết lập và thông tin file.");
  await loadSettings();
 }catch(e){message(e.message,true);}
}

async function loadHistory(){
 try{
  const search=encodeURIComponent(document.getElementById("historySearch").value||"");
  const event=encodeURIComponent(document.getElementById("historyEvent").value||"");
  const d=await api("/admin/history?q="+search+"&event="+event,null,"GET");
  const root=document.getElementById("historyRows");
  root.innerHTML="";

  for(const item of d.items||[]){
   const tr=document.createElement("tr");
   for(const value of [item.time,item.event,item.name,item.detail,item.ip]){
    const td=document.createElement("td");
    td.textContent=value||"";
    tr.append(td);
   }
   root.append(tr);
  }
 }catch(e){message(e.message,true);}
}

async function loadNotice(){
 const d=await api("/admin/notice");
 document.getElementById("announcementEnabled").checked=d.announcement.enabled;
 document.getElementById("announcementMessage").value=d.announcement.message||"";
 document.getElementById("maintenanceEnabled").checked=d.maintenance.enabled;
 document.getElementById("maintenanceMessage").value=d.maintenance.message||"";
}

async function saveAnnouncement(){
 try{
  await api("/admin/notice",{
   announcement:{
    enabled:document.getElementById("announcementEnabled").checked,
    message:document.getElementById("announcementMessage").value
   }
  });
  message("Đã cập nhật thông báo trang chủ.");
 }catch(e){message(e.message,true);}
}

async function saveMaintenance(){
 try{
  await api("/admin/notice",{
   maintenance:{
    enabled:document.getElementById("maintenanceEnabled").checked,
    message:document.getElementById("maintenanceMessage").value
   }
  });
  message("Đã cập nhật chế độ bảo trì.");
 }catch(e){message(e.message,true);}
}

async function changePassword(){
 try{
  const oldPassword=document.getElementById("oldPassword").value;
  const newPassword=document.getElementById("newPassword").value;
  const confirmPassword=document.getElementById("confirmPassword").value;

  if(newPassword.length<8)throw new Error("Mật khẩu mới cần ít nhất 8 ký tự.");
  if(newPassword!==confirmPassword)throw new Error("Hai mật khẩu mới không khớp.");

  await api("/admin/change-password",{oldPassword,newPassword});
  message("Đổi mật khẩu thành công. Phiên hiện tại sẽ kết thúc.");
  setTimeout(logout,1200);
 }catch(e){message(e.message,true);}
}

async function resetStats(){
 if(!confirm("Bạn chắc chắn muốn xóa dữ liệu thống kê và lịch sử?"))return;
 try{
  await api("/admin/reset-stats",{confirm:true});
  message("Đã xóa dữ liệu thống kê.");
  await loadAll();
 }catch(e){message(e.message,true);}
}

async function loadAdminLogs(){
 try{
  const d=await api("/admin/logs");
  const root=document.getElementById("adminLogRows");
  root.innerHTML="";
  for(const item of d.items||[]){
   const tr=document.createElement("tr");
   for(const value of [item.time,item.action,item.ip,item.detail]){
    const td=document.createElement("td");td.textContent=value||"";tr.append(td);
   }
   root.append(tr);
  }
 }catch(e){message(e.message,true);}
}

async function logout(){
 try{await api("/admin/logout",{});}catch(e){}
 logoutLocal();
 location.reload();
}

async function checkAdmin(){
 try{
  const d=await api("/admin/me");
  if(d.success)await startDashboard();
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

    server_version = "PhongWeb/2.3.1"
    sys_version = ""

    def client_ip(self):
        # Không tin X-Forwarded-For do client có thể tự giả mạo.
        # Khi chạy sau proxy, đây có thể là IP của proxy.
        return self.client_address[0]

    def send_security_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header(
            "Referrer-Policy",
            "strict-origin-when-cross-origin"
        )
        self.send_header(
            "Permissions-Policy",
            "camera=(), microphone=(), geolocation=()"
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
        self.send_header("Content-Length", str(len(content)))
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
        self.send_header("Content-Length", str(len(data)))
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
            length = int(self.headers.get("Content-Length", "0"))
        except ValueError:
            return None

        if length <= 0 or length > 20000:
            return None

        try:
            raw = self.rfile.read(length)
            value = json.loads(raw.decode("utf-8"))
            return value if isinstance(value, dict) else None
        except (ValueError, UnicodeDecodeError):
            return None

    def get_cookie(self, name):
        cookie = SimpleCookie()

        try:
            cookie.load(self.headers.get("Cookie", ""))
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

            session["last_seen"] = time.time()
            return True

    def require_admin(self):
        if not self.is_admin():
            self.send_json(401, {
                "success": False,
                "message": "Phiên quản trị hết hạn. Vui lòng đăng nhập lại."
            })
            return False

        return True

    def require_csrf(self):
        if not self.require_admin():
            return False

        token = self.admin_token()
        supplied = self.headers.get("X-CSRF-Token", "")

        with LOCK:
            session = ADMIN_SESSIONS.get(token)
            expected = session.get("csrf", "") if session else ""

        if (
            not supplied
            or not expected
            or not secrets.compare_digest(supplied, expected)
        ):
            self.send_json(403, {
                "success": False,
                "message": "CSRF token không hợp lệ. Hãy tải lại trang Admin."
            })
            return False

        return True

    def send_html_with_cookie(self, html, headers):
        data = html.encode("utf-8")

        self.send_response(200)
        self.send_header(
            "Content-Type",
            "text/html; charset=utf-8"
        )
        self.send_header("Content-Length", str(len(data)))
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
    # GET ROUTES
    # =====================================================

    def do_GET(self):
        cleanup_sessions()

        parsed = urlsplit(self.path)
        path = parsed.path
        query = parse_qs(parsed.query)

        # Public pages.
        if path in (
            "/", "/index.html", "/dinh-vi", "/menu",
            "/proxy-mod-alen-crack", "/mizze-crack"
        ):
            visitor = self.get_cookie("ph_visitor")
            headers = {}

            if not valid_token(visitor):
                visitor = secrets.token_urlsafe(24)
                secure = "; Secure" if SITE_URL.startswith("https://") else ""

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

        # Heartbeat + statistics.
        if path == "/stats":
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

        # Public settings.
        if path == "/public-settings":
            data = load_data()
            files = get_file_settings()

            self.send_json(200, {
                **{
                    key: destination_enabled(key)
                    for key in DEFAULT_DESTINATIONS
                },
                "files": files,
                "announcement": data["announcement"],
                "maintenance": data["maintenance"]
            })
            return

        # Create short link.
        if path == "/create-short-link":
            ip = self.client_ip()

            if rate_limited(ip, MAX_LINK_REQUESTS):
                self.send_json(429, {
                    "success": False,
                    "message": "Bạn thao tác quá nhanh. Hãy thử lại sau."
                })
                return

            if rate_limited(ip, MAX_API_REQUESTS, API_RATE_LIMITS):
                self.send_json(429, {
                    "success": False,
                    "message": "Bạn đã đạt giới hạn yêu cầu API."
                })
                return

            provider = query.get("provider", ["link4m"])[0].lower()
            destination = query.get("destination", [""])[0].lower()

            if provider != "link4m":
                self.send_json(400, {
                    "success": False,
                    "message": "PHONG WEB V2.3.1 chỉ hỗ trợ Link4M."
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

            file_info = get_file_settings().get(destination, {})

            if file_info.get("status") != "available":
                self.send_json(403, {
                    "success": False,
                    "message": "File hiện đang tạm ngưng."
                })
                return

            data = load_data()

            if data["maintenance"].get("enabled"):
                self.send_json(503, {
                    "success": False,
                    "message": data["maintenance"].get(
                        "message", "Website đang bảo trì."
                    )
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
                        "success_counted": False,
                        "provider": "link4m",
                        "destination": destination
                    }

                add_history(
                    "create", destination,
                    "Đã tạo liên kết Link4M", ip
                )

                print("[V2.3.1] LINK CREATED:", destination)

                self.send_json(200, {
                    "success": True,
                    "url": shortened_url,
                    "provider": "link4m",
                    "destination": destination
                })

            except Exception as error:
                record_event_counter(
                    "failed", destination,
                    "Lỗi tạo link: " + str(error)[:150], ip
                )

                print("[LINK4M ERROR]", str(error)[:300])

                self.send_json(502, {
                    "success": False,
                    "message": str(error)[:220]
                })

            return

        # Link4M callback.
        if path == "/provider-return":
            token = query.get("token", [""])[0]

            if not valid_token(token):
                self.redirect("/?result=failed")
                return

            destination = None
            should_count = False

            with LOCK:
                session = SESSIONS.get(token)

                if (
                    session
                    and time.time() - session["created"] <= SESSION_TTL
                    and session.get("provider") == "link4m"
                ):
                    destination = session.get("destination")

                    if not session.get("returned"):
                        session["returned"] = True
                        session["returned_at"] = time.time()

                    if not session.get("success_counted"):
                        session["success_counted"] = True
                        should_count = True

            if not destination:
                self.redirect("/?result=failed")
                return

            if should_count:
                record_event_counter(
                    "success", destination,
                    "Callback Link4M được tiếp nhận", self.client_ip()
                )

            print("[V2.3.1] CALLBACK:", destination)

            self.redirect(
                "/?result=thanks&destination=" +
                quote(destination, safe="") +
                "&token=" + quote(token, safe="")
            )
            return

        # Check session.
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

        # Download routes.
        download_routes = {
            route: key for key, route in DOWNLOAD_ROUTES.items()
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

            file_info = get_file_settings().get(destination, {})

            if file_info.get("status") != "available":
                self.send_json(403, {
                    "success": False,
                    "message": "File hiện đang tạm ngưng."
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

            record_event_counter(
                "download", destination,
                "Người dùng nhấn LẤY FILE", self.client_ip()
            )

            print("[V2.3.1] DOWNLOAD:", destination)
            self.redirect(target)
            return

        # Admin status.
        if path == "/admin/me":
            self.send_json(200, {
                "success": self.is_admin()
            })
            return

        # Admin CSRF token.
        if path == "/admin/csrf":
            if not self.require_admin():
                return

            token = self.admin_token()

            with LOCK:
                session = ADMIN_SESSIONS.get(token)
                csrf = session.get("csrf", "") if session else ""

            self.send_json(200, {
                "success": True,
                "csrf": csrf
            })
            return

        # Admin stats.
        if path == "/admin/stats":
            if not self.require_admin():
                return

            self.send_json(200, {
                "success": True,
                **get_statistics()
            })
            return

        # Admin daily chart.
        if path == "/admin/daily":
            if not self.require_admin():
                return

            days = safe_count(query.get("days", ["7"])[0])
            self.send_json(200, {
                "success": True,
                "items": get_daily_statistics(days)
            })
            return

        # Admin settings.
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
                "items": items,
                "files": get_file_settings()
            })
            return

        # Admin history with search and event filter.
        if path == "/admin/history":
            if not self.require_admin():
                return

            search = safe_text(query.get("q", [""])[0], 100).lower()
            event = safe_text(query.get("event", [""])[0], 40)

            with JSON_LOCK:
                data = load_data_unlocked()
                records = list(reversed(data["history"]))

            filtered = []

            for item in records:
                if event and item.get("event") != event:
                    continue

                searchable = " ".join([
                    str(item.get("time", "")),
                    str(item.get("event", "")),
                    str(item.get("name", "")),
                    str(item.get("detail", "")),
                    str(item.get("ip", ""))
                ]).lower()

                if search and search not in searchable:
                    continue

                filtered.append(item)

                if len(filtered) >= 300:
                    break

            self.send_json(200, {
                "success": True,
                "items": filtered
            })
            return

        # Admin announcement and maintenance settings.
        if path == "/admin/notice":
            if not self.require_admin():
                return

            data = load_data()

            self.send_json(200, {
                "success": True,
                "announcement": data["announcement"],
                "maintenance": data["maintenance"]
            })
            return

        # Admin login logs.
        if path == "/admin/logs":
            if not self.require_admin():
                return

            with JSON_LOCK:
                data = load_data_unlocked()
                logs = list(reversed(data["admin_logs"]))

            self.send_json(200, {
                "success": True,
                "items": logs[:200]
            })
            return

        # Static files.
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

        # Legacy routes.
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

        self.send_json(404, {
            "success": False,
            "message": "Không tìm thấy đường dẫn."
        })

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
            self.send_json(404, {"success": False})
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
            range_header = self.headers.get("Range", "")
            start = 0
            end = size - 1
            status = 200

            # Hỗ trợ HTTP Range để trình duyệt điện thoại tải/seek MP3 ổn định.
            if path.endswith(".mp3") and range_header.startswith("bytes="):
                try:
                    requested = range_header[6:].split(",", 1)[0].strip()
                    left, right = requested.split("-", 1)

                    if left:
                        start = int(left)
                        end = int(right) if right else size - 1
                    elif right:
                        suffix_length = int(right)
                        if suffix_length <= 0:
                            raise ValueError("Range suffix không hợp lệ.")
                        start = max(0, size - suffix_length)
                        end = size - 1
                    else:
                        raise ValueError("Range không hợp lệ.")

                    if start < 0 or start >= size or end < start:
                        self.send_response(416)
                        self.send_header("Content-Range", "bytes */" + str(size))
                        self.send_header("Accept-Ranges", "bytes")
                        self.send_header("Content-Length", "0")
                        self.send_security_headers()
                        self.end_headers()
                        return

                    end = min(end, size - 1)
                    status = 206

                except (ValueError, TypeError):
                    self.send_response(416)
                    self.send_header("Content-Range", "bytes */" + str(size))
                    self.send_header("Accept-Ranges", "bytes")
                    self.send_header("Content-Length", "0")
                    self.send_security_headers()
                    self.end_headers()
                    return

            length = max(0, end - start + 1)
            self.send_response(status)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(length))
            self.send_header("Accept-Ranges", "bytes")
            self.send_header("Cache-Control", "public, max-age=3600")
            if status == 206:
                self.send_header(
                    "Content-Range",
                    f"bytes {start}-{end}/{size}"
                )
            self.send_security_headers()
            self.end_headers()

            with open(file_path, "rb") as file:
                file.seek(start)
                remaining = length
                while remaining > 0:
                    chunk = file.read(min(65536, remaining))
                    if not chunk:
                        break
                    self.wfile.write(chunk)
                    remaining -= len(chunk)

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

        # Admin login.
        if path == "/admin/login":
            ip = self.client_ip()

            if rate_limited("admin:" + ip, MAX_LOGIN_ATTEMPTS):
                add_admin_log("LOGIN_BLOCKED", ip, "Quá nhiều lần đăng nhập")
                self.send_json(429, {
                    "success": False,
                    "message": "Quá nhiều lần đăng nhập. Hãy thử lại sau."
                })
                return

            password = data.get("password", "")

            if (
                not isinstance(password, str)
                or not secrets.compare_digest(
                    hash_text(password),
                    hash_text(ADMIN_PASSWORD)
                )
            ):
                add_admin_log("LOGIN_FAILED", ip, "Sai mật khẩu")
                self.send_json(401, {
                    "success": False,
                    "message": "Mật khẩu quản trị không chính xác."
                })
                return

            token = secrets.token_urlsafe(36)
            csrf = secrets.token_urlsafe(32)

            with LOCK:
                ADMIN_SESSIONS[token] = {
                    "created": time.time(),
                    "last_seen": time.time(),
                    "csrf": csrf
                }

            secure = "; Secure" if SITE_URL.startswith("https://") else ""

            add_admin_log("LOGIN_SUCCESS", ip, "Đăng nhập thành công")

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

        # All following admin write actions require CSRF.
        if path.startswith("/admin/") and path != "/admin/login":
            if not self.require_csrf():
                return

        # Admin logout.
        if path == "/admin/logout":
            token = self.admin_token()

            with LOCK:
                ADMIN_SESSIONS.pop(token, None)

            add_admin_log("LOGOUT", self.client_ip(), "Đăng xuất")

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

        # Save destinations and file metadata.
        if path == "/admin/settings":
            items = data.get("items")
            files = data.get("files", {})

            if not isinstance(items, dict) or not isinstance(files, dict):
                self.send_json(400, {
                    "success": False,
                    "message": "Thiếu dữ liệu thiết lập."
                })
                return

            for key in DEFAULT_DESTINATIONS:
                item = items.get(key)
                file_info = files.get(key, {})

                if not isinstance(item, dict) or not isinstance(file_info, dict):
                    self.send_json(400, {
                        "success": False,
                        "message": "Thiếu cấu hình mục " + key
                    })
                    return

                if not validate_mediafire_url(item.get("url")):
                    self.send_json(400, {
                        "success": False,
                        "message": (
                            "Link của " + DESTINATION_NAMES[key] +
                            " phải là MediaFire HTTPS hợp lệ."
                        )
                    })
                    return

                if not isinstance(item.get("enabled"), bool):
                    self.send_json(400, {
                        "success": False,
                        "message": "Trạng thái bật/tắt không hợp lệ."
                    })
                    return

                if file_info.get("status", "available") not in (
                    "available", "unavailable"
                ):
                    self.send_json(400, {
                        "success": False,
                        "message": "Trạng thái file không hợp lệ."
                    })
                    return

                if not validate_image_url(
                    file_info.get("image", "/logo.png")
                ):
                    self.send_json(400, {
                        "success": False,
                        "message": "Ảnh đại diện phải là URL HTTPS hoặc ảnh nội bộ cho phép."
                    })
                    return

                if len(safe_text(file_info.get("name", ""), 120)) > 120:
                    self.send_json(400, {
                        "success": False,
                        "message": "Tên file quá dài."
                    })
                    return

            with JSON_LOCK:
                stored = load_data_unlocked()

                for key in DEFAULT_DESTINATIONS:
                    item = items[key]
                    file_info = files.get(key, {})

                    stored["settings"]["url_" + key] = item["url"].strip()
                    stored["settings"]["enabled_" + key] = (
                        "1" if item["enabled"] else "0"
                    )

                    old_downloads = safe_count(
                        stored["files"][key].get("downloads", 0)
                    )

                    stored["files"][key] = {
                        "name": safe_text(file_info.get("name"), 120),
                        "size": safe_text(file_info.get("size"), 40),
                        "status": file_info.get("status", "available"),
                        "image": file_info.get("image", "/logo.png").strip(),
                        "downloads": old_downloads
                    }

                save_data_unlocked(stored)

            add_admin_log(
                "UPDATE_SETTINGS",
                self.client_ip(),
                "Cập nhật cấu hình mục tải file"
            )

            print("[V2.3.1] ADMIN UPDATED SETTINGS")

            self.send_json(200, {
                "success": True,
                "message": "Đã lưu thiết lập thành công."
            })
            return

        # Update announcements and maintenance.
        if path == "/admin/notice":
            announcement = data.get("announcement")
            maintenance = data.get("maintenance")

            if not isinstance(announcement, dict) or not isinstance(maintenance, dict):
                self.send_json(400, {
                    "success": False,
                    "message": "Dữ liệu thông báo không hợp lệ."
                })
                return

            if not isinstance(announcement.get("enabled"), bool):
                self.send_json(400, {
                    "success": False,
                    "message": "Trạng thái thông báo không hợp lệ."
                })
                return

            if not isinstance(maintenance.get("enabled"), bool):
                self.send_json(400, {
                    "success": False,
                    "message": "Trạng thái bảo trì không hợp lệ."
                })
                return

            with JSON_LOCK:
                stored = load_data_unlocked()

                stored["announcement"] = {
                    "enabled": announcement["enabled"],
                    "message": safe_text(
                        announcement.get("message", ""), 1000
                    )
                }

                stored["maintenance"] = {
                    "enabled": maintenance["enabled"],
                    "message": safe_text(
                        maintenance.get("message", ""), 1000
                    ) or "Website đang bảo trì. Vui lòng quay lại sau."
                }

                save_data_unlocked(stored)

            add_admin_log(
                "UPDATE_NOTICE",
                self.client_ip(),
                "Cập nhật thông báo/bảo trì"
            )

            self.send_json(200, {
                "success": True,
                "message": "Đã cập nhật thông báo."
            })
            return

        # Change admin password.
        if path == "/admin/change-password":
            old_password = data.get("oldPassword", "")
            new_password = data.get("newPassword", "")

            if not isinstance(old_password, str) or not isinstance(new_password, str):
                self.send_json(400, {
                    "success": False,
                    "message": "Mật khẩu không hợp lệ."
                })
                return

            if not secrets.compare_digest(
                hash_text(old_password),
                hash_text(ADMIN_PASSWORD)
            ):
                self.send_json(403, {
                    "success": False,
                    "message": "Mật khẩu hiện tại không chính xác."
                })
                return

            if len(new_password) < 8 or len(new_password) > 200:
                self.send_json(400, {
                    "success": False,
                    "message": "Mật khẩu mới phải có từ 8 đến 200 ký tự."
                })
                return

            self.send_json(400, {
                "success": False,
                "message": (
                    "Không thể thay đổi biến môi trường trực tiếp. "
                    "Hãy cập nhật ADMIN_PASSWORD trên Render rồi khởi động lại."
                )
            })
            return

        # Reset statistics.
        if path == "/admin/reset-stats":
            if data.get("confirm") is not True:
                self.send_json(400, {
                    "success": False,
                    "message": "Thiếu xác nhận xóa dữ liệu."
                })
                return

            with JSON_LOCK:
                stored = load_data_unlocked()

                stored["stats"] = {
                    "total": 0,
                    "android": 0,
                    "iphone": 0,
                    "success": 0,
                    "failed": 0,
                    "downloads": 0
                }

                stored["daily"] = {}
                stored["history"] = []
                stored["visitors"] = {}
                stored["visitor_devices"] = {}

                for key in DEFAULT_DESTINATIONS:
                    stored["files"][key]["downloads"] = 0

                save_data_unlocked(stored)

            add_admin_log(
                "RESET_STATISTICS",
                self.client_ip(),
                "Đã xóa dữ liệu thống kê"
            )

            self.send_json(200, {
                "success": True,
                "message": "Đã xóa dữ liệu thống kê."
            })
            return

        self.send_json(404, {
            "success": False,
            "message": "Không tìm thấy API."
        })

    def log_message(self, fmt, *args):
        print("[PHONG WEB V2.3.1]", fmt % args)


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
    print("              V2.3.1")
    print("======================================")

    print("Port:", PORT)
    print("JSON:", DATA_FILE)

    print(
        "Link4M:",
        "ENABLED" if LINK4M_API_TOKEN else "MISSING API TOKEN"
    )

    print("Admin page: /admin")
    print("Admin password: Set by ADMIN_PASSWORD")
    print("Storage: JSON")
    print("SQLite: DISABLED")

    print("Statistics: ONLINE + TOTAL + DEVICES")
    print("Link success/failure counters: ENABLED")
    print("Daily statistics: 7 DAYS / 30 DAYS")
    print("History: SEARCH + FILTER")
    print("File management: ENABLED")
    print("Announcement + Maintenance: ENABLED")
    print("Admin CSRF: ENABLED")
    print("Admin login logs: ENABLED")
    print("Theme: LIGHT / DARK")
    print("Animated particles: ENABLED")

    print("Online timeout:", VISITOR_TIMEOUT, "seconds")
    print("Session TTL:", SESSION_TTL, "seconds")
    print("Admin TTL:", ADMIN_TTL, "seconds")

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