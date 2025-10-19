import hashlib
from pathlib import Path
from os import environ
import shutil
import subprocess
from .cli import parser

ROOT_PATH = (
    Path(environ.get("XDG_DATA_HOME", "~/.local/share")).expanduser() / "elk" / "store"
)


def get_store_path(path: Path) -> Path:
    """Gets the path to the store directory for a given path"""

    path_hash = hashlib.sha1(str(path).encode()).hexdigest()

    return ROOT_PATH / path_hash


def main():
    parsed = parser.parse_args()

    ROOT_PATH.mkdir(parents=True, exist_ok=True)

    match str(parsed.command):
        case "remove" | "rm" | "d":
            # removes a directory from the elk store, along with its symlink if it exists
            targets: list[str] = parsed.target
            by_id: bool = parsed.id

            for target in targets:
                if by_id:
                    store_path = ROOT_PATH / target

                    if not store_path.exists():
                        print(f"Cannot delete non-existent store entry {target}")
                        continue

                    origin_symlink = store_path / ".elk_origin"

                    if origin_symlink.is_symlink():
                        origin = origin_symlink.readlink()

                        if origin.exists():
                            origin.unlink()
                            print(f"Removed link at {origin}")

                        origin_symlink.unlink()

                    subprocess.run(["rm", "-r", str(store_path)], check=False)
                    print(f"Removed store entry at {store_path}")

                    continue

                target_path = Path(target).absolute()

                if not target_path.is_symlink():
                    print(
                        f"{target} is not a symlink and thus cannot be removed from the store"
                    )
                    continue

                store_path = get_store_path(target_path)

                if store_path.exists():
                    subprocess.run(["rm", "-r", str(store_path)], check=False)
                    print(f"Removed store entry at {store_path}")

                else:
                    print(f"{target} was not in the store")

                target_path.unlink()
                print(f"Removed link at {target_path}")

        case "add" | "a":
            # adds a new directory into the elk store
            targets: list[str] = parsed.target

            for target in targets:
                target_path = Path(target).absolute()

                target_path.parent.mkdir(parents=True, exist_ok=True)
                store_path = get_store_path(target_path)

                if target_path.is_symlink():
                    store_path.mkdir(parents=True, exist_ok=True)
                    target_path.unlink()

                    print(f"Recreated existing link {target_path}")

                elif target_path.exists():
                    shutil.move(target_path, store_path)
                    print(f"Moved {target_path} into store")

                else:
                    store_path.mkdir(parents=True, exist_ok=True)

                    print(f"Created new location within store for {target_path}")

                target_path.symlink_to(store_path)

                (store_path / ".elk_origin").symlink_to(target_path)

        case "list" | "ls":
            for entry in ROOT_PATH.iterdir():
                symlink = entry / ".elk_origin"

                if not symlink.is_symlink():
                    print(f"Missing .elk_origin: {entry}")

                origin = symlink.readlink()

                MISSING = "" if origin.exists() else " (origin is missing)"

                print(f"{origin} -> {entry}{MISSING}")

        case "restore" | "r":
            targets: list[str] = parsed.target

            for target in targets:
                target_path = Path(target).absolute()
                store_path = get_store_path(target_path)

                if not store_path.exists():
                    print(
                        f"Error: Store entry for '{target}' not found at {store_path}."
                    )
                    continue

                origin_symlink = store_path / ".elk_origin"

                if target_path.is_symlink():
                    current_link_target = target_path.readlink()

                    if current_link_target == store_path:
                        target_path.unlink()
                        print(f"Removed existing symlink at {target_path}")

                    elif current_link_target.is_relative_to(ROOT_PATH):
                        print(
                            f"Error: {target_path} is currently linked to a different elk store entry ({current_link_target})."
                        )
                        continue

                    else:
                        print(
                            f"Warning: {target_path} is an existing symlink (not an elk symlink). Skipping overwrite. Please move or delete it manually if you wish to restore here."
                        )
                        continue

                elif target_path.exists():
                    print(
                        f"Error: Cannot restore to '{target_path}' because it already exists and is not an elk symlink. Please move or delete it manually."
                    )
                    continue

                target_path.parent.mkdir(parents=True, exist_ok=True)

                origin_symlink.unlink(missing_ok=True)
                print(f"Removed .elk_origin from {store_path}")

                shutil.move(store_path, target_path)
                print(f"Moved content from {store_path} back to {target_path}")

        case _:
            parser.error(f"Unknown command: {parsed.command}")
