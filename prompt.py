#!/usr/bin/env python3

from collections import defaultdict
from subprocess import Popen, PIPE, DEVNULL

def without(input, char):
    return [x for x in input if x != char]


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


STATES = {
    "A": "added",
    "M": "modified",
    "T": "type_change",
    "D": "deleted",
    "R": "renamed",
    "C": "copied",
}


def get_status():
    index_status = defaultdict(int)
    worktree_status = defaultdict(int)

    result = call_git("status", "--porcelain").split("\n")
    for file in without(result, ""):
        index_state = file[0]
        worktree_state = file[1]

        if index_state != " ":
            index_status[STATES[index_state]] += 1

        if worktree_state != " ":
            worktree_status[STATES[worktree_state]] += 1

    return {
        "index_status": index_status,
        "worktree_status": worktree_status
    }


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


def build_status_line(status):
    parts = []
    added = status["added"] + status["copied"]
    if added > 0:
        parts.append(f"\x1b[97;0m{added}+")

    modified = status["modified"] + status["renamed"] + status["type_change"]
    if modified:
        parts.append(f"\x1b[93;0m{modified}∆")

    if status["deleted"] > 0:
        parts.append(f"\x1b[0;41m{status['deleted']}-")

    return " ".join(parts)


def build_status_lines(status):
    parts = []
    index_line = build_status_line(status["index_status"])
    worktree_line = build_status_line(status["worktree_status"])

    if index_line != "":
        parts.append(index_line)

    if worktree_line != "":
        parts.append(worktree_line)

    return " \x1b[0m/ ".join(parts)


if __name__ == '__main__':
    if get_in_git_repo():
        stashes = get_shashes()
        current_branch = get_branch()
        status_line = build_status_lines(get_status())

        prompt_parts = [
            f"[\x1b[0;35m{current_branch}"
        ]

        if status_line != "":
            prompt_parts.append(status_line)

        if stashes > 0:
            prompt_parts.append(f"\x1b[0;37m{stashes}\u2691")

        prompt = " \x1b[0m| ".join(prompt_parts) + "\x1b[0m]"


        print(prompt)
