#!/usr/bin/env python3
# coding: utf-8

TESTUSERNAME="testing"
CONFDIR="/var/src/benchmark"

TMPDIR="/tmp/.benchmark_conf_dir.conf"

tests=  [
        'NUMERIC SORT',
        'STRING SORT',
        'BITFIELD',
        'FP EMULATION',
        'FOURIER',
        'ASSIGNMENT',
        'IDEA',
        'HUFFMAN',
        'NEURAL NET',
        'LU DECOMPOSITION',
        ]

def parse_args():
    global args
    from argparse import ArgumentParser
    from socket import gethostname
    ap=ArgumentParser()
    ap.add_argument("-t","--testname",default=gethostname())
    ap.add_argument("-u","--username",default=TESTUSERNAME)
    args=ap.parse_args()

def print_compare(data):
    keys=data['handy'].keys()
    print("{:15.15} {}".format("test","[handy/dusteater]"))
    for k in keys:
        z0=(sum(a['handy'][k])/len(a['handy'][k]))
        z1=(sum(a['dusteater'][k])/len(a['dusteater'][k]))
        print("{:15.15} {:.1f}".format(k,z0/z1))


                

def run_test(resultfilepath):
    from subprocess import check_output,check_call,call
    from os import makedirs
    from os import readlink,getpid,getuid
    from os.path import dirname,islink
    #confdir=dirname(readlink("/proc/"+str(getpid())+"/exe"))
    confdir=CONFDIR
    makedirs(TMPDIR,exist_ok=True)
    config_file_name="B.CONF"
    dest_path  = TMPDIR+"/"+config_file_name
    source_path = confdir+"/"+config_file_name
    with open(source_path,"rb") as f:
        confcontent=f.read()
    cmd=[ 'sudo', 'chown',"-R",args.username+":"+str(getuid()), TMPDIR ]
    check_call(cmd)
    print(cmd)
    cmd=[ 'sudo', 'chmod',"-R",'g+rw', TMPDIR ]
    print(cmd)
    call(cmd)
    with open(dest_path,"wb") as f:
        f.write(confcontent)
    cmd=[ 'sudo', 'chmod','g+rw', dest_path ]
    print(cmd)
    call(cmd)
    cmd=[ 'sudo', 'nice', '-n', '-5', 'sudo', '-u', args.username , 'nbench', '-cB.CONF']
    print(cmd)
    output=check_output(cmd,cwd=TMPDIR)
    with open(resultfilepath,"wb") as f:
        f.write(output)

def read_data(resultfilepath):
    with open(resultfilepath) as f:
        data=f.read()
    lines=data.strip().split("\n")
    from pprint import pprint
    data_1={}
    for line in lines:
        for t in tests:
            if not t in data_1:
                data_1.update({t:[]})
            if line.find(t) != -1:
                line_parts = line.split(":")
                app=float(line_parts[1].strip())
                data_1[t].append(app)
    return data_1


if __name__=="__main__":
    parse_args()
    from os.path import isfile,exists
    from os import listdir
    from pprint import pprint

    # optionally run tests
    resultfilepath=TMPDIR+"/"+args.testname+".result"
    if not exists(resultfilepath):
        run_test(resultfilepath)
    
    # determine resultfiles
    dirlist=listdir(TMPDIR)
    resultfiles=[]
    for thing in dirlist:
        f=TMPDIR+"/"+thing
        if thing[-7:]==".result" and isfile(f):
            resultfiles.append((thing[:-7],f))
    print("resultfiles="+str(resultfiles))

    # read results
    data={}
    for name, resultfile in resultfiles:
        data.update({ name : read_data(resultfile) } )
    pprint(data)
    
# vim: set foldmethod=indent foldlevel=0 foldnestmax=1 :
