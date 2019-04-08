###################################################################################################
#  Deployment specific global definitions - executed after startup.py
###################################################################################################

run("pink/pink_class.py")
run("pink/bpm_class.py")
run("pink/blade_class.py")
run("pink/pink_extra.py")
run("pink/gap_class.py")

pink=PINKCLASS()
bpm=BPMCLASS()
blade=BLADECLASS()
gap=GAPCLASS()

print("Pink beamline")
pink.help()
print("Type \"pink.help_information()\" to print this information again")

