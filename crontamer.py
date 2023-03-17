#!/usr/bin/python -W ignore
#  Cron wrapper to make sure cron started jobs time out and do not start multiple jobs
#  Sam Pepler
#
# Adapted form ingest control SJP 2016


import hashlib
import optparse
import os
import smtplib
import subprocess
import sys
import time
import psutil


#todo: Write some unittests for this module (SJD)

def write_verbose(options, msg):
    if options.verbose:
        sys.stderr.write("%s\n" % msg)


def parse_time_period(s):
    try:
        unit = s[-1]
        number = float(s[:-1])
        period = number * {"h": 3600, "m": 60, "s": 1}[unit]
    except (ValueError, IndexError):
        sys.stderr.write("Trouble parsing time period. Should be number with unit. For example, 12h, 30m or 45s\n")
        sys.exit(1)
    return period


def kill_children(p, int_wait=10, kill_wait=5):
    child_processes = p.children()
    for c in child_processes:
        kill_children(c)
        c.terminate()
    gone, alive = psutil.wait_procs(child_processes, timeout=int_wait)
    for c in alive:
        c.kill()
    gone, alive = psutil.wait_procs(child_processes, timeout=kill_wait)
    for a in alive:
        sys.stderr.write("Problem killing %s!\n" % a)


def crontamer(script, options):
    """Run the script monitoring for failure."""
    #  loop until process stops.  If time out is reached kill process

    # if lock option spesified then lock process
    if options.lock:
        if not options.lock_file:
            h = hashlib.md5()
            h.update(script.encode())
            h.update(str(os.getuid()).encode())
            lockfile = "/tmp/crontamer." + h.hexdigest()
        else:
            lockfile = options.lock_file

        # check for lock
        if os.path.exists(lockfile):
            with open(lockfile, 'r') as fd:
                pid = fd.readline()

                if pid != '':
                    if psutil.pid_exists(int(pid)):
                        write_verbose(options, "Lock (%s) on and process (%s) found - Exiting." % (lockfile, pid))
                        sys.exit(0)
                    else:
                        write_verbose(options, "Lock file exists (%s) but no process running remove lock file." % lockfile)
                        os.unlink(lockfile)

        # lock
        write_verbose(options, "Make Lock for process %s file: %s\n" % (os.getpid(), lockfile))
        with open(lockfile, 'w') as fd:
            fd.write("%d" % os.getpid())

    # variables set before prcess starts
    start_time = time.time()

    timeout = parse_time_period(options.timeout)
    ko_timeout = parse_time_period(options.kill_timeout)

    killed = False

    # start process
    write_verbose(options, "Starting process for '%s'" % script)
    write_verbose(options, "Process started %s" % time.asctime(time.localtime(start_time)))
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
            p = psutil.Process(process.pid)
            kill_children(p, int_wait=ko_timeout, kill_wait=ko_timeout)
            p.terminate()
            try:
                p.wait(timeout=ko_timeout)
            except psutil.TimeoutExpired:
                p.kill()
            killed = True
            write_verbose(options, "Primary process killed on timeout!")

        else:
            # job is finished exit polling loop
            break

    # mark the end of the job
    end_time = time.time()
    write_verbose(options, "Process ended %s\n" % time.asctime(time.localtime(end_time)))

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
        msg += "pid:           %s\n" % process.pid
        msg += "returncode:    %s\n" % returncode
        msg += "start time:    %s\n" % time.asctime(time.localtime(start_time))
        msg += "end time:      %s\n" % time.asctime(time.localtime(end_time))
        msg += "host:          %s\n" % os.uname()[1]
        msg += "killed:        %s\n" % killed

        server = smtplib.SMTP('localhost')
        server.sendmail(options.email, options.email, msg)

    if killed:
        sys.exit(1)
    else:
        sys.exit(returncode)


def main():
    parser = optparse.OptionParser(usage="%prog [options] 'my_script -opt1 -opt2 arg1 arg2'")
    parser.add_option("-t", "--timeout", dest="timeout", default="12h",
                      help="set timeout for jobs in hours [default: %default]", metavar="PERIOD")
    parser.add_option("-l", action="store_true", dest="lock",
                      help="Sets the process locking so that another instance of this job will not start [default]")
    parser.add_option("-L", "--lock-file", dest="lock_file", type="str", action="store",
                      help="Explicit lock file name.  If not used lock file generated will be based on command supplied.")
    parser.add_option("-K", "--kill-timeout", dest="kill_timeout", type="str", action="store",
                      help="When timed out will kill all child processes, but wait this period to allow them to "
                           "finish after sending an interrupt. [default: %default]",
                      default="5s")
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

    # set remainder arguments to script to be run
    script = ' '.join(args)

    # make connector and run script
    crontamer(script, options)


if __name__ == "__main__":
    main()



