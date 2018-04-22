# By : Behzad Bahjat Manesh Ardakan
# ===================================
from mininet.net import Mininet
from mininet.node import Controller, RemoteController, OVSController
from mininet.node import CPULimitedHost, Host, Node
from mininet.node import OVSKernelSwitch, UserSwitch, OVSSwitch
from mininet.node import IVSSwitch
from mininet.cli import CLI
from mininet.log import setLogLevel, info
from mininet.link import TCLink, Intf
from subprocess import call
import requests
import json


def myNetwork():
    net = Mininet(topo=None,
                  build=False,
                  ipBase='10.0.0.0/8')

    info('*** Adding controller\n')
    c0 = net.addController(name='c0',
                           controller=RemoteController,
                           ip='127.0.0.1',
                           protocol='tcp',
                           port=6633)

    info('*** Add switches\n')
    s1 = net.addSwitch('s1', cls=OVSKernelSwitch)
    s3 = net.addSwitch('s3', cls=OVSKernelSwitch)
    s2 = net.addSwitch('s2', cls=OVSKernelSwitch)

    info('*** Add hosts\n')
    h1 = net.addHost('h1', cls=Host, ip='172.16.20.10/24', defaultRoute='via 172.16.20.1')
    h2 = net.addHost('h2', cls=Host, ip='172.16.10.10/24', defaultRoute='via 172.16.10.1')
    h3 = net.addHost('h3', cls=Host, ip='192.168.30.10/24', defaultRoute='via 192.168.30.1')
    h4 = net.addHost('h4', cls=Host, ip='192.168.30.11/24', defaultRoute='via 192.168.30.1')

    info('*** Add links\n')
    net.addLink(h1, s1)
    net.addLink(h2, s2)
    net.addLink(h3, s3)
    net.addLink(h4, s3)
    net.addLink(s1, s2)
    net.addLink(s2, s3)
    net.addLink(s1, s3)

    info('*** Starting network\n')
    net.build()
    info('*** Starting controllers\n')
    for controller in net.controllers:
        controller.start()

    info('*** Starting switches\n')
    net.get('s1').start([c0])
    net.get('s2').start([c0])
    net.get('s3').start([c0])

    info('*** Post configure switches and hosts\n')

    ## Set IP Addressess for Routers s1 s2 s3

    # ======================s1===========================
    url = 'http://localhost:8080/router/0000000000000001'
    payload = {'address': '172.16.20.1/24'}
    r = requests.post(url, data=json.dumps(payload))

    url = 'http://localhost:8080/router/0000000000000001'
    payload = {'address': '172.16.30.30/24'}
    r = requests.post(url, data=json.dumps(payload))

    url = 'http://localhost:8080/router/0000000000000001'
    payload = {'address': '192.168.100.1/24'}
    r = requests.post(url, data=json.dumps(payload))

    # =======================s2==========================
    url = 'http://localhost:8080/router/0000000000000002'
    payload = {'address': '172.16.10.1/24'}
    r = requests.post(url, data=json.dumps(payload))

    url = 'http://localhost:8080/router/0000000000000002'
    payload = {'address': '172.16.30.1/24'}
    r = requests.post(url, data=json.dumps(payload))

    url = 'http://localhost:8080/router/0000000000000002'
    payload = {'address': '192.168.10.1/24'}
    r = requests.post(url, data=json.dumps(payload))

    # =======================s3==========================
    url = 'http://localhost:8080/router/0000000000000003'
    payload = {'address': '192.168.30.1/24'}
    r = requests.post(url, data=json.dumps(payload))

    url = 'http://localhost:8080/router/0000000000000003'
    payload = {'address': '192.168.10.20/24'}
    r = requests.post(url, data=json.dumps(payload))

    url = 'http://localhost:8080/router/0000000000000003'
    payload = {'address': '192.168.100.20/24'}
    r = requests.post(url, data=json.dumps(payload))

    ## Set Default routes for routers

    # set s1 default route is s2
    url = 'http://localhost:8080/router/0000000000000001'
    payload = {'gateway': '172.16.30.1'}
    r = requests.post(url, data=json.dumps(payload))

    # set s2 default route is s1
    url = 'http://localhost:8080/router/0000000000000002'
    payload = {'gateway': '172.16.30.30'}
    r = requests.post(url, data=json.dumps(payload))

    # set s3 default route is s2
    url = 'http://localhost:8080/router/0000000000000003'
    payload = {'gateway': '192.168.10.1'}
    r = requests.post(url, data=json.dumps(payload))

    ###================ Set static routes for routers================================
    # For s2 router, set a static route to the host (192.168.30.0/24) under router s3
    url = 'http://localhost:8080/router/0000000000000002'
    payload = {'destination': '192.168.30.0/24', 'gateway': '192.168.10.20'}
    r = requests.post(url, data=json.dumps(payload))
    '''
    url = 'http://localhost:8080/router/0000000000000001'
    payload = {'destination': '192.168.30.0/24', 'gateway': '192.168.100.20' }
    r = requests.post(url, data=json.dumps(payload))

      '''
    c0.cmd('ovs-vsctl set port s3-eth4 trunk=20 vlan_mode=trunk')

    CLI(net)
    net.stop()


if __name__ == '__main__':
    setLogLevel('info')
    myNetwork()
