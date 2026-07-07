from mininet.net import Mininet
from mininet.node import OVSBridge
from mininet.cli import CLI 
from mininet.log import setLogLevel
import time

def ipv6_multicast():
    net = Mininet(switch=OVSBridge, controller=None)

    print("** Adding manual IPv6 hosts")
    r1 = net.addHost("r1", ip=None) # Gateway node
    h1 = net.addHost("h1", ip=None) # Sender
    h2 = net.addHost("h2", ip=None) # Receiver 1
    h3 = net.addHost("h3", ip=None) # Receiver 2
    h4 = net.addHost("h4", ip=None) # Receiver 3
    
    # Adding a switch
    print("** Creating Separate Network Switches")
    s1 = net.addSwitch("s1") # Subnet A
    s2 = net.addSwitch("s2") # Subnet B

    print("** Connecting Topology Topology Matrix")
    net.addLink(h1, s1)
    net.addLink(r1, s1) # Router Interface 1 (r1-eth0)
    net.addLink(r1, s2) # Router Interface 2 (r1-eth1)
    net.addLink(h2, s2)
    net.addLink(h3, s2)
    net.addLink(h4, s2)

    print("** Starting Topology")
    net.start()
    time.sleep(1)

    print("** Configuring IPv6 Routing Space")
    r1.cmd("sysctl -w net.ipv6.conf.all.forwarding=1")

    # Assign Router Interface Unicast IPs
    r1.cmd("ip -6 addr add 2001:db8:a::1/64 dev r1-eth0")
    r1.cmd("ip -6 addr add 2001:db8:b::1/64 dev r1-eth1")

    # Sender Subnet A
    h1.cmd("ip -6 addr add 2001:db8:a::11/64 dev h1-eth0")
    h1.cmd("ip -6 route add default via 2001:db8:a::1")

    # Receivers Subnet B
    h2.cmd("ip -6 addr add 2001:db8:b::22/64 dev h2-eth0")
    h2.cmd("ip -6 route add default via 2001:db8:b::1")
    
    h3.cmd("ip -6 addr add 2001:db8:b::33/64 dev h3-eth0")
    h3.cmd("ip -6 route add default via 2001:db8:b::1")
    
    h4.cmd("ip -6 addr add 2001:db8:b::44/64 dev h4-eth0")
    h4.cmd("ip -6 route add default via 2001:db8:b::1")

    # Wait a moment for IPv6 Duplicate Address Detection (DAD) to finish clearing
    print("** Waiting for IPv6 DAD link stabilization...")
    time.sleep(3)

    print("** Launching Static Multicast Routing Daemon")
    r1.cmd("pkill smcrouted")
    time.sleep(0.5)
    r1.cmd("smcrouted -d -m")
    time.sleep(2)
    
    # Dynamic runtime injection via smcroutectl ---
    # Tell the router to accept multicast group membership on the inbound interface
    r1.cmd("smcroutectl a r1-eth0 ff05::101")
    # Rule syntax: smcroutectl a <In-Intf> <Source-IP> <Multicast-Group> <Out-Intf>
    r1.cmd("smcroutectl a r1-eth0 2001:db8:a::11 ff05::101 r1-eth1")
    time.sleep(1)

    # Running multicast listener on receivers
    print("** Starting Multicast Observers on Subnet B")
    h2.cmd('socat UDP6-RECVFROM:5001,ipv6-join-group="[ff05::101]:h2-eth0",fork STDOUT > /tmp/h2_multicast.log &')
    h3.cmd('socat UDP6-RECVFROM:5001,ipv6-join-group="[ff05::101]:h3-eth0",fork STDOUT > /tmp/h3_multicast.log &')
    h4.cmd('socat UDP6-RECVFROM:5001,ipv6-join-group="[ff05::101]:h4-eth0",fork STDOUT > /tmp/h4_multicast.log &')
    time.sleep(1)

    print("** LAB READY - Dropping to CLI")
    CLI(net)
    net.stop() 

if __name__ == "__main__":
    setLogLevel("info")
    ipv6_multicast()