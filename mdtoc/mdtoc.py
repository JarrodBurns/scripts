
import argparse
import win32clipboard
from pathlib import Path
from typing import Any, TextIO


def _get_heading_whitelist(args: list) -> list[str]:

    WHITELIST = ["#", "##", "###", "####", "#####", "######"]
    user_whitelist = []

    if args:

        try:

            for i in args:

                user_whitelist.append(WHITELIST[i - 1])

        except IndexError:

            print(f"[-w] Invalid argument: {i}")

    return user_whitelist or WHITELIST


def _valid_path(path: Path) -> bool:
    """
    Error checking for path object, expected:  the file exists
    and the format is markdown.

    Returns true if successful.
    """
    if not path.exists():

        print("ERROR:  Invalid path or destination.")
        return False

    if path.suffix.lower() not in [".md", ".markdown"]:

        print("ERROR:  Expected file format is '.md' or '.markdown'")
        return False

    return True


def get_args() -> list[str, bool, bool]:
    """
    Define and return command line arguments.
    """
    script_desc = (
        "Iterates over the ##### Headers of a markdown file "
        "and returns a formatted table of contents. "
        "Output is printed to the console and appended to the system clipboard."
    )
    parser = argparse.ArgumentParser(description=script_desc)

    parser.add_argument(
        "path",
        help=(
            "Provide the file path to a markdown file. "
            "Paths may be relative or absolute."
        )
    )

    parser.add_argument(
        "-a",
        "--alphabetical",
        help="Results are returned alphabetically.",
        action="store_true"
    )

    parser.add_argument(
        "-c",
        "--clipboard",
        help="Disable saving results to the system clipboard.",
        action="store_false"
    )

    parser.add_argument(
        "-o",
        "--output",
        help="Disable printing results to the console.",
        action="store_false"
    )

    parser.add_argument(
        "-w",
        "--whitelist",
        nargs="*",
        type=int,
        help=(
            'Whiteist for heading tags. '
            'H1 - H6 tags are supported by default. '
            'EXAMPLES:  '
            'To capture only H1 or "#" tags, you would pass ... -w 1 '
            'To capture "##" and "####", pass ... -w 2 4'
        )
    )

    return parser.parse_args()


def parse_file(file_handle: TextIO, headings: list[str, ...]) -> list[str, ...]:
    """
    Sample in from file:  "# My project name"
    Sample out:  [My project name](#my-project-name)
    """
    table_of_contents = []
    fenced_code = False

    for line in file_handle:

        if line.startswith("```"):

            fenced_code = not fenced_code

        if not fenced_code and line.startswith('#'):

            tokens = line.rstrip().split()

            if tokens[0] in headings:

                title = ' '.join(tokens[1:])
                link  = '-'.join(tokens[1:]).lower()

                table_of_contents.append(f"[{title}](#{link})")

    return table_of_contents


def set_win_clipboard(output: str) -> None:
    """
    Saves the supplied text to the Windows clipboard via API call.

    For more information on the Win32Clipboard API, visit:
    https://learn.microsoft.com/en-us/windows/win32/dataxchg/clipboard
    """
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardText(output)
    win32clipboard.CloseClipboard()


def main(args: Any) -> int:

    path = Path(args.path)
    heading_whitelist = _get_heading_whitelist(args.whitelist)

    if not _valid_path(path):

        return 1

    try:

        with open(path, 'r') as file_handle:

            results = parse_file(file_handle, heading_whitelist)

    except OSError as e:

        print(e.strerror)
        return 1

    if not results:

        print("No Headers found.")
        return 1

    if args.alphabetical:

        results = sorted(results)

    if args.output:

        for line in results:

            print(line)

    if args.clipboard:

        set_win_clipboard('\n'.join(results))

    return 0


if __name__ == "__main__":

    args = get_args()
    main(args)
