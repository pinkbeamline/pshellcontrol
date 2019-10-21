## m2mirror_class.py

import config.ml_mirror_config as m2mcfg

class M2Mirror():

    m2poslist = m2mcfg.m2mirpos

    def select_2300ev(self):
        layer = 8
        self.__movemirror(layer)
        
    def select_3000ev(self):
        layer = 7
        self.__movemirror(layer)

    def select_4000ev(self):
        layer = 6
        self.__movemirror(layer)
        
    def select_5000ev(self):
        layer = 5
        self.__movemirror(layer)

    def select_6300ev(self):
        layer = 4
        self.__movemirror(layer)
        
    def select_6800ev(self):
        layer = 3
        self.__movemirror(layer)

    def select_7300ev(self):
        layer = 2
        self.__movemirror(layer)
        
    def select_8000ev(self):
        layer = 1
        self.__movemirror(layer)        

    def select_9500ev(self):
        layer = 0
        self.__movemirror(layer)   

    def __movemirror(self,layer):
        group = self.m2poslist[layer][3]
        pos = self.m2poslist[layer][2]
        try:
            self.__movegroup(group)
            self.__movelayer(pos)
            print("Mirror Ready. OK")
        except:
            print("Error moving mirror or operation canceled")

    def __movegroup(self, group):
        grouplabels = ["Optic ID#3", "Optic ID#2", "Optic ID#1"]
        actualgroup = caget("HEX2OS12L:hexapod:mbboMirrorChoicerRun", 'i')
        if(group != actualgroup):
            tout = 0
            while(caget("HEX2OS12L:multiaxis:running")):
                if tout%5==0:
                    print("Mirror is in use. Waiting! ( "+ str(tout) + " sec ) ")
                sleep(1)
                tout = tout+1
            print("Changing mirror to " + grouplabels[group]+". Please wait. This takes a while...")
            caput("HEX2OS12L:hexapod:mbboMirrorChoicerRun", group)
            sleep(1)
            while(caget("HEX2OS12L:multiaxis:running")):
                sleep(1)
            sleep(1)

    def __movelayer(self, pos):
        while(caget("HEX2OS12L:multiaxis:running")):
            if tout%5==0:
                print("Mirror is in use. Waiting! ( "+ str(tout) + " sec ) ")
            sleep(1)
            tout = tout+1        
        print("Moving mirror to Tx: "+str(pos)+". Please wait. This takes a while...")     
        caput("HEX2OS12L:hexapod:setPoseX", pos)
        sleep(1)
        while(caget("HEX2OS12L:multiaxis:running")):
            sleep(1)
        sleep(1)
        
            