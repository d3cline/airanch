import opalstack
from celery import shared_task
from django.conf import settings
from opalstack.util import filt, filt_one, one
from airanch.settings import OPALSTACK_API_KEY, NODE_BASE_DOMAIN_NAME, APPNAME, WEBSERVER
from django.apps import apps
from socket import gethostname
import paramiko


@shared_task
def upload_content_to_server(file_content, remote_filepath, hostname, username, password, permissions=600):
    try:
        # Initialize the SSH client
        client = paramiko.SSHClient()
        # Automatically add host key
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # Connect to the server
        client.connect(hostname, port=22, username=username, password=password)
        
        # Use Paramiko's SFTP client for file operations
        sftp = client.open_sftp()
        
        # Open the remote file in write mode ('w') and write the content
        with sftp.file(remote_filepath, 'w') as remote_file:
            remote_file.write(file_content)
        
        # Set permissions for the remote file
        sftp.chmod(remote_filepath, permissions)
        
        # Cleanup: close the SFTP client and SSH connection
        sftp.close()
        client.close()
        return True
    except Exception as e:
        print(f"Failed to upload content: {e}")
        return False


@shared_task
def create_tunnel_port(id):
    Node = apps.get_model('nodes', 'Node')
    Port = apps.get_model('nodes', 'Port')
    node = Node.objects.get(id=id)
    ports = Port.objects.filter(node=node)

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


    apps_to_create = []
    for port in ports:
        apps_to_create.append({
            'name': f'{port.entry_port}',
            'osuser': osuser['id'],
            'type': 'CUS',
        })

    port_apps = opalapi.apps.create(apps_to_create)

    routes = []
    for port_app in port_apps:
        Port.objects.filter(entry_port=port_app['name']).update(
            exit_port=port_app['port'],
            port_app_id=port_app['id'],
        )
        routes.append(
            {'app': port_app['id'], 'uri': f'/{port_app["name"]}'}
        )

    sites_to_create = [{
        'name': f'{APPNAME}_{node.name}',
        'ip4': webserver_primary_ip['id'],
        'domains': [node_domain['id']],
        'routes': routes,
    }]
    site = one(opalapi.sites.create(sites_to_create))

    Node.objects.filter(id=id).update(
        node_domain_id=node_domain['id'],
        os_user_id=osuser['id'],
        site_route_id=site['id'],
        password=osuser['default_password'],
        state='READY'
    )

    return True

@shared_task
def delete_tunnel_port_objects(os_user_id, site_route_id, node_domain_id):
    opalapi = opalstack.Api(token=OPALSTACK_API_KEY)

    site = filt_one(opalapi.sites.list_all(), {'id': str(site_route_id)})
    opalapi.sites.delete([site])

    domain = filt_one(opalapi.domains.list_all(), {'id': str(node_domain_id)})
    opalapi.domains.delete([domain])

    osuer = filt_one(opalapi.osusers.list_all(), {'id': str(os_user_id)})
    opalapi.osusers.delete([osuer])

    return True
