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

    def __init__(self, polyglot, parent, address, name):
        super().__init__(polyglot, parent, address, name)

        self.poly = polyglot
        self.count = 0

        self.units = units
        # self.define_drivers(temp_list)

    def set_Driver(self, driver, value, units=None):
        if self.units == "us":
            value = (value * 1.8) + 32  # convert to F

        self.setDriver(driver, round(value, 1))

    def define_drivers(self, drivers):

        driver_list = []

        for d in drivers:
            driver_list.append(
                {
                    'driver': uom.TEMP_DRVS[d],
                    'value': 0,
                    'uom': uom.UOM[drivers[d]]
                })
        self.drivers = driver_list
