"""Sync .env files between multiple environments or profiles."""

from envoy import vault, audit


def sync_envs(project: str, src_env: str, dst_env: str, passphrase: str) -> dict:
    """Copy variables from src_env into dst_env, merging (dst wins on conflict)."""
    src = vault.pull(project, src_env, passphrase)
    try:
        dst = vault.pull(project, dst_env, passphrase)
    except FileNotFoundError:
        dst = {}

    merged = {**src, **dst}  # dst values take precedence
    added = {k: v for k, v in src.items() if k not in dst}
    vault.push(project, dst_env, merged, passphrase)

    audit.log_event(
        project=project,
        action="sync",
        detail=f"{src_env} -> {dst_env}, {len(added)} key(s) added",
    )
    return {"merged": merged, "added": added}


def copy_env(project: str, src_env: str, dst_env: str, passphrase: str) -> dict:
    """Overwrite dst_env with an exact copy of src_env."""
    data = vault.pull(project, src_env, passphrase)
    vault.push(project, dst_env, data, passphrase)

    audit.log_event(
        project=project,
        action="copy",
        detail=f"{src_env} -> {dst_env}",
    )
    return data


def rename_env(project: str, old_env: str, new_env: str, passphrase: str) -> None:
    """Rename an environment by copying then removing the original."""
    data = vault.pull(project, old_env, passphrase)
    vault.push(project, new_env, data, passphrase)
    vault.remove(project, old_env)

    audit.log_event(
        project=project,
        action="rename",
        detail=f"{old_env} -> {new_env}",
    )
