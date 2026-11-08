"""Lectura de las tablas financieras del QFR (Census) a una tabla larga, desde .xlsx (openpyxl) y .xls (BIFF8).

`xlrd` no está en el entorno y no se añade (encargo F14a): `grid_xls` es un lector mínimo de BIFF8 (OLE2 + SST + celdas
NUMBER/RK/MULRK/LABELSST/FORMULA), suficiente para estas tablas. Se valida contra el solape 2022Q2 (xls frente a xlsx) en
`test_qfr.py`. Salida: una fila por (tabla, grupo industria×tamaño, partida, trimestre).
"""

import re
import struct
from pathlib import Path

import openpyxl
import pandas as pd

QRE = re.compile(r"(\d)Q_?\s*(\d{4})")
CLEAN = re.compile(r"[\s\.…�]+")  # los puntos guía vienen como � o '.'


def _norm(s):
    return re.sub(r"\s+", " ", CLEAN.sub(" ", str(s))).strip()


# ---------- .xlsx ----------
def grid_xlsx(path):
    wb = openpyxl.load_workbook(path, read_only=True, data_only=True)
    return {n: [list(r) for r in wb[n].iter_rows(values_only=True)] for n in wb.sheetnames}


# ---------- .xls (BIFF8) ----------
def _ole_stream(buf, want=("Workbook", "Book")):
    ss = 1 << struct.unpack_from("<H", buf, 30)[0]
    nfat, dir0 = struct.unpack_from("<II", buf, 44)
    difat = list(struct.unpack_from("<109I", buf, 76))
    d, nd = struct.unpack_from("<II", buf, 68)
    def sec(i):
        return buf[512 + i * ss: 512 + (i + 1) * ss]

    for _ in range(nd):
        t = struct.unpack(f"<{ss // 4}I", sec(d))
        difat += t[:-1]
        d = t[-1]
    fat = []
    for s in difat[:nfat]:
        fat += struct.unpack(f"<{ss // 4}I", sec(s))

    def chain(s):
        out = b""
        while s < 0xFFFFFFFA:
            out += sec(s)
            s = fat[s]
        return out

    dirs = chain(dir0)
    for i in range(0, len(dirs), 128):
        e = dirs[i:i + 128]
        name = e[:struct.unpack_from("<H", e, 64)[0] - 2].decode("utf-16-le")
        if name in want:
            start, size = struct.unpack_from("<II", e, 116)
            assert size >= 4096, "stream en mini-FAT: no soportado"
            return chain(start)[:size]
    raise ValueError("sin stream Workbook")


def _records(b, pos=0):
    while pos + 4 <= len(b):
        rid, ln = struct.unpack_from("<HH", b, pos)
        yield rid, b[pos + 4: pos + 4 + ln], pos
        pos += 4 + ln


class _Chunks:
    """Lee cadenas de la SST a través de los límites de CONTINUE (cada trozo reabre con su byte de flags)."""

    def __init__(self, chunks):
        self.c, self.i, self.p = chunks, 0, 0

    def _need(self):
        while self.p >= len(self.c[self.i]):
            self.i, self.p = self.i + 1, 0

    def raw(self, n):
        out = b""
        while n:
            self._need()
            t = self.c[self.i][self.p:self.p + n]
            out, self.p, n = out + t, self.p + len(t), n - len(t)
        return out

    def string(self):
        cch, fl = struct.unpack("<HB", self.raw(3))
        wide, ext, rich = fl & 1, fl & 4, fl & 8
        nr = struct.unpack("<H", self.raw(2))[0] if rich else 0
        ne = struct.unpack("<I", self.raw(4))[0] if ext else 0
        s = ""
        while cch:
            if self.p >= len(self.c[self.i]):  # trozo nuevo: primer byte = flags
                self.i, self.p = self.i + 1, 1
                wide = self.c[self.i][0] & 1
            w = 2 if wide else 1
            k = min(cch, (len(self.c[self.i]) - self.p) // w)
            s += self.c[self.i][self.p:self.p + k * w].decode("utf-16-le" if wide else "latin-1")
            self.p += k * w
            cch -= k
        self.raw(4 * nr + ne)
        return s


def _rk(v):
    if v & 2:
        x = v >> 2
        x = x - (1 << 30) if x & (1 << 29) else x
        x = float(x)
    else:
        x = struct.unpack("<d", struct.pack("<II", 0, v & 0xFFFFFFFC))[0]
    return x / 100 if v & 1 else x


def grid_xls(path):
    b = _ole_stream(Path(path).read_bytes())
    sheets, chunks, last = [], None, None
    for rid, d, pos in _records(b):
        if rid == 0x85:
            off = struct.unpack_from("<I", d, 0)[0]
            n, fl = d[6], d[7]
            sheets.append((d[8:8 + n * (1 + (fl & 1))].decode("utf-16-le" if fl & 1 else "latin-1"), off))
        elif rid == 0xFC:
            chunks, last = [d[8:]], "sst"
        elif rid == 0x3C and last == "sst":
            chunks.append(d)
        elif rid == 0x0A and sheets and pos > 0:
            break
        else:
            last = None
    sst = []
    if chunks:
        cr = _Chunks(chunks)
        for _ in range(struct.unpack_from("<I", b, next(p for r, _, p in _records(b) if r == 0xFC) + 8)[0]):
            sst.append(cr.string())
    out = {}
    for name, off in sheets:
        cells, fcell = {}, None
        for rid, d, _ in _records(b, off):
            if rid == 0xFD:
                r, c, _, i = struct.unpack_from("<HHHI", d)
                cells[r, c] = sst[i]
            elif rid == 0x203:
                r, c, _ = struct.unpack_from("<HHH", d)
                cells[r, c] = struct.unpack_from("<d", d, 6)[0]
            elif rid == 0x27E:
                r, c, _, v = struct.unpack_from("<HHHI", d)
                cells[r, c] = _rk(v)
            elif rid == 0xBD:
                r, c0 = struct.unpack_from("<HH", d)
                for k in range((len(d) - 6) // 6):
                    cells[r, c0 + k] = _rk(struct.unpack_from("<I", d, 4 + 6 * k + 2)[0])
            elif rid == 0x06:
                r, c = struct.unpack_from("<HH", d)
                if d[12:14] == b"\xff\xff":
                    fcell = (r, c)
                else:
                    cells[r, c] = struct.unpack_from("<d", d, 6)[0]
            elif rid == 0x207 and fcell:
                cells[fcell] = _Chunks([d]).string()
                fcell = None
            elif rid == 0x0A:
                break
        nr = max((r for r, _ in cells), default=-1) + 1
        nc = max((c for _, c in cells), default=-1) + 1
        out[name] = [[cells.get((r, c)) for c in range(nc)] for r in range(nr)]
    return out


def grid(path):
    return (grid_xlsx if str(path).endswith("xlsx") else grid_xls)(path)


# ---------- tabla larga ----------
def long_table(path):
    """Una fila por (tabla, grupo, partida, trimestre). `tabla` = 'T03_1' (balance) o 'T03_0' (resultados).

    Las hojas se identifican por su título (`Table 3.1 --`), no por el nombre de hoja, que cambia entre vintages.
    """
    rows = []
    for g in grid(path).values():
        h = next((i for i, r in enumerate(g[:8]) if r and str(r[0]).strip() == "Item"), None)
        t0 = next((i for i, r in enumerate(g[:3]) if r and re.match(r"Table \d+\.\d", str(r[0]).strip())), None)
        if h is None or t0 is None:
            continue
        # título en 1–2 filas (las vintages de 2006–07 lo parten); cabeceras: grupos en h-1, trimestres en h
        title = re.sub(r"\s+", " ", " ".join(str(r[0]) for r in g[t0:h - 1] if r and r[0])).split("See the Survey")[0].strip()
        m = re.match(r"Table (\d+)\.(\d)", title)
        tab = f"T{int(m[1]):02d}_{m[2]}"
        gh, qh = g[h - 1], g[h]
        # en las vintages de 2006–07 el tamaño va en el título ("..., Total Assets $25 Million and Over"), no en la cabecera
        tsize = re.search(r"(Total Assets (?:Under|\$)[^,]*?(?:and Over|Million|Billion))(?:\s+\d)?\s*$", title)
        groups, cur = {}, None
        for j in range(1, len(qh)):
            if j < len(gh) and gh[j]:
                cur = _norm(gh[j])
                if tsize and "Total Assets" not in cur and "Asset Sizes" not in cur:
                    cur = f"{cur} {tsize[1]}"
            q = QRE.search(str(qh[j])) if qh[j] else None
            if cur and q:
                groups[j] = (cur, f"{q[2]}Q{q[1]}")
        section, prefix = "", ""
        for r in g[h + 2:]:
            lab = r[0] if r else None
            if not lab:
                continue
            lab = _norm(lab)
            if "RATIO" in lab and lab.isupper():  # lo que sigue son porcentajes, no importes
                break
            vals =[r[j] if j < len(r) else None for j in groups]
            if all(v is None or isinstance(v, str) for v in vals):  # cabecera o primera línea de una etiqueta partida
                if lab.endswith(":"):
                    section, prefix = lab, ""
                else:
                    prefix = (prefix + " " + lab).strip()
                continue
            item = (prefix + " " + lab).strip()
            prefix = ""
            if re.match(r"^[abc] ", item):
                item = section + " " + item
            for j, v in zip(groups, vals):
                if isinstance(v, (int, float)):
                    rows.append((Path(path).name, tab, title, *groups[j], item, float(v)))
    return pd.DataFrame(rows, columns=["file", "table", "title", "group", "quarter", "item", "value"])
