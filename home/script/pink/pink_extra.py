## PINK Extra functions
#from __future__ import division

def myfit_gaussian_exp_bkg(y, x, start_point = None, weights = None):
    """Fits data into a gaussian with exponential background.
       f(x) = a * math.exp(-(x/b)) + c * exp(-(pow((x - d), 2) / (2 * pow(e, 2))))

    Args:
        x(float array or list): observed points x
        y(float array or list): observed points y
        start_point(optional tuple of float): initial parameters (normalization, mean, sigma)
        weights(optional float array or list): weight for each observed point
    Returns:
        Tuples of gaussian parameters: (offset, normalization, mean, sigma)
    """

    # For normalised gauss curve sigma=1/(amp*sqrt(2*pi))
    if start_point is None:
        off = min(y)  # good enough starting point for offset
        com = x[len(x)/2]
        #com = 11.9
        amp = max(y) - off
        sigma = trapz([v-off for v in y], x) / (amp*math.sqrt(2*math.pi))
        start_point = [1, 1, amp, com, sigma]

    class Model(MultivariateJacobianFunction):
        def value(self, variables):
            value = ArrayRealVector(len(x))
            jacobian = Array2DRowRealMatrix(len(x), 5)
            for i in range(len(x)):
                (a,b,c,d,e) = (variables.getEntry(0), variables.getEntry(1), variables.getEntry(2), variables.getEntry(3), variables.getEntry(4))
                v = math.exp(-(math.pow((x[i] - d), 2) / (2 * math.pow(e, 2))))
                bkg=math.exp(-(x[i]/b))
                model = a*bkg + c * v
                value.setEntry(i, model)
                jacobian.setEntry(i, 0, bkg)               # derivative with respect to p0 = a
                jacobian.setEntry(i, 1, a*x[i]*bkg/math.pow(b, 2))    # derivative with respect to p1 = b
                jacobian.setEntry(i, 2, v)                  # derivative with respect to p2 = c
                v2 = c*v*((x[i] - d)/math.pow(e, 2))
                jacobian.setEntry(i, 3, v2)                 # derivative with respect to p3 = d
                jacobian.setEntry(i, 4, v2*(x[i] - d)/e )   # derivative with respect to p4 = e
            return Pair(value, jacobian)

    model = Model()
    target = [v for v in y]      #the target is to have all points at the positios
    (parameters, residuals, rms, evals, iters) = optimize_least_squares(model, target, start_point, weights)
    return parameters

def pink_save_bl_snapshot():
    pvlist = [
    ["beamline/ring_current", "MDIZ3T5G:current"],
    ["beamline/U17_Gap", "U17IT6R:BasePmGap.A"],
    ["beamline/AU1_Top", "WAUY02U012L:rdPosM1"],
    ["beamline/AU1_Bottom", "WAUY02U012L:rdPosM2"],
    ["beamline/AU1_Wall", "WAUY02U012L:rdPosM3"],
    ["beamline/AU1_Ring", "WAUY02U012L:rdPosM4"],
    ["beamline/M1_Tx", "U17_M1:rdTx"],
    ["beamline/M1_Ty", "U17_M1:rdTy"],
    ["beamline/M1_Rx", "U17_M1:rdRx"],
    ["beamline/M1_Ry", "U17_M1:rdRy"],
    ["beamline/M1_Rz", "U17_M1:rdRz"],
    ["beamline/Diamond_Hor", "u171dcm1:PH_1_GET"],
    ["beamline/Diamond_Vert", "u171dcm1:PH_2_GET"],
    ["beamline/AU2_Top", "u171pgm1:PH_2_GET"],
    ["beamline/AU2_Bottom", "u171pgm1:PH_3_GET"],
    ["beamline/AU2_Right", "u171pgm1:PH_5_GET"],
    ["beamline/AU2_Left", "u171pgm1:PH_4_GET"],
    ["beamline/AU3_Top", "AUY01U112L:rdPosM1"],
    ["beamline/AU3_Bottom", "AUY01U112L:rdPosM2"],
    ["beamline/AU3_Right", "AUY01U112L:rdPosM4"],
    ["beamline/AU3_Left", "AUY01U112L:rdPosM3"],
    ["beamline/M2_Tx", "HEX2OS12L:hexapod:getReadPoseX"],
    ["beamline/M2_Ty", "HEX2OS12L:hexapod:getReadPoseY"],
    ["beamline/M2_Tz", "HEX2OS12L:hexapod:getReadPoseZ"],
    ["beamline/M2_Rx", "HEX2OS12L:hexapod:getReadPoseA"],
    ["beamline/M2_Ry", "HEX2OS12L:hexapod:getReadPoseB"],
    ["beamline/M2_Rz", "HEX2OS12L:hexapod:getReadPoseC"],
    ["station/Table_Tx", "PINK:TBL:pinkX"],
    ["station/Table_Ty", "PINK:TBL:pinkY"],
    ["station/Table_Rx", "PINK:TBL.EAX"],
    ["station/Table_Ry", "PINK:TBL.EAY"],
    ["station/Table_Rz", "PINK:TBL.EAZ"],
    ["station/Table_Sx", "PINK:TBL:pinkSX"],
    ["station/Table_Sy", "PINK:TBL:pinkSY"],
    ["station/Table_Sz", "PINK:TBL:pinkSZ"],
    ["station/Slits_Top", "PINK:PHY:AxisF.RBV"],
    ["station/Slits_Bottom", "PINK:PHY:AxisG.RBV"],
    ["station/Slits_Right", "PINK:PHY:AxisI.RBV"],
    ["station/Slits_Left", "PINK:PHY:AxisH.RBV"],
    ["station/Filter1", "PINK:SMA01:m0.RBV"],
    ["station/Filter2", "PINK:SMA01:m1.RBV"],
    ["station/Filter3", "PINK:SMA01:m2.RBV"],
    ["station/Diodes_Vert", "PINK:SMA01:m3.RBV"],
    ["station/Diodes_Hor", "PINK:SMA01:m4.RBV"],
    ["station/Filter1_offset", "PINK:SMA01:m0.OFF"],
    ["station/Filter2_offset", "PINK:SMA01:m1.OFF"],
    ["station/Filter3_offset", "PINK:SMA01:m2.OFF"],
    ["station/Diodes_Vert_offset", "PINK:SMA01:m3.OFF"],
    ["station/Diodes_Hor_offset", "PINK:SMA01:m4.OFF"],
    ["station/Scatter", "PINK:SMA01:m5.RBV"],
    ["station/Scatter_offset", "PINK:SMA01:m5.OFF"],
    ["station/VH2_crystal_yaw", "PINK:SMA01:m6.RBV"],
    ["station/VH2_crystal_roll", "PINK:SMA01:m7.RBV"],
    ["station/VH2_blade_top", "PINK:SMA01:m8.RBV"],
    ["station/VH2_crystal_linear", "PINK:PHY:AxisN.RBV"],
    ["station/Spec_atm_hor", "PINK:PHY:AxisK.RBV"],
    ["station/Spec_atm_vert", "PINK:PHY:AxisL.RBV"],
    ["station/Spec_atm_angle", "PINK:PHY:AxisM.RBV"],
    ["station/Sample_env_cryo_vti", "PINK:LKS:KRDG0"],
    ["station/Sample_env_cryo_head", "PINK:LKS:KRDG1"],
    ["station/Sample_env_cryo_cu", "PINK:LKS:KRDG2"],
    ["station/Sample_env_cryo_holder", "PINK:LKS:KRDG3"],
    ["station/Sample_env_cryo_int_press", "PINK:MAXC:S1Measure"],
    ["station/Sample_env_cryo_vac_press", "PINK:MAXB:S5Measure"],
    ["station/Sample_env_press", "PINK:MAXB:S3Measure"],
    ]
    for dat in pvlist:
        try:
            pval = caget(dat[1])
        except:
            print("PV is unreachable: " + dat[1])
            pval = 0
        save_dataset(dat[0], pval)


# ******** Pseudo Devices ************

class Array2Matrix(ReadonlyRegisterBase, ReadonlyRegisterMatrix):
    def __init__(self, name, src_array, src_width, src_height):
        ReadonlyRegisterBase.__init__(self, name)
        self.src_array = src_array
        self.src_width = src_width
        self.src_height = src_height

    def doRead(self):
        data = self.src_array.take()
        h = self.getHeight()
        w = self.getWidth()
        ret = Convert.reshape(data, h, w)
        return ret

    def getWidth(self):
        return int(self.src_width.take())

    def getHeight(self):
        return int(self.src_height.take())

add_device(Array2Matrix("GE_BG_Image", GE_BG_Array, GE_BG_SizeX, GE_BG_SizeY), True)
add_device(Array2Matrix("GE_ROI_Image", GE_ROI_Array, GE_ROI_SizeX, GE_ROI_SizeY), True)
add_device(Array2Matrix("GE_Raw_Image", GE_Raw_Array, GE_BG_SizeX, GE_BG_SizeY), True)

sleep(1)

GE_BG_Image.read()
GE_ROI_Image.read()
GE_Raw_Image.read()


