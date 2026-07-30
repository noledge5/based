#!/usr/bin/env python3
"""Turn a folder of images into a captioned ai-toolkit LoRA dataset.

Scans an input folder, drops near-duplicates, normalises the images, captions
each one with Claude against the bundled Krea 2 character prompt, and writes a
renamed `name_001.png` + `name_001.txt` pair per image plus a run report.

    pip install anthropic pillow
    export ANTHROPIC_API_KEY=...
    ./build_dataset.py -i ./raw -o ./dataset --prefix ada \
        --constant-traits "short black hair, brown eyes, freckles"
"""

from __future__ import annotations

import argparse
import base64
import io
import json
import sys
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image, ImageFilter, ImageOps, ImageStat

SOURCE_EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff", ".avif"}
AI_TOOLKIT_EXTS = {".jpg", ".jpeg", ".png"}

# Fixed defect vocabulary. Consistency is the point — a defect phrase is only
# learnable if it appears identically every time it appears.
DEFECT_ADJECTIVES = {
    "blurry": "blurry",
    "low-resolution": "low-resolution",
    "heavily compressed": "heavily compressed",
    "grainy": "grainy",
}
DEFECT_ORDER = list(DEFECT_ADJECTIVES)

CAPTION_SCHEMA = {
    "type": "object",
    "properties": {
        "caption": {"type": "string"},
        "defects": {"type": "array", "items": {"type": "string", "enum": DEFECT_ORDER}},
    },
    "required": ["caption", "defects"],
    "additionalProperties": False,
}

QUALITY_BLOCK_OFF = (
    "Judge defects on their own merits; they are recorded for review and do not\n"
    "affect the caption text."
)
QUALITY_BLOCK_ON = (
    "Defects you report WILL be appended to the caption by the calling tool, in\n"
    "fixed wording. Report only defects that are plainly visible."
)


@dataclass
class Item:
    source: Path
    index: int = 0
    name: str = ""
    width: int = 0
    height: int = 0
    sharpness: float = 0.0
    caption: str = ""
    defects: list[str] = field(default_factory=list)
    notes: list[str] = field(default_factory=list)
    error: str = ""


# ---------------------------------------------------------------- image utils


def load_image(path: Path) -> Image.Image:
    """Open, apply EXIF rotation, and flatten to RGB on white."""
    img = Image.open(path)
    img = ImageOps.exif_transpose(img)
    if img.mode in ("RGBA", "LA", "P"):
        img = img.convert("RGBA")
        flat = Image.new("RGB", img.size, (255, 255, 255))
        flat.paste(img, mask=img.split()[-1])
        return flat
    return img.convert("RGB")


def dhash(img: Image.Image, size: int = 8) -> int:
    """Difference hash — cheap perceptual fingerprint for dedupe."""
    small = img.convert("L").resize((size + 1, size), Image.LANCZOS)
    px = small.tobytes()  # mode "L" — one byte per pixel, row-major
    bits = 0
    for row in range(size):
        base = row * (size + 1)
        for col in range(size):
            bits = (bits << 1) | int(px[base + col] > px[base + col + 1])
    return bits


def sharpness(img: Image.Image) -> float:
    """Relative sharpness proxy. Only meaningful compared within one dataset."""
    edges = img.convert("L").filter(ImageFilter.FIND_EDGES)
    return round(ImageStat.Stat(edges).stddev[0], 1)


def fit(img: Image.Image, max_side: int) -> Image.Image:
    if max(img.size) <= max_side:
        return img
    scale = max_side / max(img.size)
    return img.resize(
        (max(1, round(img.width * scale)), max(1, round(img.height * scale))),
        Image.LANCZOS,
    )


def to_jpeg_b64(img: Image.Image, max_side: int) -> str:
    buf = io.BytesIO()
    fit(img, max_side).save(buf, format="JPEG", quality=88, optimize=True)
    return base64.standard_b64encode(buf.getvalue()).decode()


# --------------------------------------------------------------------- prompt


def build_system_prompt(traits: str, note_quality: bool) -> str:
    path = Path(__file__).resolve().parent.parent / "references" / "caption-system-prompt.md"
    if not path.exists():
        sys.exit(f"missing prompt file: {path}")
    traits_block = (
        "\n".join(f"- {t.strip()}" for t in traits.split(",") if t.strip())
        if traits.strip()
        else (
            "- (none declared) Still avoid describing the face, body type, and any\n"
            "  hair or feature that appears unchanged across the whole dataset."
        )
    )
    return (
        path.read_text(encoding="utf-8")
        .replace("{{CONSTANT_TRAITS}}", traits_block)
        .replace("{{QUALITY_BLOCK}}", QUALITY_BLOCK_ON if note_quality else QUALITY_BLOCK_OFF)
    )


# --------------------------------------------------------------------- Claude


def caption_one(client, model: str, system: str, img: Image.Image, api_max_side: int) -> dict:
    response = client.messages.create(
        model=model,
        max_tokens=500,
        system=system,
        # Captioning is perception + formatting, not reasoning. Low effort keeps
        # this cheap; thinking stays on (its default) because disabling it on
        # Opus 5 risks <thinking> tags leaking into the output.
        output_config={
            "effort": "low",
            "format": {"type": "json_schema", "schema": CAPTION_SCHEMA},
        },
        messages=[
            {
                "role": "user",
                "content": [
                    {
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": to_jpeg_b64(img, api_max_side),
                        },
                    },
                    {"type": "text", "text": "Caption this image."},
                ],
            }
        ],
    )
    if response.stop_reason == "refusal":
        raise RuntimeError("model declined to caption this image")
    text = next(b.text for b in response.content if b.type == "text")
    return json.loads(text)


# -------------------------------------------------------------------- caption


def assemble(raw: str, defects: list[str], trigger: str, note_quality: bool) -> tuple[str, list[str]]:
    """Normalise the model's caption into the final .txt contents."""
    notes: list[str] = []
    caption = " ".join(raw.split())

    if "[trigger]" not in caption:
        notes.append("model omitted [trigger]; prepended")
        caption = f"[trigger], {caption[0].lower()}{caption[1:]}" if caption else "[trigger]"

    if note_quality and defects:
        ordered = [DEFECT_ADJECTIVES[d] for d in DEFECT_ORDER if d in defects]
        caption = f"{caption.rstrip(' .')}, a {', '.join(ordered)} photo."

    words = len(caption.split())
    if words > 70:
        notes.append(f"caption is {words} words (ceiling is 70)")

    return caption.replace("[trigger]", trigger), notes


# ----------------------------------------------------------------------- main


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("-i", "--input", type=Path, required=True, help="folder of source images")
    p.add_argument("-o", "--output", type=Path, required=True, help="dataset folder to create")
    p.add_argument("--prefix", help="filename prefix (default: output folder name)")
    p.add_argument(
        "--constant-traits",
        default="",
        help="comma-separated traits the captioner must never mention, "
        'e.g. "short black hair, brown eyes, freckles"',
    )
    p.add_argument("--trigger", default="[trigger]", help="token written into captions (default: %(default)s)")
    p.add_argument("--model", default="claude-opus-5", help="captioning model (default: %(default)s)")
    p.add_argument("--note-quality", action="store_true", help="append visible defects to captions")
    p.add_argument("--min-side", type=int, default=1024, help="warn below this shortest side (default: %(default)s)")
    p.add_argument("--max-side", type=int, default=2048, help="downscale dataset images above this (default: %(default)s)")
    p.add_argument("--api-max-side", type=int, default=1024, help="downscale for the API only (default: %(default)s)")
    p.add_argument("--workers", type=int, default=4, help="parallel caption requests (default: %(default)s)")
    p.add_argument("--dedupe-distance", type=int, default=4, help="dHash distance for near-duplicates; 0 disables")
    p.add_argument("--overwrite", action="store_true", help="recaption images that already have a .txt")
    p.add_argument("--dry-run", action="store_true", help="scan and report without calling the API or writing")
    return p.parse_args(argv)


def collect(folder: Path, dedupe_distance: int) -> tuple[list[Item], list[tuple[Path, Path]]]:
    paths = sorted(p for p in folder.iterdir() if p.is_file() and p.suffix.lower() in SOURCE_EXTS)
    items: list[Item] = []
    dupes: list[tuple[Path, Path]] = []
    seen: list[tuple[int, Path]] = []

    for path in paths:
        try:
            img = load_image(path)
        except Exception as exc:  # unreadable / truncated / unsupported codec
            print(f"  skip {path.name}: {exc}", file=sys.stderr)
            continue

        if dedupe_distance > 0:
            h = dhash(img)
            match = next((p for prev, p in seen if bin(h ^ prev).count("1") <= dedupe_distance), None)
            if match:
                dupes.append((path, match))
                continue
            seen.append((h, path))

        items.append(Item(source=path, width=img.width, height=img.height, sharpness=sharpness(img)))

    return items, dupes


def write_report(out: Path, items: list[Item], dupes, args, median_sharp: float) -> None:
    lines = [
        "# Dataset build report",
        "",
        f"- source: `{args.input}`",
        f"- images written: {sum(1 for i in items if not i.error)}",
        f"- model: `{args.model}`",
        f"- constant traits: {args.constant_traits or '(none declared)'}",
        f"- defects appended to captions: {'yes' if args.note_quality else 'no (recorded only)'}",
        "",
        "## Images",
        "",
        "| file | source | source size | sharpness | defects | notes |",
        "| --- | --- | --- | --- | --- | --- |",
    ]
    for item in items:
        notes = "; ".join(item.notes) or ("FAILED: " + item.error if item.error else "")
        lines.append(
            f"| `{item.name or '-'}` | `{item.source.name}` | {item.width}x{item.height} "
            f"| {item.sharpness} | {', '.join(item.defects) or '-'} | {notes} |"
        )

    lines += ["", f"Median sharpness {median_sharp}. The score is a relative proxy —",
              "compare images within this set only; it is not an absolute measure."]

    if dupes:
        lines += ["", "## Near-duplicates dropped", ""]
        lines += [f"- `{d.name}` ≈ `{k.name}`" for d, k in dupes]

    (out / "_report.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    args = parse_args(argv)
    if not args.input.is_dir():
        sys.exit(f"not a directory: {args.input}")

    prefix = args.prefix or args.output.name
    print(f"scanning {args.input} ...")
    items, dupes = collect(args.input, args.dedupe_distance)
    if not items:
        sys.exit("no readable images found")

    sharps = sorted(i.sharpness for i in items)
    median_sharp = round(sharps[len(sharps) // 2], 1)
    soft = [i for i in items if i.sharpness < median_sharp * 0.6]
    small = [i for i in items if min(i.width, i.height) < args.min_side]

    print(f"  {len(items)} images, {len(dupes)} near-duplicates dropped")
    if small:
        print(f"  {len(small)} below {args.min_side}px shortest side — ai-toolkit will not upscale these")
    if soft:
        print(f"  {len(soft)} notably softer than the set median")

    for n, item in enumerate(items, start=1):
        item.index = n
        ext = item.source.suffix.lower()
        item.name = f"{prefix}_{n:03d}" + (ext if ext in AI_TOOLKIT_EXTS else ".png")
        if min(item.width, item.height) < args.min_side:
            item.notes.append(f"below {args.min_side}px shortest side")

    if args.dry_run:
        for item in items:
            print(f"  {item.source.name} -> {item.name}  ({item.width}x{item.height}, sharp {item.sharpness})")
        print("\ndry run — nothing written, no API calls made")
        return 0

    args.output.mkdir(parents=True, exist_ok=True)
    system = build_system_prompt(args.constant_traits, args.note_quality)

    try:
        import anthropic
    except ImportError:
        sys.exit("pip install anthropic")
    client = anthropic.Anthropic()

    pending = [i for i in items if args.overwrite or not (args.output / f"{Path(i.name).stem}.txt").exists()]
    print(f"\ncaptioning {len(pending)} images with {args.model} ...")

    def work(item: Item) -> None:
        try:
            img = load_image(item.source)
            result = caption_one(client, args.model, system, img, args.api_max_side)
            item.defects = [d for d in result.get("defects", []) if d in DEFECT_ADJECTIVES]
            item.caption, notes = assemble(result["caption"], item.defects, args.trigger, args.note_quality)
            item.notes.extend(notes)

            # Always re-encode rather than copying: that bakes in EXIF rotation
            # and guarantees RGB, so ai-toolkit sees exactly what we captioned.
            target = args.output / item.name
            resized = fit(img, args.max_side)
            if target.suffix in (".jpg", ".jpeg"):
                resized.save(target, quality=95, subsampling=0)
            else:
                resized.save(target)
            (args.output / f"{Path(item.name).stem}.txt").write_text(item.caption + "\n", encoding="utf-8")
            print(f"  {item.name}: {item.caption[:88]}")
        except Exception as exc:
            item.error = str(exc)
            print(f"  {item.name}: FAILED {exc}", file=sys.stderr)

    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        list(pool.map(work, pending))

    (args.output / "_manifest.json").write_text(
        json.dumps(
            [
                {
                    "file": i.name,
                    "source": str(i.source),
                    "caption": i.caption,
                    "defects": i.defects,
                    "size": [i.width, i.height],
                    "sharpness": i.sharpness,
                    "notes": i.notes,
                    "error": i.error,
                }
                for i in items
            ],
            indent=2,
        ),
        encoding="utf-8",
    )
    write_report(args.output, items, dupes, args, median_sharp)

    failed = [i for i in items if i.error]
    print(f"\nwrote {len(items) - len(failed)} pairs to {args.output}")
    print(f"review {args.output / '_report.md'} before training — hand-edit captions that got it wrong")
    return 1 if failed else 0


if __name__ == "__main__":
    raise SystemExit(main())
