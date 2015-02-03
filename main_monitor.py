#!/user/bin/env python
# -*- coding: utf-8 -*-

import argparse
import os
import sys
import signal

from log_reader import LogReader
from log_parser import ApacheLogParser
from request_monitor import RequestMonitor
from overload_monitor import OverloadMonitor
from stats_monitor import StatsMonitor
from section_monitor import SectionMonitor
from monitor_gui import MonitorGui


class MainMonitor:
    """
    Generic class of the http monitoring program.

    The program will display the sections of the website with
    the most hits (recomputed and redisplayed every ten seconds),
    the average number of hits/minute since the program has been
    launched or the percentage of successfull requests. I used a
    very simple and probably not completely accurate model :
    I consider some HTTP status codes (1xx, 2xx and 3xx) to be
    fullfilling the request and the other codes (4xx and 5xx) to be
    errors. It is very minimalistic but is something a server
    administrator may like to have in order to fix potential broken
    links and setup a redirection or display a nice message instead
    of an ugly 404. Thus, the failing requests are also stored and
    displayed to the user.

    It also contains an alert system : whenever the traffic for the
    past two minutes exceeds a certain number (to be specified when
    MainMonitor is instantiated), a message is shown to the user on
    the top of the console and remains visible until the traffic.

    It takes the path to the log file to monitor as only parameter
    argument. For information about optionnal paramaters, launch the
    program with the -h flag.
    """

    def __init__(self, filename, LogParser=ApacheLogParser, alert_threshold=50,
                 log_check_interval=0.4, overload_timeframe=120,
                 overload_responsetime=2, section_dropinterval=10,
                 stats_update_interval=1):
        self._log_reader = LogReader(filename, self,
                                     timeout=log_check_interval)
        self._log_parser = LogParser()
        self._overload_monitor = OverloadMonitor(alert_threshold,
                                                 overload_responsetime,
                                                 overload_timeframe)
        self._stats_monitor = StatsMonitor(stats_update_interval)
        self._section_monitor = SectionMonitor(section_dropinterval)
        self._request_monitor = RequestMonitor(submonitors=
                                               [self._overload_monitor,
                                                self._stats_monitor,
                                                self._section_monitor])
        self._monitor_gui = MonitorGui(self)
        self._overload_monitor.add_observer(self._monitor_gui, 'alert')
        self._stats_monitor.add_observer(self._monitor_gui, 'stat_change')
        self._section_monitor.add_observer(self._monitor_gui, 'section_change')

    def add_request(self, newline):
        new_request = self._log_parser.parseline(newline)

        # Here the request is passed to the RequestMonitor
        self._request_monitor.add_request(new_request)

    def run(self):
        # We start the statistic monitoring (refreshed in a separate
        # thread)
        self._overload_monitor.start()
        self._stats_monitor.start()
        self._section_monitor.start()

        # And we launch the watch_log in the main thread
        self._log_reader.watch_log()

    def shutdown(self):
        # We ask all the threads to stop
        self._overload_monitor.stop_monitoring()
        self._stats_monitor.stop_monitoring()
        self._section_monitor.stop_monitoring()

        # We tell the user we are going to shut down
        self._monitor_gui.stop()

        # And we wait for them to do so
        self._overload_monitor.join()
        self._stats_monitor.join()
        self._section_monitor.join()

    def _get_stats_monitor(self):
        return self._stats_monitor

    stats_monitor = property(_get_stats_monitor, None)

    def _get_overload_monitor(self):
        return self._overload_monitor

    overload_monitor = property(_get_overload_monitor, None)

    def _get_section_monitor(self):
        return self._section_monitor

    section_monitor = property(_get_section_monitor, None)

    def _get_request_monitor(self):
        return self._stats_monitor

    request_monitor = property(_get_request_monitor, None)


if __name__ == '__main__':
    # Let's get the path to the log file as a console argument
    parser = argparse.ArgumentParser()

    parser.add_argument('logfile', type=str,
                        help='Path to the log file to monitor')
    parser.add_argument('-t', '--threshold', type=int,
                        help='The minimum number of requests per 2 minutes \
(or -t minutes if specified) displaying an overload alert.')
    parser.add_argument('-c', '--log-check-interval', type=int,
                        help='Check the log file every -c seconds')
    parser.add_argument('-i', '--overload-timeframe', type=int,
                        help='The overload timeframe (an alert is thrown if \
there are more than -t requests per -i seconds')
    parser.add_argument('-o', '--overload-response-time', type=int,
                        help='Check whether there is an overload every -o \
seconds')
    parser.add_argument('-s', '--section-drop-interval', type=int,
                        help='The most visited sections is refreshed every -s \
seconds. Put 0 here if you don\'t want the ranking to be cleared.')
    parser.add_argument('-u', '--stats-update-interval', type=int,
                        help='Recompute the time dependant statistics every \
-u seconds.')

    args = parser.parse_args()

    logfilename = args.logfile
    threshold = args.threshold if args.threshold is not None else 50
    log_check_interval = args.log_check_interval if args.log_check_interval \
        is not None else 0.4
    overload_timeframe = args.overload_timeframe if args.overload_timeframe \
        is not None else 120
    overload_response_time = args.overload_response_time if \
        args.overload_response_time is not None else 2
    section_drop_interval = args.section_drop_interval if \
        args.section_drop_interval is not None else 10
    stats_update_interval = args.stats_update_interval if \
        args.stats_update_interval is not None else 1

    # Possible improvement : we could check the validity of all the parameters
    if not os.path.isfile(logfilename):
        raise IOError("File " + logfilename + " doesn't seem to exist")

    # We have parsed all the arguments

    main_monitor = MainMonitor(logfilename, alert_threshold=threshold,
                               log_check_interval=log_check_interval,
                               overload_timeframe=overload_timeframe,
                               overload_responsetime=overload_response_time,
                               section_dropinterval=section_drop_interval,
                               stats_update_interval=stats_update_interval)

    def _on_close_request(*args):
        main_monitor.shutdown()
        sys.exit(0)

    signal.signal(signal.SIGINT, _on_close_request)

    main_monitor.run()
