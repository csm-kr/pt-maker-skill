#!/usr/bin/env python3
"""Write the neutral synthetic judged-deck template "샘플 심사 템플릿" (.pptx) with zipfile only.

It stands in for a contest's required template in the pt-maker judged example. It is not any real
contest's template: a plain 16:9 (13.333 x 7.5 in) file with one cover slot and ten content slots. Every
slot has the same 120 px header band that carries the slot title, and a thin bottom bar.

Adapted from the pt-maker review's tools/make_pptx.py, made into a complete package that
PowerPoint, Keynote and Quick Look can open (content types, theme with format scheme, docProps).

Usage: python3 make_template.py out.pptx
"""
import sys
import zipfile
from xml.sax.saxutils import escape

NS = (
    'xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
    'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
    'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"'
)
REL_NS = "http://schemas.openxmlformats.org/package/2006/relationships"
OD = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
XML = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'

W, H = 12192000, 6858000          # 13.333 x 7.5 in; 1 px at 1920 wide = 6350 EMU
PX = 6350
BAND = "22303C"                   # header and cover band (dark slate)
BAR = "4A7C99"                    # thin bottom bar (steel blue)
TITLE_ON_BAND = "F4F6F8"          # slot title color on the band
FONT_LATIN, FONT_EA = "Arial", "Malgun Gothic"

# Story order: problem and message, then (1) what was shown and how the numbers check out, then (2) what is still a promise.
SLOTS = ["표지", "문제", "핵심 주장", "무엇을 보여줬나", "숫자 검증", "무엇을 약속했나", "일정", "한계", "결론", "출처", "감사"]


def rels(*items):
    rows = "".join(f'<Relationship Id="{i}" Type="{OD}/{k}" Target="{t}"/>' for i, k, t in items)
    return f'{XML}<Relationships xmlns="{REL_NS}">{rows}</Relationships>'


def rect(shape_id, name, x, y, cx, cy, color):
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{shape_id}" name="{name}"/><p:cNvSpPr/><p:nvPr/></p:nvSpPr>'
            f'<p:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm>'
            f'<a:prstGeom prst="rect"><a:avLst/></a:prstGeom><a:solidFill><a:srgbClr val="{color}"/></a:solidFill>'
            '<a:ln><a:noFill/></a:ln></p:spPr></p:sp>')


def title(shape_id, text, x, y, cx, cy, size=2000, color=TITLE_ON_BAND):
    return (f'<p:sp><p:nvSpPr><p:cNvPr id="{shape_id}" name="Title {shape_id}"/>'
            '<p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr><p:nvPr><p:ph type="title"/></p:nvPr></p:nvSpPr>'
            f'<p:spPr><a:xfrm><a:off x="{x}" y="{y}"/><a:ext cx="{cx}" cy="{cy}"/></a:xfrm></p:spPr>'
            '<p:txBody><a:bodyPr anchor="ctr"/><a:lstStyle/><a:p>'
            f'<a:r><a:rPr lang="ko-KR" sz="{size}" b="0"><a:solidFill><a:srgbClr val="{color}"/></a:solidFill>'
            f'<a:latin typeface="{FONT_LATIN}"/><a:ea typeface="{FONT_EA}"/></a:rPr><a:t>{escape(text)}</a:t></a:r>'
            '</a:p></p:txBody></p:sp>')


def tree(body):
    return ('<p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>'
            '<p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/>'
            f'<a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>{body}</p:spTree>')


def slide(body):
    return (f'{XML}<p:sld {NS}><p:cSld>{tree(body)}</p:cSld>'
            '<p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>')


def theme():
    colors = {"dk1": "1C1F23", "lt1": "FFFFFF", "dk2": BAND, "lt2": "EEF1F4", "accent1": BAR, "accent2": "8A9AA8",
              "accent3": "5E6670", "accent4": "B8C3CD", "accent5": "2E5A73", "accent6": "C9D1DA",
              "hlink": "2E5A73", "folHlink": "5E6670"}
    scheme = "".join(
        f'<a:{k}><a:sysClr val="{"windowText" if k == "dk1" else "window"}" lastClr="{v}"/></a:{k}>'
        if k in ("dk1", "lt1") else f'<a:{k}><a:srgbClr val="{v}"/></a:{k}>'
        for k, v in colors.items())
    font = f'<a:latin typeface="{FONT_LATIN}"/><a:ea typeface="{FONT_EA}"/><a:cs typeface=""/>'
    solid = '<a:solidFill><a:schemeClr val="phClr"/></a:solidFill>'
    line = lambda w: f'<a:ln w="{w}"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln>'
    return (f'{XML}<a:theme xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" name="Sample judged">'
            f'<a:themeElements><a:clrScheme name="Sample judged">{scheme}</a:clrScheme>'
            f'<a:fontScheme name="Sample judged"><a:majorFont>{font}</a:majorFont><a:minorFont>{font}</a:minorFont></a:fontScheme>'
            '<a:fmtScheme name="Sample judged">'
            f'<a:fillStyleLst>{solid * 3}</a:fillStyleLst>'
            f'<a:lnStyleLst>{line(6350)}{line(12700)}{line(19050)}</a:lnStyleLst>'
            '<a:effectStyleLst>' + '<a:effectStyle><a:effectLst/></a:effectStyle>' * 3 + '</a:effectStyleLst>'
            f'<a:bgFillStyleLst>{solid * 3}</a:bgFillStyleLst>'
            '</a:fmtScheme></a:themeElements><a:objectDefaults/><a:extraClrSchemeLst/></a:theme>')


def master():
    lvl = lambda sz: f'<a:lvl1pPr><a:defRPr sz="{sz}"><a:latin typeface="+mn-lt"/><a:ea typeface="+mn-ea"/></a:defRPr></a:lvl1pPr>'
    return (f'{XML}<p:sldMaster {NS}><p:cSld><p:bg><p:bgPr><a:solidFill><a:srgbClr val="FFFFFF"/></a:solidFill>'
            f'<a:effectLst/></p:bgPr></p:bg>{tree("")}</p:cSld>'
            '<p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" '
            'accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/>'
            '<p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst>'
            f'<p:txStyles><p:titleStyle>{lvl(2000)}</p:titleStyle><p:bodyStyle>{lvl(1800)}</p:bodyStyle>'
            f'<p:otherStyle>{lvl(1200)}</p:otherStyle></p:txStyles></p:sldMaster>')


def layout():
    return (f'{XML}<p:sldLayout {NS} type="titleOnly" preserve="1"><p:cSld name="Title Only">{tree("")}</p:cSld>'
            '<p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sldLayout>')


def slides():
    out = []
    bar = rect(3, "Bottom bar", 0, 1056 * PX, W, 24 * PX, BAR)
    # Every slot, the cover included: a 120 px header band with the slot title on it, and the bottom bar.
    for name in SLOTS:
        out.append(slide(rect(2, "Header band", 0, 0, W, 120 * PX, BAND) + bar
                         + title(4, name, 96 * PX, 30 * PX, 1728 * PX, 60 * PX)))
    return out


def build(path):
    body = slides()
    n = len(body)
    ids = "".join(f'<p:sldId id="{256 + i}" r:id="rId{10 + i}"/>' for i in range(n))
    pres = (f'{XML}<p:presentation {NS} saveSubsetFonts="1"><p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId1"/>'
            f'</p:sldMasterIdLst><p:sldIdLst>{ids}</p:sldIdLst><p:sldSz cx="{W}" cy="{H}"/>'
            '<p:notesSz cx="6858000" cy="9144000"/><p:defaultTextStyle/></p:presentation>')
    overrides = [
        ("/ppt/presentation.xml", "application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"),
        ("/ppt/slideMasters/slideMaster1.xml", "application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"),
        ("/ppt/slideLayouts/slideLayout1.xml", "application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"),
        ("/ppt/theme/theme1.xml", "application/vnd.openxmlformats-officedocument.theme+xml"),
        ("/ppt/presProps.xml", "application/vnd.openxmlformats-officedocument.presentationml.presProps+xml"),
        ("/ppt/viewProps.xml", "application/vnd.openxmlformats-officedocument.presentationml.viewProps+xml"),
        ("/ppt/tableStyles.xml", "application/vnd.openxmlformats-officedocument.presentationml.tableStyles+xml"),
        ("/docProps/core.xml", "application/vnd.openxmlformats-package.core-properties+xml"),
        ("/docProps/app.xml", "application/vnd.openxmlformats-officedocument.extended-properties+xml"),
    ] + [(f"/ppt/slides/slide{i + 1}.xml", "application/vnd.openxmlformats-officedocument.presentationml.slide+xml") for i in range(n)]
    types = (f'{XML}<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
             '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
             '<Default Extension="xml" ContentType="application/xml"/>'
             + "".join(f'<Override PartName="{p}" ContentType="{t}"/>' for p, t in overrides) + "</Types>")
    core = (f'{XML}<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
            'xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" '
            'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
            '<dc:title>샘플 심사 템플릿</dc:title><dc:creator>pt-maker sample</dc:creator>'
            '<dc:description>Neutral synthetic judged-deck template for the pt-maker example. Not any real contest template.</dc:description>'
            '<dcterms:created xsi:type="dcterms:W3CDTF">2026-10-19T00:00:00Z</dcterms:created></cp:coreProperties>')
    app = (f'{XML}<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties">'
           f'<Application>pt-maker sample</Application><Slides>{n}</Slides></Properties>')
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", types)
        core_type = "http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties"
        z.writestr("_rels/.rels", (
            f'{XML}<Relationships xmlns="{REL_NS}">'
            f'<Relationship Id="rId1" Type="{OD}/officeDocument" Target="ppt/presentation.xml"/>'
            f'<Relationship Id="rId2" Type="{core_type}" Target="docProps/core.xml"/>'
            f'<Relationship Id="rId3" Type="{OD}/extended-properties" Target="docProps/app.xml"/></Relationships>'))
        z.writestr("docProps/core.xml", core)
        z.writestr("docProps/app.xml", app)
        z.writestr("ppt/presentation.xml", pres)
        z.writestr("ppt/_rels/presentation.xml.rels", rels(
            ("rId1", "slideMaster", "slideMasters/slideMaster1.xml"),
            ("rId2", "theme", "theme/theme1.xml"),
            ("rId3", "presProps", "presProps.xml"),
            ("rId4", "viewProps", "viewProps.xml"),
            ("rId5", "tableStyles", "tableStyles.xml"),
            *[(f"rId{10 + i}", "slide", f"slides/slide{i + 1}.xml") for i in range(n)]))
        z.writestr("ppt/presProps.xml", f"{XML}<p:presentationPr {NS}/>")
        z.writestr("ppt/viewProps.xml", f"{XML}<p:viewPr {NS}/>")
        z.writestr("ppt/tableStyles.xml", f'{XML}<a:tblStyleLst xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" def="{{5C22544A-7EE6-4342-B048-85BDC9FD1C3A}}"/>')
        z.writestr("ppt/slideMasters/slideMaster1.xml", master())
        z.writestr("ppt/slideMasters/_rels/slideMaster1.xml.rels",
                   rels(("rId1", "slideLayout", "../slideLayouts/slideLayout1.xml"), ("rId2", "theme", "../theme/theme1.xml")))
        z.writestr("ppt/theme/theme1.xml", theme())
        z.writestr("ppt/slideLayouts/slideLayout1.xml", layout())
        z.writestr("ppt/slideLayouts/_rels/slideLayout1.xml.rels", rels(("rId1", "slideMaster", "../slideMasters/slideMaster1.xml")))
        for i, s in enumerate(body):
            z.writestr(f"ppt/slides/slide{i + 1}.xml", s)
            z.writestr(f"ppt/slides/_rels/slide{i + 1}.xml.rels", rels(("rId1", "slideLayout", "../slideLayouts/slideLayout1.xml")))


if __name__ == "__main__":
    build(sys.argv[1])
    print(sys.argv[1])
