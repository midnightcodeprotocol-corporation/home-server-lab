"""Build the complete Home Server Lab book from current repository chapters.

Usage: python tools/build_handbook.py [--pdf PATH] [--markdown PATH]
Requires reportlab (the Codex bundled Python runtime includes it).
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path
from html import unescape
from xml.sax.saxutils import escape

import reportlab
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (BaseDocTemplate, CondPageBreak, Flowable, Frame,
    KeepTogether, PageBreak, PageTemplate, Paragraph, Spacer, Table, TableStyle)
from reportlab.platypus.tableofcontents import TableOfContents

ROOT = Path(__file__).resolve().parents[1]
EDITION = "Edisi Terpadu 2026.11"
DATE = "1 November 2026"

EDISI2_INDEX = ROOT / "docs/bab/edisi2/README.md"
SUPPLEMENT_INDEX = ROOT / "docs/bab/suplemen/README.md"

def parse_index(path: Path) -> list[tuple[str, Path]]:
    entries = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.startswith("- [") or "(Dihapus)" in line:
            continue
        match = re.search(r"\[([^\]]+)\]\(([^)]+\.md)\)", line)
        if not match:
            continue
        title, rel = match.groups()
        target = (path.parent / rel).resolve()
        if target.exists():
            entries.append((title, target))
    return entries

def source_content() -> str:
    ed2 = parse_index(EDISI2_INDEX)
    supp = parse_index(SUPPLEMENT_INDEX)
    def pick(entries, pattern):
        return next((p for _, p in entries if pattern in p.name), None)
    def chapter(entries, number):
        return next((p for _, p in entries if re.match(rf"{number:02d}-", p.name)), None)
    def phase(entries, n, ending=False):
        suffix = "99-penutup" if ending else "00-pengantar"
        return next((p for _, p in entries if p.name.startswith(f"bagian-{n}-{suffix}")), None)
    ordered: list[tuple[str,Path]] = []
    # First book: Bab 1-24, then Appendices A-D as ordered by its index.
    ordered.extend(ed2)
    # Suplemen grouped by the work phases so the reading order follows the project.
    ordered += [("Pengantar Fase 1", phase(supp,1)), ("Bab 25",chapter(supp,25)), ("Bab 26",chapter(supp,26)), ("Penutup Fase 1",phase(supp,1,True))]
    ordered += [("Pengantar Fase 2", phase(supp,2))] + [(f"Bab {n}",chapter(supp,n)) for n in (27,28,30)] + [("Penutup Fase 2",phase(supp,2,True)), ("Bab 31",chapter(supp,31))]
    ordered += [("Pengantar Fase 3",phase(supp,3))] + [(f"Bab {n}",chapter(supp,n)) for n in (32,33,34)] + [("Penutup Fase 3",phase(supp,3,True))]
    ordered += [("Pengantar Fase 4",phase(supp,4))] + [(f"Bab {n}",chapter(supp,n)) for n in (35,36,37,38)] + [("Penutup Fase 4",phase(supp,4,True))]
    ordered += [("Pengantar Fase 5",phase(supp,5))] + [(f"Bab {n}",chapter(supp,n)) for n in (39,40,41,42,43,44)] + [("Penutup Fase 5",phase(supp,5,True))]
    ordered += [("Pengantar Fase 6",phase(supp,6))] + [(f"Bab {n}",chapter(supp,n)) for n in (45,46,47)] + [("Penutup Fase 6",phase(supp,6,True))]
    ordered += [("Pengantar Fase 7",phase(supp,7))] + [(f"Bab {n}",chapter(supp,n)) for n in (48,49,50,51,52)] + [("Penutup Fase 7",phase(supp,7,True))]
    ordered += [("Pengantar Fase 8",phase(supp,8)), ("Bab 53",chapter(supp,53)), ("Penutup Fase 8",phase(supp,8,True))]
    ordered += [("Pengantar Fase 9",phase(supp,9))] + [(f"Bab {n}",chapter(supp,n)) for n in (54,55)] + [("Penutup Fase 9",phase(supp,9,True)), ("Bab 56",chapter(supp,56))]
    ordered = [(label,p) for label,p in ordered if p is not None]

    parts = ["""# Buku Panduan Lengkap Home Server Lab

## Edisi Terpadu 2026.11 - 1 November 2026

Panduan menyeluruh dari persiapan komputer, jaringan, instalasi Proxmox, VM/LXC, layanan, keamanan, backup, pemantauan, hingga pemulihan. Edisi ini menggabungkan Bab 1-56, lampiran, serta sembilan pengantar dan penutup fase dari materi proyek yang masih berlaku.

> **Status aktual (1 November 2026):** Proxmox VE 9.2.24 berjalan pada ThinkCentre M710q dengan kernel 7.0.14-26-pve. RAM 16+8 GB terbaca Linux sebagai 23 GiB; BIOS/MemTest86 belum diperiksa. VT-x/KVM aktif; NVMe Samsung 476,9 GB. Jaringan host sementara 192.168.0.200/24, gateway/DNS 192.168.0.1. Template Debian 13 CT 100 dan VM 200 telah diperbaiki setelah ditemukan host key SSH dan machine ID yang ikut tersalin. Clone uji lulus boot, DHCP, DNS, SSH, dan identitas baru; semua guest uji telah dihapus. Paket VM, guest layanan, backup, HDD, dan jaringan MikroTik belum diuji.

## Sebelum mulai

- Bacalah bab berurutan dan kerjakan satu perubahan pada satu waktu.
- Gunakan konfigurasi di direktori `konfigurasi/` sebagai sumber YAML/Compose yang benar; sebagian teks sumber berasal dari ekstraksi dan format kodenya perlu dicocokkan.
- Jangan menaruh password, token, private key, serial disk, atau konfigurasi rahasia di GitHub, buku, tangkapan layar, atau chat.
- Operasi instalasi, partisi, firewall, SSH, hapus guest, dan ubah jaringan dapat memutus akses atau menghapus data. Baca peringatan dan siapkan console lokal sebelum menekan Apply.
- Jika hasil berbeda dari petunjuk, berhenti, simpan pesan error persis, dan catat di `catatan/hasil-uji.md`.
- Label **[BELUM PASTI]** harus diverifikasi pada perangkat/versi aktual. Panduan ini bukan bukti bahwa server sudah berhasil dipasang.

## Peta jaringan aktual dan target

[[ILUSTRASI:JARINGAN]]

Garis dan kotak menjelaskan jaringan rumah yang sudah berjalan dan status host Proxmox. Host saat ini berada di jaringan sementara `192.168.0.200/24`; `192.168.88.10` adalah alamat target setelah disambungkan ke MikroTik. Jangan membuka panel admin ke internet. Akses Tailscale dan aplikasi privat belum aktif sampai dikonfigurasi dan diuji.

## Koreksi keamanan dan versi terbaru


## Daftar isi

"""]
    for label,p in ordered:
        rel=p.relative_to(ROOT).as_posix()
        # Keep source paths visible for later maintenance and verification.
        content=p.read_text(encoding="utf-8").strip()
        # The original first chapter used plain text rows instead of Markdown
        # tables. Preserve those columns in the compiled book so the glossary
        # and equipment inventory remain easy to scan.
        if p.name == "01-gambaran-besar.md":
            replacements = [
                (("## 1.2 Perangkat yang dipakai", "## 1.3 Prinsip:"), """
## 1.2 Perangkat yang dipakai

| Perangkat | Peran | Keterangan |
| --- | --- | --- |
| IndiHome | Sumber internet | Tidak ada kabel LAN yang bisa dipakai, jadi uplink lewat WiFi. |
| TP-Link TL-WR840N | Router penerima | Mode WISP: menerima WiFi IndiHome, memberi kabel LAN ke MikroTik. |
| MikroTik RB750GL | Router utama | Gateway, DHCP, dan firewall jaringan rumah (192.168.88.0/24). |
| TP-Link TL-WR820N | Access Point | Mode AP di belakang MikroTik untuk WiFi rumah. |
| TP-Link LiteWave LS1005 | Switch | Memperbanyak port LAN. |
| STB HG680 (Armbian) | DNS utama + Tailscale | AdGuard Home dan Tailscale, selalu hidup, di luar Proxmox. |
| Lenovo ThinkCentre M710q | Server Proxmox | Core i5-6500T; RAM 16+8 GB (Linux melaporkan 23 GiB; BIOS/MemTest belum diverifikasi); NVMe Samsung 476,9 GB; Proxmox berjalan, VT-x/KVM aktif. |
| HDD 2 TB | Disk data / backup | Disk kedua (bay 2,5\" atau USB), dipakai untuk datastore backup. |

"""),
                (("## 1.3 Prinsip:", "## 1.4 Topologi jaringan"), """
## 1.3 Prinsip: yang kritis dipisah dari yang bereksperimen

Server Proxmox akan sering di-reboot, di-update, dan kadang rusak karena eksperimen. Karena itu layanan yang menjaga internet dan akses jarak jauh rumah tidak ditaruh di dalamnya.

| Selalu hidup (di luar Proxmox) | Boleh sering diutak-atik (di Proxmox) |
| --- | --- |
| MikroTik, TP-Link penerima, TP-Link AP | VM Debian 13: Docker, Portainer, Git (Forgejo), Nextcloud, dashboard, Renovate |
| AdGuard Home utama di STB | Container AdGuard Home kedua (pasangan failover) |
| Tailscale (subnet router) di STB | VM Home Assistant OS |
|  | VM k3s untuk Kubernetes dan GitOps |
|  | TrueNAS (nanti, di mesin asli) |

"""),
                (("## 1.5 Konsep dasar yang sering membingungkan", "## 1.6 Cara membaca kotak di buku ini"), """
## 1.5 Konsep dasar yang sering membingungkan

Bagian ini menjawab hal-hal yang biasanya membuat orang berhenti di tengah instalasi. Baca sekali, lalu rujuk lagi saat perlu.

| Istilah | Penjelasan sederhana | Contoh di proyek ini |
| --- | --- | --- |
| IP address | Alamat sebuah perangkat di jaringan, seperti nomor rumah. | 192.168.88.10 = Proxmox |
| CIDR /24 | Menunjukkan ukuran jaringan. /24 berarti tiga angka pertama sama untuk semua perangkat (192.168.88.x). Setara subnet mask 255.255.255.0. | 192.168.88.10/24 |
| Gateway | Perangkat tempat semua lalu lintas ke luar jaringan dititipkan (biasanya router). | MikroTik: 192.168.88.1 |
| DNS | Penerjemah nama situs (google.com) menjadi alamat IP. | AdGuard: 192.168.88.253 |
| DHCP | Layanan yang membagikan IP otomatis ke perangkat yang baru tersambung. | MikroTik, pool .100 sampai .254 |
| Static lease | Pengaturan DHCP agar satu perangkat selalu mendapat IP yang sama (berdasarkan MAC). | Proxmox VM, LXC, STB |
| MAC address | Nomor unik kartu jaringan (contoh BC:24:11:AA:BB:CC). Dipakai DHCP untuk mengenali perangkat. | Lihat di tab Hardware VM |
| ISO | Berkas salinan DVD instalasi. Dipasang ke VM atau ditulis ke USB. | proxmox-ve_9.2-1.iso |
| Root | Akun administrator tertinggi di Linux. | Login Proxmox, Debian, dan STB |
| Shell / Konsol / Terminal | Jendela tempat mengetik perintah teks. | Menu Shell di web Proxmox |
| Hostname / FQDN | Nama komputer / nama lengkap dengan domain. | pve / pve.lab.local |
| Node | Satu server Proxmox di dalam cluster (lab ini hanya satu node). | Node bernama pve |
| Bridge (vmbr0) | Saklar virtual di dalam Proxmox yang menghubungkan VM dan container ke kabel LAN. | vmbr0 terhubung ke kartu fisik |
| VM vs LXC | VM = komputer virtual penuh dengan kernel sendiri. LXC = container ringan yang berbagi kernel host. | LXC: AdGuard. VM: Docker, HAOS, k3s |
| Realm | Jenis otentikasi saat login web Proxmox. | Pilih Linux PAM standard authentication |

""")
            ]
            for (start, end), block in replacements:
                left=content.find(start)
                right=content.find(end, left+len(start))
                if left >= 0 and right > left:
                    content=content[:left]+block.strip()+"\n\n"+content[right:]
        content=re.sub(r"(?m)^# (.+)$",r"# \1",content)
        parts.append(f"\n<!-- SOURCE: {rel} -->\n\n{content}\n")
    parts.append("""
# Roadmap terbaru: manfaat dan keamanan

Sumber roadmap lengkap: `docs/12-roadmap-manfaat-keamanan.md`.

[[ROADMAP:INCLUDE]]

## Penutup: server dianggap siap setelah diuji

Proxmox sudah dipasang dan diperbarui. Backup, firewall, layanan, Tailscale, dan instruksi pemulihan dalam buku belum dibuktikan di mesin ini. Template VM/CT menjadi langkah pertama setelah update host dan pemeriksaan KVM. Catat uji aktual, versi, kendala, dan hasil restore sebelum menandai pekerjaan selesai. Repo menjadi catatan utama untuk perubahan konfigurasi.
""")
    return "\n".join(parts)

NAVY=colors.HexColor("#153451")
BLUE=colors.HexColor("#245B83")
TEAL=colors.HexColor("#1F8582")
INK=colors.HexColor("#253746")
PALE=colors.HexColor("#EAF2F7")
GRID=colors.HexColor("#C4D2DD")
PURPLE=colors.HexColor("#EFE9F8")
AMBER=colors.HexColor("#FFF1D5")
GREEN=colors.HexColor("#E5F3E9")
RED=colors.HexColor("#FBE9E7")

font_dir=Path(reportlab.__file__).resolve().parent/"fonts"
for name,file in [("Vera","Vera.ttf"),("Vera-Bold","VeraBd.ttf"),("Vera-Italic","VeraIt.ttf"),("Vera-BoldItalic","VeraBI.ttf")]:
    pdfmetrics.registerFont(TTFont(name,str(font_dir/file)))
pdfmetrics.registerFontFamily("Vera",normal="Vera",bold="Vera-Bold",italic="Vera-Italic",boldItalic="Vera-BoldItalic")

styles=getSampleStyleSheet()
styles.add(ParagraphStyle(name="BodyID",fontName="Vera",fontSize=9.7,leading=13.8,textColor=INK,spaceAfter=6,alignment=TA_LEFT))
styles.add(ParagraphStyle(name="PartID",fontName="Vera-Bold",fontSize=21,leading=25,textColor=NAVY,spaceBefore=14,spaceAfter=12,keepWithNext=True))
styles.add(ParagraphStyle(name="ChapterID",fontName="Vera-Bold",fontSize=17,leading=22,textColor=BLUE,spaceBefore=12,spaceAfter=8,keepWithNext=True,borderColor=TEAL,borderWidth=0,borderPadding=0))
styles.add(ParagraphStyle(name="H2ID",fontName="Vera-Bold",fontSize=11.4,leading=15,textColor=BLUE,spaceBefore=9,spaceAfter=4,keepWithNext=True))
styles.add(ParagraphStyle(name="H3ID",fontName="Vera-Bold",fontSize=10,leading=13,textColor=TEAL,spaceBefore=7,spaceAfter=3,keepWithNext=True))
styles.add(ParagraphStyle(name="BodySmall",fontName="Vera",fontSize=7.3,leading=9.4,textColor=INK))
styles.add(ParagraphStyle(name="TableHead",fontName="Vera-Bold",fontSize=7.8,leading=10,textColor=colors.white))
styles.add(ParagraphStyle(name="TableCell",fontName="Vera",fontSize=7.8,leading=10,textColor=INK))
styles.add(ParagraphStyle(name="QuoteID",fontName="Vera",fontSize=9.1,leading=12.3,leftIndent=6,rightIndent=5,textColor=NAVY,spaceAfter=6))
styles.add(ParagraphStyle(name="SmallID",fontName="Vera",fontSize=7.2,leading=9.2,textColor=colors.HexColor("#50677A"),spaceAfter=3))
styles.add(ParagraphStyle(name="CodeID",fontName="Courier",fontSize=7.4,leading=9.4,textColor=colors.white))
styles.add(ParagraphStyle(name="CoverTitle",fontName="Vera-Bold",fontSize=26,leading=31,textColor=colors.white))

def clean_unicode(s:str)->str:
    return s.translate(str.maketrans({"—":"-","–":"-","−":"-","·":"/","→":"to","×":"x","’":"'","“":"\"","”":"\"","≤":"<=","≥":">="}))

def inline(s:str)->str:
    s=escape(unescape(clean_unicode(s)))
    s=re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)",r'<link href="\2" color="#1768A0">\1</link>',s)
    s=re.sub(r"\[([^\]]+)\]\(([^)]+)\)",r"\1 (\2)",s)
    s=re.sub(r"`([^`]+)`",r'<font name="Courier" color="#153451">\1</font>',s)
    s=re.sub(r"\*\*(.+?)\*\*",r"<b>\1</b>",s)
    s=re.sub(r"(?<!\*)\*([^*]+)\*(?!\*)",r"<i>\1</i>",s)
    return s

class Diagram(Flowable):
    def __init__(self,kind,w=165*mm,h=55*mm): super().__init__();self.kind=kind;self.width=w;self.height=h
    def draw(self):
        c=self.canv;w=self.width;h=self.height;c.setFillColor(PALE);c.roundRect(0,0,w,h,6,fill=1,stroke=0)
        def box(x,y,bw,bh,title,sub,fill=colors.white):
            c.setFillColor(fill);c.setStrokeColor(GRID);c.roundRect(x,y,bw,bh,5,fill=1,stroke=1);c.setFillColor(NAVY);c.setFont("Vera-Bold",7.2);c.drawCentredString(x+bw/2,y+bh-11,title);c.setFillColor(INK);c.setFont("Vera",6)
            for n,t in enumerate(sub.split("\n")):c.drawCentredString(x+bw/2,y+bh-20-n*8,t)
        def arrow(x1,y1,x2,y2,label=""):
            c.setStrokeColor(BLUE);c.setFillColor(BLUE);c.setLineWidth(1.2);c.line(x1,y1,x2,y2)
            import math
            a=math.atan2(y2-y1,x2-x1);c.line(x2,y2,x2-4*math.cos(a-.45),y2-4*math.sin(a-.45));c.line(x2,y2,x2-4*math.cos(a+.45),y2-4*math.sin(a+.45))
            if label:c.setFont("Vera",5.8);c.drawCentredString((x1+x2)/2,(y1+y2)/2+4,label)
        if self.kind=="JARINGAN":
            items=[("Internet","IndiHome"),("WISP","TL-WR840N"),("Router","MikroTik\n.88.1"),("LAN","AP + switch"),("DNS","STB AdGuard\n.88.253"),("Host PVE","sementara .0.200\ntarget .88.10")];bw=23*mm;gap=(w-16*mm-6*bw)/5;x0=8*mm;y=(h-18*mm)/2
            for i,(a,b) in enumerate(items):box(x0+i*(bw+gap),y,bw,18*mm,a,b, GREEN if i<5 else AMBER)
            for i in range(5):arrow(x0+i*(bw+gap)+bw,y+9*mm,x0+(i+1)*(bw+gap),y+9*mm)
            c.setFont("Vera",6);c.setFillColor(INK);c.drawCentredString(w/2,5,"Internet -> jaringan rumah -> host Proxmox sementara .0.200, target rumah .88.10")
        elif self.kind=="BACKUP":
            xs=[8*mm,62*mm,116*mm]; labels=[("Guest","data kerja"),("Backup","PBS / disk"),("Salinan lain","offline / lokasi lain")]
            for x,(a,b) in zip(xs,labels):box(x,h/2-9*mm,40*mm,18*mm,a,b,GREEN)
            arrow(48*mm,h/2,62*mm,h/2,"jadwal");arrow(102*mm,h/2,116*mm,h/2,"salinan")
        elif self.kind=="PROXY":
            items=[(7,"Klien","HTTPS nama lokal"),(61,"DNS","nama -> IP Caddy"),(115,"Caddy","reverse proxy")]
            for x,a,b in items:box(x*mm,h/2-8*mm,39*mm,16*mm,a,b)
            arrow(46*mm,h/2,61*mm,h/2,"DNS");arrow(100*mm,h/2,115*mm,h/2,"HTTPS");box(61*mm,4*mm,39*mm,15*mm,"Aplikasi","port internal",GREEN);arrow(134*mm,h/2-8*mm,100*mm,12*mm)

class CodeBlock(Flowable):
    def __init__(self,lines,start=1):super().__init__();self.lines=lines;self.start=start;self.font=7.4;self.leading=9.4;self.maxchars=103;self._expanded=[]
    def _expand(self):
        if self._expanded:return self._expanded
        for line in self.lines:
            text=clean_unicode(line.expandtabs(4))
            if not text:self._expanded.append("");continue
            while len(text)>self.maxchars:
                cut=text.rfind(" ",0,self.maxchars)
                if cut<30:cut=self.maxchars
                self._expanded.append(text[:cut]);text="    "+text[cut:].lstrip()
            self._expanded.append(text)
        return self._expanded
    def wrap(self,aw,ah):self.width=aw;self.height=max(self.leading+8,len(self._expand())*self.leading+8);return self.width,self.height
    def split(self,aw,ah):
        lines=self._expand()
        if ah < self.leading+9:return []
        room=max(1,int((ah-9)/self.leading))
        if len(lines)<=room:return []
        return [CodeBlock(lines[:room],self.start),CodeBlock(lines[room:],self.start+room)]
    def draw(self):
        c=self.canv;c.setFillColor(NAVY);c.roundRect(0,0,self.width,self.height,3,fill=1,stroke=0);c.setFont("Courier",self.font);lines=self._expand();y=self.height-8
        for i,line in enumerate(lines):
            c.setFillColor(colors.HexColor("#8FB0C8"));c.drawRightString(20,y,str(self.start+i));c.setFillColor(colors.HexColor("#F2F7FA"));c.drawString(25,y,line);y-=self.leading

def add_page_header(canvas,doc):
    if doc.page==1:return
    canvas.saveState();w,h=A4;canvas.setStrokeColor(GRID);canvas.line(22*mm,14*mm,w-20*mm,14*mm);canvas.setFont("Vera",6.7);canvas.setFillColor(colors.HexColor("#526B80"));canvas.drawString(22*mm,9*mm,"Home Server Lab / "+EDITION);canvas.drawRightString(w-20*mm,9*mm,f"Halaman {doc.page}");canvas.restoreState()

class FullDoc(BaseDocTemplate):
    def __init__(self,path):
        super().__init__(str(path),pagesize=A4,leftMargin=24*mm,rightMargin=22*mm,topMargin=20*mm,bottomMargin=21*mm,title="Buku Panduan Lengkap Home Server Lab - Edisi Terpadu 2026.11",author="Home Server Lab")
        frame=Frame(self.leftMargin,self.bottomMargin,self.width,self.height,leftPadding=0,rightPadding=0,topPadding=0,bottomPadding=0,id="main")
        self.addPageTemplates(PageTemplate(id="all",frames=frame,onPage=add_page_header))
    def afterFlowable(self,f):
        if isinstance(f,Paragraph) and hasattr(f,"toc_level"):
            level=f.toc_level;title=f.getPlainText();key=f"b-{self.page}-{abs(hash(title))}"
            self.canv.bookmarkPage(key);self.canv.addOutlineEntry(title,key,level=min(level,1),closed=level==0);self.notify("TOCEntry",(level,title,self.page,key))

def cover():
    class Cover(Flowable):
        def __init__(self):super().__init__();self.width=165*mm;self.height=245*mm
        def draw(self):
            c=self.canv;w=self.width;h=self.height;c.setFillColor(NAVY);c.rect(0,0,w,h,fill=1,stroke=0);c.setFillColor(TEAL);c.rect(0,h-4*mm,w,4*mm,fill=1,stroke=0)
            c.setFillColor(colors.white);c.setFont("Vera-Bold",24);c.drawString(14*mm,h-45*mm,"Buku Panduan") ;c.drawString(14*mm,h-59*mm,"Home Server Lab")
            c.setFillColor(colors.HexColor("#DBE7F0"));c.setFont("Vera",10);c.drawString(14*mm,h-78*mm,"Dari persiapan komputer hingga pemulihan layanan:");c.drawString(14*mm,h-86*mm,"langkah rinci, diagram, perintah, dan pemecahan masalah.")
            c.setStrokeColor(TEAL);c.setLineWidth(1.5);c.line(14*mm,h-101*mm,w-14*mm,h-101*mm)
            lines=["Proxmox VE / Lenovo ThinkCentre M710q","MikroTik / Debian / Docker / backup / keamanan",f"56 bab + lampiran + 9 panduan fase",f"{EDITION} / {DATE}"]
            c.setFillColor(colors.HexColor("#E3EDF3"));c.setFont("Vera",8)
            for i,line in enumerate(lines):c.drawString(14*mm,h-119*mm-i*8*mm,line)
            c.setFillColor(AMBER);c.roundRect(14*mm,35*mm,w-28*mm,39*mm,3*mm,fill=1,stroke=0);c.setFillColor(NAVY);c.setFont("Vera-Bold",8);c.drawString(19*mm,63*mm,"STATUS PROYEK PER 1 NOVEMBER 2026")
            c.setFont("Vera",7.2)
            for i,line in enumerate(["Proxmox VE 9.2.24; kernel 7.0.14-26-pve.","Template CT 100/VM 200 diperbaiki; clone lulus.", "Identitas SSH dan machine ID unik sudah diuji.", "Host sementara .0.200; gateway/DNS .0.1."]):c.drawString(19*mm,54*mm-i*5*mm,line)
    return [Spacer(1,4*mm),Cover(),PageBreak()]

def parse_md(path:Path):
    return parse_text(path.read_text(encoding="utf-8"))

def parse_text(text:str,include_toc:bool=True):
    lines=text.splitlines();story=[];i=0
    while i<len(lines):
        raw=lines[i].rstrip();s=raw.strip()
        if not s or s=="---" or s.startswith("<!-- SOURCE:"):i+=1;continue
        if s.startswith("[[ILUSTRASI:"):
            kind=s[12:-2]
            if kind in ("JARINGAN","BACKUP","PROXY"):story.extend([Spacer(1,3*mm),Diagram(kind),Spacer(1,4*mm)])
            i+=1;continue
        if s.startswith("[[ROADMAP:"):
            road=ROOT/"docs/12-roadmap-manfaat-keamanan.md"
            # Insert full roadmap body inline, leaving its duplicate title out.
            sub=road.read_text(encoding="utf-8").splitlines()[1:]
            temp=ROOT/"tmp_roadmap_generated.md";temp.write_text("\n".join(sub),encoding="utf-8")
            story.extend(parse_text(temp.read_text(encoding="utf-8"),include_toc=False));temp.unlink(missing_ok=True);i+=1;continue
        if s.startswith("```"):
            i+=1;code=[]
            while i<len(lines) and not lines[i].strip().startswith("```"):
                code.append(lines[i].rstrip());i+=1
            i+=1;story.append(CodeBlock(code));story.append(Spacer(1,3));continue
        if s.startswith("|"):
            rows=[]
            while i<len(lines) and lines[i].strip().startswith("|"):
                rows.append([x.strip().replace("\\|","|") for x in lines[i].strip().strip("|").split("|")]);i+=1
            rows=[r for r in rows if not all(re.fullmatch(r"\s*:?-{3,}:?\s*",c or "") for c in r)]
            if rows:
                n=max(len(r) for r in rows);rows=[r+([""]*(n-len(r))) for r in rows]
                avail=165*mm; widths=[avail/n]*n
                if n==2:widths=[50*mm,115*mm]
                elif n==3:widths=[42*mm,55*mm,68*mm]
                elif n==4:widths=[35*mm,38*mm,50*mm,42*mm]
                data=[[Paragraph(inline(c),styles["TableHead"] if ri==0 else styles["TableCell"]) for c in row] for ri,row in enumerate(rows)]
                t=Table(data,colWidths=widths,repeatRows=1,hAlign="LEFT")
                t.setStyle(TableStyle([("BACKGROUND",(0,0),(-1,0),NAVY),("GRID",(0,0),(-1,-1),.35,GRID),("VALIGN",(0,0),(-1,-1),"TOP"),("LEFTPADDING",(0,0),(-1,-1),4),("RIGHTPADDING",(0,0),(-1,-1),4),("TOPPADDING",(0,0),(-1,-1),3),("BOTTOMPADDING",(0,0),(-1,-1),3),("ROWBACKGROUNDS",(0,1),(-1,-1),[colors.white,colors.HexColor("#F3F7F9")])]))
                story.extend([Spacer(1,2*mm),t,Spacer(1,3*mm)])
            continue
        if s.startswith(">"):
            qs=[]
            while i<len(lines):
                quote_line=lines[i].strip()
                if quote_line.startswith(">"):
                    qs.append(quote_line.lstrip("> "));i+=1;continue
                if not quote_line or quote_line.startswith(("#","```","|","[[")) or re.match(r"^[-*] |^\d+[.)]\s",quote_line):
                    break
                # Markdown permits wrapped continuation lines in a blockquote.
                qs.append(quote_line);i+=1
            content=" ".join(qs); color=RED if any(x in content.lower() for x in ("perhatian","peringatan","bahaya","jangan")) else (AMBER if "belum pasti" in content.lower() else PALE)
            st=ParagraphStyle("Callout",parent=styles["QuoteID"],backColor=color,borderColor=GRID,borderWidth=.4,borderPadding=6)
            story.append(Paragraph(inline(content),st));continue
        heading_match=re.match(r"^(#{1,4})\s+(.*)$",s)
        if heading_match:
            level=len(heading_match.group(1));title=inline(heading_match.group(2))
            if level==1 and "Buku Panduan Lengkap Home Server Lab" in heading_match.group(2):
                i+=1;continue
            if level==2 and heading_match.group(2).strip()=="Daftar isi":
                i+=1;continue
            if level==1:
                p=Paragraph(title,styles["ChapterID"]);p.toc_level=0;story.extend([PageBreak(),p])
            elif level==2:
                p=Paragraph(title,styles["H2ID"])
                if include_toc:p.toc_level=1
                story.append(p)
            else:story.append(Paragraph(title,styles["H3ID"]))
            i+=1;continue
        if s.startswith("- [ ] ") or s.startswith("- [x] "):
            prefix="[ ] " if "[ ]" in s else "[x] "; story.append(Paragraph(prefix+inline(s[6:]),ParagraphStyle("ListItem",parent=styles["BodyID"],leftIndent=10,firstLineIndent=-10)));i+=1;continue
        if s.startswith("- ") or s.startswith("* ") or re.match(r"^\d+[.)]\s",s):
            if s.startswith(("- ","* ")):prefix="- ";txt=s[2:]
            else:
                list_match=re.match(r"^(\d+)[.)]\s+(.*)$",s);prefix=list_match.group(1)+". ";txt=list_match.group(2)
            story.append(Paragraph(prefix+inline(txt),ParagraphStyle("ListItem",parent=styles["BodyID"],leftIndent=12,firstLineIndent=-12)));i+=1;continue
        if s.startswith("**PENEMPATAN") or s.startswith("PENEMPATAN -"):
            story.append(Paragraph(inline(s),ParagraphStyle("Placement",parent=styles["QuoteID"],backColor=PURPLE,borderColor=colors.HexColor("#B8A7D0"),borderWidth=.5,borderPadding=7)));i+=1;continue
        para=[s];i+=1
        while i<len(lines):
            t=lines[i].strip()
            if not t or t.startswith(("#","````","````","|",">","[[")) or re.match(r"^[-*] ",t) or re.match(r"^\d+[.)]\s",t):break
            para.append(t);i+=1
        text=" ".join(para)
        if len(text)>900: # Split very long unbroken source paragraphs into readable pieces.
            chunks=re.split(r"(?<=[.!?])\s+",text)
            story.extend(Paragraph(inline(x),styles["BodyID"]) for x in chunks if x)
        else:story.append(Paragraph(inline(text),styles["BodyID"]))
    return story

def main():
    ap=argparse.ArgumentParser();ap.add_argument("--pdf",type=Path);ap.add_argument("--markdown",type=Path);args=ap.parse_args()
    book_md="\n".join(line.rstrip() for line in source_content().splitlines())+"\n";md_path=args.markdown or ROOT/"docs/panduan-lengkap-home-server-lab.md";md_path.parent.mkdir(parents=True,exist_ok=True);md_path.write_text(book_md,encoding="utf-8",newline="\r\n")
    pdf_path=args.pdf or ROOT.parent/"06-Book/Panduan_Lengkap_Home_Server_Lab_Edisi_Lengkap_2026.pdf";pdf_path.parent.mkdir(parents=True,exist_ok=True)
    mdtext=md_path.read_text(encoding="utf-8")
    front,body=mdtext.split("## Daftar isi",1)
    story=cover()+parse_text(front,include_toc=False)+[PageBreak(),Paragraph("Daftar Isi",styles["PartID"])]
    toc=TableOfContents();toc.levelStyles=[ParagraphStyle("TOC0",fontName="Vera-Bold",fontSize=7.2,leading=8.4,leftIndent=0,spaceBefore=2,textColor=NAVY),ParagraphStyle("TOC1",fontName="Vera",fontSize=6.4,leading=7.4,leftIndent=12,textColor=INK)];story.extend([toc,PageBreak()])
    story.extend(parse_text(body));doc=FullDoc(pdf_path);doc.multiBuild(story)
    print(f"Source chapters: {len(parse_index(EDISI2_INDEX))+len(parse_index(SUPPLEMENT_INDEX))}; PDF: {pdf_path}; pages: {doc.page}")

if __name__=="__main__":main()

