import dashboard

TASKS = """# p — TASKS
Estado: `[ ]` pendiente · `[~]` en curso · `[x]` hecha · `[!]` bloqueada.

## Fase 0
- [x] **0.1** · coordination · Inventario hecho. Detalle largo.
  - 2026-11-04 · nota que no es una tarea

## Diseño F
- [!] **F4** · econometrics · `mc-validate` del estimador. Hecho: cobertura.
- [~] **F9** · econometrics · MC del diseño **rediseñado**. Encargo: x.
- [ ] **F10** · referee · Auditoría del MC de F9 en sesión nueva, antes de estimar nada.
"""


def test_tasks_parse_state_desk_title_and_section():
    ts = dashboard.tasks(TASKS)
    assert [(t["id"], t["state"], t["desk"], t["section"]) for t in ts] == [
        ("0.1", "hecha", "coordination", "Fase 0"), ("F4", "bloqueada", "econometrics", "Diseño F"),
        ("F9", "en curso", "econometrics", "Diseño F"), ("F10", "pendiente", "referee", "Diseño F")]
    assert ts[2]["title"] == "MC del diseño rediseñado"  # primera frase, sin marcas de Markdown


def test_spec_estado_joins_the_paragraph_and_strips_markup():
    spec = "# p — SPEC\n\nEstado: **Diseño F; prereg aprobado.** Siguiente paso: F4\n(Monte Carlo) antes.\n\n## Otra\n"
    assert dashboard.spec_estado(spec) == "Diseño F; prereg aprobado. Siguiente paso: F4 (Monte Carlo) antes."
    assert "no tiene" in dashboard.spec_estado("# sin estado")


def test_render_reads_the_real_repo_and_escapes_html():
    page = dashboard.render()
    assert all(h in page for h in ("<h2>Ahora</h2>", "<h2>Espera a alguien</h2>", "<h2>Consumo</h2>",
                                   "<h2>Salud del repo</h2>", "p01-liquidity"))
    assert "<script" not in page
