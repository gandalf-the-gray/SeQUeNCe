"""Definition of Routing protocol.

This module defines the StaticRouting protocol, which uses a pre-generated static routing table to direct reservation hops.
Routing tables may be created manually, or generated and installed automatically by the `Topology` class.
Also included is the message type used by the routing protocol.
"""

from enum import Enum
from typing import Dict, TYPE_CHECKING
if TYPE_CHECKING:
    from ..topology.node import Node 


from ..message import Message
from ..protocol import StackProtocol
import json

class StaticRoutingMessage(Message):
    """Message used for communications between routing protocol instances.

    Attributes:
        msg_type (Enum): type of message, required by base `Message` class.
        receiver (str): name of destination protocol instance.
        payload (Message): message to be delivered to destination.
    """
    
    def __init__(self, msg_type: Enum, receiver: str, payload: "Message"):
        super().__init__(msg_type, receiver)
        self.payload = payload


class StaticRoutingProtocol(StackProtocol):
    """Class to route reservation requests.

    The `StaticRoutingProtocol` class uses a static routing table to direct the flow of reservation requests.
    This is usually defined based on the shortest quantum channel length.

    Attributes:
        own (Node): node that protocol instance is attached to.
        name (str): label for protocol instance.
        forwarding_table (Dict[str, str]): mapping of destination node names to name of node for next hop.
    """
    
    def __init__(self, own: "Node", name: str, forwarding_table: Dict):
        """Constructor for routing protocol.

        Args:
            own (Node): node protocol is attached to.
            name (str): name of protocol instance.
            forwarding_table (Dict[str, str]): forwarding routing table in format {name of destination node: name of next node}.
        """

        super().__init__(own, name)
        self.forwarding_table = forwarding_table

    def add_forwarding_rule(self, dst: str, next_node: str):
        """Adds mapping {dst: next_node} to forwarding table."""

        assert dst not in self.forwarding_table
        self.forwarding_table[dst] = next_node
        print('----------Next Hop-------------', next_node)

    def update_forwarding_rule(self, dst: str, next_node: str):
        """updates dst to map to next_node in forwarding table."""

        self.forwarding_table[dst] = next_node
        print('----------Next Hop-------------', next_node)

    def push(self, dst: str, msg: "Message"):
        """Method to receive message from upper protocols.

        Routing packages the message and forwards it to the next node in the optimal path (determined by the forwarding table).

        Args:
            dst (str): name of destination node.
            msg (Message): message to relay.

        Side Effects:
            Will invoke `push` method of lower protocol or network manager.
        """

        #Compute the next hop here using our logic
        #Pick the best possible nieghbor according to physical distance



        assert dst != self.own.name
        #-----------print(self.own.all_pair_shortest_dist)
        #dst = self.forwarding_table[dst]
        dst =  self.custom_next_best_hop(self.own.name, dst)
        new_msg = StaticRoutingMessage(Enum, self.name, msg)
        #print('--------------self.own.name------------', self.own.name)
        #print('--------------dst------------', dst)
        self._push(dst=dst, msg=new_msg)

    #--------------------------------------------------
    def custom_next_best_hop(self, curr_node, dest):
        all_pair_path = self.own.all_pair_shortest_dist
        neighbors = self.own.neighbors
        #Modified Greedy: Pick the best physical neighbor and generate entanglements through it
        least_dist = 10e10
        best_hop = None
        nodewise_dest_distance = all_pair_path[dest]
        nodewise_dest_distance = json.loads(json.dumps(nodewise_dest_distance))
        print('Dist Matrix for destination node(',dest,') :  ')
        print(nodewise_dest_distance)
        print('Neighbors of current node(',curr_node,'):  ', neighbors)
        for node in nodewise_dest_distance:
            #print((node,neighbor_dict[node]))
            if node in neighbors:
                dist = nodewise_dest_distance[node]
                if dist < least_dist:
                    best_hop = node
                    least_dist = dist
        print()
        print('---------Next Hop Calculation using Modified Greedy------------')
        print('Curr Node: ', curr_node,', picked neighbor: ', best_hop, ', distance b/w picked neighbor and destination ', least_dist)
        print('---------------------------------------------------------------')
        print()
        return best_hop
    #--------------------------------------------------

    def pop(self, src: str, msg: "StaticRoutingMessage"):
        """Message to receive reservation messages.

        Messages are forwarded to the upper protocol.

        Args:
            src (str): node sending the message.
            msg (StaticRoutingMessage): message received.

        Side Effects:
            Will call `pop` method of higher protocol.
        """

        self._pop(src=src, msg=msg.payload)

    def received_message(self, src: str, msg: "Message"):
        """Method to directly receive messages from node (should not be used)."""

        raise Exception("RSVP protocol should not call this function")

    def init(self):
        pass
