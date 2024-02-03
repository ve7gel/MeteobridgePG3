version = "3.1.4"  # added error trapping to catch missing values from Meteobridge


def cardinal_wind_dir_map(cardinal_dir):
    CARDINAL_WIND_DIR_MAP = {
        'N': 0,
        'NNE': 1,
        'NE': 2,
        'ENE': 3,
        'E': 4,
        'ESE': 5,
        'SE': 6,
        'SSE': 7,
        'S': 8,
        'SSW': 9,
        'SW': 10,
        'WSW': 11,
        'W': 12,
        'WNW': 13,
        'NW': 14,
        'NNW': 15
    }
    if cardinal_dir in CARDINAL_WIND_DIR_MAP:
        return CARDINAL_WIND_DIR_MAP[cardinal_dir]

    return 0


def mbtemplate():
    MBTEMPLATELIST = [
        "[th0temp-act]",  # 0, current outdoor temperature
        "[th0dew-act]",  # 1, current outdoor dewpoint
        "[wind0chill-act]",  # 2 current windchill as calculated by MeteoBridge
        "[th0temp-dmax]",  # 3, max outdoor temp today
        "[th0temp-dmin]",  # 4, min outdoor temp today

        "[th0hum-act]",  # 5 current outdoor relative humidity
        "[th0hum-dmax]",  # 6 max outdoor relative humidity today
        "[th0hum-dmin]",  # 7 min outddor relative humidity today

        "[thb0press-act]",  # 8 current station pressure
        "[thb0seapress-act]",  # 9 current sealevel barometric pressure
        "[thb0press-delta3h=barotrend]",  # 10 pressure trend

        "[sol0rad-act]",  # 11 current solar radiation
        "[uv0index-act]",  # 12 current UV index
        "[sol0evo-daysum]",  # 13 today's cumulative evapotranspiration - Davis Vantage only

        "[wind0avgwind-act]",  # 14 average wind (depends on particular station)
        "[wind0wind-max10]",  # 15 10 minute wind gust
        "[wind0dir-act]",  # 16 current wind direction
        "[wind0dir-act=endir]",  # 17 current cardinal wind direction

        "[rain0rate-act]",  # 18 current rate of rainfall
        "[rain0total-daysum]",  # 19 rain accumulation for today
        "[rain0total-sum24h]",  # 20 rain over the last 24 hours
        "[rain0total-ydmax]",  # 21 total rainfall yesterday
        "[rain0total-monthsum]",  # 22 rain accumulation for this month
        "[rain0total-yearsum]",  # 23 rain accumulation year-to-date

        "[mbsystem-station]",  # 24 station id
        "[mbsystem-stationnum]",  # 25 meteobridge station number
        "[thb0lowbat-act]",  # 26 Station battery status (0=Ok, 1=Replace)
        "[th0lowbat-act]",  # 27 Station battery status (0=Ok, 1=Replace)

        #  "[UYYYY][UMM][UDD][Uhh][Umm][Uss] ",  # 28 current observation time
        "[hh][mm][ss]",
        "[epoch]",  # 29 current unix time
        "[mbsystem-lastgooddata]",  # 30 seconds since last good data received from console
    ]
    mbtemplate_tmp = ""
    # values = str(CreateTemplate())
    for tempstr in MBTEMPLATELIST:
        mbtemplate_tmp = mbtemplate_tmp + tempstr + "%20"

    mbtemplate_tmp.strip("%20")
    # Insert spaces between elements of the template to allow splitting the returned data, but no trailing space
    return mbtemplate_tmp


# Unit of Measure map
#
# Map the editor ID to the ISY UOM number

UOM = {
    'I_TEMP_C': 4,
    'I_TEMP_F': 17,
    'I_HUMIDITY': 51,
    'I_MB': 117,
    'I_INHG': 23,
    'I_TREND': 25,
    'I_KPH': 32,
    'I_MPH': 48,
    'I_DEGREE': 14,
    'I_MMHR': 46,
    'I_INHR': 24,
    'I_MM': 82,
    'I_INCHES': 105,
    'I_UV': 71,
    'I_LUX': 36,
    'I_RADIATION': 74,
    'I_STRIKES': 56,
    'I_KM': 83,
    'I_MILE': 116,
    'I_MPS': 40,
    'I_BATTERY': 25,
    'I_LAST_UPDATE': 56,
    'I_CARDINAL': 25,
}

TEMP_DRVS = {
    'main': 'ST',
    'dewpoint': 'GV0',
    'windchill': 'GV1',
    'heatindex': 'GV2',
    'apparent': 'GV3',
    'inside': 'GV4',
    'extra1': 'GV5',
    'extra2': 'GV6',
    'extra3': 'GV7',
    'extra4': 'GV8',
    'extra5': 'GV9',
    'extra6': 'GV10',
    'extra7': 'GV11',
    'extra8': 'GV12',
    'extra9': 'GV13',
    'extra10': 'GV14',
    'tempmax': 'GV15',
    'tempmin': 'GV16',
    'soil': 'GV17',
}

HUMD_DRVS = {
    'main': 'ST',
    'inside': 'GV0',
    'max': 'GV1',
    'min': 'GV2',
    'extra3': 'GV3',
    'extra4': 'GV4',
    'extra5': 'GV5',
}

PRES_DRVS = {
    'station': 'ST',
    'sealevel': 'GV0',
    'trend': 'GV1'
}

WIND_DRVS = {
    'windspeed': 'ST',
    'gustspeed': 'GV0',
    'winddir': 'GV1',
    'winddircard': 'GV2',
    'windspeed1': 'GV3',
    'gustspeed1': 'GV4',
}

RAIN_DRVS = {
    'rate': 'ST',
    'hourly': 'GV0',
    'daily': 'GV1',
    '24hour': 'GV2',
    'monthly': 'GV3',
    'yearly': 'GV4',
    'maxrate': 'GV5',
    'yesterday': 'GV6',
    'total': 'GV7'
}

LITE_DRVS = {
    'uv': 'ST',
    'solar_radiation': 'GV0',
    'illuminace': 'GV1',
    'evapotranspiration': 'GV2'
}

LITE_EDIT = {
    'uv': 'I_UV',
    'solar_radiation': 'I_RADIATION',
    'illuminace': 'I_LUX',
    'evapotranspiration': 'I_MM'
}

LTNG_DRVS = {
    'strikes': 'ST',
    'distance': 'GV0'
}
