#------------------------------------
# you need to install Pillow first
# python -m pip install Pillow
#------------------------------------

import argparse
import sys
from pathlib import Path

from PIL import (Image, ImageDraw, ImageEnhance,
                 ImageFilter, ImageFont)

IMAGE_EXTENSIONS = {".jpg", ".jpeg", ".png", ".webp",
                    ".bmp", ".gif", ".tiff"}

FILTERS = {
    "blur":         ImageFilter.BLUR,
    "sharpen":      ImageFilter.SHARPEN,
    "edge":         ImageFilter.EDGE_ENHANCE,
    "emboss":       ImageFilter.EMBOSS,
    "smooth":       ImageFilter.SMOOTH,
    "detail":       ImageFilter.DETAIL,
}



def find_images(input_dir: Path) -> list[Path]:
    images = []
    for ext in IMAGE_EXTENSIONS:
        images.extend(input_dir.glob(f"*{ext}"))
        images.extend(input_dir.glob(f"*{ext.upper()}"))
    return sorted(set(images))



def resize_image(img: Image.Image, width: int,
                 height: int | None = None) -> Image.Image:
    if height:
        return img.resize((width, height), Image.LANCZOS)
    
    ratio  = width / img.width
    h      = int(img.height * ratio)
    return img.resize((width, h), Image.LANCZOS)

def make_thumbnail(img: Image.Image, max_size: int) -> Image.Image:
    thumb = img.copy()
    thumb.thumbnail((max_size, max_size), Image.LANCZOS)
    return thumb

def apply_filter(img: Image.Image, filter_name: str) -> Image.Image:
    f = FILTERS.get(filter_name.lower())
    if not f:
        print(f"  Unknown filter '{filter_name}'. "
              f"Options: {', '.join(FILTERS)}")
        return img
    return img.filter(f)

def apply_grayscale(img: Image.Image) -> Image.Image:
    return img.convert("L").convert("RGB")

def adjust_brightness(img: Image.Image, factor: float) -> Image.Image:
    return ImageEnhance.Brightness(img).enhance(factor)

def adjust_contrast(img: Image.Image, factor: float) -> Image.Image:
    return ImageEnhance.Contrast(img).enhance(factor)

def add_watermark(img: Image.Image, text: str,
                  opacity: int = 100) -> Image.Image:
    base    = img.convert("RGBA")
    overlay = Image.new("RGBA", base.size, (0, 0, 0, 0))
    draw    = ImageDraw.Draw(overlay)
    try:
        font_size = max(16, base.width // 25)
        font = ImageFont.truetype("arial.ttf", size=font_size)
    except (IOError, OSError):
        font = ImageFont.load_default()

    bbox   = draw.textbbox((0, 0), text, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    x = base.width  - tw - 20
    y = base.height - th - 20

    draw.text((x + 2, y + 2), text, font=font,
              fill=(0, 0, 0, opacity // 2))
    draw.text((x, y), text, font=font,
              fill=(255, 255, 255, opacity))

    return Image.alpha_composite(base, overlay).convert("RGB")



def get_image_info(path: Path):
    img = Image.open(path)
    size_kb = path.stat().st_size / 1024
    print(f"\n  File    : {path.name}")
    print(f"  Format  : {img.format}")
    print(f"  Mode    : {img.mode}")
    print(f"  Size    : {img.width} × {img.height} px")
    print(f"  On disk : {size_kb:.1f} KB")



def process_image(src: Path, output_dir: Path, opts: dict) -> Path | None:
    try:
        img = Image.open(src)

        
        if img.mode not in ("RGB", "L"):
            img = img.convert("RGB")

        
        if opts.get("grayscale"):
            img = apply_grayscale(img)

        if opts.get("resize_w"):
            img = resize_image(img, opts["resize_w"],
                               opts.get("resize_h"))

        if opts.get("thumbnail"):
            img = make_thumbnail(img, opts["thumbnail"])

        if opts.get("filter"):
            img = apply_filter(img, opts["filter"])

        if opts.get("brightness") and opts["brightness"] != 1.0:
            img = adjust_brightness(img, opts["brightness"])

        if opts.get("contrast") and opts["contrast"] != 1.0:
            img = adjust_contrast(img, opts["contrast"])

        if opts.get("watermark"):
            img = add_watermark(img, opts["watermark"],
                                opacity=opts.get("opacity", 100))

        
        out_fmt  = opts.get("format", src.suffix.lstrip(".")).lower()
        out_fmt  = "jpeg" if out_fmt == "jpg" else out_fmt
        out_name = src.stem + "." + ("jpg" if out_fmt == "jpeg" else out_fmt)
        out_path = output_dir / out_name

        save_kwargs = {}
        if out_fmt == "jpeg":
            save_kwargs["quality"]   = opts.get("quality", 90)
            save_kwargs["optimize"]  = True
            img = img.convert("RGB")   
        elif out_fmt == "webp":
            save_kwargs["quality"]  = opts.get("quality", 85)

        img.save(out_path, format=out_fmt.upper(), **save_kwargs)
        return out_path

    except Exception as e:
        print(f"  ✖  {src.name}: {e}")
        return None



def batch_process(input_dir: Path, output_dir: Path, opts: dict):
    images = find_images(input_dir)
    if not images:
        print(f"  No images found in '{input_dir}'.")
        return

    output_dir.mkdir(parents=True, exist_ok=True)
    print(f"\n  Processing {len(images)} image(s)...\n")

    ok = fail = 0
    for i, src in enumerate(images, 1):
        out = process_image(src, output_dir, opts)
        if out:
            size_in  = src.stat().st_size  / 1024
            size_out = out.stat().st_size  / 1024
            saving   = (1 - size_out / size_in) * 100 if size_in else 0
            print(f"  [{i:>3}/{len(images)}] ✔  {src.name:<30} "
                  f"{size_in:>6.0f}KB → {size_out:>6.0f}KB "
                  f"({saving:+.0f}%)")
            ok += 1
        else:
            fail += 1

    print(f"\n  Done — {ok} succeeded, {fail} failed.")
    print(f"  Output: {output_dir.resolve()}")



def build_parser():
    p = argparse.ArgumentParser(
        description="Batch image processor using Pillow."
    )
    p.add_argument("input",  help="Input folder containing images")
    p.add_argument("output", nargs="?", default="output",
                   help="Output folder (default: ./output)")

    
    p.add_argument("--resize",      type=int, metavar="W",
                   help="Resize to width W (preserves aspect ratio)")
    p.add_argument("--resize-h",    type=int, metavar="H",
                   help="Explicit height (use with --resize)")
    p.add_argument("--thumbnail",   type=int, metavar="PX",
                   help="Fit inside a PX×PX box")
    p.add_argument("--filter",      choices=list(FILTERS),
                   help="Apply a named filter")
    p.add_argument("--grayscale",   action="store_true",
                   help="Convert to greyscale")
    p.add_argument("--brightness",  type=float, default=1.0,
                   metavar="F", help="Brightness factor (1.0 = original)")
    p.add_argument("--contrast",    type=float, default=1.0,
                   metavar="F", help="Contrast factor (1.0 = original)")
    p.add_argument("--watermark",   type=str, metavar="TEXT",
                   help="Watermark text to stamp on images")
    p.add_argument("--opacity",     type=int, default=100, metavar="0-255",
                   help="Watermark opacity (default: 100)")

    
    p.add_argument("--format",      choices=["jpg","png","webp"],
                   help="Convert all images to this format")
    p.add_argument("--quality",     type=int, default=90, metavar="1-100",
                   help="JPEG/WebP quality (default: 90)")
    p.add_argument("--info",        action="store_true",
                   help="Print info about each image instead of processing")
    return p

def main():
    parser = build_parser()
    if len(sys.argv) == 1:
        parser.print_help()
        return

    args      = parser.parse_args()
    input_dir = Path(args.input)

    if not input_dir.exists():
        print(f"  Input folder not found: {input_dir}")
        return

    if args.info:
        for p in find_images(input_dir):
            get_image_info(p)
        return

    opts = {
        "resize_w":   args.resize,
        "resize_h":   args.resize_h,
        "thumbnail":  args.thumbnail,
        "filter":     args.filter,
        "grayscale":  args.grayscale,
        "brightness": args.brightness,
        "contrast":   args.contrast,
        "watermark":  args.watermark,
        "opacity":    args.opacity,
        "format":     args.format,
        "quality":    args.quality,
    }

    batch_process(input_dir, Path(args.output), opts)

if __name__ == "__main__":
    main()