import json, pathlib, re, sys, zipfile
from xml.sax.saxutils import escape

# Document metadata carries the author's name into the .docx. Read it from the
# profile rather than hardcoding it, so the script stays user-neutral.
_profile = pathlib.Path(__file__).parent / "profile" / "user_profile.json"
AUTHOR = json.loads(_profile.read_text()).get("name", "") if _profile.exists() else ""

src, out = sys.argv[1], sys.argv[2]
lines = open(src).read().split('\n')
PT = 20  # twips per point
def cm(v): return int(round(v * 567))

body = []

def run(text, size=9.0, bold=False, colour="111111", underline=False):
    rpr = ['<w:rFonts w:ascii="Helvetica" w:hAnsi="Helvetica"/>']
    if bold: rpr.append('<w:b/>')
    if underline: rpr.append('<w:u w:val="single"/>')
    rpr.append(f'<w:color w:val="{colour}"/>')
    rpr.append(f'<w:sz w:val="{int(size*2)}"/><w:szCs w:val="{int(size*2)}"/>')
    return (f'<w:r><w:rPr>{"".join(rpr)}</w:rPr>'
            f'<w:t xml:space="preserve">{escape(text)}</w:t></w:r>')

def para(text, size=9.0, bold=False, colour="111111", before=0, after=2, bullet=False):
    ppr = [f'<w:spacing w:before="{int(before*PT)}" w:after="{int(after*PT)}" w:line="240" w:lineRule="auto"/>']
    if bullet:
        ppr.append(f'<w:ind w:left="{cm(0.45)}" w:hanging="{cm(0.25)}"/>')
    runs = []
    for tok in re.split(r'(\*\*.+?\*\*|\[[^\]]+\]\([^)]+\))', text):
        if not tok: continue
        if tok.startswith('**'):
            runs.append(run(tok[2:-2], size, True, colour))
        elif tok.startswith('['):
            runs.append(run(re.match(r'\[([^\]]+)\]', tok).group(1), size, bold, colour, underline=True))
        else:
            runs.append(run(tok, size, bold, colour))
    body.append(f'<w:p><w:pPr>{"".join(ppr)}</w:pPr>{"".join(runs)}</w:p>')

meta_re = re.compile(r'^\*\*[^*]+\*\*\s*\|')
for ln in lines:
    t = ln.rstrip()
    if t == '---' or not t.strip(): continue
    if   t.startswith('# '):   para(t[2:], 20, True, "000000", 0, 2)
    elif t.startswith('## '):  para(t[3:].upper(), 10, True, "222222", 9, 3)
    elif t.startswith('### '): para(t[4:], 9.5, True, "000000", 6, 0)
    elif t.startswith('- '):   para('•  ' + t[2:], 9, False, "111111", 1.5, 1.5, bullet=True)
    elif meta_re.match(t):     para(t, 8.5, False, "555555", 0, 1)
    elif t.startswith('+44'):  para(t, 9, False, "555555", 0, 2)
    else:                      para(t, 9, False, "111111", 0, 2)

sect = (f'<w:sectPr><w:pgSz w:w="11906" w:h="16838"/>'
        f'<w:pgMar w:top="{cm(1.4)}" w:right="{cm(1.3)}" w:bottom="{cm(0.5)}" w:left="{cm(1.3)}"'
        f' w:header="0" w:footer="0" w:gutter="0"/></w:sectPr>')

document = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
  '<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">'
  f'<w:body>{"".join(body)}{sect}</w:body></w:document>')

ct = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
  '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">'
  '<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>'
  '<Default Extension="xml" ContentType="application/xml"/>'
  '<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>'
  '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>'
  '</Types>')

rels = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
  '<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">'
  '<Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/>'
  '<Relationship Id="rId2" Type="http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties" Target="docProps/core.xml"/>'
  '</Relationships>')

core = ('<?xml version="1.0" encoding="UTF-8" standalone="yes"?>'
  '<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties"'
  ' xmlns:dc="http://purl.org/dc/elements/1.1/">'
  f'<dc:title>{escape("CV - " + AUTHOR if AUTHOR else "CV")}</dc:title>'
  f'<dc:creator>{escape(AUTHOR)}</dc:creator>'
  f'<cp:lastModifiedBy>{escape(AUTHOR)}</cp:lastModifiedBy></cp:coreProperties>')

with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
    z.writestr('[Content_Types].xml', ct)
    z.writestr('_rels/.rels', rels)
    z.writestr('docProps/core.xml', core)
    z.writestr('word/document.xml', document)
print("saved:", out, "| paragraphs:", len(body))
