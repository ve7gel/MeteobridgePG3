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

MBTEMPLATE = {
    "[th0temp-act] ",  # 0, current outdoor temperature
    "[th0temp-dmax] ",  # 1, max outdoor temp today
    "[th0temp-dmin] ",  # 2, min outdoor temp today
    "[th0dew-act] ",  # 3, current outdoor dewpoint
    "[wind0chill-act] ",  # 4 current windchill as calculated by MeteoBridge

    "[th0hum-act] ",  # 5 current outdoor relative humidity
    "[th0hum-dmax] ",  # 6 max outdoor relative humidity today
    "[th0hum-dmin] ",  # 7 min outddor relative humidity today

    "[thb0press-act] ",  # 8 current station pressure
    "[thb0seapress-act] ",  # 9 current sealevel barometric pressure
    "[thb0press-delta3h=barotrend] ",  # 10 pressure trend

    "[sol0rad-act] ",  # 11 current solar radiation
    "[uv0index-act] ",  # 12 current UV index
    "[sol0evo-daysum] ",  # 13 today's cumulative evapotranspiration - Davis Vantage only

    "[wind0avgwind-act] ",  # 14 average wind (depends on particular station)
    "[wind0wind-max10] ",  # 15 10 minute wind gust
    "[wind0dir-act] ",  # 16 current wind direction
    "[wind0dir-act=endir] ",  # 17 current cardinal wind direction

    "[rain0rate-act] ",  # 18 current rate of rainfall
    "[rain0total-daysum] ",  # 19 rain accumulation for today
    "[rain0total-sum24h] ",  # 20 rain over the last 24 hours
    "[rain0total-ydmax] ",  # 21 total rainfall yesterday
    "[rain0total-monthsum] ",  # 22 rain accumulation for this month
    "[rain0total-yearsum] ",  # 23 rain accumulation year-to-date

    "[mbsystem-station] ",  # 24 station id
    "[mbsystem-stationnum] ",  # 25 meteobridge station number
    "[thb0lowbat-act] ",  # 26 Station battery status (0=Ok, 1=Replace)
    "[th0lowbat-act] ",  # 27 Station battery status (0=Ok, 1=Replace)

    #  "[UYYYY][UMM][UDD][Uhh][Umm][Uss] ",  # 28 current observation time
    "[hh][mm][ss] ",
    "[epoch] ",  # 29 current unix time
    "[mbsystem-lastgooddata]",  # 30 seconds since last good data received from console
}