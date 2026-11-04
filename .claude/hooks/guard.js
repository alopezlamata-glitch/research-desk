// PreToolUse: guardarraíles de la Research Desk (spec: specs/guardrails/SPEC.md).
//  1. Datos brutos y muestra reservada son de solo lectura: data/raw/, datalake/raw/, data/holdout/.
//  2. data/holdout/ no se lee (Read/Grep/Glob/Bash) hasta abrirla con tools/research.py (deja audits/holdout_opened.md).
//  3. No se salta el pre-commit: ni `git commit --no-verify|-n` ni cambios de core.hooksPath.
// Sale con 2 y el motivo en stderr para bloquear; con 0 deja pasar.
const fs = require('fs');
const path = require('path');

const RAW = /(^|\/)(data|datalake)\/raw\//;
const HOLDOUT = /(^|\/)data\/holdout(\/|$)/;

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
  if (/data\/holdout/.test(c) && !/tools\/research\.py/.test(c)) {
    for (const m of c.matchAll(/(\S*?)data\/holdout\S*/g)) {
      if (!holdoutOpened(m[0], cwd)) block('la muestra reservada (data/holdout/) no se ha abierto. Usa research.open_holdout().');
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
