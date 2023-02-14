# !/usr/bin/env python3
"""
Polyglot v3 node server for Meteobridge
Copyright (C) 2021 Gordon Larsen
"""
import udi_interface
import sys
import uom

LOGGER = udi_interface.LOGGER
Custom = udi_interface.Custom


class HumidityNode(udi_interface.Node):
    id = 'humidity'
    units = 'metric'
    drivers = []
    hint = [1, 0x0b, 1, 0]

    def __init__(self, polyglot, parent, address, name, driver_list):
        super(HumidityNode, self).__init__(polyglot, parent, address, name)

        self.poly = polyglot
        self.count = 0
        self.humidity_list = {}
        self.define_drivers(driver_list)

    def set_Driver(self, driver, value, **kwargs):

        super(HumidityNode, self).setDriver(driver, round(value, 1))

    def define_drivers(self, drivers):

        LOGGER.debug(f'HumidityNode drivers: {drivers}')

        driver_list = []

        # for d in self.humidity_list:
        for d in drivers:
            driver_list.append(
                {
                    'driver': uom.HUMD_DRVS[d],
                    'value': 0,
                    # 'uom': uom.UOM[self.humidity_list[d]]
                    'uom': uom.UOM[drivers[d]]
                })
        self.drivers = driver_list
        LOGGER.debug('Defining Humidity drivers = {}'.format(self.drivers))