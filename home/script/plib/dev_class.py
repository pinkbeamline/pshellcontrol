## device creation class

import config.devices_config as devlist

class DEV():
    ### MSIM2
    def msim2_create(self):
        pvlist = devlist.MSIM2
        self.__create_devices(pvlist)

    def msim2_remove(self):
        pvlist = devlist.MSIM2
        self.__remove_devices(pvlist)

    ### Mythen
    def mythen_create(self):
        pvlist = devlist.MYTHEN
        self.__create_devices(pvlist)

    def mythen_remove(self):
        pvlist = devlist.MYTHEN
        self.__remove_devices(pvlist)

    ### U17M1
    def U17M1_create(self):
        pvlist = devlist.U17M1
        self.__create_devices(pvlist)

    def U17M1_remove(self):
        pvlist = devlist.U17M1
        self.__remove_devices(pvlist)

    ### U17M2
    def U17M2_create(self):
        pvlist = devlist.U17M2
        self.__create_devices(pvlist)

    def U17M2_remove(self):
        pvlist = devlist.U17M2
        self.__remove_devices(pvlist)

    ### Delay Generator
    def Delaygen_create(self):
        pvlist = devlist.DELAYGEN
        self.__create_devices(pvlist)

    def Delaygen_remove(self):
        pvlist = devlist.DELAYGEN
        self.__remove_devices(pvlist)

    ### Eiger2 Detector
    def Eiger_create(self):
        pvlist = devlist.EIGER
        self.__create_devices(pvlist)

    def Eiger_remove(self):
        pvlist = devlist.EIGER
        self.__remove_devices(pvlist)
        
### Internal functions ##########################################################

    def __create_devices(self, pvlist):
        for pvr in pvlist:
            devstate = True
            if pvr[0] == "Double":
                add_device(ch.psi.pshell.epics.ChannelDouble(pvr[1], pvr[2]), True)
            elif pvr[0] == "Positioner":
                add_device(ch.psi.pshell.epics.Positioner(pvr[1], pvr[2], pvr[3]), True)
            elif pvr[0] == "Array":
                add_device(ch.psi.pshell.epics.GenericArray(pvr[1], pvr[2], pvr[3]), True)
            elif pvr[0] == "Matrix":
                devwidth = caget(pvr[3])
                devheight = caget(pvr[4])
                add_device(ch.psi.pshell.epics.ChannelDoubleMatrix(pvr[1], pvr[2], devwidth, devheight), True)
            elif pvr[0] == "String":
                add_device(ch.psi.pshell.epics.ChannelString(pvr[1], pvr[2]), True)
            else:
                print("Wrong device type for device:")
                print(pvr)
                devstate = False

            if devstate:
                exec(pvr[1]+".setMonitored(True)")

    def __remove_devices(self, pvlist):
        for pvr in pvlist:
            execcmd = "remove_device("+pvr[1]+")"
            exec(execcmd)
