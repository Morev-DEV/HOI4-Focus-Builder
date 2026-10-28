import os
import re
import shutil
import tempfile

full_path = ""
c_tag = ""


def start():
    print(
        " MMMMMMMMMMMMMMM\n"
        " MMMMMMMMMMMMMMM\n"
        " MM--^^MMM^^--MM\n"
        "<     ( M )     >\n"
        " MM--__MMM__--MM\n"
        " MMM   MMM   MMM\n"
        " MMM   MMM   MMM\n"
        " MMM   MMM   MMM\n"
        " MMM   MMM   MMM\n\n"
        "  MOREV PROJECT"
    )
    print("\n\nHello! Welcome to Focus Maker\nLet's start!\n")


def reg():
    global full_path, c_tag

    print("Please, write your project folder")
    print(
        "Example: C:/users/user/documents/"
        "Paradox Interactive/mod/PROJECT FOLDER"
    )

    while True:
        directory = input("> ").strip().strip('"').strip("'")

        if os.path.isdir(directory):
            break

        print("OOPS! FM couldn't find folder. Try again")

    c_tag = input("Write country TAG\n> ").strip().upper()

    if len(c_tag) != 3 or not c_tag.isascii() or not c_tag.isalnum():
        print("Invalid TAG. Enter three Latin letters or digits.")
        return False

    filename = f"{c_tag}_national_focuses.txt"
    focus_directory = os.path.join(directory, "common", "national_focus")
    full_path = os.path.join(focus_directory, filename)

    try:
        os.makedirs(focus_directory, exist_ok=True)
    except OSError as error:
        print(f"Couldn't create focus folder: {error}")
        return False

    print(f"File path: {full_path}")
    return True


def new_tree():
    return (
        "focus_tree = {\n"
        f"    id = {c_tag}_focus_tree\n"
        "    country = {\n"
        "        factor = 0\n"
        "        modifier = {\n"
        "            add = 10\n"
        f"            tag = {c_tag}\n"
        "        }\n"
        "    }\n"
        "}\n"
    )


def find_tree_end(content):
    clean = list(content)
    in_string = False
    in_comment = False
    escaped = False

    for i, char in enumerate(content):
        if in_comment:
            if char == "\n":
                in_comment = False
            else:
                clean[i] = " "
            continue

        if in_string:
            clean[i] = " "

            if escaped:
                escaped = False
            elif char == "\\":
                escaped = True
            elif char == '"':
                in_string = False

            continue

        if char == "#":
            clean[i] = " "
            in_comment = True
        elif char == '"':
            clean[i] = " "
            in_string = True

    if in_string:
        raise ValueError("Unclosed string in the existing file.")

    clean_content = "".join(clean)
    matches = list(re.finditer(r"\bfocus_tree\s*=\s*\{", clean_content))

    if len(matches) != 1:
        raise ValueError(
            "The file must contain exactly one focus_tree block."
        )

    opening = matches[0].end() - 1
    depth = 0

    for i in range(opening, len(clean_content)):
        if clean_content[i] == "{":
            depth += 1
        elif clean_content[i] == "}":
            depth -= 1

            if depth == 0:
                return i

    raise ValueError("The focus_tree block has no closing brace.")


def create_backup():
    number = 0

    while True:
        if number == 0:
            backup_path = full_path + ".bak"
        else:
            backup_path = full_path + f".bak{number}"

        try:
            with open(backup_path, "xb") as backup:
                with open(full_path, "rb") as original:
                    shutil.copyfileobj(original, backup)

            print(f"Backup created: {backup_path}")
            return

        except FileExistsError:
            number += 1


def save_existing(content):
    directory = os.path.dirname(full_path)
    temp_path = None

    try:
        with tempfile.NamedTemporaryFile(
            mode="w",
            encoding="utf-8-sig",
            dir=directory,
            delete=False
        ) as temp_file:
            temp_path = temp_file.name
            temp_file.write(content)

        create_backup()
        os.replace(temp_path, full_path)
        temp_path = None

    finally:
        if temp_path and os.path.exists(temp_path):
            os.remove(temp_path)


def save_new(content):
    with open(full_path, "x", encoding="utf-8-sig") as f:
        f.write(content)


def read_focus():
    focus_id = input("Focus ID: ").strip()
    icon = input("Icon GFX ID: ").strip()

    if not focus_id or not icon:
        print("Focus ID and icon cannot be empty. Focus not added.")
        return None

    relative_position = input(
        "Relative position focus ID (leave empty if none): "
    ).strip()

    while True:
        try:
            x = int(input("x position: ").strip())
            y = int(input("y position: ").strip())
            cost = float(input("cost: ").strip())

            if not 0 < cost < float("inf"):
                print("Cost must be a positive number.")
                continue

            break

        except ValueError:
            print("x and y must be integers; cost must be a number.")

    prerequisite = input(
        "Required focus ID (leave empty if none): "
    ).strip()

    conditions = input(
        "Availability conditions "
        "(separate with ;, leave empty if none): "
    ).strip()

    completion_reward = input(
        "Completion rewards "
        "(separate with ;, leave empty if none): "
    ).strip()

    ideas = input(
        "Idea IDs (separate with ;, leave empty if none): "
    ).strip()

    lines = [
        "    focus = {",
        f"        id = {focus_id}",
        f"        icon = {icon}",
    ]

    if relative_position:
        lines.append(f"        relative_position_id = {relative_position}")

    lines.extend([
        f"        x = {x}",
        f"        y = {y}",
        f"        cost = {cost:g}",
    ])

    if prerequisite:
        lines.extend([
            "        prerequisite = {",
            f"            focus = {prerequisite}",
            "        }",
        ])

    if conditions:
        lines.append("        available = {")

        for condition in conditions.split(";"):
            condition = condition.strip()

            if condition:
                lines.append(f"            {condition}")

        lines.append("        }")

    lines.append("        completion_reward = {")

    for reward in completion_reward.split(";"):
        reward = reward.strip()

        if reward:
            lines.append(f"            {reward}")

    for idea in ideas.split(";"):
        idea = idea.strip()

        if idea:
            lines.append(f"            add_ideas = {idea}")

    lines.extend([
        "        }",
        "        ai_will_do = {",
        "            factor = 1",
        "        }",
        "    }",
    ])

    return "\n".join(lines) + "\n"


def writeF():
    existing_file = os.path.exists(full_path)

    try:
        if existing_file:
            print("\nThe focus file already exists.")
            print("1 - Continue the existing focus tree")
            print("2 - Start a new focus tree")
            print("3 - Exit")

            while True:
                choice = input("> ").strip()

                if choice in ("1", "2", "3"):
                    break

                print("Please enter 1, 2 or 3.")

            if choice == "3":
                print("No changes made.")
                return

            if choice == "1":
                with open(full_path, "r", encoding="utf-8-sig") as f:
                    content = f.read()

                find_tree_end(content)
            else:
                content = new_tree()
        else:
            content = new_tree()

        added = 0

        try:
            while True:
                print(
                    "\nWrite FINISH to save and exit, "
                    "or press Enter to add a focus."
                )

                if input("> ").strip().upper() == "FINISH":
                    break

                focus = read_focus()

                if focus is None:
                    continue

                tree_end = find_tree_end(content)
                before = content[:tree_end]

                if before and not before.endswith("\n"):
                    before += "\n"

                content = before + focus + content[tree_end:]
                added += 1
                print("Focus added.")

        except (KeyboardInterrupt, EOFError):
            print("\nStopping program and saving completed focuses.")

        if existing_file and choice == "1" and added == 0:
            print("No focuses added. The file was not changed.")
            return

        if existing_file:
            save_existing(content)
        else:
            save_new(content)

        print(f"Done! {added} focus(es) saved.")

    except FileExistsError:
        print("The file was created by another program. No changes made.")

    except (OSError, UnicodeError, ValueError) as error:
        print(f"Error: {error}")
        print("Could not save the focus tree.")


if __name__ == "__main__":
    start()

    if reg():
        writeF()