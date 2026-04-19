"""High-level vault operations: push, pull, list, remove, diff."""

from envoy import storage, crypto, env_file
from envoy.lock import assert_unlocked


def push(project: str, env: str, passphrase: str, data: dict) -> None:
    assert_unlocked(project, env)
    plaintext = env_file.serialize(data)
    ciphertext = crypto.encrypt(plaintext, passphrase)
    storage.save(project, env, ciphertext)


def pull(project: str, env: str, passphrase: str) -> dict:
    ciphertext = storage.load(project, env)
    plaintext = crypto.decrypt(ciphertext, passphrase)
    return env_file.parse(plaintext)


def list_envs(project: str) -> list[str]:
    return storage.list_environments(project)


def remove(project: str, env: str) -> None:
    assert_unlocked(project, env)
    storage.delete(project, env)


def diff(project: str, env: str, passphrase: str, local: dict) -> dict:
    remote = pull(project, env, passphrase)
    added = {k: v for k, v in local.items() if k not in remote}
    removed = {k: v for k, v in remote.items() if k not in local}
    changed = {
        k: (remote[k], local[k])
        for k in local
        if k in remote and remote[k] != local[k]
    }
    return {"added": added, "removed": removed, "changed": changed}
