def gap_upd_scan_data():
    scan._extra_scan_data()

def blade_upd_scan_data():
    scan._extra_scan_data()

class PSCANS():
    ####################################################################################
    #### Internal variables ############################################################
    ####################################################################################
    ge_start_frame=0
    ge_Num_Images=1
    ge_Num_Images_total=1
    line_images = 1
    scan_images = 1
    total_images = 1
    DEBUG=0
    DEBUGLOG=1
    ge_exptime=0
    ge_init_time=0
    sample=" "
    x0_mdata = []
    y0_mdata = []
    x1_mdata = []
    y1_mdata = []
    x_mdata =[]
    y_mdata =[]
    cont_speed = 0
    data_compression = {
        "compression":"True",
        "shuffle":"True"}
    ge_bg_spectra = []

    pressure_pvlist = [
        ["GP9","PINK:DGION:Pressure"],
        ["G01","PINK:MAXB:S6Measure"],
        ["G02","PINK:MAXA:S3Measure"],
        ["G03","PINK:MAXA:S2Measure"],
        ["G04","PINK:MAXB:S3Measure"],
        ["G05","PINK:MAXB:S4Measure"],
        ["G06","PINK:MAXA:S5Measure"],
        ["G07","PINK:MAXA:S1Measure"],
        ["G08","PINK:MAXD:S3Measure"],
        ["G09","PINK:MAXB:S5Measure"],
        ["G11","PINK:MAXB:S2Measure"],
        ["G12","PINK:MAXB:S1Measure"],
        ["G13","PINK:MAXC:S1Measure"],
        ["G16","PINK:MAXC:S3Measure"],
        ["G19","PINK:MAXD:S2Measure"],
        ["G20","PINK:MAXA:S4Measure"],
    ]

    ### Gap variables
    sig2fwmh=2.355
    diode1=[]
    diode2=[]
    diode3=[]
    diode4=[]
    diode_sum=[]
    gappos=[]
    tfy=[]

    ####################################################################################
    #### Callable Functions ############################################################
    ####################################################################################

    #### SPOT SCAN          ############################################################
    def ge_SEC_EL_spot(self, exposure, images, sample=" "):
        #self.ge_Num_Images=images
        self.line_images=images
        self.scan_images=images
        self.total_images=images
        self.ge_exptime=exposure
        self.sample=sample
        GE_AreaDet.stop()
        self.__ge_setup_file("ge")
        self.__create_pressure_devices()
        self.__ge_setup_caenels1(exposure)
        self.__ge_setup_caenels2(exposure)
        self.__ge_setup_delaygen(1, [0, exposure], [0, 0.001], [0, 0.001], [0, 0])
        self.__publish_fname(fname=" ")
        caput("PINK:AUX:ps_sample", " ")
        self.__eta_calc(exposure, images, 1, 1, 0)
        self.__ge_save_background(exposure)
        self.__ge_setup_greateyes(exposure, self.line_images)
        self.__ge_init_progress()
        self.__ge_clean_spec_sum()
        self.__ge_Create_Scan_Dataset()
        self.__ge_Save_Pre_Scan_Data(scantype="Spot")
        self.__ge_Arguments([exposure, images, sample], ftype=1)
        self.__publish_fname()
        self.__publish_status("Running spot scan...")
        caput("PINK:AUX:ps_sample", sample)
        GE_AreaDet.start()
        try:
            for scan_count in range(images):
                self.__ge_start_frame_countdown()
                GE_Raw_Array.waitCacheChange((int(math.ceil(exposure))*1000)+10000)
                #add 10ms delay to make sure all new data have arrived
                sleep(0.01)
                self.__ge_Save_Scan_Data()
                self.__ge_calc_progress()
        except Exception, ex1:
            print("Script Aborted")
            print(ex1)
            self.__publish_status("Script aborted")
            GE_AreaDet.stop()
        self.__ge_Save_Pos_Scan_Data()
        self.__save_specfile(0)
        pink_save_bl_snapshot()
        self.__remove_pressure_devices()
        print("Scan complete")
        self.__publish_status("Scan complete")

    #### LINE SCAN          ############################################################
    def ge_SEC_EL_line_vert(self, exposure, Y0, deltaY, Ypoints, passes=1, sample=" "):
        self.ge_exptime=exposure
        self.sample=sample
        start=float(Y0)
        step=float(deltaY)
        self.line_images=Ypoints
        self.scan_images=Ypoints
        self.total_images=Ypoints*passes
        self.ge_Num_Images=Ypoints
        self.ge_Num_Images_total=Ypoints*passes
        self.__publish_fname(fname=" ")
        caput("PINK:AUX:ps_sample", " ")
        GE_AreaDet.stop()
        self.__ge_setup_file("ge")
        self.__create_pressure_devices()
        self.__ge_setup_caenels1(exposure)
        self.__ge_setup_caenels2(exposure)
        self.__ge_setup_delaygen(1, [0, exposure], [0, 0.001], [0, 0.001], [0, 0])
        self.__ge_Save_Pre_Scan_Data_v2(scantype="Line")
        self.__ge_Create_Scan_Dataset_v3(cont=False, passes=passes)
        self.__ge_Arguments([exposure, Y0, deltaY, Ypoints, passes, sample], ftype=2)
        self.__publish_fname()
        scan_done=False
        passid=0
        while not(scan_done):
            if self.DEBUG: print("Scan pass = " + str(passid))
            self.__eta_calc(exposure, Ypoints, 1, (passes-passid), 0)
            self.__ge_save_background(exposure)
            self.__ge_setup_greateyes_sw_sync(exposure, self.line_images)
            self.__ge_init_progress()
            self.__ge_clean_spec_sum()
            self.__ge_Create_Scan_Dataset_v2(cont=False, passid=passid)
            self.__ge_Save_Pre_Scan_Data_v3(cont=False, passid=passid)
            self.__publish_status("line scan: " + "pass " + '{:d}'.format(passid+1) + "/" + '{:d}'.format(passes))
            caput("PINK:AUX:ps_sample", sample)
            SEC_el_y.move(start)
            try:
                for scan_count in range(self.line_images):
                    SEC_el_y.move(start+(scan_count*step))
                    self.__ge_start_frame_countdown()
                    GE_AreaDet.start()
                    GE_Raw_Array.waitCacheChange(120000)
                    #add 10ms delay to make sure all new data have arrived
                    sleep(0.01)
                    self.__ge_Save_Scan_Data_v2(cont=False, passid=passid)
                    self.__ge_calc_progress()
            except Exception, ex1:
                scan_done=True
                print("Script Aborted")
                print(ex1)
                self.__publish_status("Script aborted")
                GE_AreaDet.stop()
            self.__ge_Save_Pos_Scan_Data_v3(passid=passid)
            self.__save_specfile(passid)
            passid=passid+1
            if passid==passes: scan_done=True
        self.__ge_Save_Pos_Scan_Data_v4()
        pink_save_bl_snapshot()
        self.__remove_pressure_devices()
        print("Scan complete")
        self.__publish_status("Scan complete")

    #### ZIGZAG SCAN        ############################################################
    def ge_SEC_EL_zigzag(self, exposure, X0, deltaX, Xpoints, Y0, deltaY, Ypoints, passes=1, sample=" ", linedelay=0):
        images=int(Xpoints*Ypoints)
        self.ge_Num_Images=images
        self.ge_Num_Images_total=int(images*passes)
        self.ge_exptime=exposure
        self.sample=sample
        self.scan_images=Ypoints*Xpoints
        #Test sample manipulator limits
        if self._test_SEC_EL_limits(X0, deltaX, Xpoints, Y0, deltaY, Ypoints): sys.exit()
        X0=float(X0)
        Xstep=float(deltaX)
        Y0=float(Y0)
        Ystep=float(deltaY)
        self.__publish_fname(fname=" ")
        caput("PINK:AUX:ps_sample", " ")
        GE_AreaDet.stop()
        self.__ge_setup_file("ge")
        self.__create_pressure_devices()
        self.__ge_setup_caenels1(exposure)
        self.__ge_setup_caenels2(exposure)
        self.__ge_setup_delaygen(1, [0, exposure], [0, 0.001], [0, 0.001], [0, 0])
        self.__ge_setup_greateyes_sw_sync(exposure, images)
        self.__ge_Save_Pre_Scan_Data_v2(scantype="Zigzag")
        self.__ge_Create_Scan_Dataset_v3(cont=False, passes=passes)
        self.__ge_Arguments([exposure, X0, deltaX, Xpoints, Y0, deltaY, Ypoints, passes, sample], ftype=3)
        self.__publish_fname()
        scan_done=False
        passid=0
        while not(scan_done):
            if self.DEBUG: print("Scan pass = " + str(passid))
            self.__eta_calc(exposure, Ypoints, Xpoints, (passes-passid), linedelay)
            self.__ge_save_background(exposure)
            self.__ge_setup_greateyes_sw_sync(exposure, images)
            self.__ge_init_progress()
            self.__ge_clean_spec_sum()
            self.__ge_Create_Scan_Dataset_v2(cont=False, passid=passid)
            self.__ge_Save_Pre_Scan_Data_v3(cont=False, passid=passid)
            self.__publish_status("zigzag scan: " + "pass " + '{:d}'.format(passid+1) + "/" +  '{:d}'.format(passes) + " (" + sample + ")")
            caput("PINK:AUX:ps_sample", sample)
            SEC_el_x.move(X0)
            SEC_el_y.move(Y0)
            scan_dir=1
            try:
                for j in range(Xpoints):
                    SEC_el_x.move(X0+(j*Xstep))
                    for i in range(Ypoints):
                        if(scan_dir):
                            yoffset=i
                        else:
                            yoffset=(Ypoints-i-1)
                        SEC_el_y.move(Y0+(yoffset*Ystep))
                        self.__ge_start_frame_countdown()
                        GE_AreaDet.start()
                        GE_Raw_Array.waitCacheChange(120000)
                        #add 10ms delay to make sure all new data have arrived
                        sleep(0.01)
                        self.__ge_Save_Scan_Data_v2(cont=False, passid=passid)
                        self.__ge_calc_progress()
                    scan_dir=abs(scan_dir-1)
                    sleep(linedelay)
            except Exception, ex1:
                print("Script Aborted:")
                print(ex1)
                self.__publish_status("Script aborted")
                GE_AreaDet.stop()
            self.__ge_Save_Pos_Scan_Data_v3(cont=False, passid=passid)
            self.__save_specfile(passid)
            passid=passid+1
            if passid==passes: scan_done=True
        self.__ge_Save_Pos_Scan_Data_v4()
        pink_save_bl_snapshot()
        self.__remove_pressure_devices()
        print("Scan complete")
        self.__publish_status("Scan complete")

   #### CONT SCAN EXPOSURE + SPEED optimized  ###########################################################################
    def ge_SEC_EL_continuous_exposure_speed(self, exposure, X0, deltaX, Xpoints, Y0, Y1, Yspeed, passes=1, sample=" ", linedelay=0):
        readout_time=0.4
        Yspeed = abs(round(Yspeed))
        self.cont_speed = Yspeed
        Ypoints = int(math.floor(abs(Y1-Y0)/(Yspeed*(exposure+readout_time))))
        print("Scan calculated Ypoints: " + str(Ypoints))
        self.line_images=Ypoints
        self.scan_images=Ypoints*Xpoints
        self.total_images=Ypoints*Xpoints*passes
        self.ge_exptime=exposure
        self.sample=sample
        X0=float(X0)
        deltaX=float(deltaX)
        Y0=float(Y0)
        Y1=float(Y1)
        self.__continous_scan(exposure, passes, X0, deltaX, Xpoints, Y0, Y1, Ypoints, Yspeed, sample, 4, linedelay)

    #### CONT SCAN POINTS + SPEED optimized    ###########################################################################
    def ge_SEC_EL_continuous_points_speed(self, X0, deltaX, Xpoints, Y0, Y1, Ypoints, Yspeed, passes=1, sample=" ", linedelay=0):
        readout_time=0.4
        Yspeed = abs(round(Yspeed))
        self.cont_speed = Yspeed
        exposure = (float(abs(Y1-Y0))/(Ypoints*Yspeed))-readout_time
        print("Greateyes set exposure: " + '{:.3f}'.format(exposure) + " seconds")
        self.line_images=Ypoints
        self.scan_images=Ypoints*Xpoints
        self.total_images=Ypoints*Xpoints*passes
        self.ge_exptime=exposure
        self.sample=sample
        X0=float(X0)
        deltaX=float(deltaX)
        Y0=float(Y0)
        Y1=float(Y1)
        self.__continous_scan(exposure, passes, X0, deltaX, Xpoints, Y0, Y1, Ypoints, Yspeed, sample, 5, linedelay)

    #### CONT SCAN EXPOSURE + POINTS optimized    ###########################################################################
    def ge_SEC_EL_continuous_exposure_points(self, exposure, X0, deltaX, Xpoints, Y0, Y1, Ypoints, passes=1, sample=" ", linedelay=0):
        readout_time=0.4
        self.line_images=Ypoints
        self.scan_images=Ypoints*Xpoints
        self.total_images=Ypoints*Xpoints*passes
        self.ge_exptime=exposure
        self.sample=sample
        X0=float(X0)
        deltaX=float(deltaX)
        Y0=float(Y0)
        Y1=float(Y1)
        totaltime = Ypoints*(exposure+readout_time)
        Yspeed = abs(int((Y1-Y0)/totaltime))
        self.cont_speed = Yspeed
        print("Sample calculated speed: " + str(Yspeed) + " um/sec")
        self.__continous_scan(exposure, passes, X0, deltaX, Xpoints, Y0, Y1, Ypoints, Yspeed, sample, 6, linedelay)


    ####################################################################################
    #### Mythen functions   ############################################################
    ####################################################################################

    #### SPOT SCAN          ############################################################
    def mythen_SEC_EL_spot(self, exposure, images, sample=" "):
        dev.mythen_create()
        #self.ge_Num_Images=images
        self.line_images=images
        self.scan_images=images
        self.total_images=images
        self.ge_exptime=exposure
        self.sample=sample
        ##GE_AreaDet.stop()
        while(MythenAcq.read()>0):
            MythenAcq.write(0)
            MythenAcq.waitValue(0.0, 60000)
        self.__ge_setup_file("mythen")
        self.__create_pressure_devices()
        self.__ge_setup_caenels1(exposure)
        self.__ge_setup_caenels2(exposure)
        ## turn off delaygen
        self.__ge_setup_delaygen(5, [0, exposure], [0, 0.001], [0, 0.001], [0, 0])
        self.__publish_fname(fname=" ")
        caput("PINK:AUX:ps_sample", " ")
        ##self.__eta_calc(exposure, images, 1, 1, 0)
        self.__mythen_eta_calc(exposure, images, 1, 1, 0)
        ##self.__ge_save_background(exposure)
        ##self.__ge_setup_greateyes(exposure, self.line_images)
        self.__mythen_setup(exposure, self.line_images, 0, 0)
        ##self.__ge_init_progress()
        self.__mythen_init_progress()
        ##self.__ge_clean_spec_sum()
        self.__mythen_clean_spec_sum()
        self.__mythen_Create_Scan_Dataset()
        ##self.__ge_Save_Pre_Scan_Data(scantype="Spot")
        self.__mythen_Save_Pre_Scan_Data(scantype="Spot")
        self.__mythen_Arguments([exposure, images, sample], ftype=1)
        self.__publish_fname()
        self.__publish_status("Running spot scan...")
        caput("PINK:AUX:ps_sample", sample)
        ##GE_AreaDet.start()
        ## open shutter
        caput("PINK:PLCGAS:ei_B01", 1)
        sleep(0.2)
        #MythenAcq.write(1)
        try:
            for scan_count in range(images):
                self.__ge_start_frame_countdown()
                MythenAcq.write(1)
                MythenSpecSum.waitCacheChange((int(math.ceil(exposure))*1000)+10000)
                #add 100ms delay to make sure all new data have arrived
                sleep(0.1)
                ##self.__ge_Save_Scan_Data()
                self.__mythen_Save_Scan_Data()
                self.__mythen_calc_progress()
        except Exception, ex1:
            print("Script Aborted")
            print(ex1)
            self.__publish_status("Script aborted")
            ##GE_AreaDet.stop()
            MythenAcq.write(0)
        self.__mythen_Save_Pos_Scan_Data()
        ## close shutter
        caput("PINK:PLCGAS:ei_B01", 0)
        ##self.__save_specfile(0)
        self.__mythen_save_specfile(0)
        pink_save_bl_snapshot()
        self.__remove_pressure_devices()
        dev.mythen_remove()
        print("Scan complete")
        self.__publish_status("Scan complete")

    #### LINE SCAN          ############################################################
    def mythen_SEC_EL_line_vert(self, exposure, Y0, deltaY, Ypoints, passes=1, sample=" "):
        dev.mythen_create()
        self.ge_exptime=exposure
        self.sample=sample
        start=float(Y0)
        step=float(deltaY)
        self.line_images=Ypoints
        self.scan_images=Ypoints
        self.total_images=Ypoints*passes
        self.ge_Num_Images=Ypoints
        self.ge_Num_Images_total=Ypoints*passes
        self.__publish_fname(fname=" ")
        caput("PINK:AUX:ps_sample", " ")
        ##GE_AreaDet.stop()
        while(MythenAcq.read()>0):
            MythenAcq.write(0)
            MythenAcq.waitValue(0.0, 60000)
        self.__ge_setup_file("mythen")
        self.__create_pressure_devices()
        self.__ge_setup_caenels1(exposure)
        self.__ge_setup_caenels2(exposure)
        self.__ge_setup_delaygen(5, [0, exposure], [0, 0.001], [0, 0.001], [0, 0])
        self.__mythen_Save_Pre_Scan_Data_v2(scantype="Line")
        self.__mythen_Create_Scan_Dataset_v3(cont=False, passes=passes)
        self.__mythen_Arguments([exposure, Y0, deltaY, Ypoints, passes, sample], ftype=2)
        self.__publish_fname()
        scan_done=False
        passid=0
        while not(scan_done):
            if self.DEBUG: print("Scan pass = " + str(passid))
            self.__mythen_eta_calc(exposure, Ypoints, 1, (passes-passid), 0)
            ##self.__ge_save_background(exposure)
            ##self.__ge_setup_greateyes_sw_sync(exposure, self.line_images)
            self.__mythen_setup(exposure, self.line_images, 0, 0)
            self.__mythen_init_progress()
            self.__mythen_clean_spec_sum()
            self.__mythen_Create_Scan_Dataset_v2(cont=False, passid=passid)
            self.__mythen_Save_Pre_Scan_Data_v3(cont=False, passid=passid)
            self.__publish_status("line scan: " + "pass " + '{:d}'.format(passid+1) + "/" + '{:d}'.format(passes))
            caput("PINK:AUX:ps_sample", sample)
            SEC_el_y.move(start)
            try:
                for scan_count in range(self.line_images):
                    SEC_el_y.move(start+(scan_count*step))
                    self.__ge_start_frame_countdown()
                    ##GE_AreaDet.start()
                    MythenAcq.write(1)
                    MythenSpecSum.waitCacheChange(120000)
                    #add 100ms delay to make sure all new data have arrived
                    sleep(0.100)
                    self.__mythen_Save_Scan_Data_v2(cont=False, passid=passid)
                    self.__mythen_calc_progress()
            except Exception, ex1:
                scan_done=True
                print("Script Aborted")
                print(ex1)
                self.__publish_status("Script aborted")
                ##GE_AreaDet.stop()
                MythenAcq.write(0)
            self.__mythen_Save_Pos_Scan_Data_v3(passid=passid)
            self.__mythen_save_specfile(passid)
            passid=passid+1
            if passid==passes: scan_done=True
        self.__ge_Save_Pos_Scan_Data_v4()
        pink_save_bl_snapshot()
        self.__remove_pressure_devices()
        dev.mythen_remove()
        print("Scan complete")
        self.__publish_status("Scan complete")

    #### ZIGZAG SCAN        ############################################################
    def mythen_SEC_EL_zigzag(self, exposure, X0, deltaX, Xpoints, Y0, deltaY, Ypoints, passes=1, sample=" ", linedelay=0):
        dev.mythen_create()
        images=int(Xpoints*Ypoints)
        self.ge_Num_Images=images
        self.ge_Num_Images_total=int(images*passes)
        self.ge_exptime=exposure
        self.sample=sample
        self.scan_images=Ypoints*Xpoints
        #Test sample manipulator limits
        if self._test_SEC_EL_limits(X0, deltaX, Xpoints, Y0, deltaY, Ypoints): sys.exit()
        X0=float(X0)
        Xstep=float(deltaX)
        Y0=float(Y0)
        Ystep=float(deltaY)
        self.__publish_fname(fname=" ")
        caput("PINK:AUX:ps_sample", " ")
        ##GE_AreaDet.stop()
        while(MythenAcq.read()>0):
            MythenAcq.write(0)
            MythenAcq.waitValue(0.0, 60000)
        self.__ge_setup_file("mythen")
        self.__create_pressure_devices()
        self.__ge_setup_caenels1(exposure)
        self.__ge_setup_caenels2(exposure)
        self.__ge_setup_delaygen(5, [0, exposure], [0, 0.001], [0, 0.001], [0, 0])
        ##self.__ge_setup_greateyes_sw_sync(exposure, images)
        self.__mythen_Save_Pre_Scan_Data_v2(scantype="Zigzag")
        self.__mythen_Create_Scan_Dataset_v3(cont=False, passes=passes)
        self.__mythen_Arguments([exposure, X0, deltaX, Xpoints, Y0, deltaY, Ypoints, passes, sample], ftype=3)
        self.__publish_fname()
        scan_done=False
        passid=0
        while not(scan_done):
            if self.DEBUG: print("Scan pass = " + str(passid))
            self.__mythen_eta_calc(exposure, Ypoints, Xpoints, (passes-passid), linedelay)
            ##self.__ge_save_background(exposure)
            ##self.__ge_setup_greateyes_sw_sync(exposure, images)
            self.__mythen_setup(exposure, self.line_images, 0, 0)
            self.__mythen_init_progress()
            self.__mythen_clean_spec_sum()
            self.__mythen_Create_Scan_Dataset_v2(cont=False, passid=passid)
            self.__mythen_Save_Pre_Scan_Data_v3(cont=False, passid=passid)
            self.__publish_status("zigzag scan: " + "pass " + '{:d}'.format(passid+1) + "/" +  '{:d}'.format(passes) + " (" + sample + ")")
            caput("PINK:AUX:ps_sample", sample)
            SEC_el_x.move(X0)
            SEC_el_y.move(Y0)
            scan_dir=1
            try:
                for j in range(Xpoints):
                    SEC_el_x.move(X0+(j*Xstep))
                    for i in range(Ypoints):
                        if(scan_dir):
                            yoffset=i
                        else:
                            yoffset=(Ypoints-i-1)
                        SEC_el_y.move(Y0+(yoffset*Ystep))
                        self.__ge_start_frame_countdown()
                        ##GE_AreaDet.start()
                        MythenAcq.write(1)
                        MythenSpecSum.waitCacheChange(120000)
                        #add 100ms delay to make sure all new data have arrived
                        sleep(0.1)
                        self.__mythen_Save_Scan_Data_v2(cont=False, passid=passid)
                        self.__mythen_calc_progress()
                    scan_dir=abs(scan_dir-1)
                    sleep(linedelay)
            except Exception, ex1:
                print("Script Aborted:")
                print(ex1)
                self.__publish_status("Script aborted")
                ##GE_AreaDet.stop()
                MythenAcq.write(0)
            self.__mythen_Save_Pos_Scan_Data_v3(cont=False, passid=passid)
            self.__mythen_save_specfile(passid)
            passid=passid+1
            if passid==passes: scan_done=True
        self.__ge_Save_Pos_Scan_Data_v4()
        pink_save_bl_snapshot()
        self.__remove_pressure_devices()
        dev.mythen_remove()
        print("Scan complete")
        self.__publish_status("Scan complete")

   #### CONT SCAN EXPOSURE + SPEED optimized  ###########################################################################
    def mythen_SEC_EL_continuous_exposure_speed(self, exposure, X0, deltaX, Xpoints, Y0, Y1, Yspeed, passes=1, sample=" ", linedelay=0):
        readout_time=0.002
        Yspeed = abs(round(Yspeed))
        self.cont_speed = Yspeed
        Ypoints = int(math.floor(abs(Y1-Y0)/(Yspeed*(exposure+readout_time))))
        print("Scan calculated Ypoints: " + str(Ypoints))
        self.line_images=Ypoints
        self.scan_images=Ypoints*Xpoints
        self.total_images=Ypoints*Xpoints*passes
        self.ge_exptime=exposure
        self.sample=sample
        X0=float(X0)
        deltaX=float(deltaX)
        Y0=float(Y0)
        Y1=float(Y1)
        self.__mythen_continous_scan(exposure, passes, X0, deltaX, Xpoints, Y0, Y1, Ypoints, Yspeed, sample, 4, linedelay)

    #### CONT SCAN POINTS + SPEED optimized    ###########################################################################
    def mythen_SEC_EL_continuous_points_speed(self, X0, deltaX, Xpoints, Y0, Y1, Ypoints, Yspeed, passes=1, sample=" ", linedelay=0):
        readout_time=0.4
        Yspeed = abs(round(Yspeed))
        self.cont_speed = Yspeed
        exposure = (float(abs(Y1-Y0))/(Ypoints*Yspeed))-readout_time
        print("Greateyes set exposure: " + '{:.3f}'.format(exposure) + " seconds")
        self.line_images=Ypoints
        self.scan_images=Ypoints*Xpoints
        self.total_images=Ypoints*Xpoints*passes
        self.ge_exptime=exposure
        self.sample=sample
        X0=float(X0)
        deltaX=float(deltaX)
        Y0=float(Y0)
        Y1=float(Y1)
        self.__mythen_continous_scan(exposure, passes, X0, deltaX, Xpoints, Y0, Y1, Ypoints, Yspeed, sample, 5, linedelay)

    #### CONT SCAN EXPOSURE + POINTS optimized    ###########################################################################
    def mythen_SEC_EL_continuous_exposure_points(self, exposure, X0, deltaX, Xpoints, Y0, Y1, Ypoints, passes=1, sample=" ", linedelay=0):
        readout_time=0.4
        self.line_images=Ypoints
        self.scan_images=Ypoints*Xpoints
        self.total_images=Ypoints*Xpoints*passes
        self.ge_exptime=exposure
        self.sample=sample
        X0=float(X0)
        deltaX=float(deltaX)
        Y0=float(Y0)
        Y1=float(Y1)
        totaltime = Ypoints*(exposure+readout_time)
        Yspeed = abs(int((Y1-Y0)/totaltime))
        self.cont_speed = Yspeed
        print("Sample calculated speed: " + str(Yspeed) + " um/sec")
        self.__mythen_continous_scan(exposure, passes, X0, deltaX, Xpoints, Y0, Y1, Ypoints, Yspeed, sample, 6, linedelay)

    ####################################################################################
    #### Internal Functions ############################################################
    ####################################################################################

    def __ydat1_grab(self):
        sleep(self.ge_exptime)
        self.ydat1.append(SEC_el_y.getPosition())

    def __sec_el_y_safemove(self, pos):
        i=0
        while(not(SEC_el_y.isInPosition(pos))):
            SEC_el_y.moveAsync(pos)
            i=i+1
            if(i==10): print("Err: Motor SEC_el_y seems to be not moving after 10 seconds")
            sleep(1)

    def __ge_init_frame_countdown(self, exposure):
        caput("PINK:AUX:countdown.B", exposure)

    def __ge_start_frame_countdown(self):
        AUX_countdown.write(100)

    def __reinit_hzb_pvs(self):
        U17_Gap_RBV.initialize()
        U17_Gap_Status.initialize()
        ring_current.initialize()

    def __ge_init_progress(self):
        Scan_Progress.write(0)
        self.GE_start_frame = GE_FrameID.take()
        self.__ge_init_frame_countdown(self.ge_exptime)
        self.__reinit_hzb_pvs()
        #self.__publish_status("Running scan...")
        #print("Scan has started...")

    def __mythen_init_progress(self):
        Scan_Progress.write(0)
        self.GE_start_frame = MythenID.take()
        self.__ge_init_frame_countdown(self.ge_exptime)
        self.__reinit_hzb_pvs()
        #self.__publish_status("Running scan...")
        #print("Scan has started...")

    def __ge_calc_progress(self):
        Scan_Progress.write(100*(GE_FrameID.take()-self.GE_start_frame)/(self.scan_images))
        if self.DEBUG: print("ID0: " + str(self.GE_start_frame) + " ID: " + str(GE_FrameID.take()) + " Total: " + str(self.scan_images) + " Progress: " + str(Scan_Progress.take()))
        #self.__ge_start_frame_countdown()

    def __mythen_calc_progress(self):
        Scan_Progress.write(100*(MythenID.take()-self.GE_start_frame)/(self.scan_images))
        if self.DEBUG: print("ID0: " + str(self.GE_start_frame) + " ID: " + str(MythenID.take()) + " Total: " + str(self.scan_images) + " Progress: " + str(Scan_Progress.take()))
        #self.__ge_start_frame_countdown()

    def __ge_setup_caenels1(self, Exp_Time=1, Enable=True):
        cae_exp_time=float(Exp_Time)
        caputq("PINK:CAE1:Acquire", 0)
        caput("PINK:CAE1:ValuesPerRead", int(1000*cae_exp_time))
        caput("PINK:CAE1:AveragingTime", float(cae_exp_time))
        caput("PINK:CAE1:TriggerMode", 1)
        if Enable:
            caputq("PINK:CAE1:Acquire", 1)
        else:
            caputq("PINK:CAE1:Acquire", 0)

    def __ge_setup_caenels2(self, Exp_Time=1, Enable=True):
        cae_exp_time=float(Exp_Time)
        caputq("PINK:CAE2:Acquire", 0)
        caput("PINK:CAE2:ValuesPerRead", int(1000*cae_exp_time))
        caput("PINK:CAE2:AveragingTime", float(cae_exp_time))
        caput("PINK:CAE2:TriggerMode", 1)
        if Enable:
            caputq("PINK:CAE2:Acquire", 1)
        else:
            caputq("PINK:CAE2:Acquire", 0)

    def __ge_setup_delaygen(self, mode, ch1, ch2, ch3, ch4):
        ## Trigger mode
        caput("PINK:DG01:TriggerSourceMO", mode)
        ## shutter delay
        caput("PINK:DG01:ADelayAO", ch1[0])
        ## shutter exposure
        caput("PINK:DG01:BDelayAO", ch1[1]-0.02)
        ## mythen delay
        caput("PINK:DG01:CDelayAO", ch2[0])
        ## mythen exposure
        caput("PINK:DG01:DDelayAO", ch2[1])
        ## greateyes delay
        caput("PINK:DG01:EDelayAO", ch3[0])
        ## greateyes exposure
        caput("PINK:DG01:FDelayAO", ch3[1])
        ## extra channel delay
        caput("PINK:DG01:GDelayAO", ch4[0])
        ## extra channel exposure
        caput("PINK:DG01:HDelayAO", ch4[1])

    def __ge_setup_greateyes(self, exposure=1, images=1):
        if self.DEBUG: print("Setup greateyes...")
        caput("PINK:GEYES:cam1:NumImages", images)
        if(images==1):
            caput("PINK:GEYES:cam1:ImageMode", 0)
        else:
            caput("PINK:GEYES:cam1:ImageMode", 1)
        caput("PINK:GEYES:cam1:AcquireTime", exposure)
        if self.DEBUG: print("Setup greateyes ok")

    def __mythen_setup(self, exposure, images, imagemode, triggermode):
        caput("PINK:MYTHEN:cam1:AcquireTime", exposure)
        caput("PINK:MYTHEN:cam1:NumFrames", images)
        caput("PINK:MYTHEN:cam1:ImageMode", imagemode)
        caput("PINK:MYTHEN:cam1:TriggerMode", triggermode)

    def __ge_setup_greateyes_sw_sync(self, exposure=1, images=1):
        if self.DEBUG: print("Setup greateyes...")
        caput("PINK:GEYES:cam1:NumImages", images)
        caput("PINK:GEYES:cam1:ImageMode", 0)
        caput("PINK:GEYES:cam1:AcquireTime", exposure)
        if self.DEBUG: print("Setup greateyes ok")

    def __ge_clean_spectrum_sum(self):
        caput("PINK:GEYES:specsum_reset", 0)
        caput("PINK:GEYES:specsum_reset", 1)

    def __ge_save_background(self, Exp_Time=1):
        acqsuccess = False
        WDog1 = 0
        #Exposure time (msec) + 10000 msec
        acqtimeout = int((Exp_Time*1000)+10000)
        while(acqsuccess==False):
            # Check Geyes status and stop if running
            if self.DEBUGLOG: log("BG: Saving Background started", data_file=False)
            WDog2=1
            if self.DEBUGLOG: log("BG: Waiting for detector to stop collecting", data_file=False)
            if(caget("PINK:GEYES:cam1:DetectorState_RBV")):
                caput("PINK:GEYES:cam1:Acquire", 0)
                while(caget("PINK:GEYES:cam1:DetectorState_RBV", type='d')):
                    print("Waiting for detector to stop collecting. ("+str(WDog2)+" sec)")
                    WDog2=WDog2+1
                    sleep(1)
            if self.DEBUGLOG: log("BG: Detector stopped. Closing Fast Shutter", data_file=False)
            # Close fast shutter
            caput("PINK:PLCGAS:ei_B01", 0)
            if self.DEBUGLOG: log("BG: Setup Detector", data_file=False)
            self.__ge_setup_greateyes(Exp_Time, 1)
            if self.DEBUG: print("Background saving...")
            self.__publish_status("Background saving...")
            #self.__publish_fname(fname=" ")
            if self.DEBUGLOG: log("BG: Initiate Frame countdown", data_file=False)
            self.__ge_init_frame_countdown(Exp_Time)
            if self.DEBUGLOG: log("BG: Write scan progress", data_file=False)
            Scan_Progress.write(-1)
            if self.DEBUGLOG: log("BG: Disabling Shutter Sync", data_file=False)
            #Disabling shutter
            ##caput("PINK:GEYES:cam1:ShutterMode", 0)
            caput("PINK:DG01:TriggerSourceMO", 5)
            if self.DEBUGLOG: log("BG: Disable BG Processing", data_file=False)
            #Disable background processing on EPICS
            caput("PINK:GEYES:Proc1:EnableBackground",0)
            sleep(1)
            if self.DEBUGLOG: log("BG: Start Frame countdown", data_file=False)
            self.__ge_start_frame_countdown()
            if self.DEBUGLOG: log("BG: *** Acquire 1 image", data_file=False)
            #Take 1 frame (Using caput blocks until acquisition is done)
            #caput("PINK:GEYES:cam1:Acquire", 1)
            GE_AreaDet.start()
            acqsuccess=GE_Raw_Array.waitCacheChange(acqtimeout)
            if acqsuccess==False:
                WDog1 = WDog1+1
                if self.DEBUGLOG: log("BG: Acquisition timeout, retrying ... #" + str(WDog1), data_file=False)
        if self.DEBUGLOG: log("BG: *** Acquire done!", data_file=False)
        #gectrl.start()
        sleep(0.5)
        if self.DEBUGLOG: log("BG: Save Bg image on extra record", data_file=False)
        #Transfer frame to bgimage
        caput("PINK:GEYES:savebg", 1)
        if self.DEBUGLOG: log("BG: Enable BG Processing", data_file=False)
        #Save image on Geyes process plugin
        caput("PINK:GEYES:Proc1:SaveBackground", 1)
        if self.DEBUGLOG: log("BG: Enable Shutter Sync", data_file=False)
        #Enabling shutter
        ##caput("PINK:GEYES:cam1:ShutterMode", 2)
        caput("PINK:DG01:TriggerSourceMO", 1)
        if self.DEBUGLOG: log("BG: Enable BG Processing", data_file=False)
        #Turns ON Background processing on GEyes Process Plugin
        caput("PINK:GEYES:Proc1:EnableBackground",1)
        self.ge_bg_spectra = GE_Spectrum.read()
        if self.DEBUG: print("Background saved")
        self.__publish_status("Background saved")

    def __ge_setup_file(self, fname="ge"):
        set_exec_pars(open=False, name=fname, reset=True)

    def __ge_clean_spec_sum(self):
        caput("PINK:GEYES:specsum_reset", 0)
        caput("PINK:GEYES:specsum_reset", 1)

    def __mythen_clean_spec_sum(self):
        caput("PINK:MYTHEN:specsum_enable", 0)
        caput("PINK:MYTHEN:specsum_enable", 1)

    def __ge_Save_Pre_Scan_Data(self, scantype=" ", passid=0):
        if self.DEBUG: print("Saving Pre scan dataset ...")
        save_dataset("RAW/GE_BG_Image", GE_BG_Image.read(), features=self.data_compression)
        #save_dataset("Processed/GE_Spectrum_Convertion", GE_Spectrum_Conv.read())
        save_dataset("Detector/BG_Spectra", self.ge_bg_spectra)
        save_dataset("Detector/GE_ROI_Line", GE_ROI_Line.read())
        save_dataset("Detector/GE_ROI_SizeX", GE_ROI_SizeX.read())
        save_dataset("Detector/GE_ROI_SizeY", GE_ROI_SizeY.read())
        save_dataset("Detector/Exposure_Time", GE_AreaDet.getExposure())
        save_dataset("Detector/GE_Open_Delay", caget("PINK:GEYES:cam1:ShutterOpenDelay"))
        save_dataset("Detector/GE_Close_Delay", caget("PINK:GEYES:cam1:ShutterCloseDelay"))
        save_dataset("Detector/GE_Num_Images", self.scan_images)
        save_dataset("Detector/Gain_Type", caget("PINK:GEYES:cam1:GreatEyesGain_RBV"))
        save_dataset("Scan/Scan_Start_Time", time.ctime())
        save_dataset("Scan/Sample", self.sample)
        save_dataset("Scan/Scan_Type", scantype)
        save_dataset("Scan/Pass", passid)
        if self.DEBUG: print("Saving Pre scan dataset OK")

    def __mythen_Save_Pre_Scan_Data(self, scantype=" ", passid=0):
        if self.DEBUG: print("Saving Pre scan dataset ...")
        ##save_dataset("RAW/GE_BG_Image", GE_BG_Image.read(), features=self.data_compression)
        #save_dataset("Processed/GE_Spectrum_Convertion", GE_Spectrum_Conv.read())
        ##save_dataset("Detector/BG_Spectra", self.ge_bg_spectra)
        ##save_dataset("Detector/GE_ROI_Line", GE_ROI_Line.read())
        ##save_dataset("Detector/GE_ROI_SizeX", GE_ROI_SizeX.read())
        ##save_dataset("Detector/GE_ROI_SizeY", GE_ROI_SizeY.read())
        save_dataset("Detector/Exposure_Time", self.ge_exptime)
        ##save_dataset("Detector/GE_Open_Delay", caget("PINK:GEYES:cam1:ShutterOpenDelay"))
        ##save_dataset("Detector/GE_Close_Delay", caget("PINK:GEYES:cam1:ShutterCloseDelay"))
        save_dataset("Detector/Num_Images", self.scan_images)
        ##save_dataset("Detector/Gain_Type", caget("PINK:GEYES:cam1:GreatEyesGain_RBV"))
        save_dataset("Scan/Scan_Start_Time", time.ctime())
        save_dataset("Scan/Sample", self.sample)
        save_dataset("Scan/Scan_Type", scantype)
        save_dataset("Scan/Pass", passid)
        if self.DEBUG: print("Saving Pre scan dataset OK")

    def __ge_Save_Pre_Scan_Data_v2(self, scantype=" "):
        if self.DEBUG: print("Saving Pre scan dataset v2 ...")
        save_dataset("Detector/GE_ROI_Line", GE_ROI_Line.read())
        save_dataset("Detector/GE_ROI_SizeX", GE_ROI_SizeX.read())
        save_dataset("Detector/GE_ROI_SizeY", GE_ROI_SizeY.read())
        save_dataset("Detector/Exposure_Time", GE_AreaDet.getExposure())
        save_dataset("Detector/BG_Spectra", self.ge_bg_spectra)
        save_dataset("Detector/GE_Open_Delay", caget("PINK:GEYES:cam1:ShutterOpenDelay"))
        save_dataset("Detector/GE_Close_Delay", caget("PINK:GEYES:cam1:ShutterCloseDelay"))
        #save_dataset("Detector/GE_Num_Images", GE_AreaDet.getNumImages())
        save_dataset("Detector/Gain_Type", caget("PINK:GEYES:cam1:GreatEyesGain_RBV"))
        save_dataset("Scan/Sample", self.sample)
        save_dataset("Scan/Scan_Type", scantype)
        save_dataset("Scan/Scan_Images", self.scan_images)
        save_dataset("Scan/Scan_Start_Time", time.ctime())
        if self.DEBUG: print("Saving Pre scan dataset OK")

    def __mythen_Save_Pre_Scan_Data_v2(self, scantype=" "):
        if self.DEBUG: print("Saving Pre scan dataset v2 ...")
        ##save_dataset("Detector/GE_ROI_Line", GE_ROI_Line.read())
        #save_dataset("Detector/GE_ROI_SizeX", GE_ROI_SizeX.read())
        ##save_dataset("Detector/GE_ROI_SizeY", GE_ROI_SizeY.read())
        save_dataset("Detector/Exposure_Time", self.ge_exptime)
        ##save_dataset("Detector/BG_Spectra", self.ge_bg_spectra)
        ##save_dataset("Detector/GE_Open_Delay", caget("PINK:GEYES:cam1:ShutterOpenDelay"))
        ##save_dataset("Detector/GE_Close_Delay", caget("PINK:GEYES:cam1:ShutterCloseDelay"))
        #save_dataset("Detector/GE_Num_Images", GE_AreaDet.getNumImages())
        ##save_dataset("Detector/Gain_Type", caget("PINK:GEYES:cam1:GreatEyesGain_RBV"))
        save_dataset("Scan/Sample", self.sample)
        save_dataset("Scan/Scan_Type", scantype)
        save_dataset("Scan/Scan_Images", self.scan_images)
        save_dataset("Scan/Scan_Start_Time", time.ctime())
        if self.DEBUG: print("Saving Pre scan dataset OK")

    def __ge_Save_Pre_Scan_Data_v3(self, cont=False, passid=0):
        if self.DEBUG: print("Saving Pre scan dataset v3 ...")
        passfolder = "pass_"+'{:03d}'.format(passid)+"/"
        save_dataset(passfolder+"RAW/GE_BG_Image", GE_BG_Image.read(), features=self.data_compression)
        save_dataset(passfolder+"Scan/Scan_Start_Time", time.ctime())
        save_dataset(passfolder+"Scan/Pass", passid)
        if self.DEBUG: print("Saving Pre scan dataset OK")

    def __mythen_Save_Pre_Scan_Data_v3(self, cont=False, passid=0):
        if self.DEBUG: print("Saving Pre scan dataset v3 ...")
        passfolder = "pass_"+'{:03d}'.format(passid)+"/"
        ##save_dataset(passfolder+"RAW/GE_BG_Image", GE_BG_Image.read(), features=self.data_compression)
        save_dataset(passfolder+"Scan/Scan_Start_Time", time.ctime())
        save_dataset(passfolder+"Scan/Pass", passid)
        if self.DEBUG: print("Saving Pre scan dataset OK")

    def __ge_Arguments(self, args, ftype=0):
        if ftype==1:
            save_dataset("Scan/Args/function", "ge_SEC_EL_spot")
            save_dataset("Scan/Args/exposure", args[0])
            save_dataset("Scan/Args/images", args[1])
            save_dataset("Scan/Args/sample", args[2])
        elif ftype==2:
            save_dataset("Scan/Args/function", "ge_SEC_EL_line_vert")
            save_dataset("Scan/Args/exposure", args[0])
            save_dataset("Scan/Args/Y0", args[1])
            save_dataset("Scan/Args/deltaY", args[2])
            save_dataset("Scan/Args/Ypoints", args[3])
            save_dataset("Scan/Args/passes", args[4])
            save_dataset("Scan/Args/sample", args[5])
        elif ftype==3:
            save_dataset("Scan/Args/function", "ge_SEC_EL_zigzag")
            save_dataset("Scan/Args/exposure", args[0])
            save_dataset("Scan/Args/X0", args[1])
            save_dataset("Scan/Args/deltaX", args[2])
            save_dataset("Scan/Args/Xpoints", args[3])
            save_dataset("Scan/Args/Y0", args[4])
            save_dataset("Scan/Args/deltaY", args[5])
            save_dataset("Scan/Args/Ypoints", args[6])
            save_dataset("Scan/Args/passes", args[7])
            save_dataset("Scan/Args/sample", args[8])
        elif ftype==4:
            save_dataset("Scan/Args/function", "ge_SEC_EL_continous_exposure_speed")
            save_dataset("Scan/Args/exposure", args[0])
            save_dataset("Scan/Args/X0", args[1])
            save_dataset("Scan/Args/deltaX", args[2])
            save_dataset("Scan/Args/Xpoints", args[3])
            save_dataset("Scan/Args/Y0", args[4])
            save_dataset("Scan/Args/Y1", args[5])
            save_dataset("Scan/Args/Yspeed", args[7])
            save_dataset("Scan/Args/passes", args[8])
            save_dataset("Scan/Args/sample", args[9])
        elif ftype==5:
            save_dataset("Scan/Args/function", "ge_SEC_EL_continous_points_speed")
            save_dataset("Scan/Args/X0", args[1])
            save_dataset("Scan/Args/deltaX", args[2])
            save_dataset("Scan/Args/Xpoints", args[3])
            save_dataset("Scan/Args/Y0", args[4])
            save_dataset("Scan/Args/Y1", args[5])
            save_dataset("Scan/Args/Ypoints", args[6])
            save_dataset("Scan/Args/Yspeed", args[7])
            save_dataset("Scan/Args/passes", args[8])
            save_dataset("Scan/Args/sample", args[9])
        elif ftype==6:
            save_dataset("Scan/Args/function", "ge_SEC_EL_continous_exposure_points")
            save_dataset("Scan/Args/exposure", args[0])
            save_dataset("Scan/Args/X0", args[1])
            save_dataset("Scan/Args/deltaX", args[2])
            save_dataset("Scan/Args/Xpoints", args[3])
            save_dataset("Scan/Args/Y0", args[4])
            save_dataset("Scan/Args/Y1", args[5])
            save_dataset("Scan/Args/Ypoints", args[6])
            save_dataset("Scan/Args/passes", args[8])
            save_dataset("Scan/Args/sample", args[9])
        else:
            return

    def __mythen_Arguments(self, args, ftype=0):
        if ftype==1:
            save_dataset("Scan/Args/function", "mythen_SEC_EL_spot")
            save_dataset("Scan/Args/exposure", args[0])
            save_dataset("Scan/Args/images", args[1])
            save_dataset("Scan/Args/sample", args[2])
        elif ftype==2:
            save_dataset("Scan/Args/function", "mythen_SEC_EL_line_vert")
            save_dataset("Scan/Args/exposure", args[0])
            save_dataset("Scan/Args/Y0", args[1])
            save_dataset("Scan/Args/deltaY", args[2])
            save_dataset("Scan/Args/Ypoints", args[3])
            save_dataset("Scan/Args/passes", args[4])
            save_dataset("Scan/Args/sample", args[5])
        elif ftype==3:
            save_dataset("Scan/Args/function", "mythen_SEC_EL_zigzag")
            save_dataset("Scan/Args/exposure", args[0])
            save_dataset("Scan/Args/X0", args[1])
            save_dataset("Scan/Args/deltaX", args[2])
            save_dataset("Scan/Args/Xpoints", args[3])
            save_dataset("Scan/Args/Y0", args[4])
            save_dataset("Scan/Args/deltaY", args[5])
            save_dataset("Scan/Args/Ypoints", args[6])
            save_dataset("Scan/Args/passes", args[7])
            save_dataset("Scan/Args/sample", args[8])
        elif ftype==4:
            save_dataset("Scan/Args/function", "mythen_SEC_EL_continous_exposure_speed")
            save_dataset("Scan/Args/exposure", args[0])
            save_dataset("Scan/Args/X0", args[1])
            save_dataset("Scan/Args/deltaX", args[2])
            save_dataset("Scan/Args/Xpoints", args[3])
            save_dataset("Scan/Args/Y0", args[4])
            save_dataset("Scan/Args/Y1", args[5])
            save_dataset("Scan/Args/Yspeed", args[7])
            save_dataset("Scan/Args/passes", args[8])
            save_dataset("Scan/Args/sample", args[9])
        elif ftype==5:
            save_dataset("Scan/Args/function", "mythen_SEC_EL_continous_points_speed")
            save_dataset("Scan/Args/X0", args[1])
            save_dataset("Scan/Args/deltaX", args[2])
            save_dataset("Scan/Args/Xpoints", args[3])
            save_dataset("Scan/Args/Y0", args[4])
            save_dataset("Scan/Args/Y1", args[5])
            save_dataset("Scan/Args/Ypoints", args[6])
            save_dataset("Scan/Args/Yspeed", args[7])
            save_dataset("Scan/Args/passes", args[8])
            save_dataset("Scan/Args/sample", args[9])
        elif ftype==6:
            save_dataset("Scan/Args/function", "mythen_SEC_EL_continous_exposure_points")
            save_dataset("Scan/Args/exposure", args[0])
            save_dataset("Scan/Args/X0", args[1])
            save_dataset("Scan/Args/deltaX", args[2])
            save_dataset("Scan/Args/Xpoints", args[3])
            save_dataset("Scan/Args/Y0", args[4])
            save_dataset("Scan/Args/Y1", args[5])
            save_dataset("Scan/Args/Ypoints", args[6])
            save_dataset("Scan/Args/passes", args[8])
            save_dataset("Scan/Args/sample", args[9])
        else:
            return

    def __ge_Create_Scan_Dataset(self, cont=False):
        if self.DEBUG: print("create scan dataset ...")
        create_dataset("RAW/GE_Raw_Image", 'd', False, (0, int(GE_BG_SizeY.take()), int(GE_BG_SizeX.take())), features=self.data_compression)
        create_dataset("RAW/IZero_Profile", 'd', False, (self.scan_images, 100))
        create_dataset("RAW/TFY_Profile", 'd', False, (self.scan_images, 100))
        create_dataset("Processed/GE_ROI_Image", 'd', False, (0, int(GE_ROI_SizeY.take()), int(GE_ROI_SizeX.take())), features=self.data_compression)
        create_dataset("Processed/GE_Spectrum", 'd', False, (self.scan_images, int(GE_BG_SizeX.take())))
        create_dataset("Processed/Izero", 'd', False)
        create_dataset("Processed/TFY", 'd', False)
        create_dataset("Detector/GE_Sensor_Temp", 'd', False)
        create_dataset("Scan/GE_FrameID", 'i', False)
        create_dataset("Scan/Timestamps", 'l', False)
        self.__create_pressure_dataset(passfolder = "")
        #create_dataset("Pressure/Diagnostic_PV", 'd', False)
        #create_dataset("Pressure/Diagnostic_HV", 'd', False)
        #create_dataset("Pressure/Spectrometer_PV", 'd', False)
        #create_dataset("Pressure/Spectrometer_HV", 'd', False)
        #create_dataset("Pressure/Sample_Chamber", 'd', False)
        if cont==False:
            create_dataset("RAW/SEC_el_x", 'd', False)
            create_dataset("RAW/SEC_el_y", 'd', False)
        create_dataset("RAW/ring_current", 'd', False)
        if self.DEBUG: print("create scan dataset ok")

    def __mythen_Create_Scan_Dataset(self, cont=False):
        if self.DEBUG: print("create scan dataset ...")
        create_dataset("RAW/Mythen_Raw_Array", 'd', False, (self.scan_images, 1280))
        create_dataset("RAW/IZero_Profile", 'd', False, (self.scan_images, 100))
        create_dataset("RAW/TFY_Profile", 'd', False, (self.scan_images, 100))
        ##create_dataset("Processed/GE_ROI_Image", 'd', False, (0, int(GE_ROI_SizeY.take()), int(GE_ROI_SizeX.take())), features=self.data_compression)
        ##create_dataset("Processed/GE_Spectrum", 'd', False, (self.scan_images, int(GE_BG_SizeX.take())))
        create_dataset("Processed/Izero", 'd', False)
        create_dataset("Processed/TFY", 'd', False)
        #create_dataset("Detector/GE_Sensor_Temp", 'd', False)
        create_dataset("Scan/Mythen_FrameID", 'i', False)
        create_dataset("Scan/Timestamps", 'l', False)
        self.__create_pressure_dataset(passfolder = "")
        #create_dataset("Pressure/Diagnostic_PV", 'd', False)
        #create_dataset("Pressure/Diagnostic_HV", 'd', False)
        #create_dataset("Pressure/Spectrometer_PV", 'd', False)
        #create_dataset("Pressure/Spectrometer_HV", 'd', False)
        #create_dataset("Pressure/Sample_Chamber", 'd', False)
        if cont==False:
            create_dataset("RAW/SEC_el_x", 'd', False)
            create_dataset("RAW/SEC_el_y", 'd', False)
        create_dataset("RAW/ring_current", 'd', False)
        if self.DEBUG: print("create scan dataset ok")


    def __ge_Create_Scan_Dataset_v2(self, cont=False, passid=0):
        if self.DEBUG: print("create scan dataset v2... ")
        passfolder = "pass_"+'{:03d}'.format(passid)+"/"
        create_dataset(passfolder+"RAW/GE_Raw_Image", 'd', False, (0, int(GE_BG_SizeY.take()), int(GE_BG_SizeX.take())), features=self.data_compression)
        create_dataset(passfolder+"RAW/IZero_Profile", 'd', False, (self.scan_images, 100))
        create_dataset(passfolder+"RAW/TFY_Profile", 'd', False, (self.scan_images, 100))
        create_dataset(passfolder+"Processed/GE_ROI_Image", 'd', False, (0, int(GE_ROI_SizeY.take()), int(GE_ROI_SizeX.take())), features=self.data_compression)
        create_dataset(passfolder+"Processed/GE_Spectrum", 'd', False, (self.scan_images, int(GE_BG_SizeX.take())))
        create_dataset(passfolder+"Processed/Izero", 'd', False)
        create_dataset(passfolder+"Processed/TFY", 'd', False)
        create_dataset(passfolder+"Detector/GE_Sensor_Temp", 'd', False)
        create_dataset(passfolder+"Scan/GE_FrameID", 'i', False)
        create_dataset(passfolder+"Scan/Timestamps", 'l', False)
        self.__create_pressure_dataset(passfolder = passfolder)
        #create_dataset(passfolder+"Pressure/Diagnostic_PV", 'd', False)
        #create_dataset(passfolder+"Pressure/Diagnostic_HV", 'd', False)
        #create_dataset(passfolder+"Pressure/Spectrometer_PV", 'd', False)
        #create_dataset(passfolder+"Pressure/Spectrometer_HV", 'd', False)
        #create_dataset(passfolder+"Pressure/Sample_Chamber", 'd', False)
        create_dataset(passfolder+"RAW/ring_current", 'd', False)
        if cont==False:
            create_dataset(passfolder+"RAW/SEC_el_x", 'd', False)
            create_dataset(passfolder+"RAW/SEC_el_y", 'd', False)
        if self.DEBUG: print("create scan dataset ok")

    def __mythen_Create_Scan_Dataset_v2(self, cont=False, passid=0):
        if self.DEBUG: print("create scan dataset v2... ")
        passfolder = "pass_"+'{:03d}'.format(passid)+"/"
        create_dataset(passfolder+"RAW/Mythen_Raw_Array", 'd', False, (self.scan_images, 1280))
        create_dataset(passfolder+"RAW/IZero_Profile", 'd', False, (self.scan_images, 100))
        create_dataset(passfolder+"RAW/TFY_Profile", 'd', False, (self.scan_images, 100))
        ##create_dataset(passfolder+"Processed/GE_ROI_Image", 'd', False, (0, int(GE_ROI_SizeY.take()), int(GE_ROI_SizeX.take())), features=self.data_compression)
        ##create_dataset(passfolder+"Processed/GE_Spectrum", 'd', False, (self.scan_images, int(GE_BG_SizeX.take())))
        create_dataset(passfolder+"Processed/Izero", 'd', False)
        create_dataset(passfolder+"Processed/TFY", 'd', False)
        ##create_dataset(passfolder+"Detector/GE_Sensor_Temp", 'd', False)
        create_dataset(passfolder+"Scan/Mythen_FrameID", 'i', False)
        create_dataset(passfolder+"Scan/Timestamps", 'l', False)
        self.__create_pressure_dataset(passfolder = passfolder)
        #create_dataset(passfolder+"Pressure/Diagnostic_PV", 'd', False)
        #create_dataset(passfolder+"Pressure/Diagnostic_HV", 'd', False)
        #create_dataset(passfolder+"Pressure/Spectrometer_PV", 'd', False)
        #create_dataset(passfolder+"Pressure/Spectrometer_HV", 'd', False)
        #create_dataset(passfolder+"Pressure/Sample_Chamber", 'd', False)
        create_dataset(passfolder+"RAW/ring_current", 'd', False)
        if cont==False:
            create_dataset(passfolder+"RAW/SEC_el_x", 'd', False)
            create_dataset(passfolder+"RAW/SEC_el_y", 'd', False)
        if self.DEBUG: print("create scan dataset ok")

    def __ge_Create_Scan_Dataset_v3(self, cont=False, passes=1):
        if self.DEBUG: print("create scan dataset v3... ")
        create_dataset("Processed/GE_Spectrum_Sum", 'd', False, (passes, int(GE_BG_SizeX.take())))
        if self.DEBUG: print("create scan dataset ok ")

    def __mythen_Create_Scan_Dataset_v3(self, cont=False, passes=1):
        if self.DEBUG: print("create scan dataset v3... ")
        create_dataset("Processed/Mythen_Spectrum_Sum", 'd', False, (passes, 1280))
        if self.DEBUG: print("create scan dataset ok ")

    def __ge_Save_Scan_Data(self, cont=False):
        if self.DEBUG: print("save scan data ...")
        append_dataset("RAW/GE_Raw_Image", GE_Raw_Image.read())
        append_dataset("RAW/IZero_Profile", IZero_Profile.take())
        append_dataset("RAW/TFY_Profile", TFY_Profile.take())
        append_dataset("Processed/GE_ROI_Image", GE_ROI_Image.read())
        append_dataset("Processed/GE_Spectrum", GE_Spectrum.take())
        append_dataset("Processed/Izero", IZero.take())
        append_dataset("Processed/TFY", TFY.take())
        append_dataset("Detector/GE_Sensor_Temp", GE_Sensor_Temp.take())
        append_dataset("Scan/GE_FrameID", GE_FrameID.take())
        append_dataset("Scan/Timestamps", GE_FrameID.getTimestampNanos())
        self.__append_pressure_dataset(passfolder = "")
        #append_dataset("Pressure/Diagnostic_PV", Press_Diag_PV.take())
        #append_dataset("Pressure/Diagnostic_HV", Press_Diag_HV.take())
        #append_dataset("Pressure/Spectrometer_PV", Press_Spec_PV.take())
        #append_dataset("Pressure/Spectrometer_HV", Press_Spec_HV.take())
        #append_dataset("Pressure/Sample_Chamber", Press_Sample_Ch.take())
        if cont==False:
            append_dataset("RAW/SEC_el_x", SEC_el_x_Enc.take())
            append_dataset("RAW/SEC_el_y", SEC_el_y_Enc.take())
        append_dataset("RAW/ring_current", ring_current.take())
        if self.DEBUG: print("save scan data ok")

    def __mythen_Save_Scan_Data(self, cont=False):
        if self.DEBUG: print("save scan data ...")
        append_dataset("RAW/Mythen_Raw_Array", MythenRaw.read())
        append_dataset("RAW/IZero_Profile", IZero_Profile.take())
        append_dataset("RAW/TFY_Profile", TFY_Profile.take())
        ##append_dataset("Processed/GE_ROI_Image", GE_ROI_Image.read())
        ##append_dataset("Processed/GE_Spectrum", GE_Spectrum.take())
        append_dataset("Processed/Izero", IZero.take())
        append_dataset("Processed/TFY", TFY.take())
        ##append_dataset("Detector/GE_Sensor_Temp", GE_Sensor_Temp.take())
        append_dataset("Scan/Mythen_FrameID", MythenID.take())
        append_dataset("Scan/Timestamps", MythenID.getTimestampNanos())
        self.__append_pressure_dataset(passfolder = "")
        #append_dataset("Pressure/Diagnostic_PV", Press_Diag_PV.take())
        #append_dataset("Pressure/Diagnostic_HV", Press_Diag_HV.take())
        #append_dataset("Pressure/Spectrometer_PV", Press_Spec_PV.take())
        #append_dataset("Pressure/Spectrometer_HV", Press_Spec_HV.take())
        #append_dataset("Pressure/Sample_Chamber", Press_Sample_Ch.take())
        if cont==False:
            append_dataset("RAW/SEC_el_x", SEC_el_x_Enc.take())
            append_dataset("RAW/SEC_el_y", SEC_el_y_Enc.take())
        append_dataset("RAW/ring_current", ring_current.take())
        if self.DEBUG: print("save scan data ok")

    def __ge_Save_Scan_Data_v2(self, cont=False, passid=0):
        if self.DEBUG: print("save scan data v2 ...")
        passfolder = "pass_"+'{:03d}'.format(passid)+"/"
        append_dataset(passfolder+"RAW/GE_Raw_Image", GE_Raw_Image.read())
        append_dataset(passfolder+"RAW/IZero_Profile", IZero_Profile.take())
        append_dataset(passfolder+"RAW/TFY_Profile", TFY_Profile.take())
        append_dataset(passfolder+"Processed/GE_ROI_Image", GE_ROI_Image.read())
        append_dataset(passfolder+"Processed/GE_Spectrum", GE_Spectrum.take())
        append_dataset(passfolder+"Processed/Izero", IZero.take())
        append_dataset(passfolder+"Processed/TFY", TFY.take())
        append_dataset(passfolder+"Detector/GE_Sensor_Temp", GE_Sensor_Temp.take())
        append_dataset(passfolder+"Scan/GE_FrameID", GE_FrameID.take())
        append_dataset(passfolder+"Scan/Timestamps", GE_FrameID.getTimestampNanos())
        self.__append_pressure_dataset(passfolder = passfolder)
        #append_dataset(passfolder+"Pressure/Diagnostic_PV", Press_Diag_PV.take())
        #append_dataset(passfolder+"Pressure/Diagnostic_HV", Press_Diag_HV.take())
        #append_dataset(passfolder+"Pressure/Spectrometer_PV", Press_Spec_PV.take())
        #append_dataset(passfolder+"Pressure/Spectrometer_HV", Press_Spec_HV.take())
        #append_dataset(passfolder+"Pressure/Sample_Chamber", Press_Sample_Ch.take())
        if cont==False:
            append_dataset(passfolder+"RAW/SEC_el_x", SEC_el_x_Enc.take())
            append_dataset(passfolder+"RAW/SEC_el_y", SEC_el_y_Enc.take())
        append_dataset(passfolder+"RAW/ring_current", ring_current.take())
        if self.DEBUG: print("save scan data ok")

    def __mythen_Save_Scan_Data_v2(self, cont=False, passid=0):
        if self.DEBUG: print("save scan data v2 ...")
        passfolder = "pass_"+'{:03d}'.format(passid)+"/"
        append_dataset(passfolder+"RAW/Mythen_Raw_Array", MythenRaw.read())
        append_dataset(passfolder+"RAW/IZero_Profile", IZero_Profile.take())
        append_dataset(passfolder+"RAW/TFY_Profile", TFY_Profile.take())
        ##append_dataset(passfolder+"Processed/GE_ROI_Image", GE_ROI_Image.read())
        ##append_dataset(passfolder+"Processed/GE_Spectrum", GE_Spectrum.take())
        append_dataset(passfolder+"Processed/Izero", IZero.take())
        append_dataset(passfolder+"Processed/TFY", TFY.take())
        ##append_dataset(passfolder+"Detector/GE_Sensor_Temp", GE_Sensor_Temp.take())
        append_dataset(passfolder+"Scan/Mythen_FrameID", MythenID.take())
        append_dataset(passfolder+"Scan/Timestamps", MythenID.getTimestampNanos())
        self.__append_pressure_dataset(passfolder = passfolder)
        #append_dataset(passfolder+"Pressure/Diagnostic_PV", Press_Diag_PV.take())
        #append_dataset(passfolder+"Pressure/Diagnostic_HV", Press_Diag_HV.take())
        #append_dataset(passfolder+"Pressure/Spectrometer_PV", Press_Spec_PV.take())
        #append_dataset(passfolder+"Pressure/Spectrometer_HV", Press_Spec_HV.take())
        #append_dataset(passfolder+"Pressure/Sample_Chamber", Press_Sample_Ch.take())
        if cont==False:
            append_dataset(passfolder+"RAW/SEC_el_x", SEC_el_x_Enc.take())
            append_dataset(passfolder+"RAW/SEC_el_y", SEC_el_y_Enc.take())
        append_dataset(passfolder+"RAW/ring_current", ring_current.take())
        if self.DEBUG: print("save scan data ok")

    def __ge_Save_Pos_Scan_Data(self):
        if self.DEBUG: print("save pos scan data ...")
        save_dataset("Processed/GE_Spectrum_Sum", GE_Spectrum_Sum.read())
        save_dataset("Scan/Scan_Finish_Time", time.ctime())
        if self.DEBUG: print("save pos scan data ok")

    def __mythen_Save_Pos_Scan_Data(self):
        if self.DEBUG: print("save pos scan data ...")
        save_dataset("Processed/Mythen_Spectrum_Sum", MythenSpecSum.read())
        save_dataset("Scan/Scan_Finish_Time", time.ctime())
        if self.DEBUG: print("save pos scan data ok")

    def __ge_Save_Pos_Scan_Data_v2(self, passid=0):
        if self.DEBUG: print("save pos scan data v2 ...")
        passfolder = "pass_"+'{:03d}'.format(passid)+"/"
        save_dataset(passfolder+"Processed/GE_Spectrum_Sum", GE_Spectrum_Sum.read())
        save_dataset(passfolder+"Scan/Scan_Finish_Time", time.ctime())
        if self.DEBUG: print("save pos scan data ok")

    def __ge_Save_Pos_Scan_Data_v3(self, cont=False, passid=0):
        if self.DEBUG: print("save pos scan data v3 ...")
        passfolder = "pass_"+'{:03d}'.format(passid)+"/"
        save_dataset(passfolder+"Scan/Scan_Finish_Time", time.ctime())
        save_dataset(passfolder+"Processed/GE_Spectrum_Sum", GE_Spectrum_Sum.read())
        append_dataset("Processed/GE_Spectrum_Sum", GE_Spectrum_Sum.read())
        if cont==True:
            save_dataset(passfolder+"RAW/SEC_el_x0", self.x0_mdata)
            save_dataset(passfolder+"RAW/SEC_el_x1", self.x1_mdata)
            save_dataset(passfolder+"RAW/SEC_el_y0", self.y0_mdata)
            save_dataset(passfolder+"RAW/SEC_el_y1", self.y1_mdata)
            save_dataset(passfolder+"RAW/SEC_el_x", self.x_mdata)
            save_dataset(passfolder+"RAW/SEC_el_y", self.y_mdata)
        if self.DEBUG: print("save pos scan data ok")

    def __mythen_Save_Pos_Scan_Data_v3(self, cont=False, passid=0):
        if self.DEBUG: print("save pos scan data v3 ...")
        passfolder = "pass_"+'{:03d}'.format(passid)+"/"
        save_dataset(passfolder+"Scan/Scan_Finish_Time", time.ctime())
        save_dataset(passfolder+"Processed/Mythen_Spectrum_Sum", MythenSpecSum.read())
        append_dataset("Processed/Mythen_Spectrum_Sum", MythenSpecSum.read())
        if cont==True:
            save_dataset(passfolder+"RAW/SEC_el_x0", self.x0_mdata)
            save_dataset(passfolder+"RAW/SEC_el_x1", self.x1_mdata)
            save_dataset(passfolder+"RAW/SEC_el_y0", self.y0_mdata)
            save_dataset(passfolder+"RAW/SEC_el_y1", self.y1_mdata)
            save_dataset(passfolder+"RAW/SEC_el_x", self.x_mdata)
            save_dataset(passfolder+"RAW/SEC_el_y", self.y_mdata)
        if self.DEBUG: print("save pos scan data ok")

    def __ge_Save_Pos_Scan_Data_v4(self):
        if self.DEBUG: print("save pos scan data v4 ...")
        save_dataset("Scan/Scan_Finish_Time", time.ctime())
        if self.DEBUG: print("save pos scan data ok")

    def __ge_Save_Pos_Scan_Data_Continous(self):
        if self.DEBUG: print("save pos scan data for continous scan...")
        save_dataset("RAW/SEC_el_x0", self.x0_mdata)
        save_dataset("RAW/SEC_el_y0", self.y0_mdata)
        save_dataset("RAW/SEC_el_x1", self.x1_mdata)
        save_dataset("RAW/SEC_el_y1", self.y1_mdata)
        save_dataset("RAW/SEC_el_y_speed", self.cont_speed)
        if self.DEBUG: print("save pos scan data for continous scan ok")

    def __ge_Save_Pos_Scan_Data_Continous_v2(self):
        if self.DEBUG: print("save pos scan data for continous scan v2...")
        save_dataset("RAW/SEC_el_y_speed", self.cont_speed)
        if self.DEBUG: print("save pos scan data for continous scan ok")

    def _ge_spot_test(self, X0, Y0, exposure, scans):
        print ("X0: \t" + str(X0))
        print ("Y0: \t" + str(Y0))
        print ("expos: \t" + str(exposure))
        print ("scans: \t" + str(scans))

    def _jf_spot_test(self, X0, Y0, exposure, scans):
        print ("X0: \t" + str(X0))
        print ("Y0: \t" + str(Y0))
        print ("expos: \t" + str(exposure))
        print ("scans: \t" + str(scans))

    def _ge_energy_calibration(self, X0, Y0):
        print ("X0: \t" + str(X0))
        print ("Y0: \t" + str(Y0))

    def __publish_fname(self, fname=None):
        if fname==None:
            execinfo=get_exec_pars()
            filenameinfo=execinfo.path
            filenameinfo=filenameinfo.split("/")
            fname=filenameinfo[9]
        try:
            caput("PINK:AUX:ps_filename_RBV", fname)
        except:
            print("Failed to publish filename to epics")

    def _mytest(self):
        set_exec_pars(open=False, name="mytest", reset=True)
        #self.__ge_Save_Pre_Scan_Data(myscantype="Continuous")
        self.ge_Num_Images=4
        self.__ge_Create_Scan_Dataset_v2(cont=False, passid=0)
        for i in range(4):
            print("Dataset #" + str(i))
            self.__ge_Save_Scan_Data_v2(cont=False, passid=0)
            sleep(1)

    def _test_SEC_EL_limits(self, X0, Xstep, Xpoints, Y0, Ystep, Ypoints):
        outofrange = 0
        X1=X0+(Xpoints*Xstep)
        Y1=Y0+(Ypoints*Ystep)
        if( (Y0<SEC_el_y.getMinValue())or(Y1>SEC_el_y.getMaxValue()) ):
            print("Sample Vertical positions out of range:")
            print("Ymin Limit: " + str(SEC_el_y.getMinValue()))
            print("Ymax Limit: " + str(SEC_el_y.getMaxValue()))
            outofrange=1

        if( (X0<SEC_el_x.getMinValue())or(X1>SEC_el_x.getMaxValue()) ):
            print("Sample Horizontal positions out of range:")
            print("Xmin Limit: " + str(SEC_el_x.getMinValue()))
            print("Xmax Limit: " + str(SEC_el_x.getMaxValue()))
            outofrange=1
        return outofrange

    def __publish_status(self, message):
        set_status(message)
        AUX_status.write(message)

    def __save_specfile(self, passid):
        try:
            datafilepath = get_exec_pars().getPath()
            fpath = datafilepath.split("/")
            fpath = datafilepath.split(fpath[-1])
            fpath = fpath[0]+"mca"
            if os.path.isdir(fpath) == False:
                os.mkdir(fpath)
            specfname = datafilepath.split("/")[-1].split(".h5")[0]+".mca"
            specfname = fpath+"/"+specfname
            spectrum = GE_Spectrum_Sum.take()
            spectext = []
            spectext.append("#S "+'{:d}'.format(int(passid))+" pass"+'{:03d}'.format(int(passid))+'\n')
            spectext.append("#N 1\n")
            spectext.append("#L Counts\n")
            for ct in spectrum:
                spectext.append('{:d}'.format(int(ct))+'\n')
            spectext.append("\n")
            fspec = open(specfname, 'a+')
            for lines in spectext:
                fspec.write(lines)
            fspec.close()
        except:
            print("[Error]: Failed to create mca file")

    def __mythen_save_specfile(self, passid):
        try:
            datafilepath = get_exec_pars().getPath()
            fpath = datafilepath.split("/")
            fpath = datafilepath.split(fpath[-1])
            fpath = fpath[0]+"mca"
            if os.path.isdir(fpath) == False:
                os.mkdir(fpath)
            specfname = datafilepath.split("/")[-1].split(".h5")[0]+".mca"
            specfname = fpath+"/"+specfname
            spectrum = MythenSpecSum.take()
            spectext = []
            spectext.append("#S "+'{:d}'.format(int(passid))+" pass"+'{:03d}'.format(int(passid))+'\n')
            spectext.append("#N 1\n")
            spectext.append("#L Counts\n")
            for ct in spectrum:
                spectext.append('{:d}'.format(int(ct))+'\n')
            spectext.append("\n")
            fspec = open(specfname, 'a+')
            for lines in spectext:
                fspec.write(lines)
            fspec.close()
        except:
            print("[Error]: Failed to create mca file")

    def __continous_scan(self, exposure, passes, X0, deltaX, Xpoints, Y0, Y1, Ypoints, Yspeed, sample, ftype, linedelay):
        self.__publish_fname(fname=" ")
        caput("PINK:AUX:ps_sample", " ")
        GE_AreaDet.stop()
        self.__ge_setup_file("ge")
        self.__create_pressure_devices()
        self.__ge_setup_caenels1(exposure)
        self.__ge_setup_caenels2(exposure)
        self.__ge_setup_delaygen(1, [0, exposure], [0, 0.001], [0, 0.001], [0, 0])
        self.__ge_Save_Pre_Scan_Data_v2(scantype="Continuous")
        self.__ge_Create_Scan_Dataset_v3(cont=True, passes=passes)
        self.__ge_Arguments([exposure, X0, deltaX, Xpoints, Y0, Y1, Ypoints, Yspeed, passes, sample], ftype=ftype)
        self.__publish_fname()
        scan_done=False
        passid=0
        while not(scan_done):
            if self.DEBUG: print("Scan pass = " + str(passid))
            self.__eta_calc(exposure, Ypoints, Xpoints, (passes-passid), linedelay)
            self.__ge_save_background(exposure)
            self.__ge_setup_greateyes(exposure, self.line_images)
            self.__ge_init_progress()
            self.__ge_clean_spec_sum()
            self.__ge_Create_Scan_Dataset_v2(cont=True, passid=passid)
            self.__ge_Save_Pre_Scan_Data_v3(cont=True, passid=passid)
            self.__publish_status("Running continuous scan: " + "pass " + '{:d}'.format(passid+1) + "/" +  '{:d}'.format(passes))
            caput("PINK:AUX:ps_sample", sample)
            SEC_el_y.setSpeed(20000.0)
            SEC_el_x.move(X0)
            SEC_el_y.move(Y0)
            scan_dir=1
            self.x0_mdata = []
            self.y0_mdata = []
            self.x1_mdata = []
            self.y1_mdata = []
            self.x_mdata = []
            self.y_mdata = []
            try:
                for j in range(Xpoints):
                    SEC_el_x.move(X0+(j*deltaX))
                    if(scan_dir):
                        ydest=Y1
                    else:
                        ydest=Y0
                    SEC_el_y.setSpeed(Yspeed)
                    SEC_el_y.moveAsync(ydest)
                    GE_AreaDet.start()
                    for i in range(Ypoints):
                        self.x0_mdata.append(SEC_el_x.getPosition())
                        self.y0_mdata.append(SEC_el_y.getPosition())
                        self.x_mdata.append(SEC_el_x.getPosition())
                        self.y_mdata.append(SEC_el_y.getPosition())
                        self.__ge_start_frame_countdown()
                        GE_Raw_Array.waitCacheChange((int(math.ceil(exposure))*1000)+10000)
                        self.x1_mdata.append(SEC_el_x.getPosition())
                        self.y1_mdata.append(SEC_el_y.getPosition())
                        self.x_mdata.append(SEC_el_x.getPosition())
                        self.y_mdata.append(SEC_el_y.getPosition())
                        #add 10ms delay to make sure all new data have arrived
                        sleep(0.01)
                        self.__ge_Save_Scan_Data_v2(cont=True, passid=passid)
                        self.__ge_calc_progress()
                    SEC_el_y.stop()
                    SEC_el_y.setSpeed(20000)
                    self.__sec_el_y_safemove(ydest)
                    scan_dir=abs(scan_dir-1)
                    sleep(linedelay)
            except Exception, ex1:
                print("Script Aborted:")
                print(ex1)
                self.__publish_status("Script aborted")
                GE_AreaDet.stop()
                SEC_el_y.setSpeed(20000)
            self.__ge_Save_Pos_Scan_Data_v3(cont=True, passid=passid)
            self.__save_specfile(passid)
            passid=passid+1
            if passid==passes: scan_done=True
        self.__ge_Save_Pos_Scan_Data_v4()
        self.__ge_Save_Pos_Scan_Data_Continous_v2()
        pink_save_bl_snapshot()
        self.__remove_pressure_devices()
        print("Scan complete")
        self.__publish_status("Scan complete")

    def __mythen_continous_scan(self, exposure, passes, X0, deltaX, Xpoints, Y0, Y1, Ypoints, Yspeed, sample, ftype, linedelay):
        dev.mythen_create()
        self.__publish_fname(fname=" ")
        caput("PINK:AUX:ps_sample", " ")
        ##GE_AreaDet.stop()
        while(MythenAcq.read()>0):
            MythenAcq.write(0)
            MythenAcq.waitValue(0.0, 60000)
        self.__ge_setup_file("mythen")
        self.__create_pressure_devices()
        self.__ge_setup_caenels1(exposure)
        self.__ge_setup_caenels2(exposure)
        self.__ge_setup_delaygen(1, [0, (exposure+0.002)*Ypoints], [0, 0.001], [0, 0.001], [0, 0])
        self.__mythen_Save_Pre_Scan_Data_v2(scantype="Continuous")
        self.__mythen_Create_Scan_Dataset_v3(cont=True, passes=passes)
        self.__mythen_Arguments([exposure, X0, deltaX, Xpoints, Y0, Y1, Ypoints, Yspeed, passes, sample], ftype=ftype)
        self.__publish_fname()
        scan_done=False
        passid=0
        while not(scan_done):
            if self.DEBUG: print("Scan pass = " + str(passid))
            self.__mythen_eta_calc(exposure, Ypoints, Xpoints, (passes-passid), linedelay)
            ##self.__ge_save_background(exposure)
            ##self.__ge_setup_greateyes(exposure, self.line_images)
            self.__mythen_setup(exposure, self.line_images, 1, 0)
            self.__mythen_init_progress()
            self.__mythen_clean_spec_sum()
            self.__mythen_Create_Scan_Dataset_v2(cont=True, passid=passid)
            self.__mythen_Save_Pre_Scan_Data_v3(cont=True, passid=passid)
            self.__publish_status("Running continuous scan: " + "pass " + '{:d}'.format(passid+1) + "/" +  '{:d}'.format(passes))
            caput("PINK:AUX:ps_sample", sample)
            SEC_el_y.setSpeed(20000.0)
            SEC_el_x.move(X0)
            SEC_el_y.move(Y0)
            scan_dir=1
            self.x0_mdata = []
            self.y0_mdata = []
            self.x1_mdata = []
            self.y1_mdata = []
            self.x_mdata = []
            self.y_mdata = []
            try:
                for j in range(Xpoints):
                    SEC_el_x.move(X0+(j*deltaX))
                    if(scan_dir):
                        ydest=Y1
                    else:
                        ydest=Y0
                    SEC_el_y.setSpeed(Yspeed)
                    SEC_el_y.moveAsync(ydest)
                    ##GE_AreaDet.start()
                    MythenAcq.write(1)
                    for i in range(Ypoints):
                        self.x0_mdata.append(SEC_el_x.getPosition())
                        self.y0_mdata.append(SEC_el_y.getPosition())
                        self.x_mdata.append(SEC_el_x.getPosition())
                        self.y_mdata.append(SEC_el_y.getPosition())
                        self.__ge_start_frame_countdown()
                        MythenSpecSum.waitCacheChange((int(math.ceil(exposure))*1000)+10000)
                        self.x1_mdata.append(SEC_el_x.getPosition())
                        self.y1_mdata.append(SEC_el_y.getPosition())
                        self.x_mdata.append(SEC_el_x.getPosition())
                        self.y_mdata.append(SEC_el_y.getPosition())
                        #add 10ms delay to make sure all new data have arrived
                        sleep(0.10)
                        self.__mythen_Save_Scan_Data_v2(cont=True, passid=passid)
                        self.__mythen_calc_progress()
                    SEC_el_y.stop()
                    SEC_el_y.setSpeed(20000)
                    self.__sec_el_y_safemove(ydest)
                    scan_dir=abs(scan_dir-1)
                    sleep(exposure+linedelay)
            except Exception, ex1:
                print("Script Aborted:")
                print(ex1)
                self.__publish_status("Script aborted")
                ##GE_AreaDet.stop()
                MythenAcq.write(0)
                SEC_el_y.setSpeed(20000)
            self.__mythen_Save_Pos_Scan_Data_v3(cont=True, passid=passid)
            self.__mythen_save_specfile(passid)
            passid=passid+1
            if passid==passes: scan_done=True
        self.__ge_Save_Pos_Scan_Data_v4()
        self.__ge_Save_Pos_Scan_Data_Continous_v2()
        pink_save_bl_snapshot()
        self.__remove_pressure_devices()
        dev.mythen_remove()
        print("Scan complete")
        self.__publish_status("Scan complete")


    def __create_pressure_devices(self):
        import config.pressure_list_config as plist
        pressure_pvlist = plist.pressure_pvlist
        if self.DEBUGLOG: log("Pressure: Creating pressure devices...", data_file=False)
        for pvr in pressure_pvlist:
            devicename = "PT"+pvr[0]
            add_device(ch.psi.pshell.epics.ChannelDouble(devicename, pvr[1]), True)
            execcmd = devicename+".setMonitored(True)"
            exec(execcmd)
            devicename = "PT"+pvr[0]+"Desc"
            pvnamedesc = pvr[1]+".DESC"
            add_device(ch.psi.pshell.epics.ChannelString(devicename, pvnamedesc), True)
            execcmd = devicename+".update()"
            exec(execcmd)
        if self.DEBUGLOG: log("Pressure: pressure devices OK", data_file=False)

    def __remove_pressure_devices(self):
        import config.pressure_list_config as plist
        pressure_pvlist = plist.pressure_pvlist
        if self.DEBUGLOG: log("Pressure: Removing pressure devices...", data_file=False)
        for pvr in pressure_pvlist:
            devicename = "PT"+pvr[0]
            execcmd = "remove_device("+devicename+")"
            exec(execcmd)
            devicename = "PT"+pvr[0]+"Desc"
            execcmd = "remove_device("+devicename+")"
            exec(execcmd)
        if self.DEBUGLOG: log("Pressure: devices removed OK", data_file=False)

    def __create_pressure_dataset(self, passfolder = ""):
        for pvr in self.pressure_pvlist:
            devicenamedesc = "PT"+pvr[0]+"Desc"
            datasetpath = passfolder+"Pressure/"+pvr[0]
            execcmd = "pvdesc = "+devicenamedesc+".take()"
            exec(execcmd)
            create_dataset(datasetpath, 'd', False)
            set_attribute(datasetpath, "DESC", pvdesc)

    def __append_pressure_dataset(self, passfolder = ""):
        for pvr in self.pressure_pvlist:
            devicename = "PT"+pvr[0]
            datasetpath = passfolder+"Pressure/"+pvr[0]
            execcmd = "pvtempval = "+devicename+".take()"
            exec(execcmd)
            append_dataset(datasetpath, pvtempval)

    def __eta_calc(self, exposure, Ypoints, Xpoints, passes, linedelay):
        bgtime = 2.881 + exposure*1.087
        linetime = (Ypoints*(exposure+0.35))+1.7+linedelay
        passtime = (Xpoints * linetime) + bgtime
        scantime = passes*passtime
        tnow = time.time()
        passETA = time.ctime(tnow + passtime)
        scanETA = time.ctime(tnow + scantime)
        caput("PINK:AUX:pass_eta", passETA)
        caput("PINK:AUX:scan_eta", scanETA)

    def __mythen_eta_calc(self, exposure, Ypoints, Xpoints, passes, linedelay):
        ##bgtime = 2.881 + exposure*1.087
        bgtime = 0
        linetime = (Ypoints*(exposure))+1.7+linedelay
        passtime = (Xpoints * linetime) + bgtime
        scantime = passes*passtime
        tnow = time.time()
        passETA = time.ctime(tnow + passtime)
        scanETA = time.ctime(tnow + scantime)
        caput("PINK:AUX:pass_eta", passETA)
        caput("PINK:AUX:scan_eta", scanETA)

    ##############################################################################
    ### GAP Scan functions
    ##############################################################################

    def gap_without_fitting(self, start, end, step, wait=0):
        def BeforeReadout():
            prec=0.005
            lwait=1
            caput("U17IT6R:BaseCmdCalc.PROC", 1)
            WDog = 0
            err_old=abs(U17_Gap_RBV.take()- U17_Gap_Set.take())
            while(lwait):
                err=abs(U17_Gap_RBV.take()- U17_Gap_Set.take())
                if (err<=prec) & (U17_Gap_Status.take()==1):
                    lwait=0
                sleep(0.25)
                WDog = WDog+1
                if (WDog%8==0):
                    if err_old-err == 0:
                        print("Undulator seems to be not moving after 2 seconds")
                    err_old = err
                set_status("Gap: " + str(U17_Gap_RBV.take()))
            sleep(wait)

        if self.__undulator_locked():
            print("Undulator U17 is locked!")
            return

        self.__reinit_hzb_pvs()

        print("Running undulator gap scan ...")
        self.__setup_file(fname="gap")
        self.__reset_extra_data()
        res = lscan(U17_Gap_Set, [Diode_sum, U17_Gap_RBV], start, end, step, enabled_plots=[Diode_sum], before_read=BeforeReadout, after_read=gap_upd_scan_data)
        pink_save_bl_snapshot()
        print("OK")

    def gap_with_Linear_Background(self, start, end, step, wait=0):
        def BeforeReadout():
            prec=0.005
            lwait=1
            caput("U17IT6R:BaseCmdCalc.PROC", 1)
            WDog = 0
            err_old=abs(U17_Gap_RBV.take()- U17_Gap_Set.take())
            while(lwait):
                err=abs(U17_Gap_RBV.take()- U17_Gap_Set.take())
                if (err<=prec) & (U17_Gap_Status.take()==1):
                    lwait=0
                sleep(0.25)
                WDog = WDog+1
                if (WDog%8==0):
                    if err_old-err == 0:
                        print("Undulator seems to be not moving after 2 seconds")
                    err_old = err
                set_status("Gap: " + str(U17_Gap_RBV.take()))
            sleep(wait)
        if self.__undulator_locked():
            print("Undulator U17 is locked!")
            return

        self.__reinit_hzb_pvs()

        print("Running undulator gap scan with linear background analysis...")
        self.__setup_file(fname="gap")
        self.__reset_extra_data()
        res = lscan(U17_Gap_Set, [Diode_sum, U17_Gap_RBV], start, end, step, enabled_plots=[Diode_sum], before_read=BeforeReadout, after_read=gap_upd_scan_data)
        #xdata = res.getPositions(0)
        #xdata = res.getReadable(1)
        #ydata = res.getReadable(0)
        xdata = self.gappos
        ydata = self.diode_sum
        self.xdata = xdata
        self.ydata = ydata
        print("Analysing...")
        (incl, off, amp, com, sigma, gauss, fwhm, xgauss) = self.__gauss_lin_fit(ydata, xdata)
        self.__print_lin_info(incl, off, amp, com, sigma, fwhm)
        self.__plot_curves(xdata, ydata, gauss, xgauss, title="Gap Scan with linear background")
        self.__save_data_lin(incl, off, amp, com, sigma, fwhm, gauss, xgauss)
        pink_save_bl_snapshot()
        print("OK")

    def gap_with_Exponential_Background(self, start, end, step, wait=0):
        def BeforeReadout():
            prec=0.005
            lwait=1
            caput("U17IT6R:BaseCmdCalc.PROC", 1)
            ##caput("PINK:GAPSIM:gapexec.PROC", 1)
            WDog = 0
            err_old=abs(U17_Gap_RBV.take()- U17_Gap_Set.take())
            ##err_old=abs(U17_Gap_RBV_SIM.take()- U17_Gap_Set_SIM.take())
            while(lwait):
                err=abs(U17_Gap_RBV.take()- U17_Gap_Set.take())
                ##err=abs(U17_Gap_RBV_SIM.take()- U17_Gap_Set_SIM.take())
                if (err<=prec) & (U17_Gap_Status.take()==1):
                ##if (err<=prec) & (U17_Gap_Status_SIM.take()==1):
                    lwait=0
                sleep(0.25)
                WDog = WDog+1
                if (WDog%8==0):
                    if err_old-err == 0:
                        print("Undulator seems to be not moving after 2 seconds")
                    err_old = err
                set_status("Gap: " + str(U17_Gap_RBV.take()))
                ##set_status("Gap: " + str(U17_Gap_RBV_SIM.take()))
            sleep(wait)
        if self.__undulator_locked():
            print("Undulator U17 is locked!")
            return

        self.__reinit_hzb_pvs()

        print("Running undulator gap scan with exponential background analysis...")
        self.__setup_file(fname="gap")
        self.__reset_extra_data()
        res = lscan(U17_Gap_Set, [Diode_sum, U17_Gap_RBV], start, end, step, enabled_plots=[Diode_sum], before_read=BeforeReadout, after_read=gap_upd_scan_data)
        ##res = lscan(U17_Gap_Set_SIM, [Diode_sum_SIM, U17_Gap_RBV_SIM], start, end, step, enabled_plots=[Diode_sum_SIM], before_read=BeforeReadout, after_read=gap_upd_scan_data)
        xdata = self.gappos
        ydata = self.diode_sum
        self.xdata = xdata
        self.ydata = ydata
        print("Analysing...")
        (eamp, decay, amp, com, sigma, gauss, fwhm, xgauss) = self.__gauss_exp_fit(ydata, xdata)
        self.__print_exp_info(eamp, decay, amp, com, sigma, fwhm)
        self.__gap_plot_curves(xdata, ydata, gauss, xgauss, title="Gap scan with exponential background")
        self.__save_data_exp(eamp, decay, amp, com, sigma, fwhm, gauss, xgauss)
        pink_save_bl_snapshot()
        print("OK")

    def __gauss_lin_fit(self, ydata, xdata):
        (incl, off, amp, com, sigma) = fit_gaussian_linear(ydata, xdata)
        f = Gaussian(amp, com, sigma)
        xgauss = frange(min(xdata),max(xdata),math.fabs((max(xdata)-min(xdata))/200))
        gauss = [f.value(i) + incl*i+off for i in xgauss]
        fwhm = self.sig2fwmh*sigma
        return (incl, off, amp, com, sigma, gauss, fwhm, xgauss)

    def __gauss_exp_fit(self, ydata, xdata):
        (incl, off, amp, com, sigma) = fit_gaussian_linear(ydata, xdata)
        start_point=[1, 1, amp, com, sigma]
        (eamp, decay, amp, com, sigma) = fit_gaussian_exp_bkg(ydata, xdata, start_point=start_point)
        f = Gaussian(amp, com, sigma)
        xgauss = frange(min(xdata),max(xdata),math.fabs((max(xdata)-min(xdata))/200))
        gauss = [f.value(i) + eamp*math.exp(-i/decay) for i in xgauss]
        fwhm = self.sig2fwmh*sigma
        return (eamp, decay, amp, com, sigma, gauss, fwhm, xgauss)

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

    def __gap_plot_curves(self, xdata, ydata, gauss, xgauss, title="myplot"):
        p1=plot(None, "Diodes", title="Gap Scan")[0]
        p1.setLegendVisible(True)
        p1.setTitle(title)
        p1.addSeries(LinePlotSeries("Fit"))
        p1.getSeries(0).setData(xdata, ydata)
        p1.getSeries(1).setData(xgauss, gauss)

    def __setup_file(self, fname="gap_scan"):
        set_exec_pars(open=False, name=fname, reset=True)

    def __reset_extra_data(self):
        self.diode1 = []
        self.diode2 = []
        self.diode3 = []
        self.diode4 = []
        self.diode_sum = []
        self.gappos = []

    def _extra_scan_data(self):
        self.diode1.append(Diode_1.take())
        self.diode2.append(Diode_2.take())
        self.diode3.append(Diode_3.take())
        self.diode4.append(Diode_4.take())
        self.diode_sum.append(Diode_sum.take())
        ##self.diode_sum.append(Diode_sum_SIM.take())
        self.tfy.append(TFY.take())
        self.gappos.append(U17_Gap_RBV.take())
        ##self.gappos.append(U17_Gap_RBV_SIM.take())

    def __save_data_lin(self, incl, off, amp, com, sigma, fwhm, gauss, xgauss):
        save_dataset("gaussian/inclination", incl)
        save_dataset("gaussian/offset", off)
        save_dataset("gaussian/amplitude", amp)
        save_dataset("gaussian/mean", com)
        save_dataset("gaussian/sigma", sigma)
        save_dataset("gaussian/FWHM", fwhm)
        save_dataset("gaussian/gauss_fit", gauss)
        save_dataset("gaussian/gauss_fit_xaxis", xgauss)
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

    ###########################################################################
    ### Blade Scan functions
    ###########################################################################

    def blade_DiC(self, start, end, steps, latency=0.0):
        print("Running ...")
        self.__setup_file(fname="blade_diag")
        self.__reset_extra_data()
        self.__blade_setup_caenels2(Exp_Time=0.5, Enable=True)
        res = lscan(Filter1, Diode_sum, start, end, steps, latency, after_read=blade_upd_scan_data)
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

    def blade_SEC_el(self, start, end, steps, latency=0.0):
        print("Running ...")
        self.__setup_file(fname="blade_sample")
        self.__reset_extra_data()
        self.__blade_setup_caenels1(Exp_Time=0.5, Enable=True)
        #res = lscan(Filter2, Filter2_SIG, start, end, steps, interval, after_read=blade_upd_scan_data)
        res = lscan(SEC_el_y, TFY, start, end, steps, latency, after_read=blade_upd_scan_data)
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


    def __blade_setup_caenels1(self, Exp_Time=0.5, Enable=True):
        cae_exp_time=float(Exp_Time)
        caputq("PINK:CAE1:Acquire", 0)
        caput("PINK:CAE1:ValuesPerRead", int(1000*cae_exp_time))
        caput("PINK:CAE1:AveragingTime", float(cae_exp_time))
        caput("PINK:CAE1:TriggerMode", 0)
        if Enable:
            caputq("PINK:CAE1:Acquire", 1)
        else:
            caputq("PINK:CAE1:Acquire", 0)

    def __blade_setup_caenels2(self, Exp_Time=0.5, Enable=True):
        cae_exp_time=float(Exp_Time)
        caputq("PINK:CAE2:Acquire", 0)
        caput("PINK:CAE2:ValuesPerRead", int(1000*cae_exp_time))
        caput("PINK:CAE2:AveragingTime", float(cae_exp_time))
        caput("PINK:CAE2:TriggerMode", 0)
        if Enable:
            caputq("PINK:CAE2:Acquire", 1)
        else:
            caputq("PINK:CAE2:Acquire", 0)
