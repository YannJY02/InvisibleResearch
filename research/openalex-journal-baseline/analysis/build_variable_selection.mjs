// Prepare independent review sheets. No research decision or model encoding is assigned.
import fs from 'node:fs/promises';
import path from 'node:path';
import os from 'node:os';
import { createRequire } from 'node:module';
import { fileURLToPath } from 'node:url';

const owner = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const pipeline = path.join(owner, 'artifacts/variable-selection-2026-10-16');
const outputDir = path.join(pipeline, 'outputs/01a1448c-26bc-7f42-b0ab-7515259cf126');
const modules = process.env.ARTIFACT_NODE_MODULES || path.join(os.homedir(),
  '.cache/codex-runtimes/codex-primary-runtime/dependencies/node/node_modules');
await fs.mkdir(pipeline, { recursive: true });
try { await fs.symlink(modules, path.join(pipeline, 'node_modules'), 'dir'); }
catch (error) { if (error.code !== 'EEXIST') throw error; }
const requireRuntime = createRequire(path.join(pipeline, 'runtime.cjs'));
const { Workbook, SpreadsheetFile } = await import(requireRuntime.resolve('@oai/artifact-tool'));
const profile = JSON.parse(await fs.readFile(path.join(pipeline, 'profile.json'), 'utf8'));
const delivery = JSON.parse(await fs.readFile(path.join(owner,
  'artifacts/two-route-delivery-2026-10-01/route-b-api/summary.json'), 'utf8'));
const dictionary = (await fs.readFile(path.join(owner, 'analysis/variable_selection_fields.tsv'), 'utf8'))
  .trimEnd().split('\n').map(line => line.split('\t'));
const definitions = dictionary.slice(1);
if (profile.header.length !== 80 || definitions.length !== 80 ||
    definitions.some((row, index) => row[0] !== profile.header[index])) {
  throw new Error('Field dictionary must match all 80 source columns in their original order');
}
if (profile.denominator_rows !== 207602) throw new Error('Unexpected Route B denominator');
const wb = Workbook.create();
const sheets = ['Jinyi', 'Saurabh'].map(name => wb.worksheets.add(name));
const guide = wb.worksheets.add('Guide');
const first = 9, last = first + definitions.length - 1;
const headers = ['Order', 'Field', 'Predictor?', 'Reason / question', 'Meaning', 'Observed example',
  'Value type', 'Null / missing', 'Empty list / object', 'Review considerations', 'Field group'];
const nonemptyExample = p => {
  const e = p.examples?.[0];
  if (!e) return 'No populated example observed';
  const raw = e.raw_preview;
  const text = `${e.source_id}: ${raw}`;
  return text.length > 160 ? text.slice(0, 157) + '...' : text;
};
const rows = definitions.map(([field, group, meaning, note], index) => {
  const p = profile.field_profiles[field], b = p.raw_buckets;
  const sum = Object.values(b).reduce((a, n) => a + n, 0);
  if (sum !== profile.denominator_rows) throw new Error(`Profile does not reconcile: ${field}`);
  const types = delivery.source_field_types[field] || Object.keys(p.parsed_type_counts);
  return [index + 1, field, null, null, meaning, nonemptyExample(p),
    [...types, ...(b.missing_marker ? ['missing'] : [])].join(', '),
    (b.missing_marker + b.null_marker + b.empty_string) / profile.denominator_rows,
    (b.empty_array + b.empty_object) / profile.denominator_rows, note, group];
});
const headerStyle = { fill: '#263C59', font: { name: 'Arial', size: 10, bold: true, color: '#FFFFFF' },
  horizontalAlignment: 'center', verticalAlignment: 'center', wrapText: true };
function baseStyle(sheet, range) {
  sheet.showGridLines = false;
  sheet.getRange(range).format.font = { name: 'Arial', size: 10, color: '#243247' };
  sheet.getRange(range).format.verticalAlignment = 'center';
  sheet.getRange(range).format.rowHeight = 24;
  sheet.getRange('A2').format.font = { name: 'Arial', size: 15, bold: true, color: '#263C59' };
}
for (const [index, sheet] of sheets.entries()) {
  baseStyle(sheet, `A1:K${last}`);
  sheet.tabColor = '#263C59';
  sheet.getRange('A2').values = [['Route B variable selection']];
  sheet.getRange('A3').values = [['207,602 journal records. October 1, 2026 API dataset. All 80 delivered columns, in source order.']];
  sheet.getRange('A4').values = [['Mark use as a predictor: yes, no or maybe, with a reason. Complete independently; compare after both reviewers finish.']];
  sheet.getRange('A5').values = [['Amber cells are editable. Topics and topic_share remain nested; granularity, encoding and the final Scopus outcome are undecided.']];
  sheet.getRange('B6').values = [['Marked fields']];
  sheet.getRange('C6').formulas = [[`=COUNTIF(C${first}:C${last},"yes")+COUNTIF(C${first}:C${last},"no")+COUNTIF(C${first}:C${last},"maybe")`]];
  sheet.getRange('D6').values = [['of 80. Enter a reason for each judgment.']];
  sheet.getRange('A8:K8').values = [headers];
  sheet.getRange(`A${first}:K${last}`).values = rows;
  sheet.tables.add(`A8:K${last}`, true, `Review${index + 1}`);
  sheet.getRange('A8:K8').format = headerStyle;
  sheet.getRange('A8:K8').format.rowHeight = 32;
  rows.forEach((row, index) => {
    const lines = Math.max(...[[1, 51], [4, 60], [5, 52], [9, 70]].map(([col, width]) =>
      Math.ceil(String(row[col]).length / width)));
    sheet.getRange(`A${first + index}:K${first + index}`).format.rowHeight = Math.max(34, lines * 14 + 10);
  });
  sheet.getRange(`A${first}:K${last}`).format.wrapText = true;
  sheet.getRange(`A${first}:K${last}`).format.verticalAlignment = 'top';
  const widths = [7, 39, 13, 42, 48, 43, 18, 16, 19, 57, 21];
  widths.forEach((width, col) => {
    const letter = String.fromCharCode(65 + col);
    sheet.getRange(`${letter}1:${letter}${last}`).format.columnWidth = width;
  });
  sheet.getRange(`A${first}:A${last}`).setNumberFormat('0');
  sheet.getRange(`H${first}:I${last}`).setNumberFormat('0.0%');
  sheet.getRange(`H${first}:I${last}`).format.horizontalAlignment = 'right';
  sheet.getRange(`C${first}:D${last}`).format.fill = '#FFF2CC';
  sheet.getRange(`C${first}:C${last}`).dataValidation = {
    rule: { type: 'list', values: ['yes', 'no', 'maybe'] },
  };
  for (const [choice, fill] of [['yes', '#E4F0E8'], ['no', '#F4E5E5'], ['maybe', '#FFF2CC']]) {
    sheet.getRange(`C${first}:C${last}`).conditionalFormats.add('cellIs', {
      operator: 'equal', formula: `"${choice}"`, format: { fill },
    });
  }
  sheet.freezePanes.freezeRows(8);
  sheet.freezePanes.freezeColumns(2);
}
baseStyle(guide, 'A1:F45');
guide.tabColor = '#A7B2C3';
guide.getRange('A2').values = [['Route B review guide']];
guide.getRange('A4:B13').values = [
  ['Dataset', 'Route B. OpenAlex API journals acquired October 1, 2026.'],
  ['Journal records', profile.denominator_rows],
  ['Columns', profile.header.length],
  ['Review workflow', 'Jinyi and Saurabh each complete their own identical sheet. Compare judgments and reasons afterwards.'],
  ['Blank judgments', 'All yes/no/maybe cells and reasons are intentionally blank. Field notes are discussion prompts, not decisions.'],
  ['Null / missing', 'Fraction of all rows encoded as \\M, \\N or an empty string. Zeros and false are populated values.'],
  ['Empty list / object', 'Fraction of all rows with [] or {}. Separate from null/missing; does not establish absence in the world.'],
  ['Examples', 'Shortened real CSV values, each prefixed with its source ID. Different fields may use different journals.'],
  ['Scopus', 'Predictor? asks about predictors only. Both candidate outcomes and their matching evidence stay outside predictor inputs. Choose the target separately. Unknown is not zero.'],
  ['Topics', 'Both arrays independently keep up to 25 entries and may differ. Keep them unchanged. topic_share uses that topic\'s Works across all primary sources, not a within-journal denominator.'],
];
guide.getRange('A16:F16').values = [['Observed topics hierarchy', 'Distinct IDs', 'Journals with data', 'Minimum per journal', 'Maximum per journal', 'Scope']];
const levels = profile.topic_lists.topics.levels;
guide.getRange('A17:F20').values = ['topic', 'subfield', 'field', 'domain'].map(level => {
  const v = levels[level];
  return [level, v.unique_id_count, v.journals_with_nonempty_level,
    v.per_journal_unique_id_min_including_empty,
    v.per_journal_unique_id_max,
    'IDs observed in the returned topics lists only; not an exhaustive Works classification.'];
});
guide.getRange('A22:B25').values = [
  ['Topic decisions open', 'Hierarchy level; binary presence versus counts; aggregation; missingness; rare categories. No encoding was performed.'],
  ['Version', 'The frozen dataset predates current live documentation. Do not refresh names or classifications silently.'],
  ['Complete task', 'Workbook preparation is complete. Both independent judgments and discussion of disagreements remain outstanding.'],
  ['Value types', 'API attributes use the delivered Source-object type inventory. Other columns use observed CSV token types. Numeric-looking identifiers remain identifiers.'],
];
guide.getRange('A27:B33').values = [
  ['Sources', 'Data provenance and interpretation'],
  ['Input file', path.basename(profile.source.relative_path)],
  ['Input SHA-256', profile.source.compressed_sha256],
  ['Data definitions', 'https://github.com/YannJY02/InvisibleResearch/blob/main/research/openalex-journal-baseline/dual-route-delivery.md'],
  ['Meeting agreement', 'https://github.com/YannJY02/InvisibleResearch/blob/main/meeting-reports/2026-10-16-variable-selection-and-conferences.md'],
  ['OpenAlex Source attributes', 'https://help.openalex.org/data/sources/attributes/ (checked October 16, 2026)'],
  ['OpenAlex topics', 'https://help.openalex.org/data/topics/ (checked October 16, 2026)'],
];
guide.getRange('A4:A33').format.columnWidth = 31;
guide.getRange('B4:B33').format.columnWidth = 53;
guide.getRange('C4:C33').format.columnWidth = 24;
guide.getRange('D4:E33').format.columnWidth = 22;
guide.getRange('F4:F33').format.columnWidth = 60;
guide.getRange('A4:B13').format.wrapText = true;
guide.getRange('A4:B13').format.rowHeight = 57;
guide.getRange('A16:F20').format.wrapText = true;
guide.getRange('A16:F16').format = headerStyle;
guide.getRange('A16:F20').format.rowHeight = 48;
guide.getRange('B17:E20').setNumberFormat('#,##0');
guide.getRange('A22:B25').format.wrapText = true;
guide.getRange('A22:B25').format.rowHeight = 65;
guide.getRange('A27:B33').format.wrapText = true;
guide.getRange('A27:B33').format.rowHeight = 53;
guide.getRange('A27:B27').format = headerStyle;

// Exercise the simple progress formula without retaining test judgments.
sheets[0].getRange('C9:C11').values = [['yes'], ['no'], ['maybe']];
wb.recalculate();
if (sheets[0].getRange('C6').values[0][0] !== 3) throw new Error('Review counter failed');
sheets[0].getRange('C9:D11').clear({ applyTo: 'contents' });
wb.recalculate();
if (sheets[0].getRange('C6').values[0][0] !== 0) throw new Error('Blank review counter failed');
if (JSON.stringify(sheets[0].getRange('A8:K88').values) !==
    JSON.stringify(sheets[1].getRange('A8:K88').values)) throw new Error('Independent templates differ');
await fs.mkdir(outputDir, { recursive: true });
const inspection = await wb.inspect({ kind: 'table', range: 'Jinyi!A8:E12',
  include: 'values,formulas', tableMaxRows: 5, tableMaxCols: 5, maxChars: 1800 });
await fs.writeFile(path.join(pipeline, 'workbook-inspect.ndjson'), inspection.ndjson);
const errors = await wb.inspect({ kind: 'match', searchTerm: '#REF!|#DIV/0!|#VALUE!|#NAME\\?|#NUM!|#SPILL!|#CALC!',
  options: { useRegex: true, maxResults: 30 }, maxChars: 1500 });
await fs.writeFile(path.join(pipeline, 'formula-errors.ndjson'), errors.ndjson);
for (const sheet of [...sheets, guide]) {
  const range = sheet.name === 'Guide' ? 'A1:F25' : 'A1:F13';
  const preview = await wb.render({ sheetName: sheet.name, range, scale: sheet.name === 'Saurabh' ? 1.2 : 1, format: 'png' });
  await fs.writeFile(path.join(pipeline, `${sheet.name.toLowerCase()}-preview.png`),
    new Uint8Array(await preview.arrayBuffer()));
}
for (const [name, range] of [['field-details', 'G8:K14'], ['topics', 'B65:K70']]) {
  const preview = await wb.render({ sheetName: 'Jinyi', range, scale: 1, format: 'png' });
  await fs.writeFile(path.join(pipeline, `${name}-preview.png`),
    new Uint8Array(await preview.arrayBuffer()));
}
const file = path.join(outputDir, 'route-b-variable-selection.xlsx');
await (await SpreadsheetFile.exportXlsx(wb)).save(file);
await fs.writeFile(path.join(pipeline, 'workbook-checks.json'), JSON.stringify({
  source_rows: profile.denominator_rows, source_columns: profile.header.length,
  review_sheets: sheets.map(sheet => sheet.name), identical_templates: true,
  original_column_order: true, judgments_blank: true, reviewer_reason_cells_blank: true,
  progress_formula_test: { three_choices: 3, restored_blank: 0 }, file,
}, null, 2));
console.log(JSON.stringify({ file, columns: rows.length, review_sheets: ['Jinyi', 'Saurabh'] }));
