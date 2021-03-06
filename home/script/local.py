###################################################################################################
#  Deployment specific global definitions - executed after startup.py
###################################################################################################
from plib.logger_class import MasterLogger

run("plib/pink_extra.py")
run("plib/pink_class.py")
run("plib/bpm_class.py")
run("plib/blade_class.py")
run("plib/scan_class.py")
#run("plib/gap_class.py")
#run("plib/m2mirror_class")
run("plib/dev_class.py")

pink=PINKCLASS()
bpm=BPMCLASS()
blade=BLADECLASS()
#gap=GAPCLASS()
mlogger = MasterLogger()
scan = PSCANS()
#mirror = M2Mirror()
dev = DEV()

print("PShell Ready")

def on_command_started(info):
    mlogger.onstart(info)
    #print("onstart")

def on_command_finished(info):
    mlogger.onend(info)
    #print("onend")
