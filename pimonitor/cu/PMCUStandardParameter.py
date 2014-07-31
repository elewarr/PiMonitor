from pimonitor.cu.PMCUContext import PMCUContext
from pimonitor.cu.PMCUParameter import PMCUParameter

__author__ = 'citan'


class PMCUStandardParameter(PMCUParameter):
    def __init__(self, pid, name, desc, byte_index, bit_index, target):
        PMCUParameter.__init__(self, PMCUParameter.CU_TYPE_STD_PARAMETER())

        self._id = pid
        self._name = name
        self._desc = desc
        self._byte_index = byte_index
        self._bit_index = bit_index
        self._target = target
        self._conversions = []
        self._address = None

    def get_id(self):
        return self._id

    def set_address(self, address):
        self._address = address

    def get_address(self):
        return self._address

    def get_target(self):
        return self._target

    def get_name(self):
        return self._name

    def add_conversion(self, conversion):
        self._conversions.append(conversion)

    # noinspection PyUnusedLocal
    def get_value(self, packet, unit=None):
        value = ""

        if len(self._conversions) > 0 and unit is None:
            unit = self._conversions[0].get_unit()

        for conversion in self._conversions:
            curr_unit = conversion.get_unit()
            expr = conversion.get_expr()
            value_format = conversion.get_format()

            if unit == curr_unit:
                # ignore 0xe8
                index = 1
                x = 0
                value_bytes = packet.get_data()[index:index + self.get_address().get_length()]

                address_length = self.get_address().get_length()
                if address_length == 1:
                    x = value_bytes[0]
                elif address_length == 2:
                    x = (value_bytes[0] << 8) | value_bytes[1]
                elif address_length == 3:
                    x = (value_bytes[0] << 16) | (value_bytes[1] << 8) | value_bytes[2]
                elif address_length == 4:
                    x = (value_bytes[0] << 24) | (value_bytes[1] << 16) | (value_bytes[2] << 8) | value_bytes[3]

                try:
                    value = eval(expr)
                except (SyntaxError, ZeroDivisionError):
                    return "exception"

                format_tokens = value_format.split(".")
                output_format = "%.0f"
                if len(format_tokens) > 1:
                    output_format = "%." + str(len(format_tokens[1])) + "f"

                value = output_format % value

        return value

    def get_default_unit(self):
        if len(self._conversions) > 0:
            return self._conversions[0].get_unit()
        return ""

    def is_supported(self, data):
        offset = PMCUContext.RESPONSE_MARK_OFFSET() + 1 + self._byte_index
        # <, not <= because last one is checksum
        if offset < len(data):
            cu_byte = data[offset]
            bit_mask = 1 << self._bit_index
            return cu_byte & bit_mask == bit_mask
        else:
            return False

    def to_string(self):
        return "id=" + self._id + "\nname=" + self._name + "\ndesc=" + self._desc + "\nbyte=" + str(
            self._byte_index) + "\n" + self._address.to_string() + "\nbit=" + str(
            self._bit_index) + "\ntarget=" + str(
            self._target) + "\nconversion:\n\t" + '%s' % ',\n\t'.join(x.to_string() for x in self._conversions)
