from mathutils import *
from plotutils import *

def blade_upd_scan_data():
    blade._extra_scan_data()

class BLADECLASS():

    sig2fwmh=2.355
    diode1=[]
    diode2=[]
    diode3=[]
    diode4=[]
    diode_sum=[]
    tfy=[]

    def _extra_scan_data(self):
        self.diode1.append(Diode_1.take())
        self.diode2.append(Diode_2.take())
        self.diode3.append(Diode_3.take())
        self.diode4.append(Diode_4.take())
        self.diode_sum.append(Diode_sum.take())
        self.tfy.append(TFY.take())

    def Diagnostic_Chamber_Blade_Scan(self, start, end, steps, time_meas=0.0):
        print("Running ...")
        self.__setup_file(fname="blade_diag")
        self.__reset_extra_data()
        self.__setup_caenels2(Exp_Time=0.5, Enable=True)
        res = lscan(Filter1, Diode_sum, start, end, steps, time_meas, after_read=blade_upd_scan_data)
        #res = lscan(Filter2, Filter2_SIG, start, end, steps, interval, after_read=blade_upd_scan_data)
        xdata = res.getPositions(0)
        ydata = res.getReadable(0)
        dt = deriv(ydata, xdata=xdata)
        #flips orientation of derivative if necessary to be compatible with pshell gauss fit function
        if mean(dt)<0:
            dt = [-i for i in dt]
        print("Analysing...")
        (off, amp, com, sigma, gauss, fwhm) = self.__gauss_fit(dt, xdata)
        self.__print_info(off, amp, com, sigma, fwhm)
        self.__save_data(off, amp, com, sigma, fwhm, gauss, dt)
        pink_save_bl_snapshot()
        self.__plot_curves(xdata, ydata, dt, gauss, label="Blade Scan Diagnostic Chamber")
        print("OK")

    def Sample_Env_Blade_Scan(self, start, end, steps, time_meas=0.0):
        print("Running ...")
        self.__setup_file(fname="blade_sample")
        self.__reset_extra_data()
        self.__setup_caenels1(Exp_Time=0.5, Enable=True)
        #res = lscan(Filter2, Filter2_SIG, start, end, steps, interval, after_read=blade_upd_scan_data)
        res = lscan(SEC_el_y, TFY, start, end, steps, time_meas, after_read=blade_upd_scan_data)
        xdata = res.getPositions(0)
        ydata = res.getReadable(0)
        dt = deriv(ydata, xdata=xdata)
        #flips orientation of derivative if necessary to be compatible with pshell gauss fit function
        if mean(dt)<0:
            dt = [-i for i in dt]
        print("Analysing...")
        (off, amp, com, sigma, gauss, fwhm) = self.__gauss_fit(dt, xdata)
        self.__print_info(off, amp, com, sigma, fwhm)
        self.__save_data(off, amp, com, sigma, fwhm, gauss, dt)
        pink_save_bl_snapshot()
        self.__plot_curves(xdata, ydata, dt, gauss, label="Blade Scan Sample Env. Chamber")
        print("OK")

    def __gauss_fit(self, dt, xdata):
        (off, amp, com, sigma) = fit_gaussian_offset(dt, xdata)
        f = Gaussian(amp, com, sigma)
        gauss = [f.value(i)+off for i in xdata]
        fwhm = self.sig2fwmh*sigma
        return (off, amp, com, sigma, gauss, fwhm)

    def __print_info(self, off, amp, com, sigma, fwhm):
        print("*** Gaussian fit ***")
        print("Offset: " + '{:.3e}'.format(off) + "\tAmplitude: " + '{:.3e}'.format(amp))
        print("Mean:   " + '{:.3f}'.format(com) + "\tSigma:     " + '{:.3f}'.format(sigma) + "\tFWHM: " + '{:.3f}'.format(fwhm))

    def __save_data(self, off, amp, com, sigma, fwhm, gauss, dt):
        save_dataset("gaussian/offset", off)
        save_dataset("gaussian/amplitude", amp)
        save_dataset("gaussian/mean", com)
        save_dataset("gaussian/sigma", sigma)
        save_dataset("gaussian/FWHM", fwhm)
        save_dataset("plot/gauss_fit", gauss)
        save_dataset("plot/derivative", dt)
        save_dataset("diodes/diode1", self.diode1)
        save_dataset("diodes/diode2", self.diode2)
        save_dataset("diodes/diode3", self.diode3)
        save_dataset("diodes/diode4", self.diode4)
        save_dataset("diodes/diode_sum", self.diode_sum)
        save_dataset("diodes/TFY", self.tfy)

    def __reset_extra_data(self):
        self.diode1 = []
        self.diode2 = []
        self.diode3 = []
        self.diode4 = []
        self.diode_sum = []
        self.tfy = []

    def __plot_curves(self, xdata, ydata, dt, gauss, label="Scan"):
        [p1, p2]=plot([None, None], [label,"Analysis"], title="Blade Scan")
        p2.addSeries(LinePlotSeries("Fit"))
        p1.getSeries(0).setData(xdata, ydata)
        p2.getSeries(0).setData(xdata, dt)
        p2.getSeries(1).setData(xdata, gauss)

    def __setup_file(self, fname="blade_scan"):
        set_exec_pars(open=False, name=fname, reset=True)


    def __setup_caenels1(self, Exp_Time=0.5, Enable=True):
        cae_exp_time=float(Exp_Time)
        caputq("PINK:CAE1:Acquire", 0)
        caput("PINK:CAE1:ValuesPerRead", int(1000*cae_exp_time))
        caput("PINK:CAE1:AveragingTime", float(cae_exp_time))
        caput("PINK:CAE1:TriggerMode", 0)
        if Enable:
            caputq("PINK:CAE1:Acquire", 1)
        else:
            caputq("PINK:CAE1:Acquire", 0)

    def __setup_caenels2(self, Exp_Time=0.5, Enable=True):
        cae_exp_time=float(Exp_Time)
        caputq("PINK:CAE2:Acquire", 0)
        caput("PINK:CAE2:ValuesPerRead", int(1000*cae_exp_time))
        caput("PINK:CAE2:AveragingTime", float(cae_exp_time))
        caput("PINK:CAE2:TriggerMode", 0)
        if Enable:
            caputq("PINK:CAE2:Acquire", 1)
        else:
            caputq("PINK:CAE2:Acquire", 0)
