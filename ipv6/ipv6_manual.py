from mininet.net import Mininet
from mininet.node import OVSBridge
from mininet.cli import CLI
from mininet.log import setLogLevel
import time
import networkx as nx
import matplotlib.pyplot as plt

def emulated_ipv6_net():
    # Initialize ipv6 net
    net = Mininet(switch=OVSBridge, controller=None)

    print("** Adding manual IPv6 hosts")
    h1 = net.addHost("h1", ip=None)
    h2 = net.addHost("h2", ip=None)
    r1 = net.addHost("r1", ip=None)

    print("** Adding Switches")
    s1 = net.addSwitch("s1")
    s2 = net.addSwitch("s2")

    print("** Connecting Subnets")
    net.addLink(h1, s1) 
    net.addLink(r1, s1)     # r1-eth0
    net.addLink(h2, s2)
    net.addLink(r1, s2)     # r1-eth1   
    
    print("** Starting Topology")
    net.start()
    time.sleep(1)

    print("** Configuring IPv6 addresses")
    
    # Subnet A configurations
    h1.cmd("ip -6 addr add 2001:db8:1::11/64 dev h1-eth0")
    r1.cmd("ip -6 addr add 2001:db8:1::1/64 dev r1-eth0")
    
    # Subnet B Configurations
    h2.cmd("ip -6 addr add 2001:db8:2::22/64 dev h2-eth0")
    r1.cmd("ip -6 addr add 2001:db8:2::1/64 dev r1-eth1")

    print("** Activating Interfaces and Turning on IPv6 Forwarding")
    r1.cmd("sysctl -w net.ipv6.conf.all.forwarding=1")

    # Bring links UP administratively
    for node in [h1, h2, r1]:
        for intf in node.intfList():
            node.cmd(f"ip link set {intf} up")

    # Brief pause
    time.sleep(1)

    print("** Injecting IPv6 Default Gateways")
    h1.cmd("ip -6 route add default via 2001:db8:1::1")
    h2.cmd("ip -6 route add default via 2001:db8:2::1")

    print("** LAB READY - Dropping to CLI")
    CLI(net)
    net.stop() 

# Function for generating graph for the topology
def generate_graph():
    G = nx.Graph()
    G.add_edges_from([('h1','s1'), ('r1','s1'), ('h2','s2'), ('r1','s2')])
    pos = nx.spring_layout(G)
    nx.draw(G, pos, with_labels=True, node_color='lightblue', node_size=2000, font_size=16, font_weight='bold')
    plt.title("IPv6 Network Topology")
    plt.savefig("ipv6_topology.png")
    plt.show()
    print("** Topology Diagram")

if __name__ == "__main__":
    setLogLevel("info")
    emulated_ipv6_net()
    generate_graph()