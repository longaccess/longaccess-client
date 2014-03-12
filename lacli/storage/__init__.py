from abc import ABCMeta, abstractmethod


class StorageConnection(object):
    __metaclass__ = ABCMeta

    def __init__(self, **kwargs):
        pass

    @abstractmethod
    def newkey(self, key):
        """ return an object representing a storage object """
