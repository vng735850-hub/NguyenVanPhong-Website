import os
import json
import time
import secrets
import hashlib
import tempfile
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
# PHONG WEB V2.8.2
# LINK4M ONLY | LOCATION + DETA + PROXY + MIZZE + DETA QUOC TE
# ADVANCED ADMIN | JSON ANALYTICS | SECURITY | CSRF
# V2.8.2: NỀN ĐEN/TRẮNG + MAP LIÊN QUÂN NOKEY + NÚT QUAY LẠI
# =========================================================

BASE_DIR = Path(__file__).resolve().parent
# Render đôi khi truyền PORT rỗng; dùng 5000 làm giá trị dự phòng.
_port_value = (os.environ.get("PORT") or "").strip()
try:
    PORT = int(_port_value) if _port_value else 5000
except (TypeError, ValueError):
    PORT = 5000



def _pick_data_file():
    # V2.7.1: tránh sập khi thư mục code không ghi được (deploy).
    # Thứ tự: DATA_DIR (nếu có) -> thư mục code -> thư mục tạm.
    candidates = []
    env_dir = (os.environ.get("DATA_DIR") or "").strip()
    if env_dir:
        candidates.append(Path(env_dir))
    candidates.append(BASE_DIR)
    candidates.append(Path(tempfile.gettempdir()))

    for folder in candidates:
        try:
            folder.mkdir(parents=True, exist_ok=True)
            probe = folder / ".write_test"
            probe.write_text("ok", encoding="utf-8")
            probe.unlink()
            return folder / "data.json"
        except OSError:
            continue

    return BASE_DIR / "data.json"


DATA_FILE = _pick_data_file()

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

# V2.8.0: link mặc định của 2 mục mới (Admin có thể đổi trong tab quản lý file).
NVPKEY_LINK = "https://zufile.com/f/2vRmNkma5C"
YSM_LINK = "https://www.mediafire.com/file/x9xo2468orsfr3l/YSM_TEAM_LIEN_QUAN.apk/file"

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

# V2.8.0: bổ sung 2 mục Liên Quân mà không đổi cấu trúc cũ.
DEFAULT_DESTINATIONS["nvpkey"] = NVPKEY_LINK
DEFAULT_DESTINATIONS["ysm"] = YSM_LINK
DESTINATION_NAMES["nvpkey"] = "Menu Nvp Crack Key"
DESTINATION_NAMES["ysm"] = "Menu YSM Team Liên Quân"
DESTINATION_ROUTES["nvpkey"] = "/menu-nvp-crack-key"
DESTINATION_ROUTES["ysm"] = "/menu-ysm-team-lien-quan"
DOWNLOAD_ROUTES["nvpkey"] = "/download-nvpkey"
DOWNLOAD_ROUTES["ysm"] = "/download-ysm"
DEFAULT_FILES["nvpkey"] = {
    "name": "Menu Nvp Crack Key",
    "size": "",
    "status": "available",
    "image": "/logo.png"
}
DEFAULT_FILES["ysm"] = {
    "name": "YSM_TEAM_LIEN_QUAN.apk",
    "size": "",
    "status": "available",
    "image": "/logo.png"
}

# V2.8.1: Deta Quốc Tế (Hack Roblox) - dùng đúng luồng vượt link của mục Định Vị.
DETAQT_MEDIAFIRE_LINK = (
    "https://www.mediafire.com/file/"
    "i52c3sjorqv5soo/Delta+V2.747+Quoc+Te.apk/file"
)
DEFAULT_DESTINATIONS["detaqt"] = DETAQT_MEDIAFIRE_LINK
DESTINATION_NAMES["detaqt"] = "Deta Quốc Tế"
DESTINATION_ROUTES["detaqt"] = "/deta-quoc-te"
DOWNLOAD_ROUTES["detaqt"] = "/download-detaqt"
DEFAULT_FILES["detaqt"] = {
    "name": "Delta V2.747 Quoc Te.apk",
    "size": "",
    "status": "available",
    "image": "/logo.png"
}

# V2.8.2: Map Liên Quân NoKey - dùng đúng luồng vượt link của mục Định Vị.
MAPLQ_LINK = "https://zufile.com/f/2DolZWoWOd"
DEFAULT_DESTINATIONS["maplq"] = MAPLQ_LINK
DESTINATION_NAMES["maplq"] = "Map Liên Quân NoKey"
DESTINATION_ROUTES["maplq"] = "/map-lien-quan-nokey"
DOWNLOAD_ROUTES["maplq"] = "/download-maplq"
DEFAULT_FILES["maplq"] = {
    "name": "Map Liên Quân NoKey",
    "size": "",
    "status": "available",
    "image": "/logo.png"
}

# V2.8.1: Tag gốc và Mục gốc có thể đổi tên / đổi Tag / xóa (ẩn) / khôi phục trong Quản Trị.
BASE_TAG_DEFAULTS = {
    "freefire": {"name": "HACK FREE FIRE", "icon": "🔥"},
    "lienquan": {"name": "HACK LIÊN QUÂN", "icon": "⚔️"},
    "roblox": {"name": "HACK ROBLOX", "icon": "🧱"}
}

BASE_ITEM_DEFAULTS = {
    "location": {"name": "Định Vị Xanh Tím OB55", "icon": "📍", "description": "Mở mục định vị", "tag": "freefire"},
    "deta": {"name": "DETA IPA CRACK NOKЕY", "icon": "🔐", "description": "Mở menu Deta", "tag": "freefire"},
    "proxy": {"name": "PROXY MOD ALEN CRACK", "icon": "🌐", "description": "Mở mục Proxy", "tag": "freefire"},
    "mizze": {"name": "MENU MIZZE CRACK", "icon": "🎮", "description": "Mở mục Mizze", "tag": "freefire"},
    "nvpkey": {"name": "MENU NVP CRACK KEY", "icon": "🔑", "description": "Mở mục Nvp Crack Key", "tag": "lienquan"},
    "ysm": {"name": "MENU YSM TEAM LIÊN QUÂN", "icon": "⚔️", "description": "Mở mục YSM Team", "tag": "lienquan"},
    "maplq": {"name": "MAP LIÊN QUÂN NOKEY", "icon": "🗺️", "description": "Mở mục Map Liên Quân NoKey", "tag": "lienquan"},
    "detaqt": {"name": "DETA QUỐC TẾ", "icon": "🌍", "description": "Mở mục Deta Quốc Tế", "tag": "roblox"}
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
    "content_items": [],
    "tag_meta": {},
    "item_meta": {},
    "notices": []
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
    for _meta_key in ("tag_meta", "item_meta"):
        if not isinstance(data.get(_meta_key), dict):
            data[_meta_key] = {}
    if not isinstance(data.get("notices"), list):
        data["notices"] = []
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


def public_content_item(item):
    # V2.8.0: mục bắt buộc vượt link thì KHÔNG lộ đường dẫn tải ra công khai.
    result = dict(item)
    if result.get("gate"):
        result.pop("url", None)
    return result


def find_content_item(slug):
    slug = safe_text(slug, 60).lower()
    with JSON_LOCK:
        data = load_data_unlocked()
        for item in data.get("content_items", []):
            if isinstance(item, dict) and item.get("slug") == slug:
                return dict(item)
    return None


def get_destination_links():
    return {
        key: setting("url_" + key, value)
        for key, value in DEFAULT_DESTINATIONS.items()
    }


def destination_enabled(key):
    return setting("enabled_" + key, "1") == "1"


# ---------------------------------------------------------------
# V2.8.1: metadata Tag gốc / Mục gốc + Bảng thông báo
# ---------------------------------------------------------------

def _slug_ok(value):
    return bool(value) and value.replace("-", "").isalnum()


def meta_flag_deleted(item_meta, key):
    return (
        isinstance(item_meta, dict)
        and isinstance(item_meta.get(key), dict)
        and item_meta[key].get("deleted") is True
    )


def destination_deleted(key):
    with JSON_LOCK:
        data = load_data_unlocked()
    return meta_flag_deleted(data.get("item_meta"), key)


def sanitize_tag_meta(raw):
    clean = {}
    if not isinstance(raw, dict):
        return clean
    for slug, value in raw.items():
        if slug not in BASE_TAG_DEFAULTS or not isinstance(value, dict):
            continue
        clean[slug] = {
            "name": safe_text(value.get("name"), 60),
            "icon": safe_text(value.get("icon"), 12),
            "deleted": value.get("deleted") is True
        }
    return clean


def sanitize_item_meta(raw, valid_tags=None):
    clean = {}
    if not isinstance(raw, dict):
        return clean
    for key, value in raw.items():
        if key not in BASE_ITEM_DEFAULTS or not isinstance(value, dict):
            continue
        tag = safe_text(value.get("tag"), 40).lower()
        if not _slug_ok(tag) or (valid_tags is not None and tag not in valid_tags):
            tag = ""
        clean[key] = {
            "name": safe_text(value.get("name"), 120),
            "icon": safe_text(value.get("icon"), 12),
            "description": safe_text(value.get("description"), 200),
            "tag": tag,
            "deleted": value.get("deleted") is True
        }
    return clean


def sanitize_notices(raw):
    clean = []
    if not isinstance(raw, list):
        return clean
    for item in raw[:30]:
        if not isinstance(item, dict):
            continue
        text = safe_text(item.get("text"), 500)
        if not text:
            continue
        stamp = safe_text(item.get("time"), 20) or vietnam_now().strftime("%d/%m/%Y %H:%M")
        clean.append({
            "text": text,
            "enabled": item.get("enabled") is not False,
            "time": stamp
        })
    return clean


def build_base_meta_view(stored):
    tag_meta = stored.get("tag_meta") if isinstance(stored.get("tag_meta"), dict) else {}
    item_meta = stored.get("item_meta") if isinstance(stored.get("item_meta"), dict) else {}
    settings = stored.get("settings") or {}

    tags = []
    for slug, default in BASE_TAG_DEFAULTS.items():
        meta = tag_meta.get(slug) if isinstance(tag_meta.get(slug), dict) else {}
        tags.append({
            "slug": slug,
            "name": meta.get("name") or default["name"],
            "icon": meta.get("icon") or default["icon"],
            "enabled": settings.get("tag_" + slug, "1") == "1",
            "deleted": meta.get("deleted") is True
        })

    items = []
    for key, default in BASE_ITEM_DEFAULTS.items():
        meta = item_meta.get(key) if isinstance(item_meta.get(key), dict) else {}
        items.append({
            "key": key,
            "route": DESTINATION_ROUTES.get(key, ""),
            "name": meta.get("name") or default["name"],
            "icon": meta.get("icon") or default["icon"],
            "description": meta.get("description") or default["description"],
            "tag": meta.get("tag") or default["tag"],
            "deleted": meta.get("deleted") is True
        })

    return {"tags": tags, "items": items}


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


def validate_download_url(value):
    # V2.8.0: nút LẤY FILE có thể trỏ tới MediaFire, Zufile hoặc bất kỳ link HTTPS hợp lệ.
    if not validate_http_url(value):
        return False

    return urlsplit(value.strip()).scheme == "https"


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
            if destination in data["files"]:
                data["files"][destination]["downloads"] = (
                    safe_count(
                        data["files"][destination].get("downloads", 0)
                    ) + 1
                )
            elif destination.startswith("c_"):
                for content in data.get("content_items", []):
                    if isinstance(content, dict) and content.get("slug") == destination[2:]:
                        content["downloads"] = safe_count(content.get("downloads", 0)) + 1
                        break

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
<meta name="theme-color" content="#ffffff">
<title>NGUYỄN VĂN PHONG WEBSITE</title>
<style>
*{box-sizing:border-box}
html{scroll-behavior:smooth}
body{
 margin:0;min-height:100vh;font-family:Arial,sans-serif;color:white;
 background:#000;
 overflow-x:hidden;transition:background .3s,color .3s
}
body.light{
 color:#10203c;
 background:#fff
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
 backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);
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
 backdrop-filter:blur(14px);-webkit-backdrop-filter:blur(14px);
 padding:23px 15px;background:rgba(9,24,55,.9);
 border:1px solid rgba(64,157,255,.65);border-radius:15px;transition:.25s
}
.menu-card h2{font-size:18px;margin:0 0 17px}
.link-box{
 backdrop-filter:blur(16px);-webkit-backdrop-filter:blur(16px);
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
.music-mini{
 display:flex;align-items:center;justify-content:center;gap:15px;
 width:min(230px,90%);min-height:58px;margin:25px auto 15px;
 padding:9px 15px;border:1px solid #55baff;border-radius:13px;
 background:linear-gradient(135deg,rgba(5,34,75,.96),rgba(0,91,170,.9));
 box-shadow:0 0 18px rgba(22,140,255,.35)
}
.music-bars{height:28px;display:flex;align-items:center;gap:4px}
.music-bars i{
 display:block;width:4px;height:7px;border-radius:5px;
 background:#79d2ff;box-shadow:0 0 7px #36baff
}
.music-mini.playing .music-bars i{animation:musicBeat .65s ease-in-out infinite alternate}
.music-mini.playing .music-bars i:nth-child(2){animation-delay:.15s}
.music-mini.playing .music-bars i:nth-child(3){animation-delay:.3s}
.music-mini.playing .music-bars i:nth-child(4){animation-delay:.45s}
@keyframes musicBeat{from{height:6px}to{height:26px}}
.music-mini button{
 width:39px;height:39px;border:1px solid #8bd7ff;border-radius:10px;
 color:white;background:linear-gradient(135deg,#086de0,#13b5ff);
 font-size:18px;font-weight:bold;cursor:pointer;box-shadow:0 0 12px #168cff
}
.music-mini button:active{transform:scale(.96)}
.home-search{max-width:650px;margin:22px auto;position:relative;text-align:left}
.home-search input{width:100%;padding:14px 16px;border:1px solid #45aaff;border-radius:12px;background:rgba(5,22,52,.94);color:#fff;font-size:15px}
.search-results{position:absolute;z-index:1200;top:calc(100% + 5px);left:0;right:0;padding:8px;background:#071a38;border:1px solid #369eff;border-radius:12px;box-shadow:0 12px 30px #00152e}
.search-results a{display:block;padding:11px;color:#d9efff;text-decoration:none;border-radius:8px}
.search-results a:hover{background:#123c70}
.music-mini{position:fixed;z-index:9000;right:14px;bottom:14px;width:auto;max-width:min(92vw,350px);margin:0;justify-content:flex-start;cursor:grab;touch-action:none}
.music-mini.dragging{cursor:grabbing;opacity:.9}.music-track-name{max-width:105px;overflow:hidden;text-overflow:ellipsis;white-space:nowrap;color:#e3f5ff;font-size:12px;font-weight:bold}
.music-mini.minimized{display:none!important}.music-restore{position:fixed;z-index:9001;right:16px;bottom:16px;width:52px;height:52px;border-radius:50%;border:1px solid #8bd7ff;color:white;background:linear-gradient(135deg,#086de0,#13b5ff);font-size:25px;box-shadow:0 0 18px #168cff}
.music-mini .music-minimize{width:28px;height:28px;font-size:15px;border-radius:7px}


/* PHONG WEB V2.8.0 – Advanced UI */
header,.side-menu,.tag-group,.tag-item-card,.stats-bar span,.home-search input,
.search-results,.music-mini,.link-box,.menu-card,.location-card{
 backdrop-filter:blur(18px);-webkit-backdrop-filter:blur(18px);
}
header{background:rgba(4,12,34,.72);border-bottom-color:rgba(91,190,255,.58)}
.side-menu{background:rgba(5,18,45,.78);border-color:rgba(91,190,255,.62)}
.tag-group{background:linear-gradient(135deg,rgba(8,42,85,.62),rgba(5,20,49,.68));border-color:rgba(91,190,255,.48);transition:transform .22s,border-color .22s,box-shadow .22s}
.tag-group:hover{border-color:rgba(100,200,255,.72);box-shadow:0 12px 32px rgba(0,100,220,.16)}
.tag-item-card{background:rgba(10,45,87,.48);box-shadow:inset 0 1px rgba(255,255,255,.06)}
.tag-item-card img{width:100%;height:118px;object-fit:cover;border-radius:9px;border:1px solid rgba(120,200,255,.25)}
.tag-count{margin-left:auto;padding:5px 9px;border-radius:999px;background:rgba(0,135,255,.2);border:1px solid rgba(91,190,255,.4);font-size:11px;color:#d9f2ff;white-space:nowrap}
.tag-menu-count{float:right;opacity:.8;font-size:11px;border-radius:20px;padding:2px 7px;background:rgba(0,130,255,.2)}
.favorite-button{align-self:flex-end;padding:6px 9px;border-radius:8px;border:1px solid rgba(105,190,255,.4);background:rgba(0,95,180,.22);color:#dff4ff;cursor:pointer}
.favorite-button.active{background:rgba(255,184,0,.18);border-color:#ffcf62;color:#ffe39a}
.catalog-empty{padding:18px;border:1px dashed rgba(100,180,255,.4);border-radius:12px;color:#b8d8f5;text-align:center}
.page{animation:pageIn .32s cubic-bezier(.2,.75,.25,1) both}
@media(max-width:600px){.tag-item-card img{height:145px}.tag-count{font-size:10px}}

.all-tags-directory{max-width:980px;margin:28px auto 38px;text-align:left}
.directory-heading{text-align:center;margin:0 0 22px}
.directory-heading h2{color:#9cddff;text-shadow:0 0 14px rgba(35,155,255,.45);margin:0 0 7px}
.directory-heading p{color:#a9c8e8;margin:0;font-size:13px}
.tag-group{margin:18px 0;padding:17px;border:1px solid rgba(65,166,255,.42);border-radius:17px;background:linear-gradient(135deg,rgba(8,35,75,.92),rgba(5,17,43,.92));box-shadow:0 8px 25px rgba(0,0,0,.18)}
.tag-group-title{display:flex;align-items:center;gap:11px;margin-bottom:14px}
.tag-group-title>span{font-size:28px}
.tag-group-title h3{margin:0;color:#e1f4ff;font-size:17px}
.tag-group-title small{display:block;color:#9ab8d8;margin-top:4px}
.tag-group-title>a{margin-left:auto;color:#69c7ff;text-decoration:none;font-weight:700;font-size:13px;white-space:nowrap}
.tag-items-grid{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:10px}
.tag-item-card{min-width:0;display:flex;flex-direction:column;gap:6px;padding:14px;border-radius:12px;border:1px solid rgba(80,168,255,.3);background:rgba(10,45,87,.7);color:#eaf7ff;text-decoration:none;transition:transform .2s,border-color .2s,background .2s}
.tag-item-card:hover{transform:translateY(-2px);border-color:#50baff;background:rgba(15,67,120,.85)}
.tag-item-card>span{font-size:23px}
.tag-item-card b{font-size:13px;line-height:1.4}
.tag-item-card small{font-size:11px;color:#a9c9e9}
@media(max-width:600px){
 .all-tags-directory{margin:22px 3px 30px}
 .tag-group{padding:13px}
 .tag-items-grid{grid-template-columns:1fr}
 .tag-group-title h3{font-size:15px}
}
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
/* ===== PHONG WEB V2.8.0: giao diện vuông góc + phông trắng (nút sáng/tối vẫn hoạt động) ===== */

.spinner{border-radius:50%}
.menu-card+.menu-card{margin-top:16px}
body.light{color:#10203c;background:#fff!important}
body.light:before,body.light #particles{display:none!important}
body.light header{background:#fff;color:#10203c;border-bottom:1px solid #299cff;box-shadow:0 1px 6px rgba(0,80,160,.12)}
body.light .header-title{text-shadow:none;color:#0b4f9c}
body.light .hamburger-button,body.light .theme-button,body.light .clock-box{background:#fff;color:#10203c;border-color:#299cff;box-shadow:none}
body.light .side-menu{background:#fff;border-color:#299cff;box-shadow:0 4px 14px rgba(0,80,160,.18)}
body.light .side-menu a{color:#10203c}
body.light .side-menu a:hover{background:#087ce5;color:#fff}
body.light h1{text-shadow:none;color:#0b4f9c}
body.light .location-card,body.light .menu-card,body.light .link-box{background:#fff;color:#10203c;border-color:#299cff;box-shadow:0 2px 10px rgba(0,80,160,.12)}
body.light .tag-group{background:#fff;border-color:#9fcfff;box-shadow:0 2px 10px rgba(0,80,160,.08)}
body.light .tag-group-title h3{color:#0b4f9c}
body.light .tag-group-title small,body.light .tag-item-card small,body.light .directory-heading p{color:#4a6a8a}
body.light .directory-heading h2{color:#0877c9;text-shadow:none}
body.light .tag-item-card{background:#f5faff;border-color:#b9dcff;color:#10203c;box-shadow:none}
body.light .tag-item-card:hover{background:#e6f3ff;border-color:#299cff}
body.light .tag-count,body.light .tag-menu-count{background:#e6f3ff;border-color:#9fcfff;color:#0b4f9c}
body.light .stats-bar{color:#274768}
body.light .stats-bar span{background:#fff;border-color:#9fcfff}
body.light .stats-bar b{color:#0b4f9c}
body.light .home-search input{background:#fff;color:#10203c;border-color:#299cff}
body.light .search-results{background:#fff;border-color:#299cff;box-shadow:0 6px 16px rgba(0,80,160,.18)}
body.light .search-results a{color:#10203c}
body.light .search-results a:hover{background:#e6f3ff}
body.light .announcement{background:#eef7ff;color:#10203c}
body.light .maintenance{background:#fff6e5;color:#4a3000}
body.light .catalog-empty{color:#4a6a8a}
body.light .back-button{background:#eef7ff;color:#0b4f9c;border-color:#299cff}
body.light .status{color:#8a5a00}
body.light .status.error{color:#c62828}
body.light .status.success{color:#0a8a4f}
body.light .thank-image-button{background:#fff;box-shadow:none}
body.light footer{background:#fff;color:#274768;border-top:1px solid #9fcfff}
body.light footer strong{color:#0877c9}
body.light #toast{background:#fff;color:#10203c}
body.light #loadingOverlay{background:rgba(255,255,255,.92);color:#10203c}
body.light .favorite-button{background:#eef7ff;color:#0b4f9c}

/* ===== PHONG WEB V2.8.0: bo góc + viền xanh glow + menu trượt + chuyển sáng/tối động ===== */
:root{--glow:rgba(41,156,255,.38)}
header,.location-card,.menu-card,.link-box,.tag-group,.tag-item-card,.stats-bar span,.announcement,.maintenance,.home-search input,.search-results,.thank-image-button,.tag-item-card img{border-radius:14px}
.hamburger-button,.theme-button,.clock-box,.cross-link-button,.open-menu-button,.location-button,.back-button,.result-action,.favorite-button,.search-results a,.side-menu a,#toast{border-radius:10px}
.music-mini{border-radius:16px}
.music-restore,.hero-logo{border-radius:50%}
.tag-count,.tag-menu-count{border-radius:999px}
.link-box,.menu-card,.location-card,.tag-group,.tag-item-card,.stats-bar span,.home-search input,.clock-box,.hamburger-button,.theme-button{
 border-color:rgba(70,170,255,.75);
 box-shadow:0 0 0 1px rgba(41,156,255,.22),0 0 16px var(--glow);
 transition:transform .28s cubic-bezier(.2,.8,.2,1),box-shadow .28s,border-color .28s,background-color .28s
}
.link-box:hover,.menu-card:hover,.location-card:hover,.tag-group:hover,.tag-item-card:hover,.stats-bar span:hover{
 transform:translateY(-3px);border-color:#5cc4ff;
 box-shadow:0 0 0 1px rgba(90,195,255,.6),0 0 30px rgba(41,156,255,.6)
}
.hamburger-button:hover,.theme-button:hover{transform:scale(1.08);box-shadow:0 0 20px rgba(41,156,255,.65)}
.cross-link-button,.open-menu-button,.location-button,.back-button,.result-action,.favorite-button{transition:transform .22s,box-shadow .22s,filter .22s}
.cross-link-button:hover,.open-menu-button:hover,.location-button:hover,.back-button:hover,.result-action:hover{transform:translateY(-2px) scale(1.03);filter:brightness(1.12);box-shadow:0 0 22px rgba(41,156,255,.6)}
body.light .link-box,body.light .menu-card,body.light .location-card,body.light .tag-group,body.light .tag-item-card,body.light .stats-bar span,body.light .home-search input,body.light .clock-box,body.light .hamburger-button,body.light .theme-button{
 border-color:#299cff;box-shadow:0 0 0 1px rgba(41,156,255,.18),0 0 14px rgba(41,156,255,.22)
}
body.light .link-box:hover,body.light .menu-card:hover,body.light .location-card:hover,body.light .tag-group:hover,body.light .tag-item-card:hover,body.light .stats-bar span:hover{
 box-shadow:0 0 0 1px rgba(41,156,255,.45),0 0 24px rgba(41,156,255,.4)
}
.side-menu{display:block!important;position:fixed;top:0;left:0;bottom:0;width:270px;max-width:82vw;margin:0;padding:84px 12px 24px;
 border-radius:0 18px 18px 0;overflow-y:auto;z-index:1500;transform:translateX(-108%);visibility:hidden;
 box-shadow:0 0 30px rgba(41,156,255,.35);
 transition:transform .38s cubic-bezier(.2,.8,.2,1),visibility 0s linear .38s}
.side-menu.show{transform:translateX(0);visibility:visible;animation:none;transition:transform .38s cubic-bezier(.2,.8,.2,1),visibility 0s}
.side-menu a{margin:3px 0;transition:background .2s,transform .2s}
.side-menu a:hover{transform:translateX(5px)}
#menuBackdrop{position:fixed;inset:0;z-index:1400;background:rgba(0,10,30,.55);opacity:0;pointer-events:none;transition:opacity .3s}
#menuBackdrop.show{opacity:1;pointer-events:auto}
body.light #menuBackdrop{background:rgba(20,50,90,.25)}
#themeFade{position:fixed;inset:0;z-index:99999;pointer-events:none;will-change:clip-path,opacity}
body.theme-anim *{transition:background-color .6s ease,color .6s ease,border-color .6s ease,box-shadow .6s ease!important}

/* ===== PHONG WEB V2.8.1: YouTube/TikTok + Bảng thông báo + Tag/Mục gốc có thể xóa ===== */
[data-deleted-tag]{display:none!important}
.social-row{display:grid;grid-template-columns:1fr 1fr;gap:12px;max-width:640px;margin:16px auto}
.social-btn{display:flex;flex-direction:column;align-items:center;justify-content:center;gap:4px;min-height:92px;padding:14px 10px;border-radius:14px;color:#fff;text-decoration:none;text-align:center;font-weight:800;letter-spacing:.4px;border:1px solid rgba(255,255,255,.25);transition:transform .22s,box-shadow .22s,filter .22s}
.social-btn span{font-size:30px;line-height:1}
.social-btn small{font-weight:600;font-size:12px;opacity:.92}
.social-btn:hover{transform:translateY(-3px);filter:brightness(1.1)}
.social-btn.youtube{background:linear-gradient(135deg,#ff2a2a,#a30000);box-shadow:0 4px 18px rgba(255,0,0,.3)}
.social-btn.tiktok{background:linear-gradient(135deg,#111,#2b2b2b);box-shadow:0 4px 18px rgba(0,242,234,.25),-2px -2px 0 rgba(0,242,234,.55),2px 2px 0 rgba(255,0,80,.55)}
.notice-board{max-width:760px;margin:16px auto;border:1px solid #50baff;border-radius:14px;background:rgba(4,20,48,.75);overflow:hidden;text-align:left}
.notice-board-head{padding:11px 14px;background:rgba(0,120,230,.35);font-weight:800;color:#fff;letter-spacing:.4px}
.notice-list{max-height:260px;overflow-y:auto;padding:6px 14px}
.notice-item{padding:10px 0;border-bottom:1px dashed rgba(120,190,255,.35)}
.notice-item:last-child{border-bottom:0}
.notice-item p{margin:4px 0 0;line-height:1.65;white-space:pre-wrap;word-break:break-word}
.notice-time{font-size:12px;color:#8fd0ff}
.notice-empty{padding:12px 0;color:#b9d7f7}
body.light .notice-board{background:#fff;border-color:#299cff;color:#10203c;box-shadow:0 2px 10px rgba(0,80,160,.12)}
body.light .notice-board-head{color:#0b3a6e;background:#e3f2ff}
body.light .notice-time{color:#0877c9}
body.light .notice-empty{color:#44607f}
@media(max-width:480px){.social-btn{min-height:80px;font-size:14px}.social-btn span{font-size:26px}}

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
 <div class="header-title" id="siteTitle">NGUYỄN VĂN PHONG WEBSITE</div>
 <div class="clock-box"><span id="liveClock">🌙 00:00:00</span></div>
 <button class="theme-button" id="themeButton" title="Đổi giao diện">☀️</button>
 </header>
<div id="menuBackdrop"></div>
<nav class="side-menu" id="sideMenu">
  <a href="/" id="homeMenuButton" data-tag="home">🏠 TRANG CHỦ</a>
  <a href="/?category=freefire" id="freeFireMenuButton" data-tag="freefire">🔥 HACK FREE FIRE</a>
  <a href="/?category=lienquan" id="lienQuanMenuButton" data-tag="lienquan">⚔️ HACK LIÊN QUÂN</a>
  <a href="/?category=roblox" id="robloxMenuButton" data-tag="roblox">🧱 HACK ROBLOX</a>
  <div id="dynamicTagMenu"></div>
  <a href="/admin">⚙️ QUẢN TRỊ</a>
 </nav>

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

  <!-- V2.8.1: YouTube + TikTok ngang nhau -->
  <div class="social-row">
   <a class="social-btn youtube" href="https://youtube.com/@phongngno1.treorank?si=EzywiALRAmFAGT58" target="_blank" rel="noopener noreferrer"><span>▶️</span><b>YOUTUBE</b><small>Mở kênh YouTube</small></a>
   <a class="social-btn tiktok" href="https://vm.tiktok.com/ZS9PAhyxoUMWy-PKpM7/" target="_blank" rel="noopener noreferrer"><span>🎵</span><b>TIKTOK</b><small>Mở kênh TikTok</small></a>
  </div>

  <!-- V2.8.1: Bảng thông báo -->
  <section class="notice-board" id="noticeBoard">
   <div class="notice-board-head">📢 BẢNG THÔNG BÁO</div>
   <div class="notice-list" id="noticeList"><div class="notice-empty">Đang tải thông báo...</div></div>
  </section>

  <div class="home-search"><input id="homeSearch" type="search" placeholder="🔎 Tìm nhanh chức năng, danh mục..." autocomplete="off"><div id="searchResults" class="search-results hidden"></div></div>

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

  <!-- V2.4.0: Trang Chủ tổng hợp nội dung từ tất cả Tag -->
  <section class="all-tags-directory" id="allTagsDirectory">
   <div class="directory-heading">
    <h2>🌐 KHÁM PHÁ TẤT CẢ DANH MỤC</h2>
    <p>Tổng hợp các mục đang có trong tất cả Tag ngay tại Trang Chủ.</p>
   </div>

   <section class="tag-group" data-tag="freefire">
    <div class="tag-group-title"><span>🔥</span><div><h3>HACK FREE FIRE</h3><small>Các mục thuộc Tag Free Fire</small></div>
     <a href="/?category=freefire">Xem Tag →</a>
    </div>
    <div class="tag-items-grid"></div>
   </section>

   <section class="tag-group" data-tag="lienquan">
    <div class="tag-group-title"><span>⚔️</span><div><h3>HACK LIÊN QUÂN</h3><small>Nội dung thuộc Tag Liên Quân</small></div>
     <a href="/?category=lienquan">Xem Tag →</a>
    </div>
    <div class="tag-items-grid"></div>
   </section>

   <section class="tag-group" data-tag="roblox">
    <div class="tag-group-title"><span>🧱</span><div><h3>HACK ROBLOX</h3><small>Nội dung thuộc Tag Roblox</small></div>
     <a href="/?category=roblox">Xem Tag →</a>
    </div>
    <div class="tag-items-grid"></div>
   </section>
  </section>
 </div>
</section>

<section class="page" id="freeFirePage">
 <div class="link-box">
  <div class="link-icon" id="freefireIcon">🔥</div>
  <h2 id="freefireTitle">CHÀO BẠN ĐẾN VỚI HACK FREE FIRE</h2>
  <div class="link-description">Chọn một trong các mục bên dưới để tiếp tục.</div>
 </div>
 <div id="freefireList" data-wrap="1"></div>
 <a class="back-button" href="/" onclick="event.preventDefault();navigateCategory('home')">← TRANG CHỦ</a>
</section>

<section class="page" id="lienQuanPage">
 <div class="link-box"><div class="link-icon" id="lienquanIcon">⚔️</div><h2 id="lienquanTitle">CHÀO BẠN ĐẾN VỚI HACK LIÊN QUÂN</h2><div id="lienquanList"></div><a class="back-button" href="/" onclick="event.preventDefault();navigateCategory('home')">← TRANG CHỦ</a></div>
</section>

<section class="page" id="robloxPage">
 <div class="link-box"><div class="link-icon" id="robloxIcon">🧱</div><h2 id="robloxTitle">CHÀO BẠN ĐẾN VỚI HACK ROBLOX</h2><div id="robloxList"></div><a class="back-button" href="/" onclick="event.preventDefault();navigateCategory('home')">← TRANG CHỦ</a></div>
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

<section class="page" id="detaqtPage">
 <div class="link-box">
  <div class="link-icon">🌍</div>
  <h2>BẠN CẦN VƯỢT LINK ĐỂ LẤY FILE DETA QUỐC TẾ</h2>
  <div class="link-description" id="detaqtFileInfo"></div>
  <button class="cross-link-button" id="detaqtCrossButton">🔓 VƯỢT LINK</button>
  <div class="status" id="detaqtStatus"></div><br>
  <a class="back-button" href="/">← QUAY LẠI TRANG CHỦ</a>
 </div>
</section>

<section class="page" id="maplqPage">
 <div class="link-box">
  <div class="link-icon">🗺️</div>
  <h2>BẠN CẦN VƯỢT LINK ĐỂ LẤY FILE MAP LIÊN QUÂN NOKEY</h2>
  <div class="link-description" id="maplqFileInfo"></div>
  <button class="cross-link-button" id="maplqCrossButton">🔓 VƯỢT LINK</button>
  <div class="status" id="maplqStatus"></div><br>
  <a class="back-button" href="/?category=lienquan" onclick="event.preventDefault();navigateCategory('lienquan')">← QUAY LẠI</a>
 </div>
</section>

<section class="page" id="nvpKeyPage"><div class="link-box"><div class="link-icon">🔑</div><h2>BẠN CẦN VƯỢT LINK ĐỂ LẤY FILE</h2><div class="link-description" id="nvpkeyFileInfo"></div><button class="cross-link-button" id="nvpKeyCrossButton">🔓 VƯỢT LINK</button><div class="status" id="nvpKeyStatus"></div><br><a class="back-button" href="/?category=lienquan" onclick="event.preventDefault();navigateCategory('lienquan')">← QUAY LẠI</a></div></section>
<section class="page" id="nvpThanksPage"><div class="link-box"><h2>CẢM ƠN BẠN ĐÃ VƯỢT LINK ỦNG HỘ WEBSITE</h2><button class="thank-image-button" id="nvpThankImage"><img src="/cam-on-tu-phong.png" alt="Cảm ơn từ Phong"></button><audio id="nvpThankAudio" src="/cam-on-tu-phong.mp3" preload="none"></audio><div class="status">Nhấn vào hình để phát lời cảm ơn.</div><button class="cross-link-button" id="nvpNextButton">TIẾP THEO</button></div></section>
<section class="page" id="nvpSuccessPage"><div class="link-box"><div class="link-icon">✅</div><h2>VƯỢT LINK THÀNH CÔNG</h2><a class="result-action" id="nvpGetFile" href="/menu-nvp-crack-key" target="_blank" rel="noopener">LẤY FILE</a></div></section>
<section class="page" id="ysmPage"><div class="link-box"><div class="link-icon">⚔️</div><h2>BẠN CẦN VƯỢT LINK ĐỂ LẤY FILE</h2><div class="link-description" id="ysmFileInfo"></div><button class="cross-link-button" id="ysmCrossButton">🔓 VƯỢT LINK</button><div class="status" id="ysmStatus"></div><br><a class="back-button" href="/?category=lienquan" onclick="event.preventDefault();navigateCategory('lienquan')">← QUAY LẠI</a></div></section>
<section class="page" id="ysmThanksPage"><div class="link-box"><h2>CẢM ƠN BẠN ĐÃ VƯỢT LINK ỦNG HỘ WEBSITE</h2><button class="thank-image-button" id="ysmThankImage"><img src="/cam-on-tu-phong.png" alt="Cảm ơn từ Phong"></button><audio id="ysmThankAudio" src="/cam-on-tu-phong.mp3" preload="none"></audio><div class="status">Nhấn vào hình để phát lời cảm ơn.</div><button class="cross-link-button" id="ysmNextButton">TIẾP THEO</button></div></section>
<section class="page" id="ysmSuccessPage"><div class="link-box"><div class="link-icon">✅</div><h2>VƯỢT LINK THÀNH CÔNG</h2><a class="result-action" id="ysmGetFile" href="/menu-ysm-team-lien-quan" target="_blank" rel="noopener">LẤY FILE</a></div></section>
<section class="page" id="gatePage"><div class="link-box"><div class="link-icon" id="gateIcon">📦</div><h2 id="gateTitle">BẠN CẦN VƯỢT LINK ĐỂ LẤY FILE</h2><div class="link-description" id="gateDesc"></div><button class="cross-link-button" id="gateCrossButton">🔓 VƯỢT LINK</button><div class="status" id="gateStatus"></div><br><a class="back-button" href="/">← QUAY LẠI TRANG CHỦ</a></div></section>
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

<div class="music-mini" id="musicPlayer" aria-label="Trình phát nhạc">
 <div class="music-bars" aria-hidden="true"><i></i><i></i><i></i><i></i></div>
 <div class="music-track-name" id="musicTrackName">Chưa phát nhạc</div>
 <button id="musicButton" type="button" aria-label="Bật hoặc tắt nhạc">
  <span id="musicIcon">▶</span>
 </button>
 <button class="music-minimize" id="musicMinimize" type="button" title="Thu nhỏ">−</button>
</div>
<button id="musicRestore" class="music-restore hidden" type="button" title="Mở trình phát nhạc">♫</button>
<audio id="backgroundMusic" preload="none"></audio>

<footer>
 © 2026 Nguyễn Văn Phong Website<br>
 <strong id="footerVersion">PHONG WEB V2.8.2</strong>
</footer>

<script>
const pages={
 home:document.getElementById("homePage"),
 freefire:document.getElementById("freeFirePage"),
 lienquan:document.getElementById("lienQuanPage"),
 roblox:document.getElementById("robloxPage"),
 location:document.getElementById("locationPage"),
 deta:document.getElementById("detaPage"),
 proxy:document.getElementById("proxyPage"),
 mizze:document.getElementById("mizzePage"),
 detaqt:document.getElementById("detaqtPage"),
 thank:document.getElementById("thankPage"),
 result:document.getElementById("resultPage"),
 nvpkey:document.getElementById("nvpKeyPage"),
 nvpthanks:document.getElementById("nvpThanksPage"),
 nvpsuccess:document.getElementById("nvpSuccessPage"),
 ysm:document.getElementById("ysmPage"),
 ysmthanks:document.getElementById("ysmThanksPage"),
 ysmsuccess:document.getElementById("ysmSuccessPage"),
 maplq:document.getElementById("maplqPage"),
 gate:document.getElementById("gatePage")
};

const destinationRoutes={
 location:"/dinh-vi",deta:"/menu",
 proxy:"/proxy-mod-alen-crack",mizze:"/mizze-crack",detaqt:"/deta-quoc-te",
 maplq:"/map-lien-quan-nokey"
};

const downloadRoutes={
 location:"/download-location",deta:"/download-deta",
 proxy:"/download-proxy",mizze:"/download-mizze",
 nvpkey:"/download-nvpkey",ysm:"/download-ysm",detaqt:"/download-detaqt",
 maplq:"/download-maplq"
};

// PHONG WEB V2.8.1: Tag gốc + Mục gốc sửa/xóa được từ Quản Trị, bảng thông báo, Deta Quốc Tế.
const BASE_TAGS={
 freefire:{name:"HACK FREE FIRE",icon:"🔥"},
 lienquan:{name:"HACK LIÊN QUÂN",icon:"⚔️"},
 roblox:{name:"HACK ROBLOX",icon:"🧱"}
};
const BASE_ITEMS=[
 {key:"location",route:"/dinh-vi",tag:"freefire",icon:"📍",name:"Định Vị Xanh Tím OB55",desc:"Mở mục định vị",btn:"MỞ MỤC"},
 {key:"deta",route:"/menu",tag:"freefire",icon:"🔐",name:"DETA IPA CRACK NOKЕY",desc:"Mở menu Deta",btn:"MỞ MENU"},
 {key:"proxy",route:"/proxy-mod-alen-crack",tag:"freefire",icon:"🌐",name:"PROXY MOD ALEN CRACK",desc:"Mở mục Proxy",btn:"MỞ MỤC"},
 {key:"mizze",route:"/mizze-crack",tag:"freefire",icon:"🎮",name:"MENU MIZZE CRACK",desc:"Mở mục Mizze",btn:"MỞ MỤC"},
 {key:"nvpkey",route:"/menu-nvp-crack-key",tag:"lienquan",icon:"🔑",name:"MENU NVP CRACK KEY",desc:"Mở mục Nvp Crack Key",btn:"MỞ MỤC"},
 {key:"ysm",route:"/menu-ysm-team-lien-quan",tag:"lienquan",icon:"⚔️",name:"MENU YSM TEAM LIÊN QUÂN",desc:"Mở mục YSM Team",btn:"MỞ MỤC"},
 {key:"maplq",route:"/map-lien-quan-nokey",tag:"lienquan",icon:"🗺️",name:"MAP LIÊN QUÂN NOKEY",desc:"Mở mục Map Liên Quân NoKey",btn:"MỞ MỤC"},
 {key:"detaqt",route:"/deta-quoc-te",tag:"roblox",icon:"🌍",name:"DETA QUỐC TẾ",desc:"Mở mục Deta Quốc Tế",btn:"MỞ MỤC"}
];
window.PHONG_BASE_META={tag_meta:{},item_meta:{},enabled:{}};
function baseTagInfo(slug){
 const d=BASE_TAGS[slug]||{name:slug,icon:"🏷️"},m=(PHONG_BASE_META.tag_meta||{})[slug]||{};
 return {slug:slug,name:m.name||d.name,icon:m.icon||d.icon,deleted:m.deleted===true};
}
function baseTagDeleted(slug){return !!(slug&&BASE_TAGS[slug]&&baseTagInfo(slug).deleted)}
function baseItemInfo(it){
 const m=(PHONG_BASE_META.item_meta||{})[it.key]||{};
 return {key:it.key,route:it.route,btn:it.btn,name:m.name||it.name,icon:m.icon||it.icon,desc:m.description||it.desc,tag:m.tag||it.tag,deleted:m.deleted===true,enabled:PHONG_BASE_META.enabled[it.key]!==false};
}
function setBaseMeta(d){
 if(!d)return;
 PHONG_BASE_META.tag_meta=d.tag_meta||{};
 PHONG_BASE_META.item_meta=d.item_meta||{};
 const en={};
 BASE_ITEMS.forEach(it=>{if(typeof d[it.key]==="boolean")en[it.key]=d[it.key]});
 PHONG_BASE_META.enabled=en;
}
function mk(tag,cls,text){const e=document.createElement(tag);if(cls)e.className=cls;if(text!==undefined)e.textContent=text;return e}
function renderBaseItems(){
 document.querySelectorAll("[data-base-card]").forEach(x=>x.remove());
 const root=document.getElementById("allTagsDirectory");
 const shown={};
 BASE_ITEMS.map(baseItemInfo).forEach(it=>{
  if(it.deleted||!it.enabled)return;
  if(BASE_TAGS[it.tag]&&baseTagDeleted(it.tag))return;
  const grid=root&&root.querySelector('.tag-group[data-tag="'+it.tag+'"] .tag-items-grid');
  if(grid){
   const a=mk("a","tag-item-card");a.dataset.baseCard=it.key;a.href=it.route;
   a.append(mk("span","",it.icon),mk("b","",it.name),mk("small","",it.desc));
   grid.insertBefore(a,grid.querySelector(":scope > .tag-item-card:not([data-base-card])"));
  }
  const list=document.getElementById(it.tag+"List");
  if(list){
   shown[it.tag]=true;
   const wrap=list.dataset.wrap==="1";
   if(it.key==="location"){
    const sec=mk("section","location-container");sec.dataset.baseCard=it.key;
    const a=mk("a","location-link");a.href=it.route;
    const card=mk("div","location-card");
    const info=mk("div","location-info");
    info.append(mk("h2","",it.name),mk("p","","Nhấn vào đây để tiếp tục"),mk("span","location-button","MỞ MỤC"));
    card.append(mk("div","location-emoji",it.icon),info);a.append(card);sec.append(a);list.append(sec);
   }else{
    const card=mk("div","menu-card");card.id="card-"+it.key;
    card.append(mk("h2","",it.icon+" "+it.name));
    const btn=mk("button","open-menu-button",it.btn);btn.type="button";btn.onclick=()=>navigate(it.route);
    card.append(btn);
    if(wrap){const sec=mk("section","menu-container");sec.dataset.baseCard=it.key;sec.append(card);list.append(sec)}
    else{card.dataset.baseCard=it.key;list.append(card)}
   }
  }
 });
 Object.keys(BASE_TAGS).forEach(slug=>{
  const list=document.getElementById(slug+"List");
  if(list&&!shown[slug]){const e=mk("div","catalog-empty","Chưa có mục nào trong Tag này.");e.dataset.baseCard="empty";list.append(e)}
 });
}
function applyBaseTagMeta(){
 const menuIds={freefire:"freeFireMenuButton",lienquan:"lienQuanMenuButton",roblox:"robloxMenuButton"};
 Object.keys(BASE_TAGS).forEach(slug=>{
  const t=baseTagInfo(slug);
  document.querySelectorAll('[data-tag="'+slug+'"]').forEach(el=>{
   if(t.deleted)el.setAttribute("data-deleted-tag","1");else el.removeAttribute("data-deleted-tag");
  });
  const mb=document.getElementById(menuIds[slug]);if(mb)mb.textContent=t.icon+" "+t.name;
  const sec=document.querySelector('#allTagsDirectory .tag-group[data-tag="'+slug+'"]');
  if(sec){
   const ic=sec.querySelector(".tag-group-title > span:first-child");if(ic)ic.textContent=t.icon;
   const h=sec.querySelector(".tag-group-title h3");if(h)h.textContent=t.name;
  }
  const title=document.getElementById(slug+"Title");if(title)title.textContent="CHÀO BẠN ĐẾN VỚI "+t.name;
  const icon=document.getElementById(slug+"Icon");if(icon)icon.textContent=t.icon;
 });
}
function refreshTagCounts(){
 document.querySelectorAll("#allTagsDirectory .tag-group").forEach(sec=>{
  const grid=sec.querySelector(".tag-items-grid");
  const n=grid?grid.querySelectorAll(".tag-item-card").length:0;
  const small=sec.querySelector(".tag-group-title small");
  if(sec.dataset.generatedTag!=="1"&&small)small.textContent=n+" mục đang hiển thị";
  const count=sec.querySelector(".tag-count");if(count)count.textContent=n+" mục";
 });
}
function renderNotices(list){
 const box=document.getElementById("noticeList");if(!box)return;
 box.replaceChildren();
 const items=(Array.isArray(list)?list:[]).filter(x=>x&&x.enabled!==false&&x.text);
 if(!items.length){box.append(mk("div","notice-empty","Hiện chưa có thông báo nào."));return}
 items.forEach(x=>{
  const row=mk("div","notice-item");
  if(x.time)row.append(mk("span","notice-time","🕒 "+x.time));
  row.append(mk("p","",x.text));
  box.append(row);
 });
}
function applyPublicMeta(d){
 setBaseMeta(d);
 renderBaseItems();
 applyBaseTagMeta();
 renderNotices(d.notices);
 refreshTagCounts();
 const cat=new URLSearchParams(location.search).get("category");
 const hit=BASE_ITEMS.find(x=>x.route===location.pathname);
 if(baseTagDeleted(cat)||(hit&&baseItemInfo(hit).deleted)){history.replaceState({},"","/");showPage()}
}
renderBaseItems();
refreshTagCounts();

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
let savedTheme="light";
try{savedTheme=localStorage.getItem("phong_theme")||"light"}catch(e){}
applyTheme(savedTheme);
let themeBusy=false;
themeButton.addEventListener("click",()=>{
 if(themeBusy)return;
 const next=document.body.classList.contains("light")?"dark":"light";
 if(window.matchMedia&&matchMedia("(prefers-reduced-motion: reduce)").matches){applyTheme(next);return}
 themeBusy=true;
 const rect=themeButton.getBoundingClientRect();
 const x=rect.left+rect.width/2,y=rect.top+rect.height/2;
 const maxR=Math.hypot(Math.max(x,innerWidth-x),Math.max(y,innerHeight-y))+30;
 const fade=document.createElement("div");
 fade.id="themeFade";
 fade.style.background=next==="light"?"#ffffff":"#000000";
 document.body.appendChild(fade);
 const grow=fade.animate([
  {clipPath:"circle(0px at "+x+"px "+y+"px)"},
  {clipPath:"circle("+maxR+"px at "+x+"px "+y+"px)"}
 ],{duration:650,easing:"cubic-bezier(.4,0,.2,1)",fill:"forwards"});
 grow.onfinish=()=>{
  document.body.classList.add("theme-anim");
  applyTheme(next);
  const out=fade.animate([{opacity:1},{opacity:0}],{duration:500,easing:"ease",fill:"forwards"});
  out.onfinish=()=>{fade.remove();document.body.classList.remove("theme-anim");themeBusy=false};
 };
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
function navigateCategory(category){
 menu.classList.remove("show");
 const value=category==="home"?"":"?category="+encodeURIComponent(category);
 history.pushState({},"","/"+value);
 showPage();
 window.scrollTo(0,0);
}
function showPage(){
 hideAllPages();
 const q=new URLSearchParams(location.search);
 const nvp=q.get("nvpkey");
 if(nvp==="thanks"){pages.nvpthanks.classList.add("active");return;}
 if(nvp==="success"){
  const tk=q.get("token"),a=document.getElementById("nvpGetFile");
  if(a)a.href=tk?"/download-nvpkey?token="+encodeURIComponent(tk):"/menu-nvp-crack-key";
  pages.nvpsuccess.classList.add("active");return;
 }
 const gateSlug=q.get("gate");
 if(gateSlug){pages.gate.classList.add("active");setupGatePage(gateSlug);return;}
 const ysmStep=q.get("ysm");
 if(ysmStep==="thanks"){pages.ysmthanks.classList.add("active");return;}
 if(ysmStep==="success"){
  const tk=q.get("token"),a=document.getElementById("ysmGetFile");
  if(a)a.href=tk?"/download-ysm?token="+encodeURIComponent(tk):"/menu-ysm-team-lien-quan";
  pages.ysmsuccess.classList.add("active");return;
 }
 const result=q.get("result");
 const category=q.get("category");
 const customTagQuery=q.get("tag");

 if(baseTagDeleted(category)){
  history.replaceState({},"","/");pages.home.classList.add("active");return;
 }
 if(category==="freefire"){
  pages.freefire.classList.add("active");return;
 }
 if(category==="lienquan"){
  pages.lienquan.classList.add("active");return;
 }
 if(category==="roblox"){
  pages.roblox.classList.add("active");return;
 }

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
  "/mizze-crack":pages.mizze,
  "/deta-quoc-te":pages.detaqt,
  "/menu-nvp-crack-key":pages.nvpkey,
  "/menu-ysm-team-lien-quan":pages.ysm,
  "/map-lien-quan-nokey":pages.maplq
 };
 const baseHit=BASE_ITEMS.find(x=>x.route===location.pathname);
 if(baseHit&&baseItemInfo(baseHit).deleted){history.replaceState({},"","/");pages.home.classList.add("active");return;}
 (routes[location.pathname]||pages.home).classList.add("active");
 if(customTagQuery){
  setTimeout(()=>{
   const root=document.getElementById("allTagsDirectory");
   const target=root&&root.querySelector('[data-tag="'+customTagQuery+'"]');
   if(target)target.scrollIntoView({behavior:"smooth",block:"start"});
  },100);
 }
}
function isGateDest(d){return typeof d==="string"&&d.startsWith("c_")}
function gateDownloadHref(d,token){return "/download-content?slug="+encodeURIComponent(d.slice(2))+"&token="+encodeURIComponent(token)}
async function setupGatePage(slug){
 const btn=document.getElementById("gateCrossButton"),st=document.getElementById("gateStatus");
 const title=document.getElementById("gateTitle"),desc=document.getElementById("gateDesc"),icon=document.getElementById("gateIcon");
 st.textContent="";let item=null;
 try{const r=await fetch("/public-settings",{cache:"no-store"});const d=await r.json();item=(d.content_items||[]).find(x=>x.slug===slug&&x.enabled!==false&&x.gate)}catch(e){}
 if(!item){title.textContent="KHÔNG TÌM THẤY MỤC";desc.textContent="";btn.classList.add("hidden");return}
 btn.classList.remove("hidden");btn.disabled=false;
 icon.textContent=item.icon||"📦";
 title.textContent="BẠN CẦN VƯỢT LINK ĐỂ LẤY "+(item.name||"FILE").toUpperCase();
 desc.textContent=item.description||"";
 btn.onclick=()=>createShortLink("c_"+slug,btn,st);
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

// PHONG WEB V2.8.0: tải tên website, Tag, thông báo và playlist từ cấu hình quản trị.
async function loadPublicConfig(){
 try{const r=await fetch("/public-settings",{cache:"no-store"});const d=await r.json();if(!r.ok)return;
  const name=d.site_name||"NGUYỄN VĂN PHONG WEBSITE";const title=document.getElementById("siteTitle");if(title)title.textContent=name;document.title=name+" | PHONG WEB";
  applyPublicMeta(d);
  document.querySelectorAll("[data-tag]").forEach(el=>{
   const enabled=!(d.tags&&d.tags[el.dataset.tag]===false);
   el.classList.toggle("hidden",!enabled);
   if(el.classList.contains("tag-group"))el.style.display=enabled?"":"none";
  });
  const ann=document.getElementById("announcement");if(ann){if(d.announcement&&d.announcement.enabled&&d.announcement.message){ann.textContent="📢 "+d.announcement.message;ann.classList.remove("hidden")}else ann.classList.add("hidden")}
  if(Array.isArray(d.music_playlist)&&d.music_playlist.length){musicPlaylist=d.music_playlist.filter(x=>x.enabled!==false);currentMusicIndex=0;updateTrackName();music.volume=Math.max(0,Math.min(1,Number(d.music_volume??.7)))}
  const m=document.getElementById("maintenanceBox"),n=document.getElementById("normalHome");if(d.maintenance&&d.maintenance.enabled&&m&&n){m.textContent=d.maintenance.message||"Website đang bảo trì.";m.classList.remove("hidden");n.classList.add("hidden")}
 }catch(e){}
}
loadPublicConfig();
function updateTrackName(){const el=document.getElementById("musicTrackName");if(el)el.textContent=musicPlaylist[currentMusicIndex]?.name||"Không có bài nhạc"}
(function(){const input=document.getElementById("homeSearch"),box=document.getElementById("searchResults");if(!input||!box)return;const items=[["Trang Chủ","/","🏠"],["Hack Free Fire","/?category=freefire","🔥"],["Hack Liên Quân","/?category=lienquan","⚔️"],["Hack Roblox","/?category=roblox","🧱"],["Định Vị","/dinh-vi","📍"],["Deta","/menu","🔐"],["Proxy Mod Alen","/proxy-mod-alen-crack","🌐"],["Menu Mizze","/mizze-crack","🎮"],["Menu Nvp Crack Key","/menu-nvp-crack-key","🔑"],["Menu YSM Team Liên Quân","/menu-ysm-team-lien-quan","⚔️"],["Deta Quốc Tế","/deta-quoc-te","🌍"],["Map Liên Quân NoKey","/map-lien-quan-nokey","🗺️"],["Quản Trị","/admin","⚙️"]];input.addEventListener("input",()=>{const q=input.value.trim().toLocaleLowerCase("vi");box.innerHTML="";if(!q){box.classList.add("hidden");return}const found=items.filter(x=>x[0].toLocaleLowerCase("vi").includes(q));found.forEach(x=>{const a=document.createElement("a");a.href=x[1];a.textContent=x[2]+" "+x[0];box.append(a)});if(!found.length){const d=document.createElement("div");d.className="small";d.textContent="Không tìm thấy chức năng phù hợp.";box.append(d)}box.classList.remove("hidden")});document.addEventListener("click",e=>{if(e.target!==input&&!box.contains(e.target))box.classList.add("hidden")})})();

// Cài đặt và thông báo công khai.
async function refreshPublic(){
 try{
  const r=await fetch("/public-settings",{cache:"no-store"});
  const d=await r.json();

  for(const key of ["location","deta","proxy","mizze","detaqt","nvpkey","ysm","maplq"]){
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

// PHONG WEB V2.8.0: danh mục động, menu Tag, thẻ ảnh, số lượng và yêu thích.
window.PHONG_CATALOG = [];
function phongSlug(value){
 return String(value||"").toLowerCase().trim().replace(/[^a-z0-9\-]+/g,"-").replace(/^-+|-+$/g,"");
}
function getFavorites(){
 try{return JSON.parse(localStorage.getItem("phong_favorites")||"[]")}catch(e){return []}
}
function setFavorite(slug,active){
 const list=getFavorites().filter(x=>x!==slug);
 if(active)list.push(slug);
 try{localStorage.setItem("phong_favorites",JSON.stringify(list))}catch(e){}
}
function createCatalogCard(item){
 const a=document.createElement("a");
 a.className="tag-item-card";
 a.href=item.gate?"/?gate="+encodeURIComponent(item.slug||phongSlug(item.name)):(item.url||"#");
 if(!item.gate&&/^https:\/\//i.test(a.href)){a.target="_blank";a.rel="noopener noreferrer"}
 if(item.image){
  const img=document.createElement("img");img.src=item.image;img.alt=item.name||"";
  img.loading="lazy";img.onerror=()=>img.remove();a.append(img);
 }else{
  const icon=document.createElement("span");icon.textContent=item.icon||"📦";a.append(icon);
 }
 const b=document.createElement("b");b.textContent=item.name||"Nội dung";a.append(b);
 const small=document.createElement("small");small.textContent=item.description||"Mở nội dung";a.append(small);
 const fav=document.createElement("button");fav.type="button";fav.className="favorite-button";
 const slug=item.slug||phongSlug(item.name);const selected=getFavorites().includes(slug);
 fav.classList.toggle("active",selected);fav.textContent=selected?"★ Đã lưu":"☆ Yêu thích";
 fav.addEventListener("click",e=>{e.preventDefault();e.stopPropagation();const on=!fav.classList.contains("active");setFavorite(slug,on);fav.classList.toggle("active",on);fav.textContent=on?"★ Đã lưu":"☆ Yêu thích";});
 a.append(fav);
 return a;
}
function renderPublicCatalog(data){
 setBaseMeta(data);
 const root=document.getElementById("allTagsDirectory");
 const menuRoot=document.getElementById("dynamicTagMenu");
 if(!root)return;
 root.querySelectorAll("[data-generated-tag]").forEach(x=>x.remove());
 if(menuRoot)menuRoot.replaceChildren();
 const builtins=Object.keys(BASE_TAGS).filter(k=>!baseTagInfo(k).deleted).map(k=>({slug:k,name:baseTagInfo(k).name,icon:baseTagInfo(k).icon}));
 const custom=(data.custom_tags||[]).filter(t=>t&&t.enabled!==false);
 const tags=[...builtins,...custom];
 const content=(data.content_items||[]).filter(x=>x&&x.enabled!==false);
 window.PHONG_CATALOG=content.map(x=>({...x,slug:x.slug||phongSlug(x.name)}));
 for(const tag of tags){
  const items=content.filter(x=>String(x.tag||"").toLowerCase()===String(tag.slug).toLowerCase());
  let section=root.querySelector('.tag-group[data-tag="'+tag.slug+'"]');
  if(!section){
   section=document.createElement("section");section.className="tag-group";section.dataset.generatedTag="1";section.dataset.tag=tag.slug;
   const head=document.createElement("div");head.className="tag-group-title";
   const icon=document.createElement("span");icon.textContent=tag.icon||"🏷️";
   const wrap=document.createElement("div");const h=document.createElement("h3");h.textContent=tag.name||tag.slug;
   const sub=document.createElement("small");sub.textContent="Danh mục nội dung";wrap.append(h,sub);
   const count=document.createElement("span");count.className="tag-count";count.textContent=items.length+" mục";
   head.append(icon,wrap,count);section.append(head);
   const grid=document.createElement("div");grid.className="tag-items-grid";section.append(grid);root.append(section);
  }else{
   let count=section.querySelector(".tag-count");
   if(!count){count=document.createElement("span");count.className="tag-count";section.querySelector(".tag-group-title")?.append(count)}
   count.textContent=items.length+" mục mới";
  }
  const grid=section.querySelector(".tag-items-grid");
  if(grid){
   items.forEach(item=>grid.append(createCatalogCard(item)));
   if(items.length===0 && section.dataset.generatedTag==="1"){
    const empty=document.createElement("div");empty.className="catalog-empty";empty.textContent="Chưa có nội dung trong danh mục này.";grid.append(empty);
   }
   const countLabel=section.querySelector(".tag-count");
   if(countLabel)countLabel.textContent=grid.querySelectorAll(".tag-item-card").length+" mục";
  }
  if(menuRoot && tag.slug!=="home"){
   const link=document.createElement("a");link.href="/?tag="+encodeURIComponent(tag.slug);
   link.textContent=(tag.icon||"🏷️")+" "+(tag.name||tag.slug);
   const badge=document.createElement("span");badge.className="tag-menu-count";badge.textContent=String(items.length);
   link.append(badge);
   link.addEventListener("click",e=>{
    e.preventDefault();menu.classList.remove("show");
    history.pushState({},"","/?tag="+encodeURIComponent(tag.slug));showPage();
    setTimeout(()=>{const target=root.querySelector('[data-tag="'+tag.slug+'"]');target?.scrollIntoView({behavior:"smooth",block:"start"});},100);
   });
   menuRoot.append(link);
  }
 }
 renderBaseItems();applyBaseTagMeta();refreshTagCounts();
}
function setupDynamicSearch(){
 const input=document.getElementById("homeSearch"),box=document.getElementById("searchResults");
 if(!input||!box||input.dataset.v250==="1")return;
 input.dataset.v250="1";
 const base=[
  {name:"Trang Chủ",url:"/",icon:"🏠"},{name:"Hack Free Fire",url:"/?category=freefire",icon:"🔥"},
  {name:"Hack Liên Quân",url:"/?category=lienquan",icon:"⚔️"},{name:"Hack Roblox",url:"/?category=roblox",icon:"🧱"},
  {name:"Định Vị",url:"/dinh-vi",icon:"📍"},{name:"Deta",url:"/menu",icon:"🔐"},
  {name:"Proxy Mod Alen",url:"/proxy-mod-alen-crack",icon:"🌐"},{name:"Menu Mizze",url:"/mizze-crack",icon:"🎮"},{name:"Menu Nvp Crack Key",url:"/menu-nvp-crack-key",icon:"🔑"},{name:"Menu YSM Team Liên Quân",url:"/menu-ysm-team-lien-quan",icon:"⚔️"},{name:"Deta Quốc Tế",url:"/deta-quoc-te",icon:"🌍"},{name:"Map Liên Quân NoKey",url:"/map-lien-quan-nokey",icon:"🗺️"}
 ];
 input.addEventListener("input",()=>{
  const q=input.value.trim().toLocaleLowerCase("vi");box.replaceChildren();
  if(!q){box.classList.add("hidden");return}
  const all=[...base,...(window.PHONG_CATALOG||[]).map(x=>({name:x.name,url:x.gate?"/?gate="+encodeURIComponent(x.slug):x.url,icon:x.icon||"📦",description:x.description}))];
  const found=all.filter(x=>(x.name+" "+(x.description||"")).toLocaleLowerCase("vi").includes(q)).slice(0,20);
  found.forEach(x=>{const a=document.createElement("a");a.href=x.url||"#";a.textContent=(x.icon||"🔎")+" "+x.name;box.append(a)});
  if(!found.length){const d=document.createElement("div");d.className="catalog-empty";d.textContent="Không tìm thấy nội dung phù hợp.";box.append(d)}
  box.classList.remove("hidden");
 });
 document.addEventListener("click",e=>{if(e.target!==input&&!box.contains(e.target))box.classList.add("hidden")});
}
async function loadPublicCatalogV250(){
 try{
  const r=await fetch("/public-settings",{cache:"no-store"});const d=await r.json();
  if(r.ok){renderPublicCatalog(d);setupDynamicSearch()}
 }catch(e){console.warn("Không tải được danh mục động:",e)}
}
loadPublicCatalogV250();

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
["location","deta","proxy","mizze","detaqt","maplq"].forEach(setupCrossButton);
document.getElementById("nvpKeyCrossButton").addEventListener("click",async()=>{const b=document.getElementById("nvpKeyCrossButton"),st=document.getElementById("nvpKeyStatus");b.disabled=true;st.textContent="Đang tạo liên kết Link4M...";try{const r=await fetch("/create-short-link?destination=nvpkey&flow=nvpkey",{cache:"no-store"});const d=await r.json();if(!r.ok||!d.success)throw new Error(d.message||"Không tạo được link");window.location.href=d.url}catch(e){st.textContent=e.message;b.disabled=false}});
document.getElementById("nvpThankImage").addEventListener("click",()=>document.getElementById("nvpThankAudio").play().catch(()=>{}));
document.getElementById("nvpNextButton").addEventListener("click",async()=>{const token=new URLSearchParams(location.search).get("token");if(!token){toast("Không tìm thấy phiên vượt link.","bad");return}try{const r=await fetch("/check-session?token="+encodeURIComponent(token),{cache:"no-store"}),d=await r.json();if(!r.ok||!d.success||!d.returned)throw new Error("API chưa xác nhận vượt link thành công.");history.pushState({},"","/?nvpkey=success&token="+encodeURIComponent(token));showPage();window.scrollTo(0,0)}catch(e){toast(e.message,"bad")}});
// V2.8.0: Menu YSM Team Liên Quân (cùng luồng với Menu Nvp Crack Key).
document.getElementById("ysmCrossButton").addEventListener("click",async()=>{const b=document.getElementById("ysmCrossButton"),st=document.getElementById("ysmStatus");b.disabled=true;st.textContent="Đang tạo liên kết Link4M...";try{const r=await fetch("/create-short-link?destination=ysm&flow=ysm",{cache:"no-store"});const d=await r.json();if(!r.ok||!d.success)throw new Error(d.message||"Không tạo được link");window.location.href=d.url}catch(e){st.textContent=e.message;b.disabled=false}});
document.getElementById("ysmThankImage").addEventListener("click",()=>document.getElementById("ysmThankAudio").play().catch(()=>{}));
document.getElementById("ysmNextButton").addEventListener("click",async()=>{const token=new URLSearchParams(location.search).get("token");if(!token){toast("Không tìm thấy phiên vượt link.","bad");return}try{const r=await fetch("/check-session?token="+encodeURIComponent(token),{cache:"no-store"}),d=await r.json();if(!r.ok||!d.success||!d.returned)throw new Error("API chưa xác nhận vượt link thành công.");history.pushState({},"","/?ysm=success&token="+encodeURIComponent(token));showPage();window.scrollTo(0,0)}catch(e){toast(e.message,"bad")}});

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

 if(!token||!destination||!(destinationRoutes[destination]||isGateDest(destination))){
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
 retry.onclick=()=>navigate(isGateDest(destination)?"/?gate="+encodeURIComponent(destination.slice(2)):(destinationRoutes[destination]||"/"));
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
 if(result!=="success"||!token||!(downloadRoutes[destination]||isGateDest(destination))){
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

  action.href=isGateDest(destination)?gateDownloadHref(destination,token):downloadRoutes[destination]+"?token="+encodeURIComponent(token);
  action.classList.remove("hidden");
 }catch(e){
  showFailure(e.message,destination);
 }
}

// Menu.
const hamburger=document.getElementById("hamburgerButton");
const menu=document.getElementById("sideMenu");
const menuBackdrop=document.getElementById("menuBackdrop");
new MutationObserver(()=>menuBackdrop.classList.toggle("show",menu.classList.contains("show"))).observe(menu,{attributes:true,attributeFilter:["class"]});
document.addEventListener("keydown",e=>{if(e.key==="Escape")menu.classList.remove("show")});
hamburger.addEventListener("click",e=>{
 e.stopPropagation();menu.classList.toggle("show");
});
// Bổ sung Tag do Admin tạo vào menu 3 gạch, kèm số mục con.
(async()=>{try{const r=await fetch("/public-settings",{cache:"no-store"}),d=await r.json();for(const tag of []){if(tag.enabled===false)continue;const count=(d.content_items||[]).filter(x=>x.tag===tag.slug&&x.enabled!==false).length;const a=document.createElement("a");a.href="/?custom_tag="+encodeURIComponent(tag.slug);a.textContent=(tag.icon||"🏷️")+" "+tag.name+" ("+count+")";a.onclick=e=>{e.preventDefault();menu.classList.remove("show");navigateCategory("home");const section=[...document.querySelectorAll(".tag-group")].find(x=>x.dataset.customTag===tag.slug);if(section)section.scrollIntoView({behavior:"smooth"})};menu.insertBefore(a,menu.querySelector('a[href="/admin"]'))}}catch(e){}})();
document.getElementById("homeMenuButton").addEventListener("click",e=>{
 e.preventDefault();navigateCategory("home");
});
document.getElementById("freeFireMenuButton").addEventListener("click",e=>{
 e.preventDefault();navigateCategory("freefire");
});
document.getElementById("lienQuanMenuButton").addEventListener("click",e=>{
 e.preventDefault();navigateCategory("lienquan");
});
document.getElementById("robloxMenuButton").addEventListener("click",e=>{
 e.preventDefault();navigateCategory("roblox");
});
document.addEventListener("click",e=>{
 if(!menu.contains(e.target)&&!hamburger.contains(e.target)){
  menu.classList.remove("show");
 }
});

// Trình phát nhạc nền: bài cũ + Nhạc1 + Nhạc2, tự chuyển bài và lặp toàn bộ.
const music=document.getElementById("backgroundMusic");
const musicButton=document.getElementById("musicButton");
const musicPlayer=document.getElementById("musicPlayer");
const musicIcon=document.getElementById("musicIcon");
let musicPlaylist=[
 {name:"Nhạc nền",src:"/music.mp3",enabled:true},
 {name:"Nhạc1",src:"/Nhac1.mp3",enabled:true},
 {name:"Nhạc2",src:"/Nhac2.mp3",enabled:true}
];
let currentMusicIndex=0;
let musicStarted=false;

function setMusicPlaying(playing){
 musicIcon.textContent=playing?"Ⅱ":"▶";
 musicPlayer.classList.toggle("playing",playing);
 musicButton.setAttribute("aria-label",playing?"Tạm dừng nhạc":"Phát nhạc");
}

async function playPlaylistTrack(index){
 currentMusicIndex=(index+musicPlaylist.length)%musicPlaylist.length;
 music.src=musicPlaylist[currentMusicIndex].src;
 updateTrackName();
 music.load();
 try{
  await music.play();
  musicStarted=true;
  setMusicPlaying(true);
 }catch(error){
  setMusicPlaying(false);
  toast("Không thể phát "+musicPlaylist[currentMusicIndex].name+
        ". Hãy kiểm tra file MP3 đã được tải lên máy chủ.","bad");
 }
}

musicButton.addEventListener("click",async()=>{
 if(music.paused){
  if(!musicStarted){
   await playPlaylistTrack(currentMusicIndex);
  }else{
   try{
    await music.play();
    setMusicPlaying(true);
   }catch(error){
    setMusicPlaying(false);
    toast("Không thể tiếp tục phát nhạc.","bad");
   }
  }
 }else{
  music.pause();
  setMusicPlaying(false);
 }
});

// Tự động phát bài kế tiếp; hết bài cuối quay lại bài đầu (lặp tất cả).
music.addEventListener("ended",()=>{
 playPlaylistTrack((currentMusicIndex+1)%musicPlaylist.length);
});
music.addEventListener("pause",()=>{
 if(music.ended===false)setMusicPlaying(false);
});
music.addEventListener("play",()=>setMusicPlaying(true));
const musicMinimize=document.getElementById("musicMinimize"),musicRestore=document.getElementById("musicRestore");
musicMinimize.addEventListener("click",e=>{e.stopPropagation();musicPlayer.classList.add("minimized");musicRestore.classList.remove("hidden")});
musicRestore.addEventListener("click",()=>{musicPlayer.classList.remove("minimized");musicRestore.classList.add("hidden")});
(function(){let active=false,sx=0,sy=0,l=0,t=0;try{const v=JSON.parse(localStorage.getItem("phong_music_position")||"null");if(v){musicPlayer.style.left=v.left+"px";musicPlayer.style.top=v.top+"px";musicPlayer.style.right="auto";musicPlayer.style.bottom="auto"}}catch(e){}musicPlayer.addEventListener("pointerdown",e=>{if(e.target.closest("button"))return;const r=musicPlayer.getBoundingClientRect();active=true;sx=e.clientX;sy=e.clientY;l=r.left;t=r.top;musicPlayer.classList.add("dragging")});musicPlayer.addEventListener("pointermove",e=>{if(!active)return;const x=Math.max(0,Math.min(innerWidth-musicPlayer.offsetWidth,l+e.clientX-sx)),y=Math.max(0,Math.min(innerHeight-musicPlayer.offsetHeight,t+e.clientY-sy));musicPlayer.style.left=x+"px";musicPlayer.style.top=y+"px";musicPlayer.style.right="auto";musicPlayer.style.bottom="auto"});function end(){if(!active)return;active=false;musicPlayer.classList.remove("dragging");const r=musicPlayer.getBoundingClientRect();try{localStorage.setItem("phong_music_position",JSON.stringify({left:r.left,top:r.top}))}catch(e){}}musicPlayer.addEventListener("pointerup",end);musicPlayer.addEventListener("pointercancel",end)})();

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
<title>PHONG WEB V2.8.2 ADMIN</title>
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
/* V2.8.0: vuông góc */

</style>
</head>
<body>
<main>
<h1>⚙️ PHONG WEB V2.8.2 - ADMIN</h1>
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
 <button onclick="tab('site',this)">🎵 Nhạc & Giao diện</button>
 <button onclick="tab('tags',this)">🏷️ Quản lý Tag</button>
 <button onclick="tab('content',this)">🧩 Nội dung web</button>
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
  <button onclick="loadStats()">LÀM MỚI</button><button onclick="exportCSV()">⬇ XUẤT CSV</button>
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
  <p class="small">Bật/tắt, đổi link nút LẤY FILE của tất cả các mục (MediaFire, Zufile hoặc link HTTPS khác) và cập nhật thông tin file.</p>
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
  <h2>🧾 BẢNG THÔNG BÁO TRANG CHÍNH</h2>
  <p class="small">Các thông báo đang bật sẽ hiển thị trong "BẢNG THÔNG BÁO" ở Trang Chủ. Thông báo mới nằm trên cùng. Tối đa 30 thông báo, mỗi thông báo tối đa 500 ký tự.</p>
  <div id="noticeItems"></div>
  <textarea id="newNoticeText" maxlength="500" placeholder="Nội dung thông báo mới..."></textarea>
  <button onclick="addNotice()">➕ THÊM THÔNG BÁO</button>
  <button class="good" onclick="saveNotices()">LƯU BẢNG THÔNG BÁO</button>
 </div>
 <div class="panel">
  <h2>🛠️ CHẾ ĐỘ BẢO TRÌ</h2>
  <label><input type="checkbox" id="maintenanceEnabled"> Bật chế độ bảo trì</label>
  <textarea id="maintenanceMessage" placeholder="Thông báo bảo trì..."></textarea>
  <button class="warning" onclick="saveMaintenance()">LƯU BẢO TRÌ</button>
 </div>
</section>

<section class="tabpage hidden" id="site">
 <div class="panel"><h2>🏷️ TÊN WEBSITE & QUẢN LÝ TAG</h2>
  <label>Tên website<input id="siteName" maxlength="80"></label>
  <div class="row"><label><input type="checkbox" id="tagHome"> Trang Chủ</label><label><input type="checkbox" id="tagFreefire"> Hack Free Fire</label></div>
  <div class="row"><label><input type="checkbox" id="tagLienquan"> Hack Liên Quân</label><label><input type="checkbox" id="tagRoblox"> Hack Roblox</label></div>
  <button class="good" onclick="saveSiteConfig()">LƯU TÊN & TAG</button>
 </div>
 <div class="panel"><h2>🎵 QUẢN LÝ NHẠC</h2><p class="small">Nhập tên và đường dẫn MP3 nội bộ hoặc URL HTTPS. Tối đa 50 bài.</p>
  <label>Âm lượng mặc định: <input id="musicVolume" type="range" min="0" max="100" value="70" oninput="document.getElementById('musicVolumeValue').textContent=this.value+'%'"></label><span id="musicVolumeValue" class="small">70%</span>
  <div id="musicItems"></div><div class="row"><input id="newMusicName" placeholder="Tên bài nhạc"><input id="newMusicSrc" placeholder="/music.mp3 hoặc URL HTTPS"><button onclick="addMusicTrack()">THÊM BÀI</button></div>
  <button class="good" onclick="saveSiteConfig()">LƯU DANH SÁCH NHẠC</button></div>
</section>
<section class="tabpage hidden" id="tags">
 <div class="panel"><h2>🏷️ QUẢN LÝ DANH MỤC TAG</h2><p class="small">Kéo thả để đổi thứ tự. Có thể bật/tắt, đổi tên hoặc xóa Tag.</p>
 <h3>🔒 Tag gốc của hệ thống</h3><p class="small">Sửa tên/icon, bật/tắt, xóa (ẩn) hoặc khôi phục. Xóa Tag sẽ ẩn các mục thuộc Tag đó; hãy chuyển mục sang Tag khác ở tab Nội dung web nếu muốn giữ.</p><div id="baseTagItems"></div><h3>🏷️ Tag tùy chỉnh</h3><div id="tagItems"></div><div class="row"><input id="newTagName" placeholder="Tên Tag"><input id="newTagSlug" placeholder="Đường dẫn slug (vd: cong-cu)"><input id="newTagIcon" placeholder="Icon" value="🏷️"><button onclick="addTag()">THÊM TAG</button></div><button class="good" onclick="saveTags()">LƯU DANH MỤC</button></div>
</section>
<section class="tabpage hidden" id="content">
 <div class="panel"><h2>🧩 QUẢN LÝ NỘI DUNG WEBSITE</h2><p class="small">Thêm hoặc sửa mục tải. URL tải phải là HTTP/HTTPS; ảnh có thể là đường dẫn nội bộ hoặc HTTPS.</p>
 <h3>🔒 Mục gốc của hệ thống</h3><p class="small">Sửa tên, icon, mô tả, đổi Tag hoặc xóa (ẩn)/khôi phục. Link nút LẤY FILE và thông tin file chỉnh ở tab Quản lý file.</p><div id="baseItemItems"></div><h3>🧩 Mục tùy chỉnh</h3><div id="contentItems"></div><div class="row"><input id="newContentName" placeholder="Tên mục"><input id="newContentSlug" placeholder="Slug"><select id="newContentTag"></select></div><textarea id="newContentDesc" placeholder="Mô tả"></textarea><label><input type="checkbox" id="newContentGate" checked> Bắt buộc vượt link Link4M trước khi LẤY FILE</label><div class="row"><input id="newContentImage" placeholder="Ảnh đại diện /logo.png"><input id="newContentUrl" placeholder="Đường dẫn tải HTTPS"></div><button onclick="addContent()">THÊM MỤC</button><button class="good" onclick="saveContent()">LƯU NỘI DUNG</button></div>
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
  <p class="small">Phiên tự hết hạn sau 30 phút không hoạt động hoặc tối đa 8 giờ. Tối đa 3 phiên Admin cùng lúc.</p>
  <button class="warning" onclick="revokeOtherSessions()">🚫 THU HỒI PHIÊN KHÁC</button>
  <button class="danger" onclick="logout()">ĐĂNG XUẤT</button>
 </div>
 <div class="panel">
  <h2>🗄️ SAO LƯU & KHÔI PHỤC CẤU HÌNH — V2.8.2</h2>
  <p class="small">Tải bản sao lưu các thiết lập website, danh mục, nội dung, nhạc và thông báo. Khi khôi phục, dữ liệu thống kê, lịch sử và nhật ký bảo mật sẽ được giữ nguyên.</p>
  <div class="row">
   <button class="good" onclick="downloadBackup()">⬇ TẢI BACKUP JSON</button>
   <input type="file" id="backupFile" accept=".json,application/json">
   <button class="warning" onclick="restoreBackup()">↻ KHÔI PHỤC BACKUP</button>
  </div>
  <p class="small">Chỉ chọn file JSON được xuất từ PHONG WEB. Hãy tải backup hiện tại trước khi khôi phục.</p>
  <div id="backupStatus" class="small" aria-live="polite"></div>
 </div>
 <div class="panel">
  <h2>🧭 KIỂM TRA CẤU HÌNH</h2>
  <p class="small">Kiểm tra nhanh cấu trúc dữ liệu website và số lượng nội dung đang quản lý.</p>
  <button onclick="runConfigCheck()">🔎 KIỂM TRA NGAY</button>
  <div id="configCheckResult" class="small" aria-live="polite"></div>
 </div>
</section>
</div>

<div id="message"></div>
<p><a href="/">← Quay lại website</a></p>
</main>

<script>
let config={};
let csrfToken="";
let musicAdminList=[];
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
  loadHistory(),loadAdminLogs(),loadChart(),loadSiteConfig(),loadTags(),loadContent(),loadBaseMeta(),loadNotices()
 ]);
}

async function loadSiteConfig(){try{const d=await api("/admin/site-config");document.getElementById("siteName").value=d.site_name||"";document.getElementById("tagHome").checked=!!d.tags.home;document.getElementById("tagFreefire").checked=!!d.tags.freefire;document.getElementById("tagLienquan").checked=!!d.tags.lienquan;document.getElementById("tagRoblox").checked=!!d.tags.roblox;musicAdminList=Array.isArray(d.music_playlist)?d.music_playlist:[];document.getElementById("musicVolume").value=Math.round((d.music_volume??.7)*100);document.getElementById("musicVolumeValue").textContent=document.getElementById("musicVolume").value+"%";renderMusicItems()}catch(e){message(e.message,true)}}
function renderMusicItems(){const root=document.getElementById("musicItems");root.innerHTML="";musicAdminList.forEach((track,i)=>{const box=document.createElement("div");box.className="item";box.draggable=true;box.dataset.index=i;box.ondragstart=e=>{e.dataTransfer.setData("text/plain",String(i));box.style.opacity=".5"};box.ondragend=()=>box.style.opacity="1";box.ondragover=e=>e.preventDefault();box.ondrop=e=>{e.preventDefault();const from=Number(e.dataTransfer.getData("text/plain"));const [moved]=musicAdminList.splice(from,1);musicAdminList.splice(i,0,moved);renderMusicItems()};const heading=document.createElement("b");heading.textContent="☰ Bài "+(i+1)+" – Kéo để sắp xếp";const name=document.createElement("input");name.value=track.name||"";name.placeholder="Tên bài";name.oninput=()=>musicAdminList[i].name=name.value;const src=document.createElement("input");src.value=track.src||"";src.placeholder="Đường dẫn MP3";src.oninput=()=>musicAdminList[i].src=src.value;const enabled=document.createElement("label");const check=document.createElement("input");check.type="checkbox";check.checked=track.enabled!==false;check.onchange=()=>musicAdminList[i].enabled=check.checked;enabled.append(check,document.createTextNode(" Bật bài nhạc"));const preview=document.createElement("button");preview.textContent="▶ PHÁT THỬ";preview.onclick=()=>{const a=new Audio(src.value);a.volume=Number(document.getElementById("musicVolume").value)/100;a.play().catch(()=>message("Không phát được file nhạc. Kiểm tra URL.",true))};const del=document.createElement("button");del.className="danger";del.textContent="XÓA";del.onclick=()=>{musicAdminList.splice(i,1);renderMusicItems()};box.append(heading,name,src,enabled,preview,del);root.append(box)})}
function addMusicTrack(){const name=document.getElementById("newMusicName").value.trim(),src=document.getElementById("newMusicSrc").value.trim();if(!name||!src){message("Hãy nhập tên và đường dẫn bài nhạc.",true);return}if(musicAdminList.length>=50){message("Tối đa 50 bài nhạc.",true);return}musicAdminList.push({name,src,enabled:true});document.getElementById("newMusicName").value="";document.getElementById("newMusicSrc").value="";renderMusicItems()}
async function saveSiteConfig(){try{const payload={site_name:document.getElementById("siteName").value.trim(),tags:{home:document.getElementById("tagHome").checked,freefire:document.getElementById("tagFreefire").checked,lienquan:document.getElementById("tagLienquan").checked,roblox:document.getElementById("tagRoblox").checked},music_playlist:musicAdminList,music_volume:Number(document.getElementById("musicVolume").value)/100};const d=await api("/admin/site-config",payload);message(d.message||"Đã lưu.");await loadSiteConfig()}catch(e){message(e.message,true)}}

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
  url.value=item.url;url.placeholder="https://www.mediafire.com/... hoặc https://zufile.com/...";

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
  const l1=document.createElement("label");l1.textContent="Link nút LẤY FILE (đổi được)";l1.append(url);
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

async function revokeOtherSessions(){
 if(!confirm("Thu hồi tất cả phiên Admin khác? Phiên hiện tại vẫn được giữ."))return;
 try{const d=await api("/admin/revoke-sessions",{});message(d.message||"Đã thu hồi các phiên khác.");}
 catch(e){message(e.message,true);}
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


let tagAdminList=[],contentAdminList=[],baseTagList=[],baseItemList=[],noticeAdminList=[];
function tagChoices(current){const base=[["","(Không thuộc Tag nào)"]];if(baseTagList.length){baseTagList.forEach(t=>{if(!t.deleted)base.push([t.slug,(t.icon||"🏷️")+" "+t.name])})}else{base.push(["freefire","🔥 Hack Free Fire"],["lienquan","⚔️ Hack Liên Quân"],["roblox","🧱 Hack Roblox"])}tagAdminList.forEach(t=>{if(t.slug)base.push([t.slug,(t.icon||"🏷️")+" "+t.name])});if(current&&!base.some(x=>x[0]===current))base.push([current,current]);return base}
function fillNewTagSelect(){const s=document.getElementById("newContentTag");if(!s)return;const cur=s.value;s.replaceChildren();tagChoices(cur).forEach(([val,text])=>{const o=document.createElement("option");o.value=val;o.textContent=text;s.append(o)});s.value=cur||"freefire"}
async function loadTags(){try{const d=await api("/admin/tags");tagAdminList=d.items||[];renderTags();renderContent();renderBaseItemRows()}catch(e){message(e.message,true)}}
function renderTags(){const root=document.getElementById("tagItems");root.innerHTML="";tagAdminList.forEach((t,i)=>{const box=document.createElement("div");box.className="item";box.draggable=true;box.ondragstart=e=>e.dataTransfer.setData("text/plain",String(i));box.ondragover=e=>e.preventDefault();box.ondrop=e=>{e.preventDefault();const n=Number(e.dataTransfer.getData("text/plain"));const [v]=tagAdminList.splice(n,1);tagAdminList.splice(i,0,v);renderTags()};const row=document.createElement("div");row.className="row";const icon=document.createElement("input");icon.value=t.icon||"🏷️";icon.oninput=()=>t.icon=icon.value;const name=document.createElement("input");name.value=t.name;name.oninput=()=>t.name=name.value;const slug=document.createElement("input");slug.value=t.slug;slug.oninput=()=>t.slug=slug.value;const enabled=document.createElement("input");enabled.type="checkbox";enabled.checked=t.enabled!==false;enabled.onchange=()=>t.enabled=enabled.checked;const del=document.createElement("button");del.className="danger";del.textContent="XÓA";del.onclick=()=>{tagAdminList.splice(i,1);renderTags()};row.append(icon,name,slug,enabled,del);box.append(row);root.append(box)})}
function addTag(){const name=document.getElementById("newTagName").value.trim(),slug=document.getElementById("newTagSlug").value.trim().toLowerCase(),icon=document.getElementById("newTagIcon").value.trim()||"🏷️";if(!name||!slug){message("Nhập tên và slug Tag.",true);return}tagAdminList.push({name,slug,icon,enabled:true});renderTags();document.getElementById("newTagName").value="";document.getElementById("newTagSlug").value=""}
async function saveTags(){try{await saveBaseMeta();const d=await api("/admin/tags",{items:tagAdminList});message(d.message);await Promise.all([loadBaseMeta(),loadTags(),loadSiteConfig()])}catch(e){message(e.message,true)}}
async function loadContent(){try{const d=await api("/admin/content");contentAdminList=d.items||[];renderContent()}catch(e){message(e.message,true)}}
function renderContent(){const root=document.getElementById("contentItems");root.innerHTML="";fillNewTagSelect();contentAdminList.forEach((v,i)=>{const box=document.createElement("div");box.className="item";box.draggable=true;box.ondragstart=e=>e.dataTransfer.setData("text/plain",String(i));box.ondragover=e=>e.preventDefault();box.ondrop=e=>{e.preventDefault();const n=Number(e.dataTransfer.getData("text/plain"));const [m]=contentAdminList.splice(n,1);contentAdminList.splice(i,0,m);renderContent()};const drag=document.createElement("b");drag.textContent="☰ Mục "+(i+1)+" – Kéo để sắp xếp";box.append(drag);const labels={name:"Tên mục",slug:"Slug (chữ thường, số, dấu -)",tag:"Thuộc Tag",description:"Mô tả",image:"Ảnh đại diện (/logo.png hoặc URL HTTPS)",url:"Đường dẫn nút LẤY FILE (HTTPS)"};const fields=["name","slug","tag","description","image","url"];fields.forEach(k=>{const cap=document.createElement("label");cap.textContent=labels[k];let el;if(k==="tag"){el=document.createElement("select");tagChoices(v[k]).forEach(([val,text])=>{const o=document.createElement("option");o.value=val;o.textContent=text;el.append(o)});el.value=v[k]||"";el.onchange=()=>v[k]=el.value}else{el=document.createElement(k==="description"?"textarea":"input");el.value=v[k]||"";el.placeholder=labels[k];el.oninput=()=>v[k]=el.value}cap.append(el);box.append(cap)});const enabled=document.createElement("input");enabled.type="checkbox";enabled.checked=v.enabled!==false;enabled.onchange=()=>v.enabled=enabled.checked;const label=document.createElement("label");label.append(enabled,document.createTextNode(" Hiển thị mục này"));const del=document.createElement("button");del.className="danger";del.textContent="XÓA MỤC";del.onclick=()=>{contentAdminList.splice(i,1);renderContent()};const gateBox=document.createElement("input");gateBox.type="checkbox";gateBox.checked=v.gate===true;gateBox.onchange=()=>v.gate=gateBox.checked;const gateLabel=document.createElement("label");gateLabel.append(gateBox,document.createTextNode(" Bắt buộc vượt link Link4M trước khi LẤY FILE"));const dl=document.createElement("p");dl.className="small";dl.textContent="Lượt lấy file: "+Number(v.downloads||0);box.append(label,gateLabel,dl,del);root.append(box)})}
function addContent(){const v={name:document.getElementById("newContentName").value.trim(),slug:document.getElementById("newContentSlug").value.trim().toLowerCase(),tag:document.getElementById("newContentTag").value.trim().toLowerCase(),description:document.getElementById("newContentDesc").value.trim(),image:document.getElementById("newContentImage").value.trim()||"/logo.png",url:document.getElementById("newContentUrl").value.trim(),enabled:true,gate:document.getElementById("newContentGate").checked};if(v.gate&&!/^https:\/\//i.test(v.url)){message("Mục bắt buộc vượt link cần đường dẫn HTTPS.",true);return}if(!v.name||!v.slug||!v.url){message("Nhập tên, slug và đường dẫn tải.",true);return}contentAdminList.push(v);renderContent();["newContentName","newContentSlug","newContentTag","newContentDesc","newContentImage","newContentUrl"].forEach(id=>document.getElementById(id).value="")}
async function saveContent(){try{await saveBaseMeta();const d=await api("/admin/content",{items:contentAdminList});message(d.message);await Promise.all([loadBaseMeta(),loadContent()])}catch(e){message(e.message,true)}}
function exportCSV(){location.href="/admin/export.csv"}
async function downloadBackup(){
 const status=document.getElementById("backupStatus");
 try{
  status.textContent="Đang tạo bản sao lưu...";
  const response=await fetch("/admin/backup.json",{cache:"no-store",credentials:"same-origin"});
  if(!response.ok){let d={};try{d=await response.json()}catch(e){}throw new Error(d.message||"Không thể tải backup.");}
  const blob=await response.blob(),url=URL.createObjectURL(blob),a=document.createElement("a");
  a.href=url;a.download="phong-web-backup-"+new Date().toISOString().slice(0,10)+".json";
  document.body.appendChild(a);a.click();a.remove();URL.revokeObjectURL(url);
  status.textContent="Đã tải bản sao lưu cấu hình.";
 }catch(e){status.textContent=e.message;message(e.message,true);}
}
async function restoreBackup(){
 const input=document.getElementById("backupFile"),status=document.getElementById("backupStatus"),file=input.files&&input.files[0];
 if(!file){message("Hãy chọn file backup JSON trước.",true);return;}
 if(file.size>2*1024*1024){message("File backup vượt quá giới hạn 2 MB.",true);return;}
 if(!confirm("Khôi phục cấu hình từ file đã chọn? Các thiết lập hiện tại sẽ được thay thế. Thống kê và lịch sử được giữ nguyên."))return;
 try{
  const raw=await file.text(),payload=JSON.parse(raw);
  if(payload.format!=="PHONG_WEB_BACKUP"||(payload.version!=="2.6.0"&&payload.version!=="2.7.0"&&payload.version!=="2.7.1"&&payload.version!=="2.7.2"&&payload.version!=="2.8.0"&&payload.version!=="2.8.1")||!payload.config)throw new Error("File backup không đúng định dạng PHONG WEB V2.8.2.");
  const result=await api("/admin/restore-backup",payload);
  status.textContent=result.message||"Khôi phục thành công.";
  input.value="";
  await Promise.all([loadSettings(),loadSiteConfig(),loadTags(),loadContent(),loadNotice(),loadBaseMeta(),loadNotices()]);
  message("Đã khôi phục cấu hình. Thống kê và lịch sử không bị thay đổi.");
 }catch(e){status.textContent=e.message;message(e.message,true);}
}
async function runConfigCheck(){
 const root=document.getElementById("configCheckResult");
 try{
  const [a,b,c,d]=await Promise.all([api("/admin/settings"),api("/admin/site-config"),api("/admin/tags"),api("/admin/content")]);
  const destinations=Object.keys(a.items||{}).length,tags=(c.items||[]).length,contents=(d.items||[]).length,tracks=(b.music_playlist||[]).length;
  root.textContent="✓ Kết nối Admin OK · "+destinations+" mục tải · "+tags+" Tag · "+contents+" nội dung · "+tracks+" bài nhạc.";
 }catch(e){root.textContent="✕ Kiểm tra thất bại: "+e.message;}
}

// ===== V2.8.1: Tag gốc / Mục gốc sửa-xóa-khôi phục + Bảng thông báo =====
async function loadBaseMeta(){try{const d=await api("/admin/base-meta");baseTagList=d.tags||[];baseItemList=d.items||[];renderBaseTagRows();renderBaseItemRows();fillNewTagSelect()}catch(e){message(e.message,true)}}
async function saveBaseMeta(){return api("/admin/base-meta",{tags:baseTagList.map(t=>({slug:t.slug,name:t.name,icon:t.icon,enabled:t.enabled!==false,deleted:t.deleted===true})),items:baseItemList.map(x=>({key:x.key,name:x.name,icon:x.icon,description:x.description,tag:x.tag,deleted:x.deleted===true}))})}
function renderBaseTagRows(){const root=document.getElementById("baseTagItems");if(!root)return;root.innerHTML="";baseTagList.forEach(t=>{const box=document.createElement("div");box.className="item";if(t.deleted)box.style.opacity=".55";const row=document.createElement("div");row.className="row";const icon=document.createElement("input");icon.value=t.icon||"";icon.placeholder="Icon";icon.oninput=()=>t.icon=icon.value;const name=document.createElement("input");name.value=t.name||"";name.placeholder="Tên Tag";name.oninput=()=>t.name=name.value;const slug=document.createElement("span");slug.className="small";slug.textContent="slug: "+t.slug+(t.deleted?" (ĐÃ XÓA)":"");const en=document.createElement("input");en.type="checkbox";en.checked=t.enabled!==false;en.onchange=()=>t.enabled=en.checked;const enLabel=document.createElement("label");enLabel.append(en,document.createTextNode(" Bật"));const btn=document.createElement("button");if(t.deleted){btn.className="good";btn.textContent="KHÔI PHỤC";btn.onclick=()=>{t.deleted=false;renderBaseTagRows();renderBaseItemRows();fillNewTagSelect()}}else{btn.className="danger";btn.textContent="XÓA";btn.onclick=()=>{if(!confirm("Xóa Tag "+t.name+"? Các mục thuộc Tag này sẽ bị ẩn khỏi website (có thể khôi phục lại). Bấm LƯU DANH MỤC để áp dụng."))return;t.deleted=true;renderBaseTagRows();renderBaseItemRows();fillNewTagSelect()}}row.append(icon,name,slug,enLabel,btn);box.append(row);root.append(box)})}
function renderBaseItemRows(){const root=document.getElementById("baseItemItems");if(!root)return;root.innerHTML="";baseItemList.forEach(x=>{const box=document.createElement("div");box.className="item";if(x.deleted)box.style.opacity=".55";const head=document.createElement("b");head.textContent="🔒 Mục gốc: "+x.key+" ("+x.route+")"+(x.deleted?" – ĐÃ XÓA":"");box.append(head);[["name","Tên mục"],["icon","Icon"],["description","Mô tả ngắn"]].forEach(([k,label])=>{const cap=document.createElement("label");cap.textContent=label;const el=document.createElement("input");el.value=x[k]||"";el.oninput=()=>x[k]=el.value;cap.append(el);box.append(cap)});const capTag=document.createElement("label");capTag.textContent="Thuộc Tag";const sel=document.createElement("select");tagChoices(x.tag).filter(o=>o[0]).forEach(([val,text])=>{const o=document.createElement("option");o.value=val;o.textContent=text;sel.append(o)});sel.value=x.tag;sel.onchange=()=>x.tag=sel.value;capTag.append(sel);box.append(capTag);const btn=document.createElement("button");if(x.deleted){btn.className="good";btn.textContent="KHÔI PHỤC MỤC";btn.onclick=()=>{x.deleted=false;renderBaseItemRows()}}else{btn.className="danger";btn.textContent="XÓA MỤC";btn.onclick=()=>{if(!confirm("Xóa mục "+x.name+"? Mục sẽ bị ẩn và không thể vượt link/lấy file (có thể khôi phục). Bấm LƯU NỘI DUNG để áp dụng."))return;x.deleted=true;renderBaseItemRows()}}box.append(btn);root.append(box)})}
async function loadNotices(){try{const d=await api("/admin/notices");noticeAdminList=d.items||[];renderNoticeRows()}catch(e){message(e.message,true)}}
function renderNoticeRows(){const root=document.getElementById("noticeItems");if(!root)return;root.innerHTML="";noticeAdminList.forEach((n,i)=>{const box=document.createElement("div");box.className="item";const head=document.createElement("b");head.textContent="📢 Thông báo "+(i+1)+(n.time?" · "+n.time:" · (mới)");const ta=document.createElement("textarea");ta.maxLength=500;ta.value=n.text||"";ta.oninput=()=>n.text=ta.value;const en=document.createElement("input");en.type="checkbox";en.checked=n.enabled!==false;en.onchange=()=>n.enabled=en.checked;const lab=document.createElement("label");lab.append(en,document.createTextNode(" Hiển thị trên bảng thông báo"));const up=document.createElement("button");up.textContent="▲";up.onclick=()=>{if(i>0){[noticeAdminList[i-1],noticeAdminList[i]]=[noticeAdminList[i],noticeAdminList[i-1]];renderNoticeRows()}};const dn=document.createElement("button");dn.textContent="▼";dn.onclick=()=>{if(i<noticeAdminList.length-1){[noticeAdminList[i+1],noticeAdminList[i]]=[noticeAdminList[i],noticeAdminList[i+1]];renderNoticeRows()}};const del=document.createElement("button");del.className="danger";del.textContent="XÓA";del.onclick=()=>{noticeAdminList.splice(i,1);renderNoticeRows()};box.append(head,ta,lab,up,dn,del);root.append(box)})}
function addNotice(){const ta=document.getElementById("newNoticeText"),text=ta.value.trim();if(!text){message("Hãy nhập nội dung thông báo.",true);return}if(noticeAdminList.length>=30){message("Tối đa 30 thông báo.",true);return}noticeAdminList.unshift({text,enabled:true,time:""});ta.value="";renderNoticeRows()}
async function saveNotices(){try{const d=await api("/admin/notices",{items:noticeAdminList});message(d.message);await loadNotices()}catch(e){message(e.message,true)}}

checkAdmin();
</script>
</body>
</html>
"""


# =========================================================
# HTTP SERVER
# =========================================================

class Website(BaseHTTPRequestHandler):

    server_version = "PhongWeb/2.8.2"
    sys_version = ""

    def client_ip(self):
        # Không tin X-Forwarded-For do client có thể tự giả mạo.
        # Khi chạy sau proxy, đây có thể là IP của proxy.
        return self.client_address[0]

    def send_security_headers(self):
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("X-Frame-Options", "DENY")
        self.send_header("Cross-Origin-Resource-Policy", "same-origin")
        self.send_header("Cross-Origin-Opener-Policy", "same-origin")
        self.send_header("X-Permitted-Cross-Domain-Policies", "none")
        if SITE_URL.startswith("https://"):
            self.send_header("Strict-Transport-Security", "max-age=31536000; includeSubDomains")
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
            "media-src 'self' https:; frame-ancestors 'none'"
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

        if length <= 0 or length > MAX_REQUEST_BODY:
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

            now = time.time()
            if now - session["created"] > ADMIN_TTL:
                ADMIN_SESSIONS.pop(token, None)
                return False
            if now - session.get("last_seen", session["created"]) > ADMIN_IDLE_TTL:
                ADMIN_SESSIONS.pop(token, None)
                return False
            session["last_seen"] = now
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

        origin = self.headers.get("Origin", "").strip()
        if origin:
            origin_host = urlsplit(origin).netloc.lower()
            request_host = self.headers.get("Host", "").lower()
            configured_host = urlsplit(SITE_URL).netloc.lower()
            if origin_host not in {h for h in (request_host, configured_host) if h}:
                self.send_json(403, {"success": False, "message": "Yêu cầu khác nguồn bị từ chối."})
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
            "/proxy-mod-alen-crack", "/mizze-crack", "/menu-nvp-crack-key",
            "/menu-ysm-team-lien-quan", "/deta-quoc-te", "/map-lien-quan-nokey"
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
                    key: (
                        destination_enabled(key)
                        and not meta_flag_deleted(data.get("item_meta"), key)
                    )
                    for key in DEFAULT_DESTINATIONS
                },
                "files": files,
                "announcement": data["announcement"],
                "maintenance": data["maintenance"],
                "site_name": data["settings"].get("site_name", "NGUYỄN VĂN PHONG WEBSITE"),
                "tags": {key: data["settings"].get("tag_" + key, "1") == "1" for key in ("home", "freefire", "lienquan", "roblox")},
                "music_playlist": data.get("music_playlist", []),
                "music_volume": data.get("music_volume", 0.7),
                "custom_tags": data.get("tags_custom", []),
                "tag_meta": data.get("tag_meta", {}),
                "item_meta": data.get("item_meta", {}),
                "notices": [
                    x for x in data.get("notices", [])
                    if isinstance(x, dict) and x.get("enabled") is not False
                ],
                "content_items": [public_content_item(x) for x in data.get("content_items", []) if isinstance(x, dict)]
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
            flow = query.get("flow", [""])[0].lower()

            if provider != "link4m":
                self.send_json(400, {
                    "success": False,
                    "message": "PHONG WEB V2.3 chỉ hỗ trợ Link4M."
                })
                return

            is_content = destination.startswith("c_")

            if is_content:
                content_item = find_content_item(destination[2:])

                if (
                    not content_item
                    or content_item.get("enabled") is False
                    or not content_item.get("gate")
                    or not validate_download_url(content_item.get("url"))
                ):
                    self.send_json(400, {
                        "success": False,
                        "message": "Mục tải file không hợp lệ hoặc không yêu cầu vượt link."
                    })
                    return

            if not is_content and destination not in DEFAULT_DESTINATIONS:
                self.send_json(400, {
                    "success": False,
                    "message": "Mục đích vượt link không hợp lệ."
                })
                return

            if not is_content and not destination_enabled(destination):
                self.send_json(403, {
                    "success": False,
                    "message": "Mục này hiện đang tạm khóa."
                })
                return

            if not is_content and destination_deleted(destination):
                self.send_json(404, {
                    "success": False,
                    "message": "Mục này đã bị xóa."
                })
                return

            file_info = {"status": "available"} if is_content else get_file_settings().get(destination, {})

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
                        "destination": destination,
                        "flow": flow
                    }

                add_history(
                    "create", destination,
                    "Đã tạo liên kết Link4M", ip
                )

                print("[V2.3] LINK CREATED:", destination)

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

            print("[V2.3] CALLBACK:", destination)

            flow = ""
            with LOCK:
                flow = SESSIONS.get(token, {}).get("flow", "")
            if flow == "nvpkey":
                self.redirect("/?nvpkey=thanks&token=" + quote(token, safe=""))
            elif flow == "ysm":
                self.redirect("/?ysm=thanks&token=" + quote(token, safe=""))
            else:
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

        # V2.8.0: tải mục nội dung do Admin thêm (gate = bắt buộc vượt Link4M).
        if path == "/download-content":
            slug = safe_text(query.get("slug", [""])[0], 60).lower()
            token = query.get("token", [""])[0]
            item = find_content_item(slug)

            if not item or item.get("enabled") is False or not item.get("gate"):
                self.send_json(404, {
                    "success": False,
                    "message": "Không tìm thấy mục tải file."
                })
                return

            if not check_session(token, "c_" + slug):
                self.send_json(403, {
                    "success": False,
                    "message": "Bạn chưa hoàn thành vượt link cho mục này."
                })
                return

            target = item.get("url", "")

            if not validate_download_url(target):
                self.send_json(500, {
                    "success": False,
                    "message": "Đường dẫn LẤY FILE chưa hợp lệ."
                })
                return

            record_event_counter(
                "download", "c_" + slug,
                "LẤY FILE: " + safe_text(item.get("name", ""), 100),
                self.client_ip()
            )
            self.redirect(target)
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

            if destination_deleted(destination):
                self.send_json(404, {
                    "success": False,
                    "message": "Mục này đã bị xóa."
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

            if not validate_download_url(target):
                self.send_json(500, {
                    "success": False,
                    "message": "Đường dẫn LẤY FILE chưa hợp lệ."
                })
                return

            record_event_counter(
                "download", destination,
                "Người dùng nhấn LẤY FILE", self.client_ip()
            )

            print("[V2.3] DOWNLOAD:", destination)
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
                    "name": DESTINATION_NAMES[key] + (
                        " (ĐÃ XÓA)" if destination_deleted(key) else ""
                    ),
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

        if path == "/admin/site-config":
            if not self.require_admin(): return
            data = load_data()
            self.send_json(200, {"success": True,
                "site_name": data["settings"].get("site_name", "NGUYỄN VĂN PHONG WEBSITE"),
                "tags": {key: data["settings"].get("tag_" + key, "1") == "1" for key in ("home", "freefire", "lienquan", "roblox")},
                "music_playlist": data.get("music_playlist", []),
                "music_volume": data.get("music_volume", 0.7)})
            return

        if path == "/admin/tags":
            if not self.require_admin(): return
            stored = load_data()
            self.send_json(200, {"success": True, "items": stored.get("tags_custom", [])})
            return

        if path == "/admin/content":
            if not self.require_admin(): return
            stored = load_data()
            self.send_json(200, {"success": True, "items": stored.get("content_items", [])})
            return

        if path == "/admin/base-meta":
            if not self.require_admin(): return
            self.send_json(200, {"success": True, **build_base_meta_view(load_data())})
            return

        if path == "/admin/notices":
            if not self.require_admin(): return
            self.send_json(200, {"success": True, "items": load_data().get("notices", [])})
            return

        if path == "/admin/backup.json":
            if not self.require_admin(): return
            with JSON_LOCK:
                stored = load_data_unlocked()
            config = {
                "settings": stored.get("settings", {}),
                "files": stored.get("files", {}),
                "announcement": stored.get("announcement", {}),
                "maintenance": stored.get("maintenance", {}),
                "music_playlist": stored.get("music_playlist", []),
                "music_volume": stored.get("music_volume", 0.7),
                "tags_custom": stored.get("tags_custom", []),
                "content_items": stored.get("content_items", []),
                "tag_meta": stored.get("tag_meta", {}),
                "item_meta": stored.get("item_meta", {}),
                "notices": stored.get("notices", [])
            }
            payload = {
                "format": "PHONG_WEB_BACKUP",
                "version": "2.8.1",
                "created_at": vietnam_now().isoformat(),
                "config": config
            }
            raw = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Content-Disposition", 'attachment; filename="phong-web-backup-v2.8.1.json"')
            self.send_header("Content-Length", str(len(raw)))
            self.send_security_headers()
            self.end_headers()
            self.wfile.write(raw)
            return

        if path == "/admin/export.csv":
            if not self.require_admin(): return
            with JSON_LOCK:
                stored = load_data_unlocked()
            import csv, io
            output = io.StringIO()
            writer = csv.writer(output)
            writer.writerow(["date", "visits", "total", "android", "iphone", "downloads"])
            for day, info in sorted(stored.get("daily", {}).items()):
                writer.writerow([day, safe_count(info.get("visits", 0)), stored["stats"].get("total", 0), stored["stats"].get("android", 0), stored["stats"].get("iphone", 0), stored["stats"].get("downloads", 0)])
            raw = output.getvalue().encode("utf-8-sig")
            self.send_response(200)
            self.send_header("Content-Type", "text/csv; charset=utf-8")
            self.send_header("Content-Disposition", "attachment; filename=phong-web-report.csv")
            self.send_header("Content-Length", str(len(raw)))
            self.send_security_headers(); self.end_headers(); self.wfile.write(raw)
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
            "/Nhac1.mp3",
            "/Nhac2.mp3",
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
            "/Nhac1.mp3",
            "/Nhac2.mp3",
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

            self.send_response(200)
            self.send_header("Content-Type", content_type)
            self.send_header("Content-Length", str(size))
            self.send_header("Cache-Control", "public, max-age=3600")
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
                now = time.time()
                for old_token in list(ADMIN_SESSIONS):
                    old_session = ADMIN_SESSIONS[old_token]
                    if (now - old_session.get("created", 0) > ADMIN_TTL or
                        now - old_session.get("last_seen", old_session.get("created", 0)) > ADMIN_IDLE_TTL):
                        ADMIN_SESSIONS.pop(old_token, None)
                if len(ADMIN_SESSIONS) >= MAX_ADMIN_SESSIONS:
                    self.send_json(429, {"success": False, "message": "Đã đạt giới hạn 3 phiên Admin. Hãy thu hồi phiên cũ."})
                    return
                ADMIN_SESSIONS[token] = {
                    "created": now,
                    "last_seen": now,
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
            if rate_limited("admin:" + self.admin_token(), 90, ADMIN_WRITE_LIMITS):
                self.send_json(429, {"success": False, "message": "Bạn thao tác quá nhanh. Vui lòng chờ một phút."})
                return

        if path == "/admin/restore-backup":
            if data.get("format") != "PHONG_WEB_BACKUP" or data.get("version") not in ("2.6.0", "2.7.0", "2.7.1", "2.7.2", "2.8.0", "2.8.1"):
                self.send_json(400, {"success": False, "message": "Định dạng backup không hợp lệ."})
                return
            config = data.get("config")
            if not isinstance(config, dict):
                self.send_json(400, {"success": False, "message": "Thiếu phần cấu hình trong backup."})
                return

            settings = config.get("settings")
            files = config.get("files")
            announcement = config.get("announcement")
            maintenance = config.get("maintenance")
            playlist = config.get("music_playlist")
            tags = config.get("tags_custom")
            contents = config.get("content_items")
            if not all(isinstance(v, dict) for v in (settings, files, announcement, maintenance)):
                self.send_json(400, {"success": False, "message": "Cấu trúc thiết lập hoặc file không hợp lệ."})
                return
            if not isinstance(playlist, list) or not 1 <= len(playlist) <= 50:
                self.send_json(400, {"success": False, "message": "Danh sách nhạc phải có từ 1 đến 50 bài."})
                return
            if not isinstance(tags, list) or len(tags) > 40 or not isinstance(contents, list) or len(contents) > 200:
                self.send_json(400, {"success": False, "message": "Danh sách Tag hoặc nội dung vượt giới hạn."})
                return

            clean_playlist = []
            for track in playlist:
                if not isinstance(track, dict):
                    self.send_json(400, {"success": False, "message": "Dữ liệu bài nhạc không hợp lệ."})
                    return
                name = safe_text(track.get("name"), 80)
                src = safe_text(track.get("src"), 500)
                local_ok = src in ("/music.mp3", "/Nhac1.mp3", "/Nhac2.mp3")
                remote_ok = validate_http_url(src) and urlsplit(src).scheme == "https"
                if not name or not (local_ok or remote_ok):
                    self.send_json(400, {"success": False, "message": "Đường dẫn nhạc trong backup không hợp lệ."})
                    return
                clean_playlist.append({"name": name, "src": src, "enabled": track.get("enabled", True) is not False})

            clean_tags = []
            seen_tags = set()
            for item in tags:
                if not isinstance(item, dict):
                    continue
                name = safe_text(item.get("name"), 60)
                slug = safe_text(item.get("slug"), 40).lower()
                icon = safe_text(item.get("icon", "🏷️"), 12)
                if not name or not slug or not slug.replace("-", "").isalnum() or slug in seen_tags:
                    self.send_json(400, {"success": False, "message": "Tag trong backup không hợp lệ hoặc bị trùng slug."})
                    return
                seen_tags.add(slug)
                clean_tags.append({"name": name, "slug": slug, "icon": icon, "enabled": item.get("enabled") is not False, "order": len(clean_tags)})

            clean_contents = []
            seen_content = set()
            for item in contents:
                if not isinstance(item, dict):
                    continue
                slug = safe_text(item.get("slug"), 50).lower()
                name = safe_text(item.get("name"), 120)
                tag = safe_text(item.get("tag"), 40).lower()
                description = safe_text(item.get("description"), 500)
                image = safe_text(item.get("image", "/logo.png"), 500)
                url = safe_text(item.get("url"), 1000)
                if not slug or not slug.replace("-", "").isalnum() or slug in seen_content or not name or not validate_http_url(url):
                    self.send_json(400, {"success": False, "message": "Nội dung trong backup không hợp lệ."})
                    return
                if not validate_image_url(image):
                    image = "/logo.png"
                seen_content.add(slug)
                clean_contents.append({"slug": slug, "name": name, "tag": tag, "description": description, "image": image, "url": url, "enabled": item.get("enabled") is not False, "gate": item.get("gate") is True, "downloads": safe_count(item.get("downloads", 0)), "order": len(clean_contents)})

            clean_settings = {}
            for key, value in settings.items():
                key = safe_text(key, 100)
                if key.startswith(("url_", "enabled_", "tag_")) or key == "site_name":
                    clean_settings[key] = safe_text(str(value), 1000)
            clean_files = {}
            for key, value in files.items():
                if key not in DEFAULT_FILES or not isinstance(value, dict):
                    continue
                image = safe_text(value.get("image", "/logo.png"), 500)
                if not validate_image_url(image):
                    image = "/logo.png"
                clean_files[key] = {
                    "name": safe_text(value.get("name"), 120),
                    "size": safe_text(value.get("size"), 40),
                    "status": value.get("status") if value.get("status") in ("available", "unavailable") else "available",
                    "image": image,
                    "downloads": safe_count(value.get("downloads", 0))
                }

            restore_meta = {}
            if "tag_meta" in config:
                restore_meta["tag_meta"] = sanitize_tag_meta(config.get("tag_meta"))
            if "item_meta" in config:
                restore_meta["item_meta"] = sanitize_item_meta(
                    config.get("item_meta"), set(BASE_TAG_DEFAULTS) | seen_tags
                )
            if "notices" in config:
                restore_meta["notices"] = sanitize_notices(config.get("notices"))

            try:
                music_volume = max(0.0, min(1.0, float(config.get("music_volume", 0.7))))
            except (TypeError, ValueError):
                music_volume = 0.7
            clean_announcement = {
                "enabled": announcement.get("enabled") is True,
                "message": safe_text(announcement.get("message"), 1000)
            }
            clean_maintenance = {
                "enabled": maintenance.get("enabled") is True,
                "message": safe_text(maintenance.get("message"), 1000) or "Website đang bảo trì. Vui lòng quay lại sau."
            }

            with JSON_LOCK:
                stored = load_data_unlocked()
                stored["settings"].update(clean_settings)
                for key in DEFAULT_FILES:
                    if key in clean_files:
                        stored["files"][key] = clean_files[key]
                stored["announcement"] = clean_announcement
                stored["maintenance"] = clean_maintenance
                stored["music_playlist"] = clean_playlist
                stored["music_volume"] = music_volume
                stored["tags_custom"] = clean_tags
                stored["content_items"] = clean_contents
                stored.update(restore_meta)
                save_data_unlocked(stored)

            add_admin_log("RESTORE_BACKUP", self.client_ip(), "Khôi phục cấu hình V2.8.2")
            self.send_json(200, {"success": True, "message": "Đã khôi phục cấu hình website. Thống kê, lịch sử và nhật ký được giữ nguyên."})
            return

        if path == "/admin/tags":
            items = data.get("items")
            if not isinstance(items, list) or len(items) > 40:
                self.send_json(400, {"success": False, "message": "Danh sách Tag không hợp lệ (tối đa 40)."}); return
            clean=[]; seen=set()
            for item in items:
                if not isinstance(item, dict): continue
                name=safe_text(item.get("name"),60); slug=safe_text(item.get("slug"),40).lower()
                icon=safe_text(item.get("icon","🏷️"),12)
                if not name or not slug or not slug.replace("-", "").isalnum() or slug in seen: continue
                seen.add(slug); clean.append({"name":name,"slug":slug,"icon":icon,"enabled":item.get("enabled") is not False,"order":len(clean)})
            with JSON_LOCK:
                stored=load_data_unlocked(); stored["tags_custom"]=clean; save_data_unlocked(stored)
            add_admin_log("UPDATE_TAGS",self.client_ip(),f"Lưu {len(clean)} Tag")
            self.send_json(200,{"success":True,"message":"Đã lưu danh mục Tag."}); return

        if path == "/admin/content":
            items=data.get("items")
            old_dl = {x.get("slug"): safe_count(x.get("downloads", 0)) for x in load_data().get("content_items", []) if isinstance(x, dict)}
            if not isinstance(items,list) or len(items)>200:
                self.send_json(400,{"success":False,"message":"Danh sách nội dung không hợp lệ (tối đa 200)."}); return
            clean=[]; seen=set()
            for item in items:
                if not isinstance(item,dict): continue
                slug=safe_text(item.get("slug"),50).lower(); name=safe_text(item.get("name"),120)
                tag=safe_text(item.get("tag"),40).lower(); desc=safe_text(item.get("description"),500)
                image=safe_text(item.get("image","/logo.png"),500); url=safe_text(item.get("url"),1000)
                if not slug or not slug.replace("-","").isalnum() or slug in seen or not name or not validate_http_url(url):
                    continue
                if not validate_image_url(image): image="/logo.png"
                seen.add(slug); clean.append({"slug":slug,"name":name,"tag":tag,"description":desc,"image":image,"url":url,"enabled":item.get("enabled") is not False,"gate":item.get("gate") is True,"downloads":old_dl.get(slug,0),"order":len(clean)})
            with JSON_LOCK:
                stored=load_data_unlocked(); stored["content_items"]=clean; save_data_unlocked(stored)
            add_admin_log("UPDATE_CONTENT",self.client_ip(),f"Lưu {len(clean)} mục nội dung")
            self.send_json(200,{"success":True,"message":"Đã lưu nội dung website."}); return

        if path == "/admin/base-meta":
            tags = data.get("tags")
            items = data.get("items")
            if (
                not isinstance(tags, list) or not isinstance(items, list)
                or len(tags) > 10 or len(items) > 30
            ):
                self.send_json(400, {"success": False, "message": "Dữ liệu Tag/Mục gốc không hợp lệ."}); return
            tag_raw = {}
            enabled_map = {}
            for t in tags:
                if isinstance(t, dict) and isinstance(t.get("slug"), str) and t["slug"] in BASE_TAG_DEFAULTS:
                    tag_raw[t["slug"]] = t
                    enabled_map[t["slug"]] = t.get("enabled") is not False
            item_raw = {
                i["key"]: i for i in items
                if isinstance(i, dict) and isinstance(i.get("key"), str)
            }
            with JSON_LOCK:
                stored = load_data_unlocked()
                valid_tags = set(BASE_TAG_DEFAULTS)
                for ct in stored.get("tags_custom", []):
                    if isinstance(ct, dict) and ct.get("slug"):
                        valid_tags.add(ct["slug"])
                stored["tag_meta"] = sanitize_tag_meta(tag_raw)
                stored["item_meta"] = sanitize_item_meta(item_raw, valid_tags)
                for slug, on in enabled_map.items():
                    stored["settings"]["tag_" + slug] = "1" if on else "0"
                save_data_unlocked(stored)
            add_admin_log("UPDATE_BASE_META", self.client_ip(), "Lưu Tag gốc và Mục gốc")
            self.send_json(200, {"success": True, "message": "Đã lưu Tag gốc và Mục gốc."}); return

        if path == "/admin/notices":
            items = data.get("items")
            if not isinstance(items, list) or len(items) > 30:
                self.send_json(400, {"success": False, "message": "Danh sách thông báo không hợp lệ (tối đa 30)."}); return
            clean = sanitize_notices(items)
            with JSON_LOCK:
                stored = load_data_unlocked(); stored["notices"] = clean; save_data_unlocked(stored)
            add_admin_log("UPDATE_NOTICES", self.client_ip(), f"Lưu {len(clean)} thông báo")
            self.send_json(200, {"success": True, "message": "Đã lưu bảng thông báo."}); return

        # Revoke all other admin sessions while preserving the current session.
        if path == "/admin/revoke-sessions":
            current_token = self.admin_token()
            with LOCK:
                revoked = 0
                for other_token in list(ADMIN_SESSIONS):
                    if other_token != current_token:
                        ADMIN_SESSIONS.pop(other_token, None)
                        revoked += 1
            add_admin_log("REVOKE_SESSIONS", self.client_ip(), f"Thu hồi {revoked} phiên khác")
            self.send_json(200, {"success": True, "message": f"Đã thu hồi {revoked} phiên Admin khác."})
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

                if not validate_download_url(item.get("url")):
                    self.send_json(400, {
                        "success": False,
                        "message": (
                            "Link của " + DESTINATION_NAMES[key] +
                            " phải là liên kết HTTPS hợp lệ."
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

            print("[V2.3] ADMIN UPDATED SETTINGS")

            self.send_json(200, {
                "success": True,
                "message": "Đã lưu thiết lập thành công."
            })
            return

        if path == "/admin/site-config":
            site_name = safe_text(data.get("site_name", ""), 80)
            tags = data.get("tags"); playlist = data.get("music_playlist")
            music_volume = data.get("music_volume", 0.7)
            try: music_volume = max(0.0, min(1.0, float(music_volume)))
            except (TypeError, ValueError): music_volume = 0.7
            if not site_name or not isinstance(tags, dict) or not isinstance(playlist, list):
                self.send_json(400, {"success": False, "message": "Thiếu cấu hình website, Tag hoặc danh sách nhạc."}); return
            normalized_tags = {}
            for key in ("home", "freefire", "lienquan", "roblox"):
                if not isinstance(tags.get(key), bool):
                    self.send_json(400, {"success": False, "message": "Trạng thái Tag không hợp lệ."}); return
                normalized_tags[key] = "1" if tags[key] else "0"
            if not 1 <= len(playlist) <= 50:
                self.send_json(400, {"success": False, "message": "Danh sách nhạc cần từ 1 đến 50 bài."}); return
            clean_playlist = []
            for track in playlist:
                if not isinstance(track, dict):
                    self.send_json(400, {"success": False, "message": "Bài nhạc không hợp lệ."}); return
                name = safe_text(track.get("name", ""), 80); src = safe_text(track.get("src", ""), 500)
                local_ok = src in ("/music.mp3", "/Nhac1.mp3", "/Nhac2.mp3")
                remote_ok = validate_http_url(src) and urlsplit(src).scheme == "https"
                if not name or not (local_ok or remote_ok):
                    self.send_json(400, {"success": False, "message": "Bài nhạc cần tên và đường dẫn MP3 nội bộ hoặc HTTPS."}); return
                clean_playlist.append({"name": name, "src": src, "enabled": track.get("enabled", True) is not False})
            with JSON_LOCK:
                stored = load_data_unlocked(); stored["settings"]["site_name"] = site_name
                for key, value in normalized_tags.items(): stored["settings"]["tag_" + key] = value
                stored["music_playlist"] = clean_playlist
                stored["music_volume"] = music_volume
                save_data_unlocked(stored)
            add_admin_log("UPDATE_SITE_CONFIG", self.client_ip(), "Cập nhật tên web, Tag và danh sách nhạc")
            self.send_json(200, {"success": True, "message": "Đã lưu tên website, Tag và danh sách nhạc."}); return

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
        print("[PHONG WEB V2.8.2]", fmt % args)


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
    print("              V2.8.2")
    print("======================================")

    print("Port:", PORT)
    print("JSON:", DATA_FILE)

    print(
        "Link4M:",
        "ENABLED" if LINK4M_API_TOKEN else "MISSING API TOKEN"
    )

    print("Admin page: /admin")
    print("Admin password: Set by ADMIN_PASSWORD")
    if ADMIN_PASSWORD == "152012":
        print("[SECURITY WARNING] ADMIN_PASSWORD đang dùng mật khẩu mặc định. Hãy đổi trong Render Environment.")
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
    print("Visitor Session TTL:", SESSION_TTL, "seconds")
    print("Admin idle TTL:", ADMIN_IDLE_TTL, "seconds")
    print("Max Admin Sessions:", MAX_ADMIN_SESSIONS)
    print("Admin TTL:", ADMIN_TTL, "seconds")

    print("Categories: /?category=freefire | lienquan | roblox")
    print("Location: /dinh-vi")
    print("Deta: /menu")
    print("Proxy: /proxy-mod-alen-crack")
    print("Mizze: /mizze-crack")
    print("Nvp Crack Key: /menu-nvp-crack-key")
    print("YSM Team Liên Quân: /menu-ysm-team-lien-quan")
    print("Deta Quốc Tế (Roblox): /deta-quoc-te")
    print("Map Liên Quân NoKey: /map-lien-quan-nokey")

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