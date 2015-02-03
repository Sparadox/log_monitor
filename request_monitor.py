#!/user/bin/env python
# -*- coding: utf-8 -*-

from urllib.parse import urlparse
import datetime


class RequestMonitor:
    """
    Constructs (from log) and dispatches new HTTP Requests to submonitors
    """

    def __init__(self, submonitors=list()):
        """
        alert threshold : the number of requests per 2 minutes that
        should trigger an alert
        stats_refresh_interval : the interval between two updates of the
        list containing all queries for the last two minutes
        submonitors : a list of instance of monitors (classes implementing
        the add_request() method)
        """
        self._submonitors = submonitors
        self._requests = list()

    def add_request(self, request):
        assert isinstance(request, Request)

        self._requests.append(request)

        # We pass the new request to submonitors
        for monitor in self._submonitors:
            monitor.add_request(request)


class Request:
    """
    A very standard "Entity" class describing an HTTP Request
    """

    def __init__(self, url, date, method, remote_addr, status,
                 protocol, client_identity, remote_username, bytes_sent):
        """
        Constructs a requests object and automatically computes the
        section of the path and whether the request is successful or
        not. Once instantiated, this object shouldn't be modified.
        It should instead be destroyed and a new request should be
        created.
        """
        self.url = url

        assert isinstance(date, datetime.datetime)
        self.date = date

        self.method = method
        self.remote_addr = remote_addr

        assert isinstance(status, int)
        self.status = status

        self.protocol = protocol
        self.client_identity = client_identity
        self.remote_username = remote_username
        self.bytes_sent = bytes_sent

        self._successful = None
        self._section = None

    def _is_successful(self):
        if self._successful is not None:
            return self._sucessful

        if(self.status <= 399):
            self._successful = True
        else:
            self._successful = False

        return self._successful

    is_successful = property(_is_successful, None)

    def _get_section(self):
        if self._section is not None:
            return self._section

        parsed_url = urlparse(self.url)
        splitted_path = parsed_url.path.split('/', 2)

        self._section = splitted_path[1]

        return self._section

    section = property(_get_section, None)
