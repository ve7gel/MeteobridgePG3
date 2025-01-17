# !/usr/bin/env python3
"""
Polyglot v3 node server for Meteobridge
Copyright (C) 2021 Gordon Larsen
"""
from udi_interface import Node, LOGGER
from constants import LITE_DRVS, UOM


class LightningNode(Node):
    id = 'zap'
    units = 'metric'
    drivers = []
    hint = [1, 0x0b, 1, 0]

    def __init__(self, polyglot, parent, address, name):
        super(LightningNode, self).__init__(polyglot, parent, address, name)

    def set_Driver(self, driver, value, units=None):

        if driver == 'GV0':
            distance = value
            if self.units == 'us':
                value = round(distance / 1.6, 1)

        super(LightningNode, self).setDriver(driver, round(value, 1))

    def define_drivers(self, driver_list):
        LOGGER.debug(f'Driver_list: {driver_list}')

        for d in driver_list:
            LightningNode.drivers.append(
                {
                    'driver': LITE_DRVS[d],
                    'value': 0,
                    'uom': UOM[driver_list[d]]
                })

        LOGGER.debug(f'Lightning Node drivers = {LightningNode.drivers}')

        return LightningNode.drivers