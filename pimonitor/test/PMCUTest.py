from pimonitor.PMXmlParser import PMXmlParser
from pimonitor.cu.PMCUContext import PMCUContext

__author__ = 'citan'

import unittest

from pimonitor.PMDemoConnection import PMDemoConnection
from pimonitor.PM import PM

class PMCUTestCase(unittest.TestCase):

    def setUp(self):
        self._ecu_packet = None
        self._tcu_packet = None

        self._connection = None

        self._parameters = None

        self._ecu_context = None
        self._tcu_context = None

        self._ecu_parameters = None
        self._ecu_switch_parameters = None
        self._ecu_calculated_parameters = None

        self._tcu_parameters = None
        self._tcu_calculated_parameters = None
        self._tcu_switch_parameters = None

        logger = PM()
        logger.set(self.log)

    def prepare_1_open_connection(self):
        self._connection = PMDemoConnection()

        result = self._connection.open()
        self.assertTrue(result)

    def prepare_2_init_connection(self):
        self.prepare_1_open_connection()
        self.assertIsNotNone(self._connection)

        self._ecu_packet = self._connection.init(1)
        self.assertIsNotNone(self._ecu_packet)

        self._tcu_packet = self._connection.init(2)
        self.assertIsNotNone(self._tcu_packet)

    def prepare_3_parse_logger_definition(self):
        self.prepare_2_init_connection()
        parser = PMXmlParser()

        self._parameters = parser.parse("logger_METRIC_EN_v263.xml")

        self._parameters = sorted(self._parameters, key=lambda x: x.get_id(), reverse=True)

        self.assertIsNotNone(self._parameters)
        self.assertEqual(len(self._parameters), 716)

    def prepare_4_match_parameters(self):
        self.prepare_3_parse_logger_definition()

        self._ecu_context = PMCUContext(self._ecu_packet, [1, 3])
        self._ecu_parameters = self._ecu_context.match_parameters(self._parameters)
        self.assertIsNotNone(self._ecu_parameters)
        self.assertEqual(len(self._ecu_parameters), 125)

        self._ecu_switch_parameters = self._ecu_context.match_switch_parameters(self._parameters)
        self.assertIsNotNone(self._ecu_switch_parameters)
        self.assertEqual(len(self._ecu_switch_parameters), 36)

        self._ecu_calculated_parameters = self._ecu_context.match_calculated_parameters(self._parameters, self._ecu_parameters)
        self.assertIsNotNone(self._ecu_calculated_parameters)
        self.assertEqual(len(self._ecu_calculated_parameters), 4)

        self._tcu_context = PMCUContext(self._tcu_packet, [2])
        self._tcu_parameters = self._tcu_context.match_parameters(self._parameters)
        self.assertIsNotNone(self._tcu_parameters)
        self.assertEqual(len(self._tcu_parameters), 11)

        self._tcu_switch_parameters = self._tcu_context.match_switch_parameters(self._parameters)
        self.assertIsNotNone(self._tcu_switch_parameters)
        self.assertEqual(len(self._tcu_switch_parameters), 13)

        self._tcu_calculated_parameters = self._tcu_context.match_calculated_parameters(self._parameters, self._tcu_parameters)
        self.assertIsNotNone(self._tcu_calculated_parameters)
        self.assertEqual(len(self._tcu_calculated_parameters), 0)

        #TODO: switches

    def test_5_read_parameters(self):
        self.prepare_4_match_parameters()

        print self._ecu_parameters[120].to_string()
        packet = self._connection.read_parameter(self._ecu_parameters[120])
        value = self._ecu_parameters[120].get_value(packet)
        print 'value=' + value

    def log(self, message, mid):
        print message

        return mid

if __name__ == '__main__':
    unittest.main()
