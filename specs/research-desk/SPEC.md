# Research Desk — SPEC (infraestructura)

## Objetivo
Una desk de investigación económica operada **solo por agentes Claude**, supervisada por un humano,
que produce **working papers publicables** y es **reutilizable entre papers**.

## Requisitos
1. **Especialización:** 6 desks con un rol, unas herramientas y unas carpetas de escritura acotadas
   (literatura, teoría, datos, econometría, redacción, referee).
2. **Aprendizaje entre papers:** memoria persistente en `kb/`, curada por el humano.
3. **Rigor:** prerregistro de hipótesis, verificación simbólica, Monte Carlo de identificación,
   auditoría independiente y replicación cruzada en R.
4. **Reproducibilidad:** todo resultado se regenera desde scripts. Datos brutos inmutables con
   MANIFEST (URL, fecha y hash).
5. **Reutilización:** un paper nuevo = `/new-paper <slug>`. Los agentes son genéricos por método y el
   dominio vive en `kb/topics/` y en el SPEC del paper.
6. **Visualización:** ver a los agentes trabajar en una oficina pixel art en el navegador.
7. **Coste:** funciona con la suscripción de Claude (sin API key ni backend propio).

## Fuera de alcance
- Backend propio (FastAPI/Redis/Postgres) y orquestador con el Agent SDK.
- Datos de pago (WRDS).
- Ejecución autónoma sin supervisión humana de principio a fin.

## Criterios de aceptación
- [ ] Un agente no puede editar `data/raw/` con Edit/Write (hook probado).
- [ ] `uv run pytest` ejecuta los checks de teoría y los tests de datos de todos los papers.
- [ ] Pixel Agents muestra la sesión principal y los subagentes en el navegador.
- [ ] El Referee lanzado en sesión nueva produce un informe en `audits/` sin tocar otros archivos.
- [ ] `/new-paper` crea un paper desde la plantilla.
