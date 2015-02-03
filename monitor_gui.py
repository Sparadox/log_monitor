#!/user/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime


class MonitorGui:
    """
    A very basic console based interface for our traffic monitor
    """

    def __init__(self, main_monitor):

        self._main_monitor = main_monitor

        self._alert = None
        self._last_alert = None
        self._shutdown_pending = False

        self.reprint()

    def on_stat_change(self):
        self.reprint()

    def on_alert(self):
        if self._main_monitor.overload_monitor.overloaded:
            self._alert = True
        else:
            self._alert = False

        self._last_alert = datetime.now()

        self.reprint()

    def on_section_change(self):
        self.reprint()

    def stop(self):
        self._shutdown_pending = True

    def print_sections(self, ranking):
        if len(ranking) > 0:
            print("    section    |   hits\n------------------------")
            for s, h in ranking:
                sp = ""
                while len(sp) + len(s) < 13:
                    sp += " "
                print('{0} {2} |    {1}'.format(s, h, sp))
        else:
            print('   No data available yet')

    def reprint(self):
        MonitorGui.clear()

        if self._alert is not None:
            if self._alert:
                print("ALERT ({0}) : traffic threshold reached. Server is \
overloaded \n".format(self._last_alert))
            else:
                print("ALERT FINISHED ({0}) : traffic load back to normal \n"
                      .format(self._last_alert))

        print("--- MOST VISITED SECTIONS ---\n")
        ranking = self._main_monitor.section_monitor.get_last_top_n(10)
        if len(ranking) == 0:
            ranking = self._main_monitor.section_monitor.get_current_top_n(10)
        self.print_sections(ranking)

        print("\n\n--- STATISTICS --- \nTotal number of request : {0} \
\nAverage number of \
requests per minute : {1:.1f} \nsince {2} \n".
              format(self._main_monitor.stats_monitor.request_count,
                     self._main_monitor.stats_monitor.av_req_per_minute,
                     self._main_monitor.stats_monitor.starting_datetime))

        print("Successful : {0} \t Failed {1} \t Success Ratio : {2:.0f} \n".
              format(self._main_monitor.stats_monitor.successful_req_count,
                     self._main_monitor.stats_monitor.failed_req_count,
                     self._main_monitor.stats_monitor.success_ratio * 100))

        print("Type CTRL-C to close (under Linux at least...)")

        if self._shutdown_pending:
            print("\n\n Log Monitor will shut down in a few seconds, \
please wait...")

    def clear():
        print(chr(27) + "[2J")
