from __future__ import annotations

import hashlib
import importlib.util
import json
import tempfile
import unittest
from pathlib import Path


MODULE_PATH = Path(__file__).parents[1] / "bridge.py"
SPEC = importlib.util.spec_from_file_location("ui_workflow_bridge", MODULE_PATH)
bridge = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(bridge)


def write(path: Path, value: str | bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    if isinstance(value, bytes):
        path.write_bytes(value)
    else:
        path.write_text(value, encoding="utf-8")


class BridgeFixture(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory(prefix="render-bridge-test.", dir="/tmp")
        self.evaluation_root = Path(self.temp.name)
        self.case = self.evaluation_root / "case"
        self.evidence = self.evaluation_root / "evidence"
        self.case.mkdir()
        self.evidence.mkdir()
        self.sources = {
            "fixture": self.case / "fixture",
            "product": self.case / "product",
            "design_authority": self.case / "DESIGN.md",
            "ui_spec": self.case / "UI-SPEC.md",
            "plugin_inventory": self.case / "installed-plugin",
        }
        write(self.sources["fixture"] / "index.html", "<button id='go'>Go</button>")
        write(self.sources["product"] / "app.css", "button { color: blue; }")
        write(self.sources["design_authority"], "# Design\n")
        write(self.sources["ui_spec"], "# UI Spec\n")
        write(self.sources["plugin_inventory"] / "SKILL.md", "---\nname: design-ui\n---\n")
        self.blocker = self.case / "sandbox.stderr.txt"
        write(self.blocker, "sandbox browser startup: Operation not permitted\n")
        self.runner = Path(__file__).parents[1] / "capture.mjs"
        self.snapshot = {
            "case_realpath": str(self.case.resolve()),
            "fixture_manifest_sha256": bridge.manifest_hash(self.sources["fixture"]),
            "product_manifest_sha256": bridge.manifest_hash(self.sources["product"]),
            "design_authority_manifest_sha256": bridge.manifest_hash(self.sources["design_authority"]),
            "ui_spec_manifest_sha256": bridge.manifest_hash(self.sources["ui_spec"]),
            "plugin_inventory_sha256": bridge.manifest_hash(self.sources["plugin_inventory"]),
        }
        self.pending = {
            "case_id": "BR2-test",
            "producer_call_id": "producer-1",
            "skill": "design-ui",
            "mode": "maker-qa",
            "blocker_class": "sandbox-browser-startup",
            "blocker_evidence_path": str(self.blocker),
            "snapshot": self.snapshot,
            "matrix": [{
                "scenario_id": "mobile-default",
                "route_or_file": (self.sources["fixture"] / "index.html").as_uri(),
                "viewport": {"width": 390, "height": 844},
                "state": "default",
                "actions": [{"action": "screenshot"}],
            }],
        }
        self.envelope = {
            "pending": self.pending,
            "capture_context": {
                "evaluation_root": str(self.evaluation_root),
                "repository_root": str(Path(__file__).parents[3]),
                "evidence_output_root": str(self.evidence),
                "snapshot_sources": {key: str(value) for key, value in self.sources.items()},
                "runner_path": str(self.runner),
                "runner_sha256": bridge.sha256_file(self.runner),
                "preconditions": {
                    "plugin_activation": True,
                    "target_spec_selection": True,
                    "build_check_status": "passed",
                },
            },
        }
        self.envelope["request_sha256"] = bridge.request_hash(self.pending)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def make_capture(self) -> dict:
        image = self.evidence / "mobile-default.png"
        write(image, b"not-empty-png-test-data")
        evidence = {
            "request_sha256": self.envelope["request_sha256"],
            "producer_call_id": "producer-1",
            "snapshot": self.snapshot,
            "browser": {
                "engine": "chromium",
                "version": "test",
                "executable_sha256": "a" * 64,
            },
            "runner_argv": ["node", str(self.runner), "--runner-sha256", bridge.sha256_file(self.runner)],
            "captures": [{
                "scenario_id": "mobile-default",
                "route_or_file": self.pending["matrix"][0]["route_or_file"],
                "viewport": {"width": 390, "height": 844},
                "state": "default",
                "image_path": str(image),
                "image_sha256": bridge.sha256_file(image),
                "exit_code": 0,
            }],
        }
        for key in bridge.SNAPSHOT_KEYS:
            evidence[key.replace("_sha256", "_sha256_after")] = self.snapshot[key]
        return {"type": "Captured", "evidence": evidence}

    def make_adjudication(self, capture: dict) -> dict:
        image = capture["evidence"]["captures"][0]
        return {
            "type": "Adjudicated",
            "adjudicator_call_id": "adjudicator-1",
            "producer_call_id": "producer-1",
            "request_sha256": self.envelope["request_sha256"],
            "capture_sha256": bridge.sha256_bytes(bridge.canonical_bytes(capture)),
            "snapshot": self.snapshot,
            "opened_images": [{
                "scenario_id": image["scenario_id"],
                "image_path": image["image_path"],
                "image_sha256": image["image_sha256"],
            }],
            "verdict_or_acceptance_results": {"result": "pass"},
            "attribution": {
                "skill": "design-ui",
                "mode": "maker-qa",
                "plugin_inventory_sha256": self.snapshot["plugin_inventory_sha256"],
                "producer_transcript_sha256": "b" * 64,
                "adjudicator_transcript_sha256": "c" * 64,
            },
        }


class RequestTests(BridgeFixture):
    def test_valid_request(self) -> None:
        result = bridge.validate_request(self.envelope)
        self.assertEqual(result["type"], "ValidRenderRequest")

    def test_each_snapshot_source_can_be_stale(self) -> None:
        mutations = {
            "fixture": self.sources["fixture"] / "index.html",
            "product": self.sources["product"] / "app.css",
            "design_authority": self.sources["design_authority"],
            "ui_spec": self.sources["ui_spec"],
            "plugin_inventory": self.sources["plugin_inventory"] / "SKILL.md",
        }
        expected_keys = list(bridge.SNAPSHOT_KEYS)
        for (source_name, path), expected_key in zip(mutations.items(), expected_keys):
            with self.subTest(source_name=source_name):
                original = path.read_text(encoding="utf-8")
                path.write_text(original + "changed", encoding="utf-8")
                result = bridge.validate_request(self.envelope)
                self.assertEqual(result["type"], "StaleRenderRequest")
                self.assertIn(expected_key, result["mismatched_manifests"])
                path.write_text(original, encoding="utf-8")

    def test_request_hash_mismatch_fails(self) -> None:
        self.envelope["request_sha256"] = "0" * 64
        with self.assertRaisesRegex(bridge.ContractError, "request_sha256"):
            bridge.validate_request(self.envelope)

    def test_non_eligible_blocker_fails(self) -> None:
        self.pending["blocker_class"] = "app-build-error"
        self.envelope["request_sha256"] = bridge.request_hash(self.pending)
        with self.assertRaisesRegex(bridge.ContractError, "blocker class"):
            bridge.validate_request(self.envelope)

    def test_build_must_pass(self) -> None:
        self.envelope["capture_context"]["preconditions"]["build_check_status"] = "failed"
        with self.assertRaisesRegex(bridge.ContractError, "build/check"):
            bridge.validate_request(self.envelope)

    def test_matrix_requires_viewport_state_and_unique_id(self) -> None:
        del self.pending["matrix"][0]["state"]
        self.envelope["request_sha256"] = bridge.request_hash(self.pending)
        with self.assertRaisesRegex(bridge.ContractError, "state"):
            bridge.validate_request(self.envelope)

    def test_case_script_and_credential_fill_fail(self) -> None:
        self.pending["matrix"][0]["actions"] = [{
            "action": "fill", "selector": "#go", "value": "credential-sentinel-secret", "fixture_data": True,
        }]
        self.envelope["request_sha256"] = bridge.request_hash(self.pending)
        with self.assertRaisesRegex(bridge.ContractError, "credential"):
            bridge.validate_request(self.envelope)

    def test_external_network_fails(self) -> None:
        self.pending["matrix"][0]["route_or_file"] = "https://example.com"
        self.envelope["request_sha256"] = bridge.request_hash(self.pending)
        with self.assertRaises(bridge.ContractError):
            bridge.validate_request(self.envelope)

    def test_root_and_symlink_escape_fail(self) -> None:
        outside = self.evaluation_root / "outside.html"
        write(outside, "outside")
        link = self.sources["fixture"] / "escape.html"
        link.symlink_to(outside)
        self.pending["matrix"][0]["route_or_file"] = link.as_uri()
        self.envelope["request_sha256"] = bridge.request_hash(self.pending)
        with self.assertRaisesRegex(bridge.ContractError, "escapes"):
            bridge.validate_request(self.envelope)


class CaptureAndAdjudicationTests(BridgeFixture):
    def test_capture_and_adjudication_positive(self) -> None:
        capture = self.make_capture()
        self.assertEqual(bridge.validate_capture(self.envelope, capture)["type"], "Captured")
        adjudication = self.make_adjudication(capture)
        self.assertEqual(bridge.validate_adjudication(self.envelope, capture, adjudication)["type"], "Adjudicated")

    def test_missing_capture_is_incomplete(self) -> None:
        capture = self.make_capture()
        capture["evidence"]["captures"] = []
        result = bridge.validate_capture(self.envelope, capture)
        self.assertEqual(result["type"], "IncompleteCapture")

    def test_empty_and_nonzero_capture_fail(self) -> None:
        capture = self.make_capture()
        image = Path(capture["evidence"]["captures"][0]["image_path"])
        image.write_bytes(b"")
        with self.assertRaisesRegex(bridge.ContractError, "empty"):
            bridge.validate_capture(self.envelope, capture)
        image.write_bytes(b"restored")
        capture = self.make_capture()
        capture["evidence"]["captures"][0]["exit_code"] = 1
        with self.assertRaisesRegex(bridge.ContractError, "non-zero"):
            bridge.validate_capture(self.envelope, capture)

    def test_post_capture_mutation_requires_unverified(self) -> None:
        capture = self.make_capture()
        write(self.sources["product"] / "app.css", "mutated")
        adjudication = self.make_adjudication(capture)
        with self.assertRaisesRegex(bridge.ContractError, "cannot be adjudicated"):
            bridge.validate_adjudication(self.envelope, capture, adjudication)
        adjudication["type"] = "AdjudicationUnverified"
        adjudication["reason"] = "stale-snapshot"
        self.assertEqual(bridge.validate_adjudication(self.envelope, capture, adjudication)["reason"], "stale-snapshot")

    def test_missing_skill_attribution_is_unverified(self) -> None:
        capture = self.make_capture()
        adjudication = self.make_adjudication(capture)
        adjudication["attribution"]["skill"] = "review-ui"
        with self.assertRaisesRegex(bridge.ContractError, "missing attribution"):
            bridge.validate_adjudication(self.envelope, capture, adjudication)
        adjudication["type"] = "AdjudicationUnverified"
        adjudication["reason"] = "skill-attribution-missing"
        self.assertEqual(
            bridge.validate_adjudication(self.envelope, capture, adjudication)["reason"],
            "skill-attribution-missing",
        )

    def test_blocked_result_requires_command_and_stderr(self) -> None:
        stderr = self.evidence / "blocked.stderr"
        write(stderr, "policy blocked")
        result = {
            "type": "CaptureBlocked",
            "command": ["node", "capture.mjs"],
            "exit_code": 64,
            "stderr_path": str(stderr),
            "affected_scenarios": ["mobile-default"],
        }
        self.assertEqual(bridge.validate_capture(self.envelope, result)["type"], "CaptureBlocked")


class ProbeAndInnerTests(BridgeFixture):
    def test_probe_is_separate_from_bridge(self) -> None:
        image = self.evidence / "probe.png"
        write(image, b"probe-image")
        probe = {
            "type": "ImageProbeEvidence",
            "probe_id": "br0-test",
            "image_path": str(image),
            "image_sha256": bridge.sha256_file(image),
            "capture_runner_sha256": bridge.sha256_file(self.runner),
            "source_deleted": True,
            "seed_deleted": True,
            "adjudicator_call_id": "probe-call",
            "image_open_event": False,
            "response": "CODE=ABC123",
            "comparison_passed": True,
        }
        self.assertEqual(bridge.validate_probe(probe)["type"], "ImageProbeValidated")
        with self.assertRaises(bridge.ContractError):
            bridge.validate_request(probe)
        probe["producer_call_id"] = "not-allowed"
        with self.assertRaisesRegex(bridge.ContractError, "masquerade"):
            bridge.validate_probe(probe)

    def test_inner_same_call_and_no_bridge(self) -> None:
        image = self.evidence / "inner.png"
        write(image, b"inner-image")
        result = {
            "type": "InnerRender",
            "producer_call_id": "same-call",
            "adjudicator_call_id": "same-call",
            "bridge_invoked": False,
            "skill": "design-ui",
            "mode": "maker-qa",
            "plugin_inventory_sha256": "a" * 64,
            "opened_images": [{"image_path": str(image), "image_sha256": bridge.sha256_file(image)}],
            "verdict_or_acceptance_results": {"result": "pass"},
        }
        self.assertEqual(bridge.validate_inner(result)["type"], "InnerRenderValidated")
        result["adjudicator_call_id"] = "other-call"
        with self.assertRaisesRegex(bridge.ContractError, "same-call"):
            bridge.validate_inner(result)
        result["adjudicator_call_id"] = "same-call"
        result["outer_capture"] = {}
        with self.assertRaisesRegex(bridge.ContractError, "forbidden"):
            bridge.validate_inner(result)


class IndexAndArchiveTests(BridgeFixture):
    def test_bridge_index_requires_full_lineage(self) -> None:
        evidence_file = self.evidence / "artifact.json"
        write(evidence_file, "{}")
        entry = {
            "case_id": "BR2",
            "kind": "bridge",
            "canonical_sections": ["8.2"],
            "verdict": "pass",
            "producer_transcript_sha256": "a" * 64,
            "adjudicator_transcript_sha256": "b" * 64,
            "request_sha256": "c" * 64,
            "capture_evidence_sha256": "d" * 64,
            "plugin_inventory_sha256": "e" * 64,
            "scenario_matrix_sha256": "f" * 64,
            "evidence": [{"path": str(evidence_file), "sha256": bridge.sha256_file(evidence_file)}],
        }
        self.assertEqual(bridge.validate_index({"entries": [entry]})["count"], 1)
        del entry["request_sha256"]
        with self.assertRaises(bridge.ContractError):
            bridge.validate_index({"entries": [entry]})

    def test_archive_rejects_auth_env_key_and_sentinel(self) -> None:
        archive = self.evaluation_root / "archive"
        archive.mkdir()
        artifact = archive / "artifact.txt"
        write(artifact, "safe")
        index = {
            "entries": [{
                "case_id": "BR0", "kind": "probe", "canonical_sections": ["8.2"],
                "verdict": "pass", "probe_evidence_sha256": "a" * 64,
                "evidence": [{"path": "artifact.txt", "sha256": bridge.sha256_file(artifact)}],
            }],
        }
        write(archive / "case-index.json", json.dumps(index))
        write(archive / "redaction-policy.json", "{}")
        self.assertEqual(bridge.verify_archive(archive)["type"], "ArchiveValidated")
        for name, content in (
            ("auth.json", "{}"),
            (".env.local", "SAFE=1"),
            ("private.pem", "key"),
            ("sentinel.txt", "credential-sentinel-do-not-copy"),
        ):
            with self.subTest(name=name):
                target = archive / name
                write(target, content)
                with self.assertRaises(bridge.ContractError):
                    bridge.verify_archive(archive)
                target.unlink()


if __name__ == "__main__":
    unittest.main()
