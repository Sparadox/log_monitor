#!/user/bin/env python
# -*- coding: utf-8 -*-

import re
from datetime import datetime

from request_monitor import Request


class ApacheLogParser:
    """
    Transforms a line of a standard Apache HTTP access log into a
    request_monitor.Request object (an object describing an HTTP Request).
    """

    LOG_REGEX = '(\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}) ([a-zA-Z0-9_\-]+) \
([a-zA-Z0-9_\-]+) \[(.+)\] "(.+)" ([0-9\-]+) ([0-9\-]+)'
    DATETIME_FORMAT = '%d/%b/%Y:%H:%M:%S'
    REQUEST_FORMAT = '([A-Z]+) (.+) (HTTP/\d\.\d)'

    def parseline(self, line):
        first_split = re.split(ApacheLogParser.LOG_REGEX, line)

        remote_addr = first_split[1]
        client_identity = first_split[2]
        remote_username = first_split[3]
        date_string = first_split[4].split()[0]
        request_string = first_split[5]
        status = int(first_split[6])
        bytes_sent = int(first_split[7]) if first_split[7] != '-' else 0

        # Date parsing
        date = datetime.strptime(date_string,
                                 ApacheLogParser.DATETIME_FORMAT)

        # HTTP message parsing
        request_split = re.split(ApacheLogParser.REQUEST_FORMAT,
                                 request_string)

        method = request_split[1]
        url = request_split[2]
        protocol = request_split[3]

        return Request(url, date, method, remote_addr, status, protocol,
                       client_identity, remote_username, bytes_sent)
