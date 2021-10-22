# MeteoBridgeAuth
Nodeserver to acquire data using templates from Meteobridge 
weather server.  Requires authorization thus entry of username
and password.  This nodeserver is an adaptation of the
meteobridgepoly nodeserver written by [Bob Pauuwe](http://www.bobsplace.com).

This node server is designed to support the [Meteobridge](http://www.meteobridge.com/)
in combination with a [Davis Instruments Vantage Pro 2+](https://www.davisinstruments.com/solution/vantage-pro2/) weather station
It should run with other Meteobridge connected weather stations, but 
the evapotranspiration values provided by the VP2+ will be missing
 
## Installation

1. Backup Your ISY in case of problems!
   * Really, do the backup, please
2. Go to the Polyglot Store in the UI and install.
3. Add NodeServer in Polyglot Web
   * After the install completes, Polyglot will reboot your ISY, you can watch the status in the main polyglot log.
4. Once your ISY is back up open the Admin Console.
5. The node server should automatically run and find your hub(s) and start adding weather sensors.  It can take a couple of minutes to discover the sensors. Verify by checking the nodeserver log. 
   * While this is running you can view the nodeserver log in the Polyglot UI to see what it's doing

### Node Settings
The settings for this node are:

#### Short Poll
   * Not used
#### Long Poll
   * How often the MeteoBridge is polled for data
#### Password
   * Password associated with above username
#### IPAddress
   * Configure the IP address of the MeteoBridge.
#### Units
   * Configure the units used when displaying data. Choices are:
   *   metric - SI / metric units
   *   us     - units generally used in the U.S.

## Requirements

1. This NS has been tested and verified for compatibility with UDI Polisy.
2. This has only been tested with ISY 5.0.16C so it is not guaranteed to work with any other version.
3. The NS has only been tested with a Davis Vantage Pro2+ via Meteobridge, so full compatibility with other platforms is not guaranteed.

## Issues
Please raise any issues on the UDI forum at "https://forum.universal-devices.com/topic/28637-new-meteobridge-weather-nodeserver/" Github is not watched.
# Upgrading

Open the Polyglot web page, go to nodeserver store and click "Update" for "MeteoBridge".

Then restart the MeteoBridge nodeserver by selecting it in the Polyglot dashboard and select Control -> Restart, then watch the log to make sure everything goes well.

The MeteoBridge nodeserver keeps track of the version number and when a profile rebuild is necessary.  The profile/version.txt will contain the MeteoBridge profile_version which is updated in server.json when the profile should be rebuilt.

# Release Notes
- 1.2.8 10/03/2021
    - profile update to 0.3.1
- 1.2.7 23/02/2021
    - catch and exception where sometimes the Meteobridge returns a nul string for cardinal wind direction text.
- 1.2.6 13/06/2020
    - update requirements for polyinterface 2.1.0
- 1.2.5 28/04/2020
    - simplify basic authorization method in requests.get
    - add node hints
    - add drivers in controller node for ISS battery state and last good data time
- 1.2.4 31/03/2020
    - fix calculation of metric windspeeds
- 1.2.3 27/03/2020
    - bugfix for wind nodes when using US units
- 1.2.2 26/03/2020
    - add cardinal wind direction
- 1.2.1 08/03/2020
    - test for UV sensor presence separately from Solar Sensor.  Apparently, there are some cases where one is installed but not the other.  The Driver displays "0" if the sensor is not available.
- 1.2.0 19/02/2020
    - add Last observation timestamp to primary node. This field displays HHmmss in local time.
- 1.1.0 18/02/2020
    - display both MPS and KPH in wind data node - may require delete/add of NS
- 1.0.9 12/02/2020
    - title change, minor code cleanup
    - strip trailing "%20" from MB template
    - minor fix to log level setting
- 1.0.8 11/02/2020
    - add log level setting to primary node. This update may require delete (not uninstall)/ add of the NS
    - minor code cleanup
    - change primary node address for clarity
- 1.0.7 08/02/2020
    - update requirements.txt and install.sh
- 1.0.6 27/01/2020
    - add a 'longPoll' in start() to immediately populate node fields 
- 1.0.5 20/01/2020
    - add some error trapping for bad/missing values from Meteobridge
- 1.0.4 18/01/2020
   - move create_url call to the start method.  There's no need to re-create it during each longpoll.
- 1.0.3 17/01/2020
   - made some corrections to README.md
   - fixed pressure trend display for "us" units
   - added 24 hour rainfall data 
- 1.0.2 17/01/2020
   - add missing conversion to "us" units for evapotranspiration
   - add missing monthly rainfall data
- 1.0.1 17/01/2020 
    - remove custom parameter for username, it is hard coded as
 "meteobridge" in the MeteoBridge.
    - fixed missing driver update for monthly rainfall
    - added yearly rainfall accumulation
- 1.0.0 16/01/2020
   - Initial alpha release
