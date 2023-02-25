# !/usr/bin/env python3
"""
Polyglot v3 node server for Meteobridge
Copyright (C) 2021 Gordon Larsen
"""
from udi_interface import LOGGER, Node
import uom


class PrecipNode(Node):
    id = 'precipitation'
    drivers = []
    hint = [1, 0x0b, 1, 0]

    def __init__(self, polyglot, parent, address, name, rain_list, units=None):
        super().__init__(polyglot, parent, address, name)

        self.poly = polyglot
        self.units = units
        self.define_drivers(rain_list)

    def set_Driver(self, driver, value, units=None):

        if self.units == 'us':
            value = round(value * 0.03937, 2)
        else:
            value = round(value, 1)

        LOGGER.debug(f'Units is set to {self.units}, value {value}')

        self.setDriver(driver, value)

    def define_drivers(self, drivers):

        driver_list = []

        for d in drivers:
            driver_list.append(
                {
                    'driver': uom.RAIN_DRVS[d],
                    'value': 0,
                    'uom': uom.UOM[drivers[d]]
                })
        self.drivers = driver_list
