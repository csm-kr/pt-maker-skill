#!/usr/bin/env python3
"""pt-maker: export reveal.js HTML or PDF to an image-based PPTX.

This exporter prioritizes visual alignment. Each slide is rendered to a PNG and
inserted as one full-slide picture in a 16:9 PowerPoint deck. The resulting PPTX
is easy to present and visually faithful, but slide text/shapes are not editable.

Usage:
  python export_pptx.py deck.html [out.pptx] [--width 2048]
  python export_pptx.py deck.pdf [out.pptx] [--width 2048]
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

from browser_harness_runtime import (
    BrowserHarnessError,
    capture_reveal_slides,
)

try:
    import fitz  # PyMuPDF
except ImportError:
    sys.exit("ERROR: install pymupdf first: pip install pymupdf")

try:
    from PIL import Image
except ImportError:
    sys.exit("ERROR: install pillow first: pip install pillow")


SLIDE_CX = 12_192_000  # 13.333333in * 914400
SLIDE_CY = 6_858_000   # 7.5in * 914400
REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
OD_REL = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"


def run(cmd: list[str], *, check: bool = False) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(cmd, capture_output=True, text=True)
    if check and result.returncode != 0:
        detail = (result.stdout or "") + (result.stderr or "")
        raise RuntimeError(detail.strip() or f"command failed: {' '.join(cmd)}")
    return result


def capture_html_with_browser_harness(
    html_path: Path,
    tmp: Path,
    width: int,
) -> list[Path]:
    try:
        return capture_reveal_slides(html_path, tmp, width=width)
    except BrowserHarnessError as exc:
        raise RuntimeError(str(exc)) from exc


def render_pdf_to_pngs(pdf_path: Path, tmp: Path, width: int) -> list[Path]:
    doc = fitz.open(str(pdf_path))
    shots: list[Path] = []
    for idx, page in enumerate(doc):
        zoom = width / float(page.rect.width)
        pix = page.get_pixmap(matrix=fitz.Matrix(zoom, zoom), alpha=False)
        shot = tmp / f"slide_{idx + 1:03d}.png"
        pix.save(str(shot))
        shots.append(shot)
    doc.close()
    return shots


def html_to_pdf(html_path: Path, tmp: Path) -> Path:
    sibling_pdf = html_path.with_suffix(".pdf")
    if sibling_pdf.exists() and sibling_pdf.stat().st_mtime >= html_path.stat().st_mtime:
        print(f"INFO: using existing PDF fallback: {sibling_pdf}")
        return sibling_pdf

    out_pdf = tmp / f"{html_path.stem}.pdf"
    export_pdf = Path(__file__).resolve().with_name("export_pdf.py")
    result = run([sys.executable, str(export_pdf), str(html_path), str(out_pdf)])
    if result.returncode != 0 or not out_pdf.exists():
        detail = (result.stdout or "") + (result.stderr or "")
        raise RuntimeError("HTML to PDF fallback failed.\n" + detail.strip())
    return out_pdf


def render_source_to_pngs(source: Path, tmp: Path, width: int) -> list[Path]:
    suffix = source.suffix.lower()
    if suffix == ".pdf":
        return render_pdf_to_pngs(source, tmp, width)
    if suffix in {".html", ".htm"}:
        try:
            return capture_html_with_browser_harness(source, tmp, width)
        except Exception as exc:
            print(
                "INFO: browser-harness screenshot path unavailable "
                f"({exc}); falling back through browser-harness PDF."
            )
            pdf = html_to_pdf(source, tmp)
            return render_pdf_to_pngs(pdf, tmp, width)
    raise SystemExit(f"ERROR: unsupported input type: {source.suffix}. Use .html, .htm, or .pdf.")


def rels_xml(rels: list[tuple[str, str, str]]) -> str:
    rows = "\n".join(
        f'  <Relationship Id="{rid}" Type="{rtype}" Target="{html.escape(target)}"/>'
        for rid, rtype, target in rels
    )
    return f'<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n<Relationships xmlns="{REL_NS}">\n{rows}\n</Relationships>'


def content_types_xml(slide_count: int) -> str:
    slide_overrides = "\n".join(
        f'  <Override PartName="/ppt/slides/slide{i}.xml" '
        'ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>'
        for i in range(1, slide_count + 1)
    )
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
  <Default Extension="xml" ContentType="application/xml"/>
  <Default Extension="png" ContentType="image/png"/>
  <Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
  <Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
  <Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>
  <Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>
  <Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>
  <Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>
{slide_overrides}
</Types>'''


def presentation_xml(slide_count: int) -> str:
    sld_ids = "\n".join(
        f'    <p:sldId id="{255 + i}" r:id="rId{i + 1}"/>'
        for i in range(1, slide_count + 1)
    )
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:presentation xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="{OD_REL}" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:sldMasterIdLst>
    <p:sldMasterId id="2147483648" r:id="rId1"/>
  </p:sldMasterIdLst>
  <p:sldIdLst>
{sld_ids}
  </p:sldIdLst>
  <p:sldSz cx="{SLIDE_CX}" cy="{SLIDE_CY}"/>
  <p:notesSz cx="6858000" cy="9144000"/>
  <p:defaultTextStyle/>
</p:presentation>'''


def slide_bounds(image_path: Path, fit: str) -> tuple[int, int, int, int]:
    if fit == "stretch":
        return 0, 0, SLIDE_CX, SLIDE_CY

    with Image.open(image_path) as img:
        iw, ih = img.size
    image_ratio = iw / ih
    slide_ratio = SLIDE_CX / SLIDE_CY

    if fit == "cover":
        if image_ratio > slide_ratio:
            h = SLIDE_CY
            w = round(h * image_ratio)
        else:
            w = SLIDE_CX
            h = round(w / image_ratio)
    else:
        if image_ratio > slide_ratio:
            w = SLIDE_CX
            h = round(w / image_ratio)
        else:
            h = SLIDE_CY
            w = round(h * image_ratio)

    x = round((SLIDE_CX - w) / 2)
    y = round((SLIDE_CY - h) / 2)
    return x, y, w, h


def slide_xml(index: int, image_path: Path, fit: str) -> str:
    x, y, cx, cy = slide_bounds(image_path, fit)
    name = html.escape(f"Slide {index} image")
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sld xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="{OD_REL}" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld>
    <p:spTree>
      <p:nvGrpSpPr>
        <p:cNvPr id="1" name=""/>
        <p:cNvGrpSpPr/>
        <p:nvPr/>
      </p:nvGrpSpPr>
      <p:grpSpPr>
        <a:xfrm>
          <a:off x="0" y="0"/>
          <a:ext cx="0" cy="0"/>
          <a:chOff x="0" y="0"/>
          <a:chExt cx="0" cy="0"/>
        </a:xfrm>
      </p:grpSpPr>
      <p:pic>
        <p:nvPicPr>
          <p:cNvPr id="2" name="{name}"/>
          <p:cNvPicPr>
            <a:picLocks noChangeAspect="1"/>
          </p:cNvPicPr>
          <p:nvPr/>
        </p:nvPicPr>
        <p:blipFill>
          <a:blip r:embed="rId2"/>
          <a:stretch><a:fillRect/></a:stretch>
        </p:blipFill>
        <p:spPr>
          <a:xfrm>
            <a:off x="{x}" y="{y}"/>
            <a:ext cx="{cx}" cy="{cy}"/>
          </a:xfrm>
          <a:prstGeom prst="rect"><a:avLst/></a:prstGeom>
        </p:spPr>
      </p:pic>
    </p:spTree>
  </p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sld>'''


def slide_master_xml() -> str:
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldMaster xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="{OD_REL}" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main">
  <p:cSld>
    <p:spTree>
      <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
      <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
    </p:spTree>
  </p:cSld>
  <p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/>
  <p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst>
  <p:txStyles><p:titleStyle/><p:bodyStyle/><p:otherStyle/></p:txStyles>
</p:sldMaster>'''


def slide_layout_xml() -> str:
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<p:sldLayout xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" xmlns:r="{OD_REL}" xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main" type="blank" preserve="1">
  <p:cSld name="Blank">
    <p:spTree>
      <p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>
      <p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>
    </p:spTree>
  </p:cSld>
  <p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr>
</p:sldLayout>'''


def theme_xml() -> str:
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="pt-maker">
  <a:themeElements>
    <a:clrScheme name="pt-maker">
      <a:dk1><a:srgbClr val="20174A"/></a:dk1>
      <a:lt1><a:srgbClr val="FFFFFF"/></a:lt1>
      <a:dk2><a:srgbClr val="20174A"/></a:dk2>
      <a:lt2><a:srgbClr val="FAF3DE"/></a:lt2>
      <a:accent1><a:srgbClr val="C73463"/></a:accent1>
      <a:accent2><a:srgbClr val="6C648F"/></a:accent2>
      <a:accent3><a:srgbClr val="E7DCB6"/></a:accent3>
      <a:accent4><a:srgbClr val="FFFCF1"/></a:accent4>
      <a:accent5><a:srgbClr val="555555"/></a:accent5>
      <a:accent6><a:srgbClr val="999999"/></a:accent6>
      <a:hlink><a:srgbClr val="0563C1"/></a:hlink>
      <a:folHlink><a:srgbClr val="954F72"/></a:folHlink>
    </a:clrScheme>
    <a:fontScheme name="pt-maker">
      <a:majorFont><a:latin typeface="Aptos Display"/><a:ea typeface=""/><a:cs typeface=""/></a:majorFont>
      <a:minorFont><a:latin typeface="Aptos"/><a:ea typeface=""/><a:cs typeface=""/></a:minorFont>
    </a:fontScheme>
    <a:fmtScheme name="pt-maker">
      <a:fillStyleLst>
        <a:solidFill><a:schemeClr val="phClr"/></a:solidFill>
        <a:solidFill><a:schemeClr val="phClr"/></a:solidFill>
        <a:solidFill><a:schemeClr val="phClr"/></a:solidFill>
      </a:fillStyleLst>
      <a:lnStyleLst>
        <a:ln w="6350" cap="flat"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln>
        <a:ln w="12700" cap="flat"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln>
        <a:ln w="19050" cap="flat"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln>
      </a:lnStyleLst>
      <a:effectStyleLst>
        <a:effectStyle><a:effectLst/></a:effectStyle>
        <a:effectStyle><a:effectLst/></a:effectStyle>
        <a:effectStyle><a:effectLst/></a:effectStyle>
      </a:effectStyleLst>
      <a:bgFillStyleLst>
        <a:solidFill><a:schemeClr val="phClr"/></a:solidFill>
        <a:solidFill><a:schemeClr val="phClr"/></a:solidFill>
        <a:solidFill><a:schemeClr val="phClr"/></a:solidFill>
      </a:bgFillStyleLst>
    </a:fmtScheme>
  </a:themeElements>
</a:theme>'''


def app_xml(slide_count: int) -> str:
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties" xmlns:vt="http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes">
  <Application>pt-maker</Application>
  <PresentationFormat>On-screen Show (16:9)</PresentationFormat>
  <Slides>{slide_count}</Slides>
  <Company/>
  <AppVersion>16.0000</AppVersion>
</Properties>'''


def core_xml(title: str) -> str:
    timestamp = dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()
    safe_title = html.escape(title)
    return f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" xmlns:dcmitype="http://purl.org/dc/dcmitype/" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
  <dc:title>{safe_title}</dc:title>
  <dc:creator>pt-maker</dc:creator>
  <cp:lastModifiedBy>pt-maker</cp:lastModifiedBy>
  <dcterms:created xsi:type="dcterms:W3CDTF">{timestamp}</dcterms:created>
  <dcterms:modified xsi:type="dcterms:W3CDTF">{timestamp}</dcterms:modified>
</cp:coreProperties>'''


def write_pptx(images: list[Path], out: Path, *, title: str, fit: str) -> None:
    out.parent.mkdir(parents=True, exist_ok=True)
    rels = [("rId1", f"{OD_REL}/slideMaster", "slideMasters/slideMaster1.xml")]
    rels.extend((f"rId{i + 1}", f"{OD_REL}/slide", f"slides/slide{i}.xml") for i in range(1, len(images) + 1))

    with zipfile.ZipFile(out, "w", compression=zipfile.ZIP_DEFLATED) as zf:
        zf.writestr("[Content_Types].xml", content_types_xml(len(images)))
        zf.writestr("_rels/.rels", rels_xml([
            ("rId1", f"{OD_REL}/officeDocument", "ppt/presentation.xml"),
            ("rId2", "http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties", "docProps/core.xml"),
            ("rId3", f"{OD_REL}/extended-properties", "docProps/app.xml"),
        ]))
        zf.writestr("docProps/app.xml", app_xml(len(images)))
        zf.writestr("docProps/core.xml", core_xml(title))
        zf.writestr("ppt/presentation.xml", presentation_xml(len(images)))
        zf.writestr("ppt/_rels/presentation.xml.rels", rels_xml(rels))
        zf.writestr("ppt/slideMasters/slideMaster1.xml", slide_master_xml())
        zf.writestr("ppt/slideMasters/_rels/slideMaster1.xml.rels", rels_xml([
            ("rId1", f"{OD_REL}/slideLayout", "../slideLayouts/slideLayout1.xml"),
            ("rId2", f"{OD_REL}/theme", "../theme/theme1.xml"),
        ]))
        zf.writestr("ppt/slideLayouts/slideLayout1.xml", slide_layout_xml())
        zf.writestr("ppt/slideLayouts/_rels/slideLayout1.xml.rels", rels_xml([
            ("rId1", f"{OD_REL}/slideMaster", "../slideMasters/slideMaster1.xml"),
        ]))
        zf.writestr("ppt/theme/theme1.xml", theme_xml())
        for idx, image in enumerate(images, start=1):
            zf.write(image, f"ppt/media/image{idx}.png")
            zf.writestr(f"ppt/slides/slide{idx}.xml", slide_xml(idx, image, fit))
            zf.writestr(f"ppt/slides/_rels/slide{idx}.xml.rels", rels_xml([
                ("rId1", f"{OD_REL}/slideLayout", "../slideLayouts/slideLayout1.xml"),
                ("rId2", f"{OD_REL}/image", f"../media/image{idx}.png"),
            ]))


def validate_zip(out: Path, slide_count: int) -> None:
    with zipfile.ZipFile(out) as zf:
        names = set(zf.namelist())
    required = {
        "[Content_Types].xml",
        "_rels/.rels",
        "ppt/presentation.xml",
        "ppt/slideMasters/slideMaster1.xml",
        "ppt/slideLayouts/slideLayout1.xml",
        "ppt/theme/theme1.xml",
    }
    missing = sorted(required - names)
    if missing:
        raise RuntimeError(f"invalid PPTX, missing parts: {missing}")
    for idx in range(1, slide_count + 1):
        for name in (f"ppt/slides/slide{idx}.xml", f"ppt/slides/_rels/slide{idx}.xml.rels", f"ppt/media/image{idx}.png"):
            if name not in names:
                raise RuntimeError(f"invalid PPTX, missing part: {name}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("source", help="Input .html, .htm, or .pdf")
    parser.add_argument("out", nargs="?", help="Output .pptx; defaults to source stem")
    parser.add_argument("--width", type=int, default=2048, help="Rendered slide image width in pixels")
    parser.add_argument("--fit", choices=["contain", "cover", "stretch"], default="contain", help="How to place images on 16:9 slides")
    parser.add_argument("--keep-shots", action="store_true", help="Keep rendered PNG files next to the output PPTX")
    args = parser.parse_args()

    source = Path(args.source).resolve()
    if not source.is_file():
        sys.exit(f"ERROR: file not found: {source}")
    out = Path(args.out).resolve() if args.out else source.with_suffix(".pptx")

    with tempfile.TemporaryDirectory(prefix="ptmaker_pptx_") as tmp_name:
        tmp = Path(tmp_name)
        images = render_source_to_pngs(source, tmp, args.width)
        if not images:
            sys.exit("ERROR: no slides were rendered")
        if args.keep_shots:
            shot_dir = out.with_suffix("")
            shot_dir = shot_dir.parent / f"{shot_dir.name}_pptx_shots"
            shot_dir.mkdir(parents=True, exist_ok=True)
            kept = []
            for image in images:
                target = shot_dir / image.name
                shutil.copyfile(image, target)
                kept.append(target)
            images = kept
        write_pptx(images, out, title=source.stem, fit=args.fit)
    validate_zip(out, len(images))
    print(f"OK: {out} ({len(images)} slides, image-based PPTX)")


if __name__ == "__main__":
    main()
