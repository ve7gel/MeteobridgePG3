# !/usr/bin/env python3
"""
Polyglot v3 node server for Meteobridge
Copyright (C) 2021 Gordon Larsen
"""
from udi_interface import LOGGER, Node
from constants import TEMP_DRVS, UOM


class TemperatureNode(Node):
    id = 'temperature'
    drivers = []

    hint = [1, 0x0b, 1, 0]

    def __init__(self, polyglot, parent, address, name):
        super().__init__(polyglot, parent, address, name)

    def set_Driver(self, driver, value, units=None):
        LOGGER.debug(f'TemperatureNode.set_Driver driver {driver} value {value}, type {type(value)}, units {units}')

        if units == "us":
            value = (value * 1.8) + 32  # convert to F

        super(TemperatureNode, self).setDriver(driver, round(value, 1))

    def define_drivers(self, driver_list):

        LOGGER.debug(f'Driver_list: {driver_list}')
        for d in driver_list:
            TemperatureNode.drivers.append(
                {
                    'driver': TEMP_DRVS[d],
                    'value': 0,
                    'uom': UOM[driver_list[d]]
                })

        LOGGER.debug(f'Temperature Node drivers {TemperatureNode.drivers}')

        return TemperatureNode.drivers
