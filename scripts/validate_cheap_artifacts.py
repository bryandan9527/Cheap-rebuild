#!/usr/bin/env python3
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ARTIFACTS_DIR = ROOT / "artifacts"
CORPUS_PATH = ROOT / "corpus" / "cheap_corpus.md"
RECORDS_PATH = ARTIFACTS_DIR / "cheap_corpus_records.jsonl"
TAXONOMY_PATH = ARTIFACTS_DIR / "cheap_taxonomy.json"

REQUIRED_FIELDS = [
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


def load_records() -> list[dict]:
    return [json.loads(line) for line in RECORDS_PATH.read_text().splitlines() if line.strip()]


def load_taxonomy() -> dict:
    return json.loads(TAXONOMY_PATH.read_text())


def scan_corpus_format() -> dict[str, list[tuple[int, str]]]:
    invalid_markdown: list[tuple[int, str]] = []
    invalid_html: list[tuple[int, str]] = []
    invalid_headings: list[tuple[int, str]] = []

    for line_number, line in enumerate(CORPUS_PATH.read_text().splitlines(), start=1):
        if INLINE_STRIKETHROUGH_RE.search(line):
            invalid_markdown.append((line_number, line.strip()))
        if HTML_STRIKETHROUGH_RE.search(line):
            invalid_html.append((line_number, line.strip()))
        if (
            MARKDOWN_HEADING_RE.search(line)
            or FULLWIDTH_HASH_HEADING_RE.search(line)
            or BRACKET_HEADING_RE.search(line.strip())
        ):
            invalid_headings.append((line_number, line.strip()))

    return {
        "markdown": invalid_markdown,
        "html": invalid_html,
        "headings": invalid_headings,
    }


def main() -> None:
    rows = load_records()
    taxonomy = load_taxonomy()
    corpus_format = scan_corpus_format()
    high_confidence = [row for row in rows if not row["low_confidence_flag"]]

    missing_fields: list[tuple[str, str]] = []
    empty_topics: list[str] = []
    empty_push_moves: list[str] = []

    for row in high_confidence:
        for field in REQUIRED_FIELDS:
            value = row.get(field)
            if value in (None, "", []):
                missing_fields.append((row["entry_id"], field))
        if not row.get("topic_tags"):
            empty_topics.append(row["entry_id"])
        if not row.get("cheap_push_moves"):
            empty_push_moves.append(row["entry_id"])

    reasoning_clusters: dict[str, set[str]] = defaultdict(set)
    route_topics: dict[str, set[str]] = defaultdict(set)
    for row in high_confidence:
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
        if not set(route_def["must_include_moves"]).intersection(set().union(*[set([m]) for m in ["反例對照", "數字換算", "荒謬類比", "邏輯反打", "風險收益比較"]])):
            weak_routes.append(route_name)

    routes_with_no_topic_spread = {
        route: len(topics)
        for route, topics in route_topics.items()
        if len(topics) < 1
    }

    print("records:", len(rows))
    print("high_confidence:", len(high_confidence))
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
        missing_fields
        or empty_topics
        or empty_push_moves
        or weak_patterns
        or weak_routes
        or corpus_format["markdown"]
        or corpus_format["html"]
        or corpus_format["headings"]
    ):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
