"""CLI entry point for envoy."""

import argparse
import getpass
import sys

from envoy import vault


def get_passphrase(prompt: str = "Passphrase: ") -> str:
    return getpass.getpass(prompt)


def cmd_push(args):
    passphrase = get_passphrase("Encryption passphrase: ")
    vault.push(args.project, args.env, args.file, passphrase)
    print(f"Pushed '{args.file}' to {args.project}/{args.env}")


def cmd_pull(args):
    passphrase = get_passphrase("Decryption passphrase: ")
    vault.pull(args.project, args.env, args.file, passphrase)
    print(f"Pulled {args.project}/{args.env} to '{args.file}'")


def cmd_list(args):
    envs = vault.list_envs(args.project)
    if not envs:
        print(f"No environments stored for project '{args.project}'")
    else:
        for e in envs:
            print(e)


def cmd_remove(args):
    removed = vault.remove(args.project, args.env)
    if removed:
        print(f"Removed {args.project}/{args.env}")
    else:
        print(f"Not found: {args.project}/{args.env}")
        sys.exit(1)


def cmd_diff(args):
    passphrase = get_passphrase("Passphrase: ")
    result = vault.diff(args.project, args.env, args.file, passphrase)
    for key in result["added"]:
        print(f"+ {key}={result['added'][key]}")
    for key in result["removed"]:
        print(f"- {key}={result['removed'][key]}")
    for key in result["changed"]:
        c = result["changed"][key]
        print(f"~ {key}: local={c['local']} remote={c['remote']}")
    if not any(result.values()):
        print("No differences found.")


def build_parser():
    parser = argparse.ArgumentParser(prog="envoy", description="Manage .env files securely")
    sub = parser.add_subparsers(dest="command", required=True)

    for cmd in ("push", "pull", "diff"):
        p = sub.add_parser(cmd)
        p.add_argument("project")
        p.add_argument("env")
        p.add_argument("--file", default=".env")

    p_list = sub.add_parser("list")
    p_list.add_argument("project")

    p_rm = sub.add_parser("remove")
    p_rm.add_argument("project")
    p_rm.add_argument("env")

    return parser


def main():
    parser = build_parser()
    args = parser.parse_args()
    dispatch = {"push": cmd_push, "pull": cmd_pull, "list": cmd_list,
                "remove": cmd_remove, "diff": cmd_diff}
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
