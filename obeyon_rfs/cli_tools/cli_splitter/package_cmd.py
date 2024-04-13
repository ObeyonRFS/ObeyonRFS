import argparse
import glob
import os
import sys
import shutil
import yaml


def add_parser_to(arg_parser:argparse.ArgumentParser|argparse._SubParsersAction):
    category_cmd = arg_parser.add_parser("pkg", help="Workspace operations")
    pkg_cmd=category_cmd.add_subparsers(dest="package_command")
    create_pkg_cmd=pkg_cmd.add_parser("create", help="Create a new package")
    create_pkg_cmd.add_argument("package_name", help="Name of the new package")

    install_pkg_cmd=pkg_cmd.add_parser("install", help="Install a package")
    install_pkg_cmd.add_argument("package_directory", help="Directory of the package to install")


def apply_args(args,parser:argparse.ArgumentParser):
    if args.cmd_category=="pkg":
        if args.package_command=="create":
            create_package(args.package_name,args.cwd_path,args.cli_tools_path)
        if args.package_command=="install":
            install_package(args.package_directory,args.cwd_path,args.cli_tools_path)
        else:
            print("Invalid package command\ntry\n\torfs pkg -h",file=sys.stderr,flush=True)
            sys.exit(1)


def create_package(pkg_name:str,cwd_path:str,cli_tools_path:str):
    if "package_base_name" in pkg_name:
        print("Invalid package name",file=sys.stderr,flush=True)
        sys.exit(1)


    
    # check if package_name folder exists in cwd_path
    pkg_path=os.path.join(cwd_path,pkg_name)
    if os.path.exists(pkg_path):
        print(f"Folder exists : {pkg_name}",file=sys.stderr,flush=True)
        sys.exit(1)


    # Copy entire package_name folder from cli_tools_path to cwd_path
    # And rename everything too
    pkg_src_path=os.path.join(cli_tools_path,"package_base_name")
    pkg_dest_path=os.path.join(cwd_path,pkg_name)

    os.makedirs(pkg_dest_path)
    for root,dir,files in os.walk(pkg_src_path):
        os.makedirs(os.path.join(pkg_dest_path,os.path.relpath(root,pkg_src_path)),exist_ok=True)
        for file in files:
            file_path=os.path.join(root,file)
            rel_path=os.path.relpath(file_path,pkg_src_path)
            dest_path=os.path.join(pkg_dest_path,rel_path)
            os.makedirs(os.path.dirname(dest_path),exist_ok=True)
            shutil.copyfile(file_path,dest_path)

            # replace package_name with pkg_name in the file
            with open(dest_path,"r") as f:
                content=f.read()
            content=content.replace("package_base_name",pkg_name)
            with open(dest_path,"w") as f:
                f.write(content)

    print(f"Created new package: {pkg_name}")
    sys.exit(0)
    

def install_package(pkg_input_path:str,cwd_path:str,cli_tools_path:str):
    pkg_path=os.path.abspath(pkg_input_path)
    pkg_name=os.path.basename(pkg_path)

    


    #check orfs_package.yaml
    orfs_package_yaml_path=os.path.join(pkg_path,"orfs_package.yaml")
    if not os.path.exists(orfs_package_yaml_path):
        print("Invalid package directory",file=sys.stderr,flush=True)
        sys.exit(1)
    with open(orfs_package_yaml_path,"r") as f:
        orfs_package_yaml=yaml.safe_load(f)
    if "package_name" not in orfs_package_yaml:
        print("Invalid package directory",file=sys.stderr,flush=True)
        sys.exit(1)
    if orfs_package_yaml["package_name"]!=pkg_name:
        print("Invalid package directory",file=sys.stderr,flush=True)
        sys.exit(1)
    # copy pyproject.toml from cli_tools_path to pkg_path
    cli_pyproject_toml_path=os.path.join(cli_tools_path,"file_base_generation","pyproject.toml")
    pkg_pyproject_toml_path=os.path.join(pkg_path,"pyproject.toml")
    shutil.copyfile(cli_pyproject_toml_path,pkg_pyproject_toml_path)

    # replace package_base_name with pkg_name in pyproject.toml
    with open(pkg_pyproject_toml_path,"r") as f:
        content=f.read()
    content=content.replace("package_base_name",pkg_name)
    content=content.replace("package_command_name",orfs_package_yaml["package_command_name"])
    with open(pkg_pyproject_toml_path,"w") as f:
        f.write(content)


    # pip install the package
    os.chdir(pkg_path)
    if os.system(f"pip install -e .")!=0:
        print("Failed to install package",file=sys.stderr,flush=True)
        os.chdir(cwd_path)
        os.remove(pkg_pyproject_toml_path)
        sys.exit(1)
    os.chdir(cwd_path)

    # delete pyproject.toml
    os.remove(pkg_pyproject_toml_path)


    

    # print(f"Installing package from directory: {args.directory}")
    sys.exit(0)