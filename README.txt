PHONG WEB - BAN SUA LOI DONG BO CAU HINH LINK4M

Ban nay da nap 6 muc tai tu file backup cua ban vao config-seed.json.
Khi backend Render chua co cau hinh, server se tu nap 6 muc nay de API
/api/link4m/create khong con tra ve "Muc tai khong kha dung".

CACH CAP NHAT:
1. Giai nen ZIP.
2. Thay cac file index.html, server.js, package.json tren GitHub bang file moi.
3. Them file config-seed.json vao cung thu muc voi server.js.
4. Commit va push len nhanh main de Render tu deploy.
5. Tren Render Environment kiem tra:
   SITE_URL=https://nvp212.onrender.com
   DATA_DIR=/tmp/phong-data (neu dang dung Free, khong co Persistent Disk)
   LINK4M_API_TOKEN=token Link4M moi
   ADMIN_PASSWORD=mat khau quan tri moi
   JWT_SECRET=chuoi bi mat moi
6. Deploy thanh cong, vao https://nvp212.onrender.com, dang nhap quan tri bang
   ADMIN_PASSWORD, vao Muc tai file va bam LUU THAY DOI de dong bo cac chinh sua
   ve backend.

LUU Y:
- File config-seed.json chi chua cau hinh website va 6 URL tai file; khong chua token,
  mat khau hay JWT_SECRET.
- DATA_DIR=/tmp/phong-data co the mat thong ke/cau hinh da chinh sua khi instance
  bi thay the. Muon luu lau dai can Persistent Disk mount tai /var/data.
- Neu token da lo trong anh/chat, hay thu hoi va tao token moi. Khong commit token
  vao GitHub.
