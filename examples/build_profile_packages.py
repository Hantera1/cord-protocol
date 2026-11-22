"""Build complete local sample packages for the initial CORD profiles.

Run from the repository root:
    python examples/build_profile_packages.py --output-dir ./build/profile-packages
"""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from verifier.profile_engine import create_profile_receipt
from verifier.verify import create_receipt

ROOT = Path(__file__).resolve().parents[1]
PROFILES = ROOT / "profiles"
EVIDENCE_ROOT = ROOT / "examples" / "profile-packages"
NOW = "2026-11-22T10:00:05Z"


def write_json(path: Path, value: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + "\\n", encoding="utf-8")


def build(profile_name: str, output_root: Path) -> Path:
    source = PROFILES / profile_name
    target = output_root / profile_name
    target.mkdir(parents=True, exist_ok=True)
    manifest = source / "manifest.json"
    evidence = EVIDENCE_ROOT / profile_name / "profile-evidence.json"
    (target / "profile-manifest.json").write_bytes(manifest.read_bytes())
    (target / "profile-evidence.json").write_bytes(evidence.read_bytes())

    bundle = {
        "spec_version": "0.1",
        "model_id": "cord-profile-fixture",
        "timestamp": "2026-11-22T10:00:00Z",
        "policy_id": "cord-profile-fixture-v0.1",
        "input_hash": "1" * 64,
        "output_hash": "2" * 64,
    }
    write_json(target / "bundle.json", bundle)
    create_receipt(target / "bundle.json", target / "receipt.json", NOW)
    create_profile_receipt(
        target / "profile-manifest.json",
        target / "profile-evidence.json",
        target / "profile-receipt.json",
        created_at="2026-11-22T10:00:06Z",
    )
    return target


def main() -> int:
    parser = argparse.ArgumentParser(description="Build CORD sample profile packages.")
    parser.add_argument("--output-dir", default="./build/profile-packages")
    args = parser.parse_args()
    output = Path(args.output_dir)
    for name in ("luxury-asset", "clock"):
        print(build(name, output))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
