# file : nodes.py
# 

import os
import subprocess
from threading import Thread
import time
import shutil
import sys

NODE_COUNT = 5
INIT_NODE_DELAY_TIME = 5
START_NODE_DELAY_TIME = 1
GET_ENODE_DELAY_TIME = 0.5

enode_arr = []

def make_node_dirs():
    for i in range(1, NODE_COUNT+1):
        path = os.path.join(".\\", "%0d"%i)
        if not os.path.exists(path):
            print("making dir " + path)
            os.mkdir(path)


def clean_all_dirs():
    for i in range(1, NODE_COUNT+1):
        path = os.path.join(".\\", "%0d"%i)
        if os.path.exists(path):
            shutil.rmtree(path)

def write_node_passwords(base_path):
    for i in range(1, NODE_COUNT+1):
        path = os.path.join(".\\", "%0d"%i)
        if os.path.exists(path):
            string = "node" + "%0d"%i
            full_path = path + "\\password.txt"
            if not os.path.exists(full_path):
                file = open(full_path, "w")
                file.write(string)
                file.close()

def write_node_new_scripts(base_path):
    for i in range(1, NODE_COUNT+1):
        path = os.path.join(".\\", "%0d"%i)
        if os.path.exists(path):
            datadir = os.path.dirname(base_path) + "\\" + "%d"%i
            passdir = os.path.dirname(base_path) + "\\" + "%d"%i + "\\" + "password.txt"
            string = "geth --datadir \"%s\""%datadir + " account new --password \"%s\""%passdir
            full_path = path + "\\new_account.bat"
            if not os.path.exists(full_path):
                file = open(full_path, "w")
                file.write(string)
                file.close()

def write_node_init_scripts(base_path):
    #geth --datadir ".\{%03d}\" init "..\00\DefaultGenesis.json"
    for i in range(1, NODE_COUNT+1):
        path = os.path.join(".\\", "%0d"%i)
        if os.path.exists(path):
            datadir = os.path.dirname(base_path) + "\\" + "%d"%i
            jsondir = os.path.dirname(base_path) + "\\" + "DefaultGenesis.json"
            string = "geth --datadir \"%s\""%datadir + " init " + "\"%s\""%jsondir
            print(path, string)
            full_path = path + "\\init_node.bat"
            if not os.path.exists(full_path):
                file = open(full_path, "w")
                file.write(string)
                file.close()            

def write_enode_scripts(base_path):
    for i in range(1, NODE_COUNT+1):
        path = os.path.join(".\\", "%0d"%i)
        if os.path.exists(path):
            keydir = os.path.dirname(base_path) + "\\" + "%d"%i + "\\geth\\nodekey"
            string = "bootnode --nodekey \"%s\""%keydir + " -writeaddress"
            full_path = path + "\\get_enode.bat"
            if not os.path.exists(full_path):
                file = open(full_path, "w")
                file.write(string)
                file.close()

def write_static_enode_scripts(base_path):
    for i in range(1, NODE_COUNT+1):
        path = os.path.join(".\\", "%0d"%i)
        if os.path.exists(path):
            full_path = path + "\\static-nodes.json"
            if not os.path.exists(full_path):
                file = open(full_path, "w")
                file.write("[\n")
                for enode in enode_arr:
                    if enode == enode_arr[-1]:
                        file.write("\t\"%s\""%enode + "\n")
                    else:
                        file.write("\t\"%s\""%enode + ",\n")
                file.write("]")
                file.close()

def write_node_run_scripts(base_path):
    for i in range(1, NODE_COUNT+1):
        path = os.path.join(".\\", "%0d"%i)
        if os.path.exists(path):
            #geth --identity "node {%03d}" --datadir ".\{%03d}\" --ipcpath geth{%03d} --port {30303+%03d} --nodiscover --networkid 6666 --http --http.corsdomain "*" 
            # -http.port {8545 + %03d} --http.api debug,eth,web3,personal,net,admin
            datadir = os.path.dirname(base_path) + "\\" + "%d"%i
            accs = os.listdir(datadir + "\\keystore")
            acc_name = accs[0][-40:-1] + accs[0][-1]

            full_path = path + "\\account.txt"
            if not os.path.exists(full_path):
                file = open(full_path, "w")
                file.write("0x%s"%acc_name)
                file.close()

            passdir = os.path.dirname(base_path) + "\\" + "%d"%i + "\\" + "password.txt"

            string = "start geth"
            string += " --identity \"node %d\""%i
            string += " --datadir \"%s\""%datadir
            string += " --syncmode full"
            string += " --ipcpath \"geth%d\""%i
            string += " --port \"%d\""%(30303+i)
            string += " --mine --miner.gasprice 0 --miner.gastarget 134217728"
            if i <= 10:
                string += " --miner.threads=1 --miner.etherbase=0x0000000000000000000000000000000000000000"
            # string += " --nodiscover"
            string += " --networkid 6666"
            string += " --http"
            string += " --http.addr \"0.0.0.0\""
            string += " --http.corsdomain \"*\""
            string += " --http.port %d"%(8545+i)
            string += " --http.api debug,eth,web3,personal,net,admin,miner"
            string += " --allow-insecure-unlock"
            string += " --rpc.allow-unprotected-txs"
            string += " --unlock \"0x%s\""%acc_name + " --password \"%s\""%passdir
            full_path = path + "\\run_node.bat"
            if not os.path.exists(full_path):
                file = open(full_path, "w")
                file.write(string)
                file.close()

def write_config_script(base_path):
    full_path = base_path + "\\config.txt"
    file = open(full_path, "w")
    for i in range(1, NODE_COUNT+1):
        print('123')
        string = "local" + "%0d"%i + ": {\n"
        string += "\thost: '127.0.0.1',\n"
        string += "\tport: %d"%(8545+i) + ",\n"
        string += "\tnetwork_id: '*',\n"
        string += "},\n"
        file.write(string)
    file.close()

def new_account(arg1, arg2):
    path = os.path.join(".\\", "%0d"%arg1)
    if os.path.exists(path):
        full_path = path + "\\new_account.bat"
        subprocess.call(full_path)

def init_one_node(arg1, arg2):
    path = os.path.join(".\\", "%0d"%arg1)
    if os.path.exists(path):
        full_path = path + "\\init_node.bat"
        subprocess.call(full_path)

def start_one_node(arg1, arg2):
    path = os.path.join(".\\", "%0d"%arg1)
    if os.path.exists(path):
        full_path = path + "\\run_node.bat"
        subprocess.call(full_path)

def init_process(arg1, arg2):
    new_account(arg1, arg2)
    init_one_node(arg1, arg2)
    # start_one_node(arg1, arg2)

def init_all_nodes():
    for i in range(1, NODE_COUNT + 1):
        t = Thread(target=init_process, args=(i, 0))
        t.daemon = True
        t.start()
        time.sleep(INIT_NODE_DELAY_TIME)

def get_process(arg1, arg2):
    path = os.path.join(".\\", "%0d"%arg1)
    if os.path.exists(path):
        full_path = path + "\\get_enode.bat"
        fh = os.popen(full_path)
        output = fh.read()
        enode_arr.append("enode://" + output[-129:-1] + "@127.0.0.1:" + "%d"%(30303+arg1))

def get_all_enodes():
    for i in range(1, NODE_COUNT + 1):
        t = Thread(target=get_process, args=(i, 0))
        t.daemon = True
        t.start()
        time.sleep(GET_ENODE_DELAY_TIME)

def run_process(arg1, arg2):
    start_one_node(arg1, arg2)

def run_all_nodes():
    for i in range(1, NODE_COUNT + 1):
        t = Thread(target=run_process, args=(i, 0))
        t.daemon = True
        t.start()
        time.sleep(START_NODE_DELAY_TIME)

print("#######" + sys.argv[1] + "#######")
print("#######" + sys.argv[2] + "#######")

NODE_COUNT = int(sys.argv[2])

clean_all_dirs()
make_node_dirs()
write_node_passwords(sys.argv[1])
write_node_new_scripts(sys.argv[1])
write_node_init_scripts(sys.argv[1])
init_all_nodes()

write_enode_scripts(sys.argv[1])

get_all_enodes()
write_static_enode_scripts(sys.argv[1])
write_node_run_scripts(sys.argv[1])
run_all_nodes()
# write_config_script(sys.argv[1])