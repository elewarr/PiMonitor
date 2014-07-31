from pimonitor.cu.PMCUParameter import PMCUParameter
from pimonitor.cu.PMCUStandardParameter import PMCUStandardParameter

__author__ = 'citan'

class PMCUFixedAddressParameter(PMCUStandardParameter):
    def __init__(self, pid, name, desc, target):
        PMCUStandardParameter.__init__(self, pid, name, desc, PMCUParameter.CU_INVALID_BYTE_INDEX(),
                                       PMCUParameter.CU_INVALID_BIT_INDEX(), target)

        self._cu_type = PMCUParameter.CU_TYPE_FIXED_ADDRESS_PARAMETER()
        self._cu_ids = {}

    def add_ecu_id(self, cu_id, address):
        self._cu_ids[cu_id] = address

    def get_address_for_id(self, cu_id):
        if cu_id in self._cu_ids:
            return self._cu_ids[cu_id]
        else:
            return None

    def switch_to_id(self, cu_id):
        self._address = self.get_address_for_id(cu_id)

    def set_address(self, address):
        raise Exception

    def is_supported(self, cu_id):
        return self.get_address_for_id(cu_id) is not None

    def to_string(self):
        return "id=" + self._id + "\nname=" + self._name + "\ndesc=" + self._desc +  "\ntarget=" + str(
            self._target) + "\nconversion:\n\t" + '%s' % '\n\t'.join(x.to_string() for x in self._conversions) + \
            '\necu: ' + ' '.join(['\n\tid={}, {}'.format(k,v.to_string()) for k,v in self._cu_ids.iteritems()])