import re

from pimonitor.cu.PMCUParameter import PMCUParameter
from pimonitor.cu.PMCUStandardParameter import PMCUStandardParameter

__author__ = 'citan'

class PMCUCalculatedParameter(PMCUStandardParameter):
    def __init__(self, pid, name, desc, target):
        PMCUStandardParameter.__init__(self, pid, name, desc, PMCUParameter.CU_INVALID_BYTE_INDEX(),
                                       PMCUParameter.CU_INVALID_BIT_INDEX(), target)

        self._cu_type = PMCUParameter.CU_TYPE_CALCULATED_PARAMETER()
        self._dependencies = []

    def add_dependency(self, parameter):
        self._dependencies.append(parameter)

    def get_calculated_value(self, packets, unit=None):
        value = ""
        local_vars = locals()

        if len(self._conversions) > 0 and unit is None:
            unit = self._conversions[0][0]

        for conversion in self._conversions:
            curr_unit = conversion.get_unit()
            expr = conversion.get_expr()
            value_format = conversion.get_format()
            conversion_map = {}
            if unit == curr_unit:
                param_pairs = re.findall(r'\[([^]]*)\]', expr)
                for pair in param_pairs:
                    attributes = pair.split(":")
                    key = attributes[0]
                    unit = attributes[1]
                    expr = expr.replace("[" + key + ":" + unit + "]", key)
                    conversion_map.update({key: unit})

                param_no = 0
                for packet in packets:
                    param = self._parameters[param_no]
                    if param.get_id() in conversion_map:
                        conversion_unit = conversion_map[param.get_id()]
                    else:
                        conversion_unit = None

                    if param.get_dependencies():
                        return "DEPS :("
                    else:
                        value = param.get_value(packet, conversion_unit)
                        local_vars[param.get_id()] = float(value)
                    param_no += 1

                try:
                    value = eval(expr)
                except (SyntaxError, ZeroDivisionError):
                    value = 0.0

                format_tokens = value_format.split(".")
                output_format = "%.0f"
                if len(format_tokens) > 1:
                    output_format = "%." + str(len(format_tokens[1])) + "f"

                value = output_format % value

        return value

    def is_supported(self, parameters):
        param_ids = [p.get_id() for p in parameters]

        for dependency in self._dependencies:
            if dependency not in param_ids:
                return False

        return True

    def to_string(self):
        return "id=" + self._id + "\nname=" + self._name + "\ndesc=" + self._desc +  "\ntarget=" + str(
            self._target) + "\nconversion:\n\t" + '%s' % ',\n\t'.join(x.to_string() for x in self._conversions) + \
            '\ndependency: ' + '%s' % ', '.join(x for x in self._dependencies)