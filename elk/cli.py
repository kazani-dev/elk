from argparse import ArgumentParser

parser = ArgumentParser(
    "elk",
    description="A program for managing a local store for ephemeral directories nested in network resources.",
)

subparsers = parser.add_subparsers(required=True, dest="command")

add_parser = subparsers.add_parser("add", aliases=["a"])
add_parser.add_argument("target", nargs="+")

remove_parser = subparsers.add_parser("remove", aliases=["rm", "d"])
remove_parser.add_argument(
    "-i",
    "--id",
    help="Removes an entry by its path hash instead of by its path.",
    action="store_true",
)
remove_parser.add_argument("target", nargs="+")

list_parser = subparsers.add_parser("list", aliases=["ls"])

restore_parser = subparsers.add_parser("restore", aliases=["r"])
restore_parser.add_argument("target", nargs="+")
