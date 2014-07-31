__author__ = 'citan'

class PMCUAddress(object):

    def __init__(self, address, length):
        self._address = address
        self._length = length

    def get_address(self):
        return self._address

    def get_length(self):
        return self._length

    def to_string(self):
        return "address=" + hex(self._address) + ", length=" + str(self._length)