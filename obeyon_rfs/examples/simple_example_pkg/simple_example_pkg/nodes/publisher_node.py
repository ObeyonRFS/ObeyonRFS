import obeyon_rfs
from obeyon_rfs.node import Node
from simple_example_pkg.comm_type.msgs import CustomMsgType


def main(args=None):
    obeyon_rfs.init(args=args)
    node=Node("publisher_node")
    publisher = node.create_publisher(CustomMsgType, 'topic')
    count=0
    while True:
        msg=CustomMsgType()
        msg.data="Hello, World!"
        count+=1
        msg.count=count
        publisher.publish(msg)
        obeyon_rfs.spin_once(0.1)


if __name__=='__main__':
    main()