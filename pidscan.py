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
process_tree = []
no_children = False
child = None
#cnt = 0

while not no_children:

    if child is None:
        parent = ppid

    #first pass at first level of child processes
    try:
        for child in childproc(parent):
            process_tree.append(int(child))

        #reset parent to the last child ppid to get the next step down.
        parent = process_tree[-1]

    except:
        no_children = True

for i in process_tree:
    print "%s has child process: %s" %(ppid,i)


