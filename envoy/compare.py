"""Compare env files across environments or projects."""
from typing import Dict, List, Tuple
from envoy import vault


def compare_envs(
    project: str,
    env_a: str,
    env_b: str,
    passphrase: str,
) -> Dict[str, Tuple[str | None, str | None]]:
    """Return a dict of key -> (value_in_a, value_in_b) for differing/missing keys."""
    data_a = vault.pull(project, env_a, passphrase)
    data_b = vault.pull(project, env_b, passphrase)
    all_keys = set(data_a) | set(data_b)
    result = {}
    for key in sorted(all_keys):
        va = data_a.get(key)
        vb = data_b.get(key)
        if va != vb:
            result[key] = (va, vb)
    return result


def missing_keys(data_a: dict, data_b: dict) -> List[str]:
    """Keys present in a but absent in b."""
    return sorted(set(data_a) - set(data_b))


def extra_keys(data_a: dict, data_b: dict) -> List[str]:
    """Keys present in b but absent in a."""
    return sorted(set(data_b) - set(data_a))


def summary(diff: Dict[str, Tuple]) -> Dict[str, int]:
    """Return counts of keys only in a, only in b, and changed in both."""
    only_in_a = sum(1 for v in diff.values() if v[1] is None)
    only_in_b = sum(1 for v in diff.values() if v[0] is None)
    changed = len(diff) - only_in_a - only_in_b
    return {"only_in_a": only_in_a, "only_in_b": only_in_b, "changed": changed}


def common_keys(data_a: dict, data_b: dict) -> List[str]:
    """Keys present in both a and b, regardless of value."""
    return sorted(set(data_a) & set(data_b))
