import argparse
import os
from typing import Dict
import obeyon_rfs
import obeyon_rfs.core
# import RFS.comm_type.msgs
# import RFS.comm_type.srvs
from pathlib import Path
import glob
import shutil
import importlib.util
import logging

from obeyon_rfs.launch import *


def main():
    logger=logging.getLogger()

    parser = argparse.ArgumentParser(description='ObeyonRFS command line interface')
    subparsers = parser.add_subparsers(title='Command', dest='command',required=True)

    if subparsers:
        version_cmd = subparsers.add_parser('version', help='Show ObeyonRFS version')
    if subparsers:
        core_arg = subparsers.add_parser('core', help='ObeyonRFS core managing command')
        core_manging_cmd = core_arg.add_subparsers(title='ObeyonRFS core managing command', dest='core_action')
        core_manging_cmd.add_parser('start', help='Start ObeyonRFS core')
        core_manging_cmd.add_parser('stop', help='Stop ObeyonRFS core')
    if subparsers:
        package_cmd = subparsers.add_parser('package', help='ObeyonRFS package operation command')
        package_operation_cmd = package_cmd.add_subparsers(title='ObeyonRFS package operation command', dest='pkg_operation',required=True)
        if package_operation_cmd:
            package_create_cmd=package_operation_cmd.add_parser('create', help='Create ObeyonRFS package')
            if package_create_cmd:
                package_create_cmd.add_argument('package_name',type=str, help='Name of the package')
                template_choices = os.listdir(os.path.join(obeyon_rfs.__module_dir__,"examples"))
                package_create_cmd.add_argument('package_template',choices=template_choices, help='Template of the package')
            package_build_cmd=package_operation_cmd.add_parser('build', help='Build&Install ObeyonRFS package')
            if package_build_cmd:
                package_build_cmd.add_argument('package_dir',type=str, help='Location of the package directory')
    if subparsers:
        workspace_cmd = subparsers.add_parser('workspace', help='ObeyonRFS workspace operation command')
        workspace_operation_cmd = workspace_cmd.add_subparsers(title='ObeyonRFS workspace operation command', dest='ws_operation')
        if workspace_operation_cmd:
            workspace_build_cmd=workspace_operation_cmd.add_parser('build', help='Build&Install all packages inside workspace')
    if subparsers:
        node_cmd = subparsers.add_parser('node', help='ObeyonRFS node operation command')
        node_operation_cmd = node_cmd.add_subparsers(title='ObeyonRFS node operation command', dest='node_operation')
        if node_operation_cmd:
            node_run_cmd=node_operation_cmd.add_parser('run', help='Run ObeyonRFS node')
            if node_run_cmd:
                node_run_cmd.add_argument('package_name',type=str, help='Name of the package')
                node_run_cmd.add_argument('node_file_location',type=str, help='Node file location')
            

    if subparsers:
        launch_cmd = subparsers.add_parser('launcher', help='Launch the set of ObeyonRFS commands')
        launch_operation_cmd = launch_cmd.add_subparsers(title='ObeyonRFS launch operation command', dest='launch_operation')
        if launch_cmd:
            launch_run_cmd=launch_operation_cmd.add_parser('run', help='Run ObeyonRFS launch file')
            if launch_run_cmd:
                launch_run_cmd.add_argument('package_name',type=str, help='Name of the package')
                launch_run_cmd.add_argument('launch_file_location',type=str, help='Location of the launch file')


    args = parser.parse_args()
    # print(args)

    match args.command:
        case 'version':
            print('ObeyonRFS version: '+obeyon_rfs.__version__)
        case 'core':
            match args.core_action:
                case 'start':
                    print('Starting ObeyonRFS core')
                    obeyon_rfs.core.start_core()
                case 'stop':
                    print('Stopping ObeyonRFS core')
        case 'package':
            match args.pkg_operation:
                case 'create':
                    print('Creating ObeyonRFS package')
                    call_dir=os.getcwd()
                    
                    package_name:str=args.package_name
                    #check valid package name
                    if package_name.isidentifier() == False:
                        print("Invalid package name")
                        exit()
                    #is the folder with package name already exists
                    if os.path.exists(os.path.join(call_dir,package_name)):
                        print(f"Folder with {package_name} name already exists")
                        exit()

                    package_template:str=args.package_template


                    #copy package template to the new package folder
                    print("Copying package template to the new package folder")
                    package_template_dir=os.path.join(obeyon_rfs.__module_dir__,"examples",package_template)
                    new_package_dir=os.path.join(call_dir,package_name)
                    shutil.copytree(package_template_dir,new_package_dir)

                    #rename package folder and its file contents
                    print("Renaming package template")
                    print("Renaming package folder&files&files' contents")
                    while True:
                        flag_rename=False
                        print("="*20)
                        for root, dirs, files in list(os.walk(new_package_dir)):
                            print(root,dirs,files)
                            for dir in dirs:
                                if package_template in dir:
                                    dir_new = dir.replace(package_template,package_name)
                                    os.rename(os.path.join(root,dir),os.path.join(root,dir_new))
                                    flag_rename=True
                                    break
                            if flag_rename==True:
                                break
                            for file in files:#doesn't have to reloop
                                file_path = os.path.join(root, file)
                                file_path_new = file_path.replace(package_template,package_name)
                                os.rename(file_path,file_path_new)
                                #check file content
                                with open(file_path_new,"r") as f:
                                    file_content=f.read()
                                with open(file_path_new,"w") as f:
                                    f.write(file_content.replace(package_template,package_name))
                        if flag_rename==True:
                            continue
                        else:
                            break
                    print("="*20)
                    print("Done")

                case 'build':
                    call_dir=os.getcwd()
                    package_dir=args.package_dir
                    call_package_dir=os.path.join(call_dir,package_dir)
                    call_package_dir=os.path.normpath(call_package_dir)
                    if os.path.isdir(call_package_dir)==False:
                        print("Not a directory")
                        exit()
                    package_name=os.path.split(call_package_dir)[-1]
                    

                    os.chdir(call_package_dir)
                    print(f"Building {package_name} package")
                    print("="*20)
                    is_safe=os.system("pip install -r requirements.txt")
                    if is_safe!=0:
                        print("Requirements not installed")
                        exit()
                    print("="*20)
                    print(package_name)
                    is_safe=os.system(f"pip uninstall {package_name} -y")
                    if is_safe!=0:
                        print("Uninstall failed")
                        exit()
                    print("="*20)
                    os.system("pip install -e .")
                    if is_safe!=0:
                        print("Install failed")
                        exit()
        case 'workspace':
            match args.ws_operation:
                case 'build':
                    print('Building current workspace')

                    for folder in os.listdir(os.getcwd()):
                        os.system(f"rfs package build {folder}")
        case 'node':
            match args.node_operation:
                case 'run':
                    print('Running ObeyonRFS node')

                    module_name=args.package_name+"."+args.node_file_location
                    
                    module_spec = importlib.util.find_spec(module_name)
                    if module_spec is not None:
                        module = importlib.util.module_from_spec(module_spec)
                        try:
                            module_spec.loader.exec_module(module)
                            module.main()
                            
                        except Exception as e:
                            logger.exception(e)
                            exit()
                    else:
                        print('Node not found')
                        exit()
        case 'launch':
            match args.launch_operation:
                case 'run':
                    print('Launching the set of ObeyonRFS commands')

                    module_name=args.package_name+"."+args.launch_file_location
                    module_spec = importlib.util.find_spec(module_name)
                    if module_spec is not None:
                        module = importlib.util.module_from_spec(module_spec)
                        try:
                            module_spec.loader.exec_module(module)
                            launch_config:LaunchConfig=module.main()
                            launch_config.run()


                            
                        except Exception as e:
                            logger.exception(e)
                            exit()
                    else:
                        print('Launch file not found')
                        exit()

        case _:
            print('Command not found')