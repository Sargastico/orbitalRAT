import resources.api as api
import resources.orbit as orbit

# resp = api.getSatelliteTLE('46235')
resp = api.getSatelliteTLE('25544')

satellite_tle = resp[0]['satname'] + '\n' + resp[1]

tle = orbit.createTLE(satellite_tle)

tle.infoPrint()

orbit.drawOrbit(resp[1])
orbit.drawGroundTrack(satellite_tle)

input("\nPress enter to exit ;)")