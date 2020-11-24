import resources.api as api
import resources.orbit as orbit
from datetime import datetime

dateTimeObj = datetime.now()

satellite_tle1 = api.getSatelliteTLE('46235')
satellite_tle2 = api.getSatelliteTLE('25544')
satellite_tle3 = api.getSatelliteTLE('33752')

tle_list = []

tle1 = orbit.createTLE(satellite_tle1)
tle_list.append(tle1)

tle2 = orbit.createTLE(satellite_tle2)
tle_list.append(tle2)

tle3 = orbit.createTLE(satellite_tle3)
tle_list.append(tle3)

# 22°50'00.9"S 47°02'14.8"W
tle2.infoPrint()
tle2.groundTrack(dateTimeObj.timestamp(), -22.833425, -47.037964)
tle2.drawOrbit()

orbit.drawMultiOrbits(tle_list)

input("\nPress enter to exit ;)")