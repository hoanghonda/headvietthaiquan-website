#!/usr/bin/env python3
"""
Sinh lại danh sách bài viết cho /tin-tuc/, các trang chuyên mục và sitemap.xml
từ file registry tin-tuc/bai-viet.json.

Cách dùng:  python3 tools/build-tin-tuc.py
Chạy lại mỗi khi thêm/sửa bài trong bai-viet.json. Không sửa tay phần nằm giữa
các marker <!-- BAI-VIET:START --> ... <!-- BAI-VIET:END --> trong HTML.
"""
import json, re, sys, html
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOMAIN = "https://headvietthaiquan.vn"
REGISTRY = ROOT / "tin-tuc" / "bai-viet.json"

# Chuyên mục (tham khảo cách chia của dat.bike: Tin tức & Sự kiện / Kiến thức / Cộng đồng).
# Thêm chuyên mục mới: thêm dòng ở đây VÀ tạo thư mục tin-tuc/<slug>/index.html (copy từ chuyên mục có sẵn).
CATEGORIES = {
    "tin-tuc-su-kien": {
        "ten": "Tin tức & Sự kiện",
        "mo_ta": "Xe mới ra mắt, chương trình và sự kiện tại HEAD Việt Thái Quân.",
    },
    "kien-thuc": {
        "ten": "Kiến thức",
        "mo_ta": "Kinh nghiệm bảo dưỡng, mua xe trả góp, so sánh và mẹo sử dụng xe Honda.",
    },
    "cong-dong": {
        "ten": "Cộng đồng",
        "mo_ta": "Hoạt động an toàn giao thông, tặng mũ bảo hiểm và đồng hành cùng địa phương.",
    },
}

# Các trang cố định trong sitemap (ngoài bài viết & chuyên mục, được sinh tự động).
STATIC_PAGES = [
    ("/", "2026-09-01", "1.0"),
    ("/head-viet-thai-quan-1/", "2026-09-01", "0.9"),
    ("/head-viet-thai-quan-2/", "2026-09-01", "0.9"),
    ("/xe-may/", "2026-09-01", "0.8"),
    ("/xe-may/vario125/", "2026-09-01", "0.8"),
    ("/dich-vu/", "2026-09-01", "0.8"),
    ("/khuyen-mai/", "2026-09-01", "0.9"),
]

START = "<!-- BAI-VIET:START -->"
END = "<!-- BAI-VIET:END -->"
CHIP_START = "<!-- DANH-MUC:START -->"
CHIP_END = "<!-- DANH-MUC:END -->"


def vn_date(iso):
    y, m, d = iso.split("-")
    return f"{d}/{m}/{y}"


def load_registry():
    posts = json.loads(REGISTRY.read_text(encoding="utf-8"))
    errors = []
    seen = set()
    for p in posts:
        for k in ("slug", "tieu_de", "danh_muc", "mo_ta", "ngay_dang", "anh", "alt"):
            if not p.get(k):
                errors.append(f"{p.get('slug','?')}: thiếu trường '{k}'")
        if p["slug"] in seen:
            errors.append(f"{p['slug']}: slug trùng")
        seen.add(p["slug"])
        if p["danh_muc"] not in CATEGORIES:
            errors.append(f"{p['slug']}: chuyên mục '{p['danh_muc']}' không tồn tại (có: {', '.join(CATEGORIES)})")
        if not re.fullmatch(r"[a-z0-9]+(-[a-z0-9]+)*", p["slug"]):
            errors.append(f"{p['slug']}: slug chỉ dùng a-z, 0-9 và dấu gạch ngang, không dấu")
        if not re.fullmatch(r"\d{4}-\d{2}-\d{2}", p["ngay_dang"]):
            errors.append(f"{p['slug']}: ngay_dang phải dạng YYYY-MM-DD")
        if not (ROOT / "tin-tuc" / p["slug"] / "index.html").exists():
            errors.append(f"{p['slug']}: chưa có file tin-tuc/{p['slug']}/index.html")
        p.setdefault("ngay_sua", p["ngay_dang"])
    if errors:
        print("LỖI trong bai-viet.json:\n  - " + "\n  - ".join(errors))
        sys.exit(1)
    posts.sort(key=lambda p: (p["ngay_dang"], p["slug"]), reverse=True)
    return posts


def card(p):
    cat = CATEGORIES[p["danh_muc"]]["ten"]
    return (
        f'      <a class="card" href="/tin-tuc/{p["slug"]}/">'
        f'<span class="badge">{html.escape(cat)}</span>'
        f'<h3>{html.escape(p["tieu_de"])}</h3>'
        f'<p>{html.escape(p["mo_ta"])}</p>'
        f'<span class="ngay">{vn_date(p["ngay_dang"])}</span></a>'
    )


def cards_block(posts):
    if not posts:
        return '      <div class="card"><h3>Chưa có bài viết</h3><p>Chuyên mục này sẽ sớm được cập nhật.</p></div>'
    return "\n".join(card(p) for p in posts)


def chips_block(active):
    items = [('/tin-tuc/', 'Tất cả', active is None)]
    items += [(f"/tin-tuc/{slug}/", c["ten"], active == slug) for slug, c in CATEGORIES.items()]
    items.append(("/khuyen-mai/", "Khuyến mãi", False))
    out = []
    for href, ten, is_active in items:
        cls = ' class="active"' if is_active else ""
        out.append(f'      <a href="{href}"{cls}>{html.escape(ten)}</a>')
    return "\n".join(out)


def replace_between(text, start, end, body, path):
    if start not in text or end not in text:
        print(f"LỖI: {path} thiếu marker {start} / {end}")
        sys.exit(1)
    pre, rest = text.split(start, 1)
    _, post = rest.split(end, 1)
    return f"{pre}{start}\n{body}\n      {end}{post}"


def write_listing(path, posts, active):
    text = path.read_text(encoding="utf-8")
    text = replace_between(text, CHIP_START, CHIP_END, chips_block(active), path)
    text = replace_between(text, START, END, cards_block(posts), path)
    path.write_text(text, encoding="utf-8")
    print(f"  ✔ {path.relative_to(ROOT)} ({len(posts)} bài)")


def write_sitemap(posts):
    latest = max(p["ngay_sua"] for p in posts) if posts else "2026-09-01"
    lines = ['<?xml version="1.0" encoding="UTF-8"?>',
             '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
    for loc, mod, pri in STATIC_PAGES:
        lines.append(f"  <url><loc>{DOMAIN}{loc}</loc><lastmod>{mod}</lastmod><priority>{pri}</priority></url>")
    lines.append(f"  <url><loc>{DOMAIN}/tin-tuc/</loc><lastmod>{latest}</lastmod><priority>0.7</priority></url>")
    for slug in CATEGORIES:
        cat_posts = [p for p in posts if p["danh_muc"] == slug]
        mod = max(p["ngay_sua"] for p in cat_posts) if cat_posts else latest
        lines.append(f"  <url><loc>{DOMAIN}/tin-tuc/{slug}/</loc><lastmod>{mod}</lastmod><priority>0.6</priority></url>")
    for p in posts:
        lines.append(f"  <url><loc>{DOMAIN}/tin-tuc/{p['slug']}/</loc><lastmod>{p['ngay_sua']}</lastmod><priority>0.7</priority></url>")
    lines.append("</urlset>")
    (ROOT / "sitemap.xml").write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"  ✔ sitemap.xml ({len(lines) - 3} URL)")


def main():
    posts = load_registry()
    print("Sinh danh sách bài viết:")
    write_listing(ROOT / "tin-tuc" / "index.html", posts, None)
    for slug in CATEGORIES:
        page = ROOT / "tin-tuc" / slug / "index.html"
        if not page.exists():
            print(f"LỖI: thiếu trang chuyên mục {page.relative_to(ROOT)}")
            sys.exit(1)
        write_listing(page, [p for p in posts if p["danh_muc"] == slug], slug)
    write_sitemap(posts)


if __name__ == "__main__":
    main()
