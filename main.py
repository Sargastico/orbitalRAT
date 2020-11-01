import resources.api as api
import resources.orbit as orbit

resp1 = api.getSatelliteTLE('46235')
resp2 = api.getSatelliteTLE('25544')
resp3 = api.getSatelliteTLE('33752')

satellite_tle1 = resp1[0]['satname'] + '\n' + resp1[1]
satellite_tle2 = resp2[0]['satname'] + '\n' + resp2[1]
satellite_tle3 = resp3[0]['satname'] + '\n' + resp3[1]

tle_list = []

tle1 = orbit.createTLE(satellite_tle1)
tle_list.append(tle1)

tle2 = orbit.createTLE(satellite_tle2)
tle_list.append(tle2)

tle3 = orbit.createTLE(satellite_tle3)
tle_list.append(tle3)

# 22°50'00.9"S 47°02'14.8"W
tle2.infoPrint()
tle2.groundTrack(-22.833425, -47.037964)
tle2.drawOrbit()

orbit.drawMultiOrbits(tle_list)

input("\nPress enter to exit ;)")