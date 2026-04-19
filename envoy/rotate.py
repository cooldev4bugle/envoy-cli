"""Key rotation: re-encrypt all envs under a new passphrase."""

from envoy import storage, crypto, env_file


def rotate_project(project: str, old_passphrase: str, new_passphrase: str) -> list[str]:
    """Re-encrypt every environment in *project* with a new passphrase.

    Returns the list of environment names that were rotated.
    """
    envs = storage.list_environments(project)
    if not envs:
        raise ValueError(f"No environments found for project '{project}'")

    rotated = []
    for env_name in envs:
        ciphertext = storage.load(project, env_name)
        plaintext = crypto.decrypt(ciphertext, old_passphrase)
        pairs = env_file.parse(plaintext)
        new_ciphertext = crypto.encrypt(env_file.serialize(pairs), new_passphrase)
        storage.save(project, env_name, new_ciphertext)
        rotated.append(env_name)

    return rotated


def rotate_env(project: str, env_name: str, old_passphrase: str, new_passphrase: str) -> None:
    """Re-encrypt a single environment with a new passphrase."""
    ciphertext = storage.load(project, env_name)
    plaintext = crypto.decrypt(ciphertext, old_passphrase)
    pairs = env_file.parse(plaintext)
    new_ciphertext = crypto.encrypt(env_file.serialize(pairs), new_passphrase)
    storage.save(project, env_name, new_ciphertext)
