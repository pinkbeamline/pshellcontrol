class PINKCLASS():
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
        self.__ge_setup_caenels1(exposure)
        self.__ge_setup_caenels2(exposure)
        self.__publish_fname(fname=" ")
        self.__ge_save_background(exposure)
        self.__ge_setup_greateyes(exposure, self.line_images)
        self.__ge_init_progress()
        self.__ge_clean_spec_sum()
        self.__ge_Create_Scan_Dataset()
        self.__ge_Save_Pre_Scan_Data(scantype="Spot")
        self.__ge_Arguments([exposure, images, sample], ftype=1)
        self.__publish_fname()
        self.__publish_status("Running spot scan...")
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
        print("Scan complete")
        self.__publish_status("Scan complete")

    #### LINE SCAN          ############################################################
    def ge_SEC_EL_line_vert(self, exposure, Y0, deltaY, Ypoints, passes=1, sample=" "):
        self.ge_exptime=exposure
        self.sample=sample
        start=float(Y0)
        step=float(deltaY)
        #images=int(Ypoints)
        self.line_images=Ypoints
        self.scan_images=Ypoints
        self.total_images=Ypoints*passes
        self.ge_Num_Images=Ypoints
        self.ge_Num_Images_total=Ypoints*passes
        self.__publish_fname(fname=" ")
        GE_AreaDet.stop()
        self.__ge_setup_file("ge")
        self.__ge_setup_caenels1(exposure)
        self.__ge_setup_caenels2(exposure)
        #self.__ge_setup_greateyes_sw_sync(exposure, images)
        self.__ge_Save_Pre_Scan_Data_v2(scantype="Line")
        self.__ge_Create_Scan_Dataset_v3(cont=False, passes=passes)
        self.__ge_Arguments([exposure, Y0, deltaY, Ypoints, passes, sample], ftype=2)
        self.__publish_fname()
        scan_done=False
        passid=0
        while not(scan_done):
            if self.DEBUG: print("Scan pass = " + str(passid))
            self.__ge_save_background(exposure)
            self.__ge_setup_greateyes_sw_sync(exposure, self.line_images)
            self.__ge_init_progress()
            self.__ge_clean_spec_sum()
            self.__ge_Create_Scan_Dataset_v2(cont=False, passid=passid)
            self.__ge_Save_Pre_Scan_Data_v3(cont=False, passid=passid)
            self.__publish_status("line scan: " + "pass " + '{:d}'.format(passid+1) + "/" + '{:d}'.format(passes) + " (" + sample + ")")
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
        print("Scan complete")
        self.__publish_status("Scan complete")

    #### ZIGZAG SCAN        ############################################################
    def ge_SEC_EL_zigzag(self, exposure, X0, deltaX, Xpoints, Y0, deltaY, Ypoints, passes=1, sample=" ", linedelay=0):
        images=int(Xpoints*Ypoints)
        self.ge_Num_Images=images
        self.ge_Num_Images_total=int(images*passes)
        self.ge_exptime=exposure
        self.sample=sample
        #Test sample manipulator limits
        if self._test_SEC_EL_limits(X0, deltaX, Xpoints, Y0, deltaY, Ypoints): sys.exit()
        X0=float(X0)
        Xstep=float(deltaX)
        Y0=float(Y0)
        Ystep=float(deltaY)
        self.__publish_fname(fname=" ")
        GE_AreaDet.stop()
        self.__ge_setup_file("ge")
        self.__ge_setup_caenels1(exposure)
        self.__ge_setup_caenels2(exposure)
        self.__ge_setup_greateyes_sw_sync(exposure, images)
        self.__ge_Save_Pre_Scan_Data_v2(scantype="Zigzag")
        self.__ge_Create_Scan_Dataset_v3(cont=False, passes=passes)
        self.__ge_Arguments([exposure, X0, deltaX, Xpoints, Y0, deltaY, Ypoints, passes, sample], ftype=3)
        self.__publish_fname()
        scan_done=False
        passid=0
        while not(scan_done):
            if self.DEBUG: print("Scan pass = " + str(passid))
            self.__ge_save_background(exposure)
            self.__ge_setup_greateyes_sw_sync(exposure, images)
            self.__ge_init_progress()
            self.__ge_clean_spec_sum()
            self.__ge_Create_Scan_Dataset_v2(cont=False, passid=passid)
            self.__ge_Save_Pre_Scan_Data_v3(cont=False, passid=passid)
            self.__publish_status("zigzag scan: " + "pass " + '{:d}'.format(passid+1) + "/" +  '{:d}'.format(passes) + " (" + sample + ")")
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
        print("Scan complete")
        self.__publish_status("Scan complete")

   #### CONT SCAN EXPOSURE + SPEED optimized  ###########################################################################
    def ge_SEC_EL_continous_exposure_speed(self, exposure, X0, deltaX, Xpoints, Y0, Y1, Yspeed, passes=1, sample=" ", linedelay=0):
        readout_time=0.4
        yspeed = abs(round(Yspeed))
        self.cont_speed = yspeed
        Ypoints = int(math.floor(abs(Y1-Y0)/(yspeed*(exposure+readout_time))))
        print("Scan calculated Ypoints: " + str(Ypoints))
        self.line_images=Ypoints
        self.scan_images=Ypoints*Xpoints
        self.total_images=Ypoints*Xpoints*passes
        #images=int(Ypoints*Xpoints)
        #self.ge_Num_Images=images
        #self.ge_Num_Images_total=int(images*passes)
        self.ge_exptime=exposure
        self.sample=sample
        X0=float(X0)
        Xstep=float(deltaX)
        Y0=float(Y0)
        Y1=float(Y1)
        self.__publish_fname(fname=" ")
        GE_AreaDet.stop()
        self.__ge_setup_file("ge")
        self.__ge_setup_caenels1(exposure)
        self.__ge_setup_caenels2(exposure)
        #self.__ge_setup_greateyes_sw_sync(exposure, self.line_images)
        self.__ge_Save_Pre_Scan_Data_v2(scantype="Continuous")
        self.__ge_Create_Scan_Dataset_v3(cont=True, passes=passes)
        self.__ge_Arguments([exposure, X0, deltaX, Xpoints, Y0, Y1, Yspeed, passes, sample], ftype=4)
        self.__publish_fname()
        scan_done=False
        passid=0
        while not(scan_done):
            if self.DEBUG: print("Scan pass = " + str(passid))
            self.__ge_save_background(exposure)
            self.__ge_setup_greateyes(exposure, self.line_images)
            self.__ge_init_progress()
            self.__ge_clean_spec_sum()
            self.__ge_Create_Scan_Dataset_v2(cont=True, passid=passid)
            self.__ge_Save_Pre_Scan_Data_v3(cont=True, passid=passid)
            self.__publish_status("continuous scan: " + "pass " + '{:d}'.format(passid+1) + "/" +  '{:d}'.format(passes) + " (" + sample + ")")
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
                    SEC_el_y.setSpeed(yspeed)
                    SEC_el_y.moveAsync(ydest)
                    GE_AreaDet.start()
                    for i in range(Ypoints):
                        self.x0_mdata.append(SEC_el_x.getPosition())
                        self.y0_mdata.append(SEC_el_y.getPosition())
                        self.x_mdata.append(SEC_el_x.getPosition())
                        self.y_mdata.append(SEC_el_y.getPosition())
                        self.__ge_start_frame_countdown()
                        GE_Raw_Array.waitCacheChange((exposure*1000)+10000)
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
        print("Scan complete")
        self.__publish_status("Scan complete")

    #### CONT SCAN POINTS + SPEED optimized    ###########################################################################
    def ge_SEC_EL_continous_points_speed(self, X0, deltaX, Xpoints, Y0, Y1, Ypoints, Yspeed, passes=1, sample=" ", linedelay=0):
        readout_time=0.4
        yspeed = abs(round(Yspeed))
        self.cont_speed = yspeed
        exposure = (float(abs(Y1-Y0))/(Ypoints*Yspeed))-readout_time
        print("Greateyes set exposure: " + '{:.3f}'.format(exposure) + " seconds")
        #images=int(Xpoints*Ypoints)
        self.line_images=Ypoints
        self.scan_images=Ypoints*Xpoints
        self.total_images=Ypoints*Xpoints*passes
        #self.ge_Num_Images=images
        #self.ge_Num_Images_total=int(images*passes)
        self.ge_exptime=exposure
        self.sample=sample
        X0=float(X0)
        Xstep=float(deltaX)
        Y0=float(Y0)
        Y1=float(Y1)
        self.__publish_fname(fname=" ")
        GE_AreaDet.stop()
        self.__ge_setup_file("ge")
        self.__ge_setup_caenels1(exposure)
        self.__ge_setup_caenels2(exposure)
        #self.__ge_setup_greateyes_sw_sync(exposure, images)
        self.__ge_Save_Pre_Scan_Data_v2(scantype="Continuous")
        self.__ge_Create_Scan_Dataset_v3(cont=True, passes=passes)
        self.__ge_Arguments([X0, deltaX, Xpoints, Y0, Y1, Ypoints, Yspeed, passes, sample], ftype=5)
        self.__publish_fname()
        scan_done=False
        passid=0
        while not(scan_done):
            if self.DEBUG: print("Scan pass = " + str(passid))
            self.__ge_save_background(exposure)
            self.__ge_setup_greateyes(exposure, self.line_images)
            self.__ge_init_progress()
            self.__ge_clean_spec_sum()
            self.__ge_Create_Scan_Dataset_v2(cont=True, passid=passid)
            self.__ge_Save_Pre_Scan_Data_v3(cont=True, passid=passid)
            self.__publish_status("continuous scan: " + "pass " + '{:d}'.format(passid+1) + "/" +  '{:d}'.format(passes) + " (" + sample + ")")
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
                    SEC_el_y.setSpeed(yspeed)
                    SEC_el_y.moveAsync(ydest)
                    GE_AreaDet.start()
                    for i in range(Ypoints):
                        self.x0_mdata.append(SEC_el_x.getPosition())
                        self.y0_mdata.append(SEC_el_y.getPosition())
                        self.x_mdata.append(SEC_el_x.getPosition())
                        self.y_mdata.append(SEC_el_y.getPosition())
                        self.__ge_start_frame_countdown()
                        #GE_AreaDet.start()
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
        print("Scan complete")
        self.__publish_status("Scan complete")

    #### CONT SCAN EXPOSURE + POINTS optimized    ###########################################################################
    def ge_SEC_EL_continous_exposure_points(self, exposure, X0, deltaX, Xpoints, Y0, Y1, Ypoints, passes=1, sample=" ", linedelay=0):
        readout_time=0.4
        self.line_images=Ypoints
        self.scan_images=Ypoints*Xpoints
        self.total_images=Ypoints*Xpoints*passes
        #images=int(Xpoints*Ypoints)
        #self.ge_Num_Images=images
        self.ge_exptime=exposure
        self.sample=sample
        X0=float(X0)
        Xstep=float(deltaX)
        Y0=float(Y0)
        Y1=float(Y1)
        totaltime = Ypoints*(exposure+readout_time)
        yspeed = abs(int((Y1-Y0)/totaltime))
        self.cont_speed = yspeed
        print("Sample calculated speed: " + str(yspeed) + " um/sec")
        self.__publish_fname(fname=" ")
        GE_AreaDet.stop()
        self.__ge_setup_file("ge")
        self.__ge_setup_caenels1(exposure)
        self.__ge_setup_caenels2(exposure)
        #self.__ge_setup_greateyes_sw_sync(exposure, images)
        self.__ge_Save_Pre_Scan_Data_v2(scantype="Continuous")
        self.__ge_Create_Scan_Dataset_v3(cont=True, passes=passes)
        self.__ge_Arguments([exposure, X0, deltaX, Xpoints, Y0, Y1, Ypoints, passes, sample], ftype=6)
        self.__publish_fname()
        scan_done=False
        passid=0
        while not(scan_done):
            if self.DEBUG: print("Scan pass = " + str(passid))
            self.__ge_save_background(exposure)
            self.__ge_setup_greateyes(exposure, self.line_images)
            self.__ge_init_progress()
            self.__ge_clean_spec_sum()
            self.__ge_Create_Scan_Dataset_v2(cont=True, passid=passid)
            self.__ge_Save_Pre_Scan_Data_v3(cont=True, passid=passid)
            self.__publish_status("continuous scan: " + "pass " + '{:d}'.format(passid+1) + "/" +  '{:d}'.format(passes) + " (" + sample + ")")
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
                    SEC_el_y.setSpeed(yspeed)
                    SEC_el_y.moveAsync(ydest)
                    for i in range(Ypoints):
                        self.x0_mdata.append(SEC_el_x.getPosition())
                        self.y0_mdata.append(SEC_el_y.getPosition())
                        self.x_mdata.append(SEC_el_x.getPosition())
                        self.y_mdata.append(SEC_el_y.getPosition())
                        self.__ge_start_frame_countdown()
                        GE_AreaDet.start()
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
        print("Scan complete")
        self.__publish_status("Scan complete")

    #### HELP INFORMATION   ############################################################
    def help(self):
        #print("***      DEVELOPMENT VERSION       ***")
        print("*** Pink Beamline list of scripts: ***")
        print("All custom functions can be found by typing:")
        print("pink.")
        print("bpm.")
        print("blade.")
        print("gap.\n\n")

    #### SAVE BL SNAPSHOT   ############################################################
    def save_Beamline_Snapshot(self):
        set_exec_pars(open=False, name="pink_bl", reset=True)
        pink_save_bl_snapshot()
        print("Pink beamline snapshot saved")

    #### Send SMS Function   ############################################################
    def send_SMS(self, phonenr=None, message=None):
        if (phonenr==None) or (message==None):
            print("Invalid. \nExample: pink.Send_SMS(\"+4901231234567\", \"My message with less than 40 characters\")")
        else:
            try:
                caput("PINK:GSM:smsnumber", phonenr)
                caput("PINK:GSM:smsmsg", message)
                caput("PINK:GSM:sendsms.PROC", 1)
            except:
                print("Error: [SMS]:Could not send SMS")


    #### Open hard shutter  ############################################################
    def shutter_hard_OPEN(self):
        for i in range(3):
            shutter_status = caget("PSHY01U012L:State1", 'd')
            if shutter_status == 14:
                return True
            else:
                caputq("PSHY01U012L:SetTa", 1)
                sleep(3)
        print("Failed to open Shutter Hard")
        log("Failed to open Shutter Hard")
        return False

    #### Close hard shutter  ############################################################
    def shutter_hard_CLOSE(self):
        for i in range(3):
            shutter_status = caget("PSHY01U012L:State1", 'd')
            if shutter_status == 5 or shutter_status == 1:
                return True
            else:
                caputq("PSHY01U012L:SetTa", 1)
                sleep(3)
        print("Failed to close Shutter Hard")
        log("Failed to close Shutter Hard")
        return False

    #### Setup Pink Beamline  ############################################################
    def __pvwait(self, pvname, value, deadband=0, timeout=300):
        cdown=timeout
        while cdown>=0:
            val = caget(pvname)
            if (val>=value-abs(deadband)) and (val<=value+abs(deadband)):
                return
            cdown=cdown-1
            sleep(1)
        print("Timeout (" + str(timeout) + " seconds) waiting for PV: " + pvname) 

    def setup_pink(self):
    #Set PV, value, Monitor PV, deadband, timeout(sec)
        # Remove U17-PGM mirror
        group1_list = [
            ["u171pgm1:PH_0_SET", 770.0, "u171pgm1:PH_0_GET", 0.3, 180],
        ]
        # AU1 Aperture
        group2_list = [
            ["WAUY02U012L:AbsM1", -1.0, "WAUY02U012L:rdPosM1", 0.1, 60],
            ["WAUY02U012L:AbsM2", -1.6, "WAUY02U012L:rdPosM2", 0.1, 60],
            ["WAUY02U012L:AbsM3",  0.4, "WAUY02U012L:rdPosM3", 0.1, 60],
            ["WAUY02U012L:AbsM4", -1.4, "WAUY02U012L:rdPosM4", 0.1, 60],
        ]
        # Pink Apertures U17-AU3-Pink
        group3_list = [
            ["AUY01U112L:AbsM1", -18.5, "AUY01U112L:rdPosM1", 0.1, 60],
            ["AUY01U112L:AbsM2", -21.5, "AUY01U112L:rdPosM2", 0.1, 60],
            ["AUY01U112L:AbsM3",  -1.5, "AUY01U112L:rdPosM3", 0.1, 60],
            ["AUY01U112L:AbsM4",   2.5, "AUY01U112L:rdPosM4", 0.1, 60],
        ]
        # Translate all M2 mirror into the beam
        group4_list = [
            ["HEX2OS12L:hexapod:setPoseY", 0.0, "HEX2OS12L:hexapod:getReadPoseY", 1.0, 120],
        ]

        task_list = [
           [group1_list, "Moving U17-PGM to home position...", "OK"], 
           [group2_list, "Moving Apertures U17-AU1-Pink...", "OK"],
           [group3_list, "Moving Apertures U17-AU3-Pink...", "OK"],
           [group4_list, "Moving Hexapod Ty...", "OK\nDone!"]
        ]

        for tsk in task_list:
            grp = tsk[0]
            print(tsk[1])
            for mpv in grp:
                caputq(mpv[0],mpv[1])
            for mpv in grp:
                self.__pvwait(mpv[2], mpv[1], deadband=mpv[3], timeout=mpv[4])
            print(tsk[2]) 

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
        ring_current.initialize()

    def __ge_init_progress(self):
        Scan_Progress.write(0)
        self.GE_start_frame = GE_FrameID.take()
        self.__ge_init_frame_countdown(self.ge_exptime)
        self.__reinit_hzb_pvs()
        #self.__publish_status("Running scan...")
        #print("Scan has started...")

    def __ge_calc_progress(self):
        Scan_Progress.write(100*(GE_FrameID.take()-self.GE_start_frame)/(self.scan_images))
        if self.DEBUG: print("ID0: " + str(self.GE_start_frame) + " ID: " + str(GE_FrameID.take()) + " Total: " + str(self.scan_images) + " Progress: " + str(Scan_Progress.take()))
        #self.__ge_start_frame_countdown()

    def __ge_setup_caenels1(self, Exp_Time=1, Enable=True):
        cae_exp_time=float(Exp_Time+0.05)
        caputq("PINK:CAE1:Acquire", 0)
        caput("PINK:CAE1:ValuesPerRead", int(1000*cae_exp_time))
        caput("PINK:CAE1:AveragingTime", float(cae_exp_time))
        caput("PINK:CAE1:TriggerMode", 1)
        if Enable:
            caputq("PINK:CAE1:Acquire", 1)
        else:
            caputq("PINK:CAE1:Acquire", 0)

    def __ge_setup_caenels2(self, Exp_Time=1, Enable=True):
        cae_exp_time=float(Exp_Time+0.05)
        caputq("PINK:CAE2:Acquire", 0)
        caput("PINK:CAE2:ValuesPerRead", int(1000*cae_exp_time))
        caput("PINK:CAE2:AveragingTime", float(cae_exp_time))
        caput("PINK:CAE2:TriggerMode", 1)
        if Enable:
            caputq("PINK:CAE2:Acquire", 1)
        else:
            caputq("PINK:CAE2:Acquire", 0)

    def __ge_setup_greateyes(self, exposure=1, images=1):
        if self.DEBUG: print("Setup greateyes...")
        caput("PINK:GEYES:cam1:NumImages", images)
        if(images==1):
            caput("PINK:GEYES:cam1:ImageMode", 0)
        else:
            caput("PINK:GEYES:cam1:ImageMode", 1)
        caput("PINK:GEYES:cam1:AcquireTime", exposure)
        if self.DEBUG: print("Setup greateyes ok")

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
            caput("PINK:GEYES:cam1:ShutterMode", 0)
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
        caput("PINK:GEYES:cam1:ShutterMode", 2)
        if self.DEBUGLOG: log("BG: Enable BG Processing", data_file=False)
        #Turns ON Background processing on GEyes Process Plugin
        caput("PINK:GEYES:Proc1:EnableBackground",1)
        if self.DEBUG: print("Background saved")
        self.__publish_status("Background saved")

    def __ge_setup_file(self, fname="ge"):
        set_exec_pars(open=False, name=fname, reset=True)

    def __ge_clean_spec_sum(self):
        caput("PINK:GEYES:specsum_reset", 0)
        caput("PINK:GEYES:specsum_reset", 1)

    def __ge_Save_Pre_Scan_Data(self, scantype=" ", passid=0):
        if self.DEBUG: print("Saving Pre scan dataset ...")
        save_dataset("RAW/GE_BG_Image", GE_BG_Image.read(), features=self.data_compression)
        #save_dataset("Processed/GE_Spectrum_Convertion", GE_Spectrum_Conv.read())
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

    def __ge_Save_Pre_Scan_Data_v2(self, scantype=" "):
        if self.DEBUG: print("Saving Pre scan dataset v2 ...")
        save_dataset("Detector/GE_ROI_Line", GE_ROI_Line.read())
        save_dataset("Detector/GE_ROI_SizeX", GE_ROI_SizeX.read())
        save_dataset("Detector/GE_ROI_SizeY", GE_ROI_SizeY.read())
        save_dataset("Detector/Exposure_Time", GE_AreaDet.getExposure())
        save_dataset("Detector/GE_Open_Delay", caget("PINK:GEYES:cam1:ShutterOpenDelay"))
        save_dataset("Detector/GE_Close_Delay", caget("PINK:GEYES:cam1:ShutterCloseDelay"))
        #save_dataset("Detector/GE_Num_Images", GE_AreaDet.getNumImages())
        save_dataset("Detector/Gain_Type", caget("PINK:GEYES:cam1:GreatEyesGain_RBV"))
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
            save_dataset("Scan/Args/Yspeed", args[6])
            save_dataset("Scan/Args/passes", args[7])
            save_dataset("Scan/Args/sample", args[8])
        elif ftype==5:
            save_dataset("Scan/Args/function", "ge_SEC_EL_continous_points_speed")
            save_dataset("Scan/Args/X0", args[0])
            save_dataset("Scan/Args/deltaX", args[1])
            save_dataset("Scan/Args/Xpoints", args[2])
            save_dataset("Scan/Args/Y0", args[3])
            save_dataset("Scan/Args/Y1", args[4])
            save_dataset("Scan/Args/Ypoints", args[5])
            save_dataset("Scan/Args/Yspeed", args[6])
            save_dataset("Scan/Args/passes", args[7])
            save_dataset("Scan/Args/sample", args[8])
        elif ftype==6:
            save_dataset("Scan/Args/function", "ge_SEC_EL_continous_exposure_points")
            save_dataset("Scan/Args/exposure", args[0])
            save_dataset("Scan/Args/X0", args[1])
            save_dataset("Scan/Args/deltaX", args[2])
            save_dataset("Scan/Args/Xpoints", args[3])
            save_dataset("Scan/Args/Y0", args[4])
            save_dataset("Scan/Args/Y1", args[5])
            save_dataset("Scan/Args/Ypoints", args[6])
            save_dataset("Scan/Args/passes", args[7])
            save_dataset("Scan/Args/sample", args[8])
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
        create_dataset("Pressure/Diagnostic_PV", 'd', False)
        create_dataset("Pressure/Diagnostic_HV", 'd', False)
        create_dataset("Pressure/Spectrometer_PV", 'd', False)
        create_dataset("Pressure/Spectrometer_HV", 'd', False)
        create_dataset("Pressure/Sample_Chamber", 'd', False)
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
        create_dataset(passfolder+"Pressure/Diagnostic_PV", 'd', False)
        create_dataset(passfolder+"Pressure/Diagnostic_HV", 'd', False)
        create_dataset(passfolder+"Pressure/Spectrometer_PV", 'd', False)
        create_dataset(passfolder+"Pressure/Spectrometer_HV", 'd', False)
        create_dataset(passfolder+"Pressure/Sample_Chamber", 'd', False)
        create_dataset(passfolder+"RAW/ring_current", 'd', False)
        if cont==False:
            create_dataset(passfolder+"RAW/SEC_el_x", 'd', False)
            create_dataset(passfolder+"RAW/SEC_el_y", 'd', False)
        if self.DEBUG: print("create scan dataset ok")

    def __ge_Create_Scan_Dataset_v3(self, cont=False, passes=1):
        if self.DEBUG: print("create scan dataset v3... ")
        create_dataset("Processed/GE_Spectrum_Sum", 'd', False, (passes, int(GE_BG_SizeX.take())))
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
        append_dataset("Pressure/Diagnostic_PV", Press_Diag_PV.take())
        append_dataset("Pressure/Diagnostic_HV", Press_Diag_HV.take())
        append_dataset("Pressure/Spectrometer_PV", Press_Spec_PV.take())
        append_dataset("Pressure/Spectrometer_HV", Press_Spec_HV.take())
        append_dataset("Pressure/Sample_Chamber", Press_Sample_Ch.take())
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
        append_dataset(passfolder+"Pressure/Diagnostic_PV", Press_Diag_PV.take())
        append_dataset(passfolder+"Pressure/Diagnostic_HV", Press_Diag_HV.take())
        append_dataset(passfolder+"Pressure/Spectrometer_PV", Press_Spec_PV.take())
        append_dataset(passfolder+"Pressure/Spectrometer_HV", Press_Spec_HV.take())
        append_dataset(passfolder+"Pressure/Sample_Chamber", Press_Sample_Ch.take())
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
