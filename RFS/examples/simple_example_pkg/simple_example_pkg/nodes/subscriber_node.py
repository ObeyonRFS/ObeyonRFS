import RFS
from RFS.node import Node
from simple_example_pkg.comm_type.msgs import CustomMsgType


def callback(msg:CustomMsgType):
    print("Received :",msg.count,msg.data)

def main(args=None):
    RFS.init(args=args)
    node=Node("subscriber_node")
    subscriber = node.create_subscriber('topic',CustomMsgType,lambda msg:print(msg.data))

    RFS.spin()
