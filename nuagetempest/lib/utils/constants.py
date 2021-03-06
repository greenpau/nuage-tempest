# VSD RESOURCE URI, not a complete list.
# list of resources currently used by nuage plugin
#
#    -----------------------WARNING----------------------------
#     This file is present to support Legacy Test Code only.
#     DO not use this file for writing the new tests.
#    ----------------------------------------------------------
#
# GATEWAY
GATEWAY = 'gateways'

# TODO: duplicate
REDUNDANCY_GROUPS = 'redundancygroups'
VSG_REDUNDANT_PORTS = 'vsgredundantports'

REDCY_GRP = 'redundancygroups'
GATEWAY_VSG_REDCY_PORT = 'vsgredundantports'
GATEWAY_PORT = 'ports'
VLAN = 'vlans'
ENTERPRISE_PERMS = 'enterprisepermissions'
NUMBER_OF_PORTS_PER_GATEWAY = 2
NUMBER_OF_VLANS_PER_PORT = 8
START_VLAN_VALUE = 100

# NETWORK
DHCPOPTION = 'dhcpoptions'
DOMAIN = 'domains'
DOMAIN_TEMPLATE = 'domaintemplates'
ENTERPRISE_NET_MACRO = 'enterprisenetworks'
FLOATINGIP = 'floatingips'
L2_DOMAIN = 'l2domains'
L2_DOMAIN_TEMPLATE = 'l2domaintemplates'
PUBLIC_NET_MACRO = 'publicnetworks'
SHARED_NET_RES = 'sharednetworkresources'
STATIC_ROUTE = 'staticroutes'
SUBNETWORK = 'subnets'
SUBNET_TEMPLATE = 'subnettemplates'
ZONE = 'zones'
ZONE_TEMPLATE = 'zonetemplates'

# POLICY
EGRESS_ACL_TEMPLATE = 'egressacltemplates'
EGRESS_ACL_ENTRY_TEMPLATE = 'egressaclentrytemplates'
INGRESS_ACL_TEMPLATE = 'ingressacltemplates'
INGRESS_ACL_ENTRY_TEMPLATE = 'ingressaclentrytemplates'
INGRESS_ADV_FWD_ENTRY_TEMPLATE = 'ingressadvfwdentrytemplates'
INGRESS_ADV_FWD_TEMPLATE = 'ingressadvfwdtemplates'
APPLY_JOBS = 'jobs'

# USER MANAGEMENT
NET_PARTITION = 'enterprises'
USER = 'users'
GROUP = 'groups'
PERMIT_ACTION = 'permissions'

# VM
VM_IFACE = 'vminterfaces'
VM = 'vms'

# VPORT
BRIDGE_IFACE = 'bridgeinterfaces'
HOST_IFACE = 'hostinterfaces'
POLICYGROUP = 'policygroups'
VPORT = 'vports'
VIRTUAL_IP = 'virtualips'
REDIRECTIONTARGETS = 'redirectiontargets'

# GATEWAY
GATEWAY = 'gateways'

# Quality of Service
QOS = 'qos'

ENABLED = 'ENABLED'
DISABLED = 'DISABLED'
INHERITED = 'INHERITED'

# CIDR_TO_NETMASK
CIDR_TO_NETMASK = {
    '8': '255.0.0.0',
    '16': '255.255.0.0',
    '24': '255.255.255.0',
    '32': '255.255.255.0'
}


PROTO_NAME_TO_NUM = {
    'tcp': u'6',
    'udp': u'17',
    'icmp': u'1',
    'IPv4': u'0x0800'
}

# Application Designer
APPLICATION_DOMAIN = 'application-domains'
APPLICATION = 'applications'
TIER = 'tiers'
FLOW = 'flows'
SERVICE = 'applicationservices'

# GATEWAYPERSONALITY
PERSONALITY_LIST = ['VRSG', 'VSG']

# Vport type
HOST_VPORT = 'HOST'
BRIDGE_VPORT = 'BRIDGE'

#System configuration
SYSTEM_CONFIGS = 'systemconfigs'

DOMAIN_TUNNEL_TYPE_VXLAN = "VXLAN"
DOMAIN_TUNNEL_TYPE_GRE = "GRE"
DOMAIN_TUNNEL_TYPE_DEFAULT = "DEFAULT"

# Plugin / neutron start command for Kilo Devstack Ubuntu
NEUTRON_KILODEVSTACK_UBUNTU_PLUGIN_FILE = "/etc/neutron/plugins/nuage/nuage_plugin.ini"
# NEUTRON_KILODEVSTACK_UBUNTU_START_CMD = "sudo nohup python /usr/local/bin/neutron-server " + \
#                                         "--config-file /etc/neutron/neutron.conf " + \
#                                         "--config-file /etc/neutron/plugins/nuage/nuage_plugin.ini " + \
#                                         "--logfile /var/log/neutron/server.log " + \
#                                         " > foo.out 2> foo.err < /dev/null &"
NEUTRON_KILODEVSTACK_UBUNTU_START_CMD = "sudo nohup python /usr/local/bin/neutron-server " + \
                                        "--config-file /etc/neutron/neutron.conf " + \
                                        "--config-file /etc/neutron/plugins/nuage/nuage_plugin.ini " + \
                                        " > foo.out 2> foo.err < /dev/null &"

## Plugin file / neutron start command for Kilo Ubuntu 1404 distro
#NEUTRON_KILO_UBUNTU_PLUGIN_FILE = "/etc/neutron/plugins/nuage/plugin.ini"
NEUTRON_KILO_UBUNTU_START_CMD = "service neutron-server restart"
NEUTRON_KILO_UBUNTU_STOP_CMD = "service neutron-server stop"

## FOr now, running on Kilo Ubuntu 1404
#NUAGE_PLUGIN_CONFIG_FILE = NEUTRON_KILO_UBUNTU_PLUGIN_FILE
NUAGE_PLUGIN_START_CMD   = NEUTRON_KILO_UBUNTU_START_CMD

# Services
NEUTRON_SERVICE = "neutron-server"

# FIP constants
FIP_RATE_GROUP = "fiprate"
FIP_RATE_DEFAULT = "default_fip_rate"
FIP_RATE_LOG_FILE = "fip_rate_change_log"

NUAGE_FIP_UNDERLAY = "nuage_fip_underlay"
NUAGE_FIP_UNDERLAY_GROUP = "restproxy"

# Special values
UNLIMITED = -1
MAX_INT = ((2 ** 32) / 2) - 1
MAX_INT_PLUS_ONE = MAX_INT + 1
MAX_UNSIGNED_INT32 = (2**32) - 1
MAX_UNSIGNED_INT32_PLUS_ONE = MAX_UNSIGNED_INT32 + 1

# PAT constants
NUAGE_PAT_VSD_ENABLED = 'ENABLED'
NUAGE_PAT_VSD_DISABLED = 'DISABLED'
NUAGE_PAT_NOTAVAILABLE = 'not_available'
NUAGE_PAT_DEFAULTDISABLED = 'default_disabled'
NUAGE_PAT_DEFAULTENABLED = 'default_enabled'
NUAGE_PAT = 'nuage_pat'
NUAGE_PAT_GROUP = 'restproxy'

# nuage-uplink constants
NUAGE_UPLINK_GROUP = 'restproxy'
NUAGE_UPLINK = 'nuage_uplink'

