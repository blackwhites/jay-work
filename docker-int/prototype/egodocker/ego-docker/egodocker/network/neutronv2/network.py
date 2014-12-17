# =================================================================
# Licensed Materials - Property of IBM
#
# (c) Copyright IBM Corp. 2013, 2014 All Rights Reserved
#
# US Government Users Restricted Rights - Use, duplication or
# disclosure restricted by GSA ADP Schedule Contract with IBM Corp.
# =================================================================

from oslo.concurrency import processutils

from egodocker import exception
from egodocker.i18n import _
from egodocker.common import log
from egodocker import utils

LOG = log.getLogger(__name__)

def teardown_network(container_id):
    try:
        output, err = utils.execute('ip', '-o', 'netns', 'list')
        for line in output.split('\n'):
            if container_id == line.strip():
                utils.execute('ip', 'netns', 'delete', container_id,
                              run_as_root=True)
                break
    except processutils.ProcessExecutionError:
        LOG.warning(_('Cannot remove network namespace, netns id: %s'),
                    container_id)

def find_fixed_ip(instance_id, network_info):
    for subnet in network_info['subnets']:
        netmask = subnet['cidr'].split('/')[1]
        for ip in subnet['ips']:
            if ip['type'] == 'fixed' and ip['address']:
                return ip['address'] + "/" + netmask
    raise exception.InstanceDeployFailure(_('Cannot find fixed ip'),
                                          instance_id=instance_id)

def find_fixed_ip_nomask(instance_id, network_info):
    for subnet in network_info['subnets']:
        for ip in subnet['ips']:
            if ip['type'] == 'fixed' and ip['address']:
                return ip['address']
    raise exception.InstanceDeployFailure(_('Cannot find fixed ip'),
                                          instance_id=instance_id)

def find_gateway(instance_id, network_info):
    for subnet in network_info['subnets']:
        return subnet['gateway']['address']
    raise exception.InstanceDeployFailure(_('Cannot find gateway'),
                                          instance_id=instance_id)

def get_ovs_interfaceid(vif):
    return vif.get('ovs_interfaceid') or vif['id']
