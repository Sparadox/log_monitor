#!/user/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os.path
import os
import time


class LogReader:
    """

    Simple class reading a given log file actively. For each new line
    added in the file, the LogReader reads it and pass it to the add_request
    function of a given instance of a class implementing this method.
    Rigourously, it means that the "callback" class implements a
    "TriggerableOnNewHit" interface but the interface mecanism is
    implicit in Python.

    For a strange reason (maybe related to the fact that log files are
    written using a 'a' mode instead of a 'w' mode ?), it works perfectly
    on apache's logs but not if the file is edited by hand with Vim and
    then saved. But anyway, we want to deal with log files...

    """

    def __init__(self, filename, line_processor, timeout=0.4):
        self._filename = filename
        self._line_processor = line_processor
        self._timeout = timeout

    def watch_log(self):

        # Let's open the file and start reading it when a
        # new line is saved in it.
        with open(self._filename, 'r') as log_file:
            # Go to EOF
            log_file.seek(os.stat(self._filename)[6])
            while True:
                cursor_pos = log_file.tell()
                newline = log_file.readline()

                if not newline:
                    time.sleep(self._timeout)
                    log_file.seek(cursor_pos)
                else:
                    self._line_processor.add_request(newline)

#### TEST CODE ####


class TestProcessor:
    def add_request(self, newline):
        print(newline)


if __name__ == '__main__':
    # We get the file path from the --logfile console parameter
    parser = argparse.ArgumentParser()
    parser.add_argument('logfile', type=str,
                        help='Path to the log file to monitor')
    args = parser.parse_args()

    logfilename = args.logfile

    if not os.path.isfile(logfilename):
        raise IOError("File " + logfilename + " doesn't seem to exist")

    processor = TestProcessor()
    logreader = LogReader(logfilename, processor)

    logreader.watch_log()
