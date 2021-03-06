# Copyright 2013 OpenStack Foundation
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

import six
import uuid

from tempest.lib.common.utils import data_utils
from tempest.lib import exceptions
from tempest import config
from tempest import test
from nuagetempest.thirdparty.nuage import test_security_groups_nuage
from nuagetempest.lib.utils import constants as constants
from nuagetempest.services import nuage_client
from nuagetempest.services.nuage_network_client import NuageNetworkClientJSON

from oslo_log import log as logging

CONF = config.CONF
LOG = logging.getLogger(__name__)

class NuageExtSecGroup(test_security_groups_nuage.SecGroupTestNuage):
    @classmethod
    def setup_clients(cls):
        super(NuageExtSecGroup, cls).setup_clients()
        cls.nuageclient = nuage_client.NuageRestClient()
        cls.client = NuageNetworkClientJSON(
            cls.os.auth_provider,
            CONF.network.catalog_type,
            CONF.network.region or CONF.identity.region,
            endpoint_type=CONF.network.endpoint_type,
            build_interval=CONF.network.build_interval,
            build_timeout=CONF.network.build_timeout,
            **cls.os.default_params)

    @classmethod
    def resource_setup(cls):
        super(NuageExtSecGroup, cls).resource_setup()
        cls.external_secgroups = []
        
    @classmethod
    def resource_cleanup(cls):
        super(NuageExtSecGroup, cls).resource_cleanup()

    @classmethod
    def _create_external_security_group(cls, **kwargs):
        body = cls.client.create_nuage_external_security_group(**kwargs)
        ext_sg = body['nuage_external_security_group']
        cls.external_secgroups.append(ext_sg)
        return ext_sg

    @classmethod
    def _delete_external_security_group(cls, esg_id):
        try:
            cls.client.delete_nuage_external_security_group(esg_id)
        except Exception as exc:
            LOG.exception(exc)
            has_exception = True

    @classmethod
    def _create_external_security_group_rule(cls, **kwargs):
        body = cls.client.create_nuage_external_security_group_rule(**kwargs)
        ext_sg_rule = body['nuage_external_security_group_rule']
        cls.external_secgroups.append(ext_sg_rule)
        return ext_sg_rule


    def _verify_external_secgroup_properties(self, actual_esg, 
                                                   expected_esg):
        self.assertEqual(actual_esg['name'], expected_esg['name'])
        self.assertEqual(actual_esg['extended_community_id'],
                         expected_esg['EVPNCommunityTag'])
        self.assertEqual(actual_esg['id'],
                         expected_esg['ID'])
    
    def _verify_external_secgroup_rule_properties(self, actual_esgr, 
                                                  expected_esgr, origin_sg):
        self.assertEqual(actual_esgr['id'], expected_esgr['ID'])
        self.assertEqual(actual_esgr['protocol'], expected_esgr['protocol'])
        self.assertEqual(actual_esgr['origin_group_id'], origin_sg['id'])

    def _get_nuage_external_acl(self, esg_router, ext_sg_rule, isList=False):
        l3domain_ext_id = self.nuageclient.get_vsd_external_id(esg_router['id'])
        l3domain = self.nuageclient.get_l3domain(
                   filters='externalID',
                   filter_value=l3domain_ext_id)

        if ext_sg_rule['direction'] == 'egress':
            nuage_eacl_template = self.nuageclient.\
                get_egressacl_template(constants.DOMAIN,
                                       l3domain[0]['ID'])
            if not isList :
                nuage_entrytemplate = self.nuageclient.\
                    get_egressacl_entytemplate(
                        constants.EGRESS_ACL_TEMPLATE,
                        nuage_eacl_template[0]['ID'],
                        filters='ID',
                        filter_value=ext_sg_rule['id'])
            else:
                nuage_entrytemplate = self.nuageclient.\
                    get_egressacl_entytemplate(
                        constants.EGRESS_ACL_TEMPLATE,
                        nuage_eacl_template[0]['ID'])
        else:
            nuage_iacl_template = self.nuageclient.\
                get_ingressacl_template(
                    constants.DOMAIN,
                    l3domain[0]['ID'])
            if not isList:
                nuage_entrytemplate = self.nuageclient.\
                    get_ingressacl_entytemplate(
                        constants.INGRESS_ACL_TEMPLATE,
                        nuage_iacl_template[0]['ID'],
                        filters='ID',
                        filter_value=ext_sg_rule['id'])
            else:
                # TODO: Check with Spurthi
                nuage_entrytemplate = self.nuageclient. \
                    get_ingressacl_entytemplate(
                        constants.INGRESS_ACL_TEMPLATE,
                        nuage_iacl_template[0]['ID'])
        return nuage_entrytemplate

    def test_create_show_list_delete_ext_secgroup(self, *args):
        router_name = data_utils.rand_name('router-')
        body = self.routers_client.create_router(router_name)
        esg_router = body['router']
        self.addCleanup(self.routers_client.delete_router, esg_router['id'])
        name = data_utils.rand_name('esg-')
        kwargs = {'name': name,
                  'router_id': esg_router['id'],
                  'extended_community_id': "1:1"}
        ext_sg = self._create_external_security_group(**kwargs)
        self.addCleanup(self._delete_external_security_group, ext_sg['id'])
        self.assertEqual(ext_sg['name'], name)
        self.assertEqual(ext_sg['extended_community_id'], 
                         "1:1")
        # VSD verification of external security group 
        res_path = self.nuageclient.build_resource_path(
            constants.POLICYGROUP,
            resource_id=ext_sg['id'])
        show_vsd_resp = self.nuageclient.get(res_path)
        show_resp = self.client.show_nuage_external_security_group(ext_sg['id'])
        self._verify_external_secgroup_properties(
            show_resp['nuage_external_security_group'],
            show_vsd_resp[0])
        
        # list_external_security_group
        res_path = self.nuageclient.build_resource_path(
            constants.POLICYGROUP,
            resource_id=ext_sg['id'])
        list_vsd_resp = self.nuageclient.get(res_path)
        list_resp = self.client.list_nuage_external_security_group(esg_router['id'])
        self._verify_external_secgroup_properties(
            list_resp['nuage_external_security_groups'][0],
            list_vsd_resp[0])

    def test_create_show_list_delete_ext_secgroup_rule(self):
        router_name = data_utils.rand_name('router-')
        body = self.routers_client.create_router(router_name)
        esg_router = body['router']
        self.addCleanup(self.routers_client.delete_router, esg_router['id'])
        body, name = self._create_security_group()
        sec_group = body['security_group']
        name = data_utils.rand_name('esg-')
        kwargs = {'name': name,
                  'router_id': esg_router['id'],
                  'extended_community_id': "1:1"}
        ext_sg = self._create_external_security_group(**kwargs)
        self.addCleanup(self._delete_external_security_group, ext_sg['id'])
        kwargs = {'protocol': 'tcp',
                  'direction': 'egress',
                  'origin_group_id': sec_group['id'],
                  'remote_external_group_id': ext_sg['id']}
        ext_sg_rule = self._create_external_security_group_rule(**kwargs)
        # Show operation and VSD verification of external security group 
        show_resp = self.client.show_nuage_external_security_group_rule(ext_sg_rule['id'])
        show_vsd_resp = self._get_nuage_external_acl(esg_router, ext_sg_rule) 
        self._verify_external_secgroup_rule_properties(
            show_resp['nuage_external_security_group_rule'],
            show_vsd_resp[0], sec_group)
         
        # Create second rule 
        kwargs = {'protocol': 'udp',
                  'port_range_min': 300,
                  'port_range_max': 500,
                  'direction': 'egress',
                  'origin_group_id': sec_group['id'],
                  'remote_external_group_id': ext_sg['id']}
        ext_sg_rule = self._create_external_security_group_rule(**kwargs)
        # List Operation on secgroup rules
        list_resp = self.client.list_nuage_external_security_group_rule(ext_sg['id'])
        list_vsd_resp = self._get_nuage_external_acl(esg_router, ext_sg_rule, True)
        self._verify_external_secgroup_rule_properties(
            list_resp['nuage_external_security_group_rules'][0],
            list_vsd_resp[0], sec_group)
        self._verify_external_secgroup_rule_properties(
            list_resp['nuage_external_security_group_rules'][1],
            list_vsd_resp[1], sec_group)

    def test_create_show_list_delete_ext_secgroup_l2domain(self):
        net_name = data_utils.rand_name('network-')
        network = self.create_network(net_name)
        esg_subnet = self.create_subnet(network)
        name = data_utils.rand_name('esg-')
        kwargs = {'name': name,
                  'subnet_id': esg_subnet['id'],
                  'extended_community_id': "4:4"}
        ext_sg = self._create_external_security_group(**kwargs)
        self.addCleanup(self._delete_external_security_group, ext_sg['id'])
        self.assertEqual(ext_sg['name'], name)
        self.assertEqual(ext_sg['extended_community_id'], 
                         "4:4")
        # VSD verification of external security group 
        res_path = self.nuageclient.build_resource_path(
            constants.POLICYGROUP,
            resource_id=ext_sg['id'])
        show_vsd_resp = self.nuageclient.get(res_path)
        show_resp = self.client.show_nuage_external_security_group(ext_sg['id'])
        self._verify_external_secgroup_properties(
            show_resp['nuage_external_security_group'],
            show_vsd_resp[0])
        
        # list_external_security_group
        res_path = self.nuageclient.build_resource_path(
            constants.POLICYGROUP,
            resource_id=ext_sg['id'])
        list_vsd_resp = self.nuageclient.get(res_path)
        list_resp = self.client.list_nuage_external_security_group_l2domain(esg_subnet['id'])
        self._verify_external_secgroup_properties(
            list_resp['nuage_external_security_groups'][0],
            list_vsd_resp[0])

    def test_create_delete_invalid_ext_secgroup(self):
        router_name = data_utils.rand_name('router-')
        body = self.routers_client.create_router(router_name)
        esg_router = body['router']
        self.addCleanup(self.routers_client.delete_router, esg_router['id'])
        body, name = self._create_security_group()
        sec_group = body['security_group']
        name = data_utils.rand_name('esg-')
        # Missing pararmeter: external_communtiy_tag in input
        kwargs = {'name': name,
                  'router_id': esg_router['id']}
        self.assertRaises(exceptions.BadRequest,
            self.client.create_nuage_external_security_group,
            **kwargs)
        # Invalid external_communtiy_tag_value
        kwargs = {'name': name,
                  'router_id': esg_router['id'],
                  'extended_community_id': "4"}
        self.assertRaises(exceptions.ServerFault,
            self.client.create_nuage_external_security_group,
            **kwargs)
        # Missing pararmeter: router/subnet ID in input
        kwargs = {'name': name,
                  'router_id':'11111111-1111-1111-1111111111111111',
                  'extended_community_id': "2:2"}
        self.assertRaises(exceptions.BadRequest,
            self.client.create_nuage_external_security_group,
            **kwargs)
        # Try deleting invalid external_secgroup
        self.assertRaises(exceptions.NotFound,
            self.client.delete_nuage_external_security_group,
            '11111111-1111-1111-1111111111111111')

    def test_create_delete_invalid_ext_secgroup_rule(self):
        router_name = data_utils.rand_name('router-')
        body = self.routers_client.create_router(router_name)
        esg_router = body['router']
        self.addCleanup(self.routers_client.delete_router, esg_router['id'])
        body, name = self._create_security_group()                           
        sec_group = body['security_group']                 
        name = data_utils.rand_name('esg-')
        kwargs = {'name': name,
                  'router_id': esg_router['id'],
                  'extended_community_id': "1:1"}    
        ext_sg = self._create_external_security_group(**kwargs)
        # Missing mandatory parameter: origin_group_id in input 
        kwargs = {'protocol': 'tcp',
                  'direction': 'egress',
                  'remote_external_group_id': ext_sg['id']}
        self.assertRaises(exceptions.ServerFault,
            self.client.create_nuage_external_security_group_rule,
            **kwargs)
        # Invalid remote_group_id value
        kwargs = {'protocol': 'tcp',
                  'direction': 'egress',
                  'origin_group_id': sec_group['id'],
                  'remote_external_group_id': '11111111-1111-1111-1111111111111111'}
        self.assertRaises(exceptions.ServerFault,
            self.client.create_nuage_external_security_group_rule,
            **kwargs)
        # Try deleting invalid external_secgroup_rule
        self.assertRaises(exceptions.NotFound,
            self.client.delete_nuage_external_security_group_rule,
            '11111111-1111-1111-1111111111111111')
