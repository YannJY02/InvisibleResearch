// Fill only the researcher-side recommendations in the existing review workbook.
import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';

const owner = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const pipeline = path.join(owner, 'artifacts/variable-selection-review-2026-10-20');
const previous = path.join(owner, 'artifacts/variable-selection-2026-10-16/outputs',
  '01a1448c-26bc-7f42-b0ab-7515259cf126/route-b-variable-selection.xlsx');
const outputDir = path.join(pipeline, 'outputs/01a1448c-26bc-7f42-b0ab-7515259cf126');
await fs.mkdir(outputDir, { recursive: true });
const modules = process.env.ARTIFACT_NODE_MODULES || path.join(os.homedir(),
  '.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules');
try { await fs.symlink(modules, path.join(pipeline, 'node_modules'), 'dir'); }
catch (error) { if (error.code !== 'EEXIST') throw error; }
const runtime = createRequire(path.join(pipeline, 'runtime.cjs'));
const { Workbook, FileBlob, SpreadsheetFile } = await import(runtime.resolve('@oai/artifact-tool'));
const wb = await SpreadsheetFile.importXlsx(await FileBlob.load(previous));
const researcher = wb.worksheets.getItem('Jinyi');
const supervisor = wb.worksheets.getItem('Saurabh');
const guide = wb.worksheets.getItem('Guide');
// Shared instructions change; the supervisor's judgments and all other cells do not.
const supervisorContent = () => supervisor.getRange('A1:K88').values.map((row, i) =>
  row.map((value, j) => ((i === 3 || i === 4) && j === 0) || (i === 7 && j === 2) ? null : value));
const beforeSupervisor = JSON.stringify(supervisorContent());
const beforeSupervisorFormulas = JSON.stringify(supervisor.getRange('A1:K88').formulas);
const beforePreview = await wb.render({ sheetName: 'Jinyi', range: 'A1:F13', scale: 1 });
await fs.writeFile(path.join(pipeline, 'before-preview.png'), new Uint8Array(await beforePreview.arrayBuffer()));
const [header, ...lines] = (await fs.readFile(path.join(owner,
  'analysis/variable_selection_decisions.tsv'), 'utf8')).trimEnd().split('\n');
const names = header.split('\t');
const decisions = lines.map(line => Object.fromEntries(line.split('\t').map((value, i) => [names[i], value])));
if (decisions.length !== 80) throw new Error('Expected exactly 80 recommendations');
const current = researcher.getRange('B9:D88').values;
for (let i = 0; i < 80; i++) {
  if (current[i][0] !== decisions[i].field) throw new Error('Source column order changed');
  if (current[i][1] || current[i][2]) throw new Error('Existing researcher input requires reconciliation');
}
researcher.getRange('C9:D88').values = decisions.map(row => [row.decision, row.reason_en || null]);
researcher.getRange('A2').values = [['Route B variable selection proposal']];
researcher.getRange('A4').values = [['AI-assisted proposal requested October 20, 2026. Pending researcher confirmation; not a supervisor judgment.']];
for (const sheet of [researcher, supervisor]) {
  sheet.getRange('C8').values = [['Keep?']];
  sheet.getRange('A5').values = [['yes = keep; maybe = discuss; no = leave out. The two Scopus outcomes are kept as results, not predictors.']];
  // Rebuild the table metadata so Excel's native column name matches C8.
  const oldTable = sheet.tables.items[0];
  const { name, style, showFilterButton, showBandedColumns } = oldTable;
  oldTable.delete();
  const table = sheet.tables.add('A8:K88', true, name);
  table.style = style;
  table.showFilterButton = showFilterButton;
  table.showBandedColumns = showBandedColumns;
}
supervisor.getRange('A4').values = [['Mark yes, no or maybe independently. Add a short note only when a choice needs discussion. Compare after both reviewers finish.']];
researcher.getRange('D6').values = [['of 80 assessed. Unresolved choices remain maybe.']];
for (let i = 0; i < decisions.length; i++) {
  if (decisions[i].reason_en) {
    researcher.getRange(`A${i + 9}:K${i + 9}`).format.rowHeight =
      Math.max(64, Math.ceil(decisions[i].reason_en.length / 48) * 14 + 12);
  }
}
guide.getRange('B7:B8').values = [
  ['Jinyi contains an AI-assisted proposal requested by the researcher. Confirm this proposal before comparing with Saurabh\'s independently completed sheet.'],
  ['Jinyi has 27 yes, 7 maybe and 46 no. Notes cover the 7 open choices and a correction about created_date. Saurabh\'s choices and reasons remain blank.'],
];
guide.getRange('B12').values = [['Keep? asks whether to retain a field for the study. The two Scopus outcomes are yes, but never predictors. Other Scopus fields are matching evidence only. Unknown is not zero.']];
guide.getRange('B24').values = [['Researcher-side recommendations are prepared for human review. Supervisor judgment and discussion of disagreements remain outstanding.']];
wb.recalculate();
if (researcher.getRange('C6').values[0][0] !== 80) throw new Error('Researcher assessment counter failed');
if (supervisor.getRange('C6').values[0][0] !== 0) throw new Error('Supervisor counter changed');
if (JSON.stringify(supervisorContent()) !== beforeSupervisor ||
    JSON.stringify(supervisor.getRange('A1:K88').formulas) !== beforeSupervisorFormulas) {
  throw new Error('Unrelated supervisor content changed');
}
for (const [name, range] of [['Jinyi', 'A1:F14'], ['Jinyi', 'B65:K70'], ['Guide', 'A4:B13']]) {
  const preview = await wb.render({ sheetName: name, range, scale: 1.1 });
  await fs.writeFile(path.join(pipeline, `${name.toLowerCase()}-${range.replace(':', '-')}.png`),
    new Uint8Array(await preview.arrayBuffer()));
}
const scan = await wb.inspect({ kind: 'match', searchTerm: '#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!|#SPILL!|#CALC!',
  options: { useRegex: true, maxResults: 20 }, maxChars: 1500 });
await fs.writeFile(path.join(pipeline, 'formula-scan.ndjson'), scan.ndjson);
const output = path.join(outputDir, 'route-b-variable-selection.xlsx');
await (await SpreadsheetFile.exportXlsx(wb)).save(output);
await fs.writeFile(path.join(pipeline, 'workbook-review-checks.json'), JSON.stringify({
  original_field_order: true, researcher_assessed: 80, supervisor_assessed: 0,
  supervisor_judgments_and_noninstruction_cells_unchanged: true,
  supervisor_formulas_unchanged: true,
  shared_instruction_cells_updated: ['A4', 'A5', 'C8'],
  ordinary_selection_reasons_blank: decisions.filter(row => row.decision !== 'maybe' && row.field !== 'created_date').every(row => !row.reason_en),
  decisions: Object.fromEntries(['yes', 'maybe', 'no'].map(choice =>
    [choice, decisions.filter(row => row.decision === choice).length])), output,
}, null, 2));
console.log(JSON.stringify({ output, researcher_assessed: 80, supervisor_assessed: 0 }));
