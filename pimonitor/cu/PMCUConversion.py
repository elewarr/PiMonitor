__author__ = 'citan'

class PMCUConversion(object):

    def __init__(self, unit, expr, format):
        self._unit = unit
        self._expr = expr
        self._format = format

    def get_unit(self):
        return self._unit

    def get_expr(self):
        return self._expr

    def get_format(self):
        return self._format

    def to_string(self):
        return "unit=" + self._unit + ", expr=" + self._expr + ", format=" + self._format