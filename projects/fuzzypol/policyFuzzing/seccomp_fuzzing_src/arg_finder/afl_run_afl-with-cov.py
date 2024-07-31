import io
import re
import shlex
import subprocess
import sys
import multiprocessing
import os
import time
import threading
import shutil
import random, string


progress_KLEE = 0
result_KLEE = None

Anzahl_der_Kerne = multiprocessing.cpu_count() - 1
CPU_Count_str = str(Anzahl_der_Kerne)
cmd_argv_len1 = len(sys.argv)
cmd_argv_1 = []
cmd_argv_1 = sys.argv
print(cmd_argv_len1)
No_Replay_B = 0
Exported_Args= []
KLEE_Target_Programm = str(cmd_argv_1[1])
if(cmd_argv_len1 > 2):
    KLEE_Target_Programm = str(cmd_argv_1[1])
    KLEE_Target_Programm_B = str(cmd_argv_1[2])
    STRING_statt_KLEE = str(cmd_argv_1[4])
    STRING_AFL_COV_GCC_SRC = str(cmd_argv_1[5]) + "src/"
    STRING_AFL_COV_GCC_Dir = str(cmd_argv_1[5]) + "GCC/src/"
    STRING_AFL_COV_GCC_Binary = STRING_AFL_COV_GCC_Dir + KLEE_Target_Programm_B
    if(cmd_argv_len1 > 3):
        KLEE_Target_Programm_args = str(cmd_argv_1[3])
    else:
        KLEE_Target_Programm_args = "5"

    STRING_DURATION = str(cmd_argv_1[6])
else:
    No_Replay_B += 1
    print("No Klee Replay Possible without normal Binary")

print ("CMD Argv: ")
print (cmd_argv_1)
print("")

print("Call: ")
print(KLEE_Target_Programm)

print("")

cmd_argv_1_first_call = KLEE_Target_Programm

print ("Use KLEE-Replay on:")
print (KLEE_Target_Programm_B)
print("")
INPUT_DIR= "AFLDir/AFLIn"
OUTPUT_DIR= "AFLDir/AFLOut"
#{}\
AFL_Fuzzing_Slave_Instance=1
def Prepare_KLEE_env():
    try:
        print("(+) Prepare sandbox Step 1")
        KLEE_cmd_sandbox_tar = "tar -xzf sandbox.tgz"
        print("(+) Prepare sandbox Step 2")
        KLEE_cmd_sandbox_tar_1 = shlex.split(KLEE_cmd_sandbox_tar)
        KLEE_cmd_sandbox_tar_exec = subprocess.Popen(KLEE_cmd_sandbox_tar_1)
        time.sleep(4)
        print("(+) CP sandbox Step 3")
        KLEE_cmd_sandbox= "cp -r sandbox/ /tmp/"
        KLEE_cmd_sandbox_1 = shlex.split(KLEE_cmd_sandbox)
        KLEE_cmd_sandbox_cp_exec = subprocess.Popen(KLEE_cmd_sandbox_1)
        time.sleep(4)
    except:
        print("(-) Failed CP sandbox")
    else:
        try:
            print("(+) Prepare env")
            KLEE_cmd_env_command = "env -i /bin/bash -c '(source testing-env.sh; env > test.env)' "
            KLEE_cmd_env_command_1 = shlex.split(KLEE_cmd_env_command)
            KLEE_cmd_Run_env = subprocess.Popen(KLEE_cmd_env_command_1)
        except:
            print("(-) env failed")

def RUN_AFL_COV_1():
    global AFL_COV_Variant
    print("Executing AFL-cov Script on: ")
    print(AFL_COV_Variant)
    print(" ")
    #AFL_COV_COMMAND_BLANK = "timeout " + AFL_Cov_argv_3 + " ./afl-cov -d "+ "AFLDir/AFLOut/fuzzer"+ AFL_Cov_argv_1 +" " + "--live " + "--coverage-cmd " + "\"" + AFL_Cov_argv_4 + " " + AFL_Cov_argv_2 + " AFL_FILE\"" + " " + "--code-dir " +  AFL_Cov_args_6 + " --overwrite --enable-branch-coverage --cover-corpus --coverage-at-exit --coverage-include-lines " + "--src-file " + AFL_Cov_args_5 + " " +  "--genhtml-path /bin/genhtml --lcov-path /bin/lcov -v"
    thread_AFL_cov_1 =threading.Thread(target=subprocess.run([AFL_COV_Variant], shell=True))
    print(" Executed AFL-Coverage Tool")


def RUN_KLEE(Programm_name, Programm_name_real, Programm_arguments, duration):
    cmd_argv_1_RUN_KLEE = " " + str(Programm_name)
    cmd_argv_2_RUN_KLEE = str(Programm_name_real)
    cmd_argv_3_RUN_KLEE = str(Programm_arguments)
    print("Executing KLEE Script on: ")
    print(Programm_name)
    print(" ")
    try:
        KLEE_cmd_Run_Sym_Exec = subprocess.run(["./Run_Klee.sh", cmd_argv_1_RUN_KLEE, cmd_argv_2_RUN_KLEE, cmd_argv_3_RUN_KLEE, duration], check=True) #timeout=40*60
        time.sleep(15)
    except subprocess.TimeoutExpired:
        time.sleep(5)
        print(" ")
        print(" Alternative Harvesting  Process of Commandline Interfaces with ktest-tool")
        KLEE_out_replay_txt_name = cmd_argv_2_RUN_KLEE + "replayAlternativ.txt"
        KLEE_out_extract_cmd = "(ktest-tool klee-last/*.ktest) 2>&1 | grep text: >> " + KLEE_out_replay_txt_name
        print("Try ktest-tool on klee-last directory with: ")
        print(" ")
        print(KLEE_out_extract_cmd)
        print(" ")
        KLEE_out_extract_cmd_Exec = subprocess.run([KLEE_out_extract_cmd], shell=True)
        print(" ")
        print(" Alternativer Ablauf abgeschlossen")
    print ("KLEE Script End")

Extracted_Params= []
Extracted_Params_KLEE_only= []
Extracted_Params_STRING_only= []

def KLEE_RUN1(Programm, Programm_bc, args, KLEE_RUN_TIME, batch_time, Max_Z3_Time):
    KLEE_run_Command_cmd_Exec = "time klee --simplify-sym-indices --write-cov --output-module --max-memory=10000 --disable-inlining --optimize --use-forked-solver --use-cex-cache --libc=uclibc --posix-runtime --libcxx --readable-posix-inputs --external-calls=all --only-output-states-covering-new --env-file=test.env --run-in-dir=/tmp/sandbox --max-sym-array-size=4096 --max-time="+ str(KLEE_RUN_TIME) +"min --watchdog --max-memory-inhibit=false --max-static-fork-pct=1 --max-static-solve-pct=1 --max-static-cpfork-pct=1 --switch-type=internal --search=random-path --search=nurs:rp --use-batching-search --batch-time="+ str(batch_time) + "s --silent-klee-assume --write-test-info --zero-seed-extension --named-seed-matching --allow-seed-extension --pgso --use-fast-cex-solver --solver-optimize-divides --speculate-one-expensive-inst --store-to-load-forwarding-conflict-detection --optimize-array=all --switch-to-lookup --trap-unreachable --max-solver-time=" + str(Max_Z3_Time)+ "s --unroll-runtime --use-cfl-aa=both --use-incomplete-merge --x86-speculative-load-hardening --use-iterative-deepening-time-search --use-newer-candidate --mul-constant-optimization --ffast-math --mergefunc-use-aliases --loop-vectorize-with-block-frequency --expensive-combines --enable-unswitch-cost-multiplier --allow-unroll-and-jam --asan-recover --threads=$(nproc) " + "./"+ str(Programm_bc) + " --sym-arg " + str(args)
    KLEE_run_Timeout_cmd_Exec = subprocess.run([KLEE_run_Command_cmd_Exec], shell=True)
    time.sleep(10)
    KLEE_run_Timeout_cmd_Exec = subprocess.run(["export KLEE_REPLAY_TIMEOUT=30"], shell=True)


def KLEE_AAA():
    global AFL_run_Variants
    print(" Funktion: ")
    thread_K =threading.Thread(target=subprocess.run([AFL_run_Variants], shell=True))

def Extract_KLEE_params(prog_name):
    #print(" ")
    global Extracted_Params 
    global Extracted_Params_KLEE_only
    global Extracted_Params_STRING_only
    #print("(+) Beginning Extraction of the Arguments in Python List")
    InputArgs= io.StringIO()
    InputArgs1= io.StringIO()
    InputArgs2= io.StringIO()
    InputArgs_KLEE_only= io.StringIO()
    InputArgs_STRING_only= io.StringIO()
    Argslist= []
    cleanArgslist= []
    cleanArgslist1= []
    cleanArgslist4= []
    cleanArgslist5= []
    cleanArgslist2= io.StringIO()
    Argslist1= []
    Argslist3= []
    Argslist4= []
    Argslist4_set= []
    Argslist_KLEE_only= []
    Argslist_STRING_only= []
    cleanArgslist3= []
    cleanArgslist_test = []
    replay_file_name = str(prog_name) + "replay.txt"
    replay_file_name_KLEE = "KLEEArgs1.txt"
    STRING_Args_txt_file="Args.txt"
    #print('Start des Einlesens des KLEE Corpus')
    replay_file_name_cmd = str(replay_file_name)

    with open(STRING_Args_txt_file, 'r') as Klee_input_String:
        InputArgs_STRING_only= Klee_input_String.read()
        for line in Klee_input_String:
            InputArgs_STRING_only = Klee_input_String.read()

    with open(replay_file_name_KLEE, 'r') as Klee_input1:
        InputArgs_KLEE_only= Klee_input1.read()
        for line in Klee_input1:
            InputArgs_KLEE_only = Klee_input1.read()

    print(' ')
    # KLEE PARAMS
    Argslist_KLEE_only+= re.findall((r'-{0,2}\w{1,30}'),InputArgs_KLEE_only)
    Extracted_Params_KLEE_only=list(set(Argslist_KLEE_only))
    # STRINGS PARAMS
    Argslist_STRING_only+=  re.findall((r'-{1,2}\w{1,20}'),InputArgs_STRING_only)
    Argslist_STRING_only+=  re.findall((r'-{1,2}\w{1,20}-{1,2}\w{1,20}'),InputArgs_STRING_only)
    Argslist_STRING_only+=  re.findall((r'-{0,2}\w{1,20}-{1,2}\w{1,20}-{1,2}\w{1,20}'),InputArgs_STRING_only)
    Extracted_Params_STRING_only+=list(set(Argslist_STRING_only))
    #Write KLEE Input Fuzz Corpus
    Myfile=open('fuzzin.txt','w')
    for element in Extracted_Params_KLEE_only:
        Myfile.write(element)
        Myfile.write('\n')
    Myfile.close()
    # Write String Param Corpus
    Myfile1=open('fuzzin_string.txt','w')
    for element in Extracted_Params_STRING_only:
        Myfile1.write(element)
        Myfile1.write('\n')
    Myfile1.close()


print(" [+] Call Prepare_KLEE_env Function")
Prepare_KLEE_env()

print(" [+] Call RUN_KLEE Function")

thread_K =threading.Thread(target=RUN_KLEE(KLEE_Target_Programm, KLEE_Target_Programm_B, KLEE_Target_Programm_args, STRING_DURATION))

time.sleep(3)

print(" [+] Finished RUN_KLEE Function")

if(No_Replay_B):
    print (" [-] can't call KLEE Replay")
    sys.exit()
else:
    print(" [+] VOR KLEE Replay")
    # Currently obsolete because its included in Bash Script
    #Run_KLEE_ARGS(KLEE_Target_Programm_B)

print(" [+] Call Extract_KLEE_params Function")

Extract_KLEE_params(KLEE_Target_Programm_B)

print("Exported KLEE Args:")
print(" ")
print(Extracted_Params_KLEE_only)
print(" ")

print("Exported STRING Args:")
print(" ")
print(Extracted_Params_STRING_only)
print(" ")

# Beginn Fuzzing Section
'''print(" [+] Beginn Fuzzing Step 1")

print(" [+] Run Fuzzer")

# RUN AFL MASTER
# Param 1 : pfad zum AFL Instrumentalisierten Binary
AFL_MASTER_PROGRAMM= "./"+str(KLEE_Target_Programm_B)
# PARAM 2 : Duration of Master Instance
AFL_MASTER_DURATION = 60
# RUN AFL SLAVE
# Param 1 : pfad zum AFL Instrumentalisierten Binary
AFL_SLAVE_PROGRAMM= "./"+str(KLEE_Target_Programm_B)
# Param 2 : Parameter mit denen AFL aufgerufen werden soll
AFL_PARAM_COUNTER= 0
# Param 3 : Instance ( Counter der Slave AFL Instanzen, starts with 1)
AFL_SLAVE_INSTANCE= 0
# Param 4 : Duration of Slave Instances
#AFL_SLAVE_DURATION = 300
AFL_SLAVE_DURATION = 60
# Param 5 : cpu (probably obsolet with this Version)
AFL_SLAVE_CPU= 14
#AFL_PARAM = str(Extracted_Params[AFL_PARAM_COUNTER])
print("DEBUG Early Exit")
WHILE_BREAKER = len(Extracted_Params_KLEE_only)
#AFL_SLAVE_DURATION= (WHILE_BREAKER / int(AFL_MASTER_DURATION) )
AFL_SLAVE_SLEEPTIME= (AFL_SLAVE_DURATION /int(Anzahl_der_Kerne)) * 2
print(AFL_SLAVE_SLEEPTIME)
NEW_STRING_ONLY_List=[]
#afl_run_slaves_silent="export AFL_QUIET=1"
#KLEE_run_Timeout_cmd_Exec = subprocess.run([afl_run_slaves_silent])
time.sleep(2)
STRINGS_Methode=0
NUMBER_OF_ARGUMENTS=0

AFL_COV_DURATION=0

if(STRING_statt_KLEE=="S"):
    STRINGS_Methode=1
    NEW_STRING_ONLY_List= [i for i in Extracted_Params_STRING_only if i not in Extracted_Params_KLEE_only]
    # Adjust While Breaker to new Params
    WHILE_BREAKER= len(NEW_STRING_ONLY_List)
    NUMBER_OF_ARGUMENTS= len(NEW_STRING_ONLY_List)
    print("STRING only Methode aktiv: ")
    print(" ")
    print(NEW_STRING_ONLY_List)
    print(" ")
elif(STRING_statt_KLEE=="K"):
    STRINGS_Methode=0
    NUMBER_OF_ARGUMENTS= len(Extracted_Params_KLEE_only)
    print(" KLEE pur Methode aktiv")
elif(STRING_statt_KLEE=="SK"):
    STRING_Methode=1
    WHILE_BREAKER= len(Extracted_Params_STRING_only)
    NUMBER_OF_ARGUMENTS= len(Extracted_Params_STRING_only)
    print(" STRING und KLEE Methode aktiv")
elif(STRING_statt_KLEE=="KS"):
    STRING_Methode=1
    WHILE_BREAKER= len(Extracted_Params_STRING_only)
    NUMBER_OF_ARGUMENTS= len(Extracted_Params_STRING_only)
    print(" STRING und KLEE Methode aktiv")
else:
    STRINGS_Methode=0
    print(" Default KLEE pur Methode aktiv")
    NUMBER_OF_ARGUMENTS= len(Extracted_Params_KLEE_only)

AFL_SLAVE_DURATION = int(AFL_MASTER_DURATION / NUMBER_OF_ARGUMENTS) * ((int(Anzahl_der_Kerne)*2)/3)

# AFL_SLAVE_DURATION = int(AFL_MASTER_DURATION / NUMBER_OF_ARGUMENTS) * int(Anzahl_der_Kerne)
print(" Number of Arguments")
print(NUMBER_OF_ARGUMENTS)
print(" ")

print(" AFL Slave Duration in Seconds")
print(AFL_SLAVE_DURATION)
print(" ")
time.sleep(5.0)

start_time = time.time()
while WHILE_BREAKER!=0:
    AFL_PARAM_ROH=" "
    for Param_Element in range(0, Anzahl_der_Kerne):
        if (STRING_statt_KLEE=="SK"):
            AFL_PARAM_ROH_KLEE_only= Extracted_Params_STRING_only[AFL_PARAM_COUNTER]
            print("Nutze STRING Argumente")
        elif (STRING_statt_KLEE=="KS"):
            AFL_PARAM_ROH_KLEE_only= Extracted_Params_STRING_only[AFL_PARAM_COUNTER]
            print("Nutze STRING Argumente")
        elif STRING_statt_KLEE=="S":
            AFL_PARAM_ROH_KLEE_only= NEW_STRING_ONLY_List[AFL_PARAM_COUNTER]
            print("Nutze String only Argumente")
        else:
            AFL_PARAM_ROH_KLEE_only= Extracted_Params_KLEE_only[AFL_PARAM_COUNTER]
            print(" Nutze nur KLEE Argumente pur")
        #AFL_PARAM_ROH_KLEE_only= Extracted_Params_KLEE_only[AFL_PARAM_COUNTER]
        print("AFL Param Roh")
        print(AFL_PARAM_ROH)
        print(" ")
        print("AFL Param KLEE only:")
        print(AFL_PARAM_ROH_KLEE_only)
        print(" ")
        AFL_PARAM = str(AFL_PARAM_ROH)
        AFL_PARAM_KLEE_only= str(AFL_PARAM_ROH_KLEE_only)
        cpu_nr= str(Param_Element)
        AFL_CPU_SLEEP_TIMER= 0
        if AFL_SLAVE_INSTANCE == 0:
            AFL_SLAVE_DURATION= AFL_MASTER_DURATION
            AFL_COV_DURATION= AFL_MASTER_DURATION + 600 
            print("AFL RUNs as MASTER Instance:")
        else:
            #AFL_SLAVE_DURATION = int(AFL_MASTER_DURATION / NUMBER_OF_ARGUMENTS) * int(Anzahl_der_Kerne)
            AFL_SLAVE_DURATION = int(AFL_MASTER_DURATION / NUMBER_OF_ARGUMENTS) * ((int(Anzahl_der_Kerne)*2)/3)
            AFL_SLAVE_DURATION_CPU_COOLDOWN_TIME = int(AFL_MASTER_DURATION / NUMBER_OF_ARGUMENTS) * (int(Anzahl_der_Kerne)/2)
            AFL_COV_DURATION= AFL_SLAVE_DURATION + 130
        print(" Vor Main Aufruf von run_AFL Python Function")
        print(" ")
        if WHILE_BREAKER-AFL_PARAM_COUNTER == 0:
            WHILE_BREAKER=0
            break;
        if AFL_SLAVE_INSTANCE == 0:
            AFL_run_Variants= "afl-fuzz -i "+ "AFLDir/AFLIn " + "-o " + "AFLDir/AFLOut "+" "+ "-p exploit " + "-V " + str(AFL_SLAVE_DURATION) + " " +"-t 500 " + "-M fuzzer" + str(AFL_SLAVE_INSTANCE) + " "+"-- " +"AFLDir/"+ str(KLEE_Target_Programm_B) + " @@"
            #AFL_run_Variants="afl-fuzz -i "+ "AFLDir/AFLIn " + "-o " + "AFLDir/AFLOut "+ "-x "+"AFLDir/testcases.dict" + " "+ "-p mmopt " +"-L 5 "+ "-V " + str(AFL_SLAVE_DURATION) + " " +"-t 500 " + "-M fuzzer" + str(AFL_SLAVE_INSTANCE) + " "+"-- " +"AFLDir/"+ str(KLEE_Target_Programm_B) + " @@"
            print(AFL_run_Variants)
            print("Start Master AFL")
        else:
            AFL_run_Variants=" afl-fuzz -i "+ "AFLDir/AFLIn " + "-o " + "AFLDir/AFLOut "+ " "+ "-p rare " +"-V " + str(AFL_SLAVE_DURATION) +" -d"+ " " + "-t 150 " + "-S fuzzer" + str(AFL_SLAVE_INSTANCE) + " "+"-- " +"AFLDir/" + str(KLEE_Target_Programm_B) + " " + AFL_PARAM_KLEE_only +" @@"
            #AFL_run_Variants="afl-fuzz -i "+ "AFLDir/AFLIn " + "-o " + "AFLDir/AFLOut "+ "-x "+"AFLDir/testcases.dict" + " "+ "-p fast " +"-V " + str(AFL_SLAVE_DURATION) +" -d"+ " " + "-t 150 " + "-S fuzzer" + str(AFL_SLAVE_INSTANCE) + " "+"-- " +"AFLDir/" + str(KLEE_Target_Programm_B) + " " + AFL_PARAM_KLEE_only +" @@"
            print(AFL_run_Variants)
            print(" Start Slave AFL")
        t = threading.Timer(0.0, KLEE_AAA, args=[]).start()
        
        if AFL_SLAVE_INSTANCE == 0:
            time.sleep(15.0)
        else:
            time.sleep(10.0)
        if AFL_SLAVE_INSTANCE == 0:
            # Add eventuell --background later
            AFL_COV_Variant = " ./afl-cov -d "+ "AFLDir/AFLOut/fuzzer"+ str(AFL_SLAVE_INSTANCE) +" " + "--live " + "--coverage-cmd " + "\"" + STRING_AFL_COV_GCC_Binary  + " AFL_FILE\"" + " " + "--code-dir " + STRING_AFL_COV_GCC_Dir  + " --overwrite --enable-branch-coverage --cover-corpus --coverage-include-lines " + "--src-file " + STRING_AFL_COV_GCC_SRC + " " +  "--genhtml-path /bin/genhtml --lcov-path /bin/lcov -v --background"
        else:
            AFL_COV_Variant = "timeout " + str(AFL_COV_DURATION) + " ./afl-cov -d "+ "AFLDir/AFLOut/fuzzer"+ str(AFL_SLAVE_INSTANCE) +" " + "--live " + "--coverage-cmd " + "\"" + STRING_AFL_COV_GCC_Binary  + " " + AFL_PARAM_KLEE_only + " AFL_FILE\"" + " " + "--code-dir " + STRING_AFL_COV_GCC_Dir  + " --overwrite --enable-branch-coverage --cover-corpus --coverage-include-lines " + "--src-file " + STRING_AFL_COV_GCC_SRC + " " +  "--genhtml-path /bin/genhtml --lcov-path /bin/lcov -v --disable-coverage-init --background"
        # Test Coverage Tool in Parallel
        threading.Timer(0.0, RUN_AFL_COV_1, args=[]).start()
        # ADDED IF Condition
        #AFL_CPU_SLEEP_TIMER= AFL_CPU_SLEEP_TIMER+1
        #if (int(AFL_CPU_SLEEP_TIMER)==10):
            #AFL_CPU_SLEEP_TIMER = 0
            #WAIT_TIME_SLAVE = int(int(AFL_SLAVE_DURATION) / 2)
            #print("Waiting for cpu Cores to cool down ...!")
            #time.sleep(WAIT_TIME_SLAVE)
        print(" Passed Main AFL Call")

        #time.sleep(AFL_SLAVE_SLEEPTIME)
        AFL_SLAVE_INSTANCE= AFL_SLAVE_INSTANCE+1
        AFL_PARAM_COUNTER= AFL_PARAM_COUNTER+1
        time.sleep(2)
    if WHILE_BREAKER-AFL_PARAM_COUNTER == 0:
        break;
    try:
        subprocess.check_call(["afl-whatsup", "-s", OUTPUT_DIR])
    except:
        pass
    if (WHILE_BREAKER-AFL_PARAM_COUNTER+1==0):
        break;
    #SLEEP_VARIABLE_SLAVE= int(AFL_SLAVE_DURATION) / 10
    # Wait for CPUs
    time.sleep(AFL_SLAVE_DURATION)
    print(" Waiting for CPUs to finish next batch of AFL Runs")

    if (time.time() - start_time) > float(STRING_DURATION):
        break

print(" [+] Run Fuzzer Ended")
'''