# !/usr/bin/env python3
"""
Polyglot v3 node server for Meteobridge
Copyright (C) 2021 Gordon Larsen
"""
import udi_interface
import uom

LOGGER = udi_interface.LOGGER
Custom = udi_interface.Custom


class PrecipNode(udi_interface.Node):
    id = 'precipitation'
    units = 'metric'
    drivers = []
    hint = [1, 0x0b, 1, 0]

    def __init__(self, polyglot, parent, address, name):
        super(PrecipNode, self).__init__(polyglot, parent, address, name)

        self.poly = polyglot
        self.count = 0
        self.rain_list = {}

        self.Parameters = Custom(polyglot, 'customparams')
        self.define_drivers()

        # subscribe to the events we want
        polyglot.subscribe(polyglot.CUSTOMPARAMS, self.parameterHandler)

    #        polyglot.subscribe(polyglot.POLL, self.poll)

    def parameterHandler(self, params):
        self.Parameters.load(params)
        self.units = self.Parameters['Units']
        LOGGER.debug(f'self.units in PrecipNode = {self.units}')

    def set_Driver(self, driver, value, **kwargs):

        if self.units == 'us':
            value = round(value * 0.03937, 2)
        else:
            value = round(value, 1)

        super(PrecipNode, self).setDriver(driver, value, report=True, force=True)

    def define_drivers(self):
        self.rain_list['rate'] = 'I_MMHR' if self.units == 'metric' else 'I_INHR'
        self.rain_list['daily'] = 'I_MM' if self.units == 'metric' else 'I_INCHES'
        self.rain_list['24hour'] = 'I_MM' if self.units == 'metric' else 'I_INCHES'
        self.rain_list['yesterday'] = 'I_MM' if self.units == 'metric' else 'I_INCHES'
        self.rain_list['monthly'] = 'I_MM' if self.units == 'metric' else 'I_INCHES'
        self.rain_list['yearly'] = 'I_MM' if self.units == 'metric' else 'I_INCHES'

        driver_list = []

        for d in self.rain_list:
            driver_list.append(
                {
                    'driver': uom.RAIN_DRVS[d],
                    'value': 0,
                    'uom': uom.UOM[self.rain_list[d]]
                })
        self.drivers = driver_list
        LOGGER.debug('Defining rain drivers = {}'.format(self.drivers))
        # self.wait_for_node_done()
