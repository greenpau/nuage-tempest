# Copyright 2014 OpenStack Foundation
# All Rights Reserved.
#
#    Licensed under the Apache License, Version 2.0 (the "License"); you may
#    not use this file except in compliance with the License. You may obtain
#    a copy of the License at
#
#         http://www.apache.org/licenses/LICENSE-2.0
#
#    Unless required by applicable law or agreed to in writing, software
#    distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#    WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#    License for the specific language governing permissions and limitations
#    under the License.

import uuid

from tempest import test
from tempest import config
from tempest.api.network import base
from tempest.lib.common.utils import data_utils
from tempest.lib import exceptions
from nuagetempest.services.nuage_client import NuageRestClient
from nuagetempest.lib.utils import constants as n_constants

CONF = config.CONF


class AllowedAddressPairTest(base.BaseNetworkTest):
    _interface = 'json'

    @classmethod
    def setup_clients(cls):
        super(AllowedAddressPairTest, cls).setup_clients()
        cls.nuage_vsd_client = NuageRestClient()

    @classmethod
    def resource_setup(cls):
        super(AllowedAddressPairTest, cls).resource_setup()
        if not test.is_extension_enabled('allowed-address-pairs', 'network'):
            msg = "Allowed Address Pairs extension not enabled."
            raise cls.skipException(msg)

        cls.network = cls.create_network()
        cls.create_subnet(cls.network)

        cls.ext_net_id = CONF.network.public_network_id
        cls.l3network = cls.create_network()
        cls.l3subnet = cls.create_subnet(cls.l3network)
        cls.router = cls.create_router(data_utils.rand_name('router-'),
                                       external_network_id=cls.ext_net_id)
        cls.create_router_interface(cls.router['id'], cls.l3subnet['id'])

    def _create_port_with_allowed_address_pair(self, allowed_address_pairs,
                                               net_id):
        body = self.ports_client.create_port(
            network_id=net_id,
            allowed_address_pairs=allowed_address_pairs)
        self.addCleanup(self.ports_client.delete_port, body['port']['id'])
        return body

    def _verify_port_by_id(self, port_id):
        body = self.ports_client.list_ports()
        ports = body['ports']
        port = [p for p in ports if p['id'] == port_id]
        msg = 'Created port not found in list of ports returned by Neutron'
        self.assertTrue(port, msg)

    def _verify_port_allowed_address_fields(self, port,
                                            addrpair_ip, addrpair_mac):
        ip_address = port['allowed_address_pairs'][0]['ip_address']
        mac_address = port['allowed_address_pairs'][0]['mac_address']
        self.assertEqual(ip_address, addrpair_ip)
        self.assertEqual(mac_address, addrpair_mac)

    def test_create_address_pair_on_l2domain_with_no_mac(self):
        # Create port with allowed address pair attribute
        # For /32 cidr
        addrpair_port = self.create_port(self.network)
        allowed_address_pairs = [{
                                     'ip_address': addrpair_port['fixed_ips'][0]['ip_address']}]
        body = self._create_port_with_allowed_address_pair(
            allowed_address_pairs, self.network['id'])
        port = body['port']
        self._verify_port_by_id(port['id'])
        # Confirm port was created with allowed address pair attribute
        self._verify_port_allowed_address_fields(
            port, addrpair_port['fixed_ips'][0]['ip_address'],
            port['mac_address'])
        # Check address spoofing is disabled on vport in VSD
        subnet_ext_id = self.nuage_vsd_client.get_vsd_external_id(
            port['fixed_ips'][0]['subnet_id'])
        nuage_subnet = self.nuage_vsd_client.get_l2domain(
            filters='externalID', filter_value=subnet_ext_id)
        port_ext_id = self.nuage_vsd_client.get_vsd_external_id(port['id'])
        nuage_vport = self.nuage_vsd_client.get_vport(
            n_constants.L2_DOMAIN,
            nuage_subnet[0]['ID'],
            filters='externalID',
            filter_value=port_ext_id)
        self.assertEqual(n_constants.ENABLED,
                         nuage_vport[0]['addressSpoofing'])

    @test.attr(type='smoke')
    def test_create_address_pair_on_l2domain_with_mac(self):
        # Create port with allowed address pair attribute
        # For /32 cidr
        addrpair_port = self.create_port(self.network)
        allowed_address_pairs = [{
                                     'ip_address': addrpair_port['fixed_ips'][0]['ip_address'],
                                     'mac_address': addrpair_port['mac_address']}]
        body = self._create_port_with_allowed_address_pair(
            allowed_address_pairs, self.network['id'])
        port = body['port']
        self._verify_port_by_id(port['id'])

        # Confirm port was created with allowed address pair attribute
        self._verify_port_allowed_address_fields(
            port, addrpair_port['fixed_ips'][0]['ip_address'],
            addrpair_port['mac_address'])

        # Check address spoofing is disabled on vport in VSD
        subnet_ext_id = self.nuage_vsd_client.get_vsd_external_id(
            port['fixed_ips'][0]['subnet_id'])
        nuage_subnet = self.nuage_vsd_client.get_l2domain(
            filters='externalID', filter_value=subnet_ext_id)
        port_ext_id = self.nuage_vsd_client.get_vsd_external_id(port['id'])
        nuage_vport = self.nuage_vsd_client.get_vport(
            n_constants.L2_DOMAIN,
            nuage_subnet[0]['ID'],
            filters='externalID',
            filter_value=port_ext_id)
        self.assertEqual(n_constants.ENABLED,
                         nuage_vport[0]['addressSpoofing'])

    def test_create_address_pair_on_l2domain_with_cidr(self):
        # Create port with AAP for non /32 cidr
        ip_address = '30.30.0.0/24'
        mac_address = 'fe:a0:36:4b:c8:70'
        allowed_address_pairs = [{'ip_address': ip_address,
                                  'mac_address': mac_address}]
        body = self._create_port_with_allowed_address_pair(
            allowed_address_pairs, self.network['id'])
        port = body['port']
        self._verify_port_by_id(port['id'])
        # Confirm port was created with allowed address pair attribute
        self._verify_port_allowed_address_fields(
            port, ip_address, mac_address)
        # Check address spoofing is disabled on vport in VSD
        subnet_ext_id = self.nuage_vsd_client.get_vsd_external_id(
            port['fixed_ips'][0]['subnet_id'])
        nuage_subnet = self.nuage_vsd_client.get_l2domain(
            filters='externalID', filter_value=subnet_ext_id)
        port_ext_id = self.nuage_vsd_client.get_vsd_external_id(port['id'])
        nuage_vport = self.nuage_vsd_client.get_vport(
            n_constants.L2_DOMAIN,
            nuage_subnet[0]['ID'],
            filters='externalID',
            filter_value=port_ext_id)
        self.assertEqual(n_constants.ENABLED,
                         nuage_vport[0]['addressSpoofing'])

    @test.attr(type='smoke')
    def test_create_address_pair_on_l3subnet_with_mac(self):
        # Create port with allowed address pair attribute
        addrpair_port = self.create_port(self.l3network)
        allowed_address_pairs = [{'ip_address':
                                      addrpair_port['fixed_ips'][0]['ip_address'],
                                  'mac_address': addrpair_port['mac_address']}]
        body = self._create_port_with_allowed_address_pair(
            allowed_address_pairs, self.l3network['id'])
        port = body['port']
        self._verify_port_by_id(port['id'])
        # Confirm port was created with allowed address pair attribute
        self._verify_port_allowed_address_fields(
            port, addrpair_port['fixed_ips'][0]['ip_address'],
            addrpair_port['mac_address'])
        # Check VIP is created in VSD
        l3domain_ext_id = self.nuage_vsd_client.get_vsd_external_id(
            self.router['id'])
        nuage_domain = self.nuage_vsd_client.get_resource(
            n_constants.DOMAIN,
            filters='externalID',
            filter_value=l3domain_ext_id)
        subnet_ext_id = self.nuage_vsd_client.get_vsd_external_id(
            port['fixed_ips'][0]['subnet_id'])
        nuage_subnet = self.nuage_vsd_client.get_domain_subnet(
            n_constants.DOMAIN, nuage_domain[0]['ID'],
            filters='externalID', filter_value=subnet_ext_id)
        port_ext_id = self.nuage_vsd_client.get_vsd_external_id(port['id'])
        nuage_vport = self.nuage_vsd_client.get_vport(
            n_constants.SUBNETWORK,
            nuage_subnet[0]['ID'],
            filters='externalID',
            filter_value=port_ext_id)
        self.assertEqual(n_constants.INHERITED,
                         nuage_vport[0]['addressSpoofing'])
        nuage_vip = self.nuage_vsd_client.get_virtual_ip(
            n_constants.VPORT,
            nuage_vport[0]['ID'],
            filters='virtualIP',
            filter_value=str(addrpair_port['fixed_ips'][0]['ip_address']))
        self.assertEqual(addrpair_port['mac_address'], nuage_vip[0]['MAC'])

    def test_create_address_pair_on_l3subnet_with_no_mac(self):
        # Create port with allowed address pair attribute
        addrpair_port = self.create_port(self.l3network)
        allowed_address_pairs = [{
                                     'ip_address': addrpair_port['fixed_ips'][0]['ip_address']}]
        body = self._create_port_with_allowed_address_pair(
            allowed_address_pairs, self.l3network['id'])
        port = body['port']
        self._verify_port_by_id(port['id'])
        # Confirm port was created with allowed address pair attribute
        self._verify_port_by_id(port['id'])
        self._verify_port_allowed_address_fields(
            port, addrpair_port['fixed_ips'][0]['ip_address'],
            port['mac_address'])
        # Check VIP is created in VSD
        l3domain_ext_id = self.nuage_vsd_client.get_vsd_external_id(
            self.router['id'])
        nuage_domain = self.nuage_vsd_client.get_resource(
            n_constants.DOMAIN,
            filters='externalID',
            filter_value=l3domain_ext_id)
        subnet_ext_id = self.nuage_vsd_client.get_vsd_external_id(
            port['fixed_ips'][0]['subnet_id'])
        nuage_subnet = self.nuage_vsd_client.get_domain_subnet(
            n_constants.DOMAIN, nuage_domain[0]['ID'],
            filters='externalID', filter_value=subnet_ext_id)
        port_ext_id = self.nuage_vsd_client.get_vsd_external_id(port['id'])
        nuage_vport = self.nuage_vsd_client.get_vport(
            n_constants.SUBNETWORK,
            nuage_subnet[0]['ID'],
            filters='externalID',
            filter_value=port_ext_id)
        self.assertEqual(n_constants.INHERITED,
                         nuage_vport[0]['addressSpoofing'])
        nuage_vip = self.nuage_vsd_client.get_virtual_ip(
            n_constants.VPORT,
            nuage_vport[0]['ID'],
            filters='virtualIP',
            filter_value=str(addrpair_port['fixed_ips'][0]['ip_address']))
        self.assertEqual(port['mac_address'], nuage_vip[0]['MAC'])

    def test_create_address_pair_on_l3subnet_with_cidr(self):
        # Create port with allowed address pair attribute
        ip_address = '30.30.0.0/24'
        mac_address = 'fe:a0:36:4b:c8:70'
        allowed_address_pairs = [{
                                     'ip_address': ip_address, 'mac_address': mac_address}]
        body = self._create_port_with_allowed_address_pair(
            allowed_address_pairs, self.l3network['id'])
        port = body['port']
        self._verify_port_by_id(port['id'])
        # Confirm port was created with allowed address pair attribute
        self._verify_port_allowed_address_fields(
            port, ip_address, mac_address)
        # Check VIP is created in VSD
        l3domain_ext_id = self.nuage_vsd_client.get_vsd_external_id(
            self.router['id'])
        nuage_domain = self.nuage_vsd_client.get_resource(
            n_constants.DOMAIN,
            filters='externalID',
            filter_value=l3domain_ext_id)
        subnet_ext_id = self.nuage_vsd_client.get_vsd_external_id(
            port['fixed_ips'][0]['subnet_id'])
        nuage_subnet = self.nuage_vsd_client.get_domain_subnet(
            n_constants.DOMAIN,
            nuage_domain[0]['ID'],
            filters='externalID',
            filter_value=subnet_ext_id)
        port_ext_id = self.nuage_vsd_client.get_vsd_external_id(port['id'])
        nuage_vport = self.nuage_vsd_client.get_vport(
            n_constants.SUBNETWORK,
            nuage_subnet[0]['ID'],
            filters='externalID',
            filter_value=port_ext_id)
        self.assertEqual(n_constants.ENABLED,
                         nuage_vport[0]['addressSpoofing'])

    @test.attr(type='smoke')
    def test_update_address_pair_on_l3subnet(self):
        addrpair_port_1 = self.create_port(self.l3network)
        allowed_address_pairs = [
            {'ip_address': addrpair_port_1['fixed_ips'][0]['ip_address'],
             'mac_address': addrpair_port_1['mac_address']}]
        body = self._create_port_with_allowed_address_pair(
            allowed_address_pairs, self.l3network['id'])
        port = body['port']
        self._verify_port_by_id(port['id'])
        # Confirm port was created with allowed address pair attribute
        self._verify_port_allowed_address_fields(
            port, allowed_address_pairs[0]['ip_address'],
            allowed_address_pairs[0]['mac_address'])
        # Check VIP is created in VSD
        l3domain_ext_id = self.nuage_vsd_client.get_vsd_external_id(
            self.router['id'])
        nuage_domain = self.nuage_vsd_client.get_resource(
            n_constants.DOMAIN,
            filters='externalID',
            filter_value=l3domain_ext_id)
        subnet_ext_id = self.nuage_vsd_client.get_vsd_external_id(
            port['fixed_ips'][0]['subnet_id'])
        nuage_subnet = self.nuage_vsd_client.get_domain_subnet(
            n_constants.DOMAIN, nuage_domain[0]['ID'],
            filters='externalID', filter_value=subnet_ext_id)
        port_ext_id = self.nuage_vsd_client.get_vsd_external_id(port['id'])
        nuage_vport = self.nuage_vsd_client.get_vport(
            n_constants.SUBNETWORK,
            nuage_subnet[0]['ID'],
            filters='externalID',
            filter_value=port_ext_id)
        self.assertEqual(n_constants.INHERITED,
                         nuage_vport[0]['addressSpoofing'])
        nuage_vip = self.nuage_vsd_client.get_virtual_ip(
            n_constants.VPORT,
            nuage_vport[0]['ID'],
            filters='virtualIP',
            filter_value=str(addrpair_port_1['fixed_ips'][0]['ip_address']))
        self.assertEqual(addrpair_port_1['mac_address'], nuage_vip[0]['MAC'])
        # Update the address pairs
        # Create port with allowed address pair attribute
        addrpair_port_2 = self.create_port(self.l3network)
        allowed_address_pairs = [
            {'ip_address': addrpair_port_2['fixed_ips'][0]['ip_address'],
             'mac_address': addrpair_port_2['mac_address']}]
        port = self.update_port(
            port, allowed_address_pairs=allowed_address_pairs)
        self._verify_port_by_id(port['id'])
        # Confirm port was created with allowed address pair attribute
        self._verify_port_allowed_address_fields(
            port, addrpair_port_2['fixed_ips'][0]['ip_address'],
            addrpair_port_2['mac_address'])
        # Verify new VIP is created
        port_ext_id = self.nuage_vsd_client.get_vsd_external_id(port['id'])
        nuage_vport = self.nuage_vsd_client.get_vport(
            n_constants.SUBNETWORK,
            nuage_subnet[0]['ID'],
            filters='externalID',
            filter_value=port_ext_id)
        self.assertEqual(n_constants.INHERITED,
                         nuage_vport[0]['addressSpoofing'])
        nuage_vip = self.nuage_vsd_client.get_virtual_ip(
            n_constants.VPORT,
            nuage_vport[0]['ID'],
            filters='virtualIP',
            filter_value=str(addrpair_port_2['fixed_ips'][0]['ip_address']))
        self.assertEqual(addrpair_port_2['mac_address'], nuage_vip[0]['MAC'])
        # Verify old VIP is deleted
        nuage_vip = self.nuage_vsd_client.get_virtual_ip(
            n_constants.VPORT,
            nuage_vport[0]['ID'],
            filters='virtualIP',
            filter_value=str(addrpair_port_1['fixed_ips'][0]['ip_address']))
        self.assertEmpty(nuage_vip)

    @test.attr(type='smoke')
    def test_create_address_pair_with_same_ip(self):
        # Create a vm
        post_body = {"network_id": self.l3network['id'],
                     "device_owner": 'compute:None',
                     "device_id": str(uuid.uuid1())}
        body = self.ports_client.create_port(**post_body)
        vm_port = body['port']
        self.addCleanup(self.ports_client.delete_port, vm_port['id'])

        # Create another port
        name = data_utils.rand_name('port-')
        post_body = {"network_id": self.l3network['id'],
                     "name": name}
        body = self.ports_client.create_port(**post_body)
        port = body['port']
        self.addCleanup(self.ports_client.delete_port, port['id'])
        # Create port with allowed address pair attribute
        allowed_address_pairs = [{'ip_address':
                                      vm_port['fixed_ips'][0]['ip_address']}]
        updated_name = data_utils.rand_name('port-')
        self.assertRaises(exceptions.ServerFault,
                          self.ports_client.update_port,
                          port['id'],
                          allowed_address_pairs=allowed_address_pairs,
                          name=updated_name)
        # verify port update did not go through
        body = self.ports_client.list_ports()
        ports = body['ports']
        port = [p for p in ports if p['id'] == port['id']]
        self.assertEqual(name, port[0]['name'])

    def test_fip_allowed_address_pairs_assoc(self):
        post_body = {"network_id": self.l3network['id'],
                     "device_owner": 'nuage:vip'}
        body = self.ports_client.create_port(**post_body)
        addrpair_port = body['port']
        allowed_address_pairs = [
            {'ip_address': addrpair_port['fixed_ips'][0]['ip_address'],
             'mac_address': addrpair_port['mac_address']}]
        body = self.ports_client.create_port(
            network_id=self.l3network['id'],
            allowed_address_pairs=allowed_address_pairs)
        port = body['port']
        self._verify_port_by_id(port['id'])
        # Confirm port was created with allowed address pair attribute
        self._verify_port_allowed_address_fields(
            port, allowed_address_pairs[0]['ip_address'],
            allowed_address_pairs[0]['mac_address'])
        body = self.floating_ips_client.create_floatingip(
            floating_network_id=self.ext_net_id,
            port_id=addrpair_port['id'])
        created_floating_ip = body['floatingip']
        self.assertIsNotNone(created_floating_ip['id'])
        self.assertEqual(created_floating_ip['fixed_ip_address'],
                         addrpair_port['fixed_ips'][0]['ip_address'])
        # VSD validation of VIP to FIP association
        l3dom_ext_id = self.nuage_vsd_client.get_vsd_external_id(
            self.router['id'])
        nuage_domain = self.nuage_vsd_client.get_l3domain(
            filters='externalID',
            filter_value=l3dom_ext_id)
        nuage_domain_fip = self.nuage_vsd_client.get_floatingip(
            n_constants.DOMAIN,
            nuage_domain[0]['ID'])
        subnet_ext_id = self.nuage_vsd_client.get_vsd_external_id(
            port['fixed_ips'][0]['subnet_id'])
        nuage_subnet = self.nuage_vsd_client.get_domain_subnet(
            n_constants.DOMAIN,
            nuage_domain[0]['ID'],
            filters='externalID',
            filter_value=subnet_ext_id)
        port_ext_id = self.nuage_vsd_client.get_vsd_external_id(port['id'])
        nuage_vport = self.nuage_vsd_client.get_vport(
            n_constants.SUBNETWORK,
            nuage_subnet[0]['ID'],
            filters='externalID',
            filter_value=port_ext_id)
        nuage_vip = self.nuage_vsd_client.get_virtual_ip(
            n_constants.VPORT, nuage_vport[0]['ID'],
            filters='virtualIP',
            filter_value=str(addrpair_port['fixed_ips'][0]['ip_address']))
        self.assertEqual(nuage_domain_fip[0]['ID'],
                         nuage_vip[0]['associatedFloatingIPID'])
        self.assertEqual(nuage_domain_fip[0]['assignedToObjectType'],
                         'virtualip')
        self.ports_client.delete_port(port['id'])
        self.ports_client.delete_port(addrpair_port['id'])
        self.floating_ips_client.delete_floatingip(created_floating_ip['id'])

    def test_allowed_address_pair_extraroute(self):
        addrpair_port = self.create_port(self.l3network)
        allowed_address_pairs = [{'ip_address':
                                      addrpair_port['fixed_ips'][0]['ip_address'],
                                  'mac_address': addrpair_port['mac_address']}]
        body = self._create_port_with_allowed_address_pair(
            allowed_address_pairs, self.l3network['id'])
        port = body['port']
        self._verify_port_by_id(port['id'])
        # Confirm port was created with allowed address pair attribute
        self._verify_port_allowed_address_fields(
            port, addrpair_port['fixed_ips'][0]['ip_address'],
            addrpair_port['mac_address'])
        # update the extra route
        next_hop = addrpair_port['fixed_ips'][0]['ip_address']
        destination = '201.1.1.5/32'

        test_routes = [{'nexthop': next_hop, 'destination': destination}]
        extra_route = self.routers_client.update_extra_routes(
            router_id=self.router['id'],
            routes=test_routes)

        self.addCleanup(self.routers_client.delete_extra_routes,
                        self.router['id'])
        self.assertEqual(1, len(extra_route['router']['routes']))
        self.assertEqual(destination,
                         extra_route['router']['routes'][0]['destination'])
        self.assertEqual(next_hop,
                         extra_route['router']['routes'][0]['nexthop'])
        show_body = self.routers_client.show_router(self.router['id'])
        self.assertEqual(destination,
                         show_body['router']['routes'][0]['destination'])
        self.assertEqual(next_hop,
                         show_body['router']['routes'][0]['nexthop'])
        # Check VIP is created in VSD
        l3domain_ext_id = self.nuage_vsd_client.get_vsd_external_id(
            self.router['id'])
        nuage_domain = self.nuage_vsd_client.get_resource(
            n_constants.DOMAIN,
            filters='externalID',
            filter_value=l3domain_ext_id)
        subnet_ext_id = self.nuage_vsd_client.get_vsd_external_id(
            port['fixed_ips'][0]['subnet_id'])
        nuage_subnet = self.nuage_vsd_client.get_domain_subnet(
            n_constants.DOMAIN, nuage_domain[0]['ID'],
            filters='externalID', filter_value=subnet_ext_id)
        port_ext_id = self.nuage_vsd_client.get_vsd_external_id(port['id'])
        nuage_vport = self.nuage_vsd_client.get_vport(
            n_constants.SUBNETWORK,
            nuage_subnet[0]['ID'],
            filters='externalID',
            filter_value=port_ext_id)
        self.assertEqual(n_constants.INHERITED,
                         nuage_vport[0]['addressSpoofing'])
        nuage_vip = self.nuage_vsd_client.get_virtual_ip(
            n_constants.VPORT,
            nuage_vport[0]['ID'],
            filters='virtualIP',
            filter_value=str(addrpair_port['fixed_ips'][0]['ip_address']))
        self.assertEqual(addrpair_port['mac_address'], nuage_vip[0]['MAC'])
        # Check static roues on VSD
        nuage_static_route = self.nuage_vsd_client.get_staticroute(
            parent=n_constants.DOMAIN, parent_id=nuage_domain[0]['ID'])
        self.assertEqual(
            nuage_static_route[0][u'nextHopIp'], next_hop, "wrong nexthop")
