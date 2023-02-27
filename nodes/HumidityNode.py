# !/usr/bin/env python3
"""
Polyglot v3 node server for Meteobridge
Copyright (C) 2021 Gordon Larsen
"""
from udi_interface import LOGGER, Node
from constants import HUMD_DRVS, UOM


class HumidityNode(Node):
    id = 'humidity'
    drivers = []
    hint = [1, 0x0b, 1, 0]

    def __init__(self, polyglot, parent, address, name):
        super().__init__(polyglot, parent, address, name)

    def set_Driver(self, driver, value):
        super(HumidityNode, self).setDriver(driver, round(value, 1))

    def define_drivers(self, driver_list):
        LOGGER.debug(f'Driver_list: {driver_list}')
        for d in driver_list:
            HumidityNode.drivers.append(
                {
                    'driver': HUMD_DRVS[d],
                    'value': 0,
                    'uom': UOM[driver_list[d]]
                })

        LOGGER.debug(f'Temperature Node drivers {HumidityNode.drivers}')

        return HumidityNode.drivers
