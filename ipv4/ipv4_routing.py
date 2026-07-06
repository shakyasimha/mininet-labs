from mininet.net import Mininet 
from mininet.node import OVSBridge
from mininet.cli import CLI 
from mininet.log import setLogLevel
import time

def setup_routing():
    net = Mininet(switch=OVSBridge, controller=None)

    print("** Adding hosts and network routes")
    h1 = net.addHost('h1', ip=None)
    h2 = net.addHost('h2', ip=None)

    # r1 -> just a regular Linux node that'll turn into a router
    r1 = net.addHost('r1', ip=None)

    print("** Adding switch and subnets")
    s1 = net.addSwitch('s1')
    s2 = net.addSwitch('s2')

    print("** Connecting Subnet A (h1 <-> r1 <-> s1)")
    net.addLink(h1, s1)
    net.addLink(r1, s1)    # r1 first interface r1-eth0

    print("** Connecting Subnet B (h2 <-> r1 <-> s2)")
    net.addLink(h2, s2)
    net.addLink(r1, s2)     # r1 second interface r1-eth1

    print("** Starting topology")
    net.start()
    time.sleep(1)

    print("** Configuring IP Address")
    # Subnet A configuration
    h1.cmd("ip addr add 192.168.10.11/24 dev h1-eth0")
    r1.cmd("ip addr add 192.168.10.1/24 dev r1-eth0")

    # Subnet B configuration
    h2.cmd("ip addr add 192.168.20.12/24 dev h2-eth0")
    r1.cmd("ip addr add 192.168.20.1/24 dev r1-eth1")

    # Bring all the interfaces UP
    for node in [h1, h2, r1]:
        for intf in node.intfList():
            node.cmd(f"ip link set {intf} up")
    
    print("** LAB READY - Dropping to CLI")
    CLI(net)
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    setup_routing()