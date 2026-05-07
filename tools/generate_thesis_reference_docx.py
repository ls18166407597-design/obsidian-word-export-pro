from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path
import xml.etree.ElementTree as ET
import re


W_NS = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
ET.register_namespace("w", W_NS)


def w(tag: str) -> str:
    return f"{{{W_NS}}}{tag}"


def find_style(root: ET.Element, style_id: str) -> ET.Element | None:
    for style in root.findall(w("style")):
      if style.get(w("styleId")) == style_id:
        return style
    return None


def ensure(parent: ET.Element, tag: str) -> ET.Element:
    child = parent.find(w(tag))
    if child is None:
        child = ET.SubElement(parent, w(tag))
    return child


def set_rfonts(target: ET.Element, east_asia: str, ascii_font: str = "Times New Roman") -> None:
    rfonts = ensure(target, "rFonts")
    for attr in ["asciiTheme", "hAnsiTheme", "cstheme", "eastAsiaTheme"]:
        if w(attr) in rfonts.attrib:
            del rfonts.attrib[w(attr)]
    rfonts.set(w("ascii"), ascii_font)
    rfonts.set(w("hAnsi"), ascii_font)
    rfonts.set(w("cs"), ascii_font)
    rfonts.set(w("eastAsia"), east_asia)


def set_spacing(target: ET.Element, before: int | None = None, after: int | None = None, line: int | None = None) -> None:
    spacing = ensure(target, "spacing")
    if before is not None:
        spacing.set(w("before"), str(before))
    if after is not None:
        spacing.set(w("after"), str(after))
    if line is not None:
        spacing.set(w("line"), str(line))
        spacing.set(w("lineRule"), "auto")


def set_indentation(target: ET.Element, first_line_chars: int | None = None, left: int | None = None) -> None:
    ind = ensure(target, "ind")
    if first_line_chars is not None:
        ind.set(w("firstLineChars"), str(first_line_chars))
    if left is not None:
        ind.set(w("left"), str(left))


def remove_children(target: ET.Element, tag: str) -> None:
    for child in list(target.findall(w(tag))):
        target.remove(child)


def create_style(root: ET.Element, style_id: str, style_type: str, name: str, based_on: str | None = None) -> ET.Element:
    style = ET.SubElement(root, w("style"))
    style.set(w("type"), style_type)
    style.set(w("styleId"), style_id)
    style.set(w("customStyle"), "1")
    ET.SubElement(style, w("name")).set(w("val"), name)
    if based_on is not None:
        ET.SubElement(style, w("basedOn")).set(w("val"), based_on)
    return style


def update_styles_xml(xml_bytes: bytes) -> bytes:
    root = ET.fromstring(xml_bytes)

    doc_defaults = root.find(w("docDefaults"))
    if doc_defaults is not None:
        rpr_default = ensure(ensure(doc_defaults, "rPrDefault"), "rPr")
        set_rfonts(rpr_default, "宋体")
        sz = ensure(rpr_default, "sz")
        sz.set(w("val"), "24")
        sz_cs = ensure(rpr_default, "szCs")
        sz_cs.set(w("val"), "24")

        ppr_default = ensure(ensure(doc_defaults, "pPrDefault"), "pPr")
        set_spacing(ppr_default, before=0, after=0, line=360)

    body = find_style(root, "BodyText")
    if body is not None:
        ppr = ensure(body, "pPr")
        set_spacing(ppr, before=0, after=0, line=360)
        set_indentation(ppr, first_line_chars=200)
        rpr = ensure(body, "rPr")
        set_rfonts(rpr, "宋体")
        sz = ensure(rpr, "sz")
        sz.set(w("val"), "24")
        sz_cs = ensure(rpr, "szCs")
        sz_cs.set(w("val"), "24")

    first = find_style(root, "FirstParagraph")
    if first is not None and body is not None:
        ppr = ensure(first, "pPr")
        set_spacing(ppr, before=0, after=0, line=360)
        set_indentation(ppr, first_line_chars=200)
        rpr = ensure(first, "rPr")
        set_rfonts(rpr, "宋体")
        sz = ensure(rpr, "sz")
        sz.set(w("val"), "24")
        sz_cs = ensure(rpr, "szCs")
        sz_cs.set(w("val"), "24")

    compact = find_style(root, "Compact")
    if compact is not None:
        ppr = ensure(compact, "pPr")
        set_spacing(ppr, before=0, after=0, line=300)
        rpr = ensure(compact, "rPr")
        set_rfonts(rpr, "宋体")
        sz = ensure(rpr, "sz")
        sz.set(w("val"), "21")
        sz_cs = ensure(rpr, "szCs")
        sz_cs.set(w("val"), "21")

    for style_id, east_asia_font, size, before, after in [
        ("Heading1", "宋体", 32, 240, 120),
        ("Heading2", "宋体", 28, 180, 80),
        ("Heading3", "宋体", 24, 120, 40),
    ]:
        style = find_style(root, style_id)
        if style is None:
            continue
        ppr = ensure(style, "pPr")
        set_spacing(ppr, before=before, after=after, line=360)
        remove_children(ppr, "jc")
        rpr = ensure(style, "rPr")
        set_rfonts(rpr, east_asia_font)
        for color in list(rpr.findall(w("color"))):
            rpr.remove(color)
        for italic in list(rpr.findall(w("i"))):
            rpr.remove(italic)
        for italic in list(rpr.findall(w("iCs"))):
            rpr.remove(italic)
        bold = ensure(rpr, "b")
        bold_cs = ensure(rpr, "bCs")
        bold.set(w("val"), "1")
        bold_cs.set(w("val"), "1")
        sz = ensure(rpr, "sz")
        sz.set(w("val"), str(size))
        sz_cs = ensure(rpr, "szCs")
        sz_cs.set(w("val"), str(size))

    for style_id, east_asia_font, size in [
        ("Heading1Char", "宋体", 32),
        ("Heading2Char", "宋体", 28),
        ("Heading3Char", "宋体", 24),
    ]:
        style = find_style(root, style_id)
        if style is None:
            continue
        rpr = ensure(style, "rPr")
        set_rfonts(rpr, east_asia_font)
        for color in list(rpr.findall(w("color"))):
            rpr.remove(color)
        for italic in list(rpr.findall(w("i"))):
            rpr.remove(italic)
        for italic in list(rpr.findall(w("iCs"))):
            rpr.remove(italic)
        bold = ensure(rpr, "b")
        bold_cs = ensure(rpr, "bCs")
        bold.set(w("val"), "1")
        bold_cs.set(w("val"), "1")
        sz = ensure(rpr, "sz")
        sz.set(w("val"), str(size))
        sz_cs = ensure(rpr, "szCs")
        sz_cs.set(w("val"), str(size))

    caption = find_style(root, "Caption")
    if caption is not None:
        ppr = ensure(caption, "pPr")
        set_spacing(ppr, before=80, after=80, line=300)
        jc = ensure(ppr, "jc")
        jc.set(w("val"), "center")
        rpr = ensure(caption, "rPr")
        set_rfonts(rpr, "宋体")
        remove_children(rpr, "i")
        sz = ensure(rpr, "sz")
        sz.set(w("val"), "21")
        sz_cs = ensure(rpr, "szCs")
        sz_cs.set(w("val"), "21")

    table = find_style(root, "Table")
    if table is not None:
        tbl_pr = ensure(table, "tblPr")
        tbl_borders = ensure(tbl_pr, "tblBorders")
        for edge in ["top", "bottom"]:
            border = ensure(tbl_borders, edge)
            border.set(w("val"), "single")
            border.set(w("sz"), "12")
            border.set(w("space"), "0")
            border.set(w("color"), "auto")
        for edge in ["left", "right", "insideH", "insideV"]:
            border = ensure(tbl_borders, edge)
            border.set(w("val"), "nil")

        tbl_cell_mar = ensure(tbl_pr, "tblCellMar")
        for edge in ["top", "bottom"]:
            mar = ensure(tbl_cell_mar, edge)
            mar.set(w("type"), "dxa")
            mar.set(w("w"), "36")
        for edge in ["left", "right"]:
            mar = ensure(tbl_cell_mar, edge)
            mar.set(w("type"), "dxa")
            mar.set(w("w"), "72")

        for style_pr in table.findall(w("tblStylePr")):
            if style_pr.get(w("type")) == "firstRow":
                tc_pr = ensure(style_pr, "tcPr")
                tc_borders = ensure(tc_pr, "tcBorders")
                bottom = ensure(tc_borders, "bottom")
                bottom.set(w("val"), "single")
                bottom.set(w("sz"), "8")
                bottom.set(w("space"), "0")
                bottom.set(w("color"), "auto")
                ppr = ensure(style_pr, "pPr")
                jc = ensure(ppr, "jc")
                jc.set(w("val"), "center")
                rpr = ensure(style_pr, "rPr")
                set_rfonts(rpr, "宋体")
                bold = ensure(rpr, "b")
                bold.set(w("val"), "1")
                sz = ensure(rpr, "sz")
                sz.set(w("val"), "21")
                sz_cs = ensure(rpr, "szCs")
                sz_cs.set(w("val"), "21")

    table_note = find_style(root, "TableNote")
    if table_note is None:
        table_note = create_style(root, "TableNote", "paragraph", "Table Note", "BodyText")
    ppr = ensure(table_note, "pPr")
    set_spacing(ppr, before=0, after=0, line=240)
    remove_children(ppr, "jc")
    set_indentation(ppr, first_line_chars=0)
    rpr = ensure(table_note, "rPr")
    set_rfonts(rpr, "宋体")
    sz = ensure(rpr, "sz")
    sz.set(w("val"), "20")
    sz_cs = ensure(rpr, "szCs")
    sz_cs.set(w("val"), "20")

    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def update_document_xml(xml_bytes: bytes) -> bytes:
    root = ET.fromstring(xml_bytes)
    body = root.find(w("body"))
    if body is None:
        return xml_bytes
    sect_pr = body.find(w("sectPr"))
    if sect_pr is None:
        return xml_bytes

    pg_sz = ensure(sect_pr, "pgSz")
    pg_sz.set(w("w"), "11906")
    pg_sz.set(w("h"), "16838")

    pg_mar = ensure(sect_pr, "pgMar")
    pg_mar.set(w("top"), "1440")
    pg_mar.set(w("right"), "1440")
    pg_mar.set(w("bottom"), "1440")
    pg_mar.set(w("left"), "1440")
    pg_mar.set(w("header"), "720")
    pg_mar.set(w("footer"), "720")
    pg_mar.set(w("gutter"), "0")

    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def update_settings_xml(xml_bytes: bytes) -> bytes:
    xml_text = xml_bytes.decode("utf-8")
    # Keep Word's original namespace declarations intact and only strip
    # the compatibility block that triggers legacy compatibility mode.
    xml_text = re.sub(r"<w:compat>.*?</w:compat>", "", xml_text, flags=re.S)
    return xml_text.encode("utf-8")


def update_app_xml(xml_bytes: bytes) -> bytes:
    ns = "http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"
    vt_ns = "http://schemas.openxmlformats.org/officeDocument/2006/docPropsVTypes"
    ET.register_namespace("", ns)
    ET.register_namespace("vt", vt_ns)
    root = ET.fromstring(xml_bytes)

    application = root.find(f"{{{ns}}}Application")
    if application is None:
        application = ET.SubElement(root, f"{{{ns}}}Application")
    application.text = "Microsoft Office Word"

    app_version = root.find(f"{{{ns}}}AppVersion")
    if app_version is None:
        app_version = ET.SubElement(root, f"{{{ns}}}AppVersion")
    app_version.text = "16.0000"

    company = root.find(f"{{{ns}}}Company")
    if company is None:
        company = ET.SubElement(root, f"{{{ns}}}Company")
    company.text = ""

    return ET.tostring(root, encoding="utf-8", xml_declaration=True)


def build_reference_docx(output_path: Path) -> None:
    with tempfile.TemporaryDirectory() as tmpdir:
        default_docx = Path(tmpdir) / "reference.docx"
        subprocess.run(
            ["pandoc", "--print-default-data-file", "reference.docx"],
            check=True,
            stdout=default_docx.open("wb"),
        )

        work_docx = Path(tmpdir) / "work.docx"
        shutil.copyfile(default_docx, work_docx)

        with zipfile.ZipFile(work_docx, "r") as zin:
            files = {name: zin.read(name) for name in zin.namelist()}

        files["word/styles.xml"] = update_styles_xml(files["word/styles.xml"])
        files["word/document.xml"] = update_document_xml(files["word/document.xml"])
        if "word/settings.xml" in files:
            files["word/settings.xml"] = update_settings_xml(files["word/settings.xml"])
        if "docProps/app.xml" in files:
            files["docProps/app.xml"] = update_app_xml(files["docProps/app.xml"])

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with zipfile.ZipFile(output_path, "w", zipfile.ZIP_DEFLATED) as zout:
            for name, data in files.items():
                zout.writestr(name, data)


def main() -> int:
    if len(sys.argv) != 2:
        print("Usage: generate_thesis_reference_docx.py /path/to/output.docx", file=sys.stderr)
        return 1
    output_path = Path(sys.argv[1]).expanduser().resolve()
    build_reference_docx(output_path)
    print(output_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
