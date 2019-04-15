###################################################################################################
#  Deployment specific global definitions - executed after startup.py
###################################################################################################
from plib.logger_class import MasterLogger

run("plib/pink_extra.py")
run("plib/pink_class.py")
run("plib/bpm_class.py")
run("plib/blade_class.py")
run("plib/gap_class.py")

pink=PINKCLASS()
bpm=BPMCLASS()
blade=BLADECLASS()
gap=GAPCLASS()
mlogger = MasterLogger()

pink.help()
print("Type \"pink.help_information()\" to print this information again")

def on_command_started(info):
    mlogger.onstart(info)
    
def on_command_finished(info):
    mlogger.onend(info)
    