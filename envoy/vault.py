"""High-level vault operations combining crypto + env_file + storage."""

from envoy import crypto, env_file, storage


def push(project: str, environment: str, filepath: str, passphrase: str) -> None:
    """Read a .env file, encrypt it, and store it."""
    raw = env_file.read(filepath)
    ciphertext = crypto.encrypt(raw, passphrase)
    storage.save(project, environment, ciphertext)


def pull(project: str, environment: str, filepath: str, passphrase: str) -> None:
    """Load encrypted env, decrypt it, and write to a .env file."""
    ciphertext = storage.load(project, environment)
    plaintext = crypto.decrypt(ciphertext, passphrase)
    env_file.write(filepath, plaintext)


def list_envs(project: str) -> list:
    """List all environments stored for a project."""
    return storage.list_environments(project)


def remove(project: str, environment: str) -> bool:
    """Remove a stored environment."""
    return storage.delete(project, environment)


def diff(project: str, environment: str, filepath: str, passphrase: str) -> dict:
    """Compare local .env file with stored version.

    Returns dict with 'added', 'removed', 'changed' keys.
    """
    ciphertext = storage.load(project, environment)
    remote_text = crypto.decrypt(ciphertext, passphrase)
    remote = env_file.parse(remote_text)
    local = env_file.parse(env_file.read(filepath))

    added = {k: local[k] for k in local if k not in remote}
    removed = {k: remote[k] for k in remote if k not in local}
    changed = {
        k: {"local": local[k], "remote": remote[k]}
        for k in local
        if k in remote and local[k] != remote[k]
    }
    return {"added": added, "removed": removed, "changed": changed}
