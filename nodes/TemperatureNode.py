# !/usr/bin/env python3
"""
Polyglot v3 node server for Meteobridge
Copyright (C) 2021 Gordon Larsen
"""
from udi_interface import LOGGER, Node, Custom
import sys
import uom


# class TemperatureNode(udi_interface.Node):
class TemperatureNode(Node):
    id = 'temperature'
    drivers = []

    hint = [1, 0x0b, 1, 0]

    def __init__(self, polyglot, parent, address, name, temp_list=None, units=None):
        super().__init__(polyglot, parent, address, name)

        self.poly = polyglot
        self.count = 0
        self.temperature_list = temp_list
        self.units = units
        self.define_drivers()

    def set_Driver(self, driver, value, units=None):
        if self.units == "us":
            value = (value * 1.8) + 32  # convert to F

        self.setDriver(driver, round(value, 1))

    def define_drivers(self):
        self.temperature_list['main'] = 'I_TEMP_F' if self.units == 'us' else 'I_TEMP_C'
        self.temperature_list['dewpoint'] = 'I_TEMP_F' if self.units == 'us' else 'I_TEMP_C'
        self.temperature_list['windchill'] = 'I_TEMP_F' if self.units == 'us' else 'I_TEMP_C'
        self.temperature_list['tempmax'] = 'I_TEMP_F' if self.units == 'us' else 'I_TEMP_C'
        self.temperature_list['tempmin'] = 'I_TEMP_F' if self.units == 'us' else 'I_TEMP_C'

        driver_list = []

        for d in self.temperature_list:
            driver_list.append(
                {
                    'driver': uom.TEMP_DRVS[d],
                    'value': 0,
                    'uom': uom.UOM[self.temperature_list[d]]
                })
        self.drivers = driver_list
        LOGGER.debug('Defining temperature drivers = {}'.format(self.drivers))
        # self.wait_for_node_done()
