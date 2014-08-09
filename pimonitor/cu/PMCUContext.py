from pimonitor.cu.PMCUParameter import PMCUParameter

__author__ = 'citan'


class PMCUContext(object):
    @classmethod
    def RESPONSE_MARK_OFFSET(cls):
        return 4

    @classmethod
    def RESPONSE_ROM_ID_OFFSET(cls):
        return 8

    @classmethod
    def INITIAL_RESPONSE_MIN_LEN(cls):
        return 13

    def __init__(self, packet, targets):
        self._packet = packet
        self._targets = targets

    def get_rom_id(self):
        data = self._packet.to_bytes()

        if data[PMCUContext.RESPONSE_MARK_OFFSET()] != 0xFF:
            raise Exception('packet', "not valid init response: " + hex(data[0]) + " instead 0xFF")
        if len(data) < PMCUContext.INITIAL_RESPONSE_MIN_LEN():
            raise Exception('packet', "not valid init response")

        rom_id = ((data[PMCUContext.RESPONSE_ROM_ID_OFFSET()] << 32) |
                  (data[PMCUContext.RESPONSE_ROM_ID_OFFSET() + 1] << 24) |
                  (data[PMCUContext.RESPONSE_ROM_ID_OFFSET() + 2] << 16) |
                  (data[PMCUContext.RESPONSE_ROM_ID_OFFSET() + 3] << 8) |
                  (data[PMCUContext.RESPONSE_ROM_ID_OFFSET() + 4])) & 0xFFFFFFFFFF

        rom_id = hex(rom_id).lstrip("0x").upper()
        if rom_id[-1] == "L":
            rom_id = rom_id[:-1]
        return rom_id

    def match_parameters(self, parameters):
        matched = []
        rom_id = self.get_rom_id()
        print 'rom id=' + rom_id

        for parameter in parameters:
            if parameter.get_target() not in self._targets:
                continue

            cu_type = parameter.get_cu_type()

            if cu_type == PMCUParameter.CU_TYPE_STD_PARAMETER():
                if parameter.is_supported(self._packet.to_bytes()):
                    matched.append(parameter)
            elif cu_type == PMCUParameter.CU_TYPE_FIXED_ADDRESS_PARAMETER():
                if parameter.is_supported(rom_id):
                    print 'match=' + parameter.get_id()
                    parameter.switch_to_id(rom_id)
                    matched.append(parameter)

        return matched

    def match_switch_parameters(self, parameters):
        matched = []

        for parameter in parameters:
            if parameter.get_target() not in self._targets:
                continue

            cu_type = parameter.get_cu_type()

            if cu_type == PMCUParameter.CU_TYPE_SWITCH_PARAMETER():
                if parameter.is_supported(self._packet.to_bytes()):
                    matched.append(parameter)

        return matched

    def match_calculated_parameters(self, parameters, supported_parameters):
        matched = []

        for parameter in parameters:
            if parameter.get_target() not in self._targets:
                continue

            cu_type = parameter.get_cu_type()
            if cu_type == PMCUParameter.CU_TYPE_CALCULATED_PARAMETER():
                if parameter.is_supported(supported_parameters):
                    parameter.fill_dependencies(supported_parameters)
                    matched.append(parameter)

        return matched
