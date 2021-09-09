from skyfield.api import load, Loader, EarthSatellite
from datetime import datetime, timedelta
import repository.twoLineElement as twoLineElement
import matplotlib.pyplot as plt
import numpy as np
import cartopy.crs as ccrs
import cartopy
import pytz
import warnings


warnings.filterwarnings("ignore")

##### DO NOT DELETE THIS!!!!! #####
from mpl_toolkits.mplot3d import Axes3D
##### ----------------------- #####

pdt = pytz.timezone('US/Pacific')

sqrt = np.sqrt
pi = np.pi
sin = np.sin
cos = np.cos

# radius in km
Earth_radius = 6371

# Standard Gravitational parameter in km^3 / s^2 of Earth
GM = 398600.4418

def makecubelimits(ax, centers=None, hw=None):

    lims = ax.get_xlim(), ax.get_ylim(), ax.get_zlim()
    if centers == None:
        centers = [0.5 * sum(pair) for pair in lims]

    if hw == None:
        widths = [pair[1] - pair[0] for pair in lims]
        hw = 0.5 * max(widths)
        ax.set_xlim(centers[0] - hw, centers[0] + hw)
        ax.set_ylim(centers[1] - hw, centers[1] + hw)
        ax.set_zlim(centers[2] - hw, centers[2] + hw)

    else:
        try:
            hwx, hwy, hwz = hw

            ax.set_xlim(centers[0] - hwx, centers[0] + hwx)
            ax.set_ylim(centers[1] - hwy, centers[1] + hwy)
            ax.set_zlim(centers[2] - hwz, centers[2] + hwz)
        except:
            ax.set_xlim(centers[0] - hw, centers[0] + hw)
            ax.set_ylim(centers[1] - hw, centers[1] + hw)
            ax.set_zlim(centers[2] - hw, centers[2] + hw)

    return centers, hw

def drawOrbit(tle):
    '''
    Using 'skyfield' for 'SGP4'
    For really big orbits, consider use 'drawMultiOrbits' instead.
    '''

    TLE = tle
    name, L1, L2 = TLE.splitlines()

    halfpi, pi, twopi = [f * np.pi for f in [0.5, 1, 2]]
    degs, rads = 180 / pi, pi / 180

    load = Loader('~/Documents/fishing/SkyData')
    data = load('de421.bsp')
    ts = load.timescale()

    planets = load('de421.bsp')

    Roadster = EarthSatellite(L1, L2)

    hours = np.arange(0, 3, 0.01)

    time = ts.utc(2018, 2, 7, hours)

    Rpos = Roadster.at(time).position.km

    re = 6378.

    theta = np.linspace(0, twopi, 201)
    cth, sth, zth = [f(theta) for f in [np.cos, np.sin, np.zeros_like]]
    lon0 = re * np.vstack((cth, zth, sth))
    lons = []
    for phi in rads * np.arange(0, 180, 15):
        cph, sph = [f(phi) for f in [np.cos, np.sin]]
        lon = np.vstack((lon0[0] * cph - lon0[1] * sph,
                         lon0[1] * cph + lon0[0] * sph,
                         lon0[2]))
        lons.append(lon)

    lat0 = re * np.vstack((cth, sth, zth))
    lats = []
    for phi in rads * np.arange(-75, 90, 15):
        cph, sph = [f(phi) for f in [np.cos, np.sin]]
        lat = re * np.vstack((cth * cph, sth * cph, zth + sph))
        lats.append(lat)

    fig = plt.figure(figsize=[10, 8])  # [12, 10]

    ax = fig.add_subplot(1, 1, 1, projection='3d')

    x, y, z = Rpos
    ax.plot(x, y, z)
    for x, y, z in lons:
        ax.plot(x, y, z, '-k')
    for x, y, z in lats:
        ax.plot(x, y, z, '-k')

    centers, hw = makecubelimits(ax)

    plt.show(block=False)

def drawMultiOrbits(tle_list):

    fig = plt.figure(figsize=plt.figaspect(1))  # Square figure
    ax = fig.add_subplot(111, projection='3d', aspect=1)
    ax.grid(False)
    plt.axis('off')

    ### Draw Earth as a globe at the origin
    global Earth_radius  # km
    max_radius = 0
    max_radius = max(max_radius, Earth_radius)

    # Coefficients in a0/c x**2 + a1/c y**2 + a2/c z**2 = 1
    coefs = (1, 1, 1)

    # Radii corresponding to the coefficients:
    rx, ry, rz = [Earth_radius / np.sqrt(coef) for coef in coefs]

    # Set of all spherical angles:
    u = np.linspace(0, 2 * np.pi, 100)
    v = np.linspace(0, np.pi, 100)

    # Cartesian coordinates that correspond to the spherical angles:
    # (this is the equation of an ellipsoid):
    x = rx * np.outer(np.cos(u), np.sin(v))
    y = ry * np.outer(np.sin(u), np.sin(v))
    z = rz * np.outer(np.ones_like(u), np.cos(v))

    # Plot:
    ax.plot_surface(x, y, z, rstride=4, cstride=4, color='b')

    for tle_index in tle_list:

        ### "Draws orbit around an earth in units of kilometers."
        # Rotation matrix for inclination
        inc = tle_index.inclination * pi / 180.;
        R = np.matrix([[1, 0, 0],
                       [0, cos(inc), -sin(inc)],
                       [0, sin(inc), cos(inc)]])

        # Rotation matrix for argument of perigee + right ascension
        rot = (tle_index.right_ascension + tle_index.argument_perigee) * pi / 180
        R2 = np.matrix([[cos(rot), -sin(rot), 0],
                        [sin(rot), cos(rot), 0],
                        [0, 0, 1]])

        ### Draw orbit
        theta = np.linspace(0, 2 * pi, 360)
        r = (tle_index.semi_major_axis * (1 - tle_index.eccentricity ** 2)) / (1 + tle_index.eccentricity * cos(theta))

        xr = r * cos(theta)
        yr = r * sin(theta)
        zr = 0 * theta

        pts = np.column_stack((xr, yr, zr))

        # Rotate by inclination
        # Rotate by ascension + perigee
        pts = (R * R2 * pts.T).T

        # Turn back into 1d vectors
        xr, yr, zr = pts[:, 0].A.flatten(), pts[:, 1].A.flatten(), pts[:, 2].A.flatten()

        # Plot the orbit
        ax.plot(xr, yr, zr, '-')
        plt.xlabel('X (km)')
        plt.ylabel('Y (km)')
        # plt.zlabel('Z (km)')

        # Plot the satellite
        sat_angle = tle_index.true_anomaly * pi / 180
        satr = (tle_index.semi_major_axis * (1 - tle_index.eccentricity ** 2)) / (1 + tle_index.eccentricity * cos(sat_angle))
        satx = satr * cos(sat_angle)
        saty = satr * sin(sat_angle)
        satz = 0

        sat = (R * R2 * np.matrix([satx, saty, satz]).T).flatten()
        satx = sat[0, 0]
        saty = sat[0, 1]
        satz = sat[0, 2]

        c = np.sqrt(satx * satx + saty * saty)
        lat = np.arctan2(satz, c) * 180 / pi
        lon = np.arctan2(saty, satx) * 180 / pi
        print("%s : Lat: %g° Long: %g" % (tle_index.name, lat, lon))

        # Draw radius vector from earth
        # ax.plot([0, satx], [0, saty], [0, satz], 'r-')
        # Draw red sphere for satellite
        ax.plot([satx], [saty], [satz], 'ro')

        max_radius = max(max(r), max_radius)

        # Write satellite name next to it
        if tle_index.name:
            ax.text(satx, saty, satz, tle_index.name, fontsize=12)

    for axis in 'xyz':
        getattr(ax, 'set_{}lim'.format(axis))((-max_radius, max_radius))

    # Draw figure
    print("----------------------------------------------------------------------------------------")
    plt.show(block=False)

def drawGroundTrack(tle, timestamp,  observer_lat=None, observer_lon=None):

    ts = load.timescale(builtin=True)

    name, L1, L2 = tle.splitlines()

    sat = EarthSatellite(L1, L2)

    date_object = datetime.fromtimestamp(timestamp)

    minutes = np.arange(0, 200, 0.1)  # about two orbits
    times = ts.utc(date_object.year, date_object.month, date_object.day, date_object.hour, minutes)

    geocentric = sat.at(times)
    subsat = geocentric.subpoint()

    fig = plt.figure(figsize=(20, 10))
    ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

    ax.stock_img()

    plt.scatter(subsat.longitude.degrees, subsat.latitude.degrees, transform=ccrs.PlateCarree(), s=1.5, color='red')

    ### Longitude and Latidude grid/labels
    ax = plt.axes(projection=ccrs.PlateCarree())
    ax.add_feature(cartopy.feature.COASTLINE)
    gridlines = ax.gridlines(draw_labels=True)

    ax.text(-0.07, 0.55, 'latitude', va='bottom', ha='center',
            rotation='vertical', rotation_mode='anchor',
            transform=ax.transAxes)

    ax.text(0.5, -0.2, 'longitude', va='bottom', ha='center',
            rotation='horizontal', rotation_mode='anchor',
            transform=ax.transAxes)

    ### Plot observer position on map
    if (observer_lat and observer_lon) != None:
        plt.plot(observer_lon, observer_lat,
                 color='blue', linewidth=2, marker='o',
                 transform=ccrs.Geodetic(),
                 )

        plt.text(observer_lon, observer_lat, 'You',
                 horizontalalignment='right',
                 transform=ccrs.Geodetic())

    plt.show(block=False)

def splitElem(tle):
    "Splits a two line element set into title and it's two lines with stripped lines"
    return map(lambda x: x.strip(), tle.split('\n'))

def checkValid(tle):
    "Checks with checksum to make sure element is valid"
    title, line1, line2 = splitElem(tle)

    return line1[0] == '1' and line2[0] == '2' and \
           line1[2:7] == line2[2:7] and \
           int(line1[-1]) == doChecksum(line1) and int(line2[-1]) == doChecksum(line2)

def stringScientificNotationToFloat(sn):
    "Specific format is 5 digits, a + or -, and 1 digit, ex: 01234-5 which is 0.01234e-5"
    return 0.00001 * float(sn[5]) * 10 ** int(sn[6:])

def eccentricAnomalyFromMean(mean_anomaly, eccentricity, initValue,maxIter=500, maxAccuracy=0.0001):
    """Approximates Eccentric Anomaly from Mean Anomaly
       All input and outputs are in radians"""
    mean_anomaly = mean_anomaly
    e0 = initValue
    for x in range(maxIter):
        e1 = e0 - (e0 - eccentricity * sin(e0) - mean_anomaly) / (1.0 - eccentricity * cos(e0))
        if abs(e1 - e0) < maxAccuracy:
            break
    return e1

def createTLE(sat_tle):


    title, line1, line2 = splitElem(sat_tle)

    if not checkValid(sat_tle):
        print("Invalid element.")
        return

    tle = twoLineElement.TLE()

    tle.raw = sat_tle
    tle.name = title
    tle.satellite_number = int(line1[2:7])
    tle.classification = line1[7:8]
    tle.international_designator_year = int(line1[9:11])
    tle.international_designator_launch_number = int(line1[11:14])
    tle.international_designator_piece_of_launch = line1[14:17]
    tle.epoch_year = int(line1[18:20])
    tle.epoch = float(line1[20:32])
    tle.first_time_derivative_of_the_mean_motion_divided_by_two = float(line1[33:43])
    tle.second_time_derivative_of_mean_motion_divided_by_six = stringScientificNotationToFloat(line1[44:52])
    tle.bstar_drag_term = stringScientificNotationToFloat(line1[53:61])
    tle.the_number_0 = float(line1[62:63])
    tle.element_number = float(line1[64:68])
    tle.checksum1 = float(line1[68:69])

    tle.satellite = int(line2[2:7])
    tle.inclination = float(line2[8:16])
    tle.right_ascension = float(line2[17:25])
    tle.eccentricity = float(line2[26:33]) * 0.0000001
    tle.argument_perigee = float(line2[34:42])
    tle.mean_anomaly = float(line2[43:51])
    tle.mean_motion = float(line2[52:63])
    tle.revolution = float(line2[63:68])
    tle.checksum2 = float(line2[68:69])

    # Inferred Epoch date
    year = 2000 + tle.epoch_year if tle.epoch_year < 70 else 1900 + tle.epoch_year
    tle.epoch_date = datetime(year=year, month=1, day=1, tzinfo=pytz.utc) + timedelta(
        days=tle.epoch - 1)  # Have to subtract one day to get correct midnight

    # Time difference of now from epoch, offset in radians
    diff = datetime.now().replace(tzinfo=pytz.utc) + timedelta(hours=8) - tle.epoch_date  # Offset for PDT
    diff_seconds = 24 * 60 * 60 * diff.days + diff.seconds + 1e-6 * diff.microseconds  # sec
    tle.motion_per_sec = tle.mean_motion * 2 * pi / (24 * 60 * 60)  # rad/sec
    offset = diff_seconds * tle.motion_per_sec  # rad
    tle.mean_anomaly += offset * 180 / pi % 360

    # Inferred period
    tle.day_seconds = 24 * 60 * 60
    period = tle.day_seconds * 1. / tle.mean_motion
    tle.period = timedelta(seconds=period)

    # Inferred semi-major axis (in km)
    tle.semi_major_axis = ((period / (2 * pi)) ** 2 * GM) ** (1. / 3)

    # Inferred true anomaly
    tle.eccentric_anomaly = eccentricAnomalyFromMean(tle.mean_anomaly * pi / 180, tle.eccentricity, tle.mean_anomaly * pi / 180)
    tle.true_anomaly = 2 * np.arctan2(sqrt(1 + tle.eccentricity) * sin(tle.eccentric_anomaly / 2.0),
                                  sqrt(1 - tle.eccentricity) * cos(tle.eccentric_anomaly / 2.0))
    # Convert to degrees
    tle.eccentric_anomaly *= 180 / pi
    tle.true_anomaly *= 180 / pi

    return tle

def doChecksum(line):
    """The checksums for each line are calculated by adding the all numerical digits on that line, including the
       line number. One is added to the checksum for each negative sign (-) on that line. All other non-digit
       characters are ignored.
       @note this excludes last char for the checksum thats already there."""
    return sum(map(int, filter(lambda c: c >= '0' and c <= '9', line[:-1].replace('-', '1')))) % 10