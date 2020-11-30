from datetime import datetime, timedelta
import repository.twoLineElement as twoLineElement
import numpy as np
import pytz
import warnings
import builtins

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

def calcOrbitEllipse(tle):

    ### "Draws orbit around an earth in units of kilometers."
    # Rotation matrix for inclination
    inc = tle.inclination * pi / 180.;
    R = np.matrix([[1, 0, 0],
                   [0, cos(inc), -sin(inc)],
                   [0, sin(inc), cos(inc)]])

    # Rotation matrix for argument of perigee + right ascension
    rot = (tle.right_ascension + tle.argument_perigee) * pi / 180
    R2 = np.matrix([[cos(rot), -sin(rot), 0],
                    [sin(rot), cos(rot), 0],
                    [0, 0, 1]])

    ### Draw orbit
    theta = np.linspace(0, 2 * pi, 360)
    r = (tle.semi_major_axis * (1 - tle.eccentricity ** 2)) / (1 + tle.eccentricity * cos(theta))

    xr = r * cos(theta)
    yr = r * sin(theta)
    zr = 0 * theta

    pts = np.column_stack((xr, yr, zr))

    # Rotate by inclination
    # Rotate by ascension + perigee
    pts = (R * R2 * pts.T).T

    # Turn back into 1d vectors
    xr, yr, zr = pts[:, 0].A.flatten(), pts[:, 1].A.flatten(), pts[:, 2].A.flatten()

    # Plot the satellite
    sat_angle = tle.true_anomaly * pi / 180
    satr = (tle.semi_major_axis * (1 - tle.eccentricity ** 2)) / (1 + tle.eccentricity * cos(sat_angle))
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
    print("%s : Lat: %g° Long: %g" % (tle.name, lat, lon))

    return xr, yr, zr, satx, saty, satz

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
