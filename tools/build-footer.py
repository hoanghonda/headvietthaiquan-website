#!/usr/bin/env python3
"""
Chèn footer chung (tools/footer.html) vào mọi trang tiếng Việt và template bài viết.

Cách dùng:  python3 tools/build-footer.py
Sửa footer: chỉ sửa tools/footer.html (và tools/footer-en.html cho bản tiếng Anh),
rồi chạy script này, sau đó chạy python3 tools/build-en.py để sinh lại trang /en/.
Trang /en/ không xử lý ở đây: build-en.py thay footer tiếng Việt bằng footer-en.html.
"""
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
FOOTER = (ROOT / "tools" / "footer.html").read_text(encoding="utf-8").rstrip("\n")
PATTERN = re.compile(r'<footer class="site">.*?</footer>', re.S)


def pages():
    for p in sorted(ROOT.rglob("*.html")):
        rel = p.relative_to(ROOT)
        if rel.parts[0] in (".git", "en", "node_modules"):
            continue
        if rel.parts[0] == "tools" and rel.name != "mau-bai-viet.html":
            continue
        yield p


def main():
    changed = 0
    for p in pages():
        s = p.read_text(encoding="utf-8")
        if not PATTERN.search(s):
            continue
        new = PATTERN.sub(lambda m: FOOTER, s, count=1)
        if new != s:
            p.write_text(new, encoding="utf-8")
            changed += 1
            print(f"✔ {p.relative_to(ROOT)}")
    print(f"Đã cập nhật footer cho {changed} trang.")


if __name__ == "__main__":
    main()
