import pytz
from skyfield.api import load, Loader, EarthSatellite
import cartopy.crs as ccrs
import matplotlib.pyplot as plt
import cartopy
import sys
import numpy as np
import warnings
from datetime import datetime
from resources import orbit as orbit

api = ''

if api == 'pyqtgraph':
    from PyQt5 import QtWidgets
    from pyqtgraph.Qt import QtCore, QtGui
    import pyqtgraph.opengl as gl

warnings.filterwarnings("ignore")

##### DO NOT DELETE THIS!!!!! #####
from mpl_toolkits.mplot3d import Axes3D
##### ----------------------- #####

pdt = pytz.timezone('US/Pacific')

Earth_radius = 6371
sqrt = np.sqrt
pi = np.pi
sin = np.sin
cos = np.cos

class GLVisualizer(object):


    tle = None

    def __init__(self, tle):

        """
          Initialize the graphics window and mesh
        """
        self.app = QtGui.QApplication(sys.argv)
        self.w = gl.GLViewWidget()
        self.w.setGeometry(0, 110, 1920, 1080)
        self.w.show()
        self.w.setWindowTitle('Orbit')
        self.w.setCameraPosition(distance=(Earth_radius + 50000), elevation=8)
        self.tle = tle

    def drawEarth(self):

        md = gl.MeshData.sphere(rows=20, cols=20, radius=Earth_radius)

        m1 = gl.GLMeshItem(
            meshdata=md,
            smooth=True,
            color=(0, 0, 120, 1),
            shader="balloon",
            drawEdges=False,
            glOptions="additive",
        )

        self.w.addItem(m1)

    def drawSatOrbit(self):

        xr, yr, zr, satx, saty, satz = orbit.calcOrbitEllipse(self.tle)

        for i in range(360):
            orbitPoints = (xr[i], yr[i], zr[i])
            drawPositions = np.array([orbitPoints])

            sh1 = gl.GLScatterPlotItem(pos=drawPositions, size=5, color=(255, 0, 0, 1))
            self.w.addItem(sh1)

    def start(self):

        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()

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

    plt.show(block=False)

def drawGroundTrack(tle, timestamp, observer_lat=None, observer_lon=None):

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

def drawMultiOrbits(tle_list):

    global Earth_radius  # km
    max_radius = 0
    max_radius = max(max_radius, Earth_radius)

    fig = plt.figure(figsize=plt.figaspect(1))
    ax = fig.add_subplot(111, projection='3d', aspect=1)
    ax.grid(False)
    plt.axis('off')
    plt.ion()

    # Set of all spherical angles:
    u = np.linspace(0, 2 * np.pi, 100)
    v = np.linspace(0, np.pi, 100)

    # Coefficients in a0/c x**2 + a1/c y**2 + a2/c z**2 = 1
    coefs = (1, 1, 1)

    # Radii corresponding to the coefficients:
    rx, ry, rz = [Earth_radius / np.sqrt(coef) for coef in coefs]

    # Cartesian coordinates that correspond to the spherical angles:
    # (this is the equation of an ellipsoid):
    x = rx * np.outer(np.cos(u), np.sin(v))
    y = ry * np.outer(np.sin(u), np.sin(v))
    z = rz * np.outer(np.ones_like(u), np.cos(v))

    # Plot:
    ax.plot_surface(x, y, z, rstride=4, cstride=4, color='b')

    for tle_index in tle_list:

        theta = np.linspace(0, 2 * pi, 360)
        r = (tle_index.semi_major_axis * (1 - tle_index.eccentricity ** 2)) / (
                1 + tle_index.eccentricity * cos(theta))

        xr, yr, zr, satx, saty, satz = orbit.calcOrbitEllipse(tle_index)

        # Plot the orbit
        ax.plot(xr, yr, zr, '-')
        plt.xlabel('X (km)')
        plt.ylabel('Y (km)')

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