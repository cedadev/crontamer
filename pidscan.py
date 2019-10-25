import subprocess, os, signal
import sys

#from https://stackoverflow.com/questions/3332043/obtaining-pid-of-child-process

def childproc(parent_pid, sig=signal.SIGTERM):

    children = []

    try:
        ps_command = subprocess.Popen("ps -o pid --ppid %d --noheaders" % parent_pid, shell=True, stdout=subprocess.PIPE)
        ps_output = ps_command.stdout.read()
        retcode = ps_command.wait()
        assert retcode == 0, "ps command returned %d" % retcode

        for pid_str in ps_output.split("\n")[:-1]:
            children.append(pid_str)

        return children

    except:
        return None


ppid = int(sys.argv[1])
process_tree = []
no_children = False
child = None
#cnt = 0

#check and get initial process
try:
    children = childproc(ppid)
except:
    print "Problem finding process %s" %ppid
    sys.exit()

if len(children) != 0 or children is None:
    no_children = False

else:
    no_children = True

while not no_children:

    for child in children:

        #first pass at first level of child processes

        more_children = childproc(child)

        if more_children:

            for child in children:
                #process_tree.append(int(child))

                #extend the list we are iterating over with the latest pids
                children.extend(child)

            #reset parent to the last child ppid to get the next step down.
            #parent = process_tree[-1]

            #process_tree += children

        else:
            no_children = True

for i in process_tree:
    print "%s has child process: %s" %(ppid,i)


