// Genera la oficina de Pixel Agents (planta abierta) y la configuración de cada desk.
// - Arriba: Literatura → Teoría → Datos → Econometría, en orden del pipeline, en planta abierta.
// - Abajo: Redacción (abierta) · Dirección (despacho cerrado con mesa de reuniones) · Referee (cerrado, aislado).
// - Cada zona es un Area con el nombre en gris sobre el suelo; el centro de cada zona queda libre.
// - Registra un Directory por desk y escribe desks/<desk>/.claude/settings.json (hook + acceso al repo).
// Uso (con el servidor de Pixel Agents parado): node .claude/office/build_office.mjs
import fs from 'node:fs';
import os from 'node:os';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '../..');
const PA = path.join(os.homedir(), '.pixel-agents');

const VOID = 255, WALL = 0;
const ZW = 10, ZH = 10, AISLE = 2;
const COLS = 1 + 4 * ZW + 3 * AISLE + 1;           // 48
const ROWS = 27;
const TOP_Y = 2, CORRIDOR = [12, 13, 14], DOOR_ROW = 15, BOT_Y = 16, BOTTOM_WALL = 26;
const zx = (k) => 1 + k * (ZW + AISLE);             // primera columna de la zona k

const LABEL_GRAY = '#9ca3af';
const C = {
  wall: { h: 214, s: 30, b: -100, c: -55 },
  common: { h: 210, s: 4, b: 8, c: -25 },          // pasillos: gris claro
  wood: { h: 30, s: 40, b: -25, c: -70 },
  tint: (h) => ({ h, s: 14, b: 12, c: -30 }),      // suelos claros con un matiz por zona
};
const FLOOR = { plain: 1, wood: 7 };

const tiles = Array(COLS * ROWS).fill(VOID);
const tileColors = Array(COLS * ROWS).fill(null);
const areaTiles = Array(COLS * ROWS).fill(null);
const set = (c, r, t, color, area = null) => {
  const i = r * COLS + c;
  tiles[i] = t; tileColors[i] = t === VOID ? null : color; areaTiles[i] = area;
};
const fill = (c0, r0, w, h, t, color, area = null) => {
  for (let r = r0; r < r0 + h; r++) for (let c = c0; c < c0 + w; c++) set(c, r, t, color, area);
};

const furniture = [];
let uid = 0;
const put = (type, col, row) => furniture.push({ uid: `f-desk-${uid++}`, type, col, row });

// Fila de 3 puestos contiguos (bench desk). facing 'up': silla debajo, mirando a la pantalla.
// facing 'down': silla encima, de cara a la mesa (vemos la parte trasera del PC).
function benchRow(x0, y, facing) {
  for (const dx of [0, 3, 6]) {
    put('DESK_FRONT', x0 + dx, y);
    if (facing === 'up') {
      put('PC_FRONT_OFF', x0 + dx + 1, y);
      put('CUSHIONED_CHAIR_BACK', x0 + dx + 1, y + 2);
    } else {
      put('PC_BACK', x0 + dx + 1, y);
      put('CUSHIONED_CHAIR_FRONT', x0 + dx + 1, y - 1);
    }
  }
}

// --- Envolvente: todo muro, luego se vacía el interior
fill(0, 1, COLS, ROWS - 1, WALL, C.wall);
fill(1, TOP_Y, COLS - 2, ZH, FLOOR.plain, C.common);          // banda superior (pasillos entre zonas)
fill(1, CORRIDOR[0], COLS - 2, CORRIDOR.length, FLOOR.plain, C.common);

// --- Zonas abiertas superiores: 6 puestos cada una (3 arriba, 3 abajo), centro libre
const TOP = [
  ['Literatura', 'literatura', 28, ['DOUBLE_BOOKSHELF', 'DOUBLE_BOOKSHELF', 'BOOKSHELF']],
  ['Teoría', 'teoria', 265, ['WHITEBOARD', 'WHITEBOARD', 'CLOCK']],
  ['Datos', 'datos', 150, ['BOOKSHELF', 'SMALL_PAINTING', 'SMALL_PAINTING_2']],
  ['Econometría', 'econometria', 205, ['WHITEBOARD', 'LARGE_PAINTING', 'CLOCK']],
];
TOP.forEach(([label, , hue, deco], k) => {
  const x0 = zx(k);
  fill(x0, TOP_Y, ZW, ZH, FLOOR.plain, C.tint(hue), label);
  benchRow(x0, TOP_Y + 1, 'up');                                // filas 3-4, sillas fila 5
  benchRow(x0, TOP_Y + 7, 'down');                              // filas 9-10, sillas fila 8
  put(deco[0], x0 + 1, 0); put(deco[1], x0 + 4, 0); put(deco[2], x0 + 7, 0);
  if (k < 3) put('LARGE_PLANT', x0 + ZW, TOP_Y);                // planta en el pasillo entre zonas
});

// --- Banda inferior
// Redacción: abierta al pasillo
const xR = zx(0);
fill(xR, DOOR_ROW, ZW, 1, FLOOR.plain, C.common);
fill(xR, BOT_Y, ZW, ZH, FLOOR.plain, C.tint(15), 'Redacción');
benchRow(xR, BOT_Y + 1, 'up');
benchRow(xR, BOT_Y + 7, 'down');

// Dirección: despacho cerrado (zonas 1-2 + pasillo intermedio = 22 de ancho), madera
const xD = zx(1), wD = 2 * ZW + AISLE;
fill(xD, BOT_Y, wD, ZH, FLOOR.wood, C.wood, 'Dirección');
fill(xD + wD / 2 - 1, DOOR_ROW, 2, 1, FLOOR.wood, C.wood, 'Dirección');   // puerta
// Puestos de Dirección (arriba a la izquierda): Coordinación y Director científico
put('DESK_FRONT', xD + 1, BOT_Y + 1); put('PC_FRONT_OFF', xD + 2, BOT_Y + 1); put('CUSHIONED_CHAIR_BACK', xD + 2, BOT_Y + 3);
put('DESK_FRONT', xD + 4, BOT_Y + 1); put('PC_FRONT_OFF', xD + 5, BOT_Y + 1); put('CUSHIONED_CHAIR_BACK', xD + 5, BOT_Y + 3);
// Mesa de reuniones (derecha), con sillas a ambos lados
const tx = xD + wD - 6, ty = BOT_Y + 2;
put('TABLE_FRONT', tx, ty);
put('WOODEN_CHAIR_SIDE', tx - 1, ty); put('WOODEN_CHAIR_SIDE', tx - 1, ty + 2);
put('WOODEN_CHAIR_SIDE:left', tx + 3, ty); put('WOODEN_CHAIR_SIDE:left', tx + 3, ty + 2);
// Rincón de sofás (abajo a la izquierda) y plantas
put('SOFA_FRONT', xD + 2, BOT_Y + 6); put('COFFEE_TABLE', xD + 2, BOT_Y + 7); put('COFFEE', xD + 2, BOT_Y + 8);
put('SOFA_SIDE', xD + 1, BOT_Y + 7); put('SOFA_SIDE:left', xD + 4, BOT_Y + 7);
put('LARGE_PLANT', xD + wD - 2, BOT_Y + 7); put('PLANT', xD, BOT_Y + 8);

// Referee: cerrado y aislado en la esquina (muro doble de separación)
const xF = zx(3);
fill(xF, BOT_Y, ZW, ZH, FLOOR.plain, C.tint(355), 'Referee');
fill(xF + 4, DOOR_ROW, 2, 1, FLOOR.plain, C.tint(355), 'Referee');       // puerta
benchRow(xF, BOT_Y + 1, 'up');
put('PLANT_2', xF, BOT_Y + 8); put('PLANT', xF + ZW - 1, BOT_Y + 8);
// Los pasillos entre zonas de la banda inferior se quedan como muro: Dirección y Referee son cerrados.

// Plantas en el pasillo
put('PLANT', 1, CORRIDOR[0]); put('PLANT_2', COLS - 2, CORRIDOR[0]);

const AREAS = ['Literatura', 'Teoría', 'Datos', 'Econometría', 'Redacción', 'Dirección', 'Referee'];
const layout = {
  version: 1, cols: COLS, rows: ROWS, layoutRevision: 2,
  tiles, tileColors, areaTiles, furniture, pets: [],
  areas: AREAS.map((label) => ({ label, color: LABEL_GRAY })),
};

const layoutPath = path.join(PA, 'layout.json');
if (fs.existsSync(layoutPath) && !fs.existsSync(layoutPath + '.orig')) fs.copyFileSync(layoutPath, layoutPath + '.orig');
fs.writeFileSync(layoutPath, JSON.stringify(layout, null, 2));

// --- Directories + mappings
// [nombre del Directory, carpeta, Area]. La Dirección tiene dos roles en el mismo despacho.
const DESKS = [
  ...TOP.map(([label, dir]) => [label, `desks/${dir}`, label]),
  ['Redacción', 'desks/redaccion', 'Redacción'],
  ['Referee', 'desks/referee', 'Referee'],
  ['Dirección', '.', 'Dirección'],
  ['Director científico', 'desks/direccion-cientifica', 'Dirección'],
];
const ours = DESKS.map(([name, dir, area]) => ({ name, path: path.resolve(ROOT, dir), area }));
const cfgPath = path.join(PA, 'config.json');
const cfg = JSON.parse(fs.readFileSync(cfgPath, 'utf8'));
const ourNames = new Set([...ours.map((d) => d.name), 'Sala común']);
cfg.directories = [...(cfg.directories || []).filter((d) => !ourNames.has(d.name)), ...ours.map(({ name, path: p }) => ({ name, path: p }))];
const mappings = Object.fromEntries(Object.entries(cfg.standalone.areaMappings || {}).filter(([k]) => !ourNames.has(k)));
// Las sesiones lanzadas desde una terminal llegan con el nombre de su carpeta (p. ej. "datos"),
// las lanzadas desde la oficina con el del Directory ("Datos"): se mapean ambos.
const aliases = ours.map((d) => [path.basename(d.path), [d.area]]);
cfg.standalone.areaMappings = { ...mappings, ...Object.fromEntries(ours.map((d) => [d.name, [d.area]])), ...Object.fromEntries(aliases) };
cfg.standalone.showAreas = true;
fs.writeFileSync(cfgPath, JSON.stringify(cfg, null, 2));

// --- Configuración de cada desk: hereda el hook protect-raw y puede trabajar en todo el repo
const deskSettings = {
  permissions: { additionalDirectories: ['../..'] },
  hooks: {
    PreToolUse: [{
      matcher: 'Edit|Write|NotebookEdit',
      hooks: [{ type: 'command', command: 'node "$CLAUDE_PROJECT_DIR/../../.claude/hooks/protect-raw.js"' }],
    }],
  },
};
for (const [, dir] of DESKS.filter(([, d]) => d !== '.')) {
  const p = path.join(ROOT, dir, '.claude');
  fs.mkdirSync(p, { recursive: true });
  fs.writeFileSync(path.join(p, 'settings.json'), JSON.stringify(deskSettings, null, 2) + '\n');
}

console.log(`Layout ${COLS}x${ROWS}: ${furniture.length} muebles, ${furniture.filter((f) => f.type.startsWith('PC')).length} PCs, ${AREAS.length} áreas, ${ours.length} directorios.`);
