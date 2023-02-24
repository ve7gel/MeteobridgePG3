# !/usr/bin/env python3
"""
Polyglot v3 node server for Meteobridge
Copyright (C) 2021 Gordon Larsen
"""
from udi_interface import LOGGER, Node
import uom


class WindNode(Node):
    id = 'wind'
    units = 'metric'
    drivers = []
    hint = [1, 0x0b, 1, 0]

    def __init__(self, polyglot, parent, address, name, wind_list, units=None):
        super(WindNode, self).__init__(polyglot, parent, address, name)

        self.poly = polyglot
        self.count = 0
        self.units = units

        self.define_drivers(wind_list)

    def set_Driver(self, driver, value, units=None):
        LOGGER.debug("WindNode.set_Driver driver {} value {}, type {}".format(driver, value, type(value)))
        if driver == 'GV3' or driver == 'GV4':
            # Metric value is meters/sec (not KPH)
            if self.units != 'metric':
                value = round(value * 2.23694, 2)
        if driver == 'ST' or driver == '0':
            # Alternate metric value is KPH)
            if self.units == 'metric':
                value = round(value * 3.6, 1)

        LOGGER.debug(f'Wind units is set to {self.units}, value {value}')

        self.setDriver(driver, value)

    def define_drivers(self, drivers):

        driver_list = []

        for d in drivers:
            driver_list.append(
                {
                    'driver': uom.WIND_DRVS[d],
                    'value': 0,
                    'uom': uom.UOM[drivers[d]]
                })
        self.drivers = driver_list
        LOGGER.debug('Defining wind drivers = {}'.format(self.drivers))
        # self.wait_for_node_done()
