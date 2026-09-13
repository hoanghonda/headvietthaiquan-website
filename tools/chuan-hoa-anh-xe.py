#!/usr/bin/env python3
"""
Chuẩn hóa ảnh xe cho thẻ sản phẩm: cùng khung 4:3 (1000x750), nền trắng,
xe chiếm 89% chiều ngang (tối đa 83% chiều cao) – giống khung ảnh chuẩn của Honda,
để mọi xe trên lưới sản phẩm hiển thị cùng cỡ mà không cần chỉnh --zoom.

Cách dùng:  python3 tools/chuan-hoa-anh-xe.py            # xử lý các ảnh trong DANH_SACH
            python3 tools/chuan-hoa-anh-xe.py anh-moi.jpg  # xử lý 1 ảnh (ghi đè tại chỗ)
            python3 tools/chuan-hoa-anh-xe.py goc.png dich.jpg
Ảnh nguồn nên có nền trắng hoặc trong suốt. Cần Pillow + numpy.
"""
import sys
from pathlib import Path
import numpy as np
from PIL import Image

ROOT = Path(__file__).resolve().parent.parent
W, H = 1000, 750
XE_NGANG, XE_CAO_MAX = 0.89, 0.83

# (nguồn, đích) – đích trùng nguồn = ghi đè
DANH_SACH = [
    ("vision.jpg", "vision.jpg"),
    ("air-blade.jpg", "air-blade.jpg"),
    ("future-125.jpg", "future-125.jpg"),
    ("icon-e.jpg", "icon-e.jpg"),
    ("sh350i.jpg", "sh350i.jpg"),
    ("vario-125.png", "vario-125-card.jpg"),
    ("super-cub-125-2026-xam.jpg", "super-cub-125-card.jpg"),
]


def tach_xe(im):
    """Trả về (ảnh RGB nền trắng, bbox của xe)."""
    if im.mode in ("RGBA", "LA") or (im.mode == "P" and "transparency" in im.info):
        im = im.convert("RGBA")
        a = np.asarray(im)[:, :, 3]
        mask = a > 20
        nen = Image.new("RGB", im.size, (255, 255, 255))
        nen.paste(im, mask=im.split()[3])
        rgb = nen
    else:
        rgb = im.convert("RGB")
        arr = np.asarray(rgb).astype(np.int16)
        lum = arr.mean(axis=2)
        sat = arr.max(axis=2) - arr.min(axis=2)
        mask = (lum < 238) | (sat > 18)
    # bỏ nhiễu: chỉ tính hàng/cột có >= 3 pixel thuộc xe
    cols = np.where(mask.sum(axis=0) >= 3)[0]
    rows = np.where(mask.sum(axis=1) >= 3)[0]
    bbox = (int(cols.min()), int(rows.min()), int(cols.max()) + 1, int(rows.max()) + 1)
    return rgb, bbox


def lam_trang_nen(rgb):
    """Kéo nền xám rất nhạt (>=238, ít bão hòa) về trắng tuyệt đối, giữ chi tiết xe."""
    arr = np.asarray(rgb).astype(np.float32)
    lum = arr.mean(axis=2)
    sat = arr.max(axis=2) - arr.min(axis=2)
    nen = (lum >= 238) & (sat <= 12)
    arr[nen] = 255
    return Image.fromarray(arr.astype(np.uint8))


def chuan_hoa(src, dst):
    im = Image.open(src)
    rgb, (x0, y0, x1, y1) = tach_xe(im)
    rgb = lam_trang_nen(rgb)
    xe = rgb.crop((x0, y0, x1, y1))
    ty_le = min(W * XE_NGANG / xe.width, H * XE_CAO_MAX / xe.height)
    xe = xe.resize((round(xe.width * ty_le), round(xe.height * ty_le)), Image.LANCZOS)
    canvas = Image.new("RGB", (W, H), (255, 255, 255))
    canvas.paste(xe, ((W - xe.width) // 2, (H - xe.height) // 2))
    canvas.save(dst, quality=86, optimize=True)
    print(f"✔ {Path(dst).name:32s} xe {xe.width}x{xe.height}px ({xe.width / W * 100:.0f}% ngang, {xe.height / H * 100:.0f}% cao)")


def main(argv):
    if len(argv) == 1:
        cap = [(ROOT / a, ROOT / b) for a, b in DANH_SACH]
    elif len(argv) == 2:
        cap = [(Path(argv[1]), Path(argv[1]))]
    else:
        cap = [(Path(argv[1]), Path(argv[2]))]
    for src, dst in cap:
        if not src.exists():
            print(f"✘ không thấy {src}")
            continue
        chuan_hoa(src, dst)


if __name__ == "__main__":
    main(sys.argv)
