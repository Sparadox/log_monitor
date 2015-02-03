#!/user/bin/env python
# -*- coding: utf-8 -*-

import datetime
import time
from threading import Thread, RLock

import observer
from request_monitor import Request


class OverloadMonitor(observer.Observable, Thread):
    """
    Keeps a list of all the requests who occured in the past two minutes
    (just the datetimes of these actually) and calls its observers in case
    an overload threshold (in requests / 2 minutes) is reached.

    The list is updated in a background thread.
    """

    def __init__(self, alert_threshold=50, update_interval=2, timeframe=120):
        observer.Observable.__init__(self)
        Thread.__init__(self)
        self._alert_threshold = alert_threshold
        self._update_interval = update_interval
        self._timeframe = timeframe

        self._requests = list()

        self._keeponrunning = True

        self._overloaded = False

        self._lock = RLock()

    def add_request(self, request):
        """
        Inserts a date in the right position in our _last_requests lists.
        No sorting is ever made so every insertion should be made through
        this method. Only it guarantees that the order in the list will be
        maintained. It also checks if the overload alert has to be triggered.
        """
        assert isinstance(request, Request)

        date = request.date

        if (datetime.datetime.now() - date) < datetime.\
                timedelta(seconds=self._timeframe):
            self._add_new_hit(date)

    def _add_new_hit(self, date):
        with self._lock:
            # Let's insert the request (it is porbably the one to insert at
            # the last position
            self._requests.append(date)

            # This is a kind of very fast bubble sort on update
            i = len(self._requests) - 1
            while i > 0:
                prev_date = self._requests[i - 1]
                if prev_date > date:
                    # Classic swap
                    self._requests[i - 1] = date
                    self._requests[i] = prev_date
                    i -= 1
                else:
                    break

        self._check_overload_start()

    def _delete_old(self):
        """
        Private function updating the last request list by removing the
        entries older than 2 minutes. (It implies that the server time and
        the system time are the same)
        """
        delete_to = 0
        for i, d in enumerate(self._requests):
            if (datetime.datetime.now() - d) > \
                    datetime.timedelta(seconds=self._timeframe):
                with self._lock:
                    delete_to = i + 1
            else:
                break
        with self._lock:
            # Working at a lower level could enable us to optimize the
            # complexity of this operation using a custom linked list-like data
            # structure.
            self._requests = self._requests[delete_to::]

        if delete_to > 0:
            self._check_overload_end()

    def _check_overload_start(self):
        if len(self._requests) >= self._alert_threshold:
            self._overloaded = True
            self.update()

    def _check_overload_end(self):
        if len(self._requests) < self._alert_threshold and self._overloaded:
            self._overloaded = False
            self.update()

    def stop_monitoring(self):
        """
        Stops the execution of the threading watching the stats as soon as
        possible (the maximum time is self._stats_refresh_interval)
        """
        self._keeponrunning = False

    def run(self):
        while self._keeponrunning:
            time.sleep(self._update_interval)
            self._delete_old()

    def _is_overloaded(self):
        return self._overloaded

    overloaded = property(_is_overloaded, None)
