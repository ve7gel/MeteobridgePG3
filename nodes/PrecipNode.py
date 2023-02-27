# !/usr/bin/env python3
"""
Polyglot v3 node server for Meteobridge
Copyright (C) 2021 Gordon Larsen
"""
from udi_interface import LOGGER, Node
from constants import RAIN_DRVS, UOM


class PrecipNode(Node):
    id = 'precipitation'
    drivers = []
    hint = [1, 0x0b, 1, 0]

    def __init__(self, polyglot, parent, address, name):
        super().__init__(polyglot, parent, address, name)

    def set_Driver(self, driver, value, units=None):

        if units == 'us':
            value = round(value * 0.03937, 2)
        else:
            value = round(value, 1)

        LOGGER.debug(f'Units is set to {units}, value {value}')

        # self.setDriver(driver, value)
        super(PrecipNode, self).setDriver(driver, value)

    def define_drivers(self, driver_list):

        for d in driver_list:
            PrecipNode.drivers.append(
                {
                    'driver': RAIN_DRVS[d],
                    'value': 0,
                    'uom': UOM[driver_list[d]]
                })

        return PrecipNode.drivers
