#!/usr/bin/env python3

from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import unittest
import zipfile
from pathlib import Path

import import_template


SCRIPT = Path(__file__).resolve().parent / "import_template.py"

NS = (
    'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
    'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
    'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"'
)
REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
OD = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
PNG = b"\x89PNG\r\n\x1a\n" + b"\x00" * 16
W, H = 12192000, 6858000  # 13.33 x 7.5 in; 1 px = 6350 EMU at 1920 wide


def rels(*items: tuple[str, str, str]) -> str:
    rows = "".join(f'<Relationship Id="{rid}" Type="{OD}/{kind}" Target="{target}"/>' for rid, kind, target in items)
    return f'<?xml version="1.0"?><Relationships xmlns="{REL_NS}">{rows}</Relationships>'


def xfrm(x: int, y: int, cx: int, cy: int) -> str:
    return f'<a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>'


def text_shape(x, y, cx, cy, paragraphs, ph="", fill="<a:noFill/>", color=""):
    runs = "".join(
        f'<a:p><a:r><a:rPr lang="en-US" sz="{size}">{color}<a:latin typeface="{face}"/></a:rPr><a:t>{text}</a:t></a:r></a:p>'
        for text, size, face in paragraphs
    )
    nv = f'<p:nvPr><p:ph type="{ph}"/></p:nvPr>' if ph else "<p:nvPr/>"
    return (
        f'<p:sp><p:nvSpPr><p:cNvPr id="9" name="t"/><p:cNvSpPr txBox="1"/>{nv}</p:nvSpPr>'
        f'<p:spPr>{xfrm(x, y, cx, cy)}<a:prstGeom prst="rect"><a:avLst/></a:prstGeom>{fill}</p:spPr>'
        f"<p:txBody><a:bodyPr/><a:lstStyle/>{runs}</p:txBody></p:sp>"
    )


def picture(rid, x, y, cx, cy, src_rect=""):
    crop = f"<a:srcRect {src_rect}/>" if src_rect else ""
    return (
        '<p:pic><p:nvPicPr><p:cNvPr id="5" name="pic"/><p:cNvPicPr/><p:nvPr/></p:nvPicPr>'
        f'<p:blipFill><a:blip r:embed="{rid}"/>{crop}<a:stretch/></p:blipFill>'
        f'<p:spPr>{xfrm(x, y, cx, cy)}<a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr></p:pic>'
    )


def shape(x, y, cx, cy, geom="rect", fill="", style=""):
    return (
        '<p:sp><p:nvSpPr><p:cNvPr id="7" name="s"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
        f'<p:spPr>{xfrm(x, y, cx, cy)}<a:prstGeom prst="{geom}"><a:avLst/></a:prstGeom>{fill}</p:spPr>{style}</p:sp>'
    )


def slide(body: str, bg: str = "") -> str:
    return (
        f'<?xml version="1.0"?><p:sld {NS}><p:cSld>{bg}<p:spTree>'
        '<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/>'
        f"{body}</p:spTree></p:cSld></p:sld>"
    )


GRADIENT = (
    '<a:gradFill><a:gsLst><a:gs pos="0"><a:srgbClr val="1B6EC2"/></a:gs>'
    '<a:gs pos="100000"><a:srgbClr val="E07A1F"/></a:gs></a:gsLst><a:lin ang="5400000"/></a:gradFill>'
)
THEME_FILL = '<p:style><a:lnRef idx="0"><a:schemeClr val="accent2"/></a:lnRef><a:fillRef idx="1"><a:schemeClr val="accent2"/></a:fillRef></p:style>'


def build_fixture(path: Path) -> None:
    """A four-slide 13.33-inch template, presented in an order unlike its file names.

    Opening: picture background (p:bg) and a full-height gradient bar on the left.
    Approach: master background, a filled title placeholder, a cropped logo, a rounded bar with a theme fill.
    Thank you: a full-slide picture (a background, not art).
    Findings: the title sits on a header band; also a group, a connector and an outline-only shape.
    """
    presentation = (
        f'<?xml version="1.0"?><p:presentation {NS}>'
        '<p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId1"/></p:sldMasterIdLst>'
        '<p:sldIdLst><p:sldId id="256" r:id="rId13"/><p:sldId id="257" r:id="rId11"/>'
        '<p:sldId id="258" r:id="rId12"/><p:sldId id="259" r:id="rId14"/></p:sldIdLst>'
        f'<p:sldSz cx="{W}" cy="{H}"/></p:presentation>'
    )
    master = (
        f'<?xml version="1.0"?><p:sldMaster {NS}><p:cSld>'
        '<p:bg><p:bgPr><a:solidFill><a:srgbClr val="F7F5F0"/></a:solidFill></p:bgPr></p:bg><p:spTree>'
        '<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/>'
        "</p:spTree></p:cSld>"
        '<p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" '
        'accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/>'
        '<p:txStyles><p:titleStyle><a:lvl1pPr><a:defRPr sz="3200"><a:solidFill><a:srgbClr val="0B3D91"/></a:solidFill></a:defRPr></a:lvl1pPr></p:titleStyle>'
        '<p:bodyStyle><a:lvl1pPr><a:defRPr sz="2000"/></a:lvl1pPr></p:bodyStyle>'
        '<p:otherStyle><a:lvl1pPr><a:defRPr sz="1200"/></a:lvl1pPr></p:otherStyle></p:txStyles></p:sldMaster>'
    )
    theme = (
        '<?xml version="1.0"?><a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="t">'
        '<a:themeElements><a:clrScheme name="c"><a:dk1><a:sysClr val="windowText" lastClr="222222"/></a:dk1>'
        '<a:lt1><a:srgbClr val="FFFFFF"/></a:lt1><a:accent1><a:srgbClr val="1B6EC2"/></a:accent1>'
        '<a:accent2><a:srgbClr val="E07A1F"/></a:accent2></a:clrScheme>'
        '<a:fontScheme name="f"><a:majorFont><a:latin typeface="Arial"/></a:majorFont>'
        '<a:minorFont><a:latin typeface="Arial"/></a:minorFont></a:fontScheme></a:themeElements></a:theme>'
    )
    layout = (
        f'<?xml version="1.0"?><p:sldLayout {NS}><p:cSld><p:spTree>'
        '<p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/>'
        "</p:spTree></p:cSld></p:sldLayout>"
    )
    opening = slide(
        shape(0, 0, 914400, H, fill=GRADIENT)
        + text_shape(1371600, 2286000, 9144000, 1371600, [("Opening", 4000, "Lato Bold"), ("Team:", 2000, "Lato")]),
        bg='<p:bg><p:bgPr><a:blipFill><a:blip r:embed="rId2"/><a:stretch/></a:blipFill></p:bgPr></p:bg>',
    )
    approach = slide(
        text_shape(457200, 457200, 11277600, 685800, [("Approach", 2800, "Lato")], ph="title",
                   fill='<a:solidFill><a:srgbClr val="EDEFF2"/></a:solidFill>')
        + picture("rId2", 10820400, 6172200, 1066800, 457200, 'l="25000" t="0" r="0" b="0"')
        + shape(0, 6553200, 6096000, 304800, geom="roundRect", style=THEME_FILL)
        + text_shape(457200, 5486400, 4572000, 457200, [("Note", 1200, "Lato")])
    )
    closing = slide(picture("rId2", 0, 0, W, H) + text_shape(1371600, 2743200, 9144000, 1143000, [("Thank you", 4400, "Lato")]))
    findings = slide(
        shape(0, 0, W, 914400, fill='<a:solidFill><a:schemeClr val="accent1"/></a:solidFill>')
        + text_shape(457200, 152400, 11277600, 609600, [("Findings", 2400, "Lato")],
                     color='<a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill>')
        + '<p:grpSp><p:nvGrpSpPr><p:cNvPr id="20" name="g"/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/></p:grpSp>'
        + '<p:cxnSp><p:nvCxnSpPr><p:cNvPr id="21" name="c"/><p:cNvCxnSpPr/><p:nvPr/></p:nvCxnSpPr><p:spPr/></p:cxnSp>'
        + shape(457200, 2286000, 4572000, 2286000, fill='<a:noFill/><a:ln><a:solidFill><a:srgbClr val="222222"/></a:solidFill></a:ln>')
    )
    slide_rels = rels(("rId1", "slideLayout", "../slideLayouts/slideLayout1.xml"), ("rId2", "image", "../media/image1.png"))
    with zipfile.ZipFile(path, "w") as z:
        z.writestr("[Content_Types].xml", "<Types/>")
        z.writestr("ppt/presentation.xml", presentation)
        z.writestr(
            "ppt/_rels/presentation.xml.rels",
            rels(
                ("rId1", "slideMaster", "slideMasters/slideMaster1.xml"),
                ("rId11", "slide", "slides/slide1.xml"),
                ("rId12", "slide", "slides/slide2.xml"),
                ("rId13", "slide", "slides/slide3.xml"),
                ("rId14", "slide", "slides/slide4.xml"),
            ),
        )
        z.writestr("ppt/slideMasters/slideMaster1.xml", master)
        z.writestr("ppt/slideMasters/_rels/slideMaster1.xml.rels", rels(("rId1", "theme", "../theme/theme1.xml")))
        z.writestr("ppt/theme/theme1.xml", theme)
        z.writestr("ppt/slideLayouts/slideLayout1.xml", layout)
        z.writestr("ppt/slideLayouts/_rels/slideLayout1.xml.rels", rels(("rId1", "slideMaster", "../slideMasters/slideMaster1.xml")))
        for name, body in (("slide1", approach), ("slide2", closing), ("slide3", opening), ("slide4", findings)):
            z.writestr(f"ppt/slides/{name}.xml", body)
            z.writestr(f"ppt/slides/_rels/{name}.xml.rels", slide_rels)
        z.writestr("ppt/media/image1.png", PNG)


class ImportTemplateTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.pptx = self.root / "template.pptx"
        build_fixture(self.pptx)
        self.out = self.root / "deck"
        self.data = import_template.import_template(self.pptx, self.out)
        self.slides = {entry["title"]: entry for entry in self.data["slides"]}

    def tearDown(self) -> None:
        self.tmp.cleanup()

    def test_size_page_and_minimum_font(self):
        self.assertEqual(self.data["slide_size"]["px"], [1920, 1080])
        self.assertEqual(self.data["slide_size"]["in"], [13.333, 7.5])
        self.assertEqual(self.data["min_font_pt"], 12.0)
        self.assertEqual(self.data["min_font_px"], 24.0)

    def test_titles_follow_presentation_order_and_default_to_exact(self):
        self.assertEqual([entry["title"] for entry in self.data["slides"]], ["Opening", "Approach", "Thank you", "Findings"])
        self.assertEqual([entry["match"] for entry in self.data["slides"]], ["exact"] * 4)
        self.assertIn("Team:", self.slides["Opening"]["prompts"])

    def test_picture_background_and_gradient_bar(self):
        opening = self.slides["Opening"]
        self.assertEqual([item["fill"]["kind"] for item in opening["background"]], ["image"])
        bar = opening["art"][0]
        self.assertEqual((bar["x"], bar["y"], bar["w"], bar["h"]), (0, 0, 144, 1080))
        self.assertEqual(bar["fill"]["kind"], "gradient")
        self.assertIn("linear-gradient(180deg, #1B6EC2 0%, #E07A1F 100%)", opening["layer_html"])
        self.assertIn('class="tart tbase"', opening["layer_html"])

    def test_master_background_filled_placeholder_logo_and_theme_fill(self):
        approach = self.slides["Approach"]
        kinds = [item["fill"].get("color") for item in approach["background"]]
        self.assertIn("#F7F5F0", kinds)  # inherited from the master
        self.assertIn("#EDEFF2", kinds)  # the filled title placeholder is drawn, not forbidden
        art = sorted(approach["art"], key=lambda item: item["x"])
        self.assertEqual(len(art), 2)
        bar, logo = art
        self.assertEqual((bar["y"], bar["w"], bar["h"]), (1032, 960, 48))
        self.assertEqual(bar["fill"], {"kind": "solid", "color": "#E07A1F"})
        self.assertIn("border-radius:8px", approach["layer_html"])
        self.assertEqual((logo["x"], logo["y"], logo["w"], logo["h"]), (1704, 972, 168, 72))
        self.assertIn("left:-56px", approach["layer_html"])
        self.assertIn("width:224px", approach["layer_html"])

    def test_full_slide_picture_is_background(self):
        closing = self.slides["Thank you"]
        self.assertEqual(closing["art"], [])
        self.assertIn("picture", [item["kind"] for item in closing["background"]])

    def test_art_under_the_title_is_drawn_below_content(self):
        findings = self.slides["Findings"]
        band = findings["art"][0]
        self.assertEqual((band["y"], band["h"], band["layer"]), (0, 144, "base"))
        box = findings["title_box"]
        self.assertEqual((box["y"], box["h"]), (24, 96))
        self.assertEqual(box["text_y"], 31.2)  # default top inset 45720 EMU
        self.assertEqual(box["color"], "#FFFFFF")
        self.assertEqual(box["font_px"], 48.0)
        self.assertEqual(self.slides["Approach"]["art"][0]["layer"], "top")
        self.assertEqual(self.slides["Approach"]["title_box"]["color"], "#0B3D91")  # the master's title style
        self.assertEqual(self.slides["Opening"]["title_box"]["color"], "#222222")  # a text box: theme text color (tx1 → dk1)

    def test_reimport_keeps_each_slot_match_mode(self):
        path = self.out / "template.json"
        data = json.loads(path.read_text(encoding="utf-8"))
        data["slides"][1]["match"] = "prefix"
        data["slides"][3]["match"] = "skip"
        path.write_text(json.dumps(data), encoding="utf-8")
        again = import_template.import_template(self.pptx, self.out)
        self.assertEqual([entry["match"] for entry in again["slides"]], ["exact", "prefix", "exact", "skip"])

    def test_skipped_parts_are_warned(self):
        warnings = " ".join(self.data["warnings"])
        for needle in ("grpSp", "cxnSp", "no fill"):
            self.assertIn(needle, warnings)

    def test_outputs(self):
        self.assertEqual(self.data["fonts"][0]["family"], "Lato")
        self.assertTrue((self.out / "assets" / "template" / "image1.png").is_file())
        css = (self.out / "template-layer.css").read_text(encoding="utf-8")
        self.assertIn("@page { size: 1920px 1080px; margin: 0; }", css)
        self.assertIn("isolation: isolate", css)
        self.assertIn(".tart.tbase { z-index: -1; }", css)
        saved = json.loads((self.out / "template.json").read_text(encoding="utf-8"))
        self.assertEqual(saved["slides"][1]["title"], "Approach")

    def test_other_output_width(self):
        data = import_template.import_template(self.pptx, self.root / "small", width=1280)
        self.assertEqual(data["slide_size"]["px"], [1280, 720])
        self.assertEqual(data["min_font_px"], 16.0)

    def test_cli_prints_summary_and_warnings(self):
        result = subprocess.run(
            [sys.executable, str(SCRIPT), str(self.pptx), str(self.root / "cli")],
            check=True,
            capture_output=True,
            text=True,
        )
        self.assertIn("1920x1080", result.stdout)
        self.assertIn("Findings", result.stdout)
        self.assertIn("warning:", result.stdout)
        self.assertTrue((self.root / "cli" / "template.json").is_file())


if __name__ == "__main__":
    unittest.main()
