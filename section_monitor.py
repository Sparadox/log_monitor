#!/user/bin/env python
# -*- coding: utf-8 -*-

import observer
import time
from threading import Thread, RLock

from request_monitor import Request


class SectionMonitor(observer.Observable, Thread):

    def __init__(self, update_interval=10):
        observer.Observable.__init__(self)
        Thread.__init__(self)

        self._update_interval = update_interval

        # List containing a tuple. The first element represents a section and
        # the second one represents the number of hits for this section
        # Since we have to perform a sort on the section I decided not to use
        # a dict, which is not supposed to be a sortable collection (even
        # though it is possible to sort a dict :
        # http://stackoverflow.com/questions/613183/sort-a-python-dictionary-\
        # by-value
        # The dict is sorted on insert/update, therefore, getting the 10 most
        # visited sections for instance doesn't cost anything and at worst, an
        # insertion/update has a cost of n but practically speaking, if we
        # assume that the order tends to stabilize, the cost is just a couple
        # of operations.
        self._section_hits = list()
        self._last_ranking = list()

        self._keeponrunning = True

        self._lock = RLock()

    def add_request(self, request):
        assert isinstance(request, Request)

        # We update the stats about the section hits
        self._new_section_hit(request.section)

    def _new_section_hit(self, section):
        index = None
        hits = 0

        with self._lock:
            for i, (s, v) in enumerate(self._section_hits):
                if s == section:
                    index = i
                    hits = v + 1
                    self._section_hits[i] = (section, hits)
                    break

            if index is not None:
                # This is a kind of very fast bubble sort on update
                i = index
                while i > 0:
                    (s, v) = self._section_hits[i - 1]
                    if v < hits:
                        # Classic swap
                        self._section_hits[i - 1] = (section, hits)
                        self._section_hits[i] = (s, v)
                    i -= 1
            else:
                self._section_hits.append((section, 1))

                self.update()

    def _drop_list(self):
        with self._lock:
            self._last_ranking = self._section_hits
            self._section_hits = list()

        self.update()

    def stop_monitoring(self):
        self._keeponrunning = False

    def run(self):
        if self._update_interval > 0:
            while self._keeponrunning:
                time.sleep(self._update_interval)
                self._drop_list()

    def get_last_top_n(self, n):
        return self._last_ranking[0:min(n, len(self._last_ranking))]

    def _get_ranking(self):
        return self._last_ranking

    ranking = property(_get_ranking, None)

    def get_current_top_n(self, n):
        return self._section_hits[0:min(n, len(self._section_hits))]

    def _get_section_hits(self):
        return self._section_hits

    session_hits = property(_get_section_hits, None)
