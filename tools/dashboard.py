"""Panel de la desk: qué está trabajando, qué espera a quién, en qué punto está cada paper, consumo y salud del repo.

Uso:
  uv run python tools/dashboard.py [puerto]   # http://127.0.0.1:3200 (configuración `dashboard` en .claude/launch.json)

Solo lee: cada recarga vuelve a leer los .lock, RUNS.csv, las transcripciones, los SPEC.md/TASKS.md/audits de cada paper
y git. No calcula nada propio: reutiliza desk.py e integrity.py.
"""

from __future__ import annotations

import html
import re
import subprocess
import sys
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import desk
import integrity

ROOT = desk.ROOT
TASK = re.compile(r"^- \[([ ~x!])\] \*\*([^*]+)\*\* · ([^·]+?) · (.*)$")
STATE = {" ": "pendiente", "~": "en curso", "x": "hecha", "!": "bloqueada"}
CTX_ALERT, IDLE_ALERT_MIN, RECENT_MIN = 150_000, 15, 10
PROJECT = ROOT.name.replace("_", "-")  # así nombra Claude Code la carpeta de transcripciones del repo
_health: dict = {"at": 0.0}


def esc(x: object) -> str:
    return html.escape(str(x))


def fmt(n: int) -> str:
    return f"{n / 1e6:.1f}M" if n >= 1e6 else f"{n / 1e3:.0f}K" if n >= 1e3 else str(n)


def git(*args: str) -> str:
    r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True, encoding="utf-8", check=False)
    return r.stdout.strip()


def read(p: Path) -> str:
    return p.read_text(encoding="utf-8", errors="replace") if p.is_file() else ""


# ---------------------------------------------------------------- datos
def tasks(text: str) -> list[dict]:
    """Tareas de un TASKS.md: estado, id, desk, título (primera frase) y la sección `##` en la que están."""
    out, section = [], ""
    for line in text.splitlines():
        if line.startswith("## "):
            section = line[3:].strip()
        elif m := TASK.match(line):
            mark, tid, who, rest = m.groups()
            title = re.sub(r"\*\*|`", "", rest).split(". ")[0]
            out.append({"state": STATE[mark], "id": tid, "desk": who.strip(), "title": title[:160], "section": section})
    return out


def spec_estado(spec: str) -> str:
    """El párrafo de la línea `Estado:` de la SPEC, sin marcas de Markdown."""
    if not (m := integrity.SPEC_STATUS.search(spec)):  # el mismo párrafo que la puerta no cuenta como científico
        return "(la SPEC no tiene línea Estado:)"
    return re.sub(r"\*\*|`", "", m.group(0).removeprefix("Estado:").strip()).replace("\n", " ")


def paper(p: Path) -> dict:
    rel = p.relative_to(ROOT).as_posix()
    ts = tasks(read(p / "TASKS.md"))
    audits = []
    for a in sorted((p / "audits").glob("*.md")):
        if integrity.REFEREE_SKIP.match(a.name) or not (fm := integrity.front_matter(read(a))):
            continue
        holds = integrity._approval_holds(ROOT, p.name, fm) if fm.get("verdict") in integrity.APPROVED else None
        audits.append({**fm, "file": a.name, "holds": holds})
    return {
        "slug": p.name,
        "estado": spec_estado(read(p / "SPEC.md")),
        "estado_date": git("log", "-1", "--format=%cs", "--", f"{rel}/SPEC.md"),
        "tasks": ts,
        "phase": next((t["section"] for t in ts if t["state"] != "hecha"), "todo hecho"),
        "log": [ln.split("|", 1) for ln in git("log", "-8", "--format=%cs|%s", "--", rel).splitlines()],
        "audits": audits,
    }


def papers() -> list[dict]:
    return [paper(p) for p in sorted((ROOT / "papers").iterdir()) if p.is_dir() and p.name != "_template"]


def recent_sessions() -> list[dict]:
    """Transcripciones de este repo (raíz y desks) escritas en los últimos RECENT_MIN minutos."""
    now, out = time.time(), []
    for f in desk.TRANSCRIPTS.glob(f"*{PROJECT}*/*.jsonl"):
        if (idle := (now - f.stat().st_mtime) / 60) <= RECENT_MIN:
            where = f.parent.name.split(PROJECT, 1)[1].lstrip("-").replace("-", "/") or "raíz"
            out.append({"where": where, "sid": f.stem, "idle": idle})
    return sorted(out, key=lambda s: s["idle"])


def candidate_lessons() -> int:
    return sum(read(f).count("Estado: candidata") for f in (ROOT / "kb" / "lessons").glob("*.md"))


def health() -> dict:
    """integrity.py tarda unos segundos: se recalcula como mucho cada 2 minutos."""
    if time.time() - _health["at"] > 120:
        _health.update(at=time.time(), violations=integrity.run(ROOT), head=git("log", "-1", "--format=%h %cs %s"),
                       dirty=len(git("status", "--porcelain").splitlines()))
    return _health


# ---------------------------------------------------------------- HTML
def table(head: list[str], rows: list[list[str]]) -> str:
    th = "".join(f"<th>{h}</th>" for h in head)
    body = "".join("<tr>" + "".join(f"<td>{c}</td>" for c in r) + "</tr>" for r in rows)
    return f"<table><tr>{th}</tr>{body}</table>"


def desk_card(name: str, info: dict) -> str:
    sid = info.get("session_id", "")
    u = desk.session_usage(sid) if sid else None
    tr = sorted(desk.TRANSCRIPTS.glob(f"*/{sid}.jsonl")) if sid else []
    idle = (time.time() - tr[0].stat().st_mtime) / 60 if tr else None
    alerts = []
    if u and u["peak_ctx"] > CTX_ALERT:
        alerts.append(f"contexto de {fmt(u['peak_ctx'])}: cada turno relee todo eso")
    if idle is not None and idle > IDLE_ALERT_MIN:
        alerts.append(f"{idle:.0f} min sin escribir en la transcripción")
    log = read(desk.DESKS / name / info.get("log", "")).splitlines()[-6:]
    effort = f" · {esc(info['effort'])}" if info.get("effort") else ""
    stats = (f"{u['turns']} turnos · pico {fmt(u['peak_ctx'])} · caché leída {fmt(u['cache_read'])} · {u['minutes']} min"
             if u else "sin transcripción todavía")
    return (f"<div class='card'><h3>{esc(name)} <span class='tag'>{esc(info.get('model', '?'))}{effort}</span></h3>"
            f"<p class='muted'>{esc(info['encargo'])} · desde {esc(info['started'])}</p><p>{stats}</p>"
            + "".join(f"<p class='alert'>⚠ {esc(a)}</p>" for a in alerts)
            + f"<pre>{esc(chr(10).join(log)) or '(el log se escribe al terminar la sesión)'}</pre></div>")


def section_now(active: dict) -> str:
    known = {r["session_id"] for r in desk.read_runs()}
    live = [[esc(s["where"]), f"<code>{esc(s['sid'][:8])}</code>", f"hace {s['idle']:.0f} min",
             "desk" if s["sid"] in known else "interactiva"] for s in recent_sessions()]
    cards = "".join(desk_card(n, i) for n, i in active.items()) or "<p>Ninguna desk trabajando.</p>"
    return (f"<h2>Ahora</h2><p class='muted'>{len(active)}/{desk.MAX_CONCURRENT} desks activas · "
            f"{desk.free_memory_gb():.1f} GB de memoria comprometida libre</p><div class='grid'>{cards}</div>"
            f"<h3>Sesiones con actividad en los últimos {RECENT_MIN} min</h3>"
            + (table(["dónde", "sesión", "última escritura", "tipo"], live) if live else "<p class='muted'>Ninguna.</p>"))


def section_waiting(ps: list[dict], rows: list[dict], active: dict) -> str:
    authors = [f"<b>{esc(p['slug'])} {esc(t['id'])}</b> · {esc(t['title'])}" for p in ps for t in p["tasks"]
               if t["state"] == "bloqueada"]
    authors += [f"<b>{esc(p['slug'])}</b> · informe RECHAZADO <code>{esc(a['file'])}</code>" for p in ps
                for a in p["audits"] if a.get("verdict") == "RECHAZADO"]
    if n := candidate_lessons():
        authors.append(f"{n} lecciones candidatas en <code>kb/lessons/</code> sin validar")
    running = {i.get("session_id") for i in active.values()}
    coord = [f"<b>{esc(r['desk'])}</b> · {esc(r['encargo'])} sin revisar "
             f"(<code>desk.py estado {esc(r['desk'])} …</code>)" for r in rows
             if not r["estado"] and r["session_id"] not in running]
    coord += [f"<b>{esc(p['slug'])}</b> · aprobación caducada <code>{esc(a['file'])}</code>: cambió lo auditado"
              for p in ps for a in p["audits"] if a["holds"] is False]

    def ul(items: list[str]) -> str:
        return "<ul>" + "".join(f"<li>{i}</li>" for i in items) + "</ul>" if items else "<p class='muted'>Nada.</p>"

    return f"<h2>Espera a alguien</h2><div class='grid'><div><h3>Autores</h3>{ul(authors)}</div>" \
           f"<div><h3>Coordinación</h3>{ul(coord)}</div></div>"


def section_paper(p: dict) -> str:
    counts = {s: sum(t["state"] == s for t in p["tasks"]) for s in STATE.values()}
    done = counts["hecha"] / len(p["tasks"]) if p["tasks"] else 0
    open_tasks = [[f"<span class='st {t['state'].replace(' ', '-')}'>{t['state']}</span>", esc(t["id"]), esc(t["desk"]),
                   esc(t["title"])] for t in p["tasks"] if t["state"] in ("bloqueada", "en curso")]
    nxt = [["<span class='st pendiente'>pendiente</span>", esc(t["id"]), esc(t["desk"]), esc(t["title"])]
           for t in p["tasks"] if t["state"] == "pendiente"][:3]
    log = "".join(f"<li><span class='muted'>{esc(d)}</span> {esc(s)}</li>" for d, s in p["log"])
    audits = [[esc(a.get("date", "")), esc(a.get("object", "")), esc(a.get("verdict", "")),
               {True: "vigente", False: "<span class='alert'>caducada</span>", None: "—"}[a["holds"]]]
              for a in p["audits"]]
    return (f"<div class='paper'><h3>{esc(p['slug'])}</h3>"
            f"<p><b>Estado (SPEC, {esc(p['estado_date'] or 'sin commit')}):</b> {esc(p['estado'])}</p>"
            f"<p><b>Fase actual:</b> {esc(p['phase'])} · {counts['hecha']}/{len(p['tasks'])} tareas hechas · "
            f"{counts['en curso']} en curso · {counts['bloqueada']} bloqueadas</p>"
            f"<div class='bar'><div style='width:{done:.0%}'></div></div>"
            f"<div class='grid'><div><h4>En curso, bloqueado y lo siguiente</h4>"
            f"{table(['estado', 'tarea', 'desk', 'qué'], open_tasks + nxt)}</div>"
            f"<div><h4>Últimos avances</h4><ul class='log'>{log}</ul></div></div>"
            f"<h4>Auditorías del Referee</h4>"
            + (table(["fecha", "objeto", "veredicto", "aprobación"], audits) if audits else "<p class='muted'>Ninguna.</p>")
            + "</div>")


def section_usage(rows: list[dict]) -> str:
    body = [[esc(r["started"]), esc(r["desk"]), esc(r["model"]), esc(r.get("effort") or "—"), str(r["launches"]),
             *([str(u["turns"]), fmt(u["cache_read"]), fmt(u["cache_write"]), fmt(u["output"]), fmt(u["peak_ctx"]),
                str(u["minutes"])] if (u := r["usage"]) else ["sin transcripción"] + [""] * 5),
             esc(r["estado"] or "—"), esc(r["encargo"])] for r in reversed(rows)]
    per = [[esc(n), f"{d['aceptadas']}/{d['revisadas']}",
            *([fmt(d["per"][k]) for k in ("cache_read", "cache_write", "output")] if d["per"] else ["—"] * 3)]
           for n, d in desk.per_accepted(rows).items()]
    return ("<h2>Consumo</h2><p class='muted'>Tokens de las transcripciones de Claude Code. La cuota de la suscripción "
            "no se expone en local, así que no se muestra.</p><h3>Por sesión aceptada</h3>"
            + table(["desk", "aceptadas/revisadas", "caché leída", "caché escrita", "salida"], per)
            + "<h3>Sesiones</h3>"
            + table(["inicio", "desk", "modelo", "esfuerzo", "lanz.", "turnos", "caché leída", "caché escrita", "salida",
                     "pico ctx", "min", "estado", "encargo"], body))


def section_health() -> str:
    h = health()
    v = h["violations"]
    checks = "<p>integrity.py: OK</p>" if not v else (
        f"<p class='alert'>integrity.py: {len(v)} incumplimientos</p>"
        + table(["check", "archivo", "motivo"], [[esc(x.check), f"{esc(x.path)}:{x.line}", esc(x.msg)] for x in v[:20]]))
    return (f"<h2>Salud del repo</h2>{checks}<p>Último commit: <code>{esc(h['head'])}</code> · "
            f"{h['dirty']} archivos sin commitear</p>")


CSS = """
:root{--bg:#f7f7f5;--fg:#1d1d1b;--muted:#6b6b66;--card:#fff;--line:#e2e2dc;--accent:#2f6f4e;--warn:#b4441c;
--blocked:#b4441c;--doing:#a26b00;--todo:#6b6b66;--done:#2f6f4e}
@media (prefers-color-scheme:dark){:root{--bg:#161615;--fg:#ececea;--muted:#9a9a94;--card:#202020;--line:#33332f;
--accent:#6fbf8f;--warn:#f08a5d;--blocked:#f08a5d;--doing:#e0b44a;--todo:#9a9a94;--done:#6fbf8f}}
body{background:var(--bg);color:var(--fg);font:14px/1.45 system-ui,sans-serif;margin:0 auto;max-width:1200px;padding:16px}
h1{font-size:20px;margin:0}h2{font-size:17px;margin:28px 0 8px;border-bottom:1px solid var(--line);padding-bottom:4px}
h3{font-size:15px;margin:14px 0 6px}h4{font-size:13px;margin:12px 0 4px;color:var(--muted)}
.muted{color:var(--muted)}.alert{color:var(--warn)}code{font-size:12px}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(320px,1fr));gap:12px}
.card,.paper{background:var(--card);border:1px solid var(--line);border-radius:8px;padding:10px 14px}
.paper{margin-bottom:14px}.card p{margin:4px 0}.tag{font-weight:400;font-size:12px;color:var(--muted)}
pre{font-size:11px;white-space:pre-wrap;max-height:120px;overflow:auto;background:var(--bg);padding:6px;border-radius:4px}
table{border-collapse:collapse;width:100%;font-size:12.5px;display:block;overflow-x:auto}
th,td{text-align:left;padding:4px 8px;border-bottom:1px solid var(--line);vertical-align:top}th{color:var(--muted);font-weight:500}
.st{font-size:11px;white-space:nowrap}.bloqueada{color:var(--blocked)}.en-curso{color:var(--doing)}
.pendiente{color:var(--todo)}.bar{height:6px;background:var(--line);border-radius:3px;margin:6px 0 4px}
.bar div{height:100%;background:var(--done);border-radius:3px}ul.log{padding-left:16px;margin:4px 0}ul.log li{margin:2px 0}
"""


def render() -> str:
    active, rows, ps = desk.active(), desk.sessions(), papers()
    return (f"<!doctype html><html lang='es'><head><meta charset='utf-8'><meta name='viewport' "
            f"content='width=device-width,initial-scale=1'><meta http-equiv='refresh' content='30'>"
            f"<title>Research Desk</title><style>{CSS}</style></head><body>"
            f"<h1>Research Desk</h1><p class='muted'>{time.strftime('%Y-%m-%d %H:%M:%S')} · se recarga cada 30 s</p>"
            + section_now(active) + section_waiting(ps, rows, active)
            + "<h2>Papers</h2>" + "".join(section_paper(p) for p in ps)
            + section_usage(rows) + section_health() + "</body></html>")


class Handler(BaseHTTPRequestHandler):
    def do_GET(self) -> None:
        if self.path not in ("/", "/index.html"):
            self.send_error(404)
            return
        try:
            body, code = render().encode("utf-8"), 200
        except Exception as e:  # noqa: BLE001 — un archivo a medio escribir no debe tumbar el panel: se muestra el error
            body, code = f"<pre>{esc(type(e).__name__)}: {esc(e)}</pre>".encode(), 500
        self.send_response(code)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, *args: object) -> None:  # sin una línea por recarga en la consola
        pass


def main(argv: list[str]) -> int:
    port = int(argv[0]) if argv else 3200
    print(f"Panel en http://127.0.0.1:{port}")
    ThreadingHTTPServer(("127.0.0.1", port), Handler).serve_forever()  # solo local: muestra logs y rutas del repo
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
