#!/usr/bin/python -W ignore
#  Cron wrapper to make sure cron started jobs time out and do not start multiple jobs
#  Sam Pepler
#
# Adapted form ingest control SJP 2016


import smtplib
import subprocess
import sys
import os
import time
import signal
import optparse
import hashlib

def check_pid(pid):
    """ Check For the existence of a unix pid. """
    try:
        os.kill(pid, 0)
    except OSError:
        return False
    else:
        return True


def crontamer(script, options):
    """Run the script monitoring for failure."""
    #  loop until process stops.  If time out is reached kill process

    # if lock option spesified then lock process
    if options.lock:
        h = hashlib.md5()
        h.update(script)
        h.update(str(os.getuid()))

        if not options.lock_file:
            lockfile = "/tmp/crontamer." + h.hexdigest()

        else:
            lockfile = options.lock_file

        # check for lock
        if os.path.exists(lockfile):
            pid = file(lockfile).readline()
            if check_pid(int(pid)):
                if options.verbose:
                    sys.stderr.write("Lock on and process found - Exiting.\n")
                sys.exit(0)
            else:
                if options.verbose:
                    sys.stderr.write("Lock file exists but no process running remove lock file.\n")
                os.unlink(lockfile)

        else:
            pid = 'N/A'

        # lock
        if options.verbose:
            sys.stderr.write("Make Lock for process %s file: %s\n" % (os.getpid(), lockfile))
        fd = file(lockfile, 'w')
        fd.write("%d" % os.getpid())
        fd.close()

    else:
        pid = 'N/A'

    # variables set before prcess starts
    start_time = time.time()
    try:
        timeout_unit = options.timeout[-1]
        timeout_number = float(options.timeout[:-1])
        timeout = timeout_number * {"h": 3600, "m": 60, "s": 1}[timeout_unit]
    except:
        sys.stderr.write("Trouble parsing timeout period. Should be number with unit. For example, 12h, 30m or 45s\n")
        sys.exit(1)
    killed = False

    # start process
    if options.verbose:
         sys.stderr.write("Starting process for '%s'\n" % script)
         sys.stderr.write("Process started %s\n" % time.asctime(time.localtime(start_time)))
    process = subprocess.Popen(script, shell=True)

    # poll until the job is done
    while 1:
        pollint = (time.time() - start_time)*0.01 + 0.001
        returncode = process.poll()
        if returncode is None and time.time() - start_time < timeout:
            # job is still going and not timed out
            time.sleep(pollint)
        elif returncode is None:
            # kill the job as it has timed out
            os.kill(process.pid, signal.SIGKILL)
            time.sleep(1)
            killed = True
            if options.verbose:
                sys.stderr.write("Killed on timeout!\n")
        else:
            # job is finished exit polling loop
            break

    # mark the end of the job
    end_time = time.time()
    if options.verbose:
        sys.stderr.write("Process ended %s\n" % time.asctime(time.localtime(end_time)))

    # unlock job
    if options.lock:
        os.unlink(lockfile)

    # send emails if failed or killed
    if (returncode != 0 or killed) and options.email != '':
        msg = "From: %s\r\n" % options.email
        msg += "To: %s\r\n" % options.email
        msg += "Subject: [crontamer] %s\r\n\r\n" % script
        msg += "Notification from crontamer\n%s" % msg
        msg += "script:        %s\n" % script
        msg += "pid:           %s\n" % pid
        msg += "returncode:    %s\n" % returncode
        msg += "start time:    %s\n" % time.asctime(time.localtime(start_time))
        msg += "end time:      %s\n" % time.asctime(time.localtime(end_time))
        msg += "host:          %s\n" % os.uname()[1]
        msg += "killed:        %s\n" % killed

        server = smtplib.SMTP('localhost')
        server.sendmail(options.email, options.email, msg)


# ------------------------------------------
# MAIN PROGRAM
#
def main():

    parser = optparse.OptionParser(usage="%prog [options] 'my_script -opt1 -opt2 arg1 arg2'")
    parser.add_option("-t", "--timeout", dest="timeout", default="12h",
                  help="set timeout for jobs in hours [default: %default]", metavar="HOURS")
    parser.add_option("-l", action="store_true", dest="lock",
                      help="Sets the process locking so that another instance of this job will not start [default]")
    parser.add_option("-L", "--lock-file", dest="lock_file", type="str", action="store", \
                         help="Explicit lock file.  If not used lock file generated will be based on command supplied.  Can only be used in tandem with -l option.")
    parser.add_option("-u", action="store_false", dest="lock",
                      help="Sets the process locking so that another instance of this job can start")

    parser.set_default("lock", True)
    parser.add_option("-e", "--email", default="",
                      help="email address to sent to on script fail or timeout", metavar="EMAIL")
    parser.add_option("-v", action="store_true", dest="verbose", default=False,
                      help="verbose output set")
    parser.description = """Wrapper script for cron jobs enabling locking, timeouts and email notification on failure.
The wrapped commands should be a single quoted string so that any shell expansion and option parsing
happens within the wrapped subprocess."""

    options, args = parser.parse_args()

    if options.lock_file and not options.lock:
        print "Please use -L option with -l option"
        sys.exit()

    # set remainder arguments to script to be run
    script = ' '.join(args)

    # make connector and run script
    crontamer(script, options)

if __name__ == "__main__":
    main()



