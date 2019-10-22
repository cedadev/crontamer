import subprocess, os, signal
import sys

#from https://stackoverflow.com/questions/3332043/obtaining-pid-of-child-process

def childproc(parent_pid, sig=signal.SIGTERM):

    children = []

    ps_command = subprocess.Popen("ps -o pid --ppid %d --noheaders" % parent_pid, shell=True, stdout=subprocess.PIPE)
    ps_output = ps_command.stdout.read()
    retcode = ps_command.wait()
    assert retcode == 0, "ps command returned %d" % retcode

    for pid_str in ps_output.split("\n")[:-1]:
        children.append(pid_str)

    return children



ppid = int(sys.argv[1])
process_map = {}
no_children = False
child = None
cnt = 0

while not no_children:

    #initialise the top level
    '''
    if cnt == 0:
        parent = ppid
        
    elif child != None:
        parent = child # this is going to get confusing..... 
        
    '''

    if child is None:
        parent = ppid

    #first pass at first level of child processes
    try:
        child = childproc(parent)

        process_map[cnt] = child

        #reset parent to the child ppid to get the next step down,
        parent = child

    except:
        no_children = True

    print cnt
    cnt+=1

for i in process_map.keys():
    if process_map[i]:
        for j in process_map[i]:
            print "%s has child process: %s" %(i, j)


