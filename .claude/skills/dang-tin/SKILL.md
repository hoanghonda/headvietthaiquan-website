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

## Bước 5 – Commit, PR, merge

Commit tất cả file thay đổi (bài mới, `bai-viet.json`, các trang danh mục, `sitemap.xml`, ảnh) với message dạng `Tin tuc: <tiêu đề ngắn không dấu>`. Push lên nhánh được chỉ định, tạo pull request vào `main`. Merge khi người dùng đồng ý (hoặc đã cho phép từ trước). Vercel deploy `main` trong khoảng 1 phút.

Ảnh: nếu người dùng dán ảnh vào chat, ảnh KHÔNG thành file trên máy chủ. Hướng dẫn họ tải lên GitHub (Add file → Upload files, tên file không dấu) hoặc Google Drive, rồi lấy về. File .jpg tải lên có thể là PNG thật: kiểm tra bằng `file`, chuyển sang JPEG bằng Pillow (`pip install pillow`), nén ≤ 300 KB, ảnh chính khung 3:4 1080×1440.

## Bước 6 – Google Search Console (không được bỏ qua)

Sau khi merge và site đã cập nhật, tự thao tác qua tool `mcp__adspirer__google_search_console`:

1. Gọi `action: "list_tools"` để lấy tên action chính xác. Nếu tool trả lời chưa kết nối, nói rõ với người dùng: cần vào Adspirer → Settings → Connections → Google Search Console để cấp quyền một lần, rồi dừng bước này và ghi vào báo cáo là còn chờ.
2. Xác nhận URL bài trả về 200 (nếu mạng phiên chặn headvietthaiquan.vn, dựa vào trạng thái deploy của Vercel trên commit merge).
3. Gọi `google_search_console-submit-url-for-indexing` với `https://headvietthaiquan.vn/tin-tuc/<slug>/`, sau đó với trang chuyên mục `https://headvietthaiquan.vn/tin-tuc/<danh-muc>/`. Chỉ gửi đúng các URL vừa thay đổi.
4. Ghi kết quả vào báo cáo cuối: URL đã gửi, thời điểm, và hẹn kiểm tra hiệu suất sau 3–7 ngày bằng `google_search_console-retrieve-site-performance-data` (dimension `page`).

Báo cáo cuối luôn có: URL bài, chuyên mục, trạng thái deploy, trạng thái Search Console.

## Sửa bài đã đăng

Sửa HTML, cập nhật `dateModified` trong JSON-LD và `ngay_sua` trong `bai-viet.json`, chạy `python3 tools/build-tin-tuc.py` rồi `python3 tools/kiem-tra-seo.py`. Không đổi slug. Sau khi deploy, gửi lại URL bài qua Search Console (Bước 6).
