// PreToolUse: guardarraíles de la Research Desk (spec: specs/guardrails/SPEC.md).
//  1. Datos brutos y muestra reservada son de solo lectura: data/raw/, datalake/raw/, data/holdout/.
//  2. data/holdout/ no se lee (Read/Grep/Glob/Bash) hasta abrirla con tools/research.py (deja audits/holdout_opened.md).
//  3. No se salta el pre-commit: ni `git commit --no-verify|-n` ni cambios de core.hooksPath.
//  4. El Referee (sesión lanzada en desks/referee/ o en papers/<slug>/audits/) solo escribe en audits/, en el TASKS.md
//     del paper y en kb/lessons/referee.md: nunca en el código ni en el texto del autor.
// Sale con 2 y el motivo en stderr para bloquear; con 0 deja pasar.
const fs = require('fs');
const path = require('path');

const RAW = /(^|\/)(data|datalake)\/raw\//;
const HOLDOUT = /(^|\/)data\/holdout(\/|$)/;
const ROOT = path.resolve(__dirname, '..', '..');
const REFEREE_SESSION = /(^|\/)(desks\/referee|papers\/[^/]+\/audits)(\/|$)/;
const REFEREE_WRITABLE = /^(papers\/[^/]+\/audits\/|papers\/[^/]+\/TASKS\.md$|kb\/lessons\/referee\.md$)/;

function block(msg) {
  console.error(`Bloqueado por guard.js: ${msg}`);
  process.exit(2);
}

const norm = (p) => (p || '').replace(/\\/g, '/');

// Raíz del paper = lo que precede a /data/holdout; la apertura deja <paper>/audits/holdout_opened.md.
function holdoutOpened(p, cwd) {
  const m = norm(p).match(/^(.*?)(?:^|\/)data\/holdout(?:\/|$)/);
  const paper = path.resolve(cwd || '.', m && m[1] ? m[1] : '.');
  return fs.existsSync(path.join(paper, 'audits', 'holdout_opened.md'));
}

function checkBash(cmd, cwd) {
  const c = norm(cmd);
  // Solo las líneas de comando: el cuerpo de un heredoc (p. ej. un mensaje de commit) no se interpreta.
  const commandLines = c.replace(/<<-?\s*['"]?(\w+)['"]?[^\n]*\n[\s\S]*?\n\1\s*(\n|$)/g, '\n');
  for (const part of commandLines.split(/&&|\|\||;|\||\n/)) {
    if (/\bgit\b(\s+-c\s+\S+)*\s+commit\b/.test(part) && /(^|\s)(--no-verify|-n|-[a-zA-Z]*n[a-zA-Z]*)(\s|$)/.test(part.replace(/-m\s+("[^"]*"|'[^']*'|\S+)/g, ''))) {
      block('git commit sin pre-commit (--no-verify/-n). Corrige las violaciones de tools/integrity.py.');
    }
  }
  for (const part of commandLines.split(/&&|\|\||;|\||\n/).map((s) => s.trim())) {
    const allowed = /^git\s+config\s+(--local\s+)?(--get\s+core\.hooksPath|core\.hooksPath\s+\.githooks)$/i;
    if (/core\.hooksPath/i.test(part) && !allowed.test(part)) {
      block('core.hooksPath solo puede valer .githooks: el pre-commit es obligatorio.');
    }
  }
  // Solo cuenta si la ruta va a un comando que lee o copia archivos (no si solo se escribe como texto).
  const READER = /^(sudo\s+)?(cat|head|tail|less|more|type|gc|get-content|grep|rg|egrep|sed|awk|cut|sort|cp|copy|copy-item|xcopy|robocopy|mv|xxd|od|strings|python3?|py|uv|node|Rscript|duckdb|sqlite3)\b/i;
  for (const part of commandLines.split(/&&|\|\||;|\||\n/).map((s) => s.trim())) {
    if (!READER.test(part) || /tools\/research\.py/.test(part)) continue;
    for (const m of part.matchAll(/["']?(\S*?data\/holdout\S*?)["']?(\s|$)/g)) {
      if (!holdoutOpened(m[1], cwd)) block('la muestra reservada (data/holdout/) no se ha abierto. Usa research.open_holdout().');
    }
  }
}

let input = '';
process.stdin.on('data', (d) => (input += d)).on('end', () => {
  let ev;
  try { ev = JSON.parse(input); } catch { process.exit(0); }
  const tool = ev.tool_name || '';
  const ti = ev.tool_input || {};
  const cwd = ev.cwd || process.cwd();
  const target = norm(ti.file_path || ti.notebook_path || ti.path || '');

  if (['Edit', 'Write', 'NotebookEdit', 'MultiEdit'].includes(tool) || (!tool && target)) {
    if (RAW.test(target)) block(`${target} es dato bruto (solo lectura). Usa un script de descarga.`);
    if (HOLDOUT.test(target)) block(`${target} es la muestra reservada (solo lectura).`);
    // La sesión se identifica por la carpeta en que se lanzó (CLAUDE_PROJECT_DIR), que no cambia con un `cd`.
    const session = norm(process.env.CLAUDE_PROJECT_DIR || cwd);
    if (REFEREE_SESSION.test(path.relative(ROOT, session).replace(/\\/g, '/'))) {
      const rel = path.relative(ROOT, path.resolve(cwd, target)).replace(/\\/g, '/');
      if (!REFEREE_WRITABLE.test(rel)) {
        block(`el Referee solo escribe en papers/<slug>/audits/, papers/<slug>/TASKS.md y kb/lessons/referee.md (no en ${rel}).`);
      }
    }
  }
  if (['Read', 'Grep', 'Glob'].includes(tool)) {
    const t = target || norm(ti.pattern || '');
    if (HOLDOUT.test(t) && !holdoutOpened(t, cwd)) {
      block('la muestra reservada (data/holdout/) no se ha abierto. Usa research.open_holdout().');
    }
  }
  if (tool === 'Bash') checkBash(ti.command || '', cwd);
  process.exit(0);
});
