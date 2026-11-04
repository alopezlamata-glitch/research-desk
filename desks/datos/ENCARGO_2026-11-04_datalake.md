# Encargo de los autores a Datos — 2026-11-04 · Datalake permanente

## Petición literal de los autores
> "Que el de datos busque en repos de internet datos económicos y los guarde para utilizarlos posteriormente,
> se usen o no; sirven de base de datos para siempre para otros proyectos. Que empiece por lo que puede llegar
> a ser relevante para este paper, no solo lo mencionado en anteriores PDFs sino otras series interesantes."

Lee primero `datalake/README.md` (estructura y reglas: obligatorias), `kb/data_catalog.md`,
`papers/p01-liquidity/exploration/INVENTORY.md` y `kb/topics/policy-transmission/README.md` (las dos líneas
de investigación). Rutas relativas a la raíz del repo (`../../`).

## Prioridades (en este orden)
**Nivel 1 — núcleo de p01 (EE. UU., trimestral/mensual, lo más largo posible):**
- Actividad y precios: PIB real y nominal, potencial CBO, deflactores, PCE, inversión, consumo, paro.
- Política: fed funds efectivo, IORB/IOER, SOFR, rendimientos del Tesoro (3m–30a), balance de la Fed (WALCL),
  reservas (WRESBAL), RRP, TGA, M2.
- Deuda y servicio de la deuda: deuda pública (total y en manos del público), pagos de intereses federales
  (A091RC1Q027SBEA), deuda de empresas no financieras y hogares, **debt service ratios** (Fed y BIS),
  vencimiento medio de la deuda del Tesoro, peso de la deuda a tipo variable (hipotecas ARM, préstamos C&I).
- Banca: capital y activos agregados (FDIC QBP, H.8), márgenes de intermediación, morosidad, encuesta de
  condiciones de crédito (SLOOS).
- Condiciones financieras y confianza: NFCI/ANFCI, excess bond premium (Gilchrist-Zakrajšek, Fed), spreads
  (Baa, high yield), VIX, Michigan (sentimiento y expectativas de inflación), SPF.
- **Shocks identificados:** Bauer-Swanson (FRBSF, **vintage ago-2025 y dic-2023**, guarda las dos), USMPD
  (FRBSF), Jarociński-Karadi, Romer-Romer (monetarios y fiscales), noticias militares de Ramey y
  Ramey-Zubairy, Aruoba-Drechsel si está disponible.

**Nivel 2 — panel internacional (para la identificación con más datos):**
JST Macrohistory, BIS (crédito total, debt service ratios, tipos oficiales, precios inmobiliarios), Baron-Verner-Xiong
(crisis bancarias), Guajardo-Leigh-Pescatori (consolidaciones), Laeven-Valencia (crisis), OCDE (confianza),
FMI (deuda histórica), BCE y BoE (incluido el "millennium dataset").

**Nivel 3 — interesantes aunque no se usen ahora** (tu criterio, justificado en el catálogo): series que un
investigador de transmisión monetaria, liquidez y finanzas públicas querría tener a mano.

## Cómo
- Un script por fuente en `datalake/fetch/<fuente>.py` (usa `requests`/`pandas`; `uv run python datalake/fetch/<fuente>.py`).
  Al guardar escribe la fila del `MANIFEST.csv` (ruta, URL, fecha, sha256, vintage).
- `datalake/fetch/update_all.py` llama a todos.
- Comprueba cada descarga: que el archivo no sea una página de error, el rango de fechas, que no haya duplicados
  y las unidades. Lo que falle se anota como **ROTO** en el catálogo con el motivo.
- `datalake/CATALOG.md`: tabla con fuente, series, frecuencia, cobertura, unidades, ruta, relevancia
  (p01-línea 1 / línea 2 / panel / general) y estado (OK / ROTO / requiere clave / requiere login).
- Actualiza `kb/data_catalog.md`: marca como **probada** cada fuente que funcione, con enlace al CATALOG.
- Lecciones en `kb/lessons/data.md`.

## Reglas
- Solo fuentes públicas y gratuitas, sin login ni claves en el código.
- No escribas en `raw/` salvo con los scripts. No toques los `papers/` ni otras carpetas.
- Si algo pesa más de 200 MB, no lo descargues: anótalo en el catálogo con su URL.
- No inventes códigos de serie: comprueba que existen antes de añadirlos.
