#!/user/bin/env python
# -*- coding: utf-8 -*-

import sys
import time
import signal
import random
import argparse
import http.client

"""
A simple script sending HTTP requests to various locations (paths) to the
localhost in order to fill up the access_log. The different URLs to call are
defined in the code. Feel free to modify the array to add sections matching
what you have on your local host.
"""

PATH_LIST = ['/blog/article/12',
             '/user/show/12',
             '/comments/create',
             '/comments/showfor/article/12',
             '/contents/evenements.php'
             ]


if __name__ == '__main__':
    parser = argparse.ArgumentParser()

    parser.add_argument('-H', '--host', type=str,
                        help='The host to send the requests to.')
    parser.add_argument('-i', '--interval', type=int,
                        help='Number of requests to send per second')

    args = parser.parse_args()

    host = args.host if args.host is not None else '127.0.0.1'
    interval = args.interval if args.interval is not None else 5

    keeponrunning = True

    def on_close_request(*args):
        global keeponrunning
        keeponrunning = False
        sys.exit(0)

    signal.signal(signal.SIGINT, on_close_request)

    while keeponrunning:
        conn = http.client.HTTPConnection(host)
        i = int(random.random() * len(PATH_LIST))
        conn.request('GET', PATH_LIST[i])
        conn.getresponse()
        conn.close()
        time.sleep(interval)
