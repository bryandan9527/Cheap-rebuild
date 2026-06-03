#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CORPUS_SOURCE_DIR = ROOT / "corpus" / "source"
CORPUS_DERIVED_DIR = ROOT / "corpus" / "derived"
MERGED_PATH = CORPUS_DERIVED_DIR / "cheap_corpus_merged.md"
RECORDS_PATH = CORPUS_DERIVED_DIR / "cheap_corpus_records.jsonl"
TAXONOMY_PATH = CORPUS_DERIVED_DIR / "cheap_taxonomy.json"
SUMMARY_PATH = CORPUS_DERIVED_DIR / "cheap_corpus_summary.json"
ENTRY_SPLIT_RE = re.compile(r"^(\d{4})\s*$", flags=re.M)

REQUIRED_FIELDS = [
    "entry_id",
    "source_path",
    "clean_text",
    "char_count",
    "topic_cluster_id",
    "reasoning_pattern",
    "primary_route",
    "topic_tags",
    "angle_statement",
    "argument_moves",
    "cheap_push_moves",
    "required_evidence_types",
    "hook_type",
    "claim_target",
    "evidence_shape",
    "opening_move",
    "rhythm_pattern",
    "closing_style",
]

INLINE_STRIKETHROUGH_RE = re.compile(r"~~[^~]+~~")
HTML_STRIKETHROUGH_RE = re.compile(r"<(?:del|s)>.*?</(?:del|s)>", flags=re.I)
MARKDOWN_HEADING_RE = re.compile(r"^#+")
BRACKET_HEADING_RE = re.compile(r"^【[^】]+】$")
FULLWIDTH_HASH_HEADING_RE = re.compile(r"^＃")
CHEAP_PUSH_SET = {"反例對照", "數字換算", "荒謬類比", "邏輯反打", "風險收益比較"}


def load_records() -> list[dict]:
    return [json.loads(line) for line in RECORDS_PATH.read_text().splitlines() if line.strip()]


def load_taxonomy() -> dict:
    return json.loads(TAXONOMY_PATH.read_text())


def load_summary() -> dict:
    return json.loads(SUMMARY_PATH.read_text())


def parse_merged_ids() -> list[str]:
    parts = ENTRY_SPLIT_RE.split(MERGED_PATH.read_text())
    return [parts[index] for index in range(1, len(parts), 2)]


def entry_id_from_source(path: Path) -> str:
    return f"{int(path.stem[4:]):04d}"


def scan_corpus_format() -> dict[str, list[tuple[str, int, str]]]:
    invalid_markdown: list[tuple[str, int, str]] = []
    invalid_html: list[tuple[str, int, str]] = []
    invalid_headings: list[tuple[str, int, str]] = []

    for source_path in sorted(CORPUS_SOURCE_DIR.glob("clip*.md"), key=lambda item: int(item.stem[4:])):
        for line_number, line in enumerate(source_path.read_text().splitlines(), start=1):
            if INLINE_STRIKETHROUGH_RE.search(line):
                invalid_markdown.append((source_path.name, line_number, line.strip()))
            if HTML_STRIKETHROUGH_RE.search(line):
                invalid_html.append((source_path.name, line_number, line.strip()))
            if (
                MARKDOWN_HEADING_RE.search(line)
                or FULLWIDTH_HASH_HEADING_RE.search(line)
                or BRACKET_HEADING_RE.search(line.strip())
            ):
                invalid_headings.append((source_path.name, line_number, line.strip()))

    return {
        "markdown": invalid_markdown,
        "html": invalid_html,
        "headings": invalid_headings,
    }


def main() -> None:
    clip_files = sorted(CORPUS_SOURCE_DIR.glob("clip*.md"), key=lambda item: int(item.stem[4:]))
    rows = load_records()
    taxonomy = load_taxonomy()
    summary = load_summary()
    merged_ids = parse_merged_ids()
    corpus_format = scan_corpus_format()
    high_confidence = [row for row in rows if not row["low_confidence_flag"]]

    issues: list[str] = []
    missing_fields: list[tuple[str, str]] = []
    empty_topics: list[str] = []
    empty_push_moves: list[str] = []

    if len(rows) != len(clip_files):
        issues.append(f"record count mismatch: {len(rows)} != {len(clip_files)}")
    if len(merged_ids) != len(clip_files):
        issues.append(f"merged count mismatch: {len(merged_ids)} != {len(clip_files)}")
    if summary.get("entry_count") != len(clip_files):
        issues.append(f"summary entry_count mismatch: {summary.get('entry_count')} != {len(clip_files)}")
    if len(set(merged_ids)) != len(merged_ids):
        issues.append("merged corpus has duplicate entry ids")

    reasoning_clusters: dict[str, set[str]] = defaultdict(set)
    route_topics: dict[str, set[str]] = defaultdict(set)

    for row in high_confidence:
        for field in REQUIRED_FIELDS:
            value = row.get(field)
            if value in (None, "", []):
                missing_fields.append((row.get("entry_id", "unknown"), field))
        if not row.get("topic_tags"):
            empty_topics.append(row["entry_id"])
        if not row.get("cheap_push_moves"):
            empty_push_moves.append(row["entry_id"])

        source_path = ROOT / row["source_path"]
        if not source_path.exists():
            issues.append(f"{row['entry_id']}: missing source file {row['source_path']}")
        elif entry_id_from_source(source_path) != row["entry_id"]:
            issues.append(f"{row['entry_id']}: source_path does not match entry_id")
        if len(row["clean_text"]) != row["char_count"]:
            issues.append(f"{row['entry_id']}: char_count mismatch")

        reasoning_clusters[row["reasoning_pattern"]].add(row["topic_cluster_id"])
        for topic_tag in row["topic_tags"]:
            route_topics[row["primary_route"]].add(topic_tag)

    weak_patterns = {
        pattern: len(clusters)
        for pattern, clusters in reasoning_clusters.items()
        if len(clusters) < 2
    }

    weak_routes = []
    for route_name, route_def in taxonomy["routes"].items():
        if not set(route_def["must_include_moves"]).intersection(CHEAP_PUSH_SET):
            weak_routes.append(route_name)

    routes_with_no_topic_spread = {
        route: len(topics)
        for route, topics in route_topics.items()
        if len(topics) < 1
    }

    print("clip_files:", len(clip_files))
    print("records:", len(rows))
    print("merged_entries:", len(merged_ids))
    print("summary_entry_count:", summary.get("entry_count"))
    print("missing_fields:", len(missing_fields))
    print("empty_topics:", len(empty_topics))
    print("empty_cheap_push_moves:", len(empty_push_moves))
    print("corpus_inline_strikethrough:", len(corpus_format["markdown"]))
    print("corpus_html_strikethrough:", len(corpus_format["html"]))
    print("corpus_markdown_headings:", len(corpus_format["headings"]))
    print("reasoning_by_cluster:")
    cluster_counts = Counter({pattern: len(clusters) for pattern, clusters in reasoning_clusters.items()})
    for pattern, count in cluster_counts.items():
        print(f"- {pattern}: {count}")
    print("weak_patterns:", json.dumps(weak_patterns, ensure_ascii=False))
    print("routes_without_cheap_push_move:", len(weak_routes))
    if weak_routes:
        print("weak_routes:", weak_routes[:10])
    print("routes_with_no_topic_spread:", json.dumps(routes_with_no_topic_spread, ensure_ascii=False))

    if (
        issues
        or missing_fields
        or empty_topics
        or empty_push_moves
        or weak_patterns
        or weak_routes
        or corpus_format["markdown"]
        or corpus_format["html"]
        or corpus_format["headings"]
    ):
        if issues:
            print("issues:")
            for issue in issues[:50]:
                print("-", issue)
        raise SystemExit(1)

    print("validation: ok")


if __name__ == "__main__":
    main()
