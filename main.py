import resources.api as api
import resources.orbit as orbit

resp = api.getSatelliteTLE('46235')

satellite_tle = resp[0]['satname'] + '\n' + resp[1]

tle = orbit.createTLE(satellite_tle)

tle.pretty_print()

orbit.drawOrbit(resp[1])