import hashlib


def sha256(data: str) -> str:
    return hashlib.sha256(data.encode()).hexdigest()


def verify(input_data: str, policy_definition: str, previous_state_hash: str):
    policy_hash = sha256(policy_definition)
    input_hash = sha256(input_data)

    # deterministic decision example rule
    result = "PASS" if input_hash[0] == policy_hash[0] else "FAIL"

    if result == "FAIL":
        return {
            "result": "FAIL",
            "state_hash": previous_state_hash
        }

    new_state_hash = sha256(
        previous_state_hash + input_hash + policy_hash + result
    )

    return {
        "result": "PASS",
        "state_hash": new_state_hash
    }