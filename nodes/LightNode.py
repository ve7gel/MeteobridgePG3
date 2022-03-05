# !/usr/bin/env python3
"""
Polyglot v3 node server for Meteobridge
Copyright (C) 2021 Gordon Larsen
"""
import udi_interface
import uom

LOGGER = udi_interface.LOGGER
Custom = udi_interface.Custom


class LightNode(udi_interface.Node):
    id = 'light'
    units = 'metric'
    drivers = []
    hint = [1, 0x0b, 1, 0]

    def __init__(self, polyglot, parent, address, name, units):
        super(LightNode, self).__init__(polyglot, parent, address, name)

        self.poly = polyglot
        self.count = 0
        self.light_list = {}
        self.units = units

        self.Parameters = Custom(polyglot, 'customparams')
        self.define_drivers()

        # subscribe to the events we want
        polyglot.subscribe(polyglot.CUSTOMPARAMS, self.parameterHandler)
#        polyglot.subscribe(polyglot.POLL, self.poll)

    def parameterHandler(self, params):
        self.Parameters.load(params)
        self.units = self.Parameters['Units']

    def set_Driver(self, driver, value, **kwargs):

        super(LightNode, self).setDriver(driver, round(value, 1))

    def define_drivers(self):

        self.light_list['uv'] = 'I_UV'
        self.light_list['solar_radiation'] = 'I_RADIATION'
        self.light_list['evapotranspiration'] = 'I_MM' if self.units == 'metric' else 'I_INCHES'
        driver_list = []

        for d in self.light_list:
            driver_list.append(
                {
                    'driver': uom.LITE_DRVS[d],
                    'value': 0,
                    'uom': uom.UOM[self.light_list[d]]
                })
        self.drivers = driver_list
        LOGGER.debug('Defining light drivers = {}'.format(self.drivers))
