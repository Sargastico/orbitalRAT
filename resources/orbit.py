from skyfield.api import Loader, EarthSatellite
import matplotlib.pyplot as plt
import numpy as np
import repository.twoLineElement as twoLineElement
from datetime import datetime, timedelta
from mpl_toolkits.mplot3d import Axes3D # DO NOT DELETE THIS!!!!!
import pytz

pdt = pytz.timezone('US/Pacific')

sqrt = np.sqrt
pi = np.pi
sin = np.sin
cos = np.cos

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
        print("hw was None so set to:", hw)
    else:
        try:
            hwx, hwy, hwz = hw
            print("ok hw requested: ", hwx, hwy, hwz)

            ax.set_xlim(centers[0] - hwx, centers[0] + hwx)
            ax.set_ylim(centers[1] - hwy, centers[1] + hwy)
            ax.set_zlim(centers[2] - hwz, centers[2] + hwz)
        except:
            print("nope hw requested: ", hw)
            ax.set_xlim(centers[0] - hw, centers[0] + hw)
            ax.set_ylim(centers[1] - hw, centers[1] + hw)
            ax.set_zlim(centers[2] - hw, centers[2] + hw)

    return centers, hw


def drawOrbit(tle):

    TLE = tle
    L1, L2 = TLE.splitlines()

    halfpi, pi, twopi = [f * np.pi for f in [0.5, 1, 2]]
    degs, rads = 180 / pi, pi / 180

    load = Loader('~/Documents/fishing/SkyData')
    data = load('de421.bsp')
    ts = load.timescale()

    planets = load('de421.bsp')
    earth = planets['earth']

    Roadster = EarthSatellite(L1, L2)

    print(Roadster.epoch.tt)
    hours = np.arange(0, 3, 0.01)

    time = ts.utc(2018, 2, 7, hours)

    Rpos = Roadster.at(time).position.km

    print(Rpos.shape)

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

    print("centers are: ", centers)
    print("hw is:       ", hw)

    plt.show()

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


def eccentricAnomalyFromMean(mean_anomaly, eccentricity, initValue,
                             maxIter=500, maxAccuracy=0.0001):
    """Approximates Eccentric Anomaly from Mean Anomaly
       All input and outputs are in radians"""
    mean_anomaly = mean_anomaly
    e0 = initValue
    for x in range(maxIter):
        e1 = e0 - (e0 - eccentricity * sin(e0) - mean_anomaly) / (1.0 - eccentricity * cos(e0))
        if abs(e1 - e0) < maxAccuracy:
            break
    return e1


def createTLE(tle):


    title, line1, line2 = splitElem(tle)

    if not checkValid(tle):
        print("Invalid element.")
        return

    tle = twoLineElement.TLE()

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
    print("Time offset: %s" % diff)
    tle.motion_per_sec = tle.mean_motion * 2 * pi / (24 * 60 * 60)  # rad/sec
    print("Radians per second: %g" % tle.motion_per_sec)
    offset = diff_seconds * tle.motion_per_sec  # rad
    print("Offset to apply: %g" % offset)
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

