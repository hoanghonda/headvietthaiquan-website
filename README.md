# Website HEAD Viet Thai Quan

Source code cua headvietthaiquan.vn - dai ly Honda uy nhiem (HEAD) tai TP.HCM.
Deploy tu dong qua Vercel khi co commit moi vao nhanh main.

Da ket noi GitHub - Vercel: moi commit vao nhanh main se tu dong deploy len headvietthaiquan.vn.

## Dang tin tuc (chuan SEO)

- Quy trinh day du: `docs/QUY-TRINH-DANG-TIN.md`
- Chuyen muc: Tin tuc & Su kien · Kien thuc · Cong dong (`/tin-tuc/<chuyen-muc>/`)
- Tao bai: `python3 tools/tao-bai-viet.py --help`
- Sinh lai danh muc + sitemap: `python3 tools/build-tin-tuc.py`
- Kiem tra SEO truoc khi commit: `python3 tools/kiem-tra-seo.py`
- Trong Claude Code: go `/dang-tin` kem noi dung bai.

## Logo chinh thuc (bo file o thu muc goc)

- `logo-vtq-mark.png` – bieu tuong VTQ (khong co dong chu) dung o header cung ten + dong mo ta, 2x cho man hinh retina.
- `logo-vtq-600.png` – logo 600px dung o footer va truong `logo` trong JSON-LD (Organization / MotorcycleDealer / publisher).
- `og-logo.jpg` – anh 1200x630 dung lam `og:image` mac dinh cho cac trang khong co anh rieng.
- `favicon.ico`, `favicon-192.png`, `favicon-512.png`, `apple-touch-icon.png` – bieu tuong tab trinh duyet / them vao man hinh chinh.

File goc: "VTQ Logo 190523-01" (PNG 4167x4167) tren Google Drive cong ty. Khi doi logo, thay ca bo file tren, giu nguyen ten.
