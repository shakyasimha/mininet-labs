from mininet.net import Mininet
from mininet.node import OVSSwitch, OVSController
from mininet.cli import CLI 
from mininet.log import setLogLevel
import time 

def sdn_topology():
    # Pass OVSController directly into the constructor
    net = Mininet(switch=OVSSwitch, controller=OVSController)

    print("** Adding manual IPv6 hosts")
    h1, h2, h3 = net.addHost("h1", ip=None), net.addHost("h2", ip=None), net.addHost("h3", ip=None)
    h4, h5, h6 = net.addHost("h4", ip=None), net.addHost("h5", ip=None), net.addHost("h6", ip=None)

    print("** Adding Switches")
    s1, s2, s3 = net.addSwitch("s1"), net.addSwitch("s2"), net.addSwitch("s3")

    print("** Connecting Hosts to Switches")
    net.addLink(h1, s1); net.addLink(h2, s1) 
    net.addLink(h3, s2); net.addLink(h4, s2)
    net.addLink(h5, s3); net.addLink(h6, s3)

    print("** Connecting Inter-Switch Links")
    net.addLink(s1, s2)
    net.addLink(s2, s3)

    # Automatically adds and boots the controller during start()
    net.addController('c0')
    
    print("** Starting Topology")
    net.start()

    print("*** Configuring IPv6 addresses")
    h1.cmd("ip -6 addr add 2001:db8:1::1/64 dev h1-eth0")
    h2.cmd("ip -6 addr add 2001:db8:1::2/64 dev h2-eth0")
    h3.cmd("ip -6 addr add 2001:db8:2::1/64 dev h3-eth0")
    h4.cmd("ip -6 addr add 2001:db8:2::2/64 dev h4-eth0")
    h5.cmd("ip -6 addr add 2001:db8:3::1/64 dev h5-eth0")
    h6.cmd("ip -6 addr add 2001:db8:3::2/64 dev h6-eth0")

    for h in [h1, h2, h3, h4, h5, h6]:
        h.cmd(f"ip link set {h.name}-eth0 up")

    time.sleep(1)
    print("** IPv6 network is live! dropping to CLI.")
    CLI(net)

    print("** Tearing down network")
    net.stop() 

if __name__ == "__main__":
    setLogLevel('info')
    sdn_topology()