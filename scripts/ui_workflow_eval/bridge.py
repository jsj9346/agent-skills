#!/usr/bin/env python3
"""Evaluation-only render bridge contract validator and coordinator."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import secrets
import shutil
import string
import subprocess
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urlparse


HASH_RE = re.compile(r"^[0-9a-f]{64}$")
ALLOWED_SKILLS = {"design-ui", "review-ui"}
ALLOWED_MODES = {"maker-qa", "audit", "repair-before", "repair-after", "general-audit"}
ALLOWED_BLOCKERS = {"sandbox-browser-startup", "sandbox-loopback-bind"}
ALLOWED_ACTIONS = {"goto", "click", "fill", "press", "waitForVisible", "screenshot"}
BLOCKER_RE = re.compile(r"sandbox|operation not permitted|permission denied|bind", re.I)
SECRET_RE = re.compile(
    rb"(?:authorization:\s*(?:basic|bearer)\s+[A-Za-z0-9._-]{12,}|"
    rb"api[_-]?key\s*[:=]\s*[A-Za-z0-9._-]{12,}|credential-sentinel-[A-Za-z0-9_-]+)",
    re.I,
)
FORBIDDEN_ARCHIVE_NAMES = {"auth.json", "id_rsa", "id_rsa.pub"}
SNAPSHOT_KEYS = (
    "fixture_manifest_sha256",
    "product_manifest_sha256",
    "design_authority_manifest_sha256",
    "ui_spec_manifest_sha256",
    "plugin_inventory_sha256",
)
SOURCE_KEYS = {
    "fixture_manifest_sha256": "fixture",
    "product_manifest_sha256": "product",
    "design_authority_manifest_sha256": "design_authority",
    "ui_spec_manifest_sha256": "ui_spec",
    "plugin_inventory_sha256": "plugin_inventory",
}


class ContractError(ValueError):
    pass


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode()


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def manifest_hash(path: Path) -> str:
    resolved = path.resolve(strict=True)
    if resolved.is_symlink():
        raise ContractError(f"symlink source is not allowed: {path}")
    if resolved.is_file():
        return sha256_file(resolved)
    if not resolved.is_dir():
        raise ContractError(f"manifest source is not a file or directory: {path}")
    digest = hashlib.sha256()
    for item in sorted(resolved.rglob("*"), key=lambda candidate: candidate.relative_to(resolved).as_posix()):
        if item.is_symlink():
            raise ContractError(f"symlink inside manifest is not allowed: {item}")
        if item.is_file():
            relative = item.relative_to(resolved).as_posix().encode()
            digest.update(relative + b"\0" + sha256_file(item).encode() + b"\n")
    return digest.hexdigest()


def is_within(path: Path, root: Path) -> bool:
    try:
        path.resolve(strict=False).relative_to(root.resolve(strict=True))
        return True
    except (ValueError, FileNotFoundError):
        return False


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ContractError(message)


def require_hash(value: Any, label: str) -> str:
    require(isinstance(value, str) and bool(HASH_RE.fullmatch(value)), f"invalid {label}")
    return value


def load_json(path: str | Path) -> dict[str, Any]:
    with Path(path).open(encoding="utf-8") as handle:
        value = json.load(handle)
    require(isinstance(value, dict), f"JSON root must be an object: {path}")
    return value


def dump_json(value: Any, output: str | None = None) -> None:
    rendered = json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    if output:
        destination = Path(output)
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_text(rendered, encoding="utf-8")
    else:
        sys.stdout.write(rendered)


def request_hash(pending: dict[str, Any]) -> str:
    return sha256_bytes(canonical_bytes(pending))


def validate_snapshot_shape(snapshot: dict[str, Any]) -> None:
    require(isinstance(snapshot.get("case_realpath"), str), "snapshot.case_realpath is required")
    for key in SNAPSHOT_KEYS:
        require_hash(snapshot.get(key), f"snapshot.{key}")


def compute_current_snapshot(envelope: dict[str, Any]) -> dict[str, Any]:
    context = envelope["capture_context"]
    sources = context["snapshot_sources"]
    current = {"case_realpath": str(Path(envelope["pending"]["snapshot"]["case_realpath"]).resolve(strict=True))}
    for snapshot_key, source_key in SOURCE_KEYS.items():
        require(source_key in sources, f"snapshot source missing: {source_key}")
        current[snapshot_key] = manifest_hash(Path(sources[source_key]))
    return current


def validate_route_or_file(value: str, case_root: Path) -> None:
    parsed = urlparse(value)
    if parsed.scheme == "file":
        require(is_within(Path(parsed.path), case_root), "file URL escapes case root")
        return
    if parsed.scheme in {"http", "https"}:
        require(parsed.scheme == "http", "https is not allowed")
        require(parsed.hostname in {"127.0.0.1", "localhost", "::1"}, "network target is not loopback")
        return
    candidate = Path(value)
    require(candidate.is_absolute(), "route_or_file must be an absolute file URL/path or loopback URL")
    require(is_within(candidate, case_root), "path escapes case root")


def validate_matrix(matrix: Any, case_root: Path) -> list[dict[str, Any]]:
    require(isinstance(matrix, list) and matrix, "scenario matrix must be non-empty")
    require(len(matrix) <= 24, "scenario matrix exceeds 24 entries")
    seen: set[str] = set()
    for scenario in matrix:
        require(isinstance(scenario, dict), "scenario must be an object")
        scenario_id = scenario.get("scenario_id")
        require(isinstance(scenario_id, str) and 1 <= len(scenario_id) <= 80, "invalid scenario_id")
        require(scenario_id not in seen, "scenario_id must be unique")
        seen.add(scenario_id)
        route = scenario.get("route_or_file")
        require(isinstance(route, str), "route_or_file is required")
        validate_route_or_file(route, case_root)
        viewport = scenario.get("viewport")
        require(isinstance(viewport, dict), "viewport is required")
        width, height = viewport.get("width"), viewport.get("height")
        require(isinstance(width, int) and 240 <= width <= 3840, "invalid viewport width")
        require(isinstance(height, int) and 240 <= height <= 3840, "invalid viewport height")
        require(isinstance(scenario.get("state"), str) and scenario["state"], "state is required")
        actions = scenario.get("actions")
        require(isinstance(actions, list) and actions, "actions must be non-empty")
        require(len(actions) <= 32, "too many actions")
        for action in actions:
            require(isinstance(action, dict), "action must be an object")
            kind = action.get("action")
            require(kind in ALLOWED_ACTIONS, f"action is not allowed: {kind}")
            require("script" not in action and "javascript" not in action and "shell" not in action,
                    "case-authored script is not allowed")
            for field in ("selector", "value", "key"):
                if field in action:
                    require(isinstance(action[field], str) and len(action[field]) <= 500, f"invalid action {field}")
            if kind == "fill":
                require(action.get("fixture_data") is True, "fill requires non-secret fixture_data")
                value = action.get("value", "")
                require(not re.search(r"credential|password|secret|token|api[_-]?key", value, re.I),
                        "credential-like fill value is not allowed")
            timeout = action.get("timeout_ms", 5000)
            require(isinstance(timeout, int) and 0 < timeout <= 15000, "invalid action timeout")
    return matrix


def validate_request(envelope: dict[str, Any], *, check_current: bool = True) -> dict[str, Any]:
    pending = envelope.get("pending")
    context = envelope.get("capture_context")
    require(isinstance(pending, dict), "pending is required")
    require(isinstance(context, dict), "capture_context is required")
    require(envelope.get("request_sha256") == request_hash(pending), "request_sha256 mismatch")
    require(isinstance(pending.get("case_id"), str) and pending["case_id"], "case_id is required")
    require(isinstance(pending.get("producer_call_id"), str) and pending["producer_call_id"],
            "producer_call_id is required")
    require(pending.get("skill") in ALLOWED_SKILLS, "unknown skill")
    require(pending.get("mode") in ALLOWED_MODES, "unknown mode")
    require(pending.get("blocker_class") in ALLOWED_BLOCKERS, "blocker class is not bridge-eligible")
    blocker = Path(pending.get("blocker_evidence_path", ""))
    require(blocker.is_file() and blocker.stat().st_size > 0, "blocker evidence is missing")
    require(BLOCKER_RE.search(blocker.read_text(encoding="utf-8", errors="replace")) is not None,
            "blocker evidence does not show an eligible sandbox error")
    preconditions = context.get("preconditions")
    require(isinstance(preconditions, dict), "preconditions are required")
    require(preconditions.get("plugin_activation") is True, "plugin activation must succeed")
    require(preconditions.get("target_spec_selection") is True, "target/spec selection must succeed")
    require(preconditions.get("build_check_status") == "passed", "build/check must pass before bridge")

    evaluation_root = Path(context.get("evaluation_root", "")).resolve(strict=True)
    repository_root = Path(context.get("repository_root", "")).resolve(strict=True)
    case_root = Path(pending["snapshot"]["case_realpath"]).resolve(strict=True)
    require(is_within(case_root, evaluation_root), "case root is outside evaluation root")
    require(not is_within(case_root, repository_root), "case root must be outside repository root")
    evidence_root = Path(context.get("evidence_output_root", "")).resolve(strict=False)
    require(is_within(evidence_root, evaluation_root), "evidence output escapes evaluation root")
    require(not is_within(evidence_root, case_root), "evidence output must be separate from case source")
    validate_snapshot_shape(pending.get("snapshot", {}))
    require(Path(pending["snapshot"]["case_realpath"]).resolve(strict=True) == case_root,
            "case_realpath is not canonical")
    validate_matrix(pending.get("matrix"), case_root)
    runner = Path(context.get("runner_path", "")).resolve(strict=True)
    require(runner.is_file(), "runner_path is missing")
    require_hash(context.get("runner_sha256"), "runner_sha256")
    require(sha256_file(runner) == context["runner_sha256"], "runner_sha256 mismatch")

    if check_current:
        current = compute_current_snapshot(envelope)
        mismatches = [key for key in SNAPSHOT_KEYS if current[key] != pending["snapshot"][key]]
        if str(current["case_realpath"]) != pending["snapshot"]["case_realpath"]:
            mismatches.insert(0, "case_realpath")
        if mismatches:
            return {"type": "StaleRenderRequest", "mismatched_manifests": mismatches}
    return {"type": "ValidRenderRequest", "request_sha256": envelope["request_sha256"]}


def validate_capture(envelope: dict[str, Any], capture: dict[str, Any]) -> dict[str, Any]:
    validate_request(envelope, check_current=False)
    capture_type = capture.get("type")
    if capture_type == "StaleRenderRequest":
        require(isinstance(capture.get("mismatched_manifests"), list) and capture["mismatched_manifests"],
                "stale result needs mismatched manifests")
        return capture
    if capture_type == "IncompleteCapture":
        require(isinstance(capture.get("missing_scenarios"), list) and capture["missing_scenarios"],
                "incomplete result needs missing scenarios")
        return capture
    if capture_type == "CaptureBlocked":
        require(isinstance(capture.get("command"), list) and capture["command"], "blocked command is required")
        require(isinstance(capture.get("exit_code"), int) and capture["exit_code"] != 0,
                "blocked exit code must be non-zero")
        require(Path(capture.get("stderr_path", "")).is_file(), "blocked stderr_path is required")
        require(isinstance(capture.get("affected_scenarios"), list) and capture["affected_scenarios"],
                "blocked affected_scenarios are required")
        return capture
    require(capture_type == "Captured", f"unknown capture result: {capture_type}")
    evidence = capture.get("evidence")
    require(isinstance(evidence, dict), "capture evidence is required")
    pending = envelope["pending"]
    require(evidence.get("request_sha256") == envelope["request_sha256"], "capture request hash mismatch")
    require(evidence.get("producer_call_id") == pending["producer_call_id"], "capture producer mismatch")
    require(evidence.get("snapshot") == pending["snapshot"], "capture snapshot mismatch")
    require(isinstance(evidence.get("browser"), dict), "browser evidence is required")
    require_hash(evidence["browser"].get("executable_sha256"), "browser executable hash")
    argv = evidence.get("runner_argv")
    require(isinstance(argv, list) and "--runner-sha256" in argv, "runner argv/hash attribution missing")
    captures = evidence.get("captures")
    require(isinstance(captures, list), "captures must be a list")
    if not captures:
        return {"type": "IncompleteCapture", "missing_scenarios": [
            item["scenario_id"] for item in pending["matrix"]
        ]}
    expected = {item["scenario_id"]: item for item in pending["matrix"]}
    actual = {item.get("scenario_id"): item for item in captures if isinstance(item, dict)}
    missing = sorted(set(expected) - set(actual))
    if missing:
        return {"type": "IncompleteCapture", "missing_scenarios": missing}
    require(set(actual) == set(expected), "capture scenario matrix is not exact")
    for scenario_id, scenario in expected.items():
        item = actual[scenario_id]
        require(item.get("route_or_file") == scenario["route_or_file"], "capture route mismatch")
        require(item.get("viewport") == scenario["viewport"], "capture viewport mismatch")
        require(item.get("state") == scenario["state"], "capture state mismatch")
        require(item.get("exit_code") == 0, "capture exit code is non-zero")
        image = Path(item.get("image_path", ""))
        require(image.is_file() and image.stat().st_size > 0, "capture image is empty or missing")
        require(sha256_file(image) == item.get("image_sha256"), "capture image hash mismatch")
    for key in SNAPSHOT_KEYS:
        after_key = key.replace("_sha256", "_sha256_after")
        require(evidence.get(after_key) == pending["snapshot"][key], f"capture after hash mismatch: {key}")
    return {"type": "Captured", "evidence": evidence}


def expected_opened_images(capture: dict[str, Any]) -> dict[str, tuple[str, str]]:
    return {
        item["scenario_id"]: (item["image_path"], item["image_sha256"])
        for item in capture["evidence"]["captures"]
    }


def validate_adjudication(
    envelope: dict[str, Any], capture: dict[str, Any], result: dict[str, Any]
) -> dict[str, Any]:
    validated_capture = validate_capture(envelope, capture)
    require(validated_capture.get("type") == "Captured", "adjudication requires Captured evidence")
    pending = envelope["pending"]
    current = compute_current_snapshot(envelope)
    stale = [key for key in SNAPSHOT_KEYS if current[key] != pending["snapshot"][key]]
    if stale:
        require(result.get("type") == "AdjudicationUnverified", "stale snapshot cannot be adjudicated")
        require(result.get("reason") == "stale-snapshot", "stale snapshot reason is required")
        return result

    attribution = result.get("attribution")
    attribution_ok = (
        isinstance(attribution, dict)
        and attribution.get("skill") == pending["skill"]
        and attribution.get("mode") == pending["mode"]
        and attribution.get("plugin_inventory_sha256") == pending["snapshot"]["plugin_inventory_sha256"]
        and HASH_RE.fullmatch(str(attribution.get("producer_transcript_sha256", "")))
        and HASH_RE.fullmatch(str(attribution.get("adjudicator_transcript_sha256", "")))
    )
    if not attribution_ok:
        require(result.get("type") == "AdjudicationUnverified", "missing attribution cannot be adjudicated")
        require(result.get("reason") == "skill-attribution-missing", "attribution failure reason is required")
        return result

    require(result.get("type") == "Adjudicated", "expected Adjudicated result")
    require(result.get("producer_call_id") == pending["producer_call_id"], "adjudication producer mismatch")
    require(isinstance(result.get("adjudicator_call_id"), str) and result["adjudicator_call_id"],
            "adjudicator_call_id is required")
    require(result["adjudicator_call_id"] != pending["producer_call_id"],
            "bridged adjudication must be a follow-up call")
    require(result.get("snapshot") == pending["snapshot"], "adjudication snapshot mismatch")
    require(result.get("request_sha256") == envelope["request_sha256"], "adjudication request mismatch")
    require_hash(result.get("capture_sha256"), "capture_sha256")
    expected_capture_hash = sha256_bytes(canonical_bytes(capture))
    require(result["capture_sha256"] == expected_capture_hash, "adjudication capture hash mismatch")
    opened = result.get("opened_images")
    require(isinstance(opened, list) and opened, "opened_images must be non-empty")
    expected = expected_opened_images(capture)
    actual = {item.get("scenario_id"): (item.get("image_path"), item.get("image_sha256")) for item in opened}
    require(actual == expected, "opened image matrix/hash mismatch")
    require(result.get("verdict_or_acceptance_results") not in (None, [], {}), "adjudication verdict is required")
    return result


def validate_probe(evidence: dict[str, Any]) -> dict[str, Any]:
    required = (
        "probe_id", "image_path", "image_sha256", "capture_runner_sha256", "source_deleted",
        "seed_deleted", "adjudicator_call_id", "response", "comparison_passed",
    )
    for key in required:
        require(key in evidence, f"probe field missing: {key}")
    require(evidence.get("type") == "ImageProbeEvidence", "invalid probe type")
    image = Path(evidence["image_path"])
    require(image.is_file() and image.stat().st_size > 0, "probe image missing")
    require(sha256_file(image) == evidence["image_sha256"], "probe image hash mismatch")
    require_hash(evidence["capture_runner_sha256"], "capture runner hash")
    require(evidence["source_deleted"] is True and evidence["seed_deleted"] is True,
            "probe source/seed must be deleted")
    require(isinstance(evidence["adjudicator_call_id"], str) and evidence["adjudicator_call_id"],
            "probe adjudicator call is required")
    require(evidence.get("image_open_event") is True or evidence.get("comparison_passed") is True,
            "image-not-opened")
    require("producer_call_id" not in evidence and "pending" not in evidence,
            "BR0 must not masquerade as a bridge request")
    return {"type": "ImageProbeValidated", "probe_id": evidence["probe_id"]}


def validate_inner(result: dict[str, Any]) -> dict[str, Any]:
    require(result.get("type") == "InnerRender", "invalid inner render type")
    call_id = result.get("producer_call_id")
    require(isinstance(call_id, str) and call_id, "producer_call_id is required")
    require(result.get("adjudicator_call_id") == call_id, "inner adjudication must be same-call")
    require(result.get("bridge_invoked") is False, "bridge must not be invoked for InnerRender")
    require("pending" not in result and "outer_capture" not in result, "bridge evidence is forbidden")
    require(result.get("skill") in ALLOWED_SKILLS and result.get("mode") in ALLOWED_MODES,
            "inner skill/mode attribution missing")
    require_hash(result.get("plugin_inventory_sha256"), "inner plugin inventory")
    opened = result.get("opened_images")
    require(isinstance(opened, list) and opened, "inner opened_images must be non-empty")
    for item in opened:
        image = Path(item.get("image_path", ""))
        require(image.is_file() and image.stat().st_size > 0, "inner image is missing")
        require(sha256_file(image) == item.get("image_sha256"), "inner image hash mismatch")
    require(result.get("verdict_or_acceptance_results") not in (None, [], {}), "inner verdict is required")
    return {"type": "InnerRenderValidated", "producer_call_id": call_id}


def validate_index(index: dict[str, Any]) -> dict[str, Any]:
    entries = index.get("entries")
    require(isinstance(entries, list) and entries, "case index entries are required")
    seen: set[str] = set()
    for entry in entries:
        require(isinstance(entry, dict), "case index entry must be an object")
        case_id = entry.get("case_id")
        require(isinstance(case_id, str) and case_id and case_id not in seen, "invalid/duplicate case_id")
        seen.add(case_id)
        kind = entry.get("kind")
        require(kind in {"probe", "inner", "bridge", "reused", "lifecycle", "invalid-status"},
                f"unknown case index kind: {kind}")
        require(isinstance(entry.get("canonical_sections"), list) and entry["canonical_sections"],
                "canonical sections are required")
        require(entry.get("verdict") in {"pass", "fail", "unverified", "contract-pass"},
                "invalid case verdict")
        evidence = entry.get("evidence")
        require(isinstance(evidence, list) and evidence, "evidence list is required")
        for item in evidence:
            require(isinstance(item, dict) and isinstance(item.get("path"), str), "invalid evidence item")
            require_hash(item.get("sha256"), "evidence hash")
        if kind == "bridge":
            for key in ("producer_transcript_sha256", "adjudicator_transcript_sha256", "request_sha256",
                        "capture_evidence_sha256", "plugin_inventory_sha256", "scenario_matrix_sha256"):
                require_hash(entry.get(key), key)
        elif kind == "inner":
            for key in ("producer_transcript_sha256", "plugin_inventory_sha256", "scenario_matrix_sha256"):
                require_hash(entry.get(key), key)
            require(entry.get("same_call") is True, "inner entry must prove same-call")
        elif kind == "probe":
            require_hash(entry.get("probe_evidence_sha256"), "probe evidence hash")
        elif kind == "reused":
            require_hash(entry.get("prior_report_sha256"), "prior report hash")
            require_hash(entry.get("transcript_sha256"), "reused transcript hash")
    return {"type": "CaseIndexValidated", "count": len(entries)}


def verify_archive(root: Path) -> dict[str, Any]:
    root = root.resolve(strict=True)
    require((root / "case-index.json").is_file(), "archive case-index.json is missing")
    require((root / "redaction-policy.json").is_file(), "archive redaction-policy.json is missing")
    validate_index(load_json(root / "case-index.json"))
    scanned = 0
    for item in root.rglob("*"):
        if item.is_symlink():
            raise ContractError(f"archive symlink is forbidden: {item}")
        if not item.is_file():
            continue
        scanned += 1
        name = item.name
        require(name not in FORBIDDEN_ARCHIVE_NAMES, f"forbidden archive file: {name}")
        require(not name.startswith(".env"), f"forbidden archive file: {name}")
        require(item.suffix.lower() not in {".pem", ".key", ".p12", ".pfx"},
                f"private key/certificate file is forbidden: {name}")
        require(SECRET_RE.search(item.read_bytes()) is None, f"secret/sentinel pattern found: {item}")
    return {"type": "ArchiveValidated", "files_scanned": scanned}


def final_bridge(case_root: Path) -> dict[str, Any]:
    envelope = load_json(case_root / "request.json")
    capture = load_json(case_root / "capture-result.json")
    capture_type = capture.get("type")
    if capture_type != "Captured":
        validated = validate_capture(envelope, capture)
        return {"case_id": envelope["pending"]["case_id"], "result": validated["type"],
                "green_eligible": False, "contract_regression_pass": True}
    adjudication_path = case_root / "adjudication.json"
    if not adjudication_path.exists():
        return {"case_id": envelope["pending"]["case_id"], "result": "AdjudicationUnverified",
                "reason": "image-not-opened", "green_eligible": False, "contract_regression_pass": True}
    result = load_json(adjudication_path)
    validated = validate_adjudication(envelope, capture, result)
    return {"case_id": envelope["pending"]["case_id"], "result": validated["type"],
            "green_eligible": validated["type"] == "Adjudicated", "contract_regression_pass": True}


def extract_codex_response(stdout: str) -> tuple[str, str, bool]:
    call_id = ""
    texts: list[str] = []
    image_event = False
    for line in stdout.splitlines():
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if event.get("type") == "thread.started":
            call_id = str(event.get("thread_id", event.get("thread", {}).get("id", "")))
        serialized = json.dumps(event, ensure_ascii=False)
        if "view_image" in serialized or '"type":"input_image"' in serialized.replace(" ", ""):
            image_event = True
        item = event.get("item")
        if isinstance(item, dict):
            text = item.get("text") or item.get("content")
            if isinstance(text, str):
                texts.append(text)
    return "\n".join(texts), call_id, image_event


def probe_image(args: argparse.Namespace) -> dict[str, Any]:
    root = Path(args.work_dir).resolve()
    private = root / "private"
    exposed = root / "exposed"
    captures = root / "captures"
    for directory in (private, exposed, captures):
        directory.mkdir(parents=True, exist_ok=True)
    code = "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(6))
    source = private / "challenge.html"
    image = exposed / f"{secrets.token_hex(8)}.png"
    source.write_text(
        "<!doctype html><meta charset='utf-8'><style>body{margin:0;width:800px;height:500px;"
        "display:grid;place-items:center;background:#101828;color:white;font-family:monospace}"
        ".card{border:14px solid #27d3a2;padding:60px;background:#26344d;text-align:center}"
        ".code{font-size:72px;letter-spacing:12px}</style><div class='card'>"
        f"<div>VISUAL CODE</div><div class='code'>{code}</div></div>",
        encoding="utf-8",
    )
    runner = Path(args.runner).resolve(strict=True)
    runner_sha = sha256_file(runner)
    capture_command = [
        args.node, str(runner), "--probe-source", str(source), "--probe-output", str(image),
        "--playwright-root", str(Path(args.playwright_root).resolve(strict=True)),
        "--chromium-executable", str(Path(args.chromium_executable).resolve(strict=True)),
        "--runner-sha256", runner_sha,
    ]
    capture_run = subprocess.run(capture_command, text=True, capture_output=True, timeout=45, check=False)
    require(capture_run.returncode == 0 and image.is_file() and image.stat().st_size > 0,
            f"probe capture failed: {capture_run.stderr[-500:]}")
    source.unlink()
    require(not source.exists(), "challenge source deletion failed")
    require(not any(private.iterdir()), "private probe directory must be empty before adjudication")
    prompt = (
        "Open the only PNG in this directory with the image viewing tool. Read the six-character "
        "VISUAL CODE shown inside the bordered card. Return exactly CODE=<six characters> and nothing else."
    )
    command = [
        args.codex, "exec", "--json", "--ephemeral", "--sandbox", args.sandbox,
        "--skip-git-repo-check", "--image", str(image),
    ]
    run = subprocess.run(
        command, cwd=exposed, input=prompt, text=True, capture_output=True,
        timeout=args.timeout, check=False,
    )
    response, call_id, image_event = extract_codex_response(run.stdout)
    match = re.search(r"CODE=([A-Z0-9]{6})", response)
    comparison = bool(match and secrets.compare_digest(match.group(1), code))
    evidence = {
        "type": "ImageProbeEvidence",
        "probe_id": f"br0-{secrets.token_hex(6)}",
        "image_path": str(image),
        "image_sha256": sha256_file(image),
        "capture_runner_sha256": runner_sha,
        "capture_command": capture_command,
        "source_deleted": True,
        "seed_deleted": True,
        "adjudicator_call_id": call_id or "unknown-call",
        "image_open_event": image_event,
        "response": response.strip(),
        "comparison_passed": comparison,
        "codex_exit_code": run.returncode,
    }
    output = root / "probe-evidence.json"
    dump_json(evidence, str(output))
    (root / "adjudicator.stdout.jsonl").write_text(run.stdout, encoding="utf-8")
    (root / "adjudicator.stderr.txt").write_text(run.stderr, encoding="utf-8")
    validate_probe(evidence)
    return evidence


def snapshot_command(args: argparse.Namespace) -> dict[str, Any]:
    case_root = Path(args.case_root).resolve(strict=True)
    return {
        "case_realpath": str(case_root),
        "fixture_manifest_sha256": manifest_hash(Path(args.fixture)),
        "product_manifest_sha256": manifest_hash(Path(args.product)),
        "design_authority_manifest_sha256": manifest_hash(Path(args.design_authority)),
        "ui_spec_manifest_sha256": manifest_hash(Path(args.ui_spec)),
        "plugin_inventory_sha256": manifest_hash(Path(args.plugin_inventory)),
    }


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    snapshot = sub.add_parser("snapshot")
    snapshot.add_argument("--case-root", required=True)
    for name in ("fixture", "product", "design-authority", "ui-spec", "plugin-inventory"):
        snapshot.add_argument(f"--{name}", required=True)
    snapshot.add_argument("--output")

    for name in ("validate-request", "validate-capture", "validate-adjudication"):
        command = sub.add_parser(name)
        command.add_argument("--request", required=True)
        if name != "validate-request":
            command.add_argument("--capture", required=True)
        if name == "validate-adjudication":
            command.add_argument("--result", required=True)
        command.add_argument("--output")

    probe = sub.add_parser("probe-image")
    probe.add_argument("--work-dir", required=True)
    probe.add_argument("--runner", required=True)
    probe.add_argument("--playwright-root", required=True)
    probe.add_argument("--chromium-executable", required=True)
    probe.add_argument("--node", default="node")
    probe.add_argument("--codex", default="codex")
    probe.add_argument("--sandbox", default="workspace-write", choices=("read-only", "workspace-write", "danger-full-access"))
    probe.add_argument("--timeout", type=int, default=180)

    validate_probe_parser = sub.add_parser("validate-probe")
    validate_probe_parser.add_argument("--evidence", required=True)
    validate_probe_parser.add_argument("--output")

    inner = sub.add_parser("finalize-inner")
    inner.add_argument("--case-root", required=True)
    inner.add_argument("--output")

    final = sub.add_parser("finalize")
    final.add_argument("--case-root", required=True)
    final.add_argument("--output")

    index = sub.add_parser("validate-index")
    index.add_argument("--index", required=True)
    index.add_argument("--output")

    archive = sub.add_parser("verify-archive")
    archive.add_argument("--root", required=True)
    archive.add_argument("--output")

    sub.add_parser("self-test")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "snapshot":
            result = snapshot_command(args)
        elif args.command == "validate-request":
            result = validate_request(load_json(args.request))
        elif args.command == "validate-capture":
            result = validate_capture(load_json(args.request), load_json(args.capture))
        elif args.command == "validate-adjudication":
            result = validate_adjudication(load_json(args.request), load_json(args.capture), load_json(args.result))
        elif args.command == "probe-image":
            result = probe_image(args)
        elif args.command == "validate-probe":
            result = validate_probe(load_json(args.evidence))
        elif args.command == "finalize-inner":
            result = validate_inner(load_json(Path(args.case_root) / "inner-result.json"))
        elif args.command == "finalize":
            result = final_bridge(Path(args.case_root))
        elif args.command == "validate-index":
            result = validate_index(load_json(args.index))
        elif args.command == "verify-archive":
            result = verify_archive(Path(args.root))
        elif args.command == "self-test":
            require(request_hash({"a": 1}) == sha256_bytes(b'{"a":1}'), "canonical hash self-test failed")
            require(not is_within(Path("/tmp"), Path.cwd()), "containment self-test failed")
            result = {"type": "SelfTestPassed", "checks": 2}
        else:
            raise ContractError(f"unsupported command: {args.command}")
        output = getattr(args, "output", None)
        if args.command != "probe-image":
            dump_json(result, output)
        return 0
    except (ContractError, FileNotFoundError, json.JSONDecodeError, subprocess.TimeoutExpired) as exc:
        dump_json({"type": "ContractError", "message": str(exc)})
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
