---
name: dang-tin
description: Đăng bài tin tức mới chuẩn SEO lên headvietthaiquan.vn (mục /tin-tuc/). Dùng khi người dùng muốn đăng tin, viết bài, thêm bài viết, đăng sự kiện, đăng kiến thức, hoặc gõ /dang-tin.
---

# Đăng tin tức chuẩn SEO

Quy trình đầy đủ ở `docs/QUY-TRINH-DANG-TIN.md`. Làm đúng thứ tự sau, không bỏ bước.

## Bước 1 – Thu thập thông tin

Từ nội dung người dùng đưa, xác định:

- **Chuyên mục** (`tin-tuc-su-kien` | `kien-thuc` | `cong-dong`) – tự chọn theo bảng trong docs, nêu rõ lựa chọn.
- **Từ khóa chính** – 1 cụm người dùng sẽ tìm trên Google.
- **Slug** – không dấu, chữ thường, gạch ngang, chứa từ khóa, không trùng thư mục có sẵn trong `tin-tuc/`.
- **Ảnh** – nếu người dùng chưa cung cấp, hỏi tên file ảnh; nếu không có, chọn ảnh có sẵn phù hợp ở thư mục gốc và nói rõ. Ảnh phải tồn tại trước khi commit.
- **Ngày đăng** – mặc định hôm nay.

Chỉ hỏi lại khi thiếu thông tin không thể suy ra (ảnh, số liệu giá, ngày sự kiện).

## Bước 2 – Viết nội dung

Viết file HTML fragment (chỉ phần thân: `<h2>`, `<p>`, `<ul>`, `<a>`), lưu trong scratchpad, theo chuẩn:

- Tiếng Việt có dấu, giọng cửa hàng nói với khách (xem 2 bài mẫu trong `tin-tuc/`).
- ≥ 500 chữ (tin sự kiện ngắn: ≥ 300), ≥ 2 `<h2>`, đoạn đầu trả lời thẳng câu hỏi/từ khóa.
- ≥ 2 link nội bộ trong thân bài (`/xe-may/`, `/dich-vu/`, `/khuyen-mai/`, `/head-viet-thai-quan-1/`, `/head-viet-thai-quan-2/`, trang xe cụ thể).
- Nhắc khu vực thật: Đông Hòa, Dĩ An, Làng Đại Học, Bình Trưng, Thủ Đức, Cát Lái.
- Không bịa số liệu; giá xe ghi "tham khảo", thông số lấy từ nội dung người dùng đưa.
- Không copy nguyên văn nguồn ngoài. Có nguồn thì thêm link `rel="noopener"` và cân nhắc `citation` trong JSON-LD.

Thẻ title 30–65 ký tự, meta description 80–160 ký tự, đều chứa từ khóa và địa điểm.

## Bước 3 – Tạo bài

```bash
python3 tools/tao-bai-viet.py --slug ... --danh-muc ... --tieu-de "..." --mo-ta "..." --anh /... --alt "..." --noi-dung <file>.html [--sapo "..."] [--ngay YYYY-MM-DD]
```

Script tạo `tin-tuc/<slug>/index.html`, cập nhật `tin-tuc/bai-viet.json`, sinh lại trang danh mục và `sitemap.xml`. Không sửa tay phần giữa các marker `BAI-VIET`/`DANH-MUC`.

Nếu bài cần khối khác template (nhiều ảnh, video, nút nguồn) thì sửa trực tiếp `tin-tuc/<slug>/index.html` sau khi tạo, giữ nguyên phần `<head>`.

## Bước 4 – Kiểm tra

```bash
python3 tools/kiem-tra-seo.py <slug>
```

Sửa cho đến khi không còn dòng ✖. Xử lý cảnh báo ⚠ nếu hợp lý. Đọc lại bài một lượt để chắc không còn TODO/placeholder.

## Bước 5 – Commit

Commit tất cả file thay đổi (bài mới, `bai-viet.json`, các trang danh mục, `sitemap.xml`, ảnh) với message dạng `Tin tuc: <tiêu đề ngắn không dấu>`. Push lên nhánh được chỉ định. Trong báo cáo cuối, ghi URL bài (`https://headvietthaiquan.vn/tin-tuc/<slug>/`), chuyên mục, và nhắc người dùng yêu cầu lập chỉ mục trong Google Search Console sau khi Vercel deploy.

## Sửa bài đã đăng

Sửa HTML, cập nhật `dateModified` trong JSON-LD và `ngay_sua` trong `bai-viet.json`, chạy `python3 tools/build-tin-tuc.py` rồi `python3 tools/kiem-tra-seo.py`. Không đổi slug.
