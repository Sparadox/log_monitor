#!/user/bin/env python
# -*- coding: utf-8 -*-

import unittest
import time
from datetime import datetime

from overload_monitor import OverloadMonitor
from request_monitor import Request


class OverloadMonitorTest(unittest.TestCase):

    def test_alert(self):
        """
        Tests that an overload of requests in a log file will make an instance
        of OverloadMonitor switch to alert status and notify his observers.
        It also test that when the number of queries per x seconds reaches a
        normal level, the alert status is cancelled and the observers are
        notified.
        """
        alert_threshold = 10
        update_interval = 1
        timeframe = 5
        self._callback_triggered = False

        overload_monitor = OverloadMonitor(alert_threshold, update_interval,
                                           timeframe)
        overload_monitor.start()

        overload_monitor.add_observer(self, 'alert')

        # We check that no overload is detected at startup
        self.assertFalse(overload_monitor.overloaded)

        # We launch a bunch of requests
        for i in range(1, alert_threshold + 1):
            overload_monitor.add_request(Request('/test/index.html',
                                                 datetime.now(),
                                                 'GET', '127.0.0.1',
                                                 200, 'HTTP/1.1', '-',
                                                 '-', 12))

        # We check that the observer has been called and that the overloaded
        # property is True
        self.assertTrue(self._callback_triggered)
        self.assertTrue(overload_monitor.overloaded)
        self._callback_triggered = False

        # We wait for the timeframe to go away and check that the callback is
        # triggered again and that the overload status is OK
        # The "+1s" is here to make sure that the list of recent requests will
        # have been updated (it takes some microseconds for the list to be
        # updated, but with this offset of 1s, unless the server is veeeery
        # slow, it shouldn't jeopardize the result of the test)
        time.sleep(timeframe + update_interval + 1)

        self.assertTrue(self._callback_triggered)
        self.assertFalse(overload_monitor.overloaded)
        self._callback_triggered = False

        # We pull in a normal amount of requests (just the limit) and check
        # that no alert is triggered
        for i in range(1, alert_threshold - 1):
            overload_monitor.add_request(Request('/test/index.html',
                                                 datetime.now(),
                                                 'GET', '127.0.0.1',
                                                 200, 'HTTP/1.1', '-',
                                                 '-', 12))

        self.assertFalse(self._callback_triggered)
        self.assertFalse(overload_monitor.overloaded)

        # And finally we check that killing the thread works
        overload_monitor.stop_monitoring()

        time.sleep(update_interval + 1)

        self.assertFalse(overload_monitor.is_alive())

    def on_alert(self):
        self._callback_triggered = True
