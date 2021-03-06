# Copyright 2015 OpenStack Foundation
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

from netaddr import *

from tempest import config
from tempest import test
from tempest.lib import exceptions

from tempest.lib import exceptions as lib_exc
from tempest.lib.common.utils import data_utils
from nuagetempest.lib.utils import constants
from nuagetempest.lib.test import nuage_test
from nuagetempest.lib.test import tags
from nuagetempest.thirdparty.nuage.vsd_managed import base_vsd_managed_networks
from nuagetempest.thirdparty.nuage.vsd_managed import base_vsd_public_resources

CONF = config.CONF

OS_FULL_CIDR24_RANGE = 254  # .256 -1 (.0) -1 (.255)
VSD_L2_SHARED_MGD_OPT3_CIDR = IPNetwork('21.21.21.0/24')
VSD_L2_SHARED_MGD_OPT3_GW = '21.21.21.1'
VSD_L2_SHARED_MGD_OPT3 = '21.21.21.121'
VSD_L3_SHARED_MGD_OPT3_CIDR = IPNetwork('31.31.31.0/24')
VSD_L3_SHARED_MGD_OPT3_GW = '31.31.31.1'
VSD_L3_SHARED_MGD_OPT3 = '31.31.31.131'
#
VALID_CIDR = IPNetwork('3.22.111.0/24')
VALID_CIDR_GW = '3.22.111.1'
#
EXPECT_DHCP_ENABLE_TRUE = "enable_dhcp in subnet must be True"
EXPECT_DHCP_ENABLE_FALSE = "enable_dhcp in subnet must be False"
EXPECT_GATEWAY_IP_MISMATCH = "Bad subnet request: Provided gateway-ip does not match VSD configuration"
EXPECT_CIDR_IN_RANGE = "Bad request: cidr in subnet must be"
EXPECT_GATEWAY_IN_CIDR = "Invalid input for operation: Gateway is not valid on subnet."


@nuage_test.class_header(tags=[tags.ML2, tags.VSD_MANAGED])
class VSDPublicResourcesSharedNetworksML2Test(base_vsd_public_resources.BaseVSDPublicResourcesTest):

    @nuage_test.header()
    def test_os_shared_vsd_l2_shared_unmgd_l2_unmgd_without_gateway_ip(self):
        # Given  I have a VSD -L2-domain without IPAM (i.e. UnManaged)
        # And I have a VSD-L2-Shared-domain without IPAM (i.e. UnManaged)
        # And  these are linked
        vsd_l2dom_unmgd = self._given_vsdl2sharedunmgd_linkedto_vsdl2domunmgd()
        self._check_vsd_l2_shared_l2_unmgd(
            vsd_l2dom_unmgd=vsd_l2dom_unmgd,
            os_shared_network=True,
            # When I create an OS subnet with
            #   enable_dhcp == False
            #   a valid CIDR
            #   nuagenet == UUID of VSD-L2-domain
            enable_dhcp=False,
            cidr=VALID_CIDR,
            gateway_ip='',

            # Then the OS subnet has
            #   an OS allocation pool covering the full CIDR range
            #   gateway_ip equal to None
            expected_gateway_ip=None,
            #   and no network:dhcp:nuage port
            expect_network_dhcp_nuage_port=False,

            # When I spin a VM in this network
            # Then the OS  VM-IPaddress is in the valid CIDR range
            # And the VMinterface-IPaddress in the VSD-L2-domain is empty
            expect_vm_ip_addresses_equal=''
        )

    @nuage_test.header()
    def test_vsd_l2_shared_unmgd_l2_unmgd_without_gateway_ip(self):
        # Given  I have a VSD -L2-domain without IPAM (i.e. UnManaged)
        # And I have a VSD-L2-Shared-domain without IPAM (i.e. UnManaged)
        # And  these are linked
        vsd_l2dom_unmgd = self._given_vsdl2sharedunmgd_linkedto_vsdl2domunmgd()
        self._check_vsd_l2_shared_l2_unmgd(
            vsd_l2dom_unmgd=vsd_l2dom_unmgd,
            # When I create an OS subnet with
            #   enable_dhcp == False
            #   a valid CIDR
            #   nuagenet == UUID of VSD-L2-domain
            os_shared_network=True,
            enable_dhcp=False,
            cidr=VALID_CIDR,
            gateway_ip='',

            # Then the OS subnet has
            #   an OS allocation pool covering the full CIDR range
            #   gateway_ip equal to None
            expected_gateway_ip=None,
            #   and no network:dhcp:nuage port
            expect_network_dhcp_nuage_port=False,

            # When I spin a VM in this network
            # Then the OS  VM-IPaddress is in the valid CIDR range
            # And the VMinterface-IPaddress in the VSD-L2-domain is empty
            expect_vm_ip_addresses_equal=''
        )

    @nuage_test.header()
    def test_vsd_l2_shared_unmgd_l2_unmgd_with_gateway_ip_neg(self):
        # Pass on Liberty, fail on kilo
        # Given  I have a VSD -L2-domain without IPAM (i.e. UnManaged)
        # And I have a VSD-L2-Shared-domain without IPAM (i.e. UnManaged)
        # And  these are linked
        vsd_l2dom_unmgd = self._given_vsdl2sharedunmgd_linkedto_vsdl2domunmgd()

        if CONF.nuage_sut.openstack_version == 'kilo':
            self.assertRaisesRegex(
                exceptions.ServerFault,
                "Details: create_subnet_postcommit failed.",
                self._check_vsd_l2_shared_l2_unmgd,
                vsd_l2dom_unmgd=vsd_l2dom_unmgd,
                os_shared_network=True,
                enable_dhcp=False,
                cidr=VALID_CIDR,
                gateway_ip=VALID_CIDR_GW
            )
        else:
            self._check_vsd_l2_shared_l2_unmgd(
                vsd_l2dom_unmgd=vsd_l2dom_unmgd,
                # When I create an OS subnet with
                #   enable_dhcp == False
                #   a valid CIDR
                #   nuagenet == UUID of VSD-L2-domain
                os_shared_network=True,
                enable_dhcp=False,
                gateway_ip=VALID_CIDR_GW,
                cidr=VALID_CIDR,

                # Then the OS subnet has
                #   an OS allocation pool covering the full CIDR range
                #   gateway_ip equal to None
                expected_gateway_ip=None,
                #   and no network:dhcp:nuage port
                expect_network_dhcp_nuage_port=False,

                # When I spin a VM in this network
                # Then the OS  VM-IPaddress is in the valid CIDR range
                # And the VMinterface-IPaddress in the VSD-L2-domain is empty
                expect_vm_ip_addresses_equal=''
            )

    @nuage_test.header()
    def test_vsd_l2_shared_unmgd_l2_unmgd_no_gateway(self):
        # Given  I have a VSD -L2-domain without IPAM (i.e. UnManaged)
        # And I have a VSD-L2-Shared-domain without IPAM (i.e. UnManaged)
        # And these are linked
        vsd_l2dom_unmgd = self._given_vsdl2sharedunmgd_linkedto_vsdl2domunmgd()
        self._check_vsd_l2_shared_l2_unmgd(
            vsd_l2dom_unmgd=vsd_l2dom_unmgd,
            # When I create an OS subnet with
            #     enable_dhcp == False
            #     a valid CIDR
            #     nuagenet == UUID of VSD-L2-domain
            #     no-gateway
            os_shared_network=True,
            enable_dhcp=False,
            cidr=VALID_CIDR,
            gateway_ip=None,

            # Then the OS subnet has
            # an OS allocation pool covering the full CIDR range
            # gateway_ip equal to None
            expected_gateway_ip=None,
            #   and no network:dhcp:nuage port
            expect_network_dhcp_nuage_port=False,

            # When I spin a VM in this network
            # Then the OS  VM-IPaddress is in the valid CIDR range
            # And the VMinterface-IPaddress in the VSD-L2-domain is empty
            expect_vm_ip_addresses_equal=''
        )

    @nuage_test.header()
    def test_vsd_l2_shared_mgd_l2_unmgd_without_gateway(self):
        # Given  I have a VSD -L2-domain without IPAM (i.e. UnManaged)
        # And I have a VSD-L2-Shared-domain without IPAM (i.e. UnManaged)
        # And  these are linked
        vsd_l2dom_unmgd = self._given_vsdl2sharedmgd_linkedto_vsdl2domunmgd()
        self._check_vsd_l2_shared_l2_unmgd(
            vsd_l2dom_unmgd=vsd_l2dom_unmgd,

            #  When I create an OS subnet with
            #   enable_dhcp == False
            #   a valid CIDR
            #   nuagenet == UUID of VSD-L2-domain
            os_shared_network=True,
            enable_dhcp=True,
            cidr=base_vsd_managed_networks.VSD_L2_SHARED_MGD_CIDR,
            gateway_ip='',

            # Then the OS subnet has
            #   an OS allocation pool covering the full CIDR range
            #   gateway_ip equal to None
            expected_gateway_ip=None,
            #   and no network:dhcp:nuage port
            expect_network_dhcp_nuage_port=False,

            # When I spin a VM in this network
            # Then the OS  VM-IPaddress is in the valid CIDR range
            # And the VMinterface-IPaddress in the VSD-L2-domain is empty
            expect_vm_ip_addresses_equal=True
        )

    @test.attr(type=['negative'])
    @nuage_test.header()
    def test_vsd_l2_shared_mgd_l2_unmgd_with_gateway_neg(self):
        # "Given  I have a VSD -L2-domain without IPAM (i.e. unmanaged)
        # And I have a VSD-L2-Shared-domain with IPAM (i.e. managed)
        # And these are linked
        # if the gateway_ip does not equal DHCP options 3, an error is thrown
        vsd_l2dom_unmgd = self._given_vsdl2sharedmgd_linkedto_vsdl2domunmgd()

        if CONF.nuage_sut.openstack_version == 'kilo':
            self.assertRaisesRegex(
                exceptions.ServerFault,
                "Details: create_subnet_postcommit failed.",
                self._check_vsd_l2_shared_l2_unmgd,
                vsd_l2dom_unmgd=vsd_l2dom_unmgd,
                os_shared_network=True,
                enable_dhcp=True,
                cidr=base_vsd_managed_networks.VSD_L2_SHARED_MGD_CIDR,
                gateway_ip=base_vsd_managed_networks.VSD_L2_SHARED_MGD_GW
            )
        else:
            # TODO: See OPENSTACK_1347 - ML2 liberty catches all exceptions
            # Only a failure is logged in neutron.log
            self._check_vsd_l2_shared_l2_unmgd(
            vsd_l2dom_unmgd=vsd_l2dom_unmgd,
            os_shared_network=True,
            enable_dhcp=True,
            cidr=base_vsd_managed_networks.VSD_L2_SHARED_MGD_CIDR,
            gateway_ip=base_vsd_managed_networks.VSD_L2_SHARED_MGD_GW)

    @nuage_test.header()
    def test_vsd_l2_shared_mgd_l2_unmgd_no_gateway(self):
        # Given I have a VSD -L2-domain without IPAM (i.e. unmanaged)
        # And I have a VSD-L2-Shared-domain with IPAM (i.e. managed)
        # And these are linked
        vsd_l2dom_unmgd = self._given_vsdl2sharedmgd_linkedto_vsdl2domunmgd()
        self._check_vsd_l2_shared_l2_unmgd(
            vsd_l2dom_unmgd=vsd_l2dom_unmgd,
            # When I create an OS subnet with
            #   enable_dhcp == True
            #   CIDR == CIDR of VSD-L2-Shared-domain
            #   nuagenet == UUID of VSD-L2-domain
            #   no-gateway
            os_shared_network=True,
            enable_dhcp=True,
            cidr=base_vsd_managed_networks.VSD_L2_SHARED_MGD_CIDR,
            gateway_ip=None,

            # Then the OS subnet has
            #   an OS allocation pool covering the full CIDR range
            #   gateway_ip equal to None
            expected_gateway_ip=None,
            #   and no network:dhcp:nuage port
            expect_network_dhcp_nuage_port=False,

            # When I spin a VM in this network
            # Then the OS  VM-IPaddress is in the CIDR range
            # And the VMinterface-IPaddress in the VSD-L2-domain equals the OS VM-IPaddress
            expect_vm_ip_addresses_equal=True
        )

    @nuage_test.header()
    def test_vsd_l2_shared_mgd_opt3_l2_unmgd_without_gateway(self):
        # Given  I have a VSD -L2-domain without IPAM (i.e. unmanaged)
        # And I have a VSD-L2-Shared-domain with IPAM (i.e. managed) with DHCP-option 3 set
        # And these are linked
        vsd_l2_dom_unmgd = self._given_vsdl2sharedmgdopt3_linkedto_vsdl2domunmgd(VSD_L2_SHARED_MGD_OPT3)
        self._check_vsd_l2_shared_l2_unmgd(
            vsd_l2_dom_unmgd,
            # When I create an OS subnet with
            #     enable_dhcp == True
            #     CIDR == CIDR of VSD-L2-Shared-domain
            #     nuagenet == UUID of VSD-L2-domain
            os_shared_network=True,
            enable_dhcp=True,
            cidr=VSD_L2_SHARED_MGD_OPT3_CIDR,
            gateway_ip='',

            # Then the OS subnet has
            # an OS allocation pool covering the full CIDR range except th gateway_ip
            # gateway_ip equal DHCP-options-3 of VSD-L2-Shared-domain
            expected_gateway_ip=VSD_L2_SHARED_MGD_OPT3,
            #   and no network:dhcp:nuage port
            expect_network_dhcp_nuage_port=False,

            # When I spin a VM in this network
            # Then the OS  VM-IPaddress is in the CIDR range
            # And the VMinterface-IPaddress in the VSD-L2-domain equals the OS VM-IPaddress
            expect_vm_ip_addresses_equal=True
        )

    @nuage_test.header()
    def test_vsd_l2_shared_mgd_opt3_l2_unmgd_with_gateway(self):
        # Given  I have a VSD -L2-domain without IPAM (i.e. unmanaged)
        # And I have a VSD-L2-Shared-domain with IPAM (i.e. managed) with DHCP-option 3 set
        # And  these are linked
        vsd_l2dom_unmgd = self._given_vsdl2sharedmgdopt3_linkedto_vsdl2domunmgd(VSD_L2_SHARED_MGD_OPT3)
        self._check_vsd_l2_shared_l2_unmgd(
            vsd_l2dom_unmgd=vsd_l2dom_unmgd,
            os_shared_network=True,

            # When I create an OS subnet with
            #  enable_dhcp == True
            #  CIDR == CIDR of VSD-L2-Shared-domain
            #  nuagenet == UUID of VSD-L2-domain
            #  gateway-ip == gateway-ip in DHCP-option-3
            enable_dhcp=True,
            cidr=VSD_L2_SHARED_MGD_OPT3_CIDR,
            gateway_ip=VSD_L2_SHARED_MGD_OPT3,

            # Then the OS subnet has
            #   an OS allocation pool covering the full CIDR range
            #   gateway_ip equal to DHCP-options-3 of VSD-L2-Shared-domain
            expected_gateway_ip=VSD_L2_SHARED_MGD_OPT3,
            #   and no network:dhcp:nuage port
            expect_network_dhcp_nuage_port=False,

            # When I spin a VM in this network
            # Then the OS  VM-IPaddress is in the CIDR range
            # And the VMinterface-IPaddress in the VSD-L2-domain equals the OS VM-IPaddress
            expect_vm_ip_addresses_equal=True
        )

    @nuage_test.header()
    @test.attr(type=['negative'])
    def test_vsd_l2_shared_mgd_opt3_l2_unmgd_no_gateway_neg(self):
        # Given  I have a VSD -L2-domain without IPAM (i.e. unmanaged)
        # And I have a VSD-L2-Shared-domain with IPAM (i.e. managed) with DHCP-option 3 set
        # And  these are linked
        vsd_l2dom_unmgd = self._given_vsdl2sharedmgdopt3_linkedto_vsdl2domunmgd(VSD_L2_SHARED_MGD_OPT3)

        self._check_vsd_l2_shared_l2_unmgd(
            vsd_l2dom_unmgd,
            os_shared_network=True,
            # When I try to create an OS subnet with
            # enable_dhcp == True
            # CIDR == CIDR of VSD-L2-Shared-domain
            # nuagenet == UUID of VSD-L2-domain
            # no-gateway
            enable_dhcp=True,
            cidr=VSD_L2_SHARED_MGD_OPT3_CIDR,
            gateway_ip=None,
            expected_gateway_ip=VSD_L2_SHARED_MGD_OPT3,
            expect_vm_ip_addresses_equal=True
        )

    @nuage_test.header()
    def test_vsd_l3_shared_mgd_l3_unmgd_without_gateway(self):
        # Given  I have a VSD -L3-domain in a public zone (i.e. without IPAM (/ UnManaged)
        # And I have a VSD-L3-Shared-domain with IPAM (i.e. Managed)
        # And  these are linked
        vsd_l3_unmgd_subnet = self._given_vsdl3sharedmgd_linkedto_vsdl2subnetunmgd()
        self._check_vsd_l3_shared_l2_unmgd(
            # When I create an OS subnet with
            #   enable_dhcp == True
            #   CIDR == CIDR of VSD-L3-Shared-domain
            #   nuagenet == UUID of VSD-L3-domain-public-zone-subnet
            vsd_l3_dom_subnet=vsd_l3_unmgd_subnet,
            os_shared_network=True,
            enable_dhcp=True,
            cidr=base_vsd_managed_networks.VSD_L3_SHARED_MGD_CIDR,
            gateway_ip='',

            # Then the OS subnet has
            #   a neutron port device_owner:network:dhcp:nuage
            #   an OS allocation pool covering the full CIDR range, except the VSD-L3-Shared gateway
            #   gateway_ip equal to gateway-ip of VSD-L3-Shared-domain
            expected_gateway_ip=base_vsd_managed_networks.VSD_L3_SHARED_MGD_GW,
            #   and no network:dhcp:nuage port
            expect_network_dhcp_nuage_port=False,

            # When I spin a VM in this network
            # Then the OS  VM-IPaddress is in the  CIDR range
            # And the VM_interface-IPaddress in the VSD-L3-domain equals the OS VM-IPaddress
            # And the VM_interface-IPaddress is different from the gateway_ip address
            expect_vm_ip_addresses_equal=True
        )

    @nuage_test.header()
    def test_vsd_l3_shared_mgd_l3_unmgd_with_gateway(self):
        # Given  I have a VSD -L3-domain without IPAM (i.e. UnManaged)
        # And I have a VSD-L3-Shared-domain with IPAM (i.e. Managed)
        # And  these are linked
        vsd_l3_unmgd_subnet = self._given_vsdl3sharedmgd_linkedto_vsdl2subnetunmgd()
        self._check_vsd_l3_shared_l2_unmgd(
            vsd_l3_dom_subnet=vsd_l3_unmgd_subnet,
            os_shared_network=True,

            # When I create an OS subnet with
            #   enable_dhcp == True
            #   CIDR == CIDR of VSD-L3-Shared-domain
            #   nuagenet == UUID of VSD-L3-domain
            #   gateway-ip == gateway-ip of VSD-L3-Shared-domain
            enable_dhcp=True,
            cidr=base_vsd_managed_networks.VSD_L3_SHARED_MGD_CIDR,
            gateway_ip=base_vsd_managed_networks.VSD_L3_SHARED_MGD_GW,

            # Then the OS subnet has
            #   a  neutron port device_owner:network:dhcp:nuage
            #   an OS allocation pool covering the full CIDR range (except the GW-ip)
            #   gateway_ip equal to gateway-ip of VSD-L3-Shared-domain
            expected_gateway_ip=base_vsd_managed_networks.VSD_L3_SHARED_MGD_GW,
            #   and no network:dhcp:nuage port
            expect_network_dhcp_nuage_port=False,

            # When I spin a VM in this network
            # Then the OS  VM-IPaddress is in the CIDR range
            # And the VM_interface-IPaddress in the VSD-L3-domain equals the OS VM-IPaddress
            # And the OS VM-IPaddress is different from the gateway-ip
            expect_vm_ip_addresses_equal=True
        )

#############################################################

    @nuage_test.header()
    def test_vsd_l3_shared_mgd_l3_unmgd_no_gateway(self):
        # Given  I have a VSD -L3-domain without IPAM (i.e. UnManaged)
        # And I have a VSD-L3-Shared-domain with IPAM (i.e. Managed)
        # And  these are linked
        vsd_l3_unmgd_subnet = self._given_vsdl3sharedmgd_linkedto_vsdl2subnetunmgd()

        self._check_vsd_l3_shared_l2_unmgd(
            vsd_l3_dom_subnet=vsd_l3_unmgd_subnet,
            os_shared_network=True,
            # When I try to create an OS subnet with
            #   enable_dhcp == True
            #   CIDR == CIDR of VSD-L3-Shared-domain
            #   nuagenet == UUID of VSD-L3-domain
            #   no-gateway
            enable_dhcp=True,
            cidr=base_vsd_managed_networks.VSD_L3_SHARED_MGD_CIDR,
            gateway_ip=None,

            # Then the OS subnet has
            #   an OS allocation pool covering the full CIDR range (except the GW-ip)
            #   gateway_ip equal to gateway-ip of VSD-L3-Shared-domain
            expected_gateway_ip=base_vsd_managed_networks.VSD_L3_SHARED_MGD_GW,
            #   and no network:dhcp:nuage port
            expect_network_dhcp_nuage_port=False,

            # When I spin a VM in this network
            # Then the OS  VM-IPaddress is in the CIDR range
            # And the VM_interface-IPaddress in the VSD-L3-domain equals the OS VM-IPaddress
            # And the OS VM-IPaddress is different from the gateway-ip
            expect_vm_ip_addresses_equal=True
        )

    @nuage_test.header()
    def test_vsd_l3_shared_mgd_opt3_l2_unmgd_without_gateway(self):
        # Given  I have a VSD -L3-domain in a public zone (i.e. without IPAM (/ UnManaged)
        # And I have a VSD-L3-Shared-domain with IPAM (i.e. Managed) with DHCP option 3
        # And  these are linked
        vsd_l3_unmgd_subnet = self._given_vsdl3sharedmgdopt3_linkedto_vsdl3subnetunmgd(VSD_L3_SHARED_MGD_OPT3)
        self._check_vsd_l3_shared_l2_unmgd(
            vsd_l3_dom_subnet=vsd_l3_unmgd_subnet,
            os_shared_network=True,
            # When I create an OS subnet with
            #   enable_dhcp == True
            #   CIDR == CIDR of VSD-L3-Shared-domain
            #   nuagenet == UUID of VSD-L3-domain-public-zone-subnet
            enable_dhcp=True,
            cidr=VSD_L3_SHARED_MGD_OPT3_CIDR,
            gateway_ip='',

            # Then the OS subnet has
            #   an OS allocation pool covering the full CIDR range, except the VSD-L3-Shared gateway
            #   gateway_ip equal to gateway-ip of VSD-L3-Shared-domain
            expected_gateway_ip=VSD_L3_SHARED_MGD_OPT3_GW,
            #   and no network:dhcp:nuage port
            expect_network_dhcp_nuage_port=False,

            # When I spin a VM in this network
            # Then the OS  VM-IPaddress is in the  CIDR range
            # And the VM_interface-IPaddress in the VSD-L3-domain equals the OS VM-IPaddress
            # And the VM_interface-IPaddress is different from the gateway_ip address
            expect_vm_ip_addresses_equal=True
        )

    @nuage_test.header()
    def test_vsd_l3_shared_mgd_opt3_l2_unmgd_with_gateway(self):
        # Given  I have a VSD -L3-domain without IPAM (i.e. UnManaged)
        # And I have a VSD-L3-Shared-domain with IPAM (i.e. Managed) with DHCP-options-3
        # And  these are linked
        vsd_l3_unmgd_subnet = self._given_vsdl3sharedmgdopt3_linkedto_vsdl3subnetunmgd(VSD_L3_SHARED_MGD_OPT3)
        self._check_vsd_l3_shared_l2_unmgd(
            vsd_l3_dom_subnet=vsd_l3_unmgd_subnet,
            os_shared_network=True,

            # When I create an OS subnet with
            #   enable_dhcp == True
            #   CIDR == CIDR of VSD-L3-Shared-domain
            #   nuagenet == UUID of VSD-L3-domain
            #   gateway-ip == gateway-ip of VSD-L3-Shared-domain
            enable_dhcp=True,
            cidr=VSD_L3_SHARED_MGD_OPT3_CIDR,
            gateway_ip=VSD_L3_SHARED_MGD_OPT3_GW,

            # Then the OS subnet has
            #   an OS allocation pool covering the full CIDR range (except the GW-ip)
            #   gateway_ip equal to gateway-ip of VSD-L3-Shared-domain
            expected_gateway_ip=VSD_L3_SHARED_MGD_OPT3_GW,
            #   and no network:dhcp:nuage port
            expect_network_dhcp_nuage_port=False,

            # When I spin a VM in this network
            # Then the OS  VM-IPaddress is in the CIDR range
            # And the VM_interface-IPaddress in the VSD-L3-domain equals the OS VM-IPaddress
            # And the OS VM-IPaddress is different from the gateway-ip
            expect_vm_ip_addresses_equal=True
        )

    @nuage_test.header()
    def test_vsd_l3_shared_mgd_opt3_l2_unmgd_no_gateway(self):
        # Given  I have a VSD -L3-domain without IPAM (i.e. UnManaged)
        # And I have a VSD-L3-Shared-domain with IPAM (i.e. Managed) with DHCP-options-3
        # And  these are linked
        vsd_l3_unmgd_subnet = self._given_vsdl3sharedmgdopt3_linkedto_vsdl3subnetunmgd(VSD_L3_SHARED_MGD_OPT3)

        self._check_vsd_l3_shared_l2_unmgd(
            vsd_l3_dom_subnet=vsd_l3_unmgd_subnet,
            os_shared_network=True,
            # When I try to create an OS subnet with
            #   enable_dhcp == True
            #   CIDR == CIDR of VSD-L3-Shared-domain
            #   nuagenet == UUID of VSD-L3-domain
            #   no-gateway
            # Then I expect a failure indicating gateway IP mismatch
            enable_dhcp=True,
            cidr=VSD_L3_SHARED_MGD_OPT3_CIDR,
            gateway_ip=None,

            # Then the OS subnet has
            #   an OS allocation pool covering the full CIDR range (except the GW-ip)
            #   gateway_ip equal to gateway-ip of VSD-L3-Shared-domain
            expected_gateway_ip=VSD_L3_SHARED_MGD_OPT3_GW,
            #   and no network:dhcp:nuage port
            expect_network_dhcp_nuage_port=False,

            # When I spin a VM in this network
            # Then the OS  VM-IPaddress is in the CIDR range
            # And the VM_interface-IPaddress in the VSD-L3-domain equals the OS VM-IPaddress
            # And the OS VM-IPaddress is different from the gateway-ip
            expect_vm_ip_addresses_equal=True
        )

    ################################################################################################################
    ################################################################################################################
    # Negative testcases
    ################################################################################################################
    ################################################################################################################

    @test.attr(type=['negative'])
    @nuage_test.header()
    def test_vsd_l2_shared_unmgd_l2_unmgd_wo_gw_enable_dhcp_not_false_neg(self):
        # Given I have a VSD -L2-domain without IPAM (i.e. unmanaged)
        # And I have a VSD-L2-Shared-domain without IPAM (i.e. UnManaged)
        # And these are linked
        vsd_l2dom = self._given_vsdl2sharedunmgd_linkedto_vsdl2domunmgd()

        self.assertRaisesRegex(
            exceptions.ServerFault,
            "Details: create_subnet_postcommit failed.",

            self._check_vsd_l2_shared_l2_unmgd,
            vsd_l2dom_unmgd=vsd_l2dom,
            os_shared_network=True,
            # When I try to create an OS subnet with
            #   enable_dhcp == True
            #   CIDR == CIDR of VSD-L3-Shared-domain
            #   nuagenet == UUID of VSD-L3-domain
            enable_dhcp=True,
            cidr=VALID_CIDR,
            gateway_ip=''

            # Then I expect a failure from OS ML2 driver
        )

    @test.attr(type=['negative'])
    @nuage_test.header()
    def test_vsd_l2_shared_unmgd_l2_unmgd_with_gw_enable_dhcp_not_false_neg(self):
        # Given I have a VSD -L2-domain without IPAM (i.e. unmanaged)
        # And I have a VSD-L2-Shared-domain without IPAM (i.e. UnManaged)
        # And these are linked
        vsd_l2dom = self._given_vsdl2sharedunmgd_linkedto_vsdl2domunmgd()

        self.assertRaisesRegex(
            exceptions.ServerFault,
            "Details: create_subnet_postcommit failed.",

            self._check_vsd_l2_shared_l2_unmgd,
            vsd_l2dom_unmgd=vsd_l2dom,
            os_shared_network=True,

            # When I try to create an OS subnet with
            #   enable_dhcp == True
            #   CIDR == CIDR of VSD-L3-Shared-domain
            #   nuagenet == UUID of VSD-L3-domain
            #   gateway_ip in CIDR
            enable_dhcp=True,
            cidr=base_vsd_managed_networks.VSD_L2_SHARED_MGD_CIDR,
            gateway_ip=base_vsd_managed_networks.VSD_L2_SHARED_MGD_GW

            # Then I expect a failure from OS ML2 driver
        )

    @test.attr(type=['negative'])
    @nuage_test.header()
    def test_vsd_l2_shared_unmgd_l2_unmgd_no_gw_enable_dhcp_not_false_neg(self):
        # Given I have a VSD -L2-domain without IPAM (i.e. unmanaged)
        # And I have a VSD-L2-Shared-domain without IPAM (i.e. UnManaged)
        # And these are linked
        vsd_l2dom = self._given_vsdl2sharedunmgd_linkedto_vsdl2domunmgd()

        self.assertRaisesRegex(
            exceptions.ServerFault,
            "Details: create_subnet_postcommit failed.",

            self._check_vsd_l2_shared_l2_unmgd,
            vsd_l2dom_unmgd=vsd_l2dom,
            os_shared_network=True,

            # When I try to create an OS subnet with
            #   enable_dhcp == False
            #   CIDR == CIDR of VSD-L3-Shared-domain
            #   nuagenet == UUID of VSD-L3-domain
            #   no gateway
            enable_dhcp=True,
            cidr=base_vsd_managed_networks.VSD_L2_SHARED_MGD_CIDR,
            gateway_ip=None,

            # Then I expect a failure from OS ML2 driver
        )

    @test.attr(type=['negative'])
    @nuage_test.header()
    def test_vsd_l2_shared_mgd_l2_unmgd_wo_gw_enable_dhcp_not_false_neg(self):
        # Given I have a VSD -L2-domain without IPAM (i.e. unmanaged)
        # And I have a VSD-L2-Shared-domain with IPAM (i.e. managed)
        #     And these are linked
        vsd_l2dom = self._given_vsdl2sharedmgd_linkedto_vsdl2domunmgd()

        self.assertRaisesRegex(
            exceptions.ServerFault,
            "Details: create_subnet_postcommit failed.",

            self._check_vsd_l2_shared_l2_unmgd,
            vsd_l2dom_unmgd=vsd_l2dom,
            os_shared_network=True,

            # When I try to create an OS subnet with
            #   enable_dhcp == True
            #   CIDR == CIDR of VSD-L3-Shared-domain
            #   nuagenet == UUID of VSD-L3-domain
            enable_dhcp=False,
            cidr=base_vsd_managed_networks.VSD_L2_SHARED_MGD_CIDR,
            gateway_ip=''

            # Then I expect a failure from OS ML2 driver
        )

    @test.attr(type=['negative'])
    @nuage_test.header()
    def test_vsd_l2_shared_mgd_l2_unmgd_with_gw_enable_dhcp_false_neg(self):
        # Given I have a VSD -L2-domain without IPAM (i.e. unmanaged)
        # And I have a VSD-L2-Shared-domain with IPAM (i.e. managed)
        #     And these are linked
        vsd_l2dom = self._given_vsdl2sharedmgd_linkedto_vsdl2domunmgd()

        self.assertRaisesRegex(
            exceptions.ServerFault,
            "Details: create_subnet_postcommit failed.",

            self._check_vsd_l2_shared_l2_unmgd,
            vsd_l2dom_unmgd=vsd_l2dom,
            os_shared_network=True,

            # When I try to create an OS subnet with
            #   enable_dhcp == True
            #   CIDR == CIDR of VSD-L3-Shared-domain
            #   nuagenet == UUID of VSD-L3-domain
            #   gateway_ip in CIDR
            enable_dhcp=False,
            cidr=base_vsd_managed_networks.VSD_L2_SHARED_MGD_CIDR,
            gateway_ip=base_vsd_managed_networks.VSD_L2_SHARED_MGD_GW

            # Then I expect a failure from OS ML2 driver
        )

    @test.attr(type=['negative'])
    @nuage_test.header()
    def test_vsd_l2_shared_mgd_l2_unmgd_no_gw_enable_dhcp_false_neg(self):
        # Given I have a VSD -L2-domain without IPAM (i.e. unmanaged)
        # And I have a VSD-L2-Shared-domain with IPAM (i.e. managed)
        #     And these are linked
        vsd_l2dom = self._given_vsdl2sharedmgd_linkedto_vsdl2domunmgd()

        self.assertRaisesRegex(
            exceptions.ServerFault,
            "Details: create_subnet_postcommit failed.",

            self._check_vsd_l2_shared_l2_unmgd,
            vsd_l2dom_unmgd=vsd_l2dom,
            os_shared_network=True,

            # When I try to create an OS subnet with
            #   enable_dhcp == True
            #   CIDR == CIDR of VSD-L3-Shared-domain
            #   nuagenet == UUID of VSD-L3-domain
            #   no gateway
            enable_dhcp=False,
            cidr=base_vsd_managed_networks.VSD_L2_SHARED_MGD_CIDR,
            gateway_ip=None

            # Then I expect a failure from OS ML2 driver
        )

    @test.attr(type=['negative'])
    @nuage_test.header()
    def test_vsd_l2_shared_mgd_l2_unmgd_wo_gw_cidr_mismatch_neg(self):
        # Given I have a VSD -L2-domain without IPAM (i.e. unmanaged)
        # And I have a VSD-L2-Shared-domain with IPAM (i.e. managed)
        # And these are linked
        vsd_l2dom = self._given_vsdl2sharedmgd_linkedto_vsdl2domunmgd()

        self.assertRaisesRegex(
            exceptions.ServerFault,
            "Details: create_subnet_postcommit failed.",

            self._check_vsd_l2_shared_l2_unmgd,
            vsd_l2dom_unmgd=vsd_l2dom,
            os_shared_network=True,

            # When I try to create an OS subnet with
            #   enable_dhcp == True
            #   CIDR != CIDR of VSD-L2-Shared-domain
            #   nuagenet == UUID of VSD-L3-domain
            enable_dhcp=True,
            cidr=VALID_CIDR,
            gateway_ip=''

            # Then I expect a failure from OS ML2 driver
        )

    @test.attr(type=['negative'])
    @nuage_test.header()
    def test_vsd_l2_shared_mgd_l2_unmgd_with_gw_cidr_mismatch_neg(self):
        # Given I have a VSD -L2-domain without IPAM (i.e. unmanaged)
        # And I have a VSD-L2-Shared-domain with IPAM (i.e. managed)
        # And these are linked
        vsd_l2dom = self._given_vsdl2sharedmgd_linkedto_vsdl2domunmgd()

        self.assertRaisesRegex(
            exceptions.ServerFault,
            "Details: create_subnet_postcommit failed.",
            self._check_vsd_l2_shared_l2_unmgd,
            vsd_l2dom_unmgd=vsd_l2dom,
            os_shared_network=True,

            # When I try to create an OS subnet with
            #   enable_dhcp == True
            #   CIDR != CIDR of VSD-L2-Shared-domain
            #   nuagenet == UUID of VSD-L3-domain
            #   gateway ip in the wrong CIDR
            enable_dhcp=True,
            cidr=VALID_CIDR,
            gateway_ip=VALID_CIDR_GW

            # Then I expect a failure from OS ML2 driver
        )

    @test.attr(type=['negative'])
    @nuage_test.header()
    def test_vsd_l2_shared_mgd_l2_no_gw_unmgd_cidr_mismatch_neg(self):
        # Given I have a VSD -L2-domain without IPAM (i.e. unmanaged)
        # And I have a VSD-L2-Shared-domain with IPAM (i.e. managed)
        # And these are linked
        vsd_l2dom = self._given_vsdl2sharedmgd_linkedto_vsdl2domunmgd()

        self.assertRaisesRegex(
            exceptions.ServerFault,
            "Details: create_subnet_postcommit failed.",
            self._check_vsd_l2_shared_l2_unmgd,
            vsd_l2dom_unmgd=vsd_l2dom,
            os_shared_network=True,

            # When I try to create an OS subnet with
            #   enable_dhcp == True
            #   CIDR != CIDR of VSD-L2-Shared-domain
            #   nuagenet == UUID of VSD-L3-domain
            #   no gateway
            enable_dhcp=True,
            cidr=VALID_CIDR,
            gateway_ip=None

            # Then I expect a failure from OS ML2 driver
        )
        pass

    @test.attr(type=['negative'])
    @nuage_test.header()
    def test_vsd_l2_shared_mgd_opt3_l2_unmgd_wo_gw_enable_dhcp_not_true_neg(self):
        # Given I have a VSD -L2-domain without IPAM (i.e. unmanaged)
        # And I have a VSD-L2-Shared-domain with IPAM (i.e. managed) with DHCP-option 3 set
        # And these are linked
        vsd_l2dom = self._given_vsdl2sharedmgdopt3_linkedto_vsdl2domunmgd(VSD_L2_SHARED_MGD_OPT3)

        self.assertRaisesRegex(
            exceptions.ServerFault,
            "Details: create_subnet_postcommit failed.",
            self._check_vsd_l2_shared_l2_unmgd,
            vsd_l2dom_unmgd=vsd_l2dom,
            os_shared_network=True,

            # When I try to create an OS subnet with
            #   enable_dhcp == False
            #   CIDR == CIDR of VSD-L3-Shared-domain
            #   nuagenet == UUID of VSD-L3-domain
            enable_dhcp=False,
            cidr=VSD_L2_SHARED_MGD_OPT3_CIDR,
            gateway_ip=''

            # Then I expect a failure from OS ML2 driver
        )

    @test.attr(type=['negative'])
    @nuage_test.header()
    def test_vsd_l2_shared_mgd_opt_3_l2_unmgd_with_gw_enable_dhcp_not_true_neg(self):
        # Given I have a VSD -L2-domain without IPAM (i.e. unmanaged)
        # And I have a VSD-L2-Shared-domain with IPAM (i.e. managed) with DHCP-option 3 set
        # And these are linked
        vsd_l2dom = self._given_vsdl2sharedmgdopt3_linkedto_vsdl2domunmgd(VSD_L2_SHARED_MGD_OPT3)

        self.assertRaisesRegex(
            exceptions.ServerFault,
            "Details: create_subnet_postcommit failed.",
            self._check_vsd_l2_shared_l2_unmgd,
            vsd_l2dom_unmgd=vsd_l2dom,
            os_shared_network=True,

            # When I try to create an OS subnet with
            # enable_dhcp == False
            # CIDR == CIDR of VSD-L2-Shared-domain
            # nuagenet == UUID of VSD-L2-domain
            # gateway-ip == gateway-ip in DHCP-option-3
            enable_dhcp=False,
            cidr=VSD_L2_SHARED_MGD_OPT3_CIDR,
            gateway_ip=VSD_L2_SHARED_MGD_OPT3_GW

            # Then I expect a failure from OS ML2 driver
        )

    @test.attr(type=['negative'])
    @nuage_test.header()
    def test_vsd_l2_shared_mgd_opt_3_l2_unmgd_no_gw_enable_dhcp_not_true_neg(self):
        # Given I have a VSD -L2-domain without IPAM (i.e. unmanaged)
        # And I have a VSD-L2-Shared-domain with IPAM (i.e. managed) with DHCP-option 3 set
        # And these are linked
        vsd_l2dom = self._given_vsdl2sharedmgdopt3_linkedto_vsdl2domunmgd(VSD_L2_SHARED_MGD_OPT3)

        self.assertRaisesRegex(
            exceptions.ServerFault,
            "Details: create_subnet_postcommit failed.",
            self._check_vsd_l2_shared_l2_unmgd,
            vsd_l2dom_unmgd=vsd_l2dom,
            os_shared_network=True,

            # When I try to create an OS subnet with
            # enable_dhcp == False
            # CIDR == CIDR of VSD-L2-Shared-domain
            # nuagenet == UUID of VSD-L2-domain
            # no gateway
            enable_dhcp=False,
            cidr=VSD_L2_SHARED_MGD_OPT3_CIDR,
            gateway_ip=None

            # Then I expect a failure from OS ML2 driver
        )

    @test.attr(type=['negative'])
    @nuage_test.header()
    def test_vsd_l2_shared_mgd_opt_3_l2_unmgd_wo_gw_cidr_mismatch_neg(self):
        # Given I have a VSD -L2-domain without IPAM (i.e. unmanaged)
        # And I have a VSD-L2-Shared-domain with IPAM (i.e. managed) with DHCP-option 3 set
        # And these are linked
        vsd_l2dom = self._given_vsdl2sharedmgdopt3_linkedto_vsdl2domunmgd(VSD_L2_SHARED_MGD_OPT3)

        self.assertRaisesRegex(
            exceptions.ServerFault,
            "Details: create_subnet_postcommit failed.",
            self._check_vsd_l2_shared_l2_unmgd,
            vsd_l2dom_unmgd=vsd_l2dom,
            os_shared_network=True,

            # When I try to create an OS subnet with
            #   enable_dhcp == True
            #   CIDR != CIDR of VSD-L2-Shared-domain
            #   nuagenet == UUID of VSD-L3-domain
            enable_dhcp=True,
            cidr=VALID_CIDR,
            gateway_ip=''

            # Then I expect a failure from OS ML2 driver
        )

    @test.attr(type=['negative'])
    @nuage_test.header()
    def test_vsd_l2_shared_mgd_opt_3_l2_unmgd_with_gw_cidr_mismatch_neg(self):
        # Given I have a VSD -L2-domain without IPAM (i.e. unmanaged)
        # And I have a VSD-L2-Shared-domain with IPAM (i.e. managed) with DHCP-option 3 set
        # And these are linked
        vsd_l2dom = self._given_vsdl2sharedmgdopt3_linkedto_vsdl2domunmgd(VSD_L2_SHARED_MGD_OPT3)

        self.assertRaisesRegex(
            exceptions.ServerFault,
            "Details: create_subnet_postcommit failed.",
            self._check_vsd_l2_shared_l2_unmgd,
            vsd_l2dom_unmgd=vsd_l2dom,
            os_shared_network=True,

            # When I try to create an OS subnet with
            #   enable_dhcp == True
            #   CIDR != CIDR of VSD-L2-Shared-domain
            #   nuagenet == UUID of VSD-L3-domain
            #   gateway ip in the wrong CIDR
            enable_dhcp=True,
            cidr=VALID_CIDR,
            gateway_ip=VALID_CIDR_GW

            # Then I expect a failure from OS ML2 driver
        )

    @test.attr(type=['negative'])
    @nuage_test.header()
    def test_vsd_l2_shared_mgd_opt_3_l2_unmgd_no_gw_cidr_mismatch_neg(self):
        # Given I have a VSD -L2-domain without IPAM (i.e. unmanaged)
        # And I have a VSD-L2-Shared-domain with IPAM (i.e. managed) with DHCP-option 3 set
        # And these are linked
        vsd_l2dom = self._given_vsdl2sharedmgdopt3_linkedto_vsdl2domunmgd(VSD_L2_SHARED_MGD_OPT3)

        self.assertRaisesRegex(
            exceptions.ServerFault,
            "Details: create_subnet_postcommit failed.",
            self._check_vsd_l2_shared_l2_unmgd,
            vsd_l2dom_unmgd=vsd_l2dom,
            os_shared_network=True,

            # When I try to create an OS subnet with
            #   enable_dhcp == True
            #   CIDR != CIDR of VSD-L2-Shared-domain
            #   nuagenet == UUID of VSD-L3-domain
            #   no gateway
            enable_dhcp=True,
            cidr=VALID_CIDR,
            gateway_ip=None

            # Then I expect a failure from OS ML2 driver
        )

    @nuage_test.header()
    def test_vsd_l3_shared_mgd_l3_unmgd_no_gateway(self):
        # Given  I have a VSD -L3-domain without IPAM (i.e. UnManaged)
        # And I have a VSD-L3-Shared-domain with IPAM (i.e. Managed)
        # And  these are linked
        vsd_l3_unmgd_subnet = self._given_vsdl3sharedmgd_linkedto_vsdl2subnetunmgd()

        self._check_vsd_l3_shared_l2_unmgd(
            vsd_l3_dom_subnet=vsd_l3_unmgd_subnet,
            os_shared_network=True,
            # When I try to create an OS subnet with
            #   enable_dhcp == True
            #   CIDR == CIDR of VSD-L3-Shared-domain
            #   nuagenet == UUID of VSD-L3-domain
            #   no-gateway
            enable_dhcp=True,
            cidr=base_vsd_managed_networks.VSD_L3_SHARED_MGD_CIDR,
            gateway_ip=None,

            # Then the OS subnet has
            #   a  neutron port device_owner:network:dhcp:nuage
            #   an OS allocation pool covering the full CIDR range (except the GW-ip)
            #   gateway_ip equal to gateway-ip of VSD-L3-Shared-domain
            expected_gateway_ip=base_vsd_managed_networks.VSD_L3_SHARED_MGD_GW,
            #   and no network:dhcp:nuage port
            expect_network_dhcp_nuage_port=False,

            # When I spin a VM in this network
            # Then the OS  VM-IPaddress is in the CIDR range
            # And the VM_interface-IPaddress in the VSD-L3-domain equals the OS VM-IPaddress
            # And the OS VM-IPaddress is different from the gateway-ip
            expect_vm_ip_addresses_equal=True
        )

    @test.attr(type=['negative'])
    @nuage_test.header()
    def test_vsd_l3_shared_mgd_l3_unmgd_wo_gw_enable_dhcp_not_true_neg(self):
        # Given  I have a VSD -L3-domain without IPAM (i.e. UnManaged)
        # And I have a VSD-L3-Shared-domain with IPAM (i.e. Managed) with dhcp options 3
        # And  these are linked
        vsd_l3_unmgd_subnet = self._given_vsdl3sharedmgd_linkedto_vsdl2subnetunmgd()

        self.assertRaisesRegex(
            exceptions.ServerFault,
            "Details: create_subnet_postcommit failed.",

            self._check_vsd_l3_shared_l2_unmgd,
            vsd_l3_dom_subnet=vsd_l3_unmgd_subnet,
            os_shared_network=True,

            # When I try to create an OS subnet with
            #   enable_dhcp == False
            #   CIDR == CIDR of VSD-L3-Shared-domain
            #   nuagenet == UUID of VSD-L3-domain
            # Then I expect a failure indicating enable dhcp may not be false
            enable_dhcp=False,
            cidr=base_vsd_managed_networks.VSD_L3_SHARED_MGD_CIDR,
            gateway_ip=''

            # Then I expect a failure from OS ML2 driver
        )

    @test.attr(type=['negative'])
    @nuage_test.header()
    def test_vsd_l3_shared_mgd_l3_unmgd_with_gw_enable_dhcp_not_true_neg(self):
        # Given  I have a VSD -L3-domain without IPAM (i.e. UnManaged)
        # And I have a VSD-L3-Shared-domain with IPAM (i.e. Managed) with dhcp options 3
        # And  these are linked
        vsd_l3_unmgd_subnet = self._given_vsdl3sharedmgd_linkedto_vsdl2subnetunmgd()

        self.assertRaisesRegex(
            exceptions.ServerFault,
            "Details: create_subnet_postcommit failed.",

            self._check_vsd_l3_shared_l2_unmgd,
            vsd_l3_dom_subnet=vsd_l3_unmgd_subnet,
            os_shared_network=True,

            # When I try to create an OS subnet with
            #   enable_dhcp == False
            #   CIDR == CIDR of VSD-L3-Shared-domain
            #   nuagenet == UUID of VSD-L3-domain
            #   gateway_ip in CIDR
            enable_dhcp=False,
            cidr=base_vsd_managed_networks.VSD_L3_SHARED_MGD_CIDR,
            gateway_ip=base_vsd_managed_networks.VSD_L3_SHARED_MGD_GW

            # Then I expect a failure from OS ML2 driver
        )

    @test.attr(type=['negative'])
    @nuage_test.header()
    def test_vsd_l3_shared_mgd_l3_unmgd_no_gw_enable_dhcp_not_true_neg(self):
        # Given  I have a VSD -L3-domain without IPAM (i.e. UnManaged)
        # And I have a VSD-L3-Shared-domain with IPAM (i.e. Managed) with dhcp options 3
        # And  these are linked
        vsd_l3_unmgd_subnet = self._given_vsdl3sharedmgd_linkedto_vsdl2subnetunmgd()

        self.assertRaisesRegex(
            exceptions.ServerFault,
            "Details: create_subnet_postcommit failed.",

            self._check_vsd_l3_shared_l2_unmgd,
            vsd_l3_dom_subnet=vsd_l3_unmgd_subnet,
            os_shared_network=True,

            # When I try to create an OS subnet with
            #   enable_dhcp == False
            #   CIDR == CIDR of VSD-L3-Shared-domain
            #   nuagenet == UUID of VSD-L3-domain
            #   no gateway
            enable_dhcp=False,
            cidr=base_vsd_managed_networks.VSD_L3_SHARED_MGD_CIDR,
            gateway_ip=None

            # Then I expect a failure from OS ML2 driver
        )

    @test.attr(type=['negative'])
    @nuage_test.header()
    def test_vsd_l3_shared_mgd_opt3_l3_unmgd_wo_gw_enable_dhcp_not_true_neg(self):
        # Given  I have a VSD -L3-domain without IPAM (i.e. UnManaged)
        # And I have a VSD-L3-Shared-domain with IPAM (i.e. Managed) with dhcp options 3
        # And  these are linked
        vsd_l3_unmgd_subnet = self._given_vsdl3sharedmgdopt3_linkedto_vsdl3subnetunmgd(VSD_L3_SHARED_MGD_OPT3)

        self.assertRaisesRegex(
            exceptions.ServerFault,
            "Details: create_subnet_postcommit failed.",

            self._check_vsd_l3_shared_l2_unmgd,
            vsd_l3_dom_subnet=vsd_l3_unmgd_subnet,
            os_shared_network=True,

            # When I try to create an OS subnet with
            #   enable_dhcp == False
            #   CIDR == CIDR of VSD-L3-Shared-domain
            #   nuagenet == UUID of VSD-L3-domain
            enable_dhcp=False,
            cidr=VSD_L3_SHARED_MGD_OPT3_CIDR,
            gateway_ip=''

            # Then I expect a failure from OS ML2 driver
        )

    @test.attr(type=['negative'])
    @nuage_test.header()
    def test_vsd_l3_shared_mgd_opt3_l3_unmgd_with_gw_enable_dhcp_not_true_neg(self):
        # Given  I have a VSD -L3-domain without IPAM (i.e. UnManaged)
        # And I have a VSD-L3-Shared-domain with IPAM (i.e. Managed)
        # And  these are linked
        vsd_l3_unmgd_subnet = self._given_vsdl3sharedmgdopt3_linkedto_vsdl3subnetunmgd(VSD_L3_SHARED_MGD_OPT3)

        self.assertRaisesRegex(
            exceptions.ServerFault,
            "Details: create_subnet_postcommit failed.",

            self._check_vsd_l3_shared_l2_unmgd,
            vsd_l3_dom_subnet=vsd_l3_unmgd_subnet,
            os_shared_network=True,
            # When I try to create an OS subnet with
            #   enable_dhcp == False
            #   CIDR == CIDR of VSD-L3-Shared-domain
            #   nuagenet == UUID of VSD-L3-domain
            #   gateway_ip in CIDR
            enable_dhcp=False,
            cidr=VSD_L3_SHARED_MGD_OPT3_CIDR,
            gateway_ip=VSD_L3_SHARED_MGD_OPT3_GW

            # Then I expect a failure from OS ML2 driver
        )

    @test.attr(type=['negative'])
    @nuage_test.header()
    def test_vsd_l3_shared_mgd_op3_l3_unmgd_no_gw_enable_dhcp_not_true_neg(self):
        # Given  I have a VSD -L3-domain without IPAM (i.e. UnManaged)
        # And I have a VSD-L3-Shared-domain with IPAM (i.e. Managed)
        # And  these are linked
        vsd_l3_unmgd_subnet = self._given_vsdl3sharedmgdopt3_linkedto_vsdl3subnetunmgd(VSD_L3_SHARED_MGD_OPT3)

        self.assertRaisesRegex(
            exceptions.ServerFault,
            "Details: create_subnet_postcommit failed.",

            self._check_vsd_l3_shared_l2_unmgd,
            vsd_l3_dom_subnet=vsd_l3_unmgd_subnet,
            os_shared_network=True,

            # When I try to create an OS subnet with
            #   enable_dhcp == False
            #   CIDR == CIDR of VSD-L3-Shared-domain
            #   nuagenet == UUID of VSD-L3-domain
            #   gateway_ip in CIDR
            # Then I expect a failure indicating enable dhcp may not be false
            enable_dhcp=False,
            cidr=VSD_L3_SHARED_MGD_OPT3_CIDR,
            gateway_ip=None

            # Then I expect a failure from OS ML2 driver
        )


    @test.attr(type=['negative'])
    @nuage_test.header()
    def test_vsd_l3_shared_mgd_l3_unmgd_wo_gw_cidr_mismatch_neg(self):
        # Given  I have a VSD -L3-domain without IPAM (i.e. UnManaged)
        # And I have a VSD-L3-Shared-domain with IPAM (i.e. Managed) with dhcp options 3
        # And  these are linked
        vsd_l3_unmgd_subnet = self._given_vsdl3sharedmgd_linkedto_vsdl2subnetunmgd()

        self.assertRaisesRegex(
            exceptions.ServerFault,
            "Details: create_subnet_postcommit failed.",

            self._check_vsd_l3_shared_l2_unmgd,
            vsd_l3_dom_subnet=vsd_l3_unmgd_subnet,
            os_shared_network=True,

            # When I try to create an OS subnet with
            #   enable_dhcp == True
            #   CIDR != CIDR of VSD-L3-Shared-domain
            #   nuagenet == UUID of VSD-L3-domain
            # Then I expect a failure indicating enable dhcp may not be false
            enable_dhcp=True,
            cidr=VALID_CIDR,
            gateway_ip=''

            # Then I expect a failure from OS ML2 driver
        )

    @test.attr(type=['negative'])
    @nuage_test.header()
    def test_vsd_l3_shared_mgd_l3_unmgd_with_gw_cidr_mismatch_neg(self):
        # Given  I have a VSD -L3-domain without IPAM (i.e. UnManaged)
        # And I have a VSD-L3-Shared-domain with IPAM (i.e. Managed) with dhcp options 3
        # And  these are linked
        vsd_l3_unmgd_subnet = self._given_vsdl3sharedmgd_linkedto_vsdl2subnetunmgd()

        self.assertRaisesRegex(
            exceptions.ServerFault,
            "Details: create_subnet_postcommit failed.",

            self._check_vsd_l3_shared_l2_unmgd,
            vsd_l3_dom_subnet=vsd_l3_unmgd_subnet,
            os_shared_network=True,

            # When I try to create an OS subnet with
            #   enable_dhcp == True
            #   CIDR != CIDR of VSD-L3-Shared-domain
            #   nuagenet == UUID of VSD-L3-domain
            #   gateway ip in CIDR
            enable_dhcp=True,
            cidr=VALID_CIDR,
            gateway_ip=VALID_CIDR_GW

            # Then I expect a failure from OS ML2 driver
        )

    @test.attr(type=['negative'])
    @nuage_test.header()
    def test_vsd_l3_shared_mgd_l3_unmgd_no_gw_cidr_mismatch_neg(self):
        # Given  I have a VSD -L3-domain without IPAM (i.e. UnManaged)
        # And I have a VSD-L3-Shared-domain with IPAM (i.e. Managed) with dhcp options 3
        # And  these are linked
        vsd_l3_unmgd_subnet = self._given_vsdl3sharedmgd_linkedto_vsdl2subnetunmgd()

        self.assertRaisesRegex(
            exceptions.ServerFault,
            "Details: create_subnet_postcommit failed.",

            self._check_vsd_l3_shared_l2_unmgd,
            vsd_l3_dom_subnet=vsd_l3_unmgd_subnet,
            os_shared_network=True,

            # When I try to create an OS subnet with
            #   enable_dhcp == True
            #   CIDR != CIDR of VSD-L3-Shared-domain
            #   nuagenet == UUID of VSD-L3-domain
            #   no gateway
            enable_dhcp=True,
            cidr=VALID_CIDR,
            gateway_ip=None

            # Then I expect a failure from OS ML2 driver
        )

    @test.attr(type=['negative'])
    @nuage_test.header()
    def test_vsd_l3_shared_mgd_l3_unmgd_with_gw_gw_mismatch_neg(self):
        # Given  I have a VSD -L3-domain without IPAM (i.e. UnManaged)
        # And I have a VSD-L3-Shared-domain with IPAM (i.e. Managed) with dhcp options 3
        # And  these are linked
        vsd_l3_unmgd_subnet = self._given_vsdl3sharedmgd_linkedto_vsdl2subnetunmgd()

        self.assertRaisesRegex(
            exceptions.BadRequest,
            EXPECT_GATEWAY_IN_CIDR,
            self._check_vsd_l3_shared_l2_unmgd,
            vsd_l3_dom_subnet=vsd_l3_unmgd_subnet,
            os_shared_network=True,
            # When I try to create an OS subnet with
            #   enable_dhcp == True
            #   CIDR != CIDR of VSD-L3-Shared-domain
            #   nuagenet == UUID of VSD-L3-domain
            #   gateway ip not in  CIDR
            enable_dhcp=True,
            cidr=VALID_CIDR,
            gateway_ip=base_vsd_managed_networks.VSD_L2_SHARED_MGD_GW

            # Then I expect a failure indicating enable dhcp may not be false
        )

