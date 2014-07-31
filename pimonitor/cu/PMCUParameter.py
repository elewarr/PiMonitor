__author__ = 'citan'

# <parameter id="P1" name="Engine Load (Relative)" desc="P1" ecubyteindex="8" ecubit="7" target="1">
# <address>0x000007</address>
# <conversions>
#        <conversion units="%" expr="x*100/255" format="0.00" />
#    </conversions>
#</parameter>

class PMCUParameter(object):

    def __init__(self, cu_type):
        self._cu_type = cu_type

    def get_cu_type(self):
        return self._cu_type

    @classmethod
    def CU_TYPE_STD_PARAMETER(cls):
        return 0

    @classmethod
    def CU_TYPE_FIXED_ADDRESS_PARAMETER(cls):
        return 1

    @classmethod
    def CU_TYPE_SWITCH_PARAMETER(cls):
        return 2

    @classmethod
    def CU_TYPE_CALCULATED_PARAMETER(cls):
        return 3

    @classmethod
    def CU_INVALID_BYTE_INDEX(cls):
        return -1

    @classmethod
    def CU_INVALID_BIT_INDEX(cls):
        return -1
