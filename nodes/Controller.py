# !/usr/bin/env python3
"""
NodeServer to extract weather data from a Meteobridge Weather device.  Designed around a DAVIS VP2+ weather station. May work
for others, not tested.  At the moment, only DAVIS stations provide ET0 readings.

Based on MeteoBridge nodeserver (meteobridgepoly) authored by Bob Paauwe
Customized to use template queries from MeteoBridge by Gordon Larsen

Copyright 2021 Robert Paauwe and Gordon Larsen, MIT License
"""
import time

from udi_interface import Node, Custom, LOGGER

from write_profile import write_profile
import requests

from nodes import TemperatureNode
from nodes import HumidityNode
from nodes import PressureNode
from nodes import WindNode
from nodes import PrecipNode
from nodes import LightNode
from nodes import LightningNode

from constants import *


class Controller(Node):
    id = 'meteobridge'
    drivers = [
        {'driver': 'ST', 'value': 1, 'uom': 2},
        {'driver': 'GV0', 'value': 0, 'uom': 25},
        {'driver': 'GV1', 'value': 0, 'uom': 25},
        {'driver': 'GV2', 'value': 0, 'uom': 56},
        {'driver': 'GV3', 'value': 0, 'uom': 58},
    ]

    def __init__(self, polyglot, parent, address, name):
        super(Controller, self).__init__(polyglot, parent, address, name)
        self.discovery_done = False
        self.stopping = None
        self.hb = 0
        self.poly = polyglot
        self.name = name
        self.address = address
        self.primary = parent
        self.configured = False

        self.password = ""
        self.username = "meteobridge"

        self.Parameters = Custom(polyglot, 'customparams')
        self.Notices = Custom(polyglot, 'notices')

        # self.poly.subscribe(self.poly.CONFIG, self.configHandler)
        self.poly.subscribe(self.poly.CUSTOMPARAMS, self.parameterHandler)
        self.poly.subscribe(self.poly.START, self.start, address)
        self.poly.subscribe(self.poly.POLL, self.poll)
        # self.poly.subscribe(self.poly.CUSTOMDATA, address)
        self.poly.subscribe(self.poly.ADDNODEDONE, self.node_queue)
        self.poly.subscribe(self.poly.STOP, self.stop)

        self.temperature_list = {}
        self.humidity_list = {}
        self.pressure_list = {}
        self.wind_list = {}
        self.rain_list = {}
        self.light_list = {}
        self.lightning_list = {}
        self.myConfig = {}  # custom parameters
        self.units = 'metric'
        self.ip = ""
        self.n_queue = []
        self.driver_list = []

        self.last_wind_dir = ''
        self.lastgooddata = None

        self.poly.ready()
        self.poly.addNode(self)

    def node_queue(self, data):
        self.n_queue.append(data['address'])

    def wait_for_node_done(self):
        while len(self.n_queue) == 0:
            time.sleep(0.1)
        self.n_queue.pop()

    def start(self):
        LOGGER.info('Starting Meteobridge Node Server')
        self.poly.setCustomParamsDoc()
        LOGGER.debug(f'self.configured: {self.configured}, self.discovery.done {self.discovery_done}')
        while not self.configured:
            time.sleep(10)

        LOGGER.debug('Calling discovery from the start method')
        self.discover()
        LOGGER.debug(f'Discovery done: {self.discovery_done}')

        LOGGER.debug(f'Connecting to Meteobridge at: {self.ip}')
        data, result = self.stationdata(self.ip, self.username, self.password)

        while result != 200:
            LOGGER.info("Node server not configured yet")
            return

        self.set_drivers(data)

    def poll(self, polltype):
        if 'longPoll' in polltype:
            pass
        else:
            # read data
            LOGGER.debug(f'Configured: {self.configured}')
            while not self.configured:
                LOGGER.info("Plugin not configured yet")
                return
            # Code for testing new polling structure
            for node_address in self.poly.getNodes():
                node = self.poly.getNode(node_address)
                if node.address != 'controller':
                    LOGGER.debug(f'Polling, node={node}, node.address={node.address} node.name={node.name}')
            ###

            data, result = self.stationdata(self.ip, self.username, self.password)
            LOGGER.debug(f'return from getstationdata {data} result code {result}')
            while result != 200:
                # return if configuration is incomplete or incorrect
                return

            self.set_drivers(data)
            LOGGER.info("Updated data from Meteobridge")

    def set_drivers(self, data):
        try:

            # Temperature values
            node = TemperatureNode(self.poly, self.address, 'temps', 'Temperatures')
            d = node.drivers
            LOGGER.debug(f'Updating Temps Drivers {d}')

            x = 0
            for n in range(len(d)):
                node.set_Driver(d[n]['driver'], float(data[x]), self.units)
                x += 1

            # Precipitation values
            node = PrecipNode(self.poly, self.address, 'precip', 'Precipitation')
            d = node.drivers
            LOGGER.debug(f'Updating Precip Drivers{d}')

            x = 0
            for n in range(len(d)):
                node.set_Driver(d[n]['driver'], float(data[21 + x]), self.units)
                x += 1

            # Humidity values
            node = HumidityNode(self.poly, self.address, 'humid', 'Humidity')

            d = node.drivers
            LOGGER.debug(f'Updating Humidity Drivers {d}')
            x = 0
            for n in range(len(d)):
                node.set_Driver(d[n]['driver'], float(data[7 + x]), )
                x += 1

            # Wind values
            node = WindNode(self.poly, self.address, 'winds', 'Wind')
            d = node.drivers
            LOGGER.debug(f'Updating Wind Drivers {d}')

            try:  # Meteobridge seems to sometimes return a nul string for wind0dir-act=endir
                # so we substitute the last good reading
                # self.wind_dir_cardinal = self.wind_card_dict[data[20]]
                wind_dir_cardinal = cardinal_wind_dir_map(data[20])
                self.last_wind_dir = wind_dir_cardinal

            except:
                wind_dir_cardinal = self.last_wind_dir
                LOGGER.info(
                    f"Cardinal wind direction substituted for last good reading: {self.last_wind_dir} ({data[20]})")

            LOGGER.debug(
                f"mbr wind: {float(data[17])}, gust: {float(data[18])}, dir: {data[19]}, wdc: {data[20]}, "
                f"wind_dir_cardinal: {wind_dir_cardinal}, last_wind_dir: {self.last_wind_dir}")

            node.set_Driver(d[0]['driver'], float(data[17]), self.units)
            node.set_Driver(d[1]['driver'], data[18], self.units)
            node.set_Driver(d[2]['driver'], float(data[19]), self.units)
            node.set_Driver(d[3]['driver'], wind_dir_cardinal, )
            node.set_Driver(d[4]['driver'], float(data[17]), self.units)
            node.set_Driver(d[5]['driver'], float(data[18]), self.units)

            # Light values
            node = LightNode(self.poly, self.address, 'solar', 'Illumination')
            d = node.drivers
            LOGGER.debug(f'Updating Humidity Drivers {d}')
            try:
                uv = float(data[15])
                node.set_Driver(d[0]['driver'], uv, )
            except:  # no uv sensor
                node.set_Driver(d[0]['driver'], 0)

            try:
                solarradiation = float(data[14])
                solrad = True
            except:
            # catch case where solar data is not available
                solrad = False
                solarradiation = 0

            node.set_Driver(d[1]['driver'], solarradiation, )

            et0 = 0
            if solrad:
                if data[27] != "Vantage":
                    et0 = calculate_et0(obs_data=data)
                else:
                    et0 = float(data[16])
            else:
                LOGGER.info("Evapotranspiration not available ")

            node.set_Driver(d[2]['driver'], et0, units=self.units)


            # Barometric pressure values
            node = PressureNode(self.poly, self.address, 'press', 'Barometric Pressure')
            d = node.drivers
            LOGGER.debug(f'Updating Pressure Drivers {d}')

            node.set_Driver(d[0]['driver'], float(data[11]), self.units)
            node.set_Driver(d[1]['driver'], float(data[12]), self.units)
            node.set_Driver(d[2]['driver'], float(data[13]), self.units)

            # Lightning values
            node = LightningNode(self.poly, self.address, 'lightning', 'Lightning')
            d = node.drivers
            LOGGER.debug(f'Updating Lightning Drivers {d}')

            node.set_Driver(d[0]['driver'], float(data[34]), self.units)
            node.set_Driver(d[1]['driver'], float(data[35]), self.units)
            node.set_Driver(d[2]['driver'], float(data[36]), '0')

            # Update controller drivers now

            self.setDriver('GV3', data[33])  # Last good data
            self.setDriver('GV0', int(float(data[29])))  # Console battery
            self.setDriver('GV1', int(float(data[30])))  # ISS battery
            # value 0 = Ok, 1 = Replace
            self.setDriver('GV2', data[31])

            LOGGER.debug(f"Timestamp: {int(float(data[31]))}, Last good data: {data[33]} second(s) ago")

        except Exception as error:
            LOGGER.error("Uncaught error:", type(error), __name__, "-", error) # Some error occurred

    def discover(self, *args, **kwargs):
        LOGGER.info("Creating nodes.")
        # Temperatures Node
        node = TemperatureNode(self.poly, self.address, 'temps', 'Temperatures')
        node.drivers = node.define_drivers(self.temperature_list)
        self.poly.addNode(node)
        self.wait_for_node_done()

        # Precipitation node
        node = PrecipNode(self.poly, self.address, 'precip', 'Precipitation')
        node.drivers = node.define_drivers(self.rain_list)
        self.poly.addNode(node)
        self.wait_for_node_done()

        # Humiditys Node
        node = HumidityNode(self.poly, self.address, 'humid', 'Humidity')
        node.drivers = node.define_drivers(self.humidity_list)
        self.poly.addNode(node)
        self.wait_for_node_done()

        # Winds Node
        node = WindNode(self.poly, self.address, 'winds', 'Wind')
        node.drivers = node.define_drivers(self.wind_list)
        self.poly.addNode(node)
        self.wait_for_node_done()

        # Illumination node
        node = LightNode(self.poly, self.address, 'solar', 'Illumination')
        node.drivers = node.define_drivers(self.light_list)
        self.poly.addNode(node)
        self.wait_for_node_done()

        # Barometric Pressures Node
        node = PressureNode(self.poly, self.address, 'press', 'Barometric Pressure')
        node.drivers = node.define_drivers(self.pressure_list)
        self.poly.addNode(node)
        self.wait_for_node_done()

        # Lightning Node
        node = LightningNode(self.poly, self.address, 'lightning', 'Lightning')
        node.drivers = node.define_drivers(self.lightning_list)
        self.poly.addNode(node)
        self.wait_for_node_done()

        self.discovery_done = True
        LOGGER.debug("Finished discovery, node setup complete")

    def delete(self):
        self.stopping = True
        LOGGER.warning('Removing Meteobridge nodeserver.')

    def stop(self):
        LOGGER.warning('Meteobridge NodeServer stopped.')
        self.poly.stop()

    def parameterHandler(self, config):
        self.Parameters.load(config)
        LOGGER.debug(f'Parameters: {self.Parameters}')
        self.Notices.clear()
        ip_exists = False
        password_exists = False

        self.ip = self.Parameters['Address']
        if self.units is not None:
            self.units = self.Parameters['Units'].lower()
        self.password = self.Parameters['Password']

        # Add notices about missing configuration
        if self.ip == "":
            self.Notices['ipaddr'] = "IP address or hostname of your MeteoBridge device is required."
        else:
            ip_exists = True

        if self.password == "":
            self.Notices['Password'] = 'Password for MeteoBridge must be set'
        else:
            password_exists = True

        if ip_exists and password_exists:
            self.Notices.clear()
            self.setup_nodedefs(self.units)
            LOGGER.info(f'Configuration complete!')
            self.configured = True

    def setup_nodedefs(self, units):
        # Configure the units for each node driver
        self.temperature_list['main'] = 'I_TEMP_F' if units == 'us' else 'I_TEMP_C'
        self.temperature_list['dewpoint'] = 'I_TEMP_F' if units == 'us' else 'I_TEMP_C'
        self.temperature_list['windchill'] = 'I_TEMP_F' if units == 'us' else 'I_TEMP_C'
        self.temperature_list['tempmax'] = 'I_TEMP_F' if units == 'us' else 'I_TEMP_C'
        self.temperature_list['tempmin'] = 'I_TEMP_F' if units == 'us' else 'I_TEMP_C'
        self.temperature_list['inside'] = 'I_TEMP_F' if units == 'us' else 'I_TEMP_C'
        self.temperature_list['dewin'] = 'I_TEMP_F' if units == 'us' else 'I_TEMP_C'

        self.humidity_list['main'] = 'I_HUMIDITY'
        self.humidity_list['max'] = 'I_HUMIDITY'
        self.humidity_list['min'] = 'I_HUMIDITY'
        self.humidity_list['inside'] = 'I_HUMIDITY'

        self.pressure_list['station'] = 'I_INHG' if units == 'us' else 'I_MB'
        self.pressure_list['sealevel'] = 'I_INHG' if units == 'us' else 'I_MB'
        self.pressure_list['trend'] = 'I_TREND'
        self.wind_list['windspeed'] = 'I_MPS' if units == 'metric' else 'I_MPH'
        self.wind_list['gustspeed'] = 'I_MPS' if units == 'metric' else 'I_MPH'
        self.wind_list['winddir'] = 'I_DEGREE'
        self.wind_list['winddircard'] = 'I_CARDINAL'
        if units == 'metric':
            self.wind_list['windspeed1'] = 'I_KPH'
            self.wind_list['gustspeed1'] = 'I_KPH'
        else:
            self.wind_list['windspeed1'] = 'I_MPH'
            self.wind_list['gustspeed1'] = 'I_MPH'
        self.rain_list['rate'] = 'I_MMHR' if units == 'metric' else 'I_INHR'
        self.rain_list['daily'] = 'I_MM' if units == 'metric' else 'I_INCHES'
        self.rain_list['24hour'] = 'I_MM' if units == 'metric' else 'I_INCHES'
        self.rain_list['yesterday'] = 'I_MM' if units == 'metric' else 'I_INCHES'
        self.rain_list['monthly'] = 'I_MM' if units == 'metric' else 'I_INCHES'
        self.rain_list['yearly'] = 'I_MM' if units == 'metric' else 'I_INCHES'
        self.light_list['uv'] = 'I_UV'
        self.light_list['solar_radiation'] = 'I_RADIATION'
        self.light_list['evapotranspiration'] = 'I_MM' if units == 'metric' else 'I_INCHES'
        self.lightning_list['strikes'] = 'I_STRIKES'
        self.lightning_list['distance'] = 'I_KM' if units == 'metric' else 'I_MILE'
        self.lightning_list['energy'] = 'I_ENERGy'

        # Build the node definition
        LOGGER.info('Creating node definition profile based on config.')
        write_profile(self.temperature_list,
                      self.humidity_list, self.pressure_list, self.wind_list,
                      self.rain_list, self.light_list, self.lightning_list)
        time.sleep(3)
        # push updated profile to ISY
        try:
            self.poly.updateProfile()

        except:
            LOGGER.error('Failed to push profile to ISY')

    # Hub status information here: battery and data health values.

    def stationdata(self, ipaddr, username, password):
        """
            Here we assemble the url and template for the call to the Meteobridge
            and then unpack the returned data into variables. Simplified in Version 1.2.5 to
            streamline the basic auth method in requests.get
        """
        try:

            values = str(mbtemplate())
            url = 'http://' + ipaddr + '/cgi-bin/template.cgi?template='
            LOGGER.debug("url in getstationdata: {}".format(url + values))

            u = requests.get(url + values, auth=(username, password))
            mbrdata = u.content.decode('utf-8')
            result_code = u.status_code
            LOGGER.debug(f'mbrdata is: {mbrdata}, status: {result_code}')
            if result_code != 200:
                LOGGER.error(f'Unable to connect to your Meteobridge device: {result_code}')
                return '', result_code

        except OSError as err:
            LOGGER.error(f"Unable to connect to your Meteobridge device: {err}")
            return

        mbrarray = mbrdata.split(" ")
        LOGGER.debug("mbrarray: {}".format(mbrarray))

        try:
            temperature = float(mbrarray[0])  # test that there's a valid response

        except ValueError or AttributeError as e:
            LOGGER.error(f"Error in getstationdata: {e}")
            LOGGER.error("Invalid value")
            LOGGER.error(mbrarray)

        # Check for invalid responses from Meteobridge and replace them with zeroes to avoid type errors during
        # conversions from strings to numbers. This can happen when a value is missing from the template request and
        # the meteobridge returns the template value rather than the actual information.

        for i in range(len(mbrarray)):
            if "[" in mbrarray[i]:
                mbrarray[i] = '0'
        LOGGER.debug("filtered mbrarray: {}".format(mbrarray))

        return mbrarray, result_code

def calculate_et0(obs_data):
    # Thanks to dwburger for this Python script
    # dwburger (https://github.com/dwburger/Tempest-ET0/blob/main/Tempest-ET0.py)
    # modified to suit array configuration from existing package
    # obs_data = data['obs'][0]
    LOGGER.debug(f'obs_data in calculate_et0 is: {obs_data}')

    air_temp = (float(obs_data[3])+float(obs_data[4])) / 2
    wind_speed = float(obs_data[17])
    rel_humidity = (float(obs_data[8]) + float(obs_data[9])) / 2

    # Check if solar radiation data is available; use 0 if None
    solar_radiation_raw = float(obs_data[14])
    solar_radiation = solar_radiation_raw * 0.0864 if solar_radiation_raw is not None else 0  # MJ/m^2/day conversion

    ALBEDO = 0.23
    G = 0.0
    PSY_CONST = 0.665e-3
    es = 0.6108 * (10 ** ((7.5 * air_temp) / (237.3 + air_temp)))
    ea = es * (rel_humidity / 100.0)
    delta = (4098.0 * es) / ((air_temp + 237.3) ** 2)
    Rn = (1 - ALBEDO) * solar_radiation - 0.34 * (1.35 * solar_radiation / 2.3 - 1.0)
    et0_daily = (0.408 * delta * (Rn - G) + PSY_CONST * (900 / (air_temp + 273)) * wind_speed * (es - ea)) / (
                delta + PSY_CONST * (1 + 0.34 * wind_speed))

    et0_hourly = et0_daily / 24  # Daily to hourly ET0
    # et0_in_inches = et0_hourly / 25.4  # Convert mm to inches
    LOGGER.debug("et0 calculated: {}".format(et0_daily))
    return et0_daily # mm/hour