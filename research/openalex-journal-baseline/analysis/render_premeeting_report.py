"""Render the meeting report and assemble a local report/data bundle.

Requires Quarto/Pandoc and the completed artifacts referenced by the report.
No source acquisition, model run, upload, or publication is performed.
"""

import hashlib
import json
from pathlib import Path
import re
import shutil
import subprocess
import zipfile


ROOT = Path(__file__).resolve().parents[3]
OWNER = ROOT / "research/openalex-journal-baseline"
OUT = OWNER / "artifacts/premeeting-report"
GITHUB = "https://github.com/YannJY02/InvisibleResearch/blob/main/"
STYLE = """
html { color: #1e293b; background: #f4f6f8; scroll-behavior: smooth; }
body { margin: 0 auto; max-width: 960px; padding: 44px 36px 90px;
  font: 16px/1.8 -apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC",sans-serif;
  background: white; }
h1,h2,h3 { color: #123c55; line-height: 1.35; scroll-margin-top: 24px; }
h1 { font-size: 30px; border-bottom: 4px solid #167d9a; padding-bottom: 20px; }
h2 { margin-top: 48px; font-size: 24px; }
h3 { margin-top: 30px; font-size: 20px; }
a { color: #006b89; text-underline-offset: 3px; overflow-wrap: anywhere; }
table { border-collapse: collapse; width: 100%; font-size: 14px; margin: 24px 0; }
th,td { border: 1px solid #d4e0e6; padding: 10px 12px; text-align: left;
  vertical-align: top; overflow-wrap: anywhere; }
th { background: #edf5f8; font-weight: 650; }
tbody tr:nth-child(even) { background: #f9fbfc; }
code { font-size: .87em; overflow-wrap: anywhere; }
pre { white-space: pre-wrap; background: #f1f5f9; border: 1px solid #d4e0e6;
  border-radius: 8px; padding: 18px; line-height: 1.6; }
nav { padding: 20px 28px; background: #edf5f8; border-radius: 8px; }
nav ul { padding-left: 22px; } nav > ul { margin: 0; }
@media(max-width: 680px) { body { padding: 24px 16px; font-size: 15px; }
  h1 { font-size: 25px; } table { font-size: 12px; } th,td { padding: 7px; } }
@media print { html,body { background: white; } body { max-width: none; padding: 0; }
  h2,h3 { break-after: avoid; } tr,pre { break-inside: avoid; } }
"""


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    copies = {}
    for name in ("sources.jsonl.gz", "journals.csv.gz", "manifest.json", "readback-verification.json"):
        copies[OWNER / "artifacts/bigquery-tabledata-2025-08" / name] = "data/" + name
    for name in ("openalex-journals-scopus-candidates.csv.gz", "summary.json", "findings.md"):
        dest = "data/" + name if name.endswith("csv.gz") else "evidence/scopus-" + name
        copies[OWNER / "artifacts/scopus-2026-08" / name] = dest
    cr = ROOT / "research/ojs-journal-metadata/artifacts/premeeting-crossref-audit"
    for name in ("summary.json", "crossref-only-examples.csv", "field-audit.csv",
                 "empty-value-examples.csv", "input-provenance.csv"):
        copies[cr / name] = "evidence/crossref/" + name
    for source, relative in copies.items():
        target = OUT / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)

    (OUT / "style.css").write_text(STYLE)
    for name in ("premeeting-report", "input-contract"):
        source = OWNER / (name + ".md")

        def relink(match):
            label, target = match.groups()
            if re.match(r"(?:[a-z]+:|#)", target):
                return match.group(0)
            resolved = (source.parent / target).resolve()
            if resolved in copies:
                url = copies[resolved]
            elif resolved == OWNER / "input-contract.md":
                url = "input-contract.html"
            else:
                url = GITHUB + resolved.relative_to(ROOT).as_posix()
            return f"[{label}]({url})"

        # Git-tracked prose names ignored local artifacts without broken links.
        # The portable HTML links those named artifacts to bundled files.
        annotated = re.sub(r"\*\*([^*]+)\*\*（本地产物：`([^`]+)`）",
                           r"[\1](\2)", source.read_text())
        text = re.sub(r"\[([^\]\n]+)\]\(([^)\s]+)\)", relink, annotated)
        md = OUT / (name + ".md")
        md.write_text(text)
        subprocess.run([
            "quarto", "pandoc", str(md), "--standalone", "--toc", "--toc-depth=2",
            "--embed-resources", "--css", str(OUT / "style.css"),
            "--metadata", "lang=zh-CN", "--metadata", "pagetitle=会前研究准备报告",
            "--output", str(OUT / (name + ".html")),
        ], check=True, cwd=ROOT)

    files = sorted(p for p in OUT.rglob("*") if p.is_file()
                   and p.name not in {"bundle-manifest.json", "premeeting-report-and-data.zip"})
    manifest = {str(p.relative_to(OUT)): {"bytes": p.stat().st_size,
                "sha256": hashlib.sha256(p.read_bytes()).hexdigest()} for p in files}
    index = OUT / "bundle-manifest.json"
    index.write_text(json.dumps(manifest, ensure_ascii=False, indent=2) + "\n")
    bundle = OUT / "premeeting-report-and-data.zip"
    with zipfile.ZipFile(bundle, "w", compression=zipfile.ZIP_DEFLATED) as z:
        for p in files + [index]:
            z.write(p, p.relative_to(OUT))
    print(json.dumps({"html": str(OUT / "premeeting-report.html"), "bundle": str(bundle),
                      "bundle_bytes": bundle.stat().st_size,
                      "bundle_sha256": hashlib.sha256(bundle.read_bytes()).hexdigest()}, indent=2))


if __name__ == "__main__":
    main()
