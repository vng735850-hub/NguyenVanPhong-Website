"use strict";

// =========================================================
// PHONG WEB V2.7.2  (bản viết lại bằng Node.js / JavaScript)
// LINK4M ONLY | LOCATION + DETA + PROXY + MIZZE
// ADVANCED ADMIN | JSON ANALYTICS | SECURITY | CSRF
// Yêu cầu: Node.js >= 18 (dùng fetch có sẵn, không cần npm install)
// =========================================================

const fs = require("fs");
const os = require("os");
const path = require("path");
const http = require("http");
const crypto = require("crypto");

const BASE_DIR = __dirname;

// Render đôi khi truyền PORT rỗng; dùng 5000 làm giá trị dự phòng.
const _portValue = String(process.env.PORT || "").trim();
let PORT = 5000;
if (/^[+-]?\d+$/.test(_portValue)) PORT = parseInt(_portValue, 10);

function pickDataFile() {
  // Thứ tự: DATA_DIR (nếu có) -> thư mục code -> thư mục tạm.
  const candidates = [];
  const envDir = String(process.env.DATA_DIR || "").trim();
  if (envDir) candidates.push(envDir);
  candidates.push(BASE_DIR);
  candidates.push(os.tmpdir());

  for (const folder of candidates) {
    try {
      fs.mkdirSync(folder, { recursive: true });
      const probe = path.join(folder, ".write_test");
      fs.writeFileSync(probe, "ok", "utf8");
      fs.unlinkSync(probe);
      return path.join(folder, "data.json");
    } catch (e) {
      continue;
    }
  }
  return path.join(BASE_DIR, "data.json");
}

const DATA_FILE = pickDataFile();

const SITE_URL = String(process.env.SITE_URL || "https://nvp-com.onrender.com")
  .trim()
  .replace(/\/+$/, "");

const LINK4M_API_TOKEN = String(process.env.LINK4M_API_TOKEN || "").trim();
const LINK4M_ENDPOINT = "https://link4m.co/api-shorten/v2";

const ADMIN_PASSWORD =
  process.env.ADMIN_PASSWORD !== undefined ? process.env.ADMIN_PASSWORD : "152012";

const SESSION_TTL = 30 * 60;
const ADMIN_IDLE_TTL = 30 * 60;
const MAX_ADMIN_SESSIONS = 3;
const MAX_REQUEST_BODY = 2 * 1024 * 1024;
const VISITOR_TIMEOUT = 120;
const ADMIN_TTL = 8 * 60 * 60;

const MAX_HISTORY = 2000;
const MAX_LOGIN_ATTEMPTS = 5;
const MAX_LINK_REQUESTS = 8;
const MAX_API_REQUESTS = 20;

const MEDIAFIRE_LINK = "https://www.mediafire.com/file/yen60lu05hfnng4/DINH_VI_BT.zip/file";
const DETA_MEDIAFIRE_LINK = "https://www.mediafire.com/file/wohet4glfwyn5j0/Deta_Crack.7z/file";
const PROXY_MEDIAFIRE_LINK =
  "https://www.mediafire.com/file/zdoapnkcx9v70gq/PROXY+MOD+ALEN+Crack.zip/file";
const MIZZE_MEDIAFIRE_LINK =
  "https://www.mediafire.com/file/2plraqmzcl7gk4m/mizze+crack+adr+chs+ff+india.zip/file";

// V2.7.2: link mặc định của 2 mục mới (Admin có thể đổi trong tab quản lý file).
const NVPKEY_LINK = "https://zufile.com/f/2vRmNkma5C";
const YSM_LINK =
  "https://www.mediafire.com/file/x9xo2468orsfr3l/YSM_TEAM_LIEN_QUAN.apk/file";

const DEFAULT_DESTINATIONS = {
  location: MEDIAFIRE_LINK,
  deta: DETA_MEDIAFIRE_LINK,
  proxy: PROXY_MEDIAFIRE_LINK,
  mizze: MIZZE_MEDIAFIRE_LINK,
  nvpkey: NVPKEY_LINK,
  ysm: YSM_LINK,
};

const DESTINATION_NAMES = {
  location: "Định Vị",
  deta: "Deta",
  proxy: "Proxy Mod Alen Crack",
  mizze: "Menu Mizze Crack",
  nvpkey: "Menu Nvp Crack Key",
  ysm: "Menu YSM Team Liên Quân",
};

const DESTINATION_ROUTES = {
  location: "/dinh-vi",
  deta: "/menu",
  proxy: "/proxy-mod-alen-crack",
  mizze: "/mizze-crack",
  nvpkey: "/menu-nvp-crack-key",
  ysm: "/menu-ysm-team-lien-quan",
};

const DOWNLOAD_ROUTES = {
  location: "/download-location",
  deta: "/download-deta",
  proxy: "/download-proxy",
  mizze: "/download-mizze",
  nvpkey: "/download-nvpkey",
  ysm: "/download-ysm",
};

const DEFAULT_FILES = {
  location: { name: "DINH_VI_BT.zip", size: "", status: "available", image: "/logo.png" },
  deta: { name: "Deta_Crack.7z", size: "", status: "available", image: "/logo.png" },
  proxy: { name: "PROXY MOD ALEN Crack.zip", size: "", status: "available", image: "/logo.png" },
  mizze: { name: "Menu Mizze Crack", size: "", status: "available", image: "/logo.png" },
  nvpkey: { name: "Menu Nvp Crack Key", size: "", status: "available", image: "/logo.png" },
  ysm: { name: "YSM_TEAM_LIEN_QUAN.apk", size: "", status: "available", image: "/logo.png" },
};

const TAG_KEYS = ["home", "freefire", "lienquan", "roblox"];
const DEFAULT_SITE_NAME = "NGUYỄN VĂN PHONG WEBSITE";
const DEFAULT_MAINTENANCE_MESSAGE = "Website đang bảo trì. Vui lòng quay lại sau.";
const LOCAL_MUSIC = ["/music.mp3", "/Nhac1.mp3", "/Nhac2.mp3"];

const STATIC_FILES = new Set([
  "/logo.png",
  "/background.jpg",
  "/music.mp3",
  "/Nhac1.mp3",
  "/Nhac2.mp3",
  "/cam-on-tu-phong.png",
  "/cam-on-tu-phong.mp3",
]);

const MIME_TYPES = {
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".jpeg": "image/jpeg",
  ".mp3": "audio/mpeg",
};

const PUBLIC_PAGES = new Set([
  "/",
  "/index.html",
  "/dinh-vi",
  "/menu",
  "/proxy-mod-alen-crack",
  "/mizze-crack",
  "/menu-nvp-crack-key",
  "/menu-ysm-team-lien-quan",
]);

// Trạng thái trong bộ nhớ (mất khi khởi động lại, giống bản Python).
const SESSIONS = new Map();
const ADMIN_SESSIONS = new Map();
const RATE_LIMITS = new Map();
const API_RATE_LIMITS = new Map();
const ADMIN_WRITE_LIMITS = new Map();

// Hai trang HTML (đã tách nguyên văn từ bản Python).
const HTML = fs.readFileSync(path.join(BASE_DIR, "views", "index.html"), "utf8");
const ADMIN_HTML = fs.readFileSync(path.join(BASE_DIR, "views", "admin.html"), "utf8");

// =========================================================
// TIỆN ÍCH CHUNG
// =========================================================

const nowSec = () => Date.now() / 1000;

// Đối tượng Date đã dịch sang UTC+7: các trường UTC chính là giờ Việt Nam.
function vietnamShifted(extraMs = 0) {
  return new Date(Date.now() + 7 * 3600 * 1000 + extraMs);
}

function vietnamDateTime() {
  const s = vietnamShifted().toISOString();
  return s.slice(0, 10) + " " + s.slice(11, 19);
}

function vietnamDate(offsetDays = 0) {
  return vietnamShifted(-offsetDays * 86400000).toISOString().slice(0, 10);
}

function vietnamIso() {
  const s = vietnamShifted().toISOString(); // YYYY-MM-DDTHH:MM:SS.mmmZ
  return s.slice(0, 23) + "000+07:00";
}

function isObj(v) {
  return v !== null && typeof v === "object" && !Array.isArray(v);
}

function has(obj, key) {
  return Object.prototype.hasOwnProperty.call(obj, key);
}

function getOr(obj, key, dflt) {
  return isObj(obj) && has(obj, key) ? obj[key] : dflt;
}

function safeCount(value) {
  let n;
  if (typeof value === "number") {
    if (!Number.isFinite(value)) return 0;
    n = Math.trunc(value);
  } else if (typeof value === "boolean") {
    n = value ? 1 : 0;
  } else if (typeof value === "string") {
    if (!/^\s*[+-]?\d+\s*$/.test(value)) return 0;
    n = parseInt(value, 10);
  } else {
    return 0;
  }
  return Math.max(0, n);
}

function safeText(value, maximum = 300) {
  if (typeof value !== "string") return "";
  return Array.from(value.trim()).slice(0, maximum).join("");
}

function clampVolume(value, dflt = 0.7) {
  let n;
  if (typeof value === "number") n = value;
  else if (typeof value === "boolean") n = value ? 1 : 0;
  else if (typeof value === "string" && value.trim() !== "") n = Number(value);
  else return dflt;
  if (Number.isNaN(n)) return dflt;
  return Math.max(0, Math.min(1, n));
}

function isAlnumSlug(slug) {
  const s = slug.replace(/-/g, "");
  return s.length > 0 && /^[\p{L}\p{N}]+$/u.test(s);
}

function tokenUrlsafe(nBytes) {
  return crypto.randomBytes(nBytes).toString("base64url");
}

function hashText(value) {
  return crypto.createHash("sha256").update(String(value), "utf8").digest("hex");
}

function compareDigest(a, b) {
  const x = Buffer.from(String(a), "utf8");
  const y = Buffer.from(String(b), "utf8");
  if (x.length !== y.length) return false;
  return crypto.timingSafeEqual(x, y);
}

function qs(params, name, dflt = "") {
  // Giống parse_qs: giá trị rỗng bị bỏ qua.
  const found = params.getAll(name).find((v) => v !== "");
  return found !== undefined ? found : dflt;
}

// =========================================================
// CƠ SỞ DỮ LIỆU JSON
// =========================================================

const DEFAULT_DATA = {
  settings: {},
  visitors: {},
  visitor_devices: {},
  stats: { total: 0, android: 0, iphone: 0, success: 0, failed: 0, downloads: 0 },
  daily: {},
  history: [],
  files: {},
  announcement: { enabled: false, message: "" },
  maintenance: { enabled: false, message: DEFAULT_MAINTENANCE_MESSAGE },
  admin_logs: [],
  music_playlist: [
    { name: "Nhạc nền", src: "/music.mp3", enabled: true },
    { name: "Nhạc 1", src: "/Nhac1.mp3", enabled: true },
    { name: "Nhạc 2", src: "/Nhac2.mp3", enabled: true },
  ],
  music_volume: 0.7,
  tags_custom: [],
  content_items: [],
};

for (const [key, value] of Object.entries(DEFAULT_DESTINATIONS)) {
  DEFAULT_DATA.settings["url_" + key] = value;
  DEFAULT_DATA.settings["enabled_" + key] = "1";
}
DEFAULT_DATA.settings.site_name = DEFAULT_SITE_NAME;
for (const tag of TAG_KEYS) DEFAULT_DATA.settings["tag_" + tag] = "1";
for (const [key, value] of Object.entries(DEFAULT_FILES)) {
  DEFAULT_DATA.files[key] = { ...value };
}

const clone = (v) => JSON.parse(JSON.stringify(v));

function saveData(data) {
  const tempFile = DATA_FILE.replace(/\.json$/, "") + ".tmp";
  try {
    const fd = fs.openSync(tempFile, "w");
    try {
      fs.writeSync(fd, JSON.stringify(data, null, 2), null, "utf8");
      fs.fsyncSync(fd);
    } finally {
      fs.closeSync(fd);
    }
    fs.renameSync(tempFile, DATA_FILE);
  } catch (e) {
    try {
      if (fs.existsSync(tempFile)) fs.unlinkSync(tempFile);
    } catch (e2) {
      /* bỏ qua */
    }
    throw e;
  }
}

function loadData() {
  let data = null;

  try {
    if (fs.existsSync(DATA_FILE) && fs.statSync(DATA_FILE).isFile()) {
      data = JSON.parse(fs.readFileSync(DATA_FILE, "utf8"));
      if (!isObj(data)) throw new Error("JSON không hợp lệ.");
    }
  } catch (e) {
    console.log("[JSON WARNING]", String(e.message || e));
    data = null;
  }

  if (!isObj(data)) data = {};

  // Giữ dữ liệu cũ và bổ sung cấu trúc mới.
  for (const key of [
    "settings", "visitors", "visitor_devices", "stats",
    "daily", "files", "announcement", "maintenance",
  ]) {
    if (!isObj(data[key])) data[key] = {};
  }

  if (!Array.isArray(data.history)) data.history = [];
  if (!Array.isArray(data.admin_logs)) data.admin_logs = [];
  if (!Array.isArray(data.tags_custom)) data.tags_custom = [];
  if (!Array.isArray(data.content_items)) data.content_items = [];

  data.music_volume = clampVolume(data.music_volume, 0.7);

  if (!Array.isArray(data.music_playlist)) data.music_playlist = clone(DEFAULT_DATA.music_playlist);
  const playlist = [];
  for (const track of data.music_playlist.slice(0, 50)) {
    if (isObj(track)) {
      const name = safeText(track.name, 80);
      const src = safeText(track.src, 500);
      if (name && src) playlist.push({ name, src, enabled: track.enabled !== false });
    }
  }
  data.music_playlist = playlist.length ? playlist : clone(DEFAULT_DATA.music_playlist);

  for (const [key, value] of Object.entries(DEFAULT_DATA.settings)) {
    if (!has(data.settings, key)) data.settings[key] = value;
  }

  for (const [key, value] of Object.entries(DEFAULT_DATA.stats)) {
    data.stats[key] = safeCount(has(data.stats, key) ? data.stats[key] : value);
  }

  for (const [key, value] of Object.entries(DEFAULT_DATA.files)) {
    if (!isObj(data.files[key])) {
      data.files[key] = { ...value };
    } else {
      for (const [field, dflt] of Object.entries(value)) {
        if (!has(data.files[key], field)) data.files[key][field] = dflt;
      }
    }
  }

  for (const [key, value] of Object.entries(DEFAULT_DATA.announcement)) {
    if (!has(data.announcement, key)) data.announcement[key] = value;
  }
  for (const [key, value] of Object.entries(DEFAULT_DATA.maintenance)) {
    if (!has(data.maintenance, key)) data.maintenance[key] = value;
  }

  data.history = data.history.slice(-MAX_HISTORY);
  data.admin_logs = data.admin_logs.slice(-500);

  return data;
}

function initData() {
  saveData(loadData());
  console.log("[JSON] DATA FILE:", DATA_FILE);
}

function setting(key, dflt = "") {
  const data = loadData();
  return has(data.settings, key) ? data.settings[key] : dflt;
}

function getFileSettings() {
  const data = loadData();
  const result = {};
  for (const key of Object.keys(DEFAULT_DESTINATIONS)) {
    const item = { ...(data.files[key] || {}) };
    item.downloads = safeCount(item.downloads);
    result[key] = item;
  }
  return result;
}

function destinationEnabled(key) {
  return setting("enabled_" + key, "1") === "1";
}

function tagStates(data) {
  const tags = {};
  for (const key of TAG_KEYS) tags[key] = (data.settings["tag_" + key] ?? "1") === "1";
  return tags;
}

// =========================================================
// HÀM BẢO MẬT
// =========================================================

function validToken(token) {
  return (
    typeof token === "string" &&
    token.length >= 30 &&
    token.length <= 120 &&
    /^[A-Za-z0-9_-]+$/.test(token)
  );
}

function parseUrl(value) {
  try {
    return new URL(value);
  } catch (e) {
    return null;
  }
}

function validateHttpUrl(value) {
  if (typeof value !== "string") return false;
  value = value.trim();
  if (!value || value.length > 4096) return false;

  const u = parseUrl(value);
  if (!u) return false;

  return (
    (u.protocol === "https:" || u.protocol === "http:") &&
    !!u.hostname &&
    !u.username &&
    !u.password &&
    (u.port === "" || u.port === "80" || u.port === "443")
  );
}

function validateMediafireUrl(value) {
  if (!validateHttpUrl(value)) return false;
  const u = parseUrl(value.trim());
  return (
    u.protocol === "https:" &&
    ["www.mediafire.com", "mediafire.com"].includes(u.hostname.toLowerCase())
  );
}

function validateDownloadUrl(value) {
  // V2.7.2: nút LẤY FILE có thể trỏ tới MediaFire, Zufile hoặc bất kỳ link HTTPS hợp lệ.
  if (!validateHttpUrl(value)) return false;
  return parseUrl(value.trim()).protocol === "https:";
}

function validateImageUrl(value) {
  if (typeof value !== "string") return false;
  value = value.trim();

  if (value.startsWith("/")) {
    return ["/logo.png", "/background.jpg", "/cam-on-tu-phong.png"].includes(value);
  }

  if (!validateHttpUrl(value)) return false;
  return parseUrl(value).protocol === "https:";
}

function validMusicSrc(src) {
  return LOCAL_MUSIC.includes(src) || (validateHttpUrl(src) && parseUrl(src.trim()).protocol === "https:");
}

function detectDevice(userAgent) {
  const ua = String(userAgent || "").toLowerCase();
  if (ua.includes("iphone")) return "iphone";
  if (ua.includes("android")) return "android";
  return "other";
}

function cleanupSessions() {
  const now = nowSec();

  for (const [token, s] of SESSIONS) {
    if (now - s.created > SESSION_TTL) SESSIONS.delete(token);
  }
  for (const [token, s] of ADMIN_SESSIONS) {
    if (now - s.created > ADMIN_TTL) ADMIN_SESSIONS.delete(token);
  }
  for (const table of [RATE_LIMITS, API_RATE_LIMITS, ADMIN_WRITE_LIMITS]) {
    for (const [ip, values] of table) {
      const kept = values.filter((t) => now - t < 60);
      if (kept.length) table.set(ip, kept);
      else table.delete(ip);
    }
  }
}

function rateLimited(ip, limit = 8, table = RATE_LIMITS) {
  const now = nowSec();
  const values = (table.get(ip) || []).filter((t) => now - t < 60);
  if (values.length >= limit) {
    table.set(ip, values);
    return true;
  }
  values.push(now);
  table.set(ip, values);
  return false;
}

function getSession(token) {
  if (!validToken(token)) return null;
  const session = SESSIONS.get(token);
  if (!session) return null;
  if (nowSec() - session.created > SESSION_TTL) {
    SESSIONS.delete(token);
    return null;
  }
  return { ...session };
}

function checkSession(token, destination = null) {
  const session = getSession(token);
  if (!session || !session.returned) return false;
  if (destination && session.destination !== destination) return false;
  return true;
}

// =========================================================
// LỊCH SỬ + THỐNG KÊ
// =========================================================

function addHistory(event, destination = "", detail = "", ip = "") {
  const data = loadData();
  data.history.push({
    time: vietnamDateTime(),
    date: vietnamDate(),
    event: safeText(event, 40),
    destination: safeText(destination, 40),
    name: DESTINATION_NAMES[destination] || destination,
    detail: safeText(detail, 250),
    ip: safeText(ip, 80),
  });
  data.history = data.history.slice(-MAX_HISTORY);
  saveData(data);
}

function recordEventCounter(event, destination = "", detail = "", ip = "") {
  const data = loadData();

  if (event === "success") {
    data.stats.success += 1;
  } else if (event === "failed") {
    data.stats.failed += 1;
  } else if (event === "download") {
    data.stats.downloads += 1;
    data.files[destination].downloads = safeCount(data.files[destination].downloads) + 1;
  }

  data.history.push({
    time: vietnamDateTime(),
    date: vietnamDate(),
    event,
    destination,
    name: DESTINATION_NAMES[destination] || destination,
    detail: safeText(detail, 250),
    ip: safeText(ip, 80),
  });

  data.history = data.history.slice(-MAX_HISTORY);
  saveData(data);
}

function registerVisit(visitorId, userAgent = "") {
  if (!validToken(visitorId)) return;

  const now = nowSec();
  const device = detectDevice(userAgent);
  const today = vietnamDate();
  const data = loadData();

  const visitors = data.visitors;
  const visitorDevices = data.visitor_devices;
  const stats = data.stats;

  if (!has(visitorDevices, visitorId)) {
    visitorDevices[visitorId] = device;
    stats.total += 1;
    if (device === "android") stats.android += 1;
    else if (device === "iphone") stats.iphone += 1;
  }

  for (const [visitor, lastSeen] of Object.entries(visitors)) {
    const t = Number(lastSeen);
    if (typeof lastSeen === "boolean" || lastSeen === null || Number.isNaN(t) || now - t > VISITOR_TIMEOUT) {
      delete visitors[visitor];
    }
  }

  visitors[visitorId] = now;

  if (!isObj(data.daily[today])) data.daily[today] = { visits: 0, visitors: [] };
  const day = data.daily[today];

  let dayVisitors = day.visitors;
  if (!Array.isArray(dayVisitors)) dayVisitors = [];

  // Đếm lượt truy cập duy nhất mỗi ngày theo cookie.
  if (!dayVisitors.includes(visitorId)) {
    dayVisitors.push(visitorId);
    day.visits = safeCount(day.visits) + 1;
  }
  day.visitors = dayVisitors.slice(-10000);

  // Giữ dữ liệu thống kê tối đa 400 ngày.
  const dates = Object.keys(data.daily).sort();
  for (const dateKey of dates.slice(0, Math.max(0, dates.length - 400))) {
    delete data.daily[dateKey];
  }

  saveData(data);
}

function getStatistics() {
  const now = nowSec();
  const data = loadData();

  const online = {};
  for (const [visitor, lastSeen] of Object.entries(data.visitors)) {
    const t = Number(lastSeen);
    if (typeof lastSeen === "boolean" || lastSeen === null || Number.isNaN(t)) continue;
    if (now - t <= VISITOR_TIMEOUT) online[visitor] = lastSeen;
  }
  data.visitors = online;

  const downloads = {};
  for (const key of Object.keys(DEFAULT_DESTINATIONS)) {
    downloads[key] = safeCount(data.files[key].downloads);
  }

  let popular = "";
  let best = -1;
  for (const [key, value] of Object.entries(downloads)) {
    if (value > best) {
      best = value;
      popular = key;
    }
  }

  const result = {
    online: Object.keys(online).length,
    total: safeCount(data.stats.total),
    android: safeCount(data.stats.android),
    iphone: safeCount(data.stats.iphone),
    success: safeCount(data.stats.success),
    failed: safeCount(data.stats.failed),
    downloads: safeCount(data.stats.downloads),
    popular,
    popular_name: DESTINATION_NAMES[popular] || "Chưa có dữ liệu",
  };

  saveData(data);
  return result;
}

function getDailyStatistics(days = 7) {
  days = days === 30 ? 30 : 7;
  const data = loadData();
  const result = [];

  for (let offset = days - 1; offset >= 0; offset--) {
    const dateValue = vietnamDate(offset);
    const item = isObj(data.daily[dateValue]) ? data.daily[dateValue] : { visits: 0 };
    result.push({ date: dateValue, visits: safeCount(item.visits) });
  }
  return result;
}

// =========================================================
// NHẬT KÝ ADMIN
// =========================================================

function addAdminLog(action, ip = "", detail = "") {
  const data = loadData();
  data.admin_logs.push({
    time: vietnamDateTime(),
    action: safeText(action, 100),
    ip: safeText(ip, 80),
    detail: safeText(detail, 200),
  });
  data.admin_logs = data.admin_logs.slice(-500);
  saveData(data);
}

// =========================================================
// LINK4M API
// =========================================================

async function apiRequest(url) {
  let response;
  try {
    response = await fetch(url, {
      method: "GET",
      headers: {
        "User-Agent": "Mozilla/5.0 PHONG-WEB/2.3",
        Accept: "application/json",
        "Cache-Control": "no-cache",
      },
      signal: AbortSignal.timeout(25000),
    });
  } catch (error) {
    const reason = (error && error.cause && error.cause.message) || (error && error.message) || String(error);
    throw new Error("Không thể kết nối Link4M: " + reason);
  }

  const body = await response.text();
  if (!response.ok) {
    throw new Error("Link4M HTTP " + response.status + ": " + body.slice(0, 180));
  }
  return body;
}

async function createLink4mUrl(callbackUrl) {
  if (!LINK4M_API_TOKEN) {
    throw new Error("Chưa cấu hình LINK4M_API_TOKEN trên Render.");
  }

  const apiUrl =
    LINK4M_ENDPOINT +
    "?" +
    new URLSearchParams({ api: LINK4M_API_TOKEN, url: callbackUrl }).toString();

  let result;
  try {
    result = JSON.parse(await apiRequest(apiUrl));
  } catch (e) {
    if (e instanceof SyntaxError) throw new Error("Link4M không trả về JSON hợp lệ.");
    throw e;
  }

  if (!isObj(result)) throw new Error("Dữ liệu Link4M không hợp lệ.");

  if (result.status !== "success") {
    throw new Error("Link4M: " + String(result.message ?? "Tạo link thất bại").slice(0, 180));
  }

  const url = result.shortenedUrl || result.shortened_url || result.short_url;
  if (!validateHttpUrl(url)) throw new Error("Link4M trả về URL không hợp lệ.");
  return url;
}

// =========================================================
// HTTP SERVER
// =========================================================

function securityHeaders() {
  const h = {
    "X-Content-Type-Options": "nosniff",
    "X-Frame-Options": "DENY",
    "Cross-Origin-Resource-Policy": "same-origin",
    "Cross-Origin-Opener-Policy": "same-origin",
    "X-Permitted-Cross-Domain-Policies": "none",
    "Referrer-Policy": "strict-origin-when-cross-origin",
    "Permissions-Policy": "camera=(), microphone=(), geolocation=()",
    "Content-Security-Policy":
      "default-src 'self' https: data:; " +
      "script-src 'self' 'unsafe-inline'; " +
      "style-src 'self' 'unsafe-inline'; " +
      "img-src 'self' https: data:; " +
      "media-src 'self' https:; frame-ancestors 'none'",
  };
  if (SITE_URL.startsWith("https://")) {
    h["Strict-Transport-Security"] = "max-age=31536000; includeSubDomains";
  }
  return h;
}

const SECURE_FLAG = () => (SITE_URL.startsWith("https://") ? "; Secure" : "");

class Ctx {
  constructor(req, res) {
    this.req = req;
    this.res = res;
  }

  clientIp() {
    // Không tin X-Forwarded-For do client có thể tự giả mạo.
    return String(this.req.socket.remoteAddress || "").replace(/^::ffff:/, "");
  }

  sendJson(status, data, extra = {}) {
    const body = Buffer.from(JSON.stringify(data), "utf8");
    this.res.writeHead(status, {
      "Content-Type": "application/json; charset=utf-8",
      "Content-Length": body.length,
      "Cache-Control": "no-store",
      ...securityHeaders(),
      ...extra,
    });
    this.res.end(body);
  }

  sendHtml(content, status = 200, extra = {}) {
    const body = Buffer.from(content, "utf8");
    this.res.writeHead(status, {
      "Content-Type": "text/html; charset=utf-8",
      "Content-Length": body.length,
      "Cache-Control": "no-store",
      ...securityHeaders(),
      ...extra,
    });
    this.res.end(body);
  }

  sendRaw(status, body, headers) {
    this.res.writeHead(status, {
      "Content-Length": body.length,
      ...headers,
      ...securityHeaders(),
    });
    this.res.end(body);
  }

  redirect(location) {
    this.res.writeHead(302, {
      Location: location,
      "Cache-Control": "no-store",
      ...securityHeaders(),
    });
    this.res.end();
  }

  getCookie(name) {
    const header = this.req.headers.cookie || "";
    for (const part of header.split(";")) {
      const idx = part.indexOf("=");
      if (idx < 0) continue;
      if (part.slice(0, idx).trim() === name) {
        let v = part.slice(idx + 1).trim();
        if (v.length >= 2 && v.startsWith('"') && v.endsWith('"')) v = v.slice(1, -1);
        return v;
      }
    }
    return "";
  }

  adminToken() {
    return this.getCookie("ph_admin");
  }

  isAdmin() {
    const token = this.adminToken();
    if (!validToken(token)) return false;

    const session = ADMIN_SESSIONS.get(token);
    if (!session) return false;

    const now = nowSec();
    if (now - session.created > ADMIN_TTL) {
      ADMIN_SESSIONS.delete(token);
      return false;
    }
    if (now - (session.last_seen ?? session.created) > ADMIN_IDLE_TTL) {
      ADMIN_SESSIONS.delete(token);
      return false;
    }
    session.last_seen = now;
    return true;
  }

  requireAdmin() {
    if (!this.isAdmin()) {
      this.sendJson(401, {
        success: false,
        message: "Phiên quản trị hết hạn. Vui lòng đăng nhập lại.",
      });
      return false;
    }
    return true;
  }

  requireCsrf() {
    if (!this.requireAdmin()) return false;

    const origin = String(this.req.headers.origin || "").trim();
    if (origin) {
      const u = parseUrl(origin);
      const originHost = u ? u.host.toLowerCase() : "";
      const requestHost = String(this.req.headers.host || "").toLowerCase();
      const cfg = parseUrl(SITE_URL);
      const configuredHost = cfg ? cfg.host.toLowerCase() : "";
      const allowed = [requestHost, configuredHost].filter(Boolean);
      if (!allowed.includes(originHost)) {
        this.sendJson(403, { success: false, message: "Yêu cầu khác nguồn bị từ chối." });
        return false;
      }
    }

    const session = ADMIN_SESSIONS.get(this.adminToken());
    const expected = session ? session.csrf || "" : "";
    const supplied = String(this.req.headers["x-csrf-token"] || "");

    if (!supplied || !expected || !compareDigest(supplied, expected)) {
      this.sendJson(403, {
        success: false,
        message: "CSRF token không hợp lệ. Hãy tải lại trang Admin.",
      });
      return false;
    }
    return true;
  }

  readJson() {
    return new Promise((resolve) => {
      const length = parseInt(this.req.headers["content-length"] || "0", 10);
      if (!Number.isFinite(length) || length <= 0 || length > MAX_REQUEST_BODY) {
        this.req.resume();
        return resolve(null);
      }
      const chunks = [];
      this.req.on("data", (c) => chunks.push(c));
      this.req.on("error", () => resolve(null));
      this.req.on("end", () => {
        try {
          const value = JSON.parse(Buffer.concat(chunks).toString("utf8"));
          resolve(isObj(value) ? value : null);
        } catch (e) {
          resolve(null);
        }
      });
    });
  }

  sendStaticFile(pathname) {
    if (!STATIC_FILES.has(pathname)) {
      return this.sendJson(404, { success: false });
    }

    const filePath = path.join(BASE_DIR, pathname.replace(/^\/+/, ""));
    let stat;
    try {
      stat = fs.statSync(filePath);
      if (!stat.isFile()) throw new Error("not file");
    } catch (e) {
      return this.sendJson(404, { success: false, message: "Không tìm thấy file tài nguyên." });
    }

    const type = MIME_TYPES[path.extname(filePath).toLowerCase()] || "application/octet-stream";
    this.res.writeHead(200, {
      "Content-Type": type,
      "Content-Length": stat.size,
      "Cache-Control": "public, max-age=3600",
      ...securityHeaders(),
    });

    const stream = fs.createReadStream(filePath);
    stream.on("error", (error) => {
      console.log("[STATIC ERROR]", String(error.message || error));
      this.res.destroy();
    });
    stream.pipe(this.res);
  }
}

// =========================================================
// GET ROUTES
// =========================================================

async function handleGet(ctx, url) {
  cleanupSessions();

  const pathname = url.pathname;
  const query = url.searchParams;
  const ua = ctx.req.headers["user-agent"] || "";

  // Trang công khai.
  if (PUBLIC_PAGES.has(pathname)) {
    let visitor = ctx.getCookie("ph_visitor");
    const headers = {};

    if (!validToken(visitor)) {
      visitor = tokenUrlsafe(24);
      headers["Set-Cookie"] =
        "ph_visitor=" + visitor + "; Path=/; Max-Age=31536000; SameSite=Lax; HttpOnly" + SECURE_FLAG();
    }

    registerVisit(visitor, ua);
    return ctx.sendHtml(HTML, 200, headers);
  }

  if (pathname === "/admin") return ctx.sendHtml(ADMIN_HTML);

  // Heartbeat + thống kê.
  if (pathname === "/stats") {
    const visitor = ctx.getCookie("ph_visitor");
    if (validToken(visitor)) registerVisit(visitor, ua);
    return ctx.sendJson(200, { success: true, ...getStatistics() });
  }

  // Cài đặt công khai.
  if (pathname === "/public-settings") {
    const data = loadData();
    const enabled = {};
    for (const key of Object.keys(DEFAULT_DESTINATIONS)) enabled[key] = destinationEnabled(key);

    return ctx.sendJson(200, {
      ...enabled,
      files: getFileSettings(),
      announcement: data.announcement,
      maintenance: data.maintenance,
      site_name: data.settings.site_name ?? DEFAULT_SITE_NAME,
      tags: tagStates(data),
      music_playlist: data.music_playlist ?? [],
      music_volume: data.music_volume ?? 0.7,
      custom_tags: data.tags_custom ?? [],
      content_items: data.content_items ?? [],
    });
  }

  // Tạo link rút gọn.
  if (pathname === "/create-short-link") {
    const ip = ctx.clientIp();

    if (rateLimited(ip, MAX_LINK_REQUESTS)) {
      return ctx.sendJson(429, { success: false, message: "Bạn thao tác quá nhanh. Hãy thử lại sau." });
    }
    if (rateLimited(ip, MAX_API_REQUESTS, API_RATE_LIMITS)) {
      return ctx.sendJson(429, { success: false, message: "Bạn đã đạt giới hạn yêu cầu API." });
    }

    const provider = qs(query, "provider", "link4m").toLowerCase();
    const destination = qs(query, "destination", "").toLowerCase();
    const flow = qs(query, "flow", "").toLowerCase();

    if (provider !== "link4m") {
      return ctx.sendJson(400, { success: false, message: "PHONG WEB V2.3 chỉ hỗ trợ Link4M." });
    }
    if (!has(DEFAULT_DESTINATIONS, destination)) {
      return ctx.sendJson(400, { success: false, message: "Mục đích vượt link không hợp lệ." });
    }
    if (!destinationEnabled(destination)) {
      return ctx.sendJson(403, { success: false, message: "Mục này hiện đang tạm khóa." });
    }

    const fileInfo = getFileSettings()[destination] || {};
    if (fileInfo.status !== "available") {
      return ctx.sendJson(403, { success: false, message: "File hiện đang tạm ngưng." });
    }

    const data = loadData();
    if (data.maintenance.enabled) {
      return ctx.sendJson(503, {
        success: false,
        message: data.maintenance.message ?? "Website đang bảo trì.",
      });
    }

    if (!SITE_URL.startsWith("https://")) {
      return ctx.sendJson(500, { success: false, message: "SITE_URL phải là HTTPS." });
    }
    if (!LINK4M_API_TOKEN) {
      return ctx.sendJson(500, { success: false, message: "Chưa cấu hình LINK4M_API_TOKEN trên Render." });
    }

    const token = tokenUrlsafe(32);
    const callbackUrl = SITE_URL + "/provider-return?token=" + encodeURIComponent(token);

    try {
      const shortenedUrl = await createLink4mUrl(callbackUrl);

      SESSIONS.set(token, {
        created: nowSec(),
        returned: false,
        success_counted: false,
        provider: "link4m",
        destination,
        flow,
      });

      addHistory("create", destination, "Đã tạo liên kết Link4M", ip);
      console.log("[V2.3] LINK CREATED:", destination);

      return ctx.sendJson(200, {
        success: true,
        url: shortenedUrl,
        provider: "link4m",
        destination,
      });
    } catch (error) {
      const msg = String(error && error.message ? error.message : error);
      try {
        recordEventCounter("failed", destination, "Lỗi tạo link: " + msg.slice(0, 150), ip);
      } catch (e2) {
        /* bỏ qua */
      }
      console.log("[LINK4M ERROR]", msg.slice(0, 300));
      return ctx.sendJson(502, { success: false, message: msg.slice(0, 220) });
    }
  }

  // Callback Link4M.
  if (pathname === "/provider-return") {
    const token = qs(query, "token", "");

    if (!validToken(token)) return ctx.redirect("/?result=failed");

    let destination = null;
    let shouldCount = false;

    const session = SESSIONS.get(token);
    if (session && nowSec() - session.created <= SESSION_TTL && session.provider === "link4m") {
      destination = session.destination;

      if (!session.returned) {
        session.returned = true;
        session.returned_at = nowSec();
      }
      if (!session.success_counted) {
        session.success_counted = true;
        shouldCount = true;
      }
    }

    if (!destination) return ctx.redirect("/?result=failed");

    if (shouldCount) {
      recordEventCounter("success", destination, "Callback Link4M được tiếp nhận", ctx.clientIp());
    }

    console.log("[V2.3] CALLBACK:", destination);

    const flow = (SESSIONS.get(token) || {}).flow || "";
    if (flow === "nvpkey") {
      return ctx.redirect("/?nvpkey=thanks&token=" + encodeURIComponent(token));
    } else if (flow === "ysm") {
      return ctx.redirect("/?ysm=thanks&token=" + encodeURIComponent(token));
    }
    return ctx.redirect(
      "/?result=thanks&destination=" + encodeURIComponent(destination) + "&token=" + encodeURIComponent(token)
    );
  }

  // Kiểm tra phiên.
  if (pathname === "/check-session") {
    const session = getSession(qs(query, "token", ""));
    if (session && session.returned) {
      return ctx.sendJson(200, {
        success: true,
        returned: true,
        destination: session.destination,
        provider: session.provider,
        message: "Đã nhận callback từ Link4M.",
      });
    }
    return ctx.sendJson(403, {
      success: false,
      returned: false,
      message: "Phiên vượt link không hợp lệ hoặc đã hết hạn.",
    });
  }

  // Các route tải file.
  const downloadKey = Object.keys(DOWNLOAD_ROUTES).find((k) => DOWNLOAD_ROUTES[k] === pathname);
  if (downloadKey) {
    const destination = downloadKey;
    const token = qs(query, "token", "");

    if (!destinationEnabled(destination)) {
      return ctx.sendJson(403, { success: false, message: "Mục tải file hiện đang bị khóa." });
    }

    if (!checkSession(token, destination)) {
      return ctx.sendJson(403, {
        success: false,
        message: "Bạn chưa hoàn thành vượt link cho mục " + DESTINATION_NAMES[destination] + ".",
      });
    }

    const fileInfo = getFileSettings()[destination] || {};
    if (fileInfo.status !== "available") {
      return ctx.sendJson(403, { success: false, message: "File hiện đang tạm ngưng." });
    }

    const target = setting("url_" + destination, DEFAULT_DESTINATIONS[destination]);
    if (!validateDownloadUrl(target)) {
      return ctx.sendJson(500, { success: false, message: "Đường dẫn LẤY FILE chưa hợp lệ." });
    }

    recordEventCounter("download", destination, "Người dùng nhấn LẤY FILE", ctx.clientIp());
    console.log("[V2.3] DOWNLOAD:", destination);
    return ctx.redirect(target);
  }

  // ---------- Admin (GET) ----------
  if (pathname === "/admin/me") return ctx.sendJson(200, { success: ctx.isAdmin() });

  if (pathname === "/admin/csrf") {
    if (!ctx.requireAdmin()) return;
    const session = ADMIN_SESSIONS.get(ctx.adminToken());
    return ctx.sendJson(200, { success: true, csrf: session ? session.csrf || "" : "" });
  }

  if (pathname === "/admin/stats") {
    if (!ctx.requireAdmin()) return;
    return ctx.sendJson(200, { success: true, ...getStatistics() });
  }

  if (pathname === "/admin/daily") {
    if (!ctx.requireAdmin()) return;
    const days = safeCount(qs(query, "days", "7"));
    return ctx.sendJson(200, { success: true, items: getDailyStatistics(days) });
  }

  if (pathname === "/admin/settings") {
    if (!ctx.requireAdmin()) return;
    const items = {};
    for (const key of Object.keys(DEFAULT_DESTINATIONS)) {
      items[key] = {
        name: DESTINATION_NAMES[key],
        enabled: destinationEnabled(key),
        url: setting("url_" + key, DEFAULT_DESTINATIONS[key]),
      };
    }
    return ctx.sendJson(200, { success: true, items, files: getFileSettings() });
  }

  if (pathname === "/admin/site-config") {
    if (!ctx.requireAdmin()) return;
    const data = loadData();
    return ctx.sendJson(200, {
      success: true,
      site_name: data.settings.site_name ?? DEFAULT_SITE_NAME,
      tags: tagStates(data),
      music_playlist: data.music_playlist ?? [],
      music_volume: data.music_volume ?? 0.7,
    });
  }

  if (pathname === "/admin/tags") {
    if (!ctx.requireAdmin()) return;
    return ctx.sendJson(200, { success: true, items: loadData().tags_custom ?? [] });
  }

  if (pathname === "/admin/content") {
    if (!ctx.requireAdmin()) return;
    return ctx.sendJson(200, { success: true, items: loadData().content_items ?? [] });
  }

  if (pathname === "/admin/backup.json") {
    if (!ctx.requireAdmin()) return;
    const stored = loadData();
    const payload = {
      format: "PHONG_WEB_BACKUP",
      version: "2.7.2",
      created_at: vietnamIso(),
      config: {
        settings: stored.settings ?? {},
        files: stored.files ?? {},
        announcement: stored.announcement ?? {},
        maintenance: stored.maintenance ?? {},
        music_playlist: stored.music_playlist ?? [],
        music_volume: stored.music_volume ?? 0.7,
        tags_custom: stored.tags_custom ?? [],
        content_items: stored.content_items ?? [],
      },
    };
    const raw = Buffer.from(JSON.stringify(payload, null, 2), "utf8");
    return ctx.sendRaw(200, raw, {
      "Content-Type": "application/json; charset=utf-8",
      "Content-Disposition": 'attachment; filename="phong-web-backup-v2.7.2.json"',
    });
  }

  if (pathname === "/admin/export.csv") {
    if (!ctx.requireAdmin()) return;
    const stored = loadData();
    const rows = [["date", "visits", "total", "android", "iphone", "downloads"]];
    for (const day of Object.keys(stored.daily).sort()) {
      const info = isObj(stored.daily[day]) ? stored.daily[day] : {};
      rows.push([
        day,
        safeCount(info.visits),
        stored.stats.total ?? 0,
        stored.stats.android ?? 0,
        stored.stats.iphone ?? 0,
        stored.stats.downloads ?? 0,
      ]);
    }
    const csvCell = (v) => {
      const s = String(v);
      return /[",\r\n]/.test(s) ? '"' + s.replace(/"/g, '""') + '"' : s;
    };
    const text = rows.map((r) => r.map(csvCell).join(",")).join("\r\n") + "\r\n";
    const raw = Buffer.from("\ufeff" + text, "utf8");
    return ctx.sendRaw(200, raw, {
      "Content-Type": "text/csv; charset=utf-8",
      "Content-Disposition": "attachment; filename=phong-web-report.csv",
    });
  }

  if (pathname === "/admin/history") {
    if (!ctx.requireAdmin()) return;

    const search = safeText(qs(query, "q", ""), 100).toLowerCase();
    const event = safeText(qs(query, "event", ""), 40);
    const records = loadData().history.slice().reverse();
    const filtered = [];

    for (const item of records) {
      if (event && item.event !== event) continue;

      const searchable = [item.time, item.event, item.name, item.detail, item.ip]
        .map((v) => (v === undefined || v === null ? "" : String(v)))
        .join(" ")
        .toLowerCase();

      if (search && !searchable.includes(search)) continue;

      filtered.push(item);
      if (filtered.length >= 300) break;
    }
    return ctx.sendJson(200, { success: true, items: filtered });
  }

  if (pathname === "/admin/notice") {
    if (!ctx.requireAdmin()) return;
    const data = loadData();
    return ctx.sendJson(200, {
      success: true,
      announcement: data.announcement,
      maintenance: data.maintenance,
    });
  }

  if (pathname === "/admin/logs") {
    if (!ctx.requireAdmin()) return;
    const logs = loadData().admin_logs.slice().reverse();
    return ctx.sendJson(200, { success: true, items: logs.slice(0, 200) });
  }

  // File tĩnh.
  if (STATIC_FILES.has(pathname)) return ctx.sendStaticFile(pathname);

  // Route cũ.
  if (pathname === "/create-link") return ctx.redirect("/dinh-vi");
  if (pathname === "/create-link4m") return ctx.redirect("/menu");
  if (pathname === "/complete") return ctx.redirect("/");

  if (pathname === "/link4m-return") {
    return ctx.redirect("/provider-return?token=" + encodeURIComponent(qs(query, "token", "")));
  }

  if (pathname === "/check-link4m") {
    if (checkSession(qs(query, "token", ""), "deta")) {
      return ctx.sendJson(200, { success: true, message: "Đã xác nhận phiên." });
    }
    return ctx.sendJson(403, { success: false, message: "Phiên không hợp lệ." });
  }

  return ctx.sendJson(404, { success: false, message: "Không tìm thấy đường dẫn." });
}

// =========================================================
// POST ROUTES
// =========================================================

function cleanTagList(items, strict, ctx) {
  // strict = true: báo lỗi khi Tag sai (khôi phục backup); false: bỏ qua mục sai.
  const clean = [];
  const seen = new Set();
  for (const item of items) {
    if (!isObj(item)) continue;
    const name = safeText(item.name, 60);
    const slug = safeText(item.slug, 40).toLowerCase();
    const icon = safeText(getOr(item, "icon", "🏷️"), 12);
    if (!name || !slug || !isAlnumSlug(slug) || seen.has(slug)) {
      if (strict) return null;
      continue;
    }
    seen.add(slug);
    clean.push({ name, slug, icon, enabled: item.enabled !== false, order: clean.length });
  }
  return clean;
}

function cleanContentList(items, strict) {
  const clean = [];
  const seen = new Set();
  for (const item of items) {
    if (!isObj(item)) continue;
    const slug = safeText(item.slug, 50).toLowerCase();
    const name = safeText(item.name, 120);
    const tag = safeText(item.tag, 40).toLowerCase();
    const description = safeText(item.description, 500);
    let image = safeText(getOr(item, "image", "/logo.png"), 500);
    const url = safeText(item.url, 1000);

    if (!slug || !isAlnumSlug(slug) || seen.has(slug) || !name || !validateHttpUrl(url)) {
      if (strict) return null;
      continue;
    }
    if (!validateImageUrl(image)) image = "/logo.png";
    seen.add(slug);
    clean.push({
      slug, name, tag, description, image, url,
      enabled: item.enabled !== false,
      order: clean.length,
    });
  }
  return clean;
}

async function handlePost(ctx, url) {
  const pathname = url.pathname;
  const data = await ctx.readJson();

  if (data === null) {
    return ctx.sendJson(400, { success: false, message: "Dữ liệu gửi lên không hợp lệ." });
  }

  // Đăng nhập Admin.
  if (pathname === "/admin/login") {
    const ip = ctx.clientIp();

    if (rateLimited("admin:" + ip, MAX_LOGIN_ATTEMPTS)) {
      addAdminLog("LOGIN_BLOCKED", ip, "Quá nhiều lần đăng nhập");
      return ctx.sendJson(429, { success: false, message: "Quá nhiều lần đăng nhập. Hãy thử lại sau." });
    }

    const password = getOr(data, "password", "");
    if (typeof password !== "string" || !compareDigest(hashText(password), hashText(ADMIN_PASSWORD))) {
      addAdminLog("LOGIN_FAILED", ip, "Sai mật khẩu");
      return ctx.sendJson(401, { success: false, message: "Mật khẩu quản trị không chính xác." });
    }

    const token = tokenUrlsafe(36);
    const csrf = tokenUrlsafe(32);
    const now = nowSec();

    for (const [oldToken, s] of ADMIN_SESSIONS) {
      if (
        now - (s.created ?? 0) > ADMIN_TTL ||
        now - (s.last_seen ?? s.created ?? 0) > ADMIN_IDLE_TTL
      ) {
        ADMIN_SESSIONS.delete(oldToken);
      }
    }
    if (ADMIN_SESSIONS.size >= MAX_ADMIN_SESSIONS) {
      return ctx.sendJson(429, {
        success: false,
        message: "Đã đạt giới hạn 3 phiên Admin. Hãy thu hồi phiên cũ.",
      });
    }
    ADMIN_SESSIONS.set(token, { created: now, last_seen: now, csrf });

    addAdminLog("LOGIN_SUCCESS", ip, "Đăng nhập thành công");

    return ctx.sendJson(
      200,
      { success: true, message: "Đăng nhập thành công." },
      {
        "Set-Cookie":
          "ph_admin=" + token + "; Path=/; HttpOnly; SameSite=Strict; Max-Age=" + ADMIN_TTL + SECURE_FLAG(),
      }
    );
  }

  // Mọi thao tác ghi của Admin đều cần CSRF.
  if (pathname.startsWith("/admin/")) {
    if (!ctx.requireCsrf()) return;
    if (rateLimited("admin:" + ctx.adminToken(), 90, ADMIN_WRITE_LIMITS)) {
      return ctx.sendJson(429, {
        success: false,
        message: "Bạn thao tác quá nhanh. Vui lòng chờ một phút.",
      });
    }
  }

  const bad = (message) => ctx.sendJson(400, { success: false, message });

  // ---------- Khôi phục backup ----------
  if (pathname === "/admin/restore-backup") {
    if (
      data.format !== "PHONG_WEB_BACKUP" ||
      !["2.6.0", "2.7.0", "2.7.1", "2.7.2"].includes(data.version)
    ) {
      return bad("Định dạng backup không hợp lệ.");
    }
    const config = data.config;
    if (!isObj(config)) return bad("Thiếu phần cấu hình trong backup.");

    const { settings, files, announcement, maintenance, music_playlist: playlist, tags_custom: tags, content_items: contents } = config;

    if (![settings, files, announcement, maintenance].every(isObj)) {
      return bad("Cấu trúc thiết lập hoặc file không hợp lệ.");
    }
    if (!Array.isArray(playlist) || playlist.length < 1 || playlist.length > 50) {
      return bad("Danh sách nhạc phải có từ 1 đến 50 bài.");
    }
    if (!Array.isArray(tags) || tags.length > 40 || !Array.isArray(contents) || contents.length > 200) {
      return bad("Danh sách Tag hoặc nội dung vượt giới hạn.");
    }

    const cleanPlaylist = [];
    for (const track of playlist) {
      if (!isObj(track)) return bad("Dữ liệu bài nhạc không hợp lệ.");
      const name = safeText(track.name, 80);
      const src = safeText(track.src, 500);
      if (!name || !validMusicSrc(src)) return bad("Đường dẫn nhạc trong backup không hợp lệ.");
      cleanPlaylist.push({ name, src, enabled: track.enabled !== false });
    }

    const cleanTags = cleanTagList(tags, true);
    if (cleanTags === null) return bad("Tag trong backup không hợp lệ hoặc bị trùng slug.");

    const cleanContents = cleanContentList(contents, true);
    if (cleanContents === null) return bad("Nội dung trong backup không hợp lệ.");

    const cleanSettings = {};
    for (const [rawKey, value] of Object.entries(settings)) {
      const key = safeText(rawKey, 100);
      if (key.startsWith("url_") || key.startsWith("enabled_") || key.startsWith("tag_") || key === "site_name") {
        cleanSettings[key] = safeText(String(value), 1000);
      }
    }

    const cleanFiles = {};
    for (const [key, value] of Object.entries(files)) {
      if (!has(DEFAULT_FILES, key) || !isObj(value)) continue;
      let image = safeText(getOr(value, "image", "/logo.png"), 500);
      if (!validateImageUrl(image)) image = "/logo.png";
      cleanFiles[key] = {
        name: safeText(value.name, 120),
        size: safeText(value.size, 40),
        status: ["available", "unavailable"].includes(value.status) ? value.status : "available",
        image,
        downloads: safeCount(getOr(value, "downloads", 0)),
      };
    }

    const musicVolume = clampVolume(getOr(config, "music_volume", 0.7), 0.7);
    const cleanAnnouncement = {
      enabled: announcement.enabled === true,
      message: safeText(announcement.message, 1000),
    };
    const cleanMaintenance = {
      enabled: maintenance.enabled === true,
      message: safeText(maintenance.message, 1000) || DEFAULT_MAINTENANCE_MESSAGE,
    };

    const stored = loadData();
    Object.assign(stored.settings, cleanSettings);
    for (const key of Object.keys(DEFAULT_FILES)) {
      if (has(cleanFiles, key)) stored.files[key] = cleanFiles[key];
    }
    stored.announcement = cleanAnnouncement;
    stored.maintenance = cleanMaintenance;
    stored.music_playlist = cleanPlaylist;
    stored.music_volume = musicVolume;
    stored.tags_custom = cleanTags;
    stored.content_items = cleanContents;
    saveData(stored);

    addAdminLog("RESTORE_BACKUP", ctx.clientIp(), "Khôi phục cấu hình V2.7.2");
    return ctx.sendJson(200, {
      success: true,
      message: "Đã khôi phục cấu hình website. Thống kê, lịch sử và nhật ký được giữ nguyên.",
    });
  }

  // ---------- Tag ----------
  if (pathname === "/admin/tags") {
    const items = data.items;
    if (!Array.isArray(items) || items.length > 40) return bad("Danh sách Tag không hợp lệ (tối đa 40).");
    const clean = cleanTagList(items, false);
    const stored = loadData();
    stored.tags_custom = clean;
    saveData(stored);
    addAdminLog("UPDATE_TAGS", ctx.clientIp(), `Lưu ${clean.length} Tag`);
    return ctx.sendJson(200, { success: true, message: "Đã lưu danh mục Tag." });
  }

  // ---------- Nội dung ----------
  if (pathname === "/admin/content") {
    const items = data.items;
    if (!Array.isArray(items) || items.length > 200) {
      return bad("Danh sách nội dung không hợp lệ (tối đa 200).");
    }
    const clean = cleanContentList(items, false);
    const stored = loadData();
    stored.content_items = clean;
    saveData(stored);
    addAdminLog("UPDATE_CONTENT", ctx.clientIp(), `Lưu ${clean.length} mục nội dung`);
    return ctx.sendJson(200, { success: true, message: "Đã lưu nội dung website." });
  }

  // ---------- Thu hồi phiên Admin khác ----------
  if (pathname === "/admin/revoke-sessions") {
    const current = ctx.adminToken();
    let revoked = 0;
    for (const other of Array.from(ADMIN_SESSIONS.keys())) {
      if (other !== current) {
        ADMIN_SESSIONS.delete(other);
        revoked += 1;
      }
    }
    addAdminLog("REVOKE_SESSIONS", ctx.clientIp(), `Thu hồi ${revoked} phiên khác`);
    return ctx.sendJson(200, { success: true, message: `Đã thu hồi ${revoked} phiên Admin khác.` });
  }

  // ---------- Đăng xuất ----------
  if (pathname === "/admin/logout") {
    ADMIN_SESSIONS.delete(ctx.adminToken());
    addAdminLog("LOGOUT", ctx.clientIp(), "Đăng xuất");
    return ctx.sendJson(
      200,
      { success: true, message: "Đã đăng xuất." },
      { "Set-Cookie": "ph_admin=; Path=/; HttpOnly; SameSite=Strict; Max-Age=0" }
    );
  }

  // ---------- Lưu thiết lập mục tải file ----------
  if (pathname === "/admin/settings") {
    const items = data.items;
    const files = getOr(data, "files", {});

    if (!isObj(items) || !isObj(files)) return bad("Thiếu dữ liệu thiết lập.");

    for (const key of Object.keys(DEFAULT_DESTINATIONS)) {
      const item = items[key];
      const fileInfo = has(files, key) ? files[key] : {};

      if (!isObj(item) || !isObj(fileInfo)) return bad("Thiếu cấu hình mục " + key);

      if (!validateDownloadUrl(item.url)) {
        return bad("Link của " + DESTINATION_NAMES[key] + " phải là liên kết HTTPS hợp lệ.");
      }
      if (typeof item.enabled !== "boolean") return bad("Trạng thái bật/tắt không hợp lệ.");

      if (!["available", "unavailable"].includes(getOr(fileInfo, "status", "available"))) {
        return bad("Trạng thái file không hợp lệ.");
      }
      if (!validateImageUrl(getOr(fileInfo, "image", "/logo.png"))) {
        return bad("Ảnh đại diện phải là URL HTTPS hoặc ảnh nội bộ cho phép.");
      }
      if (safeText(fileInfo.name, 120).length > 120) return bad("Tên file quá dài.");
    }

    const stored = loadData();
    for (const key of Object.keys(DEFAULT_DESTINATIONS)) {
      const item = items[key];
      const fileInfo = has(files, key) ? files[key] : {};

      stored.settings["url_" + key] = item.url.trim();
      stored.settings["enabled_" + key] = item.enabled ? "1" : "0";

      const oldDownloads = safeCount(stored.files[key].downloads);
      stored.files[key] = {
        name: safeText(fileInfo.name, 120),
        size: safeText(fileInfo.size, 40),
        status: getOr(fileInfo, "status", "available"),
        image: String(getOr(fileInfo, "image", "/logo.png")).trim(),
        downloads: oldDownloads,
      };
    }
    saveData(stored);

    addAdminLog("UPDATE_SETTINGS", ctx.clientIp(), "Cập nhật cấu hình mục tải file");
    console.log("[V2.3] ADMIN UPDATED SETTINGS");
    return ctx.sendJson(200, { success: true, message: "Đã lưu thiết lập thành công." });
  }

  // ---------- Cấu hình website ----------
  if (pathname === "/admin/site-config") {
    const siteName = safeText(getOr(data, "site_name", ""), 80);
    const tags = data.tags;
    const playlist = data.music_playlist;
    const musicVolume = clampVolume(getOr(data, "music_volume", 0.7), 0.7);

    if (!siteName || !isObj(tags) || !Array.isArray(playlist)) {
      return bad("Thiếu cấu hình website, Tag hoặc danh sách nhạc.");
    }

    const normalizedTags = {};
    for (const key of TAG_KEYS) {
      if (typeof tags[key] !== "boolean") return bad("Trạng thái Tag không hợp lệ.");
      normalizedTags[key] = tags[key] ? "1" : "0";
    }

    if (playlist.length < 1 || playlist.length > 50) return bad("Danh sách nhạc cần từ 1 đến 50 bài.");

    const cleanPlaylist = [];
    for (const track of playlist) {
      if (!isObj(track)) return bad("Bài nhạc không hợp lệ.");
      const name = safeText(track.name, 80);
      const src = safeText(track.src, 500);
      if (!name || !validMusicSrc(src)) {
        return bad("Bài nhạc cần tên và đường dẫn MP3 nội bộ hoặc HTTPS.");
      }
      cleanPlaylist.push({ name, src, enabled: track.enabled !== false });
    }

    const stored = loadData();
    stored.settings.site_name = siteName;
    for (const [key, value] of Object.entries(normalizedTags)) stored.settings["tag_" + key] = value;
    stored.music_playlist = cleanPlaylist;
    stored.music_volume = musicVolume;
    saveData(stored);

    addAdminLog("UPDATE_SITE_CONFIG", ctx.clientIp(), "Cập nhật tên web, Tag và danh sách nhạc");
    return ctx.sendJson(200, { success: true, message: "Đã lưu tên website, Tag và danh sách nhạc." });
  }

  // ---------- Thông báo + bảo trì ----------
  if (pathname === "/admin/notice") {
    const announcement = data.announcement;
    const maintenance = data.maintenance;

    if (!isObj(announcement) || !isObj(maintenance)) return bad("Dữ liệu thông báo không hợp lệ.");
    if (typeof announcement.enabled !== "boolean") return bad("Trạng thái thông báo không hợp lệ.");
    if (typeof maintenance.enabled !== "boolean") return bad("Trạng thái bảo trì không hợp lệ.");

    const stored = loadData();
    stored.announcement = {
      enabled: announcement.enabled,
      message: safeText(announcement.message, 1000),
    };
    stored.maintenance = {
      enabled: maintenance.enabled,
      message: safeText(maintenance.message, 1000) || DEFAULT_MAINTENANCE_MESSAGE,
    };
    saveData(stored);

    addAdminLog("UPDATE_NOTICE", ctx.clientIp(), "Cập nhật thông báo/bảo trì");
    return ctx.sendJson(200, { success: true, message: "Đã cập nhật thông báo." });
  }

  // ---------- Đổi mật khẩu Admin ----------
  if (pathname === "/admin/change-password") {
    const oldPassword = getOr(data, "oldPassword", "");
    const newPassword = getOr(data, "newPassword", "");

    if (typeof oldPassword !== "string" || typeof newPassword !== "string") {
      return bad("Mật khẩu không hợp lệ.");
    }
    if (!compareDigest(hashText(oldPassword), hashText(ADMIN_PASSWORD))) {
      return ctx.sendJson(403, { success: false, message: "Mật khẩu hiện tại không chính xác." });
    }
    if (Array.from(newPassword).length < 8 || Array.from(newPassword).length > 200) {
      return bad("Mật khẩu mới phải có từ 8 đến 200 ký tự.");
    }
    return bad(
      "Không thể thay đổi biến môi trường trực tiếp. " +
        "Hãy cập nhật ADMIN_PASSWORD trên Render rồi khởi động lại."
    );
  }

  // ---------- Xóa thống kê ----------
  if (pathname === "/admin/reset-stats") {
    if (data.confirm !== true) return bad("Thiếu xác nhận xóa dữ liệu.");

    const stored = loadData();
    stored.stats = { total: 0, android: 0, iphone: 0, success: 0, failed: 0, downloads: 0 };
    stored.daily = {};
    stored.history = [];
    stored.visitors = {};
    stored.visitor_devices = {};
    for (const key of Object.keys(DEFAULT_DESTINATIONS)) stored.files[key].downloads = 0;
    saveData(stored);

    addAdminLog("RESET_STATISTICS", ctx.clientIp(), "Đã xóa dữ liệu thống kê");
    return ctx.sendJson(200, { success: true, message: "Đã xóa dữ liệu thống kê." });
  }

  return ctx.sendJson(404, { success: false, message: "Không tìm thấy API." });
}

// =========================================================
// KHỞI ĐỘNG MÁY CHỦ
// =========================================================

const server = http.createServer(async (req, res) => {
  const ctx = new Ctx(req, res);
  const started = res;

  res.on("finish", () => {
    console.log("[PHONG WEB V2.7.2]", ctx.clientIp(), `"${req.method} ${req.url}"`, res.statusCode);
  });

  try {
    const url = new URL(req.url, "http://localhost");

    if (req.method === "GET") return await handleGet(ctx, url);
    if (req.method === "POST") return await handlePost(ctx, url);

    res.writeHead(501, { "Content-Type": "text/plain; charset=utf-8", ...securityHeaders() });
    res.end("Unsupported method");
  } catch (error) {
    console.log("[SERVER ERROR]", error && error.stack ? error.stack : error);
    if (!res.headersSent) {
      ctx.sendJson(500, { success: false, message: "Lỗi máy chủ nội bộ." });
    } else {
      res.destroy();
    }
  }
});

server.headersTimeout = 30000;

if (require.main === module) {
  initData();

  console.log("======================================");
  console.log("       NGUYEN VAN PHONG WEBSITE");
  console.log("              V2.7.2 (Node.js)");
  console.log("======================================");

  console.log("Port:", PORT);
  console.log("JSON:", DATA_FILE);
  console.log("Link4M:", LINK4M_API_TOKEN ? "ENABLED" : "MISSING API TOKEN");

  console.log("Admin page: /admin");
  console.log("Admin password: Set by ADMIN_PASSWORD");
  if (ADMIN_PASSWORD === "152012") {
    console.log(
      "[SECURITY WARNING] ADMIN_PASSWORD đang dùng mật khẩu mặc định. Hãy đổi trong Render Environment."
    );
  }
  console.log("Storage: JSON");
  console.log("Online timeout:", VISITOR_TIMEOUT, "seconds");
  console.log("Visitor Session TTL:", SESSION_TTL, "seconds");
  console.log("Admin idle TTL:", ADMIN_IDLE_TTL, "seconds");
  console.log("Max Admin Sessions:", MAX_ADMIN_SESSIONS);
  console.log("Admin TTL:", ADMIN_TTL, "seconds");

  console.log("Categories: /?category=freefire | lienquan | roblox");
  for (const key of Object.keys(DESTINATION_ROUTES)) {
    console.log(DESTINATION_NAMES[key] + ":", DESTINATION_ROUTES[key]);
  }
  console.log("Callback: /provider-return");
  console.log("Session check: /check-session");
  console.log("Admin settings: /admin/settings");
  console.log("Providers: LINK4M ONLY");
  console.log("======================================");

  server.listen(PORT, "0.0.0.0");

  const shutdown = () => {
    console.log("[PHONG WEB] Server stopped.");
    server.close(() => process.exit(0));
    setTimeout(() => process.exit(0), 1000).unref();
  };
  process.on("SIGINT", shutdown);
  process.on("SIGTERM", shutdown);
}

module.exports = { server };
