import copy
from network import Network
from typing import Dict, List, Tuple, Set


# table class added to deal with level 5 and 6
class Table:
    # Tuple is an ordered list of elements, and this helps make coding aggregation and routing table more organized
    routing_table: List[Tuple[Network, str]]
    agg_networks: Set[Network]

    def __init__(self):
        self.routing_table = []
        self.agg_networks = set()

    # update the routing table using the passed in message
    def route_update_helper(self, msg):
        network = Network(msg)
        # we index the table by msg["src"]
        self.routing_table.append((network, msg["src"]))
        self.aggregate()

    # calls the prefix match method in the network class to check if there is a possible route
    def find_possible_routes(self, dst):
        possible_routes = []
        for network, neighbor in self.routing_table:
            if network.prefix_match(dst):
                possible_routes.append(network)
        return possible_routes

    # make a new table to update the changes after withdrawal
    def new_table(self, updates):
        self.routing_table = []
        for msg in updates:
            self.route_update_helper(msg)
        self.aggregate()

    # used in dump to get the table as a list
    def get_table_as_list(self):
        return [vars(entry[0]) for entry in self.routing_table]
    
    # aggregate the network whenever possible
    def aggregate(self):
        # initialize this dictionary to keep track of which networks have been aggregated
        agg_map: Dict[int, int] = {}
        # interate over each network and check for adjacent networks which can be aggregated
        for index, (network, neighbour) in enumerate(self.routing_table):
            adj_networks = self.adj_networks(network, agg_map)
            # must be adjacent AND aggregable
            if adj_networks:
                agg_networks = self.get_agg_networks(network, adj_networks)
                # update agg_map with new aggregated networks using index
                if agg_networks:
                    agg_map[index] = agg_networks
        # loop thru the aggregated map to perform the aggregation process
        for network, adj_network in agg_map.items():
            # if adjacent network exists
            if adj_network:
                # remove the adjacent network from routing table
                self.routing_table.pop(adj_network)
                # aggregate the network and netmask using helper methods
                self.routing_table[network][0].network = self.agg_network(self.routing_table[network][0].network, self.routing_table[network][0].netmask)
                self.routing_table[network][0].netmask = self.agg_netmask(self.routing_table[network][0].netmask)
        # after all checking, call aggregate
        if len(agg_map) > 0: # we need to check if call is available or it will crash
            self.aggregate()

    # returns the networks we can aggregate on
    def adj_networks(self, other, agg_map): # cant use 'network' so we use 'other' as parameter
        for index, (network, neighbour) in enumerate(self.routing_table):
            #skip if network has already been aggregated, or is passed as other
            if index not in agg_map and network != other:
                #if network is adjacent, return it (we check CIDR length and IP in binary)
                cidr1 = self.cidr_length(network.netmask)
                cidr2 = self.cidr_length(other.netmask)
                if cidr1 == cidr2:
                    if self.ip_to_binary(network.network)[:cidr1 - 1] == self.ip_to_binary(other.network)[:cidr2 - 1]:
                        return index
    
    # checks each network if it is adjacent and has the same attributes as the current network
    def get_agg_networks(self, network, adj_networks):
        for index, (peer_network, neighbour) in enumerate(self.routing_table):
            if index == adj_networks: # we cant just loop thru adj_networks, that caused errors
                if not network.have_same_attributes(peer_network):
                    return None
        return adj_networks
    
    # calculate the aggregated network using the given ip and netmask
    def agg_network(self, ip, netmask):
        cidr_length = self.cidr_length(netmask) - 1
        # binary ip up to CIDR length
        binary_ip_reduced = self.ip_to_binary(ip)[:cidr_length]
        # complete the binary ip by padding up the bits
        zeros_left_to_complete = 32 - len(binary_ip_reduced)
        binary_ip_reduced = binary_ip_reduced + "0" * zeros_left_to_complete
        return self.binary_to_ip(binary_ip_reduced)
    
    # calculate the aggregated netmask using the given netmask
    def agg_netmask(self, netmask):
        agg_netmask = ""
        cidr_length = self.cidr_length(netmask) - 1
        # there are 32 bits in an IP, so there are 32 - CIDR length zeros to complete the netmask
        zeros_left_to_complete = 32 - cidr_length
        agg_netmask = agg_netmask + "1" * cidr_length
        agg_netmask = agg_netmask + "0" * zeros_left_to_complete
        return self.binary_to_ip(agg_netmask)

    # converts a binary ip back to dotted ip decimal format
    def binary_to_ip(self, binary_ip):
        result = []
         # convert the binary to 4 different octects, and convert each octect to decimal
        for i in range(4):
            octet = binary_ip[i * 8: (i + 1) * 8]
            result.append(str(int(octet, 2)))
        return ".".join(result) # join the octects, seperated by decimals to form the desired format
    
    # converts an ip address to binary by splitting the ip by ".", converting to 8-bit binary, and mapping it all together
    def ip_to_binary(self, ip):
        return "".join(map(str, ["{0:08b}".format(int(ip)) for ip in ip.split(".")]))

    # calculates the CIDR length of a given netmask by converting to binary and counting the '1's
    def cidr_length(self, netmask):
        return max(map(len, self.ip_to_binary(netmask).split('0')))
