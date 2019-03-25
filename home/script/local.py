###################################################################################################
#  Deployment specific global definitions - executed after startup.py
###################################################################################################

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
pink.help()
print("Type \"pink.help_information()\" to print this information again")

