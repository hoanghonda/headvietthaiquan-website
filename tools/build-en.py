#!/usr/bin/env python3
"""
Sinh các trang tiếng Anh /en/ từ trang tiếng Việt tương ứng bằng bảng dịch.

Cách dùng:  python3 tools/build-en.py
Chạy lại mỗi khi sửa nội dung trang chủ hoặc trang chi nhánh. Script sẽ báo lỗi nếu
còn sót chữ tiếng Việt chưa dịch, hoặc nếu một chuỗi trong bảng dịch không còn tồn tại
(tức trang tiếng Việt đã đổi nội dung -> cần cập nhật bảng dịch bên dưới).

Các trang chưa có bản tiếng Anh riêng (xe máy, dịch vụ, khuyến mãi, tin tức) được link
qua Google Translate (headvietthaiquan-vn.translate.goog).
"""
import re, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DOMAIN = "https://headvietthaiquan.vn"
GT = "https://headvietthaiquan-vn.translate.goog{path}?_x_tr_sl=vi&amp;_x_tr_tl=en&amp;_x_tr_hl=en&amp;_x_tr_pto=wapp"

# Trang tiếng Việt -> trang tiếng Anh
PAGES = {
    "index.html": "en/index.html",
    "head-viet-thai-quan-1/index.html": "en/head-viet-thai-quan-1/index.html",
    "head-viet-thai-quan-2/index.html": "en/head-viet-thai-quan-2/index.html",
}
EN_PATH = {"index.html": "/en/", "head-viet-thai-quan-1/index.html": "/en/head-viet-thai-quan-1/",
           "head-viet-thai-quan-2/index.html": "/en/head-viet-thai-quan-2/"}
VI_PATH = {"index.html": "/", "head-viet-thai-quan-1/index.html": "/head-viet-thai-quan-1/",
           "head-viet-thai-quan-2/index.html": "/head-viet-thai-quan-2/"}

GLOBE = ('<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20Zm7.9 9h-3.1a15.6 '
         '15.6 0 0 0-1.4-6A8 8 0 0 1 19.9 11ZM12 4c1.1 1.4 2.2 4 2.5 7h-5C9.8 8 10.9 5.4 12 4ZM4.1 13h3.1c.1 2.2.6 4.3 1.4 '
         '6A8 8 0 0 1 4.1 13Zm3.1-2H4.1a8 8 0 0 1 4.5-6c-.8 1.7-1.3 3.8-1.4 6ZM12 20c-1.1-1.4-2.2-4-2.5-7h5c-.3 3-1.4 '
         '5.6-2.5 7Zm3.4-1a15.6 15.6 0 0 0 1.4-6h3.1a8 8 0 0 1-4.5 6Z"/></svg>')

# ---- Bảng dịch dùng chung cho mọi trang (thứ tự có ý nghĩa: chuỗi dài đứng trước) ----
COMMON = [
    ('<html lang="vi">', '<html lang="en">'),
    # Header / logo
    ('<a class="logo" href="/"><img src="/logo-vtq-mark.png" alt="Logo Việt Thái Quân" width="253" height="96"><span class="logo-tx"><strong>HEAD Việt Thái Quân</strong><small>Cửa hàng Honda ủy nhiệm</small></span></a>',
     '<a class="logo" href="/en/"><img src="/logo-vtq-mark.png" alt="Viet Thai Quan logo" width="253" height="96"><span class="logo-tx"><strong>HEAD Viet Thai Quan</strong><small>Honda authorised dealer</small></span></a>'),
    ('<a href="/" class="active">Trang chủ</a>', '<a href="/en/" class="active">Home</a>'),
    ('<a href="/">Trang chủ</a>', '<a href="/en/">Home</a>'),
    ('<a href="/xe-may/">Xe máy</a>', '<a href="%s">Motorcycles</a>' % GT.format(path="/xe-may/")),
    ('<a href="/dich-vu/">Dịch vụ</a>', '<a href="%s">Services</a>' % GT.format(path="/dich-vu/")),
    ('<a href="/khuyen-mai/">Khuyến mãi</a>', '<a href="%s">Promotions</a>' % GT.format(path="/khuyen-mai/")),
    ('<a href="/head-viet-thai-quan-1/" class="active">Chi nhánh 1</a>', '<a href="/en/head-viet-thai-quan-1/" class="active">Branch 1</a>'),
    ('<a href="/head-viet-thai-quan-1/">Chi nhánh 1</a>', '<a href="/en/head-viet-thai-quan-1/">Branch 1</a>'),
    ('<a href="/head-viet-thai-quan-2/" class="active">Chi nhánh 2</a>', '<a href="/en/head-viet-thai-quan-2/" class="active">Branch 2</a>'),
    ('<a href="/head-viet-thai-quan-2/">Chi nhánh 2</a>', '<a href="/en/head-viet-thai-quan-2/">Branch 2</a>'),
    ('<a href="/tin-tuc/">Tin tức</a>', '<a href="%s">News</a>' % GT.format(path="/tin-tuc/")),
    # Footer
    ('<h4>Liên kết</h4>', '<h4>Links</h4>'),
    ('<a href="/xe-may/">Bảng giá xe</a>', '<a href="%s">Models &amp; prices</a>' % GT.format(path="/xe-may/")),
    ('<a href="/dich-vu/">Dịch vụ</a>', '<a href="%s">Services</a>' % GT.format(path="/dich-vu/")),
    ('<a href="/khuyen-mai/">Khuyến mãi</a>', '<a href="%s">Promotions</a>' % GT.format(path="/khuyen-mai/")),
    ('<a href="/tin-tuc/">Tin tức</a>', '<a href="%s">News</a>' % GT.format(path="/tin-tuc/")),
    ('© 2026 <strong>Công ty TNHH Việt Thái Quân</strong> · Mã số doanh nghiệp (MST): <strong>0305778228</strong> do Phòng Đăng ký kinh doanh – Sở Tài chính TP.HCM cấp, đăng ký lần đầu ngày 06/06/2008.<br>Trụ sở chính: 111 Nguyễn Duy Trinh, phường Bình Trưng, TP.HCM · Đại lý Honda ủy nhiệm (HEAD).',
     '© 2026 <strong>Viet Thai Quan Co., Ltd</strong> · Business registration no. <strong>0305778228</strong> issued by the Business Registration Office – Ho Chi Minh City Department of Finance, first registered 06/06/2008.<br>Head office: 111 Nguyen Duy Trinh, Binh Trung Ward, Ho Chi Minh City · Authorised Honda dealer (HEAD).'),
    ('<a class="btn btn-red" href="/xe-may/">Xem bảng giá xe</a>', '<a class="btn btn-red" href="%s">See models &amp; prices</a>' % GT.format(path="/xe-may/")),
    # Callbar
    ('☎ Gọi ngay', '☎ Call now'),
    ('☎ Gọi chi nhánh 2', '☎ Call branch 2'),
    ('>Chat Zalo</a>', '>Chat on Zalo</a>'),
    # Google review card
    ('<span class="rv-stars" aria-label="5 sao">★★★★★</span><span>Google Review 5 sao</span>', '<span class="rv-stars" aria-label="5 stars">★★★★★</span><span>5-star Google review</span>'),
    # Địa chỉ
    ('<li><strong>Địa chỉ</strong> 53 QL1K, phường Đông Hòa, TP.HCM (khu vực Làng Đại Học, Dĩ An, Bình Dương cũ)</li>',
     '<li><strong>Address</strong> 53 National Route 1K (QL1K), Dong Hoa Ward, Ho Chi Minh City (University Village area, Di An, formerly Binh Duong)</li>'),
    ('<li><strong>Địa chỉ</strong> 111 Nguyễn Duy Trinh, phường Bình Trưng, TP.HCM (Quận 2 cũ, TP. Thủ Đức)</li>',
     '<li><strong>Address</strong> 111 Nguyen Duy Trinh, Binh Trung Ward, Ho Chi Minh City (formerly District 2, Thu Duc City)</li>'),
    ('53 QL1K, phường Đông Hòa, TP.HCM', '53 National Route 1K (QL1K), Dong Hoa Ward, Ho Chi Minh City'),
    ('111 Nguyễn Duy Trinh, phường Bình Trưng, TP.HCM', '111 Nguyen Duy Trinh, Binh Trung Ward, Ho Chi Minh City'),
    ('<h4>Chi nhánh 1 – phường Đông Hòa</h4>', '<h4>Branch 1 – Dong Hoa Ward</h4>'),
    ('<h4>Chi nhánh 2 – phường Bình Trưng</h4>', '<h4>Branch 2 – Binh Trung Ward</h4>'),
    ('<h4>Chi nhánh khác</h4>', '<h4>Other branch</h4>'),
    ('<a href="/head-viet-thai-quan-2/">HEAD Việt Thái Quân 2 – 111 Nguyễn Duy Trinh, phường Bình Trưng</a>', '<a href="/en/head-viet-thai-quan-2/">HEAD Viet Thai Quan 2 – 111 Nguyen Duy Trinh, Binh Trung Ward</a>'),
    ('<a href="/head-viet-thai-quan-1/">HEAD Việt Thái Quân 1 – 53 QL1K, phường Đông Hòa</a>', '<a href="/en/head-viet-thai-quan-1/">HEAD Viet Thai Quan 1 – 53 QL1K, Dong Hoa Ward</a>'),
    # Trang chi nhánh: khối thông tin & dịch vụ
    ('<h2 class="sec">Thông tin cửa hàng</h2>', '<h2 class="sec">Store information</h2>'),
    ('<li><strong>Điện thoại</strong>', '<li><strong>Phone</strong>'),
    ('<li><strong>Zalo</strong> <a href="https://zalo.me/1375768392800157726">HEAD Honda Việt Thái Quân QL 1K Đông Hòa</a></li>',
     '<li><strong>Zalo</strong> <a href="https://zalo.me/1375768392800157726">HEAD Honda Viet Thai Quan QL1K Dong Hoa</a></li>'),
    ('<li><strong>Zalo</strong> <a href="https://zalo.me/596730140125275087">HEAD Việt Thái Quân 111 Nguyễn Duy Trinh</a></li>',
     '<li><strong>Zalo</strong> <a href="https://zalo.me/596730140125275087">HEAD Viet Thai Quan 111 Nguyen Duy Trinh</a></li>'),
    ('<li><strong>Đánh giá</strong> <span class="stars">4.9★</span> (1.648 đánh giá Google)</li>', '<li><strong>Rating</strong> <span class="stars">4.9★</span> (1,648 Google reviews)</li>'),
    ('<li><strong>Đánh giá</strong> <span class="stars">4.7★</span> (1.955 đánh giá Google)</li>', '<li><strong>Rating</strong> <span class="stars">4.7★</span> (1,955 Google reviews)</li>'),
    ('<tr><th>Thứ 2 – Chủ nhật</th>', '<tr><th>Monday – Sunday</th>'),
    ('<iframe title="Bản đồ HEAD Việt Thái Quân 1" loading="lazy"', '<iframe title="Map of HEAD Viet Thai Quan 1" loading="lazy"'),
    ('<iframe title="Bản đồ HEAD Việt Thái Quân 2" loading="lazy"', '<iframe title="Map of HEAD Viet Thai Quan 2" loading="lazy"'),
    ('&output=embed"></iframe>', '&output=embed&hl=en"></iframe>'),
    ('<a class="btn btn-outline" href="https://zalo.me/1375768392800157726">💬 Chat Zalo</a>', '<a class="btn btn-outline" href="https://zalo.me/1375768392800157726">💬 Chat on Zalo</a>'),
    ('<a class="btn btn-outline" href="https://zalo.me/596730140125275087">💬 Chat Zalo</a>', '<a class="btn btn-outline" href="https://zalo.me/596730140125275087">💬 Chat on Zalo</a>'),
    ('>Chỉ đường Google Maps</a>', '>Directions on Google Maps</a>'),
    ('aria-label="Mạng xã hội chi nhánh 1"', 'aria-label="Branch 1 social media"'),
    ('aria-label="Mạng xã hội chi nhánh 2"', 'aria-label="Branch 2 social media"'),
    ('title="Facebook chi nhánh 1"', 'title="Branch 1 on Facebook"'),
    ('title="Facebook chi nhánh 2"', 'title="Branch 2 on Facebook"'),
    ('title="TikTok chi nhánh 1"', 'title="Branch 1 on TikTok"'),
    ('title="TikTok chi nhánh 2"', 'title="Branch 2 on TikTok"'),
    ('title="YouTube HEAD Việt Thái Quân"', 'title="HEAD Viet Thai Quan on YouTube"'),
    ('>Kênh YouTube HEAD Việt Thái Quân</a>', '>HEAD Viet Thai Quan YouTube channel</a>'),
    ('>HEAD Việt Thái Quân 1 trên Facebook</a>', '>HEAD Viet Thai Quan 1 on Facebook</a>'),
    ('>HEAD Việt Thái Quân 2 trên Facebook</a>', '>HEAD Viet Thai Quan 2 on Facebook</a>'),
    ('<div class="card"><h3>Bảo dưỡng &amp; sửa chữa</h3><p>Thay nhớt, bảo dưỡng định kỳ, sửa chữa với phụ tùng chính hãng ngay tại chỗ. Hỗ trợ cứu hộ tận nơi.</p></div>',
     '<div class="card"><h3>Servicing &amp; repairs</h3><p>Oil changes, scheduled maintenance and repairs with genuine parts, done on site. Roadside assistance available.</p></div>'),
    ('<div class="card"><h3>Bảo dưỡng &amp; sửa chữa</h3><p>Thay nhớt, bảo dưỡng định kỳ với phụ tùng chính hãng. Hỗ trợ cứu hộ tận nơi khi xe gặp sự cố.</p></div>',
     '<div class="card"><h3>Servicing &amp; repairs</h3><p>Oil changes and scheduled maintenance with genuine parts. Roadside assistance if your bike breaks down.</p></div>'),
    # JSON-LD chung
    ('"alternateName": "Xe Máy HEAD Việt Thái Quân 1"', '"alternateName": "Xe Máy HEAD Việt Thái Quân 1"'),
    ('"addressLocality": "Phường Đông Hòa"', '"addressLocality": "Dong Hoa Ward"'),
    ('"addressLocality": "Phường Bình Trưng"', '"addressLocality": "Binh Trung Ward"'),
    ('"addressRegion": "Thành phố Hồ Chí Minh"', '"addressRegion": "Ho Chi Minh City"'),
    ('"addressRegion": "TP.HCM"', '"addressRegion": "Ho Chi Minh City"'),
    ('    "name": "HEAD Việt Thái Quân",\n    "url": "https://headvietthaiquan.vn/"', '    "name": "HEAD Viet Thai Quan",\n    "url": "https://headvietthaiquan.vn/en/"'),
]

# ---- Bảng dịch riêng từng trang ----
PER_PAGE = {
"index.html": [
    ('<title>HEAD Việt Thái Quân – Đại lý xe máy Honda ủy nhiệm TP.HCM</title>', '<title>HEAD Viet Thai Quan – Authorised Honda Motorcycle Dealer in Ho Chi Minh City</title>'),
    ('<meta name="description" content="Đại lý Honda ủy nhiệm tại 53 QL1K, phường Đông Hòa và 111 Nguyễn Duy Trinh, phường Bình Trưng, TP.HCM. Mua xe trả góp, bảo dưỡng và phụ tùng chính hãng.">',
     '<meta name="description" content="Authorised Honda dealer (HEAD) at 53 National Route 1K, Dong Hoa Ward and 111 Nguyen Duy Trinh, Binh Trung Ward, Ho Chi Minh City. New Honda motorcycles, financing, servicing and genuine parts. English-speaking staff.">'),
    ('"name": "HEAD Việt Thái Quân",', '"name": "HEAD Viet Thai Quan",'),
    ('"url": "https://headvietthaiquan.vn/",\n  "email"', '"url": "https://headvietthaiquan.vn/en/",\n  "email"'),
    ('"description": "Hệ thống cửa hàng xe máy Honda ủy nhiệm (HEAD) Việt Thái Quân tại TP.HCM: chi nhánh 1 tại phường Đông Hòa (Dĩ An) và chi nhánh 2 tại phường Bình Trưng (Quận 2)."',
     '"description": "Viet Thai Quan authorised Honda motorcycle dealers (HEAD) in Ho Chi Minh City: branch 1 in Dong Hoa Ward (Di An) and branch 2 in Binh Trung Ward (District 2)."'),
    ('{"@type": "MotorcycleDealer", "name": "HEAD Việt Thái Quân 1", "url": "https://headvietthaiquan.vn/head-viet-thai-quan-1/"}', '{"@type": "MotorcycleDealer", "name": "HEAD Viet Thai Quan 1", "url": "https://headvietthaiquan.vn/en/head-viet-thai-quan-1/"}'),
    ('{"@type": "MotorcycleDealer", "name": "HEAD Việt Thái Quân 2", "url": "https://headvietthaiquan.vn/head-viet-thai-quan-2/"}', '{"@type": "MotorcycleDealer", "name": "HEAD Viet Thai Quan 2", "url": "https://headvietthaiquan.vn/en/head-viet-thai-quan-2/"}'),
    ('<span>Phục vụ bà con từ 2004</span>', '<span>Serving the community since 2004</span>'),
    ('<h2 class="sec">Vì sao chọn HEAD Việt Thái Quân?</h2>', '<h2 class="sec">Why choose HEAD Viet Thai Quan?</h2>'),
    ('<p class="sec-sub">Hàng nghìn khách hàng đã chọn và nhận xe tại cửa hàng — cảm ơn quý khách đã tin tưởng HEAD Việt Thái Quân.</p>',
     '<p class="sec-sub">Thousands of customers have chosen and collected their bikes at our stores — thank you for trusting HEAD Viet Thai Quan.</p>'),
    ('aria-label="Hình ảnh khách hàng nhận xe tại HEAD Việt Thái Quân"', 'aria-label="Customers collecting their new Honda at HEAD Viet Thai Quan"'),
    ('alt="Khách hàng nhận xe Honda SH tại HEAD Việt Thái Quân"', 'alt="Customer collecting a Honda SH at HEAD Viet Thai Quan"'),
    ('alt="Khách hàng nhận xe Honda ADV 350 tại HEAD Việt Thái Quân"', 'alt="Customer collecting a Honda ADV 350 at HEAD Viet Thai Quan"'),
    ('alt="Khách hàng nhận xe Honda LEAD tại HEAD Việt Thái Quân"', 'alt="Customer collecting a Honda LEAD at HEAD Viet Thai Quan"'),
    ('alt="Khách hàng nhận xe tay ga Honda tại HEAD Việt Thái Quân"', 'alt="Customer collecting a Honda scooter at HEAD Viet Thai Quan"'),
    ('alt="Khách hàng nhận xe máy điện Honda ICON e: tại HEAD Việt Thái Quân"', 'alt="Customer collecting a Honda ICON e: electric scooter at HEAD Viet Thai Quan"'),
    ('alt="Khách hàng nhận xe Honda Super Cub tại HEAD Việt Thái Quân"', 'alt="Customer collecting a Honda Super Cub at HEAD Viet Thai Quan"'),
    ('alt="Khách hàng nhận xe Honda Vision màu đỏ tại HEAD Việt Thái Quân"', 'alt="Customer collecting a red Honda Vision at HEAD Viet Thai Quan"'),
    ('alt="Khách hàng nhận xe Honda Air Blade tại HEAD Việt Thái Quân"', 'alt="Customer collecting a Honda Air Blade at HEAD Viet Thai Quan"'),
    ('alt="Khách hàng nhận xe Honda Vision màu xanh tại HEAD Việt Thái Quân"', 'alt="Customer collecting a blue Honda Vision at HEAD Viet Thai Quan"'),
    ('alt="Khách hàng nhận xe Honda Vario 125 màu trắng tại HEAD Việt Thái Quân"', 'alt="Customer collecting a white Honda Vario 125 at HEAD Viet Thai Quan"'),
    ('alt="Khách hàng nhận xe Honda CBR tại HEAD Việt Thái Quân"', 'alt="Customer collecting a Honda CBR at HEAD Viet Thai Quan"'),
    ('<h1>Mua xe máy Honda chính hãng tại phường Đông Hòa &amp; phường Bình Trưng, TP.HCM</h1>', '<h1>Genuine Honda motorcycles in Dong Hoa Ward &amp; Binh Trung Ward, Ho Chi Minh City</h1>'),
    ('<a class="rv-anh" href="/head-viet-thai-quan-1/"><img src="/cua-hang-1.jpg" alt="Mặt tiền HEAD Việt Thái Quân 1 – phường Đông Hòa"', '<a class="rv-anh" href="/en/head-viet-thai-quan-1/"><img src="/cua-hang-1.jpg" alt="HEAD Viet Thai Quan 1 storefront – Dong Hoa Ward"'),
    ('<a class="rv-anh" href="/head-viet-thai-quan-2/"><img src="/cua-hang-2.jpg" alt="Mặt tiền HEAD Việt Thái Quân 2 – phường Bình Trưng"', '<a class="rv-anh" href="/en/head-viet-thai-quan-2/"><img src="/cua-hang-2.jpg" alt="HEAD Viet Thai Quan 2 storefront – Binh Trung Ward"'),
    ('<span class="cn-phuong">Phường Đông Hòa · Làng Đại Học (Bình Dương cũ)</span>', '<span class="cn-phuong">Dong Hoa Ward · University Village (formerly Binh Duong)</span>'),
    ('<span class="cn-phuong">Phường Bình Trưng · Quận 2 cũ</span>', '<span class="cn-phuong">Binh Trung Ward · formerly District 2</span>'),
    ('<h2 class="rv-title"><a href="/head-viet-thai-quan-1/">HEAD Việt Thái Quân 1</a></h2>', '<h2 class="rv-title"><a href="/en/head-viet-thai-quan-1/">HEAD Viet Thai Quan 1</a></h2>'),
    ('<h2 class="rv-title"><a href="/head-viet-thai-quan-2/">HEAD Việt Thái Quân 2</a></h2>', '<h2 class="rv-title"><a href="/en/head-viet-thai-quan-2/">HEAD Viet Thai Quan 2</a></h2>'),
    ('<p>“Honda recommended có khác! Ai đã từng sử dụng dịch vụ nhiều nơi thì sẽ có cảm nhận y mình từ dịch vụ chăm sóc khác biệt hẳn các HEAD khác.”</p>',
     '<p>“A Honda-recommended dealer really is different! Anyone who has had their bike serviced at many places will feel, as I did, that the customer care here stands out from other HEAD dealers.”</p>'),
    ('<p class="rv-meta">Trung bình <b class="stars">4.9★</b> từ 1.648 đánh giá Google<a href="/head-viet-thai-quan-1/">Xem chi nhánh 1 →</a></p>',
     '<p class="rv-meta">Average <b class="stars">4.9★</b> from 1,648 Google reviews<a href="/en/head-viet-thai-quan-1/">View branch 1 →</a></p>'),
    ('<p class="rv-meta">Trung bình <b class="stars">4.7★</b> từ 1.955 đánh giá Google<a href="/head-viet-thai-quan-2/">Xem chi nhánh 2 →</a></p>',
     '<p class="rv-meta">Average <b class="stars">4.7★</b> from 1,955 Google reviews<a href="/en/head-viet-thai-quan-2/">View branch 2 →</a></p>'),
    ('<span class="badge">Khuyến mãi 01/09 – 31/10/2026</span>', '<span class="badge">Promotion 1 Sep – 31 Oct 2026</span>'),
    ('<h2 class="sec">Cùng Lên Ga – Quà Bao La</h2>', '<h2 class="sec">“Cùng Lên Ga – Quà Bao La” gift promotion</h2>'),
    ('<p>Mua Honda Vision, LEAD, Air Blade 125/160 nhận quà tặng 1 triệu đồng; mua Winner R nhận combo quà 3 triệu đồng hoặc gói trả góp lãi suất 0%; mua xe máy điện ICON e: được tặng ngay 2 triệu đồng tiền mặt.</p>',
     '<p>Buy a Honda Vision, LEAD or Air Blade 125/160 and receive a VND 1 million gift; buy a Winner R and get a VND 3 million gift bundle or 0% interest financing; buy the ICON e: electric scooter and receive VND 2 million cash back.</p>'),
    ('<a class="btn btn-red mt-2" href="/khuyen-mai/">Xem chi tiết chương trình khuyến mãi</a>', '<a class="btn btn-red mt-2" href="%s">See promotion details</a>' % GT.format(path="/khuyen-mai/")),
    ('aria-label="Video khuyến mãi Cùng Lên Ga – Quà Bao La"', 'aria-label="Cùng Lên Ga – Quà Bao La promotion video"'),
    ('<h2 class="sec">Xe bán chạy</h2>', '<h2 class="sec">Best sellers</h2>'),
    ('<p class="sec-sub">Đầy đủ các dòng xe tay ga, xe số, xe côn tay và xe điện Honda mới nhất. Giá lăn bánh và ưu đãi cập nhật tại cửa hàng.</p>',
     '<p class="sec-sub">The full Honda range: scooters, underbone (cub) models, manual-clutch bikes and electric scooters. On-the-road prices and offers are updated in store.</p>'),
    ('alt="Honda Vision tại HEAD Việt Thái Quân"', 'alt="Honda Vision at HEAD Viet Thai Quan"'),
    ('alt="Honda LEAD 125 tại HEAD Việt Thái Quân"', 'alt="Honda LEAD 125 at HEAD Viet Thai Quan"'),
    ('alt="Honda SH Mode tại HEAD Việt Thái Quân"', 'alt="Honda SH Mode at HEAD Viet Thai Quan"'),
    ('alt="Honda Vario 125 tại HEAD Việt Thái Quân"', 'alt="Honda Vario 125 at HEAD Viet Thai Quan"'),
    ('<span class="cat">Xe tay ga</span>', '<span class="cat">Scooter</span>'),
    ('<span class="price">Liên hệ</span>', '<span class="price">Contact us</span>'),
    ('<span class="price">Từ 43 triệu</span>', '<span class="price">From VND 43 million</span>'),
    ('<a class="product" href="/xe-may/vario125/">', '<a class="product" href="%s">' % GT.format(path="/xe-may/vario125/")),
    ('<div class="mt-3"><a class="btn btn-red" href="/xe-may/">Xem tất cả xe &amp; bảng giá</a></div>', '<div class="mt-3"><a class="btn btn-red" href="%s">See all models &amp; prices</a></div>' % GT.format(path="/xe-may/")),
    ('<h4>HEAD Việt Thái Quân</h4>\n        <p>Đại lý xe máy Honda ủy nhiệm tại TP.HCM.<br>', '<h4>HEAD Viet Thai Quan</h4>\n        <p>Authorised Honda motorcycle dealer in Ho Chi Minh City.<br>'),
],
"head-viet-thai-quan-1/index.html": [
    ('<title>HEAD Việt Thái Quân 1 – 53 QL1K, phường Đông Hòa</title>', '<title>HEAD Viet Thai Quan 1 – 53 National Route 1K, Dong Hoa Ward (Di An)</title>'),
    ('<meta name="description" content="Cửa hàng xe máy Honda ủy nhiệm tại 53 QL1K, phường Đông Hòa, TP.HCM (Dĩ An cũ). 4.9★ từ 1.648 đánh giá Google. Mở cửa 07:30–18:00 hằng ngày.">',
     '<meta name="description" content="Authorised Honda motorcycle dealer at 53 National Route 1K, Dong Hoa Ward, Ho Chi Minh City (formerly Di An). Rated 4.9★ from 1,648 Google reviews. Open daily 07:30–18:00.">'),
    ('"name": "HEAD Việt Thái Quân 1",', '"name": "HEAD Viet Thai Quan 1",'),
    ('"url": "https://headvietthaiquan.vn/head-viet-thai-quan-1/",', '"url": "https://headvietthaiquan.vn/en/head-viet-thai-quan-1/",'),
    ('<span>HEAD Việt Thái Quân 1 · phường Đông Hòa</span>', '<span>HEAD Viet Thai Quan 1 · Dong Hoa Ward</span>'),
    ('<h1>HEAD Việt Thái Quân 1 – Cửa hàng xe máy Honda tại phường Đông Hòa, Dĩ An</h1>', '<h1>HEAD Viet Thai Quan 1 – Honda motorcycle dealer in Dong Hoa Ward, Di An</h1>'),
    ('<p>Đại lý Honda ủy nhiệm sớm nhất trên Quốc lộ 1K, phục vụ bà con khu vực Làng Đại Học, phường Đông Hòa, Dĩ An, Thủ Đức hơn 20 năm. Đánh giá 4.9★ từ 1.648 khách hàng trên Google.</p>',
     '<p>The first authorised Honda dealer on National Route 1K, serving the University Village area, Dong Hoa Ward, Di An and Thu Duc for over 20 years. Rated 4.9★ by 1,648 customers on Google.</p>'),
    ('☎ Gọi 0274 3779 889', '☎ Call 0274 3779 889'),
    ('<p style="color:var(--gray);font-size:.92rem">Khách hàng gần Làng Đại Học, phường Đông Hòa, Dĩ An, Linh Xuân, Thủ Đức ghé cửa hàng để xem xe, nhận báo giá lăn bánh và ưu đãi mới nhất.</p>',
     '<p style="color:var(--gray);font-size:.92rem">Customers near the University Village, Dong Hoa Ward, Di An, Linh Xuan and Thu Duc are welcome to visit the store to view bikes, get an on-the-road quote and the latest offers.</p>'),
    ('<h2 class="sec">Dịch vụ tại chi nhánh 1</h2>', '<h2 class="sec">Services at branch 1</h2>'),
    ('<div class="card"><h3>Bán xe máy Honda mới</h3><p>Đầy đủ xe tay ga, xe số, xe côn tay và xe điện Honda. Hỗ trợ đăng ký biển số, giao xe tận nơi.</p></div>',
     '<div class="card"><h3>New Honda motorcycles</h3><p>Full range of Honda scooters, underbone models, manual-clutch bikes and electric scooters. We handle registration and number plates, and deliver to your door.</p></div>'),
    ('<div class="card"><h3>Mua xe trả góp</h3><p>Thủ tục rõ ràng – đúng quy định, ít chi phí, duyệt nhanh. Mua xe nhẹ gánh, an tâm sử dụng lâu dài.</p></div>',
     '<div class="card"><h3>Financing</h3><p>Clear, fully compliant paperwork, low fees and fast approval. Own your bike with lighter monthly payments.</p></div>'),
    ('<div><h4>HEAD Việt Thái Quân 1</h4>', '<div><h4>HEAD Viet Thai Quan 1</h4>'),
],
"head-viet-thai-quan-2/index.html": [
    ('<title>HEAD Việt Thái Quân 2 – 111 Nguyễn Duy Trinh, Bình Trưng</title>', '<title>HEAD Viet Thai Quan 2 – 111 Nguyen Duy Trinh, Binh Trung Ward (District 2)</title>'),
    ('<meta name="description" content="Cửa hàng xe máy Honda ủy nhiệm tại 111 Nguyễn Duy Trinh, phường Bình Trưng, TP.HCM (Quận 2 cũ). 4.7★ từ 1.955 đánh giá Google. Mở cửa đến 19:30.">',
     '<meta name="description" content="Authorised Honda motorcycle dealer at 111 Nguyen Duy Trinh, Binh Trung Ward, Ho Chi Minh City (formerly District 2). Rated 4.7★ from 1,955 Google reviews. Open until 19:30. English-speaking management.">'),
    ('"name": "HEAD Việt Thái Quân 2",', '"name": "HEAD Viet Thai Quan 2",'),
    ('"url": "https://headvietthaiquan.vn/head-viet-thai-quan-2/",', '"url": "https://headvietthaiquan.vn/en/head-viet-thai-quan-2/",'),
    ('<span>HEAD Việt Thái Quân 2 · phường Bình Trưng, Quận 2</span>', '<span>HEAD Viet Thai Quan 2 · Binh Trung Ward, District 2</span>'),
    ('<h1>HEAD Việt Thái Quân 2 – Cửa hàng xe máy Honda tại phường Bình Trưng, Quận 2</h1>', '<h1>HEAD Viet Thai Quan 2 – Honda motorcycle dealer in Binh Trung Ward, District 2</h1>'),
    ('<p>Đại lý Honda ủy nhiệm tại 111 Nguyễn Duy Trinh, phục vụ khách hàng khu vực Quận 2, Thủ Đức và TP.HCM. Đánh giá 4.7★ từ 1.955 khách hàng trên Google. Mở cửa đến 19:30 mỗi ngày.</p>',
     '<p>Authorised Honda dealer at 111 Nguyen Duy Trinh, serving customers across District 2, Thu Duc and Ho Chi Minh City. Rated 4.7★ by 1,955 customers on Google. Open until 19:30 every day. Our management speaks English.</p>'),
    ('☎ Gọi 028 7772 6789', '☎ Call 028 7772 6789'),
    ('<li><strong>Hotline</strong>', '<li><strong>Hotline</strong>'),
    ('<p style="color:var(--gray);font-size:.92rem">Mở cửa muộn nhất khu vực – tiện cho khách hàng bảo dưỡng xe sau giờ làm. Hỗ trợ giao xe tận nơi.</p>',
     '<p style="color:var(--gray);font-size:.92rem">The latest-closing Honda dealer in the area – convenient for servicing after work. Home delivery available.</p>'),
    ('<h2 class="sec">Dịch vụ tại chi nhánh 2</h2>', '<h2 class="sec">Services at branch 2</h2>'),
    ('<div class="card"><h3>Bán xe máy Honda mới</h3><p>Showroom đầy đủ xe tay ga (SH, SH Mode, LEAD, Vision, Vario, Air Blade), xe số, xe côn tay và xe điện ICON e:.</p></div>',
     '<div class="card"><h3>New Honda motorcycles</h3><p>Showroom with the full range of scooters (SH, SH Mode, LEAD, Vision, Vario, Air Blade), underbone models, manual-clutch bikes and the ICON e: electric scooter.</p></div>'),
    ('<div class="card"><h3>Thu xe cũ – đổi xe mới</h3><p>Định giá xe cũ minh bạch, hỗ trợ lên đời xe Honda mới với chi phí tốt nhất.</p></div>',
     '<div class="card"><h3>Trade-in &amp; upgrade</h3><p>Transparent valuation of your current bike and the best deal on upgrading to a new Honda.</p></div>'),
    ('<div><h4>HEAD Việt Thái Quân 2</h4>', '<div><h4>HEAD Viet Thai Quan 2</h4>'),
],
}

VI_CHARS = re.compile(r"[ăâđêôơưĂÂĐÊÔƠƯ\u0300-\u036f"
                      r"àáảãạằắẳẵặầấẩẫậèéẻẽẹềếểễệìíỉĩịòóỏõọồốổỗộờớởỡợùúủũụừứửữựỳýỷỹỵ"
                      r"ÀÁẢÃẠẰẮẲẴẶẦẤẨẪẬÈÉẺẼẸỀẾỂỄỆÌÍỈĨỊÒÓỎÕỌỒỐỔỖỘỜỚỞỠỢÙÚỦŨỤỪỨỬỮỰỲÝỶỸỴ]")
# Chuỗi tiếng Việt được phép giữ (tên riêng, tên chương trình)
ALLOWED_VI = ["Cùng Lên Ga – Quà Bao La", "Công ty TNHH Việt Thái Quân", "VIET THAI QUAN CO.,LTD",
              "Xe Máy HEAD Việt Thái Quân", "Nguyễn Duy Trinh", "Thành phố Hồ Chí Minh", "Tiếng Việt", "Xem trang này bằng tiếng Việt",
              "111+Nguy%E1%BB%85n", "Vi%E1%BB%87t+Th%C3%A1i+Qu%C3%A2n", "%C4%90%C3%B4ng+H%C3%B2a", "B%C3%ACnh+Tr%C6%B0ng"]


def build(vi_file):
    src = (ROOT / vi_file).read_text(encoding="utf-8")
    out = src
    errors = []
    for old, new in PER_PAGE[vi_file] + COMMON:   # riêng trước, chung sau (chuỗi dài trước)
        if old not in out:
            # Chuỗi chung có thể không có ở mọi trang; chuỗi riêng thì bắt buộc
            if (old, new) in PER_PAGE[vi_file]:
                errors.append(f"không tìm thấy: {old[:80]}")
            continue
        out = out.replace(old, new)
    vi_path, en_path = VI_PATH[vi_file], EN_PATH[vi_file]
    # canonical + hreflang
    out = out.replace(f'<link rel="canonical" href="{DOMAIN}{vi_path}">',
                      f'<link rel="canonical" href="{DOMAIN}{en_path}">\n'
                      f'<link rel="alternate" hreflang="en" href="{DOMAIN}{en_path}">\n'
                      f'<link rel="alternate" hreflang="vi" href="{DOMAIN}{vi_path}">\n'
                      f'<link rel="alternate" hreflang="x-default" href="{DOMAIN}{vi_path}">')
    # Nút ngôn ngữ: English -> Tiếng Việt (quay về trang gốc)
    out, n = re.subn(r'<a class="lang" href="[^"]*" lang="en" hreflang="en" title="Read this website in English"(?: rel="nofollow")?>',
                     f'<a class="lang" href="{vi_path}" lang="vi" hreflang="vi" title="Xem trang này bằng tiếng Việt">', out)
    if n != 1: errors.append("không tìm thấy nút ngôn ngữ")
    out = out.replace(GLOBE + 'English</a>', GLOBE + 'Tiếng Việt</a>')
    # Kiểm tra sót tiếng Việt (bỏ qua các tên riêng cho phép)
    chk = out
    for a in ALLOWED_VI: chk = chk.replace(a, "")
    for i, line in enumerate(chk.splitlines(), 1):
        if VI_CHARS.search(line):
            errors.append(f"dòng {i} còn tiếng Việt: {line.strip()[:110]}")
    return out, errors


def main():
    ok = True
    for vi_file, en_file in PAGES.items():
        out, errors = build(vi_file)
        if errors:
            ok = False
            print(f"[{vi_file}] LỖI:\n  - " + "\n  - ".join(errors))
            continue
        dest = ROOT / en_file
        dest.parent.mkdir(parents=True, exist_ok=True)
        dest.write_text(out, encoding="utf-8")
        print(f"✔ {en_file}")
    if not ok:
        sys.exit(1)


if __name__ == "__main__":
    main()
