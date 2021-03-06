import time
import re
import logging

LOG = logging.getLogger(__name__)

def setup_tempest_public_network(osc):

    out = osc.cmd("source ~/admin_rc;neutron net-list", timeout=30, strict=False)

    cmds = [
        'source ~/admin_rc',
        'neutron net-create tempestPublicNw --router:external',
        'neutron subnet-create tempestPublicNw 10.10.1.0/24 --allocation-pool start=10.10.1.5,end=10.10.1.253 --name tempestPublicSubnet --underlay true',
        'neutron net-list',
        'neutron subnet-list'
    ]
    osc.cmd(' ; '.join(cmds), timeout=60)

    out = osc.cmd("source ~/admin_rc;neutron net-list", timeout=30, strict=False)
    m = re.search(r"(\w+\-\w+\-\w+\-\w+\-\w+)", out[0][3])
    if m:
        net_id = m.group(0)
    else:
        print "Network id not found"
        return None

    return net_id

def get_glance_image_id(osc, imagename):

    cmd = "source ~/admin_rc;glance image-list | grep "
    cmd = cmd + imagename + " | awk '{print $2}'"
    out = osc.cmd(cmd, timeout=30, strict=False)
    if re.search(r"(\w+\-\w+\-\w+\-\w+\-\w+)", out[0][0]):
        image_id = out[0][0]
    else:
        LOG.info('Unable to find image ID for' + imagename)
        return None

    return image_id

def get_glance_image_id(osc, imagename):

    cmd = "source ~/admin_rc;glance image-list | grep "
    cmd = cmd + imagename + " | awk '{print $2}'"
    out = osc.cmd(cmd, timeout=30, strict=False)
    if re.search(r"(\w+\-\w+\-\w+\-\w+\-\w+)", out[0][0]):
        image_id = out[0][0]
    else:
        LOG.info('Unable to find image ID for' + imagename)
        return None

    return image_id


def setup_tempest_tenant_user(osc, tenant, user, password, role):

    def ks_cmd(cmd):
        ks_base_cmd = 'source ~/admin_rc ; keystone'
        awk_cmd = 'awk "/ id / {print $4}"'
        command = '{} {} | {}'.format(ks_base_cmd, cmd, awk_cmd)
        return osc.cmd(command, timeout=30, strict=False)

    tenantid = ks_cmd('tenant-get {}'.format(tenant))
    if not tenantid[0]:
        tenantid = ks_cmd('tenant-create --name {}'.format(tenant))
    tenantid = tenantid[0][0]
    LOG.info('Tenant: {}  ID: {}'.format(tenant, tenantid))

    userid = ks_cmd('user-get {}'.format(user))
    if not userid[0]:
        cmd = 'user-create --name {} --pass {} --tenant {}'
        userid = ks_cmd(cmd.format(user, password, tenant))
    userid = userid[0][0]
    LOG.info('User: {} ID: {}'.format(user, userid))

    roleid = ks_cmd('role-get {}'.format(role))
    if not roleid[0]:
        cmd = 'user-role-add --name {} --pass {} --tenant {} --role {}'
        roleid = ks_cmd(cmd.format(user, password, tenant, role))
    roleid = userid[0][0]
    LOG.info('Role: {} ID: {}'.format(role, roleid))


def setup_cmsid(osc):
    plugin_file = "/etc/neutron/plugins/nuage/plugin.ini"
    audit_cmd = ('python set_and_audit_cms.py '
                 '--plugin-config-file ' + plugin_file +
                 ' --neutron-config-file /etc/neutron/neutron.conf')
    path = '/opt/upgrade-script/upgrade-scripts'
    cmd = 'cd {} ; {}'.format(path, audit_cmd)
    osc.cmd(cmd, timeout=30, strict=False)

    osc.cmd('service neutron-server restart', strict=False, timeout=20)
    time.sleep(5)
    osc.cmd('service neutron-server status', strict=False, timeout=20)

    cmd = "cat {} | grep cms_id".format(plugin_file)
    out = osc.cmd(cmd, timeout=30, strict=False)
    m = re.search(r"cms_id = (\w+\-\w+\-\w+\-\w+\-\w+)", out[0][0])
    if m:
        cms_id = m.group(1)
    else:
        raise Exception('Could not retrieve CMS ID')
    return cms_id


def add_csproot_to_cms(vsd_api, vspk):

    global_ent_id = vsd_api.session.user.enterprise_id
    global_ent = vspk.NUEnterprise(id=global_ent_id)
    grp_filter = 'name IS "CMS Group"'
    usr_filter = 'userName IS "csproot"'
    vsd.add_user_to_group(global_ent, usr_filter=usr_filter, grp_filter=grp_filter)
