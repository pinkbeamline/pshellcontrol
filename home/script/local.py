###################################################################################################
#  Deployment specific global definitions - executed after startup.py
###################################################################################################
from plib.logger_class import MasterLogger

run("pink/pink_class.py")
run("pink/bpm_class.py")
run("pink/blade_class.py")
run("pink/pink_extra.py")
run("pink/gap_class.py")

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
    