#!/usr/bin/env python3
"""
Tạo bài viết mới trong /tin-tuc/ từ template tools/mau-bai-viet.html,
đăng ký vào tin-tuc/bai-viet.json rồi chạy build (danh mục + sitemap).

Cách dùng (tất cả tham số dạng --ten=gia-tri hoặc --ten "giá trị"):

  python3 tools/tao-bai-viet.py \
    --slug bao-lau-nen-thay-nhot-xe-may \
    --danh-muc kien-thuc \
    --tieu-de "Bao lâu nên thay nhớt xe máy Honda?" \
    --mo-ta "Chu kỳ thay nhớt theo từng dòng xe Honda và điều kiện đi phố tại TP.HCM. Bảng giá nhớt chính hãng tại HEAD Việt Thái Quân." \
    --anh /thay-nhot-xe-may.jpg \
    --alt "Kỹ thuật viên HEAD Việt Thái Quân thay nhớt xe Honda" \
    [--tieu-de-seo "Bao lâu nên thay nhớt xe máy? | HEAD Việt Thái Quân"] \
    [--sapo "1 câu mở đầu hiển thị dưới H1"] \
    [--noi-dung noi-dung.html]   (file HTML fragment: các <h2>, <p>, <ul>; nếu bỏ qua sẽ tạo khung TODO)
    [--ngay 2026-09-15]           (mặc định: hôm nay)
    [--topbar "Câu chạy ở thanh trên cùng"]
    [--chu-thich "Chú thích dưới ảnh"]
    [--cta-link /dich-vu/ --cta-text "Xem dịch vụ tại cửa hàng"]
    [--tieu-de-ngan "Thay nhớt xe máy"]  (đoạn cuối breadcrumb, mặc định = tiêu đề)

Sau khi chạy: mở tin-tuc/<slug>/index.html để hoàn thiện nội dung,
rồi chạy python3 tools/kiem-tra-seo.py trước khi commit.
"""
import argparse, datetime, html, json, subprocess, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from importlib import import_module
build = import_module("build-tin-tuc")

CATEGORIES = build.CATEGORIES
REGISTRY = build.REGISTRY
TEMPLATE = ROOT / "tools" / "mau-bai-viet.html"

CTA_MAC_DINH = {
    "tin-tuc-su-kien": ("/xe-may/", "Xem bảng giá xe Honda"),
    "kien-thuc": ("/dich-vu/", "Xem dịch vụ tại cửa hàng"),
    "cong-dong": ("/dich-vu/", "Kiểm tra xe miễn phí tại cửa hàng"),
}

KHUNG_NOI_DUNG = """        <!-- TODO: viết nội dung. Mỗi ý lớn là 1 <h2>. Mỗi đoạn 2-4 câu. Bài từ 500 chữ trở lên.
             Có ít nhất 2 link nội bộ (ví dụ /xe-may/, /dich-vu/, /khuyen-mai/, /head-viet-thai-quan-1/). -->
        <h2>Ý chính thứ nhất (chứa từ khóa)</h2>
        <p>Đoạn mở đầu trả lời thẳng câu hỏi của người đọc trong 2-3 câu.</p>

        <h2>Ý chính thứ hai</h2>
        <p>Chi tiết, số liệu, ví dụ thực tế tại cửa hàng.</p>
        <ul>
          <li><strong>Gạch đầu dòng 1</strong> — giải thích ngắn.</li>
          <li><strong>Gạch đầu dòng 2</strong> — giải thích ngắn.</li>
        </ul>

        <h2>Áp dụng tại HEAD Việt Thái Quân</h2>
        <p>Liên hệ nội dung với dịch vụ / xe đang bán, kèm link nội bộ: <a href="/dich-vu/">dịch vụ tại cửa hàng</a>, <a href="/xe-may/">bảng giá xe</a>.</p>"""


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--slug", required=True)
    ap.add_argument("--danh-muc", required=True, choices=list(CATEGORIES))
    ap.add_argument("--tieu-de", required=True)
    ap.add_argument("--mo-ta", required=True)
    ap.add_argument("--anh", required=True, help="đường dẫn ảnh, bắt đầu bằng /, ví dụ /ten-anh.jpg")
    ap.add_argument("--alt", required=True)
    ap.add_argument("--tieu-de-seo")
    ap.add_argument("--tieu-de-ngan")
    ap.add_argument("--sapo")
    ap.add_argument("--noi-dung", help="file HTML fragment")
    ap.add_argument("--ngay", default=datetime.date.today().isoformat())
    ap.add_argument("--topbar", default="Đại lý Honda ủy nhiệm (HEAD) – phục vụ trên 20 năm")
    ap.add_argument("--chu-thich")
    ap.add_argument("--cta-link")
    ap.add_argument("--cta-text")
    a = ap.parse_args()

    dest = ROOT / "tin-tuc" / a.slug / "index.html"
    if dest.exists():
        sys.exit(f"LỖI: {dest.relative_to(ROOT)} đã tồn tại. Chọn slug khác hoặc xóa bài cũ.")
    if not a.anh.startswith("/"):
        sys.exit("LỖI: --anh phải bắt đầu bằng / (ảnh đặt ở thư mục gốc, ví dụ /ten-anh.jpg)")
    if not (ROOT / a.anh.lstrip("/")).exists():
        print(f"CẢNH BÁO: chưa có file ảnh {a.anh} – nhớ thêm ảnh trước khi commit.")

    cat_ten = CATEGORIES[a.danh_muc]["ten"]
    tieu_de_seo = a.tieu_de_seo or (a.tieu_de if len(a.tieu_de) > 45 else f"{a.tieu_de} | HEAD Việt Thái Quân")
    cta_link, cta_text = CTA_MAC_DINH[a.danh_muc]
    noi_dung = Path(a.noi_dung).read_text(encoding="utf-8").rstrip() if a.noi_dung else KHUNG_NOI_DUNG

    def j(s):  # escape cho JSON-LD
        return json.dumps(s, ensure_ascii=False)[1:-1]

    values = {
        "SLUG": a.slug,
        "DANH_MUC": a.danh_muc,
        "DANH_MUC_TEN": cat_ten,
        "DANH_MUC_TEN_HTML": html.escape(cat_ten),
        "DANH_MUC_TEN_JSON": j(cat_ten),
        "TIEU_DE": html.escape(a.tieu_de, quote=False),
        "TIEU_DE_JSON": j(a.tieu_de),
        "TIEU_DE_SEO": html.escape(tieu_de_seo, quote=False),
        "TIEU_DE_NGAN": html.escape(a.tieu_de_ngan or a.tieu_de, quote=False),
        "MO_TA": html.escape(a.mo_ta),
        "MO_TA_JSON": j(a.mo_ta),
        "SAPO": html.escape(a.sapo or a.mo_ta, quote=False),
        "ANH": a.anh,
        "ALT": html.escape(a.alt),
        "CHU_THICH": html.escape(a.chu_thich or a.alt, quote=False),
        "NGAY_ISO": a.ngay,
        "NGAY_VN": build.vn_date(a.ngay),
        "TOPBAR": html.escape(a.topbar, quote=False),
        "CTA_LINK": a.cta_link or cta_link,
        "CTA_TEXT": html.escape(a.cta_text or cta_text, quote=False),
        "NOI_DUNG": noi_dung,
    }
    out = TEMPLATE.read_text(encoding="utf-8")
    for k, v in values.items():
        out = out.replace("{{" + k + "}}", v)
    if "{{" in out:
        sys.exit("LỖI: template còn placeholder chưa thay: " + out[out.index("{{"):out.index("}}") + 2])
    dest.parent.mkdir(parents=True)
    dest.write_text(out, encoding="utf-8")
    print(f"  ✔ tạo {dest.relative_to(ROOT)}")

    posts = json.loads(REGISTRY.read_text(encoding="utf-8"))
    posts.append({
        "slug": a.slug, "tieu_de": a.tieu_de, "danh_muc": a.danh_muc, "mo_ta": a.mo_ta,
        "ngay_dang": a.ngay, "ngay_sua": a.ngay, "anh": a.anh, "alt": a.alt,
    })
    REGISTRY.write_text(json.dumps(posts, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"  ✔ đăng ký vào {REGISTRY.relative_to(ROOT)}")

    subprocess.run([sys.executable, str(ROOT / "tools" / "build-tin-tuc.py")], check=True)
    steps = []
    if not a.noi_dung:
        steps.append(f"Viết nội dung trong tin-tuc/{a.slug}/index.html (phần TODO).")
    steps += ["Kiểm tra: python3 tools/kiem-tra-seo.py", "Commit & push lên main để Vercel deploy."]
    print("\nTiếp theo:")
    for i, s in enumerate(steps, 1):
        print(f"  {i}. {s}")


if __name__ == "__main__":
    main()
