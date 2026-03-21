import json
import hashlib
import sys

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def canonical_json(obj) -> bytes:
    return json.dumps(obj, separators=(",", ":"), sort_keys=True).encode()

def main(bundle_path, receipt_path):
    try:
        with open(bundle_path, "rb") as f:
            bundle_bytes = f.read()

        with open(receipt_path, "r") as f:
            receipt = json.load(f)

        bundle = json.loads(bundle_bytes)

        # Required fields check
        if "bundle_hash" not in receipt or "bundle_file_hash" not in receipt:
            print("FAIL")
            return

        # Hashes
        bundle_file_hash = sha256(bundle_bytes)
        bundle_hash = sha256(canonical_json(bundle))

        # Compare
        if (
            receipt["bundle_file_hash"] == bundle_file_hash and
            receipt["bundle_hash"] == bundle_hash
        ):
            print("PASS")
        else:
            print("FAIL")

    except Exception:
        print("FAIL")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: verify.py bundle.json receipt.json")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2])