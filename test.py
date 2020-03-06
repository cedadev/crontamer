
import unittest
import os
import subprocess
import glob
import time

TESTFILE = "/tmp/x.tmp"

class DCTestCase(unittest.TestCase):

    def tearDown(self):
        if os.path.exists(TESTFILE):
            os.remove(TESTFILE)

    def test_process_ok(self):
        """run """
        os.system("crontamer 'ls' > %s" % TESTFILE)
        assert os.path.exists(TESTFILE)

    def test_lock(self):
        """Check lock files are made"""
        p = subprocess.Popen(["crontamer", "sleep", "2"])
        time.sleep(0.5)
        lockfiles = glob.glob("/tmp/crontamer.*")
        assert len(lockfiles) == 1
        lockfile = lockfiles[0]
        while True:
            time.sleep(0.5)
            if p.poll() is not None:
                break
        assert not os.path.exists(lockfile)

    def test_lock_named(self):
        """Check named lock files are made"""
        lockfile = "/tmp/testlock.tmp"
        p = subprocess.Popen(["crontamer", "-L", lockfile,  "sleep", "2"])
        time.sleep(0.5)
        assert os.path.exists(lockfile)
        while True:
            time.sleep(0.5)
            if p.poll() is not None:
                break
        assert not os.path.exists(lockfile)

    def test_locking(self):
        """check we only run one job at a time"""
        lockfile = "/tmp/testlock.tmp"
        p1 = subprocess.Popen(["crontamer", "-L", lockfile,  "sleep", "3"])
        time.sleep(0.5)
        assert p1.poll() is None
        p2 = subprocess.Popen(["crontamer", "-L", lockfile,  "sleep", "3"])
        time.sleep(0.5)
        assert p2.poll() is not None
        while True:
            time.sleep(0.5)
            if p1.poll() is not None:
                break

    def test_unlocking(self):
        """check we can start more than one job if unlocked option used."""
        lockfile = "/tmp/testlock.tmp"
        p1 = subprocess.Popen(["crontamer", "-u", "-L", lockfile,  "sleep", "3"])
        time.sleep(0.5)
        assert p1.poll() is None
        p2 = subprocess.Popen(["crontamer", "-u", "-L", lockfile,  "sleep", "3"])
        time.sleep(0.5)
        assert p2.poll() is None
        while True:
            time.sleep(0.5)
            if p1.poll() is not None and p2.poll() is not None:
                break

    def test_timeout(self):
        """check timeout function works"""
        lockfile = "/tmp/testlock.tmp"
        p = subprocess.Popen(["crontamer", "-L", lockfile, "-t3s", "sleep", "20"])
        time.sleep(0.5)
        assert p.poll() is None
        while True:
            time.sleep(0.5)
            status = p.poll()
            if status is not None:
                assert status != 0
                break

    def test_timeout_subprocess(self):
        """check timeout function works"""
        lockfile = "/tmp/testlock.tmp"
        p = subprocess.Popen(["crontamer", "-L", lockfile, "-t3s", "sleep", "20"])
        time.sleep(0.5)
        assert p.poll() is None
        while True:
            time.sleep(0.5)
            status = p.poll()
            if status is not None:
                assert status != 0
                break


    def test_email(self):
        """email sent after fail"""






