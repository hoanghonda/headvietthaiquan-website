# Quy trình đăng tin tức chuẩn SEO – headvietthaiquan.vn

Áp dụng cho mọi bài mới trong mục **Tin tức**. Cấu trúc chuyên mục tham khảo cách chia của dat.bike
(`Tin tức` → `Tin tức & Sự kiện` / `Kiến thức` / `Cộng đồng`).

## 1. Cấu trúc chuyên mục

| Chuyên mục | Slug | URL | Dùng cho |
|---|---|---|---|
| Tin tức & Sự kiện | `tin-tuc-su-kien` | `/tin-tuc/tin-tuc-su-kien/` | Xe mới ra mắt, sự kiện tại cửa hàng, thông báo |
| Kiến thức | `kien-thuc` | `/tin-tuc/kien-thuc/` | Bảo dưỡng, mua xe trả góp, so sánh xe, mẹo sử dụng |
| Cộng đồng | `cong-dong` | `/tin-tuc/cong-dong/` | An toàn giao thông, tặng mũ bảo hiểm, hoạt động địa phương |

- Trang tổng: `/tin-tuc/` (tất cả bài, thanh chuyên mục ở trên).
- Bài viết: `/tin-tuc/<slug>/` (phẳng, không lồng theo chuyên mục – đổi chuyên mục không làm đổi URL).
- Khuyến mãi vẫn ở trang riêng `/khuyen-mai/`, được link từ thanh chuyên mục.
- Nguồn dữ liệu duy nhất: `tin-tuc/bai-viet.json`. Danh sách bài trên các trang và `sitemap.xml` được sinh tự động từ file này.

## 2. Chuẩn bị trước khi viết (5 phút)

1. **Từ khóa chính**: 1 cụm người dùng sẽ gõ Google (ví dụ: `thay nhớt xe máy bao lâu`, `vario 125 2027 giá`). Từ khóa phải nằm trong tiêu đề, H1, mô tả, đoạn mở đầu và ít nhất 1 H2.
2. **Slug**: không dấu, chữ thường, gạch ngang, 3–6 từ, chứa từ khóa. Ví dụ `bao-lau-nen-thay-nhot-xe-may`.
3. **Ảnh đại diện**: 1 ảnh JPG tỷ lệ 3:4 (1080×1440), ≤ 300 KB, đặt ở thư mục gốc, tên không dấu (ví dụ `thay-nhot-xe-may.jpg`). Ảnh này dùng cho cả `og:image` (Facebook/Zalo) và JSON-LD.
4. **Chọn chuyên mục** theo bảng trên.

## 3. Tạo bài

```bash
python3 tools/tao-bai-viet.py \
  --slug bao-lau-nen-thay-nhot-xe-may \
  --danh-muc kien-thuc \
  --tieu-de "Bao lâu nên thay nhớt xe máy Honda?" \
  --mo-ta "Chu kỳ thay nhớt theo từng dòng xe Honda và điều kiện đi phố tại TP.HCM. Bảng giá nhớt chính hãng tại HEAD Việt Thái Quân." \
  --anh /thay-nhot-xe-may.jpg \
  --alt "Kỹ thuật viên HEAD Việt Thái Quân thay nhớt xe Honda" \
  --noi-dung noi-dung.html        # tùy chọn: file HTML phần thân bài; bỏ qua thì tạo khung TODO
```

Script sẽ: tạo `tin-tuc/<slug>/index.html` từ `tools/mau-bai-viet.html` (đủ title, description, canonical, Open Graph,
JSON-LD `NewsArticle` + `BreadcrumbList`, breadcrumb 4 cấp, link chuyên mục), thêm bài vào `bai-viet.json`,
rồi sinh lại `/tin-tuc/`, trang chuyên mục và `sitemap.xml`.

Tham số tùy chọn: `--tieu-de-seo` (thẻ title riêng), `--sapo` (câu dẫn dưới H1), `--ngay YYYY-MM-DD`,
`--topbar`, `--chu-thich`, `--cta-link`, `--cta-text`, `--tieu-de-ngan` (đoạn cuối breadcrumb).

## 4. Chuẩn nội dung

| Hạng mục | Yêu cầu |
|---|---|
| Thẻ `<title>` | 30–65 ký tự, chứa từ khóa, thường kết thúc `\| HEAD Việt Thái Quân` |
| Meta description | 80–160 ký tự, có từ khóa + lợi ích + địa điểm (TP.HCM / tên chi nhánh) |
| H1 | Đúng 1, trùng hoặc gần trùng tiêu đề |
| H2 | ≥ 2, mỗi H2 là một ý người đọc muốn biết; ít nhất 1 H2 chứa từ khóa |
| Độ dài | ≥ 500 chữ (tin sự kiện ngắn có thể 300–400) |
| Link nội bộ | ≥ 2 trong thân bài: `/xe-may/`, `/xe-may/vario125/`, `/dich-vu/`, `/khuyen-mai/`, `/head-viet-thai-quan-1/`, `/head-viet-thai-quan-2/` |
| Địa phương | Nhắc tên khu vực khách hàng thật: Đông Hòa, Dĩ An, Làng Đại Học, Bình Trưng, Thủ Đức, Cát Lái… |
| Ảnh | `alt` mô tả có ý nghĩa, có `width`/`height` |
| Nguồn | Tin dẫn từ nơi khác: thêm `citation` vào JSON-LD và link nguồn `rel="noopener"` |
| CTA | Cuối bài 1 nút đỏ: báo giá / dịch vụ / liên hệ chi nhánh |
| Không | Không copy nguyên văn từ web khác, không nhồi từ khóa, không để `TODO` |

## 5. Kiểm tra và đăng

```bash
python3 tools/kiem-tra-seo.py            # toàn bộ bài
python3 tools/kiem-tra-seo.py <slug>     # 1 bài
```

Phải **không còn dòng ✖**. Cảnh báo ⚠ nên xử lý nhưng không bắt buộc. Sau đó:

```bash
git add -A
git commit -m "Tin tuc: <tiêu đề ngắn>"
git push origin main            # Vercel tự deploy lên headvietthaiquan.vn
```

Sau khi deploy: vào Google Search Console → *Kiểm tra URL* → *Yêu cầu lập chỉ mục* cho URL bài mới
(sitemap đã tự cập nhật). Chia sẻ link lên Fanpage/Zalo để kiểm tra og:image hiển thị đúng.

## 6. Sửa bài đã đăng

1. Sửa HTML trong `tin-tuc/<slug>/index.html`.
2. Cập nhật `dateModified` trong JSON-LD và `ngay_sua` trong `bai-viet.json` (cùng giá trị).
3. Nếu đổi tiêu đề / mô tả / chuyên mục: sửa cả trong `bai-viet.json`.
4. Chạy `python3 tools/build-tin-tuc.py` rồi `python3 tools/kiem-tra-seo.py`.

**Không đổi slug** của bài đã đăng (mất thứ hạng Google). Nếu bắt buộc, giữ thư mục cũ với `<meta http-equiv="refresh">` sang URL mới.

## 7. Thêm chuyên mục mới

1. Thêm mục vào `CATEGORIES` trong `tools/build-tin-tuc.py`.
2. Copy một trang chuyên mục có sẵn (ví dụ `tin-tuc/kien-thuc/index.html`) thành `tin-tuc/<slug-moi>/index.html`, sửa title, description, canonical, hero và JSON-LD.
3. Chạy build – thanh chuyên mục trên mọi trang tự cập nhật.

## 8. Dùng với Claude Code

Gõ `/dang-tin` kèm nội dung thô (tiêu đề, ý chính, ảnh, chuyên mục). Claude sẽ chạy đúng quy trình
trên: hỏi thông tin còn thiếu, viết bài theo chuẩn mục 4, tạo file, kiểm tra và commit.
