#!/usr/bin/env python3
"""pt-maker judged mode: read a required .pptx template into a deck folder.

심사용 모드에서 지정 템플릿(.pptx)을 읽어 덱이 지켜야 할 값들을 뽑는다.

사용:
  python import_template.py template.pptx out_dir [--width 1920]

out_dir에 만드는 것:
  template.json        슬라이드 크기(px, 인치), 슬라이드별 배경·템플릿 아트 영역(px)·슬롯 제목과 제목 상자,
                       최소 글자 크기(px), 템플릿 글꼴, 슬라이드별 template layer HTML, 건너뛴 것(warnings)
  template-layer.css   @page 크기, .slide 크기, .tart(템플릿 아트) 기본 스타일
  assets/template/     템플릿이 쓰는 ppt/media 이미지 복사본

읽는 규칙:
  - 배경: 슬라이드 → 레이아웃 → 마스터 순으로 처음 나오는 p:bg(단색, 그라데이션, 그림),
    슬라이드 전체를 덮는 그림·도형, 채워진 placeholder(제목 상자 등). 내용 아래에 깔고 겹침 검사는 하지 않는다.
  - 템플릿 아트(겹치면 안 되는 영역): 슬라이드·레이아웃·마스터의 그림(srcRect crop 반영)과 채워진 도형
    (도형 모양과 상관없이; 단색, 그라데이션, 그림 채우기, p:style 테마 채우기).
    템플릿 제목 상자와 겹치는 아트는 제목 아래(layer "base")에 그려, 제목이 그 위에 올라갈 수 있다.
  - 최소 글자 크기: 슬라이드와 그 레이아웃·마스터에 쓰인 가장 작은 sz(pt)를 출력 폭 기준 px로 바꾼 값.
  - 그룹, 표·차트(graphicFrame), 연결선(cxnSp), 채우기 없는 도형, 회전, 색 보정은 warnings에 남긴다.

표준 라이브러리(zipfile + xml.etree)만 사용한다.
"""

from __future__ import annotations

import argparse
import json
import posixpath
import re
import sys
import xml.etree.ElementTree as ET
import zipfile
from collections import Counter
from pathlib import Path
from typing import Any

A = "http://schemas.openxmlformats.org/drawingml/2006/main"
P = "http://schemas.openxmlformats.org/presentationml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PKG = "http://schemas.openxmlformats.org/package/2006/relationships"
NS = {"a": A, "p": P, "r": R}

EMU_PER_PT = 12700
EMU_PER_IN = 914400
DEFAULT_INSET_X = 91440  # bodyPr lIns/rIns default
DEFAULT_INSET_Y = 45720  # bodyPr tIns/bIns default
FULL_SLIDE = 0.98
WEIGHT_RE = re.compile(r"\s+(?:Thin|Light|Regular|Medium|SemiBold|Bold|ExtraBold|Black)$")
COLOR_MODIFIERS = {"lumMod", "lumOff", "tint", "shade", "alpha", "satMod", "hueMod"}
FILL_TAGS = ("noFill", "solidFill", "gradFill", "blipFill", "pattFill")


class TemplateError(RuntimeError):
    """Raised when the .pptx cannot be read as a template."""


def q(prefix: str, name: str) -> str:
    return f"{{{NS[prefix]}}}{name}"


def local(element: ET.Element) -> str:
    return element.tag.split("}")[1]


def r2(value: float) -> float:
    rounded = round(value + 0.0, 2)
    return int(rounded) if rounded == int(rounded) else rounded


class Package:
    def __init__(self, path: Path) -> None:
        try:
            self.zip = zipfile.ZipFile(path)
        except zipfile.BadZipFile as exc:
            raise TemplateError(f"not a .pptx (zip) file: {path}") from exc
        self.names = set(self.zip.namelist())

    def xml(self, part: str) -> ET.Element:
        if part not in self.names:
            raise TemplateError(f"missing part in .pptx: {part}")
        return ET.fromstring(self.zip.read(part))

    def rels(self, part: str) -> dict[str, tuple[str, str]]:
        """rId -> (type suffix, absolute part name)."""
        folder, name = posixpath.split(part)
        rels_part = posixpath.join(folder, "_rels", name + ".rels")
        if rels_part not in self.names:
            return {}
        result: dict[str, tuple[str, str]] = {}
        for rel in ET.fromstring(self.zip.read(rels_part)).iter(f"{{{PKG}}}Relationship"):
            if rel.get("TargetMode") == "External":
                continue
            target = rel.get("Target", "")
            resolved = target.lstrip("/") if target.startswith("/") else posixpath.normpath(posixpath.join(folder, target))
            result[rel.get("Id", "")] = (rel.get("Type", "").rsplit("/", 1)[-1], resolved)
        return result

    def first_rel(self, part: str, kind: str) -> str | None:
        for rel_kind, target in self.rels(part).values():
            if rel_kind == kind:
                return target
        return None


class Theme:
    def __init__(self, pkg: Package, master_part: str) -> None:
        self.colors: dict[str, str] = {}
        self.fonts: dict[str, str] = {}
        theme_part = pkg.first_rel(master_part, "theme")
        if theme_part and theme_part in pkg.names:
            theme = pkg.xml(theme_part)
            scheme = theme.find(".//a:clrScheme", NS)
            for child in scheme if scheme is not None else []:
                for value in child:
                    hex_value = value.get("val") if value.tag == q("a", "srgbClr") else value.get("lastClr")
                    if hex_value:
                        self.colors[local(child)] = "#" + hex_value.upper()
            for kind in ("majorFont", "minorFont"):
                latin = theme.find(f".//a:{kind}/a:latin", NS)
                if latin is not None and latin.get("typeface"):
                    self.fonts[kind.replace("Font", "")] = latin.get("typeface", "")
        clr_map = pkg.xml(master_part).find("p:clrMap", NS)
        self.clr_map = dict(clr_map.attrib) if clr_map is not None else {}

    def color(self, holder: ET.Element | None, warnings: list[str], where: str) -> str | None:
        """Resolve the first color child of holder (a fill, a gradient stop, a style ref)."""
        for value in holder if holder is not None else []:
            tag = local(value)
            if tag not in ("srgbClr", "sysClr", "schemeClr", "prstClr"):
                continue
            if any(local(child) in COLOR_MODIFIERS for child in value):
                warnings.append(f"{where}: color modifiers ignored")
            if tag == "srgbClr":
                return "#" + value.get("val", "").upper()
            if tag == "sysClr":
                return "#" + value.get("lastClr", "").upper()
            if tag == "schemeClr":
                name = value.get("val", "")
                return self.colors.get(self.clr_map.get(name, name))
            warnings.append(f"{where}: preset color {value.get('val')} not resolved")
        return None


class Importer:
    def __init__(self, pptx: Path, width: int) -> None:
        self.pptx = pptx
        self.pkg = Package(pptx)
        self.warnings: list[str] = []
        pres = self.pkg.xml("ppt/presentation.xml")
        size = pres.find("p:sldSz", NS)
        if size is None:
            raise TemplateError("ppt/presentation.xml has no p:sldSz")
        self.cx = int(size.get("cx", "0"))
        self.cy = int(size.get("cy", "0"))
        if not self.cx or not self.cy:
            raise TemplateError("slide size is zero")
        self.width = width
        self.height = round(width * self.cy / self.cx)
        self.scale = width / self.cx
        self.px_per_pt = width / (self.cx / EMU_PER_PT)
        pres_rels = self.pkg.rels("ppt/presentation.xml")
        self.slide_parts = [
            pres_rels[sld.get(q("r", "id"), "")][1]
            for sld in pres.iterfind("p:sldIdLst/p:sldId", NS)
            if sld.get(q("r", "id"), "") in pres_rels
        ]
        if not self.slide_parts:
            raise TemplateError("the template has no slides")
        self.media: dict[str, str] = {}

    def px(self, emu: float) -> float:
        return emu * self.scale

    def media_path(self, part: str, rid: str) -> str | None:
        rels = self.pkg.rels(part)
        if rid not in rels:
            return None
        name = posixpath.basename(rels[rid][1])
        self.media[name] = rels[rid][1]
        return f"assets/template/{name}"

    def fill(self, holder: ET.Element | None, style: ET.Element | None, theme: Theme, part: str, where: str) -> dict[str, Any] | None:
        """A fill from spPr/bgPr children, or the p:style theme fill. None means no fill."""
        found = None
        for child in holder if holder is not None else []:
            if local(child) in FILL_TAGS:
                found = child
                break
        if found is None and style is not None:
            ref = style.find("a:fillRef", NS)
            if ref is not None and ref.get("idx", "0") not in ("0", "1000"):
                if ref.get("idx") != "1":
                    self.warnings.append(f"{where}: theme fill style {ref.get('idx')} drawn as its base color")
                color = theme.color(ref, self.warnings, where)
                return {"kind": "solid", "color": color} if color else None
            return None
        if found is None or local(found) == "noFill":
            return None
        kind = local(found)
        if kind == "solidFill":
            return {"kind": "solid", "color": theme.color(found, self.warnings, where)}
        if kind == "pattFill":
            self.warnings.append(f"{where}: pattern fill drawn as its foreground color")
            return {"kind": "solid", "color": theme.color(found.find("a:fgClr", NS), self.warnings, where)}
        if kind == "gradFill":
            stops = [
                [round(int(gs.get("pos", "0")) / 1000), theme.color(gs, self.warnings, where)]
                for gs in found.iterfind("a:gsLst/a:gs", NS)
            ]
            lin = found.find("a:lin", NS)
            if lin is None:
                self.warnings.append(f"{where}: non-linear gradient drawn as linear")
            angle = (int(lin.get("ang", "0")) / 60000 if lin is not None else 0) + 90
            return {"kind": "gradient", "angle": r2(angle % 360), "stops": stops}
        blip = found.find("a:blip", NS)
        media = self.media_path(part, blip.get(q("r", "embed"), "")) if blip is not None else None
        return {"kind": "image", "media": media} if media else None

    def box(self, x: float, y: float, cx: float, cy: float) -> dict[str, Any]:
        return {"x": r2(self.px(x)), "y": r2(self.px(y)), "w": r2(self.px(cx)), "h": r2(self.px(cy))}

    def clipped(self, box: dict[str, Any]) -> dict[str, Any] | None:
        left, top = max(0.0, box["x"]), max(0.0, box["y"])
        right, bottom = min(float(self.width), box["x"] + box["w"]), min(float(self.height), box["y"] + box["h"])
        if right - left <= 0 or bottom - top <= 0:
            return None
        return {"x": r2(left), "y": r2(top), "w": r2(right - left), "h": r2(bottom - top)}

    def full_slide(self, x: int, y: int, cx: int, cy: int) -> bool:
        return cx >= FULL_SLIDE * self.cx and cy >= FULL_SLIDE * self.cy and x <= 0.01 * self.cx and y <= 0.01 * self.cy

    def background(self, parts: list[str], theme: Theme) -> dict[str, Any] | None:
        for part in parts:
            bg = self.pkg.xml(part).find("p:cSld/p:bg", NS)
            if bg is None:
                continue
            where = f"background of {part}"
            bg_pr = bg.find("p:bgPr", NS)
            if bg_pr is not None:
                fill = self.fill(bg_pr, None, theme, part, where)
            else:
                ref = bg.find("p:bgRef", NS)
                color = theme.color(ref, self.warnings, where)
                fill = {"kind": "solid", "color": color} if color else None
                if fill is None:
                    self.warnings.append(f"{where}: theme background not resolved")
            if fill:
                return {"kind": "background", "fill": fill, "box": self.box(0, 0, self.cx, self.cy), "geom": "rect"}
            return None
        return None

    def shapes(self, part: str, theme: Theme, label: str) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
        """(background pieces, art pieces) from one part's shape tree."""
        tree = self.pkg.xml(part).find("p:cSld/p:spTree", NS)
        backgrounds: list[dict[str, Any]] = []
        art: list[dict[str, Any]] = []
        for shape in tree if tree is not None else []:
            tag = local(shape)
            if tag in ("grpSp", "graphicFrame", "cxnSp", "contentPart"):
                self.warnings.append(f"{label}: {tag} skipped (not read as template art)")
                continue
            if tag not in ("pic", "sp"):
                continue
            frame = shape.find("p:spPr/a:xfrm", NS)
            off = frame.find("a:off", NS) if frame is not None else None
            ext = frame.find("a:ext", NS) if frame is not None else None
            if off is None or ext is None:
                continue
            x, y = int(off.get("x", "0")), int(off.get("y", "0"))
            cx, cy = int(ext.get("cx", "0")), int(ext.get("cy", "0"))
            if frame.get("rot", "0") != "0":
                self.warnings.append(f"{label}: rotated {tag} read without rotation")
            geom_el = shape.find("p:spPr/a:prstGeom", NS)
            geom = geom_el.get("prst", "rect") if geom_el is not None else "rect"
            placeholder = shape.find("./*/p:nvPr/p:ph", NS) is not None
            if tag == "pic":
                blip = shape.find("p:blipFill/a:blip", NS)
                media = self.media_path(part, blip.get(q("r", "embed"), "")) if blip is not None else None
                if not media:
                    self.warnings.append(f"{label}: picture without an image skipped")
                    continue
                crop_el = shape.find("p:blipFill/a:srcRect", NS)
                crop = {s: int(crop_el.get(s, "0")) / 100000 if crop_el is not None else 0.0 for s in ("l", "t", "r", "b")}
                item = {"kind": "picture", "fill": {"kind": "image", "media": media}, "crop": crop}
            else:
                fill = self.fill(shape.find("p:spPr", NS), shape.find("p:style", NS), theme, part, label)
                if fill is None:
                    has_text = bool("".join(t.text or "" for t in shape.iter(q("a", "t"))).strip())
                    if not has_text and not placeholder:
                        self.warnings.append(f"{label}: {geom} shape with no fill skipped")
                    continue
                item = {"kind": "shape", "fill": fill}
            if geom not in ("rect", "roundRect", "ellipse"):
                self.warnings.append(f"{label}: {geom} drawn as a rectangle")
            item.update({"geom": geom, "box": self.box(x, y, cx, cy), "from": label.split(" ")[0]})
            adj = shape.find("p:spPr/a:prstGeom/a:avLst/a:gd", NS)
            if geom == "roundRect":
                value = int(adj.get("fmla", "val 16667").split()[-1]) if adj is not None else 16667
                item["radius"] = r2(value / 100000 * min(self.px(cx), self.px(cy)))
            if placeholder or self.full_slide(x, y, cx, cy):
                backgrounds.append(item)
                continue
            zone = self.clipped(item["box"])
            if zone is None:
                continue
            item.update(zone)
            art.append(item)
        return backgrounds, art

    def title_of(self, part: str, theme: Theme) -> tuple[str, list[str], dict[str, Any] | None]:
        tree = self.pkg.xml(part).find("p:cSld/p:spTree", NS)
        shapes = []
        for shape in tree.iterfind("p:sp", NS) if tree is not None else []:
            frame = shape.find("p:spPr/a:xfrm", NS)
            paras = []
            for para in shape.iter(q("a", "p")):
                text = "".join(
                    (node.text or "") if node.tag == q("a", "t") else " "
                    for node in para.iter()
                    if node.tag in (q("a", "t"), q("a", "br"))
                ).strip()
                if text:
                    run = para.find(".//a:rPr", NS)
                    paras.append({"text": re.sub(r"\s+", " ", text), "run": run})
            if paras and frame is not None and frame.find("a:off", NS) is not None:
                off, ext = frame.find("a:off", NS), frame.find("a:ext", NS)
                geometry = tuple(int(v) for v in (off.get("x", "0"), off.get("y", "0"), ext.get("cx", "0"), ext.get("cy", "0")))
                shapes.append((geometry, shape, paras))
        shapes.sort(key=lambda entry: (entry[0][1], entry[0][0]))
        chosen = next(
            (entry for entry in shapes if (ph := entry[1].find("./*/p:nvPr/p:ph", NS)) is not None and ph.get("type") in ("title", "ctrTitle")),
            shapes[0] if shapes else None,
        )
        if chosen is None:
            return "", [], None
        (x, y, cx, cy), shape, paras = chosen
        title = paras[0]
        prompts = [p["text"] for _, other, other_paras in shapes for p in other_paras if not (other is shape and p is title)]
        body = shape.find("p:txBody/a:bodyPr", NS)
        attrs = body.attrib if body is not None else {}
        run = title["run"]
        size = int(run.get("sz")) if run is not None and run.get("sz") else None
        latin = run.find("a:latin", NS) if run is not None else None
        title_box = self.box(x, y, cx, cy)
        title_box.update(
            {
                "text_x": r2(self.px(x + int(attrs.get("lIns", DEFAULT_INSET_X)))),
                "text_y": r2(self.px(y + int(attrs.get("tIns", DEFAULT_INSET_Y)))),
                "font_px": r2(size / 100 * self.px_per_pt) if size else None,
                "font": latin.get("typeface") if latin is not None else None,
                "color": (theme.color(run.find("a:solidFill", NS), self.warnings, part) if run is not None else None)
                or theme.colors.get(theme.clr_map.get("tx1", "dk1")),
            }
        )
        return title["text"], prompts, title_box

    def run(self) -> dict[str, Any]:
        slides = []
        sizes: list[int] = []
        faces: list[str] = []
        seen_parts: set[str] = set()
        theme_fonts: dict[str, str] = {}
        for index, part in enumerate(self.slide_parts, start=1):
            layout = self.pkg.first_rel(part, "slideLayout")
            master = self.pkg.first_rel(layout, "slideMaster") if layout else None
            if not master:
                raise TemplateError(f"{part} has no slide layout or master")
            theme = Theme(self.pkg, master)
            theme_fonts = theme_fonts or theme.fonts
            slide_root, layout_root = self.pkg.xml(part), self.pkg.xml(layout)
            parts = [(part, f"slide {index}")]
            if slide_root.get("showMasterSp") != "0":
                parts.insert(0, (layout, f"layout of slide {index}"))
                if layout_root.get("showMasterSp") != "0":
                    parts.insert(0, (master, f"master of slide {index}"))
            background: list[dict[str, Any]] = []
            bg = self.background([part, layout, master], theme)
            if bg:
                background.append(bg)
            art: list[dict[str, Any]] = []
            for source, label in parts:
                found_bg, found_art = self.shapes(source, theme, label)
                background.extend(found_bg)
                art.extend(found_art)
            for source in (part, layout, master):
                if source not in seen_parts:
                    seen_parts.add(source)
                    sizes.extend(
                        int(el.get("sz", "0"))
                        for el in self.pkg.xml(source).iter()
                        if el.tag in (q("a", "rPr"), q("a", "defRPr"), q("a", "endParaRPr")) and el.get("sz")
                    )
            faces.extend(
                latin.get("typeface", "")
                for el in slide_root.iter()
                if el.tag in (q("a", "rPr"), q("a", "endParaRPr"))
                for latin in el.iterfind("a:latin", NS)
                if not latin.get("typeface", "+").startswith("+")
            )
            title, prompts, title_box = self.title_of(part, theme)
            for item in art:
                item["layer"] = "base" if title_box and overlaps(item, title_box) else "top"
            slides.append(
                {
                    "index": index,
                    "part": part,
                    "title": title,
                    "match": "exact",
                    "prompts": prompts,
                    "title_box": title_box,
                    "background": background,
                    "art": art,
                    "layer_html": layer_html(background, art),
                }
            )
        if not sizes:
            raise TemplateError("no text sizes (sz) found in the template")
        min_pt = min(sizes) / 100
        families = Counter(WEIGHT_RE.sub("", face) for face in faces)
        return {
            "source": self.pptx.name,
            "slide_size": {
                "emu": [self.cx, self.cy],
                "px": [self.width, self.height],
                "in": [round(self.cx / EMU_PER_IN, 3), round(self.cy / EMU_PER_IN, 3)],
            },
            "px_per_pt": r2(self.px_per_pt),
            "min_font_pt": min_pt,
            "min_font_px": r2(min_pt * self.px_per_pt),
            "fonts": [{"family": family, "uses": uses} for family, uses in families.most_common()],
            "theme_fonts": theme_fonts,
            "slides": slides,
            "warnings": sorted(set(self.warnings)),
        }


def overlaps(item: dict[str, Any], box: dict[str, Any]) -> bool:
    return item["x"] < box["x"] + box["w"] and item["x"] + item["w"] > box["x"] and item["y"] < box["y"] + box["h"] and item["y"] + item["h"] > box["y"]


def style(**values: Any) -> str:
    return ";".join(
        f"{key.replace('_', '-')}:{value:g}px" if isinstance(value, (int, float)) else f"{key.replace('_', '-')}:{value}"
        for key, value in values.items()
    )


def paint(fill: dict[str, Any]) -> str:
    if fill["kind"] == "solid":
        return f"background:{fill['color'] or 'transparent'}"
    if fill["kind"] == "gradient":
        stops = ", ".join(f"{color or 'transparent'} {pos}%" for pos, color in fill["stops"])
        return f"background:linear-gradient({fill['angle']:g}deg, {stops})"
    return f"background:url({fill['media']}) center / 100% 100% no-repeat"


def piece_html(item: dict[str, Any], base: bool) -> str:
    box = item["box"]
    cls = "tart tbase" if base else "tart"
    geometry = style(left=box["x"], top=box["y"], width=box["w"], height=box["h"])
    if item.get("geom") == "ellipse":
        geometry += ";border-radius:50%"
    elif item.get("radius"):
        geometry += f";border-radius:{item['radius']:g}px"
    crop = item.get("crop") or {}
    if item["kind"] != "picture":
        return f'<div class="{cls}" style="{geometry};{paint(item["fill"])}"></div>'
    if not any(crop.values()):
        return f'<img class="{cls}" src="{item["fill"]["media"]}" alt="" style="{geometry}">'
    full_w = box["w"] / max(1e-6, 1 - crop["l"] - crop["r"])
    full_h = box["h"] / max(1e-6, 1 - crop["t"] - crop["b"])
    inner = style(left=r2(-crop["l"] * full_w), top=r2(-crop["t"] * full_h), width=r2(full_w), height=r2(full_h))
    return (
        f'<div class="{cls}" style="{geometry};overflow:hidden">'
        f'<img src="{item["fill"]["media"]}" alt="" style="position:absolute;{inner}"></div>'
    )


def layer_html(background: list[dict[str, Any]], art: list[dict[str, Any]]) -> str:
    """Backgrounds and art under the title go below the content; other art goes on top of it."""
    return "".join(piece_html(item, True) for item in background) + "".join(
        piece_html(item, item.get("layer") == "base") for item in art
    )


def layer_css(data: dict[str, Any]) -> str:
    width, height = data["slide_size"]["px"]
    return "\n".join(
        [
            f"/* Generated by import_template.py from {data['source']}. Re-run the import instead of editing. */",
            f"@page {{ size: {width}px {height}px; margin: 0; }}",
            f".slide {{ position: relative; width: {width}px; height: {height}px; overflow: hidden; isolation: isolate; }}",
            ".tart { position: absolute; display: block; z-index: 3; pointer-events: none; }",
            ".tart.tbase { z-index: -1; }",
        ]
    ) + "\n"


def import_template(pptx: Path, out_dir: Path, *, width: int = 1920) -> dict[str, Any]:
    importer = Importer(Path(pptx), width)
    data = importer.run()
    out_dir = Path(out_dir)
    media_dir = out_dir / "assets" / "template"
    media_dir.mkdir(parents=True, exist_ok=True)
    for name, part in importer.media.items():
        (media_dir / name).write_bytes(importer.pkg.zip.read(part))
    (out_dir / "template.json").write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out_dir / "template-layer.css").write_text(layer_css(data), encoding="utf-8")
    return data


def summary(data: dict[str, Any]) -> str:
    width, height = data["slide_size"]["px"]
    inches = data["slide_size"]["in"]
    lines = [
        f"template: {data['source']} → {width}x{height} px ({inches[0]:g} x {inches[1]:g} in), {len(data['slides'])} slides",
        f"min font: {data['min_font_pt']:g} pt = {data['min_font_px']:g} px",
        "fonts: " + (", ".join(f"{f['family']} ({f['uses']})" for f in data["fonts"]) or "none named"),
    ]
    for entry in data["slides"]:
        zones = ", ".join(f"{item['kind']} {item['y']:g}–{item['y'] + item['h']:g}" for item in entry["art"])
        lines.append(
            f"{entry['index']:02d} {entry['title'] or '(no title)'} | art: {zones or 'none'} | background: {len(entry['background'])}"
        )
    lines.extend(f"warning: {warning}" for warning in data["warnings"])
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("pptx", type=Path)
    parser.add_argument("out_dir", type=Path)
    parser.add_argument("--width", type=int, default=1920, help="output slide width in px (default 1920)")
    args = parser.parse_args()
    if not args.pptx.is_file():
        print(f"ERROR: file not found: {args.pptx}", file=sys.stderr)
        return 2
    try:
        data = import_template(args.pptx, args.out_dir, width=args.width)
    except (TemplateError, ET.ParseError, KeyError, ValueError) as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 2
    print(summary(data))
    print(args.out_dir / "template.json")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
