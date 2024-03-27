import sys, os, psycopg, json,subprocess
from dotenv import load_dotenv

## Utility Functions

## Return Test Configuration
def get_settings():
    port_n1 = 6432
    port_n2 = 6433
    host_n1 = "127.0.0.1"
    host_n2 = "127.0.0.1"
    db = "mydb"
    usr = "admin"
    pw = "passwd"
    repuser = os.popen('whoami').read() 
    pgv = "16"
    repo = "upstream"
    return port_n1, port_n2, host_n1, host_n2, db, usr, pw, repuser, pgv, repo

def set_env():
    load_dotenv(dotenv_path='lib/config.env')


## abruptly terminate with a codified message
def exit_message(p_msg, p_rc=1):
    if p_rc == 0:
       print(f"INFO {p_msg}")
    else:
       print(f"ERROR {p_msg}")
    sys.exit(p_rc)

def run_home_cmd(msg, cmd, node_path):
    print(cmd) 
    print(node_path) 
    rc = os.system(f"{node_path}/pgedge {cmd}")
    if rc != 0:
       exit_message(f"Failed on step: {msg}",1) 
    return rc 
       
## Run functions on both nodes
def run_home_err(msg, cmd, node_path):
    print(cmd)
    result = subprocess.run(f"{node_path}/pgedge {cmd}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result  

  
## Run functions on both nodes
def run_cmd(msg, cmd, node_path):
    print(cmd)
    result = subprocess.run(f"{node_path}/pgedge/pgedge {cmd}", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return result         
'''

## Run  functions on both nodes
def run_cmd(msg, cmd, node_path):
    print(cmd) 
    rc = os.system(f"{node_path}/pgedge/pgedge {cmd}")
    if rc != 0:
       exit_message(f"Failed on step: {msg}",1) 
       
       
## Get two psql connections
def get_pg_connection():
  port_n1, port_n2, host_n1, host_n2, db, usr, pw, repuser, pgv, repo = get_settings()
  try:
    con1 = psycopg.connect(dbname=db, user=usr, host=host_n1, port=port_n1, password=pw, autocommit=False)
    con2 = psycopg.connect(dbname=db, user=usr, host=host_n2, port=port_n2, password=pw, autocommit=False)
  except Exception as e:
    exit_message(e)
  return(con1, con2)
'''

 
## Get two psql connections
def get_pg_con(host,dbname,port,pw,usr):
  #port, port_n2, host_n1, host_n2, db, usr, pw, repuser, pgv, repo = get_settings()
  try:
    con1 = psycopg.connect(dbname=dbname, user=usr, host=host, port=port, password=pw, autocommit=False)
    #con2 = psycopg.connect(dbname=db, user=repuser, host=host_n2, port=port_n2, password=pw, autocommit=False)
  except Exception as e:
    exit_message(e)
  return(con1)

## Run psql on both nodes
def run_psql(cmd1,con1):
    #con1 = get_pg_connection()  
    try:
        cur1 = con1.cursor()
        cur1.execute(cmd1)
        print(json.dumps(cur1.fetchall()))
        ret1 = 0
        cur1.close()
    except Exception as e:
        exit_message(e)
    
    try:
        con1.close()
        #con2.close()
    except Exception as e:
        pass
    return ret1
    
## Run psql
def write_psql(cmd,host,dbname,port,pw,usr):
    ret = 1
    con = get_pg_con(host,dbname,port,pw,usr)
    try:
        cur = con.cursor()
        print(cur)
        cur.execute(cmd)
        ret = 0
        con.commit()
        cur.close()
    except Exception as e:
        exit_message(e)

    try:
        con.close()
    except Exception as e:
        pass
    return ret


## Run psql
def read_psql(cmd,host,dbname,port,pw,usr):
    con = get_pg_con(host,dbname,port,pw,usr)
    try:
        cur = con.cursor()
        cur.execute(cmd)
        ret = json.dumps(cur.fetchall())
        cur.close()
    except Exception as e:
        exit_message(e)

    try:
        con.close()
    except Exception as e:
        pass
    return ret


def cleanup_sub(db):
    cmd = "SELECT sub_name FROM spock.subscription"
    ret_n1, ret_n2 = run_psql(cmd)
    if "sub_n1n2" in str(ret_n1):
        cmd1 = f"spock sub-drop sub_n1n2 {db}"
        cmd2 = None
        if "sub_n2n1" in str(ret_n2):
            cmd2 = f"spock sub-drop sub_n2n1 {db}"
        run_cmd("Drop Subs",cmd1,cmd2)
        
        
def contains(haystack, needle):
    print(f'haystack = ({haystack})')
    print(f'needle = ({needle})')
    
    if haystack is None or needle is None or len(haystack) == 0 or len(needle) == 0:
        return 0

    if haystack.find(needle) != -1:
        print('Haystack and needle both have content, and our value is found - this case correctly returns true')
        return 1
    else:
        print('Haystack and needle both have content, but our value is not found - returning 0 as it should')
        return 0
        
        
        
        
        

def needle_in_haystack(haystack, needle):
    if needle in str(haystack):
      print("pass")
      exit_message("Pass", p_rc=0)
    else:
      exit_message("Fail", p_rc=1)
