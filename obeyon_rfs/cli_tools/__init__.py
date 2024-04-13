def main():
    """
    to create new workspace you can just
    $ mkdir WORKSPACE_NAME

    package operation
        create new package
        $ orfs pkg new PACKAGE_NAME
            - internally use 
                $ poetry new PACKAGE_NAME

        install package
        $ orfs pkg install PACKAGE_DIRECTORY
            this command will create pyproject.toml?
            
    
    run node
    $ orfs node run
        - internally use
            $ poetry run obeyon-rfs-node

    """