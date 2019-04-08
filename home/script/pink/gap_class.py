from mathutils import *
from plotutils import *

def gap_upd_scan_data():
    gap._extra_scan_data()

class GAPCLASS():

    sig2fwmh=2.355
    diode1=[]
    diode2=[]
    diode3=[]
    diode4=[]
    diode_sum=[]


    def Scan_without_fitting(self, start, end, step, wait=0):
        def BeforeReadout():
            prec=0.005
            lwait=1
            #caput("PINK:AUX1:U17_exec.PROC",1)
            caput("U17IT6R:BaseCmdCalc.PROC", 1)
            while(lwait):
                #err=abs(U17_GAP_SIM.take()-U17_SET_SIM.take())
                err=abs(U17_Gap_RBV.take()- U17_Gap_Set.take())
                if (err<=prec) & (U17_Gap_Status.take()==1):
                    lwait=0
                sleep(0.25)
            sleep(wait)

        if self.__undulator_locked():
            print("Undulator U17 is locked!")
            return

        print("Running undulator gap scan with linear background analysis...")
        self.__setup_file(fname="gap")
        self.__reset_extra_data()
        #res = lscan(U17_SET_SIM, [DSUM_SIM, U17_GAP_SIM], start, end, step, enabled_plots=[DSUM_SIM], before_read=BeforeReadout, after_read=gap_upd_scan_data)
        res = lscan(U17_Gap_Set, [Diode_sum, U17_Gap_RBV], start, end, step, enabled_plots=[Diode_sum], before_read=BeforeReadout, after_read=gap_upd_scan_data)
        pink_save_bl_snapshot()
        print("OK")

    def Scan_with_Linear_Background(self, start, end, step, wait=0):
        def BeforeReadout():
            prec=0.005
            lwait=1
            #caput("PINK:AUX1:U17_exec.PROC",1)
            caput("U17IT6R:BaseCmdCalc.PROC", 1)
            while(lwait):
                #err=abs(U17_GAP_SIM.take()-U17_SET_SIM.take())
                err=abs(U17_Gap_RBV.take()- U17_Gap_Set.take())
                if (err<=prec) & (U17_Gap_Status.take()==1):
                    lwait=0
                sleep(0.25)
            sleep(wait)
        if self.__undulator_locked():
            print("Undulator U17 is locked!")
            return

        print("Running undulator gap scan with linear background analysis...")
        self.__setup_file(fname="gap")
        self.__reset_extra_data()
        #res = lscan(U17_SET_SIM, [DSUM_SIM, U17_GAP_SIM], start, end, step, enabled_plots=[DSUM_SIM], before_read=BeforeReadout, after_read=gap_upd_scan_data)
        res = lscan(U17_Gap_Set, [Diode_sum, U17_Gap_RBV], start, end, step, enabled_plots=[Diode_sum], before_read=BeforeReadout, after_read=gap_upd_scan_data)
        #xdata = res.getPositions(0)
        xdata = res.getReadable(1)
        ydata = res.getReadable(0)
        #xdat = [i/1000 for i in xdata]
        print("Analysing...")
        (incl, off, amp, com, sigma, gauss, fwhm) = self.__gauss_lin_fit(ydata, xdata)
        self.__print_lin_info(incl, off, amp, com, sigma, fwhm)
        self.__plot_curves(xdata, ydata, gauss, title="Gap Scan with linear background")
        self.__save_data_lin(incl, off, amp, com, sigma, fwhm, gauss)
        pink_save_bl_snapshot()
        print("OK")


    def Scan_with_Exponential_Background(self, start, end, step, wait=0):
        def BeforeReadout():
            prec=0.005
            lwait=1
            #caput("PINK:AUX1:U17_exec.PROC",1)
            caput("U17IT6R:BaseCmdCalc.PROC", 1)
            g0 = abs(U17_Gap_RBV.take())
            WDog = 0
            while(lwait):
                #err=abs(U17_GAP_SIM.take()-U17_SET_SIM.take())
                err=abs(U17_Gap_RBV.take()- U17_Gap_Set.take())
                #dgap =
                if (err<=prec) & (U17_Gap_Status.take()==1):
                    lwait=0
                sleep(0.25)
                WDog = WDog+1
                if (WDog%8==0):
                    print("Undulator seems to be not moving after 2 seconds")
            sleep(wait)
        if self.__undulator_locked():
            print("Undulator U17 is locked!")
            return

        print("Running undulator gap scan with exponential background analysis...")
        self.__setup_file(fname="gap")
        self.__reset_extra_data()
        #res = lscan(U17_SET_SIM, [DSUM_SIM, U17_GAP_SIM], start, end, step, enabled_plots=[DSUM_SIM],before_read=BeforeReadout, after_read=gap_upd_scan_data)
        res = lscan(U17_Gap_Set, [Diode_sum, U17_Gap_RBV], start, end, step, enabled_plots=[Diode_sum], before_read=BeforeReadout, after_read=gap_upd_scan_data)
        #xdata = res.getPositions(0)
        xdata = res.getReadable(1)
        ydata = res.getReadable(0)
        self.xdata = xdata
        self.ydata = ydata
        #xdat = [i/1000 for i in xdata]
        print("Analysing...")
        (eamp, decay, amp, com, sigma, gauss, fwhm) = self.__gauss_exp_fit(ydata, xdata)
        self.__print_exp_info(eamp, decay, amp, com, sigma, fwhm)
        self.__plot_curves(xdata, ydata, gauss, title="Gap scan with exponential background")
        self.__save_data_exp(eamp, decay, amp, com, sigma, fwhm, gauss)
        pink_save_bl_snapshot()
        print("OK")

    def __gauss_lin_fit(self, ydata, xdata):
        (incl, off, amp, com, sigma) = fit_gaussian_linear(ydata, xdata)
        f = Gaussian(amp, com, sigma)
        gauss = [f.value(i) + incl*i+off for i in xdata]
        fwhm = self.sig2fwmh*sigma
        return (incl, off, amp, com, sigma, gauss, fwhm)

    def __gauss_exp_fit(self, ydata, xdata):
        (incl, off, amp, com, sigma) = fit_gaussian_linear(ydata, xdata)
        start_point=[1, 1, amp, com, sigma]
        (eamp, decay, amp, com, sigma) = fit_gaussian_exp_bkg(ydata, xdata, start_point=start_point)
        f = Gaussian(amp, com, sigma)
        gauss = [f.value(i) + eamp*math.exp(-i/decay) for i in xdata]
        fwhm = self.sig2fwmh*sigma
        return (eamp, decay, amp, com, sigma, gauss, fwhm)

    def __print_lin_info(self, incl, off, amp, com, sigma, fwhm):
        print("*** Gaussian fit with linear background ***")
        print("Inclination: " + '{:.3e}'.format(incl) + "\tOffset: " + '{:.3e}'.format(off))
        print("  Amplitude: " + '{:.3e}'.format(amp)  + "\t  Mean: " + '{:.3f}'.format(com))
        print("      Sigma: " + '{:.3f}'.format(sigma)+ "\t  FWHM: " + '{:.3f}'.format(fwhm))

    def __print_exp_info(self, eamp, decay, amp, com, sigma, fwhm):
        print("*** Gaussian fit with exponential background ***")
        print("BG Amplitude: " + '{:.3e}'.format(eamp) + "\tDecay: " + '{:.3e}'.format(decay))
        print("   Amplitude: " + '{:.3e}'.format(amp)  + "\t Mean: " + '{:.3f}'.format(com))
        print("       Sigma: " + '{:.3f}'.format(sigma)+ "\t FWHM: " + '{:.3f}'.format(fwhm))

    def __plot_curves(self, xdata, ydata, gauss, title="myplot"):
        p1=plot(None, "Diodes", title="Gap Scan")[0]
        p1.setLegendVisible(True)
        p1.setTitle(title)
        p1.addSeries(LinePlotSeries("Fit"))
        p1.getSeries(0).setData(xdata, ydata)
        p1.getSeries(1).setData(xdata, gauss)

    def __setup_file(self, fname="gap_scan"):
        set_exec_pars(open=False, name=fname, reset=True)

    def __reset_extra_data(self):
        self.diode1 = []
        self.diode2 = []
        self.diode3 = []
        self.diode4 = []
        self.diode_sum = []

    def _extra_scan_data(self):
        self.diode1.append(Diode_1.take())
        self.diode2.append(Diode_2.take())
        self.diode3.append(Diode_3.take())
        self.diode4.append(Diode_4.take())
        self.diode_sum.append(Diode_sum.take())
        #self.diode_sum.append(Diode4Sum.take())

    def __save_data_lin(self, incl, off, amp, com, sigma, fwhm, gauss):
        save_dataset("gaussian/inclination", incl)
        save_dataset("gaussian/offset", off)
        save_dataset("gaussian/amplitude", amp)
        save_dataset("gaussian/mean", com)
        save_dataset("gaussian/sigma", sigma)
        save_dataset("gaussian/FWHM", fwhm)
        save_dataset("gaussian/gauss_fit", gauss)
        save_dataset("diodes/diode1", self.diode1)
        save_dataset("diodes/diode2", self.diode2)
        save_dataset("diodes/diode3", self.diode3)
        save_dataset("diodes/diode4", self.diode4)
        save_dataset("diodes/diode_sum", self.diode_sum)

    def __save_data_exp(self, eamp, decay, amp, com, sigma, fwhm, gauss):
        save_dataset("gaussian/bg_amplitude", eamp)
        save_dataset("gaussian/decay", decay)
        save_dataset("gaussian/amplitude", amp)
        save_dataset("gaussian/mean", com)
        save_dataset("gaussian/sigma", sigma)
        save_dataset("gaussian/FWHM", fwhm)
        save_dataset("gaussian/gauss_fit", gauss)
        save_dataset("diodes/diode1", self.diode1)
        save_dataset("diodes/diode2", self.diode2)
        save_dataset("diodes/diode3", self.diode3)
        save_dataset("diodes/diode4", self.diode4)
        save_dataset("diodes/diode_sum", self.diode_sum)

    def __undulator_locked(self):
        #Wake up U17 Gap monitor
        junk = U17_Gap_RBV.read()
        stat=caget("U17IT6R:BaseCmdHmLock")
        if stat==0:
            return 0
        else:
            return 1
