import argparse
import sys
import os

def add_parser_to(arg_parser:argparse.ArgumentParser|argparse._SubParsersAction):
    global ws_cmd
    category_cmd = arg_parser.add_parser("ws", help="Workspace operations")
    ws_cmd=category_cmd.add_subparsers(dest="workspace_command")
    create_ws_cmd=ws_cmd.add_parser("create", help="Create a new workspace")
    create_ws_cmd.add_argument("workspace_name", help="Name of the new workspace")


def apply_args(args,parser:argparse.ArgumentParser):
    if args.cmd_category=="ws":
        if args.workspace_command=="create":
            create_workspace(args.workspace_name)
        else:
            print("Invalid workspace command\ntry\n\torfs ws -h",file=sys.stderr,flush=True)
            sys.exit(1)

def create_workspace(ws_name:str):
    cwd_path=os.getcwd()
    ws_path=os.path.join(cwd_path,ws_name)
    if os.path.exists(ws_path):
        print(f"Workspace already exists: {ws_name}",file=sys.stderr,flush=True)
        sys.exit(1)
    os.makedirs(ws_path)
    print(f"Created new workspace: {ws_name}")
    sys.exit(0)

    
    