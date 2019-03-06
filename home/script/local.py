###################################################################################################
#  Deployment specific global definitions - executed after startup.py
###################################################################################################

from __future__ import division

run("shared/pink_class.py")
run("shared/bpm_class.py")
run("shared/blade_class.py")
run("shared/pink_extra.py")
run("shared/gap_class.py")

pink=PINKCLASS()
bpm=BPMCLASS()
blade=BLADECLASS()
gap=GAPCLASS()

print("Pink beamline")


# to be cleaned and organized


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

class AnalogOutput(RegisterBase):
    def __init__(self, name):
        RegisterBase.__init__(self, name)
        self.val = 0

    def doRead(self):
        return self.val

    def doWrite(self, val):
        self.val = val


class Fraction(RegisterBase):
    def __init__(self, name):
        RegisterBase.__init__(self, name)
        self.val = 0.0

    def doRead(self):
        return self.val

    def doWrite(self, val):
        self.val = val
        return self.val

    def updt(self, current, vmin, vmax):
        self.val = (current-vmin)/(vmax-vmin)
        return self.val
    

add_device(Array2Matrix("GE_BG_Image", GE_BG_Array, GE_BG_SizeX, GE_BG_SizeY), True) 
add_device(Array2Matrix("GE_ROI_Image", GE_ROI_Array, GE_ROI_SizeX, GE_ROI_SizeY), True) 
add_device(Array2Matrix("GE_Raw_Image", GE_Raw_Array, GE_BG_SizeX, GE_BG_SizeY), True) 

sleep(1)

GE_BG_Image.read()
GE_ROI_Image.read()
GE_Raw_Image.read()
