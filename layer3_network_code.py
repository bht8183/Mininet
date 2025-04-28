"""
Mininet L3 topology for HW5
Routers: rA, rB, rC
Each router has 2 hosts on its LAN plus one interface on the inter-router /24 mesh
"""

from mininet.net import Mininet
from mininet.node import Node
from mininet.cli  import CLI
from mininet.link import TCLink
from mininet.log  import setLogLevel


class Router(Node):
    "A Node with IP forwarding enabled."

    def config(self, **params):
        super().config(**params)
        # Turn on IP forwarding inside the namespace
        self.cmd('sysctl -w net.ipv4.ip_forward=1')

    def terminate(self):
        self.cmd('sysctl -w net.ipv4.ip_forward=0')
        super().terminate()


def build_topo():
    net = Mininet(link=TCLink)

    # === Routers ===
    rA = net.addHost('rA', cls=Router, ip='20.10.100.1/24')
    rB = net.addHost('rB', cls=Router, ip='20.10.100.2/24')
    rC = net.addHost('rC', cls=Router, ip='20.10.100.3/24')

    # === LAN A (20.10.172.128/26) ===
    hA1 = net.addHost('hA1', ip='20.10.172.129/26', defaultRoute='via 20.10.172.129')
    hA2 = net.addHost('hA2', ip='20.10.172.130/26', defaultRoute='via 20.10.172.129')

    # === LAN B (20.10.172.0/25) ===
    hB1 = net.addHost('hB1', ip='20.10.172.1/25',  defaultRoute='via 20.10.172.1')
    hB2 = net.addHost('hB2', ip='20.10.172.2/25',  defaultRoute='via 20.10.172.1')

    # === LAN C (20.10.172.192/27) ===
    hC1 = net.addHost('hC1', ip='20.10.172.193/27', defaultRoute='via 20.10.172.193')
    hC2 = net.addHost('hC2', ip='20.10.172.194/27', defaultRoute='via 20.10.172.193')

    # === Switches (one per LAN) ===
    sA = net.addSwitch('sA')
    sB = net.addSwitch('sB')
    sC = net.addSwitch('sC')
    sBackbone = net.addSwitch('sBB')          # connects the 3 routers together

    # --- Wire the LANs ---
    net.addLink(sA, rA, intfName2='rA-eth1', params2={'ip': '20.10.172.129/26'})
    net.addLink(sB, rB, intfName2='rB-eth1', params2={'ip': '20.10.172.1/25'})
    net.addLink(sC, rC, intfName2='rC-eth1', params2={'ip': '20.10.172.193/27'})

    net.addLink(sA, hA1); net.addLink(sA, hA2)
    net.addLink(sB, hB1); net.addLink(sB, hB2)
    net.addLink(sC, hC1); net.addLink(sC, hC2)

    # --- Inter-router mesh (/24) ---
    net.addLink(sBackbone, rA, intfName2='rA-eth2')   # already has 20.10.100.1/24
    net.addLink(sBackbone, rB, intfName2='rB-eth2')   # 20.10.100.2/24
    net.addLink(sBackbone, rC, intfName2='rC-eth2')   # 20.10.100.3/24

    net.build()

    # Quick reachability test inside each LAN only
    print("\n=== pingall (intra-LAN will reply, inter-LAN will fail) ===")
    net.pingAll()

    CLI(net)   # drop to CLI so you can run pingall again, ifconfig, etc.
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    build_topo()