#!/user/bin/env python
# -*- coding: utf-8 -*-

from datetime import datetime

import time
from threading import Thread, RLock

import observer
from request_monitor import Request


class StatsMonitor(observer.Observable, Thread):

    def __init__(self, update_interval=1):
        observer.Observable.__init__(self)
        Thread.__init__(self)

        self._update_interval = update_interval
        self._request_count = 0
        self._av_reqs_per_minute = 0
        self._successful_req_count = 0

        self._keeponrunning = True
        self._starting_datetime = datetime.now()
        self._lock = RLock()

    def add_request(self, request):
        """
        Increments the request count.
        """
        assert isinstance(request, Request)

        self._request_count += 1

        if request.is_successful:
            self._successful_req_count += 1

        self.update()

    def _update_stats(self):
        timedelta = (datetime.now() - self._starting_datetime)\
            .total_seconds()
        if timedelta != 0:
            with self._lock:
                self._av_reqs_per_minute = (self._request_count) / \
                    timedelta * 60
            self.update()

    def stop_monitoring(self):
        self._keeponrunning = False

    def run(self):
        while self._keeponrunning:
            time.sleep(self._update_interval)
            self._update_stats()

    def _get_request_count(self):
        return self._request_count

    request_count = property(_get_request_count, None)

    def _get_av_req_per_minute(self):
        return self._av_reqs_per_minute

    av_req_per_minute = property(_get_av_req_per_minute, None)

    def _get_starting_datetime(self):
        return self._starting_datetime

    starting_datetime = property(_get_starting_datetime, None)

    def _get_successful_req_count(self):
        return self._successful_req_count

    successful_req_count = property(_get_successful_req_count, None)

    def _get_failed_req_count(self):
        return self._request_count - self._successful_req_count

    failed_req_count = property(_get_failed_req_count, None)

    def _get_success_ratio(self):
        if self._request_count == 0:
            return 0

        return self._successful_req_count / self._request_count

    success_ratio = property(_get_success_ratio, None)
