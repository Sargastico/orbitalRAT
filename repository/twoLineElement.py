class TLE:

    name= None
    raw = None
    tle = None
    title = None
    satellite_number = None
    classification = None
    international_designator_year = None
    international_designator_launch_number = None
    international_designator_piece_of_launch = None
    epoch_date = None
    second_time_derivative_of_mean_motion_divided_by_six = None
    bstar_drag_term = None
    the_number_0 = None
    element_number = None
    inclination = None
    right_ascension = None
    eccentricity = None
    argument_perigee = None
    mean_anomaly = None
    eccentric_anomaly = None
    true_anomaly = None
    mean_motion = None
    period = None
    revolution = None
    semi_major_axis = None
    epoch_year = None
    epoch = None
    first_time_derivative_of_the_mean_motion_divided_by_two = None

    def infoPrint(self):

        print("----------------------------------------------------------------------------------------")
        print(self.name)
        print(self.raw)
        print("----------------------------------------------------------------------------------------")
        print("Satellite number                                          = %g (%s)" % (self.satellite_number, "Unclassified" if self.classification == 'U' else "Classified"))
        print("International Designator                                  = YR: %02d, LAUNCH #%d, PIECE: %s" % (self.international_designator_year, self.international_designator_launch_number, self.international_designator_piece_of_launch))
        print("Epoch Date                                                = %s  (YR:%02d DAY:%.11g)" % (self.epoch_date.strftime("%Y-%m-%d %H:%M:%S.%f %Z"), self.epoch_year, self.epoch))
        print("First Time Derivative of the Mean Motion divided by two   = %g" % self.first_time_derivative_of_the_mean_motion_divided_by_two)
        print("Second Time Derivative of Mean Motion divided by six      = %g" % self.second_time_derivative_of_mean_motion_divided_by_six)
        print("BSTAR drag term                                           = %g" % self.bstar_drag_term)
        print("The number 0                                              = %g" % self.the_number_0)
        print("Element number                                            = %g" % self.element_number)
        print()
        print("Inclination [Degrees]                                     = %g°" % self.inclination)
        print("Right Ascension of the Ascending Node [Degrees]           = %g°" % self.right_ascension)
        print("Eccentricity                                              = %g" % self.eccentricity)
        print("Argument of Perigee [Degrees]                             = %g°" % self.argument_perigee)
        print("Mean Anomaly [Degrees] Anomaly                            = %g°" % self.mean_anomaly)
        print("Eccentric Anomaly                                         = %g°" % self.eccentric_anomaly)
        print("True Anomaly                                              = %g°" % self.true_anomaly)
        print("Mean Motion [Revs per day] Motion                         = %g" % self.mean_motion)
        print("Period                                                    = %s" % self.period)
        print("Revolution number at epoch [Revs]                         = %g" % self.revolution)
        print()
        print("semi_major_axis                                           = %gkm" % self.semi_major_axis)
        print("eccentricity                                              = %g" % self.eccentricity)
        print("inclination                                               = %g°" % self.inclination)
        print("arg_perigee                                               = %g°" % self.argument_perigee)
        print("right_ascension                                           = %g°" % self.right_ascension)
        print("true_anomaly                                              = %g°" % self.true_anomaly)
        print("----------------------------------------------------------------------------------------")