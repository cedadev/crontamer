# Crontamer
A wrapper script for cron to stop multiple process instances starting. Also times out after 12 hours (default)
and emails on error.

Installation.
This is simple python script, put it somewhere in your path.

Usage
Usage: crontamer.py [options] 'my_script -opt1 -opt2 arg1 arg2'

Wrapper script for cron jobs enabling locking, timeouts and email of failures.
The wrapped commands should be a single quoted string so that any shell
expansion and option parsing happens within the wrapped subprocess.

Options:
  -h, --help            show this help message and exit
  -t HOURS, --timeout=HOURS
                        set timeout for jobs in hours [default: 12.0]
  -l                    Sets the process locking so that another instance of
                        this job will not start [default]
  -u                    Sets the process locking so that another instance of
                        this job can start
  -e EMAIL, --email=EMAIL
                        email address to sent to on script fail or timeout
  -v                    verbose output set

Examples


$ crontamer

$ crontamer.py  -v  -t 0.001 'echo START...;sleep 20 ;echo ...END'
Make Lock for process 16875 file: /tmp/crontamer.bf3743cba1a799ee03400690ff8b2a38
Starting process for 'echo START...;sleep 20 ;echo ...END'
START...
Killed on timeout!
Process ended Mon Aug  1 11:53:39 2016





