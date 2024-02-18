import opalstack
from celery import shared_task
from django.conf import settings
from opalstack.util import filt, filt_one, one
from airanch.settings import OPALSTACK_API_KEY, NODE_BASE_DOMAIN_NAME, APPNAME, WEBSERVER
from django.apps import apps
from socket import gethostname

@shared_task
def create_tunnel_port(id):
    Node = apps.get_model('nodes', 'Node')
    node = Node.objects.get(id=id)
    opalapi = opalstack.Api(token=OPALSTACK_API_KEY)

    '''
    1. Create OS User 
    2. Create Nginx Port App, save port to model
    3. Create domain NODENAME.SITEDOMAIN.TLD
    4. Create site binding and SSL etc.
    save every UUID to model for deletion later. 
    '''

    # Retrieve the "opalstacked" gift domain.
    # TODO add if not exists logic here. 
    base_domain = filt_one(opalapi.domains.list_all(), {'name': NODE_BASE_DOMAIN_NAME})

    base_domain_name = base_domain['name']
    node_domain_name = f'{node.name}.{base_domain_name}'
    domains_to_create = [{
        'name': node_domain_name,
    }]
    node_domain = one(opalapi.domains.create(domains_to_create))

    if WEBSERVER: 
        web_server = filt_one(opalapi.servers.list_all()['web_servers'], {'hostname': gethostname()})
        webserver_primary_ip = filt_one(opalapi.ips.list_all(embed=['server']), {'server.hostname': gethostname(), 'primary': True})
    else: 
        web_server = opalapi.servers.list_all()['web_servers'][0]
        webserver_primary_ip = filt_one(opalapi.ips.list_all(embed=['server']), {'server.hostname': web_server['hostname'], 'primary': True})

    osusers_to_create = [{
        'name':  f'{node.name}',
        'server': web_server['id'],
    }]
    osuser = one(opalapi.osusers.create(osusers_to_create))

    apps_to_create = [{
        'name': f'{APPNAME}_{node.name}',
        'osuser': osuser['id'],
        'type': 'CUS',
    }]
    port_app = one(opalapi.apps.create(apps_to_create))

    sites_to_create = [{
        'name': f'{APPNAME}_{node.name}',
        'ip4': webserver_primary_ip['id'],
        'domains': [node_domain['id']],
        'routes': [{'app': port_app['id'], 'uri': '/'}],
    }]
    site = one(opalapi.sites.create(sites_to_create))

    Node.objects.filter(id=id).update(
        exit_port=port_app['port'],
        node_domain_id=node_domain['id'],
        os_user_id=osuser['id'],
        port_app_id=port_app['id'],
        site_route_id=site['id'],
        state='READY'
    )

    return True

@shared_task
def delete_tunnel_port_objects(id):
    Node = apps.get_model('nodes', 'Node')
    node = Node.objects.get(id=id)
    opalapi = opalstack.Api(token=OPALSTACK_API_KEY)
    opalapi.sites.delete([created_site])
    opalapi.apps.delete([created_app])
    opalapi.osusers.delete([created_osuser])
    opalapi.domains.delete([created_domain])
