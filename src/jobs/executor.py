# import paramiko
import subprocess

def run_command_on_remote(command):
    # ssh = paramiko.SSHClient()
    # ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # ssh.connect('your.remote.host', username='user', password='pass')
    # stdin, stdout, stderr = ssh.exec_command(command)
    # output = stdout.read().decode() + stderr.read().decode()
    # ssh.close()
    
    result = subprocess.run(command, shell=True, capture_output=True, text=True)
    output = result.stdout + result.stderr
    
    return output
