from obeyon_rfs.components import LocalNetworkCoreNode

def main():
    node = LocalNetworkCoreNode("core_node")
    node.start_as_main()

if __name__=='__main__':
    main()


