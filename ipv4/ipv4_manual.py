from mininet.net import Mininet
from mininet.node import OVSBridge 
from mininet.cli import CLI 
from mininet.log import setLogLevel
import time 

def emulated_ipv4_net():
    # Initialize minite with user-space 
    net = Mininet(switch=OVSBridge, controller=None)

    print("** Adding manual IPv4 hosts")
    # Add hosts with manual IPv4 addresses and CIDR masks (/24)
    h1 = net.addHost('h1', ip=None)
    h2 = net.addHost('h2', ip=None)

    print("** Adding switch")
    s1 = net.addSwitch('s1')

    print("** Creating connections")
    net.addLink(h1, s1)
    net.addLink(h2, s1)

    print("** Starting network")
    net.start()

    # Give the virtual interface a time to stabilize
    time.sleep(1)

    print("** Manually injecting IPv4 addresses via IPv4 namespace")
    h1.cmd('ip addr add 192.168.10.11/24 dev h1-eth0')
    h2.cmd('ip addr add 192.168.10.12/24 dev h2-eth0')

    # Bring the links up explicitly
    h1.cmd('ip link set h1-eth0 up')
    h2.cmd('ip link set h2-eth0 up')

    print('** IPv4 Network is live! dropping to CLI.')
    CLI(net)

    print("** Tearing down network")
    net.stop()

if __name__ == '__main__':
    setLogLevel('info')
    emulated_ipv4_net()
