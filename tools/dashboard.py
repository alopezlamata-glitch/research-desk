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
# Paleta y anatomía de la guía de visualización (dataviz, `references/palette.md`): una sola serie en el acento azul,
# colores de estado reservados (bien, aviso, crítico) siempre con icono y texto, y el texto siempre en tinta, nunca en
# el color del dato.
CTX_SCALE = 2 * CTX_ALERT  # escala del medidor de contexto; la marca del umbral queda en la mitad
TASK_STYLE = {"hecha": ("good", "✓"), "en curso": ("accent", "●"), "bloqueada": ("critical", "■"),
              "pendiente": ("muted", "○")}


def chip(text: str, kind: str = "neutral", icon: str = "") -> str:
    return f"<span class='chip {kind}'>{f'<i>{icon}</i>' if icon else ''}{esc(text)}</span>"


def task_chip(state: str) -> str:
    kind, icon = TASK_STYLE[state]
    return chip(state, kind, icon)


def table(head: list[str], rows: list[list[str]], num: set[int] = frozenset()) -> str:
    th = "".join(f"<th class='{'num' if i in num else ''}'>{h}</th>" for i, h in enumerate(head))
    body = "".join("<tr>" + "".join(f"<td class='{'num' if i in num else ''}'>{c}</td>" for i, c in enumerate(r))
                   + "</tr>" for r in rows)
    return f"<div class='table-wrap'><table><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table></div>"


def tile(label: str, value: str, note: str = "", kind: str = "") -> str:
    return (f"<div class='tile {kind}'><div class='tile-label'>{esc(label)}</div>"
            f"<div class='tile-value'>{value}</div><div class='tile-note'>{note}</div></div>")


def panel(title: str, body: str, sub: str = "", cls: str = "") -> str:
    return (f"<section class='panel {cls}'><header><h2>{esc(title)}</h2>"
            f"{f'<p class=sub>{sub}</p>' if sub else ''}</header>{body}</section>")


def meter(value: int) -> str:
    over = value > CTX_ALERT
    return (f"<div class='meter' title='Pico de contexto {fmt(value)}; umbral {fmt(CTX_ALERT)}'>"
            f"<div class='fill {'critical' if over else 'accent'}' style='width:{min(value / CTX_SCALE, 1):.0%}'></div>"
            f"<div class='tick' style='left:50%'></div></div>"
            f"<div class='meter-legend'><span>pico de contexto <b>{fmt(value)}</b></span>"
            f"<span>umbral {fmt(CTX_ALERT)}</span></div>")


def desk_card(name: str, info: dict) -> str:
    sid = info.get("session_id", "")
    u = desk.session_usage(sid) if sid else None
    tr = sorted(desk.TRANSCRIPTS.glob(f"*/{sid}.jsonl")) if sid else []
    idle = (time.time() - tr[0].stat().st_mtime) / 60 if tr else None
    alerts = []
    if u and u["peak_ctx"] > CTX_ALERT:
        alerts.append("cada turno relee todo el contexto: conviene cerrar con HANDOFF y seguir en sesión nueva")
    if idle is not None and idle > IDLE_ALERT_MIN:
        alerts.append(f"{idle:.0f} min sin escribir en la transcripción: ¿colgada?")
    status = chip("sin actividad", "warning", "▲") if idle is not None and idle > IDLE_ALERT_MIN else \
        chip("trabajando", "good", "●")
    log = read(desk.DESKS / name / info.get("log", "")).splitlines()[-8:]
    metrics = "".join(f"<div><span>{k}</span><b>{v}</b></div>" for k, v in (
        ("turnos", u["turns"] if u else "—"), ("minutos", f"{u['minutes']:.0f}" if u else "—"),
        ("caché leída", fmt(u["cache_read"]) if u else "—"), ("salida", fmt(u["output"]) if u else "—")))
    return (f"<article class='card'><div class='card-head'><h3>{esc(name)}</h3>{status}</div>"
            f"<p class='muted small'>{chip(info.get('model', '?'))}"
            f"{chip('esfuerzo ' + info['effort']) if info.get('effort') else ''} {esc(info['encargo'])}</p>"
            f"<div class='metrics'>{metrics}</div>{meter(u['peak_ctx']) if u else ''}"
            + "".join(f"<p class='alert'><i>▲</i>{esc(a)}</p>" for a in alerts)
            + f"<details><summary>Últimas líneas del log</summary><pre>"
              f"{esc(chr(10).join(log)) or '(claude -p escribe el log al terminar)'}</pre></details></article>")


def section_now(active: dict) -> str:
    known = {r["session_id"] for r in desk.read_runs()}
    live = [[esc(s["where"]), f"<code>{esc(s['sid'][:8])}</code>", f"hace {s['idle']:.0f} min",
             chip("desk", "accent") if s["sid"] in known else chip("interactiva")] for s in recent_sessions()]
    cards = "".join(desk_card(n, i) for n, i in active.items()) or "<p class='empty'>Ninguna desk trabajando.</p>"
    body = (f"<div class='cards'>{cards}</div><h4>Sesiones con actividad en los últimos {RECENT_MIN} min</h4>"
            + (table(["dónde", "sesión", "última escritura", "tipo"], live) if live else "<p class='empty'>Ninguna.</p>"))
    return panel("Ahora", body, f"{len(active)} de {desk.MAX_CONCURRENT} plazas ocupadas · "
                                f"{desk.free_memory_gb():.1f} GB de memoria comprometida libre")


def waiting(ps: list[dict], rows: list[dict], active: dict) -> tuple[list[str], list[str]]:
    authors = [f"<b>{esc(p['slug'])} · {esc(t['id'])}</b> {esc(t['title'])}" for p in ps for t in p["tasks"]
               if t["state"] == "bloqueada"]
    authors += [f"<b>{esc(p['slug'])}</b> informe RECHAZADO <code>{esc(a['file'])}</code>" for p in ps
                for a in p["audits"] if a.get("verdict") == "RECHAZADO"]
    if n := candidate_lessons():
        authors.append(f"<b>{n} lecciones candidatas</b> en <code>kb/lessons/</code> sin validar")
    running = {i.get("session_id") for i in active.values()}
    coord = [f"<b>{esc(r['desk'])}</b> {esc(r['encargo'])} sin revisar · <code>desk.py estado {esc(r['desk'])} …</code>"
             for r in rows if not r["estado"] and r["session_id"] not in running]
    coord += [f"<b>{esc(p['slug'])}</b> aprobación caducada <code>{esc(a['file'])}</code>: cambió lo auditado"
              for p in ps for a in p["audits"] if a["holds"] is False]
    return authors, coord


def section_waiting(authors: list[str], coord: list[str]) -> str:
    def col(title: str, items: list[str]) -> str:
        li = "".join(f"<li>{i}</li>" for i in items) or "<li class='empty'>Nada pendiente.</li>"
        return f"<div><h4>{title} <span class='count'>{len(items)}</span></h4><ul class='todo'>{li}</ul></div>"

    return panel("Espera a alguien", f"<div class='two'>{col('Autores', authors)}{col('Coordinación', coord)}</div>")


def progress(ts: list[dict]) -> str:
    """Barra segmentada de tareas por estado, con leyenda: el color nunca va solo."""
    order = ("hecha", "en curso", "bloqueada", "pendiente")
    counts = {s: sum(t["state"] == s for t in ts) for s in order}
    segs = "".join(f"<div class='seg {TASK_STYLE[s][0]}' style='flex:{c}' title='{s}: {c}'></div>"
                   for s, c in counts.items() if c)
    legend = "".join(f"<span><i class='dot {TASK_STYLE[s][0]}'></i>{s} <b>{c}</b></span>" for s, c in counts.items())
    return f"<div class='segbar'>{segs}</div><div class='legend'>{legend}</div>" if ts else ""


def section_paper(p: dict) -> str:
    done = sum(t["state"] == "hecha" for t in p["tasks"])
    focus = [t for t in p["tasks"] if t["state"] in ("bloqueada", "en curso")]
    focus += [t for t in p["tasks"] if t["state"] == "pendiente"][:3]
    rows = [[task_chip(t["state"]), f"<b>{esc(t['id'])}</b>", esc(t["desk"]), esc(t["title"])] for t in focus]
    log = "".join(f"<li><time>{esc(d)}</time><span>{esc(s)}</span></li>" for d, s in p["log"])
    verdict = {"APROBADO": "good", "APROBADO CON CAMBIOS": "good", "RECHAZADO": "critical"}
    audits = [[esc(a.get("date", "")), esc(a.get("object", "")),
               chip(a.get("verdict", "?"), verdict.get(a.get("verdict", ""), "neutral")),
               {True: chip("vigente", "good", "✓"), False: chip("caducada", "critical", "■"), None: "—"}[a["holds"]]]
              for a in p["audits"]]
    body = (f"<div class='paper-head'><div><p class='estado'>{esc(p['estado'])}</p>"
            f"<p class='muted small'>Estado según la SPEC · actualizado {esc(p['estado_date'] or 'sin commit')}</p></div>"
            f"<div class='big'><b>{done}</b><span>/ {len(p['tasks'])} tareas</span></div></div>"
            f"<p class='small'><span class='muted'>Fase actual</span> <b>{esc(p['phase'])}</b></p>{progress(p['tasks'])}"
            f"<div class='two wide-left'><div><h4>En curso, bloqueado y lo siguiente</h4>"
            f"{table(['estado', 'tarea', 'desk', 'qué'], rows)}</div>"
            f"<div><h4>Últimos avances</h4><ol class='timeline'>{log}</ol></div></div>"
            f"<h4>Auditorías del Referee</h4>"
            + (table(["fecha", "objeto", "veredicto", "aprobación"], audits) if audits else "<p class='empty'>Ninguna.</p>"))
    return panel(p["slug"], body, cls="paper")


def bars(rows: list[dict]) -> str:
    """Caché leída por sesión: una serie, barras horizontales con el valor en la punta y tooltip nativo."""
    data = [r for r in rows if r["usage"]][-12:]
    peak = max((r["usage"]["cache_read"] for r in data), default=1) or 1
    out = []
    for r in reversed(data):
        u = r["usage"]
        tip = (f"{r['desk']} · {r['encargo']}\ncaché leída {u['cache_read']:,} · escrita {u['cache_write']:,} · "
               f"salida {u['output']:,}\n{u['turns']} turnos · pico {u['peak_ctx']:,} · {u['minutes']} min")
        out.append(f"<div class='bar-row' title='{esc(tip)}'><span class='bar-label'>{esc(r['desk'])}"
                   f"<small>{esc(r['started'][:10])}</small></span><span class='bar-track'>"
                   f"<span class='bar' style='width:{u['cache_read'] / peak:.1%}'></span>"
                   f"<span class='bar-value'>{fmt(u['cache_read'])}</span></span>"
                   f"<span class='bar-state'>{chip('aceptada', 'good', '✓') if r['estado'] == 'aceptada' else esc(r['estado'] or 'sin revisar')}"
                   f"</span></div>")
    return "<div class='bars'>" + "".join(out) + "</div>"


def section_usage(rows: list[dict]) -> str:
    per = [[f"<b>{esc(n)}</b>", f"{d['aceptadas']}/{d['revisadas']}",
            *([fmt(d["per"][k]) for k in ("cache_read", "cache_write", "output")] if d["per"] else ["—"] * 3)]
           for n, d in desk.per_accepted(rows).items()]
    body = [[esc(r["started"]), esc(r["desk"]), esc(r["model"]), esc(r.get("effort") or "—"), str(r["launches"]),
             *([str(u["turns"]), fmt(u["cache_read"]), fmt(u["cache_write"]), fmt(u["output"]), fmt(u["peak_ctx"]),
                f"{u['minutes']:.0f}"] if (u := r["usage"]) else ["—"] * 6),
             esc(r["estado"] or "—"), esc(r["encargo"])] for r in reversed(rows)]
    content = (f"<div class='two'><div><h4>Contexto releído (caché leída) por sesión</h4>{bars(rows)}</div>"
               f"<div><h4>Por sesión aceptada</h4>"
               f"{table(['desk', 'aceptadas', 'caché leída', 'caché escrita', 'salida'], per, {1, 2, 3, 4})}"
               f"<p class='muted small'>Reparte entre las aceptadas el consumo de todas las revisadas.</p></div></div>"
               f"<details><summary>Todas las sesiones</summary>"
               + table(["inicio", "desk", "modelo", "esfuerzo", "lanz.", "turnos", "caché leída", "caché escrita",
                        "salida", "pico ctx", "min", "estado", "encargo"], body, set(range(4, 11)))
               + "</details>")
    return panel("Consumo", content, "Tokens de las transcripciones de Claude Code. La cuota de la suscripción no se "
                                     "expone en local.")


def section_health(h: dict) -> str:
    v = h["violations"]
    status = chip("integrity.py OK", "good", "✓") if not v else chip(f"integrity.py: {len(v)} incumplimientos",
                                                                         "critical", "■")
    detail = table(["check", "archivo", "motivo"], [[esc(x.check), f"{esc(x.path)}:{x.line}", esc(x.msg)]
                                                    for x in v[:20]]) if v else ""
    return panel("Salud del repo", f"<p>{status} {chip(str(h['dirty']) + ' archivos sin commitear')}</p>"
                                   f"<p class='small'><span class='muted'>Último commit</span> <code>{esc(h['head'])}</code></p>"
                                   f"{detail}")


CSS = """
:root{color-scheme:light;--page:#f9f9f7;--surface:#fcfcfb;--ink:#0b0b0b;--ink-2:#52514e;--muted:#898781;
--grid:#e1e0d9;--axis:#c3c2b7;--ring:rgba(11,11,11,.10);--accent:#2a78d6;--accent-wash:rgba(42,120,214,.10);
--good:#0ca30c;--good-ink:#006300;--warning:#fab219;--critical:#d03b3b;--neutral-wash:rgba(11,11,11,.05)}
@media (prefers-color-scheme:dark){:root:not([data-theme="light"]){color-scheme:dark;--page:#0d0d0d;--surface:#1a1a19;
--ink:#f0efec;--ink-2:#c3c2b7;--grid:#2c2c2a;--axis:#383835;--ring:rgba(255,255,255,.10);--accent:#3987e5;
--accent-wash:rgba(57,135,229,.16);--good-ink:#0ca30c;--neutral-wash:rgba(255,255,255,.06)}}
:root[data-theme="dark"]{color-scheme:dark;--page:#0d0d0d;--surface:#1a1a19;--ink:#f0efec;--ink-2:#c3c2b7;
--grid:#2c2c2a;--axis:#383835;--ring:rgba(255,255,255,.10);--accent:#3987e5;--accent-wash:rgba(57,135,229,.16);
--good-ink:#0ca30c;--neutral-wash:rgba(255,255,255,.06)}
*{box-sizing:border-box}
body{margin:0;background:var(--page);color:var(--ink);font:14px/1.5 system-ui,-apple-system,"Segoe UI",sans-serif;
font-variant-numeric:tabular-nums}
.wrap{max-width:1280px;margin:0 auto;padding:20px 16px 48px}
.top{display:flex;flex-wrap:wrap;gap:12px;align-items:flex-end;justify-content:space-between;margin-bottom:16px}
h1{font-size:22px;font-weight:650;margin:0;letter-spacing:-.01em}
.top p{margin:2px 0 0;color:var(--muted);font-size:12.5px}
h2{font-size:15px;font-weight:600;margin:0}h3{font-size:15px;margin:0}
h4{font-size:12px;font-weight:600;text-transform:uppercase;letter-spacing:.04em;color:var(--muted);margin:18px 0 8px}
.tiles{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px;margin-bottom:16px}
.tile{background:var(--surface);border:1px solid var(--ring);border-radius:10px;padding:14px 16px}
.tile-label{font-size:12.5px;color:var(--ink-2)}
.tile-value{font-size:28px;font-weight:600;line-height:1.15;margin-top:4px}
.tile-value small{font-size:15px;color:var(--muted);font-weight:500}
.tile-note{font-size:12px;color:var(--muted);margin-top:2px;min-height:18px}
.tile.alert-tile{box-shadow:inset 3px 0 0 var(--critical)}
.panel{background:var(--surface);border:1px solid var(--ring);border-radius:12px;padding:16px 18px;margin-bottom:16px}
.panel>header{display:flex;flex-wrap:wrap;gap:8px 16px;align-items:baseline;margin-bottom:10px}
.sub{margin:0;color:var(--muted);font-size:12.5px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:12px}
.card{border:1px solid var(--ring);border-radius:10px;padding:14px}
.card-head{display:flex;justify-content:space-between;align-items:center;gap:8px}
.metrics{display:grid;grid-template-columns:repeat(4,1fr);gap:8px;margin:10px 0}
.metrics div{display:flex;flex-direction:column}.metrics span{font-size:11.5px;color:var(--muted)}
.metrics b{font-size:17px;font-weight:600}
.meter{position:relative;height:8px;border-radius:4px;background:var(--accent-wash);overflow:hidden}
.meter .fill{height:100%;border-radius:4px}.meter .tick{position:absolute;top:0;bottom:0;width:2px;background:var(--surface)}
.meter-legend{display:flex;justify-content:space-between;font-size:11.5px;color:var(--muted);margin-top:4px}
.meter-legend b{color:var(--ink)}
.fill.accent,.seg.accent,.dot.accent{background:var(--accent)}.fill.critical,.seg.critical,.dot.critical{background:var(--critical)}
.seg.good,.dot.good{background:var(--good)}.seg.muted,.dot.muted{background:var(--axis)}
.alert{display:flex;gap:6px;margin:8px 0 0;font-size:12.5px;color:var(--ink-2)}.alert i{color:var(--critical);font-style:normal}
.chip{display:inline-flex;align-items:center;gap:4px;font-size:11.5px;font-weight:500;padding:1px 8px;border-radius:999px;
background:var(--neutral-wash);color:var(--ink-2);white-space:nowrap;margin-right:4px}
.chip i{font-style:normal;font-size:9px}.chip.good i{color:var(--good)}.chip.accent i{color:var(--accent)}
.chip.critical i{color:var(--critical)}.chip.warning i{color:var(--warning)}.chip.muted i{color:var(--muted)}
.muted{color:var(--muted)}.small{font-size:12.5px}.empty{color:var(--muted);font-size:13px}
code{font:12px ui-monospace,"Cascadia Code",Consolas,monospace;background:var(--neutral-wash);padding:1px 4px;border-radius:4px}
details{margin-top:12px}summary{cursor:pointer;font-size:12.5px;color:var(--ink-2)}
pre{font:11.5px/1.45 ui-monospace,Consolas,monospace;white-space:pre-wrap;max-height:180px;overflow:auto;
background:var(--page);padding:8px 10px;border-radius:6px;margin:8px 0 0}
.two{display:grid;grid-template-columns:repeat(auto-fit,minmax(340px,1fr));gap:8px 24px}
.two.wide-left{grid-template-columns:minmax(0,1.6fr) minmax(280px,1fr)}
@media (max-width:820px){.two.wide-left{grid-template-columns:1fr}.metrics{grid-template-columns:repeat(2,1fr)}}
.count{display:inline-block;min-width:20px;text-align:center;background:var(--neutral-wash);color:var(--ink);border-radius:999px;
font-size:11px;padding:0 6px;margin-left:4px}
ul.todo{list-style:none;margin:0;padding:0}ul.todo li{padding:8px 0;border-bottom:1px solid var(--grid);font-size:13px}
ul.todo li:last-child{border-bottom:0}
.paper-head{display:flex;gap:16px;justify-content:space-between;align-items:flex-start}
.estado{margin:0;font-size:14.5px;max-width:80ch}
.big{text-align:right;white-space:nowrap}.big b{font-size:32px;font-weight:600}.big span{color:var(--muted);margin-left:4px}
.segbar{display:flex;gap:2px;height:10px;margin:8px 0 6px}.seg{border-radius:4px;min-width:4px}
.legend{display:flex;flex-wrap:wrap;gap:4px 16px;font-size:12px;color:var(--ink-2)}
.legend .dot,.dot{display:inline-block;width:8px;height:8px;border-radius:50%;margin-right:6px}
ol.timeline{list-style:none;margin:0;padding:0 0 0 14px;border-left:1px solid var(--grid)}
ol.timeline li{position:relative;padding:0 0 10px 6px;font-size:13px}
ol.timeline li:before{content:"";position:absolute;left:-19px;top:6px;width:8px;height:8px;border-radius:50%;
background:var(--accent);box-shadow:0 0 0 2px var(--surface)}
ol.timeline li:not(:first-child):before{background:var(--axis)}
ol.timeline time{display:block;font-size:11.5px;color:var(--muted)}
.table-wrap{overflow-x:auto}
table{border-collapse:collapse;width:100%;font-size:12.5px}
th{font-weight:500;color:var(--muted);text-align:left;padding:6px 10px 6px 0;border-bottom:1px solid var(--axis);white-space:nowrap}
td{padding:7px 10px 7px 0;border-bottom:1px solid var(--grid);vertical-align:top}.num{text-align:right}
tbody tr:hover{background:var(--neutral-wash)}
.bars{display:flex;flex-direction:column;gap:6px}
.bar-row{display:grid;grid-template-columns:120px 1fr 96px;gap:10px;align-items:center;font-size:12.5px;padding:2px 0}
.bar-row:hover{background:var(--neutral-wash);border-radius:6px}
.bar-label{display:flex;flex-direction:column;line-height:1.2}.bar-label small{color:var(--muted);font-size:11px}
.bar-track{display:flex;align-items:center;gap:6px;min-width:0}
.bar{height:14px;border-radius:0 4px 4px 0;background:var(--accent);min-width:2px}
.bar-value{font-size:12px;color:var(--ink-2);white-space:nowrap}.bar-state{font-size:11.5px;color:var(--muted)}
"""


def render() -> str:
    active, rows, ps, h = desk.active(), desk.sessions(), papers(), health()
    authors, coord = waiting(ps, rows, active)
    tasks_all = [t for p in ps for t in p["tasks"]]
    done = sum(t["state"] == "hecha" for t in tasks_all)
    cache = [r["usage"]["cache_read"] for r in rows if r["usage"]]
    tiles = (tile("Desks activas", f"{len(active)}<small> / {desk.MAX_CONCURRENT}</small>",
                  ", ".join(esc(n) for n in active) or "ninguna")
             + tile("Tareas hechas", f"{done}<small> / {len(tasks_all)}</small>",
                    f"{sum(t['state'] == 'en curso' for t in tasks_all)} en curso")
             + tile("Esperan a los autores", str(len(authors)), "bloqueos, RECHAZADOS y lecciones",
                    "alert-tile" if authors else "")
             + tile("Por revisar (Coordinación)", str(len(coord)), "sesiones y aprobaciones caducadas",
                    "alert-tile" if coord else "")
             + tile("Caché leída registrada", fmt(sum(cache)), f"{len(cache)} sesiones de desk")
             + tile("integrity.py", "OK" if not h["violations"] else str(len(h["violations"])),
                    "sin incumplimientos" if not h["violations"] else "incumplimientos",
                    "alert-tile" if h["violations"] else ""))
    return (f"<!doctype html><html lang='es'><head><meta charset='utf-8'><meta name='viewport' "
            f"content='width=device-width,initial-scale=1'><meta http-equiv='refresh' content='30'>"
            f"<title>Research Desk</title><style>{CSS}</style></head><body><div class='wrap'>"
            f"<div class='top'><div><h1>Research Desk</h1><p>Panel de estado · actualizado "
            f"{time.strftime('%d/%m/%Y %H:%M:%S')} · se recarga cada 30 s</p></div></div>"
            f"<div class='tiles'>{tiles}</div>"
            + section_now(active) + section_waiting(authors, coord)
            + "".join(section_paper(p) for p in ps)
            + section_usage(rows) + section_health(h) + "</div></body></html>")


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
