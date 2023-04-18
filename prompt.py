#!/usr/bin/env python3

from subprocess import Popen, PIPE, DEVNULL


def call_git(*args):
    proc = Popen(("git", *args), stdout=PIPE, stderr=DEVNULL)
    proc.wait()
    return proc.stdout.read().decode("utf-8")


def get_files(opt):
    result = call_git("ls-files", opt)
    return len([x for x in result.split('\n') if x != ""])

def get_untracked():
    found = []
    files = call_git("ls-files", "-o").strip().split("\n")

    for file in files:
        result = call_git("check-ignore", "-v", file)
        if result == "":
            found.append(file)

    return len(found)

def get_branch():
    result = call_git("branch", "--show-current")
    branch_name = result.strip()

    if branch_name == 'HEAD':
        return "--"
    return branch_name


def get_shashes():
    result = call_git("stash", "list")
    return len([x for x in result.split("\n") if x != ""])


def get_in_git_repo():
    result = call_git("rev-parse", "--is-inside-work-tree")
    return result.strip() == "true"


if __name__ == '__main__':
    if get_in_git_repo():
        current_branch = get_branch()
        tracked_files = get_files("-c")
        untracked_files = get_untracked()
        stashes = get_shashes()

        prompt = " ".join([x for x in [
            f"[\x1b[0;35m{current_branch}",
            "\x1b[0m|",
            f"\x1b[0;34m{tracked_files}+" if tracked_files > 0 else "",
            f"\x1b[0;31m{untracked_files}\u26A0" if untracked_files > 0 else "",
            f"\x1b[0;37m{stashes}\u2691" if stashes > 0 else ""
        ] if x != ""]) + "\x1b[0m]"

        print(prompt)
