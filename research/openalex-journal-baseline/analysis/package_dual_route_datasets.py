"""Package independently verified routes without altering acquisition outputs."""
import argparse
import csv
import gzip
from pathlib import Path
import shutil

import collect_source_metadata as base


def read(path):
    return base.loads(path.read_bytes())


def copy_verified(source, target, expected_hash):
    if base.sha256_file(source) != expected_hash:
        raise ValueError("Input artifact hash differs")
    if not target.exists():
        partial = target.with_name(target.name + ".tmp")
        shutil.copyfile(source, partial)
        if base.sha256_file(partial) != expected_hash:
            raise ValueError("Copy hash differs")
        partial.replace(target)
    elif base.sha256_file(target) != expected_hash:
        raise ValueError("Existing artifact differs; it will not be overwritten")


def package(root, scopus):
    files, routes, all_columns = [], {}, {}
    extra = None
    for route, name in (("a", "route-a-bigquery"), ("b", "route-b-api")):
        directory = root / name
        summary = read(directory / "summary.json")
        matched = read(scopus / f"route-{route}-journals-scopus.csv.gz.summary.json")
        if summary["status"] != "complete" or not summary["verification"]["passed"]:
            raise ValueError("Route build is incomplete")
        if not matched["validation"]["all_original_cells_and_order_preserved"] or matched["rows"] != summary["rows"]:
            raise ValueError("Scopus did not preserve the journal cohort")
        inputs = {entry["name"]: entry for entry in summary["files"]}
        if matched["input_sha256"] != inputs["journals.pre-scopus.csv.gz"]["sha256"]:
            raise ValueError("Scopus matched a different intermediate table")
        stem = f"openalex-route-{route}-{'bigquery' if route == 'a' else 'api'}-2026-10-01"
        final, raw = directory / (stem + "-journals.csv.gz"), directory / (stem + "-sources.jsonl.gz")
        copy_verified(Path(matched["output_path"]), final, matched["output_sha256"])
        raw_entry = inputs["sources-with-provenance.jsonl.gz"]
        copy_verified(directory / raw_entry["name"], raw, raw_entry["sha256"])
        with gzip.open(final, "rt", newline="", encoding="utf-8") as stream:
            header = next(csv.reader(stream))
        if len(header) != len(set(header)):
            raise ValueError("Duplicate delivery field")
        scopus_fields = [c for c in header if c.startswith("scopus_")
                         and c not in ("scopus_match_issn_json", "scopus_identifier_policy")]
        if extra is not None and extra != scopus_fields:
            raise ValueError("Scopus schema differs between routes")
        extra, all_columns[route] = scopus_fields, header
        for p, purpose in ((final, "最终一行一期刊 CSV：完整属性、语言分布、Scopus"),
                           (raw, "完整 Source 对象及行身份、历史单元格的 JSONL")):
            files.append({"route": route.upper(), "name": p.name, "relative_path": str(p.relative_to(root)),
                          "purpose": purpose, "bytes": p.stat().st_size, "sha256": base.sha256_file(p)})
        routes[route] = {"rows": summary["rows"], "columns": len(header),
                         "source_fields": summary["source_fields"], "source_field_types": summary["source_field_types"],
                         "identity_counts": summary["source_identity_status_counts"],
                         "language_works": summary["language_works_total"],
                         "unknown_language_works": summary["unknown_language_works"],
                         "scopus_reference_sha256": matched["reference_sha256"],
                         "scopus_membership_counts": matched["membership_counts"],
                         "scopus_active_journal_counts": matched["active_journal_counts"],
                         "csv_encoding": summary["csv_encoding"],
                         "verification": summary["verification"] | matched["validation"]}
    guide = root / "openalex-two-route-field-guide-2026-10-01.md"
    lines = ["# 两套 OpenAlex 期刊数据字段说明", "", "生成日期：" + base.now(), "",
             "A 为固定 BigQuery 209,799 行；B 为本轮独立 API journal 母体。各自是一条期刊记录一行。",
             "CSV.gz 解压后是 UTF-8 CSV；JSONL.gz 每行包含完整 Source 对象与 provenance。", "",
             "## 值与身份", "",
             r"Source／派生字段：\M 未返回，\N JSON null，\S 后接 JSON 字符串用于转义；字符串原样、数值和布尔值为 JSON。",
             "数组与语言分布均是完整 JSON 单元格，导入时关闭默认 NA 猜测。Scopus 未定标签使用空值。",
             r"A 的 historical_ 列保留原 CSV 单元格（SQL NULL 标记仍为 \N），不是新的 API 字段。",
             "route_row_id 唯一识别行；source_id 为母体 ID；resolved_id 为实际返回的当前身份。",
             "issn_candidate_unconfirmed 是补充候选，不是已证实历史合并。共享当前身份的旧行分别保留。", "",
             "## 语言", "",
             "全部可用年份、全部类型，包含 XPAC；按主要发表 Source 归属，按 Work ID 去重。",
             "language_counts_json：小写语言代码及 __unknown__ 的计数；原始代码在取数回执中保留。",
             "language_proportions_json 以全部 Works 包括未知为分母；language_known_proportions_json 仅以已知 Works 为分母。",
             "language_works_count、language_known_works_count、language_unknown_works_count、language_unknown_share 保存相应总数和未知比例。",
             "无 Works 时计数0、占比 null、分布为空对象；Source works_count 另保留，日期与口径不强行等同。", "",
             "## Scopus", "",
             "两套使用同一官方 August 2026 工作簿。scopus_match_issn_json 与 scopus_identifier_policy 保留实际匹配号码及规则。",
             "scopus_membership_in_reference：1=唯一明确名录身份；0=有效号码未在这版收录表找到；空=无有效号码／多身份／身份未知。",
             "scopus_active_journal_in_reference：1=唯一明确 Active Journal；0=名录未匹配或明确非 Journal／Inactive；空=身份或状态未明。",
             "0 不等于从未收录；待收录与候选证据另列。Scopus 语言没有作为 OpenAlex 特征，两列不是已定模型 y。", ""]
    for route in ("a", "b"):
        lines += [f"## Route {route.upper()} 全部列（{len(all_columns[route])}）", "",
                  "| 列名 | 来源／表示 |", "|---|---|"]
        for field in all_columns[route]:
            if field in routes[route]["source_fields"]:
                desc = "完整 API Source；JSON 类型：" + ", ".join(routes[route]["source_field_types"].get(field, []))
            elif field.startswith("historical_"):
                desc = "原始 BigQuery CSV 单元格，保持原编码"
            elif field in extra:
                desc = "固定 Scopus 名录的匹配证据／标签"
            else:
                desc = "行身份、匹配规则或语言派生统计"
            lines.append(f"| {field} | {desc} |")
        lines += [""]
    guide.write_text("\n".join(lines), encoding="utf-8")
    files.append({"route": "both", "name": guide.name, "relative_path": guide.name,
                  "purpose": "全部列、缺失编码、语言分母及 Scopus 定义",
                  "bytes": guide.stat().st_size, "sha256": base.sha256_file(guide)})
    uploaded = []
    for item in files:
        receipt = root / "remote-delivery" / (item["name"] + ".upload.json")
        if receipt.exists():
            evidence = read(receipt)
            if evidence.get("verified") and evidence.get("remote_sha256") == item["sha256"] and evidence.get("remote_bytes") == item["bytes"]:
                uploaded.append({"name": item["name"], "verified_at": evidence["verified_at"], "sha256": item["sha256"]})
    base.save_json(root / "delivery-manifest.json",
                  {"status": "complete", "completed_at": base.now(), "routes": routes, "scopus_columns": extra,
                   "files": files, "remote_delivery": {"status": "partial_before_user_pause", "further_uploads": "pending_user_review",
                                                        "already_verified_files": uploaded}, "contains_credentials": False})
    print(base.dumps({"status": "complete", "routes": {k: {f: v[f] for f in ("rows", "columns")}
                                                       for k, v in routes.items()}, "files": len(files)}).decode())


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--delivery", required=True, type=Path)
    parser.add_argument("--scopus", required=True, type=Path)
    args = parser.parse_args()
    if "artifacts" not in args.delivery.parts:
        parser.error("Use a named artifacts delivery directory")
    package(args.delivery, args.scopus)
