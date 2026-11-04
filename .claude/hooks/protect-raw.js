// PreToolUse: bloquea Edit/Write/NotebookEdit sobre cualquier data/raw/ o datalake/raw/.
// Los datos brutos solo los escriben los scripts de descarga.
// ponytail: no cubre escrituras vía Bash; si un agente lo intenta, añadir matcher Bash con regex sobre el comando.
let input = '';
process.stdin.on('data', (d) => (input += d)).on('end', () => {
  let path = '';
  try {
    const ti = JSON.parse(input).tool_input || {};
    path = (ti.file_path || ti.notebook_path || '').replace(/\\/g, '/');
  } catch {
    process.exit(0);
  }
  if (/(^|\/)(data|datalake)\/raw\//.test(path)) {
    console.error(`Bloqueado: ${path} es dato bruto (solo lectura). Usa un script de descarga (code/data/download_*.py o datalake/fetch/*.py).`);
    process.exit(2);
  }
});
