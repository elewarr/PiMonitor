from pimonitor.cu.PMCUAddress import PMCUAddress
from pimonitor.cu.PMCUParameter import PMCUParameter
from pimonitor.cu.PMCUStandardParameter import PMCUStandardParameter

__author__ = 'citan'


class PMCUSwitchParameter(PMCUStandardParameter):
    def __init__(self, pid, name, desc, address, byte_index, bit_index, target):
        PMCUStandardParameter.__init__(self, pid, name, desc, byte_index,
                                       bit_index, target)

        self._cu_type = PMCUParameter.CU_TYPE_SWITCH_PARAMETER()
        self.set_address(PMCUAddress(address, 1))

    def get_value(self, packet):
        index = 1
        value_byte = packet.get_data()[index:index + self._address.get_length()][0]

        bit_mask = 1 << self._bit_index
        if value_byte & bit_mask == bit_mask:
            return "1"
        else:
            return "0"

    def to_string(self):
        return "id=" + self._id + "\nname=" + self._name + "\ndesc=" + self._desc + "\nbyte=" + str(
            self._byte_index) + "\n" + self._address.to_string() + "\nbit=" + str(
            self._bit_index) + "\ntarget=" + str(
            self._target)
