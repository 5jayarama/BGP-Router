from typing import List

# a network is an element in a routing table
class Network:
    peer: str
    network: str
    netmask: str
    localpref: int
    selfOrigin: bool
    ASPath: List[int]
    origin: str

    # initialize a network with all the information listed in the route update instructions, plus the peer
    def __init__(self, update_message):
        object.__setattr__(self, 'network', (update_message["msg"]["network"]))
        object.__setattr__(self, 'netmask', (update_message["msg"]["netmask"]))
        object.__setattr__(self, 'localpref', update_message["msg"]["localpref"])
        object.__setattr__(self, 'selfOrigin', update_message["msg"]["selfOrigin"])
        object.__setattr__(self, 'ASPath', update_message["msg"]["ASPath"])
        object.__setattr__(self, 'origin', update_message["msg"]["origin"])
        object.__setattr__(self, 'peer', (update_message["src"])) # added to meet new requirements

    # method to check if one network(self) is better than another network(other)
    def __lt__(self, other):
        # The entry with the longest prefix match wins. If the prefix lengths are equal...
        if self.cidr_length(self.netmask) > self.cidr_length(other.netmask):
            return True
        elif self.cidr_length(self.netmask) < self.cidr_length(other.netmask):
            return False
        # The entry with the highest localpref wins. If the localprefs are equal…
        if self.localpref > other.localpref:
            return True
        elif self.localpref < other.localpref:
            return False
        # The entry with selfOrigin as true wins. If all selfOrigins are the equal…
        if self.selfOrigin is True and other.selfOrigin is False:
            return True
        elif self.selfOrigin is False and other.selfOrigin is True:
            return False
        # The entry with the shortest ASPath wins. If multiple entries have the shortest length…
        if len(self.ASPath) < len(other.ASPath):
            return True
        elif len(self.ASPath) > len(other.ASPath):
            return False
        # The entry with the best origin wins, where IGP > EGP > UNK. If multiple entries have the best origin…
        if (self.origin == "IGP" and other.origin != "IGP") or (self.origin == "EGP" and other.origin == "UNK"):
            return True
        elif self.origin != other.origin: # if not equal, then self must be worse than other
            return False
        # The entry from the neighbor router (i.e., the src of the update message) with the lowest IP address.
        if self.peer.split(".") < other.peer.split("."):
            return True
        else:
            return False

    # this checks if one network(self) is equal to another network(other)
    def __eq__(self, other):
        return self.__dict__ == other.__dict__

    # check if both networks have all the same attributes(like peer, netmask, etc.)
    def have_same_attributes(self, other):
        return (self.peer == other.peer and #check if peer attribute matches
            self.netmask == other.netmask and #check if netmask attribute matches
            self.localpref == other.localpref and #check if localpref attribute matches
            self.selfOrigin == other.selfOrigin and #check if selfOrigin attribute matches
            len(self.ASPath) == len(other.ASPath) and #check if ASPath lists length attribute matches
            self.origin == other.origin) #check if origin attribute matches

    # check if an IPaddress is in this network through the first quadrant(prefix)
    def prefix_match(self, ip):
        CIDR = self.cidr_length(self.netmask)
        return self.ip_to_binary(self.network)[:CIDR] == self.ip_to_binary(ip)[:CIDR]

    # converts an ip address to binary by splitting the ip by ".", converting to 8-bit binary, and mapping it all together
    def ip_to_binary(self, ip):
        return "".join(map(str, ["{0:08b}".format(int(ip)) for ip in ip.split(".")]))

    # calculates the CIDR length of a given netmask by converting to binary and counting the '1's
    def cidr_length(self, netmask):
        return max(map(len, self.ip_to_binary(netmask).split('0')))
