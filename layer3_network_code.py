# Mininet L3 topology for HW5
# Routers: rA, rB, rC
# Each router has 2 hosts on its LAN plus one interface on the inter-router /24 mesh

from mininet.net import Mininet
from mininet.node import Node, OVSSwitch
from mininet.cli import CLI
from mininet.link import TCLink
from mininet.log import setLogLevel

class Router(Node):
    "A Node with IP forwarding enabled."

    def config(self, **params):
        super().config(**params)
        self.cmd('sysctl -w net.ipv4.ip_forward=1')

    def terminate(self):
        self.cmd('sysctl -w net.ipv4.ip_forward=0')
        super().terminate()

def build_topo():
    print("*** Creating network")
    net = Mininet(link=TCLink)

    print("*** Adding routers")
    rA = net.addHost('rA', cls=Router)
    rB = net.addHost('rB', cls=Router)
    rC = net.addHost('rC', cls=Router)

    print("*** Adding hosts")
    hA1 = net.addHost('hA1', ip='20.10.172.130/26', defaultRoute='via 20.10.172.129')
    hA2 = net.addHost('hA2', ip='20.10.172.131/26', defaultRoute='via 20.10.172.129')
    hB1 = net.addHost('hB1', ip='20.10.172.2/25', defaultRoute='via 20.10.172.1')
    hB2 = net.addHost('hB2', ip='20.10.172.3/25', defaultRoute='via 20.10.172.1')
    hC1 = net.addHost('hC1', ip='20.10.172.194/27', defaultRoute='via 20.10.172.193')
    hC2 = net.addHost('hC2', ip='20.10.172.195/27', defaultRoute='via 20.10.172.193')

    print("*** Adding switches")
    s1 = net.addSwitch('s1', cls=OVSSwitch, failMode='standalone')
    s2 = net.addSwitch('s2', cls=OVSSwitch, failMode='standalone')
    s3 = net.addSwitch('s3', cls=OVSSwitch, failMode='standalone')
    s4 = net.addSwitch('s4', cls=OVSSwitch, failMode='standalone')

    print("*** Creating links")
    net.addLink(s1, rA, intfName2='rA-eth1')
    net.addLink(s2, rB, intfName2='rB-eth1')
    net.addLink(s3, rC, intfName2='rC-eth1')

    net.addLink(s1, hA1)
    net.addLink(s1, hA2)
    net.addLink(s2, hB1)
    net.addLink(s2, hB2)
    net.addLink(s3, hC1)
    net.addLink(s3, hC2)

    net.addLink(s4, rA, intfName2='rA-eth2')
    net.addLink(s4, rB, intfName2='rB-eth2')
    net.addLink(s4, rC, intfName2='rC-eth2')

    print("*** Building network")
    net.build()

    # get your routers
    rA, rB, rC = net.get('rA','rB','rC')

    # 1) Assign LAN‐side IPs (your subnets from Task 1)
    rA.setIP('20.10.172.129/26', intf='rA-eth1')
    rB.setIP('20.10.172.1/25',  intf='rB-eth1')
    rC.setIP('20.10.172.193/27',intf='rC-eth1')

    # 2) Assign backbone IPs as you already had
    rA.setIP('20.10.100.1/24', intf='rA-eth2')
    rB.setIP('20.10.100.2/24', intf='rB-eth2')
    rC.setIP('20.10.100.3/24', intf='rC-eth2')

    # 3) Now actually start the network (so switches come up)
    net.start()

    # 4) Test intra-LAN reachability
    print("\n=== Testing intra-LAN connectivity only ===")
    net.ping([ net.get('hA1'), net.get('hA2') ])
    net.ping([ net.get('hB1'), net.get('hB2') ])
    net.ping([ net.get('hC1'), net.get('hC2') ])

    CLI(net)
    net.stop()
    
if __name__ == '__main__':
    setLogLevel('info')
    build_topo()