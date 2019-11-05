import subprocess, signal

def childproc(parent_pid, sig=signal.SIGTERM):
    '''
    Method to return all child processes for the given ppid as a list.  Returns None if nothing found
    # from https://stackoverflow.com/questions/3332043/obtaining-pid-of-child-process

    '''
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

def find_all_child_processes(ppid):
    '''
    Method to return a list of all child processes related to a given PID.
    Will return list of all processes in ascending order.  i.e. pid's at bottom of list are the last generated children
    :param ppid: process id
    :return: list of child processes.  None if none available.
    '''
    no_children = True

    #check and get initial process
    children = childproc(int(ppid))

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
    '''
    if children:
        for i in children:
            print "%s has child process: %s" % (int(sys.argv[1]), i)

    else:
        print "No children"
    '''

    return children



