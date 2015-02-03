#!/user/bin/env python
# -*- coding: utf-8 -*-


class Observable:
    """
    An abstract implementation of an Observable class. I.E. a class with a list
    of Observers that can be notfied when something is modified in the current
    instance of the class (for this, a call the the update method is needed).
    """
    def __init__(self):
        self._observers = list()

    def update(self):
        for (observer, callback) in self._observers:
            method = getattr(observer, 'on_'+callback)
            method()

    def add_observer(self, observer, callback = 'update'):
        self._observers.append((observer, callback))

    def remove_observer(self, observer):
        index = None
        for i, (obs, callback) in enumerate(self._observers):
            if observer == obs:
                index = i
                break

        if index is not None:
            self._observers.pop(index)
