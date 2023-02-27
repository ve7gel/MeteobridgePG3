# !/usr/bin/env python3
"""
Polyglot v3 node server for Meteobridge
Copyright (C) 2021 Gordon Larsen
"""
from udi_interface import Node, LOGGER
from constants import PRES_DRVS, UOM


class PressureNode(Node):
    id = 'pressure'
    units = 'metric'
    drivers = []
    hint = [1, 0x0b, 1, 0]

    def __init__(self, polyglot, parent, address, name):
        super(PressureNode, self).__init__(polyglot, parent, address, name)

    def set_Driver(self, driver, value, units=None):
        if driver != 'GV1':
            if units == 'us':
                value = round(value * 0.02952998751, 2)
            else:
                value = round(value, 1)

        super(PressureNode, self).setDriver(driver, value)

    def define_drivers(self, driver_list):

        LOGGER.debug(f'Driver_list: {driver_list}')
        for d in driver_list:
            PressureNode.drivers.append(
                {
                    'driver': PRES_DRVS[d],
                    'value': 0,
                    'uom': UOM[driver_list[d]]
                })

        LOGGER.debug(f'Pressure Node drivers = {PressureNode.drivers}')

        return PressureNode.drivers
