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
            children.append(int(pid_str))

        return children

    except:
        return None


no_children = True

#check and get initial process
children = childproc(int(sys.argv[1]))

if children:
    no_children = False

while not no_children:

    for child in children:

        #first pass at first level of child processes
        anymore_children = childproc(child)

        if anymore_children:

            for another_child in anymore_children:

                #extend the list we are iterating over with the latest pids
                children.extend([another_child])

        else:
            no_children = True

for i in children:
    print "%s has child process: %s" %(int(sys.argv[1]),i)


