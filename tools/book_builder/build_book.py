#!/usr/bin/env python3
"""Rebuild the Home Server Lab handbook with Book-1 style typography.

Sources:  repo Markdown (latest text)  +  Book 1 PDF oracles (tables, figures).
"""
import re, json, sys, importlib.util, math, difflib
from pathlib import Path
from html import unescape
from xml.sax.saxutils import escape

KIT = Path(__file__).resolve().parent
SCR = KIT / 'oracle'
REPO = KIT.parents[1]
OUT = Path(sys.argv[1]) if len(sys.argv) > 1 else REPO.parent / '06-Book/Panduan_Lengkap_Home_Server_Lab_Edisi_Terpadu_2026.11.pdf'
LIMIT = int(sys.argv[2]) if len(sys.argv) > 2 else 0   # debug: only first N segments

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table,
    TableStyle, PageBreak, KeepTogether, Flowable, Preformatted, Image, CondPageBreak)
from reportlab.platypus.tableofcontents import TableOfContents

# ---------------------------------------------------------------- fonts / colors
FD = Path(importlib.util.find_spec('reportlab').origin).parent / 'fonts'
for n, f in [('Sans', 'Vera'), ('Sans-B', 'VeraBd'), ('Sans-I', 'VeraIt'), ('Sans-BI', 'VeraBI')]:
    pdfmetrics.registerFont(TTFont(n, str(FD / (f + '.ttf'))) )
pdfmetrics.registerFontFamily('Sans', normal='Sans', bold='Sans-B', italic='Sans-I', boldItalic='Sans-BI')
# ReportLab's built-in Courier is portable and fixed-width for terminal examples.

pdfmetrics.registerFontFamily('Courier', normal='Courier', bold='Courier-Bold', italic='Courier-Oblique', boldItalic='Courier-BoldOblique')

NAVY = colors.HexColor('#13233B'); INK = colors.HexColor('#1B2233'); BLUE = colors.HexColor('#1F5EA8')
TEAL = colors.HexColor('#1F7A8C'); GRID = colors.HexColor('#C9D3DE'); GRAY = colors.HexColor('#5B6573')
CODEBG = colors.HexColor('#0F1B2D'); CODEFG = colors.HexColor('#E6EEF7'); NUM = colors.HexColor('#8AA4BF')
C_NOTE = (colors.HexColor('#E8F1FB'), colors.HexColor('#2E6DB4'))
C_TIP = (colors.HexColor('#E6F4EA'), colors.HexColor('#2E8B57'))
C_WARN = (colors.HexColor('#FDEBE8'), colors.HexColor('#C0392B'))
C_SEC = (colors.HexColor('#FFF3D6'), colors.HexColor('#C98A10'))
C_CASE = (colors.HexColor('#FFF6E0'), colors.HexColor('#D9822B'))
C_PLACE = (colors.HexColor('#EFE9F8'), colors.HexColor('#7B5EA7'))
W = 170 * mm   # text width

def S(name, **kw):
    base = dict(fontName='Sans', fontSize=9.3, leading=13.2, textColor=INK, alignment=TA_LEFT)
    base.update(kw); return ParagraphStyle(name, **base)
ST = {
    'body': S('body', spaceAfter=5),
    'h1': S('h1', fontName='Sans-B', fontSize=22, leading=27, textColor=BLUE, spaceBefore=0, spaceAfter=10, keepWithNext=1),
    'h2': S('h2', fontName='Sans-B', fontSize=14, leading=18, textColor=TEAL, spaceBefore=14, spaceAfter=5, keepWithNext=1),
    'h3': S('h3', fontName='Sans-B', fontSize=10.6, leading=14, textColor=INK, spaceBefore=9, spaceAfter=3, keepWithNext=1),
    'bul': S('bul', leftIndent=13, firstLineIndent=-9, spaceAfter=2.5),
    'step': S('step', leftIndent=16, firstLineIndent=-16, spaceAfter=2.5),
    'expl': S('expl', fontSize=8.5, leading=11.6, textColor=colors.HexColor('#3C4655')),
    'cell': S('cell', fontSize=8.1, leading=10.6),
    'cellh': S('cellh', fontName='Sans-B', fontSize=8.1, leading=10.6, textColor=colors.white),
    'cap': S('cap', fontName='Sans-I', fontSize=8, leading=10.5, textColor=GRAY, spaceBefore=3, spaceAfter=8),
    'call': S('call', fontSize=8.9, leading=12.3),
    'bar': S('bar', fontName='Sans-B', fontSize=8.2, leading=10.5, textColor=colors.white),
    'toc0': S('toc0', fontName='Sans-B', fontSize=8.6, leading=11, spaceBefore=4, textColor=NAVY),
    'toc1': S('toc1', fontSize=7.8, leading=9.6, leftIndent=10, textColor=INK),
}
MONO_OPEN = '<font name="Courier" color="#9B1C31">'

# ---------------------------------------------------------------- inline text
IP_RE = re.compile(r'(?<![\w.])\d{1,3}(?:\.\d{1,3}){3}(?:/\d{1,2}|:\d{2,5})?(?![\w])')
PATH_RE = re.compile(r'(?<![\w/:.])(/(?:[A-Za-z0-9._\-*]+/?)+)')
FILE_RE = re.compile(r'(?<![\w/.])([\w\-]+\.(?:yaml|yml|conf|env|json|sh|sources|hujson|service|ini|cfg|txt|md|py))(?![\w])')
URL_RE = re.compile(r'(https?://[^\s<>"]+?)(?=[.,;:)]*(?:\s|$))')

COMB_RE = re.compile('|'.join('(?:%s)' % r.pattern for r in (URL_RE, IP_RE, PATH_RE, FILE_RE)))

def inline(s, mono=True):
    s = unescape(s)
    s = s.replace('\\*', '*').replace('\\_', '_')
    s = re.sub(r'\[([^\]]+)\]\((?!https?://)[^)]*\)', r'\1', s)
    t = escape(s)
    t = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', t)
    t = re.sub(r'\[([^\]]+)\]\((https?://[^)]+)\)', r'<link href="\2" color="#1768A0">\1</link>', t)
    t = re.sub(r'`([^`]+)`', lambda m: MONO_OPEN + m.group(1) + '</font>', t)
    if mono:
        parts = re.split(r'(<font name="Courier".*?</font>|</?[a-z]+[^>]*>)', t)
        out = []
        for p in parts:
            if p.startswith('<'):
                out.append(p); continue
            out.append(COMB_RE.sub(lambda m: MONO_OPEN + m.group(0) + '</font>', p))
        t = ''.join(out)
    return t

def P(text, style='body', mono=True):
    return Paragraph(inline(text, mono), ST[style])

# ---------------------------------------------------------------- oracle tables
def load_oracle():
    T = json.load(open(SCR / 'oracle_tables.json'))
    real = []
    for t in T:
        r0 = ''.join(t['rows'][0])
        if re.match(r'(TERMINAL|COMMAND|BERKAS|POWERSHELL|PENEMPATAN|KASUS|CATATAN|TIPS|PERINGATAN)', r0.replace(' ', '')):
            continue
        if len(t['rows'][0]) < 2: continue
        real.append(t)
    merged = []
    for t in real:
        if merged:
            m = merged[-1]
            if (t['page'] == m['page_end'] + 1 and t['bbox'][1] < 90 and m['bbox'][3] > 690
                    and len(t['rows'][0]) == len(m['rows'][0])):
                rows = t['rows']
                if rows and rows[0] == m['rows'][0]: rows = rows[1:]
                m['rows'] = m['rows'] + rows; m['page_end'] = t['page']; m['bbox'][3] = t['bbox'][3]
                continue
        d = dict(t); d['page_end'] = t['page']; merged.append(d)
    return merged
ORACLE = load_oracle()
def nz(s): return re.sub(r'[\s|]+', '', s)
for t in ORACLE:
    t['key'] = nz(''.join(''.join(r) for r in t['rows']))

# ---------------------------------------------------------------- figures
FIG_DIR = SCR / 'figs'
NATIVE_FIGS = {'1.1', '3.1', '8.1', '8.4', '8.5'}
FIG_DUMP_MAX = {'1.1': 22, '3.1': 22, '8.1': 7, '8.4': 7, '8.5': 9}
FIG_HAS_TEXT = {'9.2': False, '9.3': False}

# ---------------------------------------------------------------- tokenizer
HEAD_RE = re.compile(r'^(#{1,4})\s+(.*)$')
HDR_RE = re.compile(r'^\*\*(.+?)\*\*\s*(?:\|\s*(.*))?$')
CALL_RE = re.compile(r'^(CATATAN|TIPS|PERINGATAN|KEAMANAN)(?:\s+-\s+(.*))?$')
CASE_RE = re.compile(r'^KASUS NYATA(?:\s*-\s*(.*))?$')
PLACE_RE = re.compile(r'^PENEMPATAN\s+-\s+(.*)$')
FIELD_RE = re.compile(r'^(Tempat|Alasan|Perhatian|Gejala|Penyebab|Solusi|Sisi klien|Akses|Catatan|Risiko|Keputusan|Fungsi|Hasil)\s*:\s*(.*)$')
BUL_RE = re.compile(r'^([•\-*]) (.*)$')
NUM_RE = re.compile(r'^(\d+)[.)]\s+(.*)$')
CAP_RE = re.compile(r'^Gambar (\d+\.\d+) - (.*)$')
H3_KNOWN = re.compile(r'^(Syarat lulus.*|Lembar [Pp]embaruan.*|Uji menyeluruh|Masalah dan solusi|Prasyarat|Daftar hal yang belum dipastikan|'
                      r'Konfigurasi di .+|Backup dan pemulihan|Cadangan dan masalah umum|Windows|Android|iPhone|WiFi|HTTPS|Kesimpulan|'
                      r'Alternatif lewat antarmuka web|Cara [A-D]: .+|Cara \d: .+|[A-D]\. .+|C\.\d .+)$')

def strip_numbers(code):
    """Fenced code whose lines carry their own sequential numbers -> (code without numbers, stray trailing lines)."""
    if len(code) < 2: return code, []
    exp = 1; out = []
    for ln in code:
        m = re.match(r'^\s*(\d{1,3})(?: (.*))?$', ln)
        if not m or int(m.group(1)) != exp: break
        out.append((m.group(2) or '').rstrip()); exp += 1
    if len(out) < 2: return code, []
    return out, [x for x in code[len(out):] if x.strip()]

def tokenize(text):
    """-> list of items: ('line', s) | ('code', [lines]) | ('table', rows)"""
    items = []; lines = text.splitlines(); i = 0
    while i < len(lines):
        raw = lines[i].rstrip()
        if raw.strip().startswith('```'):
            i += 1; code = []
            while i < len(lines) and not lines[i].strip().startswith('```'):
                code.append(lines[i].rstrip('\n').rstrip()); i += 1
            i += 1; cd, extra = strip_numbers(code); items.append(('code', cd))
            for x in extra: items.append(('line', x.strip(), x))
            continue
        items.append(('line', raw.strip(), raw)); i += 1
    return items

LEGEND = [['Awalan di kotak', 'Artinya'], ['#', 'Prompt root di Linux (Proxmox, Debian, STB). Jangan ikut diketik.'],
          ['$', 'Prompt user biasa di Linux atau Git Bash.'], ['C:\\>', 'Command Prompt Windows.'], ['PS>', 'PowerShell Windows.'],
          ['>', 'Terminal MikroTik (WinBox: New Terminal).']]

def fuzzy_split(run_texts, t):
    """Split flattened md lines into the cell grid of oracle table t (approximate)."""
    joined = ' '.join(run_texts)
    idx = [i for i, ch in enumerate(joined) if not (ch.isspace() or ch == '|')]
    reg = ''.join(joined[i] for i in idx)
    key = t['key']
    cuts = []; pos = 0
    for r in t['rows']:
        for c in r:
            pos += len(nz(c)); cuts.append(pos)
    sm = difflib.SequenceMatcher(None, key, reg, autojunk=False)
    ops = sm.get_opcodes()
    def mp(pk):
        for tag, i1, i2, j1, j2 in ops:
            if i1 <= pk <= i2:
                if i2 == i1: return j1
                return j1 + round((pk - i1) * (j2 - j1) / (i2 - i1))
        return len(reg)
    ends = [mp(c) for c in cuts]
    ends[-1] = len(reg)
    cells = []; prev = 0
    for e in ends:
        e = max(e, prev)
        a = idx[prev] if prev < len(idx) else len(joined)
        b = (idx[e - 1] + 1) if 0 < e <= len(idx) else a
        cells.append(joined[a:b].strip()); prev = e
    rows = []; k = 0
    for r in t['rows']:
        rows.append(cells[k:k + len(r)]); k += len(r)
    return rows

def apply_oracle(items):
    # fixed legend table of chapter 1.6
    for i, it in enumerate(items):
        if it[0] == 'line' and it[1] == 'Awalan di kotak Artinya' and i + 5 < len(items) and items[i + 1][1].startswith('# Prompt root'):
            items[i:i + 6] = [('table', LEGEND)]; break
    used = 0
    i = 0
    isrun = lambda it: it[0] == 'line' and not it[1].startswith('|')
    while i < len(items):
        if not isrun(items[i]): i += 1; continue
        j = i
        while j < len(items) and isrun(items[j]): j += 1
        run = items[i:j]
        stream = []; owner = []
        for k, it in enumerate(run):
            s = it[1]; n = nz(s)
            stream.append(n); owner.extend([k] * len(n))
        big = ''.join(stream)
        # collect all matches, longest first, non-overlapping
        found = []
        for t in ORACLE:
            key = t['key']
            if len(key) < 25: continue
            p = big.find(key[:30])
            while p >= 0:
                seg = big[p:p + len(key)]
                if seg == key or difflib.SequenceMatcher(None, seg, key).quick_ratio() > 0.97 and seg[-20:] == key[-20:]:
                    found.append((p, p + len(key), t)); break
                p = big.find(key[:30], p + 1)
        exact_keys = {id(t) for _, _, t in found}
        for t in ORACLE:
            key = t['key']
            if id(t) in exact_keys or len(key) < 60 or not t.get('fuzzy_ok', True): continue
            h, tl = key[:16], key[-16:]
            p = big.find(h)
            while p >= 0:
                q = big.find(tl, p + len(key) // 2)
                if q >= 0:
                    seg = big[p:q + len(tl)]
                    if 0.75 * len(key) <= len(seg) <= 1.35 * len(key) and difflib.SequenceMatcher(None, seg, key, autojunk=False).ratio() >= 0.80:
                        found.append((p, q + len(tl), t)); break
                p = big.find(h, p + 1)
        found.sort(key=lambda x: (x[0], -(x[1] - x[0])))
        last = -1; repl = []
        for a, b, t in found:
            if a < last: continue
            ia, ib = owner[a], owner[min(b - 1, len(owner) - 1)]
            repl.append((ia, ib, t)); last = b
        for ia, ib, t in reversed(repl):
            texts = [x[1] for x in run[ia:ib + 1]]
            exact = nz(''.join(texts)) == t['key']
            rows = t['rows'] if exact else fuzzy_split(texts, t)
            run[ia:ib + 1] = [('table', rows)]; used += 1
        items[i:j] = run
        i += len(run)
    return items, used


NUMLINE_RE = re.compile(r'^\s*(\d{1,3})(?: (.*))?$')
KONF = REPO / 'konfigurasi'
def find_conf(path):
    path = re.sub(r'\s*\(.*\)\s*$', '', path.strip()).strip()
    cands = []
    if path.startswith('/'):
        cands.append(KONF / 'server' / path.lstrip('/'))
    if path.startswith('apps/'): cands.append(KONF / 'gitops' / path)
    if path.endswith('settings.yaml'): cands.append(KONF / 'server/opt/stacks/homepage/config/settings.yaml')
    for c in cands:
        if c.exists(): return c
    return None

def conf_lines(path, md_lines):
    """Restore indentation of md_lines from the authoritative file (content stays as in the book)."""
    c = find_conf(path)
    if not c: return None
    fl = c.read_text(encoding='utf-8').rstrip('\n').splitlines()
    key = lambda x: re.sub(r'\s+', '', x)
    mk = [key(x) for x in md_lines]; fk = [key(x) for x in fl]
    sm = difflib.SequenceMatcher(None, mk, fk, autojunk=False)
    nonblank = [k for k in mk if k]
    if not nonblank: return None
    matched = 0; out = []
    for tag, i1, i2, j1, j2 in sm.get_opcodes():
        if tag == 'equal':
            out += fl[j1:j2]; matched += sum(1 for k in mk[i1:i2] if k)
        elif tag == 'replace' and (i2 - i1) == (j2 - j1):
            for a_, b_ in zip(range(i1, i2), range(j1, j2)):
                if mk[a_] and difflib.SequenceMatcher(None, mk[a_], fk[b_]).ratio() >= 0.8:
                    out.append(fl[b_]); matched += 1
                else: out.append(md_lines[a_])
        elif tag in ('replace', 'delete'):
            out += md_lines[i1:i2]
    return out if matched / len(nonblank) >= 0.6 else None

TREE = ['homelab/', '  clusters/', '    home/', '      apps.yaml          <- memberi tahu Flux folder apps/ harus diterapkan',
        '      flux-system/       <- dibuat otomatis oleh flux bootstrap', '  apps/', '    web/', '      namespace.yaml', '      deployment.yaml',
        '      service.yaml', '      kustomization.yaml', '  renovate.json']

def fix_orphans(items):
    """Merge numbered orphan lines ("N text") into code blocks / BERKAS boxes."""
    out = []; i = 0
    while i < len(items):
        it = items[i]
        if it[0] == 'line' and NUMLINE_RE.match(it[2]) and not re.match(r'^\s*\d+[.)]', it[2]):
            j = i; run = []; exp = int(NUMLINE_RE.match(it[2]).group(1))
            while j < len(items) and items[j][0] == 'line':
                m = NUMLINE_RE.match(items[j][2])
                if not m or int(m.group(1)) != exp: break
                run.append((m.group(2) or '').rstrip()); exp += 1; j += 1
            start = int(NUMLINE_RE.match(it[2]).group(1))
            prev = out[-1] if out else None
            # skip blank 'line' items between code and orphans
            k = len(out) - 1
            while k >= 0 and out[k][0] == 'line' and not out[k][1]: k -= 1
            if len(run) >= 2 and k >= 0 and out[k][0] == 'code' and len(out[k][1]) == start - 1:
                out[k] = ('code', out[k][1] + run); del out[k + 1:]; i = j; continue
            if len(run) >= 3 and k >= 0 and out[k][0] == 'line' and out[k][1].startswith('BERKAS:') and start == 1:
                out[k] = ('berkas', out[k][1], run); del out[k + 1:]; i = j; continue
        out.append(it); i += 1
    return out

# ---------------------------------------------------------------- block parser
def cont(prev, nxt):
    p = prev.rstrip(); n = nxt.strip()
    if not n or not p: return False
    if n[0].islower() and p[-1] not in '.!?;': return True
    if len(p) >= 88 and not (p[-1] in '.!?:' and len(p) < 100): return True
    return False

def is_marker(s):
    return bool(HEAD_RE.match(s) or s.startswith(('```', '|', '>', '[[', '<!--')) or CALL_RE.match(s) or CASE_RE.match(s)
                or PLACE_RE.match(s) or CAP_RE.match(s) or BUL_RE.match(s) or NUM_RE.match(s) or HDR_RE.match(s)
                or s.startswith('Contoh hasil'))

class Parser:
    def __init__(self, items, ctx):
        self.it = items; self.j = 0; self.out = []; self.ctx = ctx

    def peek(self, k=0):
        return tuple(self.it[self.j + k][:2]) if self.j + k < len(self.it) else (None, None)

    def take_text(self, first):
        """Collect wrapped continuation lines for a paragraph starting with `first`."""
        txt = first; prev = first
        while True:
            kind, s = self.peek()
            if kind != 'line' or not s or is_marker(s) or FIELD_RE.match(s) or H3_KNOWN.match(s) and len(s) < 40:
                break
            if not cont(prev, s): break
            txt += ' ' + s; prev = s; self.j += 1
        return txt

    def parse(self):
        out = self.out
        while self.j < len(self.it):
            kind, s = self.it[self.j][:2]
            if kind == 'code':
                out.append(('code', s)); self.j += 1; continue
            if kind == 'table':
                out.append(('table', s)); self.j += 1; continue
            if kind == 'berkas':
                it3 = self.it[self.j]; self.j += 1
                path = it3[1][len('BERKAS:'):].strip()
                lines = conf_lines(path, it3[2])
                if lines is None and path.startswith('struktur folder'): lines = TREE
                if lines is None: lines = it3[2]
                out.append(('file', 'BERKAS: ' + path, '', [{'code': lines, 'expl': None}])); continue
            self.j += 1
            if not s or s == '---' or s.startswith('<!--'): continue
            m = HEAD_RE.match(s)
            if m and len(m.group(1)) == 1 and not re.match(r'^(Bab \d+|Bagian \d+|Lampiran|Roadmap|Panduan|Buku)', m.group(2)):
                m = None
            if m:
                out.append(('h%d' % min(len(m.group(1)), 3), m.group(2).strip())); continue
            if s.startswith('[[ROADMAP'):
                out.append(('roadmap', None)); continue
            if s.startswith('[[ILUSTRASI'):
                out.append(('topology', None)); continue
            if s.startswith('|'):
                rows = [s]
                while self.peek()[0] == 'line' and self.peek()[1].startswith('|'):
                    rows.append(self.peek()[1]); self.j += 1
                rr = [[c.strip().replace('\\|', '|') for c in r.strip().strip('|').split('|')] for r in rows]
                rr = [r for r in rr if not all(re.fullmatch(r':?-{3,}:?', c or '') for c in r)]
                if rr: out.append(('table', rr))
                continue
            if s.startswith('>'):
                qs = [s.lstrip('> ').rstrip()]
                while self.peek()[0] == 'line' and self.peek()[1].startswith('>'):
                    qs.append(self.peek()[1].lstrip('> ').rstrip()); self.j += 1
                body = ' '.join(q for q in qs if q)
                al = re.match(r'^\[!(NOTE|IMPORTANT|WARNING|TIP|CAUTION)\]\s*(.*)$', body)
                if al:
                    kind2 = {'NOTE': 'CATATAN', 'IMPORTANT': 'KEAMANAN', 'WARNING': 'PERINGATAN', 'CAUTION': 'PERINGATAN', 'TIP': 'TIPS'}[al.group(1)]
                    out.append(('callout', kind2, None, [al.group(2)]))
                elif body.startswith('Penjelasan'):
                    out.append(('expl', self.take_text_from(body)))
                else:
                    out.append(('callout', 'CATATAN', None, [body]))
                continue
            m = CAP_RE.match(s)
            if m:
                cap = self.take_text(s)
                out.append(('figure', m.group(1), CAP_RE.match(cap).group(2))); continue
            m = HDR_RE.match(s)
            if m and ('TERMINAL' in m.group(1) or 'POWERSHELL' in m.group(1) or 'COMMAND PROMPT' in m.group(1)
                      or m.group(1).startswith('MIKROTIK') or m.group(1).startswith('BERKAS')
                      or m.group(1).startswith('/') or re.search(r'\.(ya?ml|conf|env|json|sh|hujson)\b|Caddyfile|crontab', m.group(1))):
                self.parse_group(m.group(1), (m.group(2) or '').strip()); continue
            if m:
                out.append(('para', s)); continue
            m = CALL_RE.match(s)
            if m:
                body = []
                k, nxt = self.peek()
                if k == 'line' and nxt and not is_marker(nxt):
                    self.j += 1; body.append(self.take_text(nxt))
                out.append(('callout', m.group(1), (m.group(2) or '').strip() or None, body)); continue
            m = CASE_RE.match(s)
            if m:
                fields = self.parse_fields(); out.append(('case', (m.group(1) or '').strip(), fields)); continue
            m = PLACE_RE.match(s)
            if m:
                fields = self.parse_fields(); out.append(('place', m.group(1).strip(), fields)); continue
            if s.startswith('Contoh hasil'):
                k, nxt = self.peek()
                title = s
                if k == 'code':
                    self.j += 1; out.append(('output', title, nxt))
                else:
                    lines = []
                    while self.peek()[0] == 'line' and self.peek()[1] and not is_marker(self.peek()[1]) and len(lines) < 12 and not self.peek()[1].startswith(('Awalan', 'Bab ')):
                        lines.append(self.it[self.j][2].rstrip()); self.j += 1
                    if lines: out.append(('output', title, lines))
                    else: out.append(('para', s))
                continue
            m = BUL_RE.match(s)
            if m:
                out.append(('bullet', self.take_text(m.group(2)))); continue
            m = NUM_RE.match(s)
            if m:
                out.append(('step', m.group(1), self.take_text(m.group(2)))); continue
            # unmarked sub-heading
            if len(s) < 60 and re.match(r'^[A-Za-z0-9]', s) and not re.search(r'[.:;,!?)]$', s):
                k, nxt = self.peek()
                if H3_KNOWN.match(s) or (k == 'line' and nxt and (BUL_RE.match(nxt) or NUM_RE.match(nxt)) and not BUL_RE.match(s)):
                    out.append(('h3', s)); continue
                if k == 'table' and nxt and H3_KNOWN.match(s):
                    out.append(('h3', s)); continue
            out.append(('para', self.take_text(s)))
        return out

    def take_text_from(self, first):
        # first is already a '> ' stripped quote body; continuation lines follow without '>'
        txt = first; prev = first
        while True:
            kind, s = self.peek()
            if kind != 'line' or not s or is_marker(s) or not cont(prev, s): break
            txt += ' ' + s; prev = s; self.j += 1
        return txt

    def parse_fields(self):
        fields = []
        while True:
            kind, s = self.peek()
            if kind != 'line' or not s: break
            m = FIELD_RE.match(s)
            if m:
                self.j += 1; fields.append([m.group(1), self.take_text(m.group(2))]); continue
            if fields and not is_marker(s) and cont(fields[-1][1], s):
                # continuation not captured (shouldn't happen) -> merge
                self.j += 1; fields[-1][1] += ' ' + s; continue
            if not fields and not is_marker(s):
                self.j += 1; fields.append(['', self.take_text(s)]); continue
            break
        return fields

    def parse_group(self, title, desc):
        is_file = not (('TERMINAL' in title) or ('POWERSHELL' in title) or ('COMMAND PROMPT' in title) or title.startswith('MIKROTIK'))
        items = []
        while True:
            kind, s = self.peek()
            if kind == 'line' and not s:
                # blank: look ahead past blanks
                k = 1
                while self.peek(k)[0] == 'line' and not self.peek(k)[1]: k += 1
                if self.peek(k)[0] == 'code' and not is_file or (self.peek(k)[0] == 'code' and is_file and not items):
                    self.j += k; continue
                if self.peek(k)[0] == 'line' and self.peek(k)[1].startswith('> Penjelasan') and items:
                    self.j += k; continue
                break
            if kind == 'code':
                self.j += 1; items.append({'code': s, 'expl': None}); continue
            if kind == 'line' and s.startswith('>') and items:
                self.j += 1
                body = s.lstrip('> ').rstrip()
                items[-1]['expl'] = self.take_text_from(body); continue
            break
        if is_file and items:
            path = re.sub(r'^BERKAS:\s*', '', title)
            lines = conf_lines(path, items[0]['code'])
            if lines is not None and len(items) == 1: items[0]['code'] = lines
        self.out.append(('file' if is_file else 'terminal', title, desc, items))

def build_blocks(segments):
    blocks = []; used_total = 0
    for rel, content in segments:
        content = re.sub(r'\bSuplemen (\d)\b', r'Bagian \1', content)
        content = re.sub(r'\bSuplemen ini\b', 'Bagian ini', content)
        items = tokenize(content)
        items = fix_orphans(items)
        items, used = apply_oracle(items); used_total += used
        items = drop_figure_dumps(items)
        p = Parser(items, rel)
        blk = p.parse()
        if 'pengantar' in rel or 'penutup' in rel:
            blk = clean_part_page(blk, rel)
        blocks.append(('seg', rel)); blocks.extend(blk)
    print('oracle tables applied:', used_total)
    return blocks

def clean_part_page(blk, relname=''):
    out = []; title = ''; drop = 0
    for b in blk:
        if b[0] == 'h1':
            title = re.sub(r'\s*\((pengantar)\)\s*$', '', b[1]); out.append(('h1', title)); drop = 3; continue
        if drop and b[0] == 'para':
            t = nz(b[1]).lower()
            if t and t in nz(title).lower() or b[1].startswith('Asal: '):
                continue
            if b[1].startswith(('Bagian ini adalah tambahan', 'Suplemen ini adalah tambahan', 'Bagian ini adalah tambahan untuk')):
                continue
            if 'penutup' in relname and len(b[1]) < 100 and not b[1].rstrip().endswith(('.', ':')):
                drop = 0; continue
        if b[0] == 'para' and b[1].startswith('Bagian ini adalah tambahan untuk Buku Panduan'):
            continue
        drop = 0 if b[0] != 'h1' else drop
        out.append(b)
    return out

def drop_figure_dumps(items):
    """Remove the flattened text dump that precedes each 'Gambar N.N' caption."""
    idx = [i for i, it in enumerate(items) if it[0] == 'line' and CAP_RE.match(it[1])]
    kill = set()
    for ci in idx:
        fig = CAP_RE.match(items[ci][1]).group(1)
        if not (FIG_DIR / ('g' + fig.replace('.', '_') + '.png')).exists() and fig not in NATIVE_FIGS: continue
        if FIG_HAS_TEXT.get(fig) is False: continue
        cap = FIG_DUMP_MAX.get(fig, 40)
        n = 0; k = ci - 1
        while k >= 0 and n < cap:
            kind, s = items[k][:2]
            if kind != 'line' or not s: break
            if HEAD_RE.match(s) or s.startswith(('>', '**')) or CALL_RE.match(s) or NUM_RE.match(s) and len(s) > 60 or BUL_RE.match(s) and len(s) > 60:
                break
            if len(s) > 100 and fig not in NATIVE_FIGS: break
            if s.startswith(('Penjelasan', 'Klik ', 'Garis =')) and fig not in ('1.1', '3.1'): break
            kill.add(k); n += 1; k -= 1
    return [it for i, it in enumerate(items) if i not in kill]

# ---------------------------------------------------------------- flowables
class CodeBox(Flowable):
    """Splittable dark code block with line numbers."""
    def __init__(self, lines, start=1, numbered=True, bg=CODEBG, fg=CODEFG, maxchars=96, font=7.7, header=None, hcolor=None):
        super().__init__(); self.header = header; self.hcolor = hcolor or colors.HexColor('#1E4F6F'); self.lines = lines; self.start = start; self.numbered = numbered
        self.bg = bg; self.fg = fg; self.maxchars = maxchars; self.font = font; self.lead = font * 1.28; self._wrapped = None
    def _w(self):
        if self._wrapped is None:
            out = []
            for n, line in enumerate(self.lines):
                t = line.expandtabs(4)
                first = True
                while len(t) > self.maxchars:
                    cut = t.rfind(' ', 20, self.maxchars)
                    if cut < 20: cut = self.maxchars
                    out.append((n + 1 if first else None, t[:cut])); first = False
                    t = '    ' + t[cut:].lstrip()
                out.append((n + 1 if first else None, t))
            self._wrapped = out
        return self._wrapped
    def wrap(self, aw, ah):
        self.width = aw; self.hh = 17 if self.header else 0; self.height = len(self._w()) * self.lead + 10 + self.hh; return aw, self.height
    def split(self, aw, ah):
        w = self._w(); hh = 17 if self.header else 0; room = int((ah - 10 - hh) / self.lead)
        if room < 3 or len(w) <= room: return []
        a = CodeBox([], 1, self.numbered, self.bg, self.fg, self.maxchars, self.font, self.header, self.hcolor); a._wrapped = w[:room]
        b = CodeBox([], 1, self.numbered, self.bg, self.fg, self.maxchars, self.font); b._wrapped = w[room:]
        return [a, b]
    def draw(self):
        c = self.canv; c.setFillColor(self.bg); c.rect(0, 0, self.width, self.height, fill=1, stroke=0)
        if self.header:
            c.setFillColor(self.hcolor); c.rect(0, self.height - 17, self.width, 17, fill=1, stroke=0)
            c.setFillColor(colors.white); c.setFont('Sans-B', 8.2); c.drawString(7, self.height - 11.8, self.header[:130])
        c.setFont('Courier', self.font); y = self.height - 5 - self.font - (17 if self.header else 0)
        for no, t in self._w():
            if self.numbered and no is not None:
                c.setFillColor(NUM); c.drawRightString(22, y, str(no))
            c.setFillColor(self.fg); c.drawString(28 if self.numbered else 8, y, t); y -= self.lead

def wrap_code(lines, maxchars=92):
    out = []
    for line in lines:
        t = line.expandtabs(4)
        while len(t) > maxchars:
            cut = t.rfind(' ', 20, maxchars)
            if cut < 20: cut = maxchars
            out.append(t[:cut]); t = '    ' + t[cut:].lstrip()
        out.append(t)
    return out

def bar(text, color=colors.HexColor('#2B3445')):
    t = Table([[Paragraph(inline(text, False), ST['bar'])]], colWidths=[W])
    t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), color), ('LEFTPADDING', (0, 0), (-1, -1), 7),
                           ('TOPPADDING', (0, 0), (-1, -1), 4), ('BOTTOMPADDING', (0, 0), (-1, -1), 4)]))
    t.keepWithNext = 1
    return t

class Badge(Flowable):
    def __init__(self, n): super().__init__(); self.n = str(n); self.width = 6 * mm; self.height = 5.2 * mm
    def draw(self):
        c = self.canv; c.setFillColor(TEAL); c.circle(3 * mm, 2.6 * mm, 2.5 * mm, fill=1, stroke=0)
        c.setFillColor(colors.white); c.setFont('Sans-B', 6.8); c.drawCentredString(3 * mm, 1.7 * mm, self.n)

def terminal_flow(title, desc, items):
    label = title + ((' | ' + desc) if desc else '')
    fl = []; first = True
    for n, it in enumerate(items, 1):
        code = Preformatted('\n'.join(wrap_code(it['code'])), S('cmd', fontName='Courier', fontSize=7.9, leading=10.2, textColor=CODEFG), maxLineLength=None)
        rows = [[Badge(n), code]]
        if it['expl']:
            rows.append(['', Paragraph(inline(it['expl']).replace('Penjelasan:', '<b>Penjelasan:</b>', 1), ST['expl'])])
        t = Table(rows, colWidths=[8 * mm, W - 8 * mm])
        sty = [('VALIGN', (0, 0), (0, 0), 'TOP'), ('BACKGROUND', (1, 0), (1, 0), CODEBG),
               ('LEFTPADDING', (1, 0), (1, 0), 7), ('RIGHTPADDING', (1, 0), (1, 0), 6),
               ('TOPPADDING', (1, 0), (1, 0), 4), ('BOTTOMPADDING', (1, 0), (1, 0), 4),
               ('LEFTPADDING', (0, 0), (0, -1), 0), ('TOPPADDING', (0, 0), (0, 0), 5),
               ('TOPPADDING', (0, 0), (-1, 0), 2 if n > 1 else 0), ('BOTTOMPADDING', (0, 0), (0, -1), 0)]
        if it['expl']:
            sty += [('LEFTPADDING', (1, 1), (1, 1), 2), ('TOPPADDING', (1, 1), (1, 1), 3), ('BOTTOMPADDING', (1, 1), (1, 1), 4)]
        t.setStyle(TableStyle(sty))
        if first:
            fl.append(KeepTogether([bar(label), t])); first = False
        else:
            fl.append(KeepTogether([t]))
    if not items: fl.append(bar(label))
    fl.append(Spacer(1, 5))
    return fl

def file_flow(title, desc, items):
    label = (title if title.startswith('BERKAS') else 'BERKAS: ' + title) + ((' | ' + desc) if desc else '')
    fl = []
    for n, it in enumerate(items):
        fl.append(CodeBox(it['code'], 1, True, header=(label if n == 0 else None)))
        if it['expl']: fl.append(Paragraph(inline(it['expl']), ST['expl']))
    fl.append(Spacer(1, 6))
    return fl

def callout(kind, title, paras):
    cmap = {'CATATAN': (C_NOTE, 'CATATAN'), 'TIPS': (C_TIP, 'TIPS'), 'PERINGATAN': (C_WARN, 'PERINGATAN'), 'KEAMANAN': (C_SEC, 'KEAMANAN')}
    (bg, fg), lab = cmap[kind]
    head = '<font color="%s"><b>%s</b></font>' % (fg.hexval().replace('0x', '#'), lab)
    if title and title.lower() != lab.lower(): head += ' <font color="%s"><b>- %s</b></font>' % (fg.hexval().replace('0x', '#'), escape(title))
    rows = [[Paragraph(head, ST['call'])]] + [[P(p, 'call')] for p in paras if p]
    t = Table(rows, colWidths=[W - 3])
    t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), bg), ('LINEBEFORE', (0, 0), (0, -1), 3, fg),
                           ('LEFTPADDING', (0, 0), (-1, -1), 8), ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                           ('TOPPADDING', (0, 0), (-1, -1), 2.5), ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
                           ('TOPPADDING', (0, 0), (-1, 0), 5), ('BOTTOMPADDING', (0, -1), (-1, -1), 6)]))
    return [KeepTogether([t]), Spacer(1, 6)]

def fields_box(label, title, fields, pal):
    bg, fg = pal; col = fg.hexval().replace('0x', '#')
    head = '<font color="%s"><b>%s%s</b></font>' % (col, label, (' - ' + escape(title)) if title else '')
    rows = [[Paragraph(head, ST['call'])]]
    for k, v in fields:
        rows.append([Paragraph(('<b>%s:</b> ' % k if k else '') + inline(v), ST['call'])])
    t = Table(rows, colWidths=[W - 3])
    t.setStyle(TableStyle([('BACKGROUND', (0, 0), (-1, -1), bg), ('LINEBEFORE', (0, 0), (0, -1), 3, fg),
                           ('LEFTPADDING', (0, 0), (-1, -1), 8), ('RIGHTPADDING', (0, 0), (-1, -1), 8),
                           ('TOPPADDING', (0, 0), (-1, -1), 2.5), ('BOTTOMPADDING', (0, 0), (-1, -1), 2.5),
                           ('TOPPADDING', (0, 0), (-1, 0), 5), ('BOTTOMPADDING', (0, -1), (-1, -1), 6)]))
    return [KeepTogether([t]), Spacer(1, 6)]

def table_flow(rows):
    n = max(len(r) for r in rows); rows = [r + [''] * (n - len(r)) for r in rows]
    # column weights
    wts = []
    for c in range(n):
        col = [r[c] for r in rows[1:]] or ['']
        longest = max((len(x) for x in col + [rows[0][c]]), default=4)
        avg = sum(len(x) for x in col) / max(1, len(col))
        wts.append(max(6, min(55, 0.55 * avg + 0.45 * longest * 0.6 + len(rows[0][c]) * 0.2)))
    tot = sum(wts); mins = 15 * mm
    widths = [max(mins, W * w / tot) for w in wts]
    sc = W / sum(widths); widths = [w * sc for w in widths]
    data = [[Paragraph(inline(c, False), ST['cellh']) for c in rows[0]]]
    for r in rows[1:]:
        data.append([P(c, 'cell') for c in r])
    t = Table(data, colWidths=widths, repeatRows=1, hAlign='LEFT')
    sty = [('BACKGROUND', (0, 0), (-1, 0), NAVY), ('GRID', (0, 0), (-1, -1), 0.4, GRID), ('VALIGN', (0, 0), (-1, -1), 'TOP'),
           ('LEFTPADDING', (0, 0), (-1, -1), 4), ('RIGHTPADDING', (0, 0), (-1, -1), 4),
           ('TOPPADDING', (0, 0), (-1, -1), 3), ('BOTTOMPADDING', (0, 0), (-1, -1), 3)]
    for i in range(1, len(data)):
        if i % 2 == 0: sty.append(('BACKGROUND', (0, i), (-1, i), colors.HexColor('#F3F6FA')))
    t.setStyle(TableStyle(sty))
    return [Spacer(1, 2), t, Spacer(1, 7)]

# ---------------------------------------------------------------- native figures
class Topology(Flowable):
    def __init__(self, w=W, h=70 * mm): super().__init__(); self.width = w; self.height = h
    def draw(self):
        c = self.canv; w = self.width; h = 82 * mm; c.saveState(); c.scale(1, self.height / h)
        def box(cx, cy, bw, bh, lines, fill=colors.HexColor('#EEF3F8'), stroke=colors.HexColor('#7E93A8'), dash=False):
            c.setFillColor(fill); c.setStrokeColor(stroke); c.setLineWidth(0.9)
            if dash: c.setDash(3, 2)
            c.roundRect(cx - bw / 2, cy - bh / 2, bw, bh, 4, fill=1, stroke=1); c.setDash()
            c.setFillColor(INK); n = len(lines); y = cy + (n - 1) * 4.2 - 2.5
            for i, (t, b) in enumerate(lines):
                c.setFont('Sans-B' if b else 'Sans', 7.2 if b else 6.6); c.drawCentredString(cx, y - i * 8.4, t)
        def ln(x1, y1, x2, y2):
            c.setStrokeColor(colors.HexColor('#51657A')); c.setLineWidth(1); c.line(x1, y1, x2, y2)
        cx = w / 2
        box(cx, h - 8 * mm, 52 * mm, 9 * mm, [('IndiHome (uplink WiFi)', 1)])
        box(cx, h - 24 * mm, 52 * mm, 11 * mm, [('TL-WR840N (mode WISP)', 1), ('LAN 192.168.0.1', 0)])
        box(cx, h - 43 * mm, 78 * mm, 14 * mm, [('MikroTik RB750GL', 1), ('ether1 = 192.168.0.100 (dari WR840N)', 0), ('LAN 192.168.88.1/24, DHCP .100-.254', 0)])
        ln(cx, h - 12.5 * mm, cx, h - 18.5 * mm); ln(cx, h - 29.5 * mm, cx, h - 36 * mm)
        bw = 38 * mm; gap = (w - 4 * bw) / 5; y = 12 * mm
        specs = [([('STB HG680', 1), ('AdGuard Home', 0), ('192.168.88.253', 0)], False),
                 ([('TL-WR820N (AP)', 1), ('mode Access Point', 0), ('192.168.88.2', 0)], False),
                 ([('Switch LiteWave', 1), ('LS1005', 0), ('(opsional)', 0)], False),
                 ([('ThinkCentre M710q', 1), ('Host sementara', 0), ('192.168.0.200', 0), ('Target rumah .88.10', 0)], True)]
        for i, (lines, dash) in enumerate(specs):
            x = gap + bw / 2 + i * (bw + gap)
            box(x, y + 8 * mm, bw, 16 * mm, lines, fill=colors.HexColor('#FFF6E0') if dash else colors.HexColor('#EAF4EE'),
                stroke=colors.HexColor('#C98A10') if dash else colors.HexColor('#5E8F74'), dash=dash)
            ln(cx, h - 50 * mm, x, y + 16 * mm)
        c.setFillColor(GRAY); c.setFont('Sans-I', 7); c.drawString(0, 1.5 * mm, 'Garis = kabel LAN (kecuali uplink IndiHome). Kotak putus-putus = rencana.'); c.restoreState()

class FormFig(Flowable):
    def __init__(self, title, rows, buttons, w=150 * mm):
        super().__init__(); self.t = title; self.rows = rows; self.b = buttons; self.width = w
        self.height = 11 * mm + len(rows) * 7.2 * mm + 13 * mm
    def draw(self):
        c = self.canv; w = self.width; h = self.height
        c.setStrokeColor(colors.HexColor('#6C7686')); c.setFillColor(colors.white); c.rect(0, 0, w, h, fill=1, stroke=1)
        c.setFillColor(colors.HexColor('#2F3541')); c.rect(0, h - 8 * mm, w, 8 * mm, fill=1, stroke=0)
        c.setFillColor(colors.white); c.setFont('Sans-B', 8.4); c.drawString(4 * mm, h - 5.3 * mm, self.t)
        y = h - 8 * mm - 7.5 * mm
        for n, lab, val in self.rows:
            if n:
                c.setFillColor(colors.HexColor('#3A4352')); c.circle(6 * mm, y + 1.6 * mm, 2.2 * mm, fill=1, stroke=0)
                c.setFillColor(colors.white); c.setFont('Sans-B', 6.6); c.drawCentredString(6 * mm, y + 0.7 * mm, str(n))
            c.setFillColor(INK); c.setFont('Sans', 7.6); c.drawString(11 * mm, y + 0.7 * mm, lab)
            c.setFillColor(colors.HexColor('#EEF1F4')); c.setStrokeColor(colors.HexColor('#B6BEC9')); c.rect(w * 0.43, y - 1.4 * mm, w * 0.54, 6 * mm, fill=1, stroke=1)
            c.setFillColor(INK); c.setFont('Sans', 7.4); c.drawString(w * 0.43 + 2 * mm, y + 0.6 * mm, val); y -= 7.2 * mm
        bx = w - 3 * mm
        for b in reversed(self.b):
            bwid = 8 * mm + len(b) * 1.6 * mm
            c.setFillColor(colors.HexColor('#E3E7EC')); c.setStrokeColor(colors.HexColor('#8E98A6')); c.roundRect(bx - bwid, 2.5 * mm, bwid, 6 * mm, 1.5, fill=1, stroke=1)
            c.setFillColor(INK); c.setFont('Sans-B', 7.4); c.drawCentredString(bx - bwid / 2, 4.4 * mm, b); bx -= bwid + 2.5 * mm

NATIVE = {
    '1.1': lambda: Topology(), '3.1': lambda: Topology(),
    '8.1': lambda: FormFig('Proxmox VE Installer - Target Harddisk',
        [(1, 'Target harddisk', '/dev/nvme0n1 (465.76GiB, NVMe SSD 500GB)'), (2, 'Filesystem (klik Options)', 'ext4'),
         (None, 'hdsize', '465.8'), (None, 'swapsize', '(otomatis)'), (None, 'maxroot / minfree / maxvz', '(kosongkan)')], ['Options', 'Next']),
    '8.4': lambda: FormFig('Proxmox VE Installer - Management Network Configuration',
        [(1, 'Management Interface', 'enp0s31f6 - XX:XX:XX:XX:XX:XX (e1000e)'), (2, 'Hostname (FQDN)', 'pve.lab.local'),
         (3, 'IP Address (CIDR)', '192.168.88.10 / 24'), (4, 'Gateway', '192.168.88.1'), (5, 'DNS Server', '192.168.88.253')], ['Previous', 'Next']),
    '8.5': lambda: FormFig('Proxmox VE Installer - Summary',
        [(None, 'Filesystem', 'ext4'), (None, 'Disk', '/dev/nvme0n1'), (None, 'Country / Time zone', 'Indonesia / Asia/Jakarta'),
         (None, 'Keyboard / Email', 'us / admin@lab.local'), (None, 'Management interface', 'enp0s31f6'),
         (1, 'Hostname / IP / Gateway', 'pve.lab.local / 192.168.88.10/24 / 192.168.88.1'), (2, 'Automatically reboot', '[x] centang')], ['Previous', 'Install']),
}

def figure_flow(fig, cap):
    fl = []
    if fig in NATIVE:
        fl.append(NATIVE[fig]())
    else:
        f = FIG_DIR / ('g' + fig.replace('.', '_') + '.png')
        if f.exists():
            from PIL import Image as PI
            w, h = PI.open(f).size
            mw = W; mh = 200 * mm
            sc = min(mw / w, mh / h, 0.48 * 72 / 170 * 3.2)
            sc = min(mw / w, mh / h)
            tw = w * sc; th = h * sc
            if tw > 150 * mm: tw, th = 150 * mm, th * 150 * mm / (w * sc)
            fl.append(Image(str(f), tw, th))
    cp = Paragraph('<b>Gambar %s</b> - %s' % (fig, inline(cap, False)), ST['cap'])
    return [KeepTogether(fl + [cp])]

# ---------------------------------------------------------------- front matter / cover
EDITION = 'Edisi Terpadu 2026.11'
DATE = '1 November 2026'
class Cover(Flowable):
    def __init__(self): super().__init__(); self.width = W; self.height = 250 * mm
    def draw(self):
        c = self.canv; w = self.width; h = self.height
        c.saveState(); c.translate(-22 * mm, -17 * mm)
        pw, ph = A4
        c.setFillColor(NAVY); c.rect(0, 0, pw, ph, fill=1, stroke=0)
        c.setFillColor(TEAL); c.rect(0, ph - 5 * mm, pw, 5 * mm, fill=1, stroke=0)
        c.setFillColor(colors.white); c.setFont('Sans-B', 36)
        c.drawString(22 * mm, ph - 70 * mm, 'Buku Panduan'); c.drawString(22 * mm, ph - 85 * mm, 'Home Server Lab')
        c.setFillColor(colors.HexColor('#C9D9E8')); c.setFont('Sans', 12.5)
        c.drawString(22 * mm, ph - 104 * mm, 'Dari persiapan komputer hingga pemulihan layanan:')
        c.drawString(22 * mm, ph - 111 * mm, 'langkah rinci, diagram, perintah, dan pemecahan masalah.')
        c.setStrokeColor(TEAL); c.setLineWidth(1.6); c.line(22 * mm, ph - 124 * mm, pw - 22 * mm, ph - 124 * mm)
        c.setFillColor(colors.HexColor('#E3EDF5')); c.setFont('Sans', 10.5)
        for i, t in enumerate(['Proxmox VE di Lenovo ThinkCentre M710q', 'MikroTik | Debian 13 | Docker | Tailscale | Caddy',
                               'Backup (PBS) | Keamanan | Monitoring | Home Assistant | k3s', '56 bab, 4 lampiran, 9 panduan fase, roadmap']):
            c.drawString(22 * mm, ph - (136 + i * 8) * mm, t)
        c.setFillColor(colors.HexColor('#FFF1D0')); c.roundRect(22 * mm, 38 * mm, pw - 44 * mm, 40 * mm, 3 * mm, fill=1, stroke=0)
        c.setFillColor(NAVY); c.setFont('Sans-B', 9.5); c.drawString(28 * mm, 70 * mm, 'STATUS PROYEK PER 1 NOVEMBER 2026')
        c.setFont('Sans', 9)
        for i, t in enumerate(['Proxmox VE 9.2.24 berjalan; kernel 7.0.14-26-pve.', 'Template Debian 13 VM 200 dan CT 100 sudah dibuat.',
                               'Host sementara 192.168.0.200; target MikroTik 192.168.88.10.']):
            c.drawString(28 * mm, (62 - i * 6) * mm, t)
        c.setFillColor(colors.HexColor('#9FB4C8')); c.setFont('Sans', 9.5)
        c.drawString(22 * mm, 24 * mm, '%s - %s' % (EDITION, DATE))
        c.restoreState()

def front_matter():
    f = [Cover(), PageBreak()]
    f.append(Paragraph('Tentang Edisi Ini', ST['h1']))
    f.append(P('Panduan menyeluruh dari persiapan komputer, jaringan, instalasi Proxmox, VM/LXC, layanan, keamanan, backup, pemantauan, hingga pemulihan. '
               'Edisi ini menggabungkan Bab 1-56, lampiran, serta sembilan pengantar dan penutup fase dari materi proyek yang masih berlaku. '
               'Tata letak (kotak perintah bernomor, kotak berkas, tabel, catatan, dan gambar) dipulihkan dengan gaya Edisi 2; isi mengikuti sumber terbaru di repositori.'))
    f += callout('PERINGATAN', 'Status aktual', ['Proxmox VE 9.2.24 berjalan pada ThinkCentre M710q; kernel aktif 7.0.14-26-pve. RAM 16+8 GB terbaca sebagai 23 GiB. '
        'NVMe Samsung berkapasitas 476,9 GB terdeteksi. Template Debian 13 VM 200 dan CT 100 telah dibuat; spesifikasi CT: 1 CPU, 512 MiB RAM, 512 MiB swap, disk 8 GiB. '
        'Host masih memakai jaringan sementara 192.168.0.200/24; target pindah ke MikroTik 192.168.88.10 belum diterapkan. Layanan, backup, HDD, dan hasil clone belum diuji.'])
    f.append(Paragraph('Sebelum mulai', ST['h2']))
    for t in ['Baca bab secara berurutan dan kerjakan satu perubahan pada satu waktu.',
              'Gunakan direktori konfigurasi/ di repositori sebagai sumber YAML/Compose yang benar bila ada perbedaan dengan teks buku.',
              'Jangan menaruh password, token, private key, serial disk, atau konfigurasi rahasia di GitHub, buku, tangkapan layar, atau chat.',
              'Operasi instalasi, partisi, firewall, SSH, hapus guest, dan ubah jaringan dapat memutus akses atau menghapus data. Baca peringatan dan siapkan konsol lokal sebelum menekan Apply.',
              'Jika hasil berbeda dari petunjuk, berhenti, simpan pesan error persis, dan catat di catatan/hasil-uji.md.',
              'Label [BELUM PASTI] harus diverifikasi pada perangkat/versi aktual. Panduan ini bukan bukti bahwa server sudah berhasil dipasang.',
              'Nomor bab 5, 7, dan 29 tidak ada: bab itu (lab VMware dan instal-ke-disk-dulu) dihapus pada Revisi 3, dan nomor bab lain dipertahankan agar rujukan silang tetap benar.']:
        f.append(Paragraph('- ' + inline(t), ST['bul']))
    f.append(Paragraph('Peta jaringan aktual dan target', ST['h2']))
    f += [Topology(), Spacer(1, 3), Paragraph('Host Proxmox saat ini berada di jaringan router sementara pada 192.168.0.200/24. Alamat 192.168.88.10 adalah target ketika host disambungkan kembali ke MikroTik; perubahan belum diterapkan. Jangan membuka panel admin ke internet. Akses Tailscale dan aplikasi privat belum aktif sampai dikonfigurasi dan diuji.', ST['cap'])]
    f.append(Paragraph('Koreksi keamanan dan versi terbaru', ST['h2']))
    f.append(P('Revisi 4 mengatur kebijakan Tailscale untuk grup admin, memperbaiki jalur data PostgreSQL 18 pada n8n, mematikan pendaftaran Vaultwarden secara default, '
               'dan memperluas .gitignore. Baca docs/bab/REVISI-4.md. Nilai email Tailscale pada contoh masih placeholder dan wajib diganti sebelum kebijakan diterapkan.'))
    f.append(P('Revisi 5 mencatat diagnosis DNS, update Proxmox, KVM/VT-x, dan jaringan sementara. Revisi 6 mencatat template Debian 13 VM 200 dan CT 100 serta langkah menuju MikroTik. Baca docs/bab/REVISI-5.md dan docs/bab/REVISI-6.md.', 'body'))
    f += [PageBreak(), Paragraph('Daftar Isi', ST['h1'])]
    return f

# ---------------------------------------------------------------- document
class Doc(BaseDocTemplate):
    def __init__(self, path):
        super().__init__(str(path), pagesize=A4, leftMargin=20 * mm, rightMargin=20 * mm, topMargin=18 * mm, bottomMargin=20 * mm,
                         title='Buku Panduan Home Server Lab - %s' % EDITION, author='Home Server Lab')
        fr = Frame(self.leftMargin, self.bottomMargin, self.width, self.height, 0, 0, 0, 0)
        self.addPageTemplates([PageTemplate(id='all', frames=fr, onPage=self.deco)])
    def deco(self, c, d):
        if d.page == 1: return
        c.saveState(); c.setStrokeColor(GRID); c.line(20 * mm, 14 * mm, A4[0] - 20 * mm, 14 * mm)
        c.setFont('Sans', 7.4); c.setFillColor(GRAY)
        c.drawString(20 * mm, 9.5 * mm, 'Buku Panduan Home Server Lab - %s' % EDITION)
        c.drawRightString(A4[0] - 20 * mm, 9.5 * mm, 'Halaman %d' % d.page); c.restoreState()
    def afterFlowable(self, f):
        lvl = getattr(f, 'toc_level', None)
        if lvl is not None:
            title = f.getPlainText(); key = 'b%d_%d' % (self.page, abs(hash(title)) % 10**8)
            self.canv.bookmarkPage(key); self.canv.addOutlineEntry(title, key, level=lvl, closed=(lvl == 0))
            self.notify('TOCEntry', (lvl, title, self.page, key))

def heading(text, lvl):
    p = Paragraph(inline(text, False), ST['h%d' % (lvl + 1)] if lvl < 2 else ST['h3'])
    if lvl < 2: p.toc_level = lvl
    return p

def render(blocks):
    story = front_matter()
    toc = TableOfContents(); toc.levelStyles = [ST['toc0'], ST['toc1']]
    toc.dotsMinLevel = 1
    story.append(toc)
    first_h1 = True
    for b in blocks:
        k = b[0]
        if k == 'seg': continue
        if k == 'h1':
            story += [PageBreak(), heading(b[1], 0)]
        elif k == 'h2': story.append(CondPageBreak(40 * mm)); story.append(heading(b[1], 1))
        elif k == 'h3': story.append(heading(b[1], 2))
        elif k == 'para': story.append(P(b[1]))
        elif k == 'bullet': story.append(Paragraph('<font color="#1F7A8C">&bull;</font>&nbsp; ' + inline(b[1]), ST['bul']))
        elif k == 'step':
            story.append(Paragraph('<font name="Sans-B" color="#1F7A8C">%s.</font>&nbsp; %s' % (b[1], inline(b[2])), ST['step']))
        elif k == 'expl':
            story.append(Paragraph(inline(b[1]).replace('Penjelasan:', '<b>Penjelasan:</b>', 1), S('ex2', parent=None, fontSize=8.5, leading=11.6, leftIndent=16, textColor=colors.HexColor('#3C4655'), spaceAfter=4)))
        elif k == 'code':
            story += [CodeBox(b[1], 1, False), Spacer(1, 6)]
        elif k == 'output':
            story += [Paragraph('<b>%s</b>' % inline(b[1], False), ST['expl']), CodeBox(b[2], 1, False, bg=colors.HexColor('#F4F1E6'), fg=colors.HexColor('#3B3A2E')), Spacer(1, 6)]
        elif k == 'terminal': story += terminal_flow(b[1], b[2], b[3])
        elif k == 'file': story += file_flow(b[1], b[2], b[3])
        elif k == 'table': story += table_flow(b[1])
        elif k == 'callout': story += callout(b[1], b[2], b[3])
        elif k == 'case': story += fields_box('KASUS NYATA', b[1], b[2], C_CASE)
        elif k == 'place': story += fields_box('PENEMPATAN', b[1], b[2], C_PLACE)
        elif k == 'figure': story += figure_flow(b[1], b[2])
        elif k == 'topology': story += [Topology(), Spacer(1, 6)]
        elif k == 'roadmap':
            txt = (REPO / 'docs/12-roadmap-manfaat-keamanan.md').read_text(encoding='utf-8').splitlines()[1:]
            items, _ = apply_oracle(tokenize('\n'.join(txt)))
            sub = Parser(items, 'roadmap').parse()
            for x in sub:
                if x[0] == 'h1': story.append(heading(x[1], 1))
                elif x[0] in ('h2',): story.append(heading(x[1], 2))
            # simple second pass using the same renderer
            story += render_blocks_simple(sub)
    return story

def render_blocks_simple(sub):
    st = []
    for b in sub:
        k = b[0]
        if k in ('h1', 'h2'): continue
        if k == 'h3': st.append(heading(b[1], 2))
        elif k == 'para': st.append(P(b[1]))
        elif k == 'bullet': st.append(Paragraph('<font color="#1F7A8C">&bull;</font>&nbsp; ' + inline(b[1]), ST['bul']))
        elif k == 'step': st.append(Paragraph('<font name="Sans-B" color="#1F7A8C">%s.</font>&nbsp; %s' % (b[1], inline(b[2])), ST['step']))
        elif k == 'table': st += table_flow(b[1])
        elif k == 'callout': st += callout(b[1], b[2], b[3])
        elif k == 'code': st += [CodeBox(b[1], 1, False), Spacer(1, 6)]
    return st

def main():
    spec = importlib.util.spec_from_file_location('bh', REPO / 'tools/build_handbook.py')
    bh = importlib.util.module_from_spec(spec); spec.loader.exec_module(bh)
    book_md = bh.source_content()
    parts = re.split(r'\n<!-- SOURCE: (.+?) -->\n', book_md)
    segs = [(parts[i], parts[i + 1]) for i in range(1, len(parts) - 1, 2)]
    if LIMIT: segs = segs[:LIMIT]
    print('segments:', len(segs))
    blocks = build_blocks(segs)
    from collections import Counter
    print(Counter(b[0] for b in blocks))
    story = render(blocks)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc = Doc(OUT); doc.multiBuild(story)
    print('pages:', doc.page, '->', OUT)

if __name__ == '__main__':
    main()
