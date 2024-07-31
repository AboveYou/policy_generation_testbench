import argparse
import os
import shutil
import subprocess
import signal
import json
import shutil
import time

def teardown(dir_to_rmrf):
  print('Removing %s' % dir_to_rmrf)
  try:
    shutil.rmtree(dir_to_rmrf)
  except:
    print('Couldn\'t remove %s' % dir_to_rmrf)

def signal_handler(sig, frame):
  exit()

if __name__ == '__main__':
  ### Register SIGINT handler
  signal.signal(signal.SIGINT, signal_handler)

  ### argument parser
  parser = argparse.ArgumentParser(description='Syscall-finder tool that uses AFL to find syscalls in a proviede binary.')
  parser.add_argument('path_to_bin', type=str, help='Path to binary to find system calls for')
  parser.add_argument('-i', '--input_data', type=str, help='Path to input data that helps create useful cases for AFL')
  parser.add_argument('-k', '--keep', action='store_true', help='Set this flag to keep files from AFL in')
  parser.add_argument('-d', '--duration', type=int, default=30, help='''Duration for fuzzing in minutes.
      Increased duration results in increased coverage. Default=30''')
  args, argv = parser.parse_known_args()

  ### directory setup
  current_dir = os.getcwd()
  #bin_name = os.path.basename(args.path_to_bin)
  bin_name = os.path.basename(args.path_to_bin)
  #print(bin_name)
  if not os.path.isfile(args.path_to_bin):
    print('No valid binary provided!')
    exit(1)
  abs_path_of_bin = os.path.abspath(args.path_to_bin)
  print('Setting up directories')
  ## create AFL directories
  #print('- Creating AFL directories')
  # in
  #print('- - Creating in directory')
  #path_in = os.path.join(current_dir, 'afl-dirs-%s' % bin_name, 'in')
  #if not os.path.exists(path_in):
  #  os.makedirs(path_in)
  
  # out
  #print('- - Creating out directory')
  #path_out = os.path.join(current_dir, 'afl-dirs-%s' % bin_name, 'out')
  #if not os.path.exists(path_out):
  #  os.makedirs(path_out)

  # syscall results
  result_dir = os.path.join('/tmp/syscall-finder', bin_name)
  if os.path.exists('/tmp/syscall-finder'):
    shutil.rmtree('/tmp/syscall-finder')
  
  os.makedirs(result_dir)

  print('- Moving input data to in')
  ## move input data to in
  if args.input_data:
    if os.path.exists(args.input_data):
      shutil.copy(args.input_data, path_in)
    print('Success!')

  ### restart autitd service for auparse plugin
  print('Restarting auditd')
  subprocess.call(['sudo', 'service', 'auditd', 'restart'])

  ### fuzz with log
  print('Starting fuzzing process')
  log_duration = 5 # log should probably run initial specific test cases
  print('- Running initial log')
  try:
    log_run = subprocess.call(['./syscall_finder/seccomp-wrapper', 'log', bin_name, abs_path_of_bin, argv[0]], timeout=log_duration)
  except:
    print('Initial log run stopped')

  ### fuzz with kill
  #print('- Running fuzzing process for %i minutes' % args.duration)
  #try:
   # subprocess.run(['afl-fuzz', '-i', path_in, '-o', path_out, './seccomp-wrapper', 'kill', bin_name, abs_path_of_bin], 
       # timeout=(args.duration*60)-log_duration)
  #except:
    #print('Stopped fuzzing process')

  ### create output
  print('Collecting results')

  ## find newest file (highest number as name)
  newest_syscalls = 0
  for filename in os.listdir(result_dir):
    new_file_name_as_int = int(filename)
    newest_syscalls = new_file_name_as_int if newest_syscalls < new_file_name_as_int else newest_syscalls
  ## loop through file to generate json
  syscalls_file_name = os.path.join(result_dir, str(newest_syscalls))
  syscalls_dict = {}
  print(f"\n\nSyscall Name is {syscalls_file_name}\n\n")
  while not os.path.exists(result_dir): 
    time.sleep(1)
  try:
    with open(syscalls_file_name, 'r') as f:
      syscall_nr = 0
      for line in f:
        for ch in line:
          ausyscall = subprocess.run(['ausyscall', str(syscall_nr)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
          if ausyscall.stderr != 'Unknown':
            syscalls_dict[ausyscall.stdout.decode('utf-8').strip()] = {
              "number": str(syscall_nr),
              "x86": "allowed" if (ch == '1' or ch == '3') else "blocked",
              "x86_64": "allowed" if (ch == '2' or ch == '3') else "blocked"
            }
            syscall_nr += 1
  except FileNotFoundError: 
    print("FileNotFoundError")
    exit(-1)
  print('Pushing results to file')
  output_file_name = os.path.join(current_dir, bin_name + '_syscalls.json')
  output_file = open(output_file_name, 'w')
  json.dump(syscalls_dict, output_file)
  output_file.close()

  ## remove fragmets
  teardown(result_dir)
  teardown(os.path.split(path_in)[0])
