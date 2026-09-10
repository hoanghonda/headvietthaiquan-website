#!/usr/bin/env python3
"""
Kiểm tra SEO cho toàn bộ bài viết trong /tin-tuc/ (hoặc 1 slug nếu truyền vào).
  python3 tools/kiem-tra-seo.py            # kiểm tra tất cả
  python3 tools/kiem-tra-seo.py <slug>     # kiểm tra 1 bài
Thoát mã 1 nếu có LỖI (cảnh báo không làm fail).
"""
import json, re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOMAIN = "https://headvietthaiquan.vn"
sys.path.insert(0, str(ROOT / "tools"))
from importlib import import_module
build = import_module("build-tin-tuc")
CATEGORIES = build.CATEGORIES

errors, warns = [], []


def err(slug, msg): errors.append(f"[{slug}] {msg}")
def warn(slug, msg): warns.append(f"[{slug}] {msg}")


def attr(text, pattern):
    m = re.search(pattern, text)
    return m.group(1) if m else None


def link_exists(href):
    if href.startswith(("http", "tel:", "mailto:", "#")):
        return True
    path = href.split("#")[0].split("?")[0]
    target = ROOT / path.lstrip("/")
    return target.exists() or (target / "index.html").exists()


def check_article(p, listings):
    slug = p["slug"]
    f = ROOT / "tin-tuc" / slug / "index.html"
    if not f.exists():
        err(slug, "thiếu index.html"); return
    t = f.read_text(encoding="utf-8")
    url = f"{DOMAIN}/tin-tuc/{slug}/"

    title = attr(t, r"<title>(.*?)</title>")
    if not title: err(slug, "thiếu <title>")
    elif len(title) > 65: warn(slug, f"<title> dài {len(title)} ký tự (nên ≤ 65)")
    elif len(title) < 30: warn(slug, f"<title> ngắn {len(title)} ký tự (nên ≥ 30)")

    desc = attr(t, r'<meta name="description" content="(.*?)">')
    if not desc: err(slug, "thiếu meta description")
    elif not 80 <= len(desc) <= 165: warn(slug, f"meta description {len(desc)} ký tự (nên 80–160)")

    if attr(t, r'<link rel="canonical" href="(.*?)">') != url: err(slug, f"canonical phải là {url}")
    for prop in ("og:title", "og:description", "og:url", "og:image", "og:type"):
        if f'property="{prop}"' not in t: err(slug, f"thiếu {prop}")
    og_url = attr(t, r'<meta property="og:url" content="(.*?)">')
    if og_url and og_url != url: err(slug, "og:url khác canonical")

    if t.count("<h1") != 1: err(slug, f"phải có đúng 1 <h1> (đang có {t.count('<h1')})")
    if t.count("<h2") < 2: warn(slug, "nên có ít nhất 2 <h2>")
    if "TODO" in t: err(slug, "còn ghi chú TODO trong bài")
    if "{{" in t: err(slug, "còn placeholder {{...}} chưa thay")

    # JSON-LD
    blocks = re.findall(r'<script type="application/ld\+json">\s*(\{.*?\})\s*</script>', t, re.S)
    types = []
    for b in blocks:
        try:
            d = json.loads(b); types.append(d.get("@type"))
        except json.JSONDecodeError as e:
            err(slug, f"JSON-LD không hợp lệ: {e}"); continue
        if d.get("@type") in ("NewsArticle", "Article", "BlogPosting"):
            for k in ("headline", "datePublished", "dateModified", "image", "author", "publisher", "mainEntityOfPage"):
                if k not in d: err(slug, f"JSON-LD thiếu {k}")
            if d.get("datePublished") != p["ngay_dang"]: err(slug, "datePublished khác ngay_dang trong bai-viet.json")
            if d.get("dateModified") != p.get("ngay_sua", p["ngay_dang"]): warn(slug, "dateModified khác ngay_sua trong bai-viet.json")
            if d.get("articleSection") != CATEGORIES[p["danh_muc"]]["ten"]: err(slug, "JSON-LD articleSection khác chuyên mục trong bai-viet.json")
        if d.get("@type") == "BreadcrumbList":
            items = d.get("itemListElement", [])
            if len(items) < 4 or f"/tin-tuc/{p['danh_muc']}/" not in json.dumps(items): err(slug, "BreadcrumbList thiếu cấp chuyên mục")
    if not any(x in types for x in ("NewsArticle", "Article", "BlogPosting")): err(slug, "thiếu JSON-LD NewsArticle")
    if "BreadcrumbList" not in types: err(slug, "thiếu JSON-LD BreadcrumbList")

    # Breadcrumb HTML + link chuyên mục
    if f'href="/tin-tuc/{p["danh_muc"]}/"' not in t: err(slug, "chưa có link tới trang chuyên mục trong bài")

    # Ảnh
    img = ROOT / p["anh"].lstrip("/")
    if not img.exists(): err(slug, f"ảnh {p['anh']} không tồn tại")
    elif img.stat().st_size > 400_000: warn(slug, f"ảnh {p['anh']} nặng {img.stat().st_size // 1000} KB (nên ≤ 300 KB)")
    for m in re.finditer(r"<img\b[^>]*>", t):
        tag = m.group(0)
        if 'alt=' not in tag: err(slug, f"img thiếu alt: {tag[:60]}")
        if 'width=' not in tag or 'height=' not in tag: warn(slug, f"img thiếu width/height: {tag[:60]}")
        src = attr(tag, r'src="(.*?)"')
        if src and not link_exists(src): err(slug, f"img src không tồn tại: {src}")

    # Link nội bộ
    hrefs = re.findall(r'href="([^"]+)"', t)
    internal = [h for h in hrefs if h.startswith("/") and not h.startswith("//")]
    for h in set(internal):
        if not link_exists(h): err(slug, f"link nội bộ hỏng: {h}")
    body_links = [h for h in re.findall(r'href="(/[^"]+)"', t.split("<article", 1)[-1].split("</article>", 1)[0])]
    if len(set(body_links)) < 2: warn(slug, "nội dung bài nên có ít nhất 2 link nội bộ")

    # Độ dài
    body = re.sub(r"<[^>]+>", " ", t.split("<article", 1)[-1].split("</article>", 1)[0])
    words = len(body.split())
    if words < 300: warn(slug, f"bài chỉ ~{words} chữ (nên ≥ 500)")

    # Có mặt trong listing + sitemap
    for name, text in listings.items():
        need = name in ("tin-tuc/index.html", f"tin-tuc/{p['danh_muc']}/index.html")
        has = f'href="/tin-tuc/{slug}/"' in text
        if need and not has: err(slug, f"chưa xuất hiện trong {name} (chạy tools/build-tin-tuc.py)")
        if not need and has and name != "sitemap.xml": err(slug, f"xuất hiện sai chuyên mục trong {name}")
    if f"<loc>{url}</loc>" not in listings["sitemap.xml"]: err(slug, "chưa có trong sitemap.xml (chạy tools/build-tin-tuc.py)")


def main():
    posts = build.load_registry()
    only = sys.argv[1] if len(sys.argv) > 1 else None
    if only:
        posts = [p for p in posts if p["slug"] == only]
        if not posts: sys.exit(f"Không thấy slug '{only}' trong bai-viet.json")
    listings = {"tin-tuc/index.html": (ROOT / "tin-tuc/index.html").read_text(encoding="utf-8"),
                "sitemap.xml": (ROOT / "sitemap.xml").read_text(encoding="utf-8")}
    for c in CATEGORIES:
        listings[f"tin-tuc/{c}/index.html"] = (ROOT / "tin-tuc" / c / "index.html").read_text(encoding="utf-8")
    # Thư mục bài viết có nhưng chưa đăng ký
    if not only:
        known = {p["slug"] for p in posts} | set(CATEGORIES)
        for d in (ROOT / "tin-tuc").iterdir():
            if d.is_dir() and d.name not in known:
                err(d.name, "có thư mục nhưng chưa đăng ký trong bai-viet.json")
    for p in posts:
        check_article(p, listings)

    print(f"Đã kiểm tra {len(posts)} bài.")
    for w in warns: print("  ⚠ " + w)
    for e in errors: print("  ✖ " + e)
    if errors:
        print(f"\n{len(errors)} LỖI – sửa trước khi commit."); sys.exit(1)
    print("✔ Không có lỗi." + (f" ({len(warns)} cảnh báo)" if warns else ""))


if __name__ == "__main__":
    main()
