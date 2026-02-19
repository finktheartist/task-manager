import argparse

parser = argparse.ArgumentParser()

subparsers = parser.add_subparsers(dest="command", required=True)

add_parser = subparsers.add_parser("add")
add_parser.add_argument("title")
add_parser.set_defaults(func=cmd_add)

list_parser = subparsers.add_parser("list")
list_parser.set_defaults(func=cmd_list)

args = parser.parse_args()
args.func(args)

print(args)

def cmd_add(args, tasks):
    print(f"ADDING: {args.title}")

def cmd_list(args):
    print("LISTING TASKS")