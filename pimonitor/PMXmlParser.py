"""
Created on 29-03-2013

@author: citan
"""

import xml.sax
import os.path

from pimonitor.PM import PM
from pimonitor.cu.PMCUAddress import PMCUAddress
from pimonitor.cu.PMCUCalculatedParameter import PMCUCalculatedParameter
from pimonitor.cu.PMCUConversion import PMCUConversion
from pimonitor.cu.PMCUFixedAddressParameter import PMCUFixedAddressParameter
from pimonitor.cu.PMCUParameter import PMCUParameter
from pimonitor.cu.PMCUStandardParameter import PMCUStandardParameter
from pimonitor.cu.PMCUSwitchParameter import PMCUSwitchParameter

# <parameter id="P1" name="Engine Load (Relative)" desc="P1" ecubyteindex="8" ecubit="7" target="1">
# <address>0x000007</address>
# <conversions>
# <conversion units="%" expr="x*100/255" format="0.00" />
#    </conversions>
#</parameter>

#<ecuparam id="E20" name="Manifold Absolute Pressure (Direct)*" desc="E20-Manifold Absolute Pressure with " target="1">
#    <ecu id="1B04400405">
#        <address length="2">0x2186A</address>
#    </ecu>
# ... ecu and conversions

#<parameter id="P200" name="Engine Load (Calculated)" desc="P200-Engine load as calculated from MAF and RPM." target="1">
#   <depends>
#       <ref parameter="P8" />
#       <ref parameter="P12" />
#   </depends>
#   <conversions>
#       <conversion units="g/rev" expr="(P12*60)/P8" format="0.00" />
#   </conversions>
#</parameter>

# <switch id="S71" name="Clear Memory Terminal" desc="(E) S71" byte="0x000061" bit="0" ecubyteindex="19" target="1" />


class PMXmlParser(xml.sax.ContentHandler):
    def __init__(self):
        xml.sax.ContentHandler.__init__(self)
        self._message = ''
        self._log_id = 0

        self._element_no = 0

        self._contexts = None

        self._parameter = None
        self._parameters = set()

        self._characters = ''
        self._ecu_ids = None
        self._address_length = 0

    def parse(self, file_name):
        self._message = 'Parsing XML data'
        self._log_id = PM.log(self._message)

        file_path = os.path.join("data", file_name)
        source = open(file_path)
        xml.sax.parse(source, self)
        self.log_progress()
        PM.log(self._message + " [DONE]")

        return self._parameters

    def startElement(self, name, attrs):
        pid = None
        desc = None
        target = 0
        units = None
        expr = None
        value_format = None
        address = None

        byte_index = PMCUParameter.CU_INVALID_BYTE_INDEX()
        bit_index = PMCUParameter.CU_INVALID_BIT_INDEX()

        if name == "parameter":

            for (k, v) in attrs.items():
                if k == "id":
                    pid = v
                if k == "name":
                    name = v
                if k == "desc":
                    desc = v
                if k == "ecubyteindex":
                    byte_index = int(v)
                if k == "ecubit":
                    bit_index = int(v)
                if k == "target":
                    target = int(v)

            if byte_index is not PMCUParameter.CU_INVALID_BYTE_INDEX() and bit_index is not PMCUParameter.CU_INVALID_BIT_INDEX():
                self._parameter = PMCUStandardParameter(pid, name, desc, byte_index, bit_index, target)
            elif byte_index is PMCUParameter.CU_INVALID_BYTE_INDEX() and bit_index is PMCUParameter.CU_INVALID_BIT_INDEX():
                self._parameter = PMCUCalculatedParameter(pid, name, desc, target)
            else:
                raise Exception

        if name == "ecuparam":
            for (k, v) in attrs.items():
                if k == "id":
                    pid = v
                if k == "name":
                    name = v
                if k == "desc":
                    desc = v
                if k == "target":
                    target = int(v)

            self._parameter = PMCUFixedAddressParameter(pid, name, desc, target)

        if name == "switch":
            for (k, v) in attrs.items():
                if k == "id":
                    pid = v
                if k == "name":
                    name = v
                if k == "desc":
                    desc = v
                if k == "byte":
                    address = int(v, 16)
                if k == "ecubyteindex":
                    byte_index = int(v)
                if k == "bit":
                    bit_index = int(v)
                if k == "target":
                    target = int(v)

            self._parameter = PMCUSwitchParameter(pid, name, desc, address, byte_index, bit_index, target)

        if name == "address":
            self._address_length = 1
            for (k, v) in attrs.items():
                if k == "length":
                    self._address_length = int(v)

        if name == "conversion":
            for (k, v) in attrs.items():
                if k == "units":
                    units = v
                if k == "expr":
                    expr = v
                if k == "format":
                    value_format = v

            self._parameter.add_conversion(PMCUConversion(units, expr, value_format))

        if name == "ecu":
            for (k, v) in attrs.items():
                if k == "id":
                    self._ecu_ids = v.split(",")

        if name == "ref":
            for (k, v) in attrs.items():
                if k == "parameter":
                    self._parameter.add_dependency(v)

    def characters(self, content):
        self._characters = self._characters + content

    def endElement(self, name):
        if name == "parameter":
            self._parameters.add(self._parameter)
            self._parameter = None

        if name == "ecuparam":
            self._parameters.add(self._parameter)
            self._parameter = None

        if name == "switch":
            self._parameters.add(self._parameter)
            self._parameter = None

        if name == "address":
            self._characters = self._characters.strip()

            if len(self._characters.strip()) > 0:

                if self._parameter.get_cu_type() == PMCUParameter.CU_TYPE_STD_PARAMETER():
                    self._parameter.set_address(PMCUAddress(int(self._characters, 16), self._address_length))
                elif self._parameter.get_cu_type() == PMCUParameter.CU_TYPE_FIXED_ADDRESS_PARAMETER():
                    address = PMCUAddress(int(self._characters, 16), self._address_length)
                    for ecu_id in self._ecu_ids:
                        self._parameter.add_ecu_id(ecu_id, address)

            self._address_length = 0
            self._characters = ''

        if name == "ecu":
            self._ecu_ids = None

        self._element_no += 1

        if self._element_no % 1000 == 0:
            self.log_progress()

    def log_progress(self):
        PM.log(self._message + " " + str(self._element_no) + " elements, " + str(len(self._parameters)) + " parameters",
               self._log_id)
