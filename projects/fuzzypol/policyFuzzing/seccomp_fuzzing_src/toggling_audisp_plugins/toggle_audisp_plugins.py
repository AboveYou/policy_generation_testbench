import os
from sys import stdout
import time 
import subprocess

plugin_dir = "/etc/audit/plugins.d/"

def toggle_syscall_finder_plugin(value:bool =False):
    global plugin_dir
    name = "sbp.conf"
    
    if value: 
        string_value = "yes"
    else: 
        string_value = "no"

    syscall_finder_plugin = f"""active = {string_value}
direction = out
path = /usr/local/sbin/sbp-audisp-plugin
type = always
#args =
format = string
"""

    with open(os.path.join(plugin_dir, name), 'w') as plugin_file: 
        plugin_file.write(syscall_finder_plugin)
    

def toggle_file_finder_plugin(value:bool =False):
    global plugin_dir
    name = "AudispPlugin.conf"

    if value: 
        string_value = "yes"
    else: 
        string_value = "no"

    file_finder_plugin = f"""active = {string_value}
direction = out
path = /home/vagrant/fileFinder/AudispPlugin
type = always
args = test
format = string
"""

    if value: 
        file_finder_plugin.replace("placeholder", "yes") 
    else: 
        file_finder_plugin.replace("placeholder", "no")

    with open(os.path.join(plugin_dir, name), 'w') as plugin_file: 
        plugin_file.write(file_finder_plugin)
    

def toggle_syscall_file_finder_plugin(value:bool =False):
    global plugin_dir
    name = "syscall_file_fuzzer.conf"

    if value: 
        string_value = "yes"
    else: 
        string_value = "no"

    syscall_file_finder_plugin = f"""active = {string_value}
direction = out
path = /usr/local/sbin/syscall_logger.py
type = always
#args =
format = string
"""
   
    with open(os.path.join(plugin_dir, name), 'w') as plugin_file: 
        plugin_file.write(syscall_file_finder_plugin)


def toggle_fuzzing_plugin(value:bool =False):
    global plugin_dir
    name = "fuzzing_plugin.conf"

    
    if value: 
        string_value = "yes"
    else: 
        string_value = "no"

    fuzzing_plugin = f"""active = {string_value}
direction = out
path = /usr/local/sbin/fuzzing_plugin.py
type = always
#args =
format = string
"""

    with open(os.path.join(plugin_dir, name), 'w') as plugin_file: 
        plugin_file.write(fuzzing_plugin)


def stop_auditd(): 
    subprocess.run(["service", "auditd", "restart"])


def restart_auditd(): 
    exit_flag = True
    while exit_flag: 
        try:
            subprocess.check_output(["service", "auditd", "restart"], stderr=subprocess.DEVNULL)
            exit_flag = False 
        except subprocess.CalledProcessError: 
            print("\t[!] Auditd Failed to start: Retrying...")
            time.sleep(2)

def main():
    toggle_fuzzing_plugin(True)
    

if __name__=="__main__": 
    pass