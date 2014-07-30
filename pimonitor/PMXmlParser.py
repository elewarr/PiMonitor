'''
Created on 29-03-2013

@author: citan
'''

import xml.sax
import os.path

from pimonitor.PM import PM
from pimonitor.PMParameter import PMParameter

# TODO: dependencies
# TODO: ecuparams

#<parameter id="P1" name="Engine Load (Relative)" desc="P1" ecubyteindex="8" ecubit="7" target="1">
#    <address>0x000007</address>
#    <conversions>
#        <conversion units="%" expr="x*100/255" format="0.00" />
#    </conversions>
#</parameter>

#<ecuparam id="E20" name="Manifold Absolute Pressure (Direct)*" desc="E20-Manifold Absolute Pressure with " target="1">
#    <ecu id="1B04400405">
#        <address length="2">0x2186A</address>
#    </ecu>
# ... ecu and conversions

# <switch id="S71" name="Clear Memory Terminal" desc="(E) S71" byte="0x000061" bit="0" ecubyteindex="19" target="1" />

class PMXmlParser(xml.sax.ContentHandler):
	'''
	classdocs
	'''


	def __init__(self):
		'''
		Constructor
		'''
		xml.sax.ContentHandler.__init__(self)
		
	def parse(self, file_name):
		self._parameters = set()
		self._parameter = None
		self._element_no = 0
		self._characters = ''
		self._ecu_id = None
		
		self._message = "Parsing XML data"
		self._log_id = PM.log(self._message)
		source = open(os.path.join("data", file_name))
		xml.sax.parse(source, self)
		PM.log(self._message + " [DONE]", self._log_id)
		
		return self._parameters

	def startElement(self, name, attrs):
		if name == "parameter":
			byte_index = "none"
			bit_index = "none"

			for (k,v) in attrs.items():
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

			self._parameter = PMParameter(pid, name, desc, byte_index, bit_index, target)

		if name == "switch":
			byte_index = "none"
			bit_index = "none"

			for (k,v) in attrs.items():
				if k == "id":
					pid = v
				if k == "name":
					name = v
				if k == "desc":
					desc = v
				if k == "ecubyteindex":
					byte_index = int(v)
				if k == "bit":
					bit_index = int(v)
				if k == "target":
					target = int(v)
				if k == "byte":
					address = v

			self._parameter = PMParameter(pid, name, desc, byte_index, bit_index, target)
			self._parameter.set_address(int(address, 16), 1)
			
	   	if name == "ecuparam":
			byte_index = "none"
			bit_index = "none"

			for (k,v) in attrs.items():
				if k == "id":
					pid = v
				if k == "name":
					name = v
				if k == "desc":
					desc = v
				if k == "target":
					target = int(v)
					
			self._parameter = PMParameter(pid, name, desc, byte_index, bit_index, target)
							 
		if name == "address":
			self._addrlen = 1
			for (k,v) in attrs.items():
				if k == "length":
					self._addrlen = int(v)
					
		if name == "depends":
			self._addrlen = 0

		if name == "ref":
			for (k,v) in attrs.items():
				if k == "parameter":
					self._parameter.add_dependency(v)
			
		if name == "conversion":
			for (k,v) in attrs.items():
				if k == "units":
					units = v
				if k == "expr":
					expr = v
				if k == "format":
					value_format = v
					
			self._parameter.add_conversion([units, expr, value_format])
		
		if name == "ecu":
			for (k,v) in attrs.items():
				if k == "id":
					self._parameter.init_ecu_id(v)
					self._ecu_id = self._parameter.get_ecu_id(v)
					
		self._name = name

	def characters(self, content):
		self._characters = self._characters + content
		
	def endElement(self, name):
		if name == "parameter":
			self._parameters.add(self._parameter)
			self._parameter = None
			self._addrlen = None
			
		if name == "ecuparam":
			self._parameters.add(self._parameter)
			self._parameter = None
			self._addrlen = None
		
		if name == "switch":
			#self._parameters.add(self._parameter)
			self._parameter = None
			self._addrlen = None
		
		if name == "address":
			self._characters = self._characters.strip()
			if len(self._characters.strip()) > 0 and self._name == "address" and self._parameter != None:			
				if self._ecu_id == None:
					self._parameter.set_address(int(self._characters, 16), self._addrlen)
				else:					
					self._ecu_id.append(int(self._characters, 16))
					self._ecu_id.append(self._addrlen)

			self._addrlen = 0
			self._characters = ''

		if name == "ecu":
			self._ecu_id = None

		if name == "depends":
			pass

		self._name = ""
		
		self._element_no += 1
		
		if self._element_no % 1000 == 0:
			PM.log(self._message + " " + str(self._element_no) + " elements", self._log_id)
