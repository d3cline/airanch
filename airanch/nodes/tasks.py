import opalstack
from celery import shared_task
from django.conf import settings
from opalstack.util import filt, filt_one, one
from airanch.settings import OPALSTACK_API_KEY, NODE_BASE_DOMAIN_NAME, APPNAME, WEBSERVER
from django.apps import apps
from socket import gethostname
import paramiko

from paramiko import SSHClient, AutoAddPolicy
from paramiko.sftp_attr import SFTPAttributes
from celery import shared_task
import os
from jinja2 import Template

@shared_task
def publish_public_key_to_server(public_key_content, hostname, username, password):
    ssh_directory = f"/home/{username}/.ssh"
    authorized_keys_file = f"{ssh_directory}/authorized_keys"

    client = SSHClient()
    client.set_missing_host_key_policy(AutoAddPolicy())

    try:
        client.connect(hostname, username=username, password=password)
        sftp = client.open_sftp()

        # Check if SSH directory exists, create it if not
        try:
            sftp.stat(ssh_directory)
        except IOError:  # If the directory does not exist, create it
            sftp.mkdir(ssh_directory, mode=0o700)

        # Check if authorized_keys file exists, create it if not
        try:
            sftp.stat(authorized_keys_file)
        except IOError:  # If the file does not exist, create it
            file = sftp.file(authorized_keys_file, 'w')
            file.close()
            sftp.chmod(authorized_keys_file, 0o600)

        # Append public key to authorized_keys file
        with sftp.file(authorized_keys_file, 'a') as authorized_keys:
            authorized_keys.write(public_key_content + "\n")

    except Exception as e:
        print(f"An error occurred: {e}")
        return False, str(e)
    finally:
        if sftp: sftp.close()
        if client: client.close()

    return True, "Public key published successfully"

@shared_task
def upload_content_to_server(template_content, context, remote_filepath, hostname, username, password, permissions=600):
    try:
        # Render the template content with the provided context
        template = Template(template_content)
        rendered_content = template.render(context)
        
        # Initialize the SSH client
        client = paramiko.SSHClient()
        # Automatically add host key
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        # Connect to the server
        client.connect(hostname, port=22, username=username, password=password)
        
        # Use Paramiko's SFTP client for file operations
        sftp = client.open_sftp()
        
        # Open the remote file in write mode ('w') and write the rendered content
        with sftp.file(remote_filepath, 'w') as remote_file:
            remote_file.write(rendered_content)
        
        # Set permissions for the remote file
        sftp.chmod(remote_filepath, permissions)
        
        # Cleanup: close the SFTP client and SSH connection
        sftp.close()
        client.close()
        return True
    except Exception as e:
        print(f"Failed to upload content: {e}")
        return False

def select_by_name(array, name):
    for item in array:
        if item['name'] == name:
            return item
    return None

@shared_task
def create_tunnel_port(id):
    Node = apps.get_model('nodes', 'Node')
    Port = apps.get_model('nodes', 'Port')
    node = Node.objects.get(id=id)
    ports = Port.objects.filter(node=node)
    opalapi = opalstack.Api(token=OPALSTACK_API_KEY)
    errors = {}

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
    if node.template and node.template.html is not None:
        apps_to_create.append({
            'name': 'template',
            'osuser': osuser['id'],
            'type': 'STA',
        })
        node.template
    port_apps = opalapi.apps.create(apps_to_create)

    Node.objects.filter(id=id).update(
        os_user_id=osuser['id'],
        password=osuser['default_password'],
        state='READY',
    )
    return True

@shared_task
def delete_tunnel_port_objects(os_user_id):
    opalapi = opalstack.Api(token=OPALSTACK_API_KEY)
    osuer = filt_one(opalapi.osusers.list_all(), {'id': str(os_user_id)})
    opalapi.osusers.delete([osuer])
    return True

@shared_task
def update_pub_key(id):
    opalapi = opalstack.Api(token=OPALSTACK_API_KEY)
    if WEBSERVER: 
        web_server = filt_one(opalapi.servers.list_all()['web_servers'], {'hostname': gethostname()})
    else: 
        web_server = opalapi.servers.list_all()['web_servers'][0]
    PublicKey = apps.get_model('nodes', 'PublicKey')
    pubkey = PublicKey.objects.get(id=id)

    publish_public_key_to_server(
        pubkey.key, 
        web_server['hostname'],
        pubkey.node.name, 
        pubkey.node.password
    )
    return True
