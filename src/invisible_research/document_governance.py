"""Check document locations and local links without modifying repository files."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import posixpath
import re
import subprocess
import sys
from pathlib import Path
from urllib.parse import unquote, urlsplit


RULES_PATH = "docs/governance/document-rules.json"
RENDER_EXTENSIONS = {".html", ".pdf", ".doc", ".docx", ".ppt", ".pptx", ".xls", ".xlsx", ".odt", ".odp", ".ods"}
SCAN_EXCLUSIONS = {"artifacts", "inbox", "libs", "_files", ".quarto", "renv", "node_modules", "env", "environment", ".venv", "venv", ".git"}


def git(root: Path, *args: str) -> bytes:
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True)
    if result.returncode:
        raise ValueError(result.stderr.decode("utf-8", errors="replace").strip())
    return result.stdout


def repository_path(value: object) -> str:
    if (
        not isinstance(value, str)
        or not value
        or value.startswith("/")
        or "\\" in value
        or any(part in {"", ".", ".."} for part in value.split("/"))
    ):
        raise ValueError(f"expected a repository-relative file path, got {value!r}")
    return value


class Snapshot:
    """Read either the worktree or the Git index, never a mixture of the two."""

    def __init__(self, root: Path, staged: bool):
        self.root = root
        self.staged = staged
        self.symlinks: set[str] = set()
        if staged:
            self.paths: set[str] = set()
            for entry in git(root, "ls-files", "--stage", "-z").split(b"\0"):
                if not entry:
                    continue
                metadata, raw_path = entry.split(b"\t", 1)
                mode, _, stage = metadata.split()
                path = os.fsdecode(raw_path)
                if stage != b"0":
                    raise ValueError(f"{path}: resolve the merge conflict before checking the index")
                self.paths.add(path)
                if mode == b"120000":
                    self.symlinks.add(path)
        else:
            self.paths = {
                os.fsdecode(path)
                for path in git(root, "ls-files", "-z", "--cached", "--others", "--exclude-standard").split(b"\0")
                if path
            }
            # git ls-files also reports tracked files deleted from the worktree.
            self.paths = {path for path in self.paths if os.path.lexists(root / path)}
        self.directories = {"."}
        for path in self.paths:
            self.directories.update(str(parent) for parent in Path(path).parents)

    def read(self, path: str) -> bytes:
        if self.staged:
            if path not in self.paths:
                raise ValueError(f"{path}: missing from the index")
            if path in self.symlinks:
                raise ValueError(f"{path}: governed documents must be regular files, not symbolic links")
            return git(self.root, "show", f":{path}")
        candidate = self.root / path
        if candidate.is_symlink():
            raise ValueError(f"{path}: governed documents must be regular files, not symbolic links")
        if not candidate.resolve().is_relative_to(self.root):
            raise ValueError(f"{path}: symbolic link points outside the repository")
        return candidate.read_bytes()

    def target_exists(self, path: str) -> bool:
        if not self.staged:
            candidate = (self.root / path).resolve()
            return candidate.is_relative_to(self.root) and candidate.exists()
        # Resolve symlinks using index bytes, including links in parent directories.
        for _ in range(40):
            components = path.split("/")
            link = next(("/".join(components[:n]) for n in range(1, len(components) + 1)
                         if "/".join(components[:n]) in self.symlinks), None)
            if link is None:
                return path in self.paths or path in self.directories
            destination = os.fsdecode(git(self.root, "show", f":{link}"))
            if destination.startswith("/"):
                return False
            suffix = path[len(link):].lstrip("/")
            path = posixpath.normpath(posixpath.join(posixpath.dirname(link), destination, suffix))
            if path == ".." or path.startswith("../"):
                return False
        return False


def load_rules(snapshot: Snapshot) -> dict:
    try:
        rules = json.loads(snapshot.read(RULES_PATH))
        if not isinstance(rules, dict):
            raise ValueError("rules must be an object")
        expected = {"document_extensions", "path_rules", "required_files", "link_exemptions", "protected_files"}
        if set(rules) != expected:
            raise ValueError(f"rules must contain exactly {sorted(expected)}")
        for key in expected:
            if not isinstance(rules[key], list):
                raise ValueError(f"{key} must be a list")
        if not rules["document_extensions"] or not all(
            isinstance(extension, str) and re.fullmatch(r"\.[a-z0-9]+", extension)
            for extension in rules["document_extensions"]
        ):
            raise ValueError("document_extensions must contain lowercase file extensions")
        if not rules["path_rules"]:
            raise ValueError("path_rules must not be empty")
        for rule in rules["path_rules"]:
            if not isinstance(rule, dict) or set(rule) != {"pattern", "description"}:
                raise ValueError("each path rule needs pattern and description")
            if not all(isinstance(value, str) and value.strip() for value in rule.values()):
                raise ValueError("path rule pattern and description must be nonempty strings")
            re.compile(rule["pattern"])
        for path in rules["required_files"]:
            repository_path(path)
        exemptions = set()
        for exemption in rules["link_exemptions"]:
            if not isinstance(exemption, dict) or set(exemption) != {"source", "target", "reason"}:
                raise ValueError("each link exemption needs source, target, and reason")
            repository_path(exemption["source"])
            if not all(isinstance(value, str) and value.strip() for value in exemption.values()):
                raise ValueError("link exemption values must be nonempty strings")
            key = exemption["source"], exemption["target"]
            if key in exemptions:
                raise ValueError(f"duplicate link exemption: {key}")
            exemptions.add(key)
        protected = set()
        for record in rules["protected_files"]:
            if not isinstance(record, dict) or set(record) != {"path", "sha256", "reason"}:
                raise ValueError("each protected file needs path, sha256, and reason")
            repository_path(record["path"])
            if not isinstance(record["sha256"], str) or not re.fullmatch(r"[0-9a-f]{64}", record["sha256"]):
                raise ValueError("protected file sha256 must be 64 lowercase hexadecimal characters")
            if not isinstance(record["reason"], str) or not record["reason"].strip():
                raise ValueError("protected file reason must be a nonempty string")
            if record["path"] in protected:
                raise ValueError(f"duplicate protected file: {record['path']}")
            protected.add(record["path"])
        return rules
    except (OSError, ValueError, re.error) as error:
        raise ValueError(f"{RULES_PATH}: invalid configuration: {error}") from error


def prose_only(markdown: str) -> str:
    """Mask comments, fenced code, and inline code while retaining line numbers."""
    def blank(match: re.Match) -> str:
        return re.sub(r"[^\n]", " ", match.group())

    markdown = re.sub(r"<!--.*?-->", blank, markdown, flags=re.S)
    lines = markdown.splitlines(keepends=True)
    fence = None
    for number, line in enumerate(lines):
        marker = re.match(r"^ {0,3}(`{3,}|~{3,})(.*)$", line)
        if fence:
            lines[number] = re.sub(r"[^\n]", " ", line)
            if marker and marker[1][0] == fence[0] and len(marker[1]) >= len(fence) and not marker[2].strip():
                fence = None
        elif marker:
            fence = marker[1]
            lines[number] = re.sub(r"[^\n]", " ", line)
    return re.sub(r"(`+)(?!`)(.+?)(?<!`)\1(?!`)", blank, "".join(lines), flags=re.S)


def destination(text: str) -> str | None:
    """Read a Markdown destination, preserving its literal spelling for exemptions."""
    text = text.lstrip()
    if text.startswith("<"):
        end = re.search(r"(?<!\\)>", text)
        return text[1:end.start()] if end else None
    depth = 0
    for offset, character in enumerate(text):
        if offset and text[offset - 1] == "\\":
            continue
        if character.isspace() or (character == ")" and depth == 0):
            return text[:offset] or None
        if character == "(":
            depth += 1
        elif character == ")":
            depth -= 1
    return text or None


def markdown_links(markdown: str) -> tuple[list[tuple[int, str]], list[tuple[int, str]]]:
    text = prose_only(markdown)
    links = []
    references = set()
    normalize = lambda label: " ".join(label.split()).casefold()
    for match in re.finditer(r"^ {0,3}\[([^]\n]+)\]:[ \t]*(?:\n[ \t]+)?([^\n]+)", text, re.M):
        references.add(normalize(match[1]))
        target = destination(match[2])
        if target:
            links.append((text.count("\n", 0, match.start()) + 1, target))
    for match in re.finditer(r"(?<!\\)\]\(\s*", text):
        target = destination(text[match.end():])
        if target:
            links.append((text.count("\n", 0, match.start()) + 1, target))
    missing = []
    for match in re.finditer(r"(?<!\\)\[([^]\n]+)\][ \t]*\[([^]\n]*)\]", text):
        label = match[2] or match[1]
        if normalize(label) not in references:
            missing.append((text.count("\n", 0, match.start()) + 1, label))
    return links, missing


def check_links(snapshot: Snapshot, source: str, markdown: str, exemptions: set[tuple[str, str]]) -> list[str]:
    links, missing = markdown_links(markdown)
    problems = [f"{source}:{line}: undefined link reference [{label}]" for line, label in missing]
    for line, literal in links:
        if (source, literal) in exemptions:
            continue
        target = re.sub(r"\\([!\"#$%&'()*+,\-./:;<=>?@\[\\\]^_`{|}~])", r"\1", literal)
        # Metavariables in documentation templates are not concrete file links.
        if re.search(r"[{}<>]", unquote(target)):
            continue
        try:
            url = urlsplit(target)
        except ValueError:
            problems.append(f"{source}:{line}: malformed link destination {literal!r}")
            continue
        if url.scheme or url.netloc or not url.path:
            continue
        decoded = unquote(url.path)
        path = posixpath.normpath(decoded.lstrip("/") if decoded.startswith("/")
                                 else posixpath.join(posixpath.dirname(source), decoded))
        if path == ".." or path.startswith("../"):
            problems.append(f"{source}:{line}: local link escapes the repository: {literal}")
        elif not snapshot.target_exists(path):
            problems.append(f"{source}:{line}: broken local link: {literal} (resolved: {path})")
    return problems


def misplaced_outputs(snapshot: Snapshot) -> list[str]:
    """Find render products and deployment state in the source trees that commonly leak them."""
    found = []
    for owner_root, source_dir in (("research", "analysis"), ("papers", "manuscript")):
        parent = snapshot.root / owner_root
        if not parent.is_dir() or parent.is_symlink():
            continue
        for owner in sorted(parent.iterdir()):
            source = owner / source_dir
            if owner.is_symlink() or source.is_symlink() or not source.is_dir():
                continue
            for current, directories, files in os.walk(source, followlinks=False):
                if "rsconnect" in directories:
                    found.append((Path(current) / "rsconnect").relative_to(snapshot.root).as_posix() + "/")
                directories[:] = [name for name in directories
                                  if name not in SCAN_EXCLUSIONS and name != "rsconnect" and not name.endswith("_files")
                                  and not (Path(current) / name).is_symlink()]
                for name in files:
                    if Path(name).suffix.lower() not in RENDER_EXTENSIONS:
                        continue
                    path = (Path(current) / name).relative_to(snapshot.root).as_posix()
                    if path not in snapshot.paths:
                        found.append(path)
    return sorted(found)


def check(root: Path, staged: bool = False) -> list[str]:
    root = root.resolve()
    snapshot = Snapshot(root, staged)
    rules = load_rules(snapshot)
    patterns = [re.compile(rule["pattern"]) for rule in rules["path_rules"]]
    extensions = set(rules["document_extensions"])
    exemptions = {(item["source"], item["target"]) for item in rules["link_exemptions"]}
    problems = []
    for path in sorted(snapshot.paths):
        if Path(path).suffix.lower() not in extensions:
            continue
        # JSON fixtures and application configuration are data/code inputs.
        # Only document and provenance records belong to this governance check.
        if Path(path).suffix.lower() == ".json" and not (
            path.startswith(("docs/", "data/artifact-versions/", "data/component-manifests/"))
            or re.match(r"papers/[^/]+/(?:governance|requirements)/", path)
        ):
            continue
        if not any(pattern.fullmatch(path) for pattern in patterns):
            problems.append(f"{path}: document placement or name is not allowed by {RULES_PATH}")
        if Path(path).suffix.lower() in {".md", ".qmd", ".rmd"}:
            try:
                problems.extend(check_links(snapshot, path, snapshot.read(path).decode("utf-8"), exemptions))
            except (OSError, ValueError) as error:
                problems.append(f"{path}: cannot check Markdown: {error}")
    for path in rules["required_files"]:
        if path not in snapshot.paths:
            problems.append(f"{path}: required file is missing")
    for record in rules["protected_files"]:
        path = record["path"]
        try:
            digest = hashlib.sha256(snapshot.read(path)).hexdigest()
            if digest != record["sha256"]:
                problems.append(f"{path}: protected file content changed ({record['reason']})")
        except (OSError, ValueError) as error:
            problems.append(f"{path}: cannot verify protected file: {error}")
    if not staged:
        for path in misplaced_outputs(snapshot):
            kind = "deployment metadata" if path.endswith("/rsconnect/") else "ignored generated render"
            problems.append(f"{path}: {kind} is misplaced; move it into the owner's artifacts/<pipeline>/ directory")
    return problems


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    command = commands.add_parser("check", help="check document rules and local Markdown links")
    command.add_argument("--staged", action="store_true", help="check the actual Git index, including its rules file")
    command.add_argument("--root", type=Path, help="repository root (defaults to the current Git repository)")
    args = parser.parse_args(argv)
    try:
        root = args.root or Path(os.fsdecode(git(Path.cwd(), "rev-parse", "--show-toplevel")).strip())
        problems = check(root, staged=args.staged)
    except (OSError, ValueError) as error:
        print(f"Document governance could not run: {error}", file=sys.stderr)
        return 1
    if problems:
        print("Document governance failed:", file=sys.stderr)
        for problem in problems:
            print(f"- {problem}", file=sys.stderr)
        return 1
    print(f"Document governance passed ({'Git index' if args.staged else 'working tree'}).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
