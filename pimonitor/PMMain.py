# -*- coding: utf-8 -*-

"""
Created on 29-03-2013

@author: citan
"""

import os
import os.path
import time
import cPickle as pickle
import platform
import re
import sys

from pimonitor.PM import PM
from pimonitor.PMConnection import PMConnection
from pimonitor.PMDemoConnection import PMDemoConnection
from pimonitor.PMXmlParser import PMXmlParser
from pimonitor.cu.PMCUParameter import PMCUParameter
from pimonitor.cu.PMCUContext import PMCUContext
from pimonitor.ui.PMScreen import PMScreen
from pimonitor.ui.PMSingleWindow import PMSingleWindow
from pimonitor.ui.PMWindow import PMWindow


def stringSplitByNumbers(x):
    r = re.compile('(\d+)')
    l = r.split(x.get_id())
    return [int(y) if y.isdigit() else y for y in l]


if __name__ == '__main__':

    if platform.system() == "Linux":
        from evdev import InputDevice, list_devices

        devices = map(InputDevice, list_devices())
        eventX = ""
        for dev in devices:
            if dev.name == "ADS7846 Touchscreen":
                eventX = dev.fn

        os.environ["SDL_FBDEV"] = "/dev/fb1"
        os.environ["SDL_MOUSEDRV"] = "TSLIB"
        os.environ["SDL_MOUSEDEV"] = eventX

    screen = PMScreen()
    log_id = PM.log('Application started')

    screen.render()

    parser = PMXmlParser()

    supported_parameters = []

    if os.path.isfile("data/data.pkl"):
        serializedDataFile = open("data/data.pkl", "rb")
        defined_parameters = pickle.load(serializedDataFile)
        serializedDataFile.close()
    else:
        defined_parameters = parser.parse("logger_METRIC_EN_v263.xml")
        defined_parameters = sorted(defined_parameters, key=lambda x: x.get_id(), reverse=True)
        output = open("data/data.pkl", "wb")
        pickle.dump(defined_parameters, output, -1)
        output.close()

    if len(sys.argv) > 1 and sys.argv[1] == "demo":
        connection = PMDemoConnection()
    elif platform.system() == "Linux":
        connection = PMConnection()
    else:
        connection = PMDemoConnection()

    while True:
        try:
            connection.open()
            ecu_packet = connection.init(1)
            tcu_packet = connection.init(2)

            ecu_context = PMCUContext(ecu_packet, [1, 3])
            ecu_parameters = ecu_context.match_parameters(defined_parameters)
            ecu_switch_parameters = ecu_context.match_switch_parameters(defined_parameters)
            ecu_calculated_parameters = ecu_context.match_calculated_parameters(defined_parameters, ecu_parameters)

            tcu_context = PMCUContext(tcu_packet, [2])
            tcu_parameters = tcu_context.match_parameters(defined_parameters)
            tcu_switch_parameters = tcu_context.match_switch_parameters(defined_parameters)
            tcu_calculated_parameters = tcu_context.match_calculated_parameters(defined_parameters, tcu_parameters)

            PM.log("ECU ROM ID: " + ecu_context.get_rom_id())
            PM.log("TCU ROM ID: " + tcu_context.get_rom_id())

            supported_parameters = ecu_parameters + ecu_switch_parameters + ecu_calculated_parameters + tcu_parameters + tcu_switch_parameters + tcu_calculated_parameters

            supported_parameters = sorted(supported_parameters, key=stringSplitByNumbers)

            pids = ["E114", "P104", "P122", "P97", "P203"]
            first_window_parameters = []

            for parameter in supported_parameters:
                if parameter.get_id() in pids:
                    pids.remove(parameter.get_id())
                    first_window_parameters.append(parameter)

            window = PMWindow(first_window_parameters)
            screen.add_window(window)

            for parameter in supported_parameters:
                window = PMSingleWindow(parameter)
                screen.add_window(window)

            screen.next_window()

            while True:
                window = screen.get_window()
                parameters = window.get_parameters()

                # TODO refactor - not possible to test at the moment, so leave working part untouched
                if len(parameters) == 1:
                    parameter = parameters[0]
                    if parameter.get_cu_type() == PMCUParameter.CU_TYPE_STD_PARAMETER():
                        packet = connection.read_parameter(parameter)
                        window.set_packets([packet])
                    elif parameter.get_cu_type() == PMCUParameter.CU_TYPE_FIXED_ADDRESS_PARAMETER():
                        packet = connection.read_parameter(parameter)
                        window.set_packets([packet])
                    elif parameter.get_cu_type() == PMCUParameter.CU_TYPE_SWITCH_PARAMETER():
                        packet = connection.read_parameter(parameter)
                        window.set_packets([packet])
                    elif parameter.get_cu_type() == PMCUParameter.CU_TYPE_CALCULATED_PARAMETER():
                        packets = connection.read_parameters(parameter.get_dependencies())
                        window.set_packets(packets)
                elif len(parameters) > 1:
                    packets = connection.read_parameters(parameters)
                    window.set_packets(packets)

                screen.render()

        except IOError as e:
            PM.log('I/O error: {0} {1}'.format(e.errno, e.strerror), log_id)
            if connection is not None:
                connection.close()
                time.sleep(3)
            continue

    screen.close()

