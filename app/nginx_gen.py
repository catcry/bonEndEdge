"""
Created on Fri Dec 15 02:15:08 2023

@author: catcry
"""


import os
import yaml
from paramiko import SSHClient, AutoAddPolicy
from scp import SCPClient


def get_server_config():
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        config_path = os.path.join(base_dir, 'config', 'nginx_server_info.yml')
        with open (config_path, 'r') as stream:
            config = yaml.safe_load(stream)
        return config['server']
    except FileNotFoundError:
        return "Error: The database configuration file 'nginx_server_info.yaml' was not found."
    except yaml.YAMLError as exc:
        return f"Error parsing 'nginx_server_info.yaml': {exc}"
    except Exception as exc:
        return f"An unexpected error occurred: {exc}"


def send_conf(server_info, gen_filepath, gen_filename):
    host = server_info['host']
    username = server_info['username']
    password = server_info['password']
    remote_path = server_info['remote_path']

    ssh = SSHClient()
    ssh.set_missing_host_key_policy(AutoAddPolicy())
    ssh.connect(host, username=username, password=password)
    
    
    with SCPClient(ssh.get_transport()) as scp:
        scp.put(gen_filepath, remote_path)
    
    # mv to nginx conf
    remote_file = remote_path + gen_filename
    
    command = f'echo {password} | sudo -S mv {remote_file} /etc/nginx/conf.d'
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    if exit_status == 0:
        return "Config Updated"

    else:
        print("Error", stderr.read().decode())
    # Reload Nginx
    command = f'echo {password} | sudo -S systemctl reload nginx.service'
    stdin, stdout, stderr = ssh.exec_command(command)
    exit_status = stdout.channel.recv_exit_status()
    if exit_status == 0:
        return "Config Updated and Nginx Reloaded Successfully"

    else:
        print("Error", stderr.read().decode())
    ssh.close()



def nginx_conf_gen(end_name, end_url, end_port):
    
    try:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        template_conf_file = os.path.join(base_dir, 'config', 'nginx_conf_template.conf')
        conf_file_path = os.path.join(base_dir, 'nginx_conf_back', end_name + '.conf')
        conf_file_name = end_name + '.conf'
        #nginx_server_info_file = os.path.join(base_dir, 'config', 'nginx_server_info.yml')
    
        with open (template_conf_file, 'r') as file:
            file_contents = file.read()
    
        file_contents = file_contents.replace("end_url",end_url)
        file_contents = file_contents.replace("end_port",end_port)
    except FileNotFoundError:
        print("Error: The file 'nginx_conf_template.conf' was not found.")
    #    return "Error: The file 'nginx_conf_template.conf' was not found."  
    
    try:
        with open (conf_file_path,'w') as file:
            file.write(file_contents)
    except FileNotFoundError:
        print("Error: The file 'conf_file_bkp.conf' was not found.")
    try:        
        server_info = get_server_config()
    except FileNotFoundError:
        print("Error: The file 'nginx_server_info_file' was not found.")

    try:
        send_conf(server_info, conf_file_path, conf_file_name)
        return 1
    except FileNotFoundError:
        print("Error: cannot call.")
        return 0


def nginx_conf_del(service_name):
    server_info = get_server_config()
    host = server_info['host']
    username = server_info['username']
    password = server_info['password']
    #password=r"p!L0\/\/"
    remote_file_path = "/etc/nginx/conf.d/" + service_name + '.conf'
    print (remote_file_path)
    try:
        ssh = SSHClient()
        ssh.set_missing_host_key_policy(AutoAddPolicy())
        ssh.connect(host, username=username, password=password)

        # Removing Config File
        command = f'echo {password} | sudo -S rm {remote_file_path}'
        #command = f"bash -c '{command}'"
        stdin, stdout, stderr = ssh.exec_command(command)
        exit_status = stdout.channel.recv_exit_status()
        if exit_status == 0:
            return "File removed successfully"

        else:
            print("Error", stderr.read().decode())
        
        # Reloading Nginx Service
        command = f"echo {password} | sudo -S systemctl reload nginx"
        stdin, stdout, stderr = ssh.exec_command(command)
        exit_status = stdout.channel.recv_exit_status()
        if exit_status == 0:
            return "Nginx Reloaded successfully"

        else:
            print("Error", stderr.read().decode())
        
    except:
        print ("cannot1")
    finally:
        ssh.close()