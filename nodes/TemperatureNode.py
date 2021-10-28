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


class TemperatureNode(udi_interface.Node):
    id = 'temperature'
    units = 'metric'
    drivers = []
    '''
    drivers = [{'driver': 'ST','value': 0, 'uom': 4},
               {'driver': 'GV0', 'value': 0, 'uom': 4},
               {'driver': 'GV1', 'value': 0, 'uom': 4},
               {'driver': 'GV15', 'value': 0, 'uom': 4},
               {'driver': 'GV16', 'value': 0, 'uom': 4}

    ]
    '''
    hint = [1, 0x0b, 1, 0]

    def __init__(self, polyglot, parent, address, name):
        super(TemperatureNode, self).__init__(polyglot, parent, address, name)

        self.poly = polyglot
        self.count = 0
        self.temperature_list = {}

        self.Parameters = Custom(polyglot, 'customparams')
        self.discover()

        # subscribe to the events we want
        self.poly.subscribe(polyglot.CUSTOMPARAMS, self.parameterHandler)
        self.poly.subscribe(self.poly.START, self.start, address)

    def parameterHandler(self, params):
        self.Parameters.load(params)
        self.units = self.Parameters['Units']

    """
    def poll(self, polltype):

        if 'shortPoll' in polltype:
            if self.Parameters['multiplier'] is not None:
                mult = int(self.Parameters['multiplier'])
            else:
                mult = 1

            self.count += 1

            self.setDriver('GV0', self.count, True, True)
            self.setDriver('GV1', (self.count * mult), True, True)
    """

    def start(self):
        # self.discover()
        # self.drivers = self.node_drivers.load(driverdata)
        LOGGER.debug("Drivers are: {}".format(self.drivers))

    def set_Driver(self, driver, value, **kwargs):
        if self.units == "us":
            value = (value * 1.8) + 32  # convert to F

        LOGGER.debug("In TempNode.setDriver: {} {}".format(driver, value))
        LOGGER.debug("Driver : {}".format(self.getDriver(driver)))
        # self.setDriver(driver, value)
        super(TemperatureNode, self).setDriver(driver, round(value, 1), report=True, force=True)

    def discover(self):
        self.temperature_list['main'] = 'I_TEMP_F' if self.units == 'us' else 'I_TEMP_C'
        self.temperature_list['dewpoint'] = 'I_TEMP_F' if self.units == 'us' else 'I_TEMP_C'
        self.temperature_list['windchill'] = 'I_TEMP_F' if self.units == 'us' else 'I_TEMP_C'
        self.temperature_list['tempmax'] = 'I_TEMP_F' if self.units == 'us' else 'I_TEMP_C'
        self.temperature_list['tempmin'] = 'I_TEMP_F' if self.units == 'us' else 'I_TEMP_C'
        # node = TemperatureNode(self.poly, self.address, 'temps', 'Temperatures')
        driver_list = []

        for d in self.temperature_list:
            driver_list.append(
                {
                    'driver': uom.TEMP_DRVS[d],
                    'value': 0,
                    'uom': uom.UOM[self.temperature_list[d]]
                })
        self.drivers = driver_list
        LOGGER.debug('in discover, drivers = {}'.format(self.drivers))
        # self.wait_for_node_done()
