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

ppid = int(sys.argv[1])
d={}

try:
	d[ppid] = childproc(ppid)

except:
	print 'here'
	d[ppid] = None
import pdb; pdb.set_trace()
for i in d.keys():
	if d[i] is not None:
		for j in d[i]:
			print "%s has child process: %s" %(i, j)
	
	else:
		print 'oops'

