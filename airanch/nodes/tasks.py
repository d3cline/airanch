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
    errors = {}

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
    try:
        osuser = one(opalapi.osusers.create(osusers_to_create))
    except RuntimeError as e:
        errors['osuser'] = str(e)
        Node.objects.filter(id=id).update(
            state='FAILED',
            error_logs=errors
        )
        raise

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
def delete_tunnel_port_objects(port_app_id, os_user_id, site_route_id, node_domain_id):
    opalapi = opalstack.Api(token=OPALSTACK_API_KEY)

    site = filt_one(opalapi.sites.list_all(), {'id': str(site_route_id)})
    opalapi.sites.delete([site])

    domain = filt_one(opalapi.domains.list_all(), {'id': str(node_domain_id)})
    opalapi.domains.delete([domain])

    app = filt_one(opalapi.apps.list_all(), {'id': str(port_app_id)})
    opalapi.apps.delete([app])

    osuer = filt_one(opalapi.osusers.list_all(), {'id': str(os_user_id)})
    opalapi.osusers.delete([osuer])

    return True
