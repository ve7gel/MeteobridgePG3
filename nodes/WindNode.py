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

    def __init__(self, polyglot, parent, address, name):
        super(WindNode, self).__init__(polyglot, parent, address, name)

    def set_Driver(self, driver, value, units=None):
        LOGGER.debug(f'WindNode.set_Driver driver {driver} value {value}, type {type(value)}')
        if driver == 'GV3' or driver == 'GV4':
            # Metric value is meters/sec (not KPH)
            if units != 'metric':
                value = round(value * 2.23694, 2)
        if driver == 'ST' or driver == '0':
            # Alternate metric value is KPH)
            if units == 'metric':
                value = round(value * 3.6, 1)

        LOGGER.debug(f'Wind units is set to {units}, value {value}')

        super(WindNode, self).setDriver(driver, value)

    def define_drivers(self, driver_list):
        LOGGER.debug(f'WindNode drivers: {driver_list}')

        for d in driver_list:
            WindNode.drivers.append(
                {
                    'driver': uom.WIND_DRVS[d],
                    'value': 0,
                    'uom': uom.UOM[driver_list[d]]
                })

        LOGGER.debug(f'Wind Node drivers = {WindNode.drivers}')

        return WindNode.drivers
