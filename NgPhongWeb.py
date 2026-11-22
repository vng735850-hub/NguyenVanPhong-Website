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
# PHONG WEB V2.7.1
# LINK4M ONLY | LOCATION + DETA + PROXY + MIZZE
# ADVANCED ADMIN | JSON ANALYTICS | SECURITY | CSRF
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
# Render đôi khi truyền PORT rỗng; dùng 5000 làm giá trị dự phòng.
_port_value = (os.environ.get("PORT") or "").strip()
try:
    PORT = int(_port_value) if _port_value else 5000
except (TypeError, ValueError):
    PORT = 5000

DATA_FILE = BASE_DIR / "data.json"

SITE_URL = os.environ.get(
    "SITE_URL", "https://nvp-com.onrender.com"
).strip().rstrip("/")

LINK4M_API_TOKEN = os.environ.get("LINK4M_API_TOKEN", "").strip()
LINK4M_ENDPOINT = "https://link4m.co/api-shorten/v2"

ADMIN_PASSWORD = os.environ.get("ADMIN_PASSWORD", "152012")

SESSION_TTL = 30 * 60
ADMIN_IDLE_TTL = 30 * 60
MAX_ADMIN_SESSIONS = 3
MAX_REQUEST_BODY = 2 * 1024 * 1024
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
ADMIN_WRITE_LIMITS = {}

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
    "admin_logs": [],
    "music_playlist": [
        {"name": "Nhạc nền", "src": "/music.mp3", "enabled": True},
        {"name": "Nhạc 1", "src": "/Nhac1.mp3", "enabled": True},
        {"name": "Nhạc 2", "src": "/Nhac2.mp3", "enabled": True}
    ],
    "music_volume": 0.7,
    "tags_custom": [],
    "content_items": []
}

for key, value in DEFAULT_DESTINATIONS.items():
    DEFAULT_DATA["settings"]["url_" + key] = value
    DEFAULT_DATA["settings"]["enabled_" + key] = "1"

DEFAULT_DATA["settings"]["site_name"] = "NGUYỄN VĂN PHONG WEBSITE"
for _tag in ("home", "freefire", "lienquan", "roblox"):
    DEFAULT_DATA["settings"]["tag_" + _tag] = "1"

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
    if not isinstance(data.get("tags_custom"), list):
        data["tags_custom"] = []
    if not isinstance(data.get("content_items"), list):
        data["content_items"] = []
    try:
        data["music_volume"] = max(0.0, min(1.0, float(data.get("music_volume", 0.7))))
    except (TypeError, ValueError):
        data["music_volume"] = 0.7
    if not isinstance(data.get("music_playlist"), list):
        data["music_playlist"] = [dict(x) for x in DEFAULT_DATA["music_playlist"]]
    playlist = []
    for track in data["music_playlist"][:50]:
        if isinstance(track, dict):
            name = safe_text(track.get("name", ""), 80)
            src = safe_text(track.get("src", ""), 500)
            if name and src:
                playlist.append({"name": name, "src": src, "enabled": track.get("enabled", True) is not False})
    data["music_playlist"] = playlist or [dict(x) for x in DEFAULT_DATA["music_playlist"]]

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

        for table in (RATE_LIMITS, API_RATE_LIMITS, ADMIN_WRITE_LIMITS):
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


de