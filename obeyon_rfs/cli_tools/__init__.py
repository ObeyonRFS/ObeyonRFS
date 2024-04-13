"""
    to create new workspace you can just
    $ mkdir WORKSPACE_NAME

    package operation
        create new package
        $ orfs pkg create PACKAGE_NAME
            - internally use 
                $ poetry new PACKAGE_NAME

        install package
        $ orfs pkg install PACKAGE_DIRECTORY
            this command will create pyproject.toml?

        list packages
        $ orfs pkg list
            - list all packages installed
            
    
    run node
    $ orfs node run PACKAGE_NAME NODE_NAME


"""


import argparse
import os
from obeyon_rfs.cli_tools.cli_splitter import workspace_cmd,package_cmd,node_cmd






def main():
    parser = argparse.ArgumentParser(description="ORFS Command Line Interface")

    cmd_category = parser.add_subparsers(title="Workspace Commands", dest="cmd_category")

    # workspace_cmd = cmd_category.add_parser("workspace", help="Workspace operations")
    workspace_cmd.add_parser_to(cmd_category)
    package_cmd.add_parser_to(cmd_category)
    node_cmd.add_parser_to(cmd_category)



    args=parser.parse_args()
    args.cwd_path=os.getcwd()
    args.cli_tools_path=os.path.abspath(os.path.dirname(__file__))


    workspace_cmd.apply_args(args,parser)
    package_cmd.apply_args(args,parser)
    node_cmd.apply_args(args,parser)
    parser.print_help()

    # # Subparser for workspace command
    # workspace_parser = parser.add_subparsers(title="Workspace Commands", dest="command")
    # workspace_create=workspace_parser.add_parser("workspace_create", help="Create a new workspace")
    # workspace_create.add_argument("workspace_name", help="Name of the new workspace")

    # # Subparser for package command
    # pkg_parser = parser.add_subparsers(title="Package Commands", dest="command")
    # pkg_create = pkg_parser.add_parser("pkg_create", help="Create a new package")
    # pkg_create.add_argument("package_create_name", help="Name of the new package")

    # pkg_install = pkg_parser.add_parser("install", help="Install a package")
    # pkg_install.add_argument("directory", help="Directory of the package to install")

    # # Subparser for node command
    # node_parser = parser.add_subparsers(title="Node Commands", dest="command")
    # node_parser.add_parser("run", help="Run the node")

    # args = parser.parse_args()

    # if args.command == "pkg_create":
    #     create_workspace(args)
    # elif args.command == "new":
    #     create_package(args)
    # elif args.command == "install":
    #     install_package(args)
    # elif args.command == "run":
    #     run_node(args)
    # else:
    #     parser.print_help()

if __name__ == "__main__":
    main()


# def main():

#     arg_parser = argparse.ArgumentParser(description="ObeyonRFS CLI")
#     cmd_category_args=arg_parser.add_subparsers(dest="command category")
#     pkg_cmd_cateogry=cmd_category_args.add_parser("pkg", help="package operation")
#     node_cmd_category=cmd_category_args.add_parser("node", help="node operation")

#     pkg_cmd_cateogry.add_subparsers(dest="pkg_command")
#     pkg_new_cmd=pkg_cmd_cateogry.add_parser("new", help="create new package")
#     pkg_new_cmd.add_argument("package_name", help="package name")

#     pkg_install_cmd=pkg_cmd_cateogry.add_parser("install", help="install package")
#     pkg_install_cmd.add_argument("package_directory", help="package directory")

#     node_cmd_category.add_argument("node_command", help="node command")






#     args = arg_parser.parse_args()
#     print(args)