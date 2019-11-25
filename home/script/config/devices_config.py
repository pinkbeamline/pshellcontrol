## vector holds
##      Double: [device type, device name, Reading PV]
## Positioners: [device type, device name, Writing PV, Reading PV]
##       Array: [device type, device name, Reading PV, Array size]
##
## Note: Positioners must be manually configured on first time

U17M1 = [
    ["Positioner", "U17M1Ty", "U17_M1:TyAbs", "U17_M1:rdTy"],
]

U17M2 = [
    ["Positioner", "U17M2Rx", "HEX2OS12L:hexapod:setPoseA", "HEX2OS12L:hexapod:getReadPoseA"],
    ["Positioner", "U17M2Ty", "HEX2OS12L:hexapod:setPoseY", "HEX2OS12L:hexapod:getReadPoseY"],
]

MSIM2 = [
    ["Positioner", "msim2", "PINK:MSIM2:m2.VAL", "PINK:MSIM2:m2.RBV"]
]

MSIM3 = [
    ["Double", "msim3", "PINK:MSIM2:m2.RBV"]
]

MYTHEN = [
    ["Array",  "MythenRaw", "PINK:MYTHEN:image1:ArrayData", 1280],
    ["Array",  "MythenSpecSum", "PINK:MYTHEN:specsum_RBV", 1280],
    ["Double", "MythenAcq", "PINK:MYTHEN:cam1:Acquire"],
    ["Double", "MythenID", "PINK:MYTHEN:cam1:ArrayCounter_RBV"],
]

DELAYGEN = [
    ["Double", "DGTrigger", "PINK:DG01:TriggerDelayBO"],
]

EIGER = [
    ["Double", "EIG_Acquire", "PINK:EIGER:cam1:Acquire"],
    ["Double", "EIG_Acquire_RBV", "PINK:EIGER:cam1:Acquire_RBV"],
    ["Array", "EIG_ROI_RAW", "PINK:EIGER:image3:ArrayData", 264710],
    ["Array", "EIG_SPEC", "PINK:EIGER:spectrum_RBV", 514],
    ["Array", "EIG_SPECSUM", "PINK:EIGER:specsum_RBV", 514],
    ["Double", "EIG_ID", "PINK:EIGER:image3:UniqueId_RBV"],
    ["Double", "EIG_Threshold", "PINK:EIGER:cam1:ThresholdEnergy_RBV"],
    ["Double", "EIG_Energy", "PINK:EIGER:cam1:PhotonEnergy_RBV"],
    ["Double", "EIG_Exposure", "PINK:EIGER:cam1:AcquireTime"],
    ["Double", "EIG_Period", "PINK:EIGER:cam1:AcquirePeriod"],
    ["Double", "EIG_Images", "PINK:EIGER:cam1:NumImages"],
    ["Matrix", "EIG_RAWROI", "PINK:EIGER:image3:ArrayData", "PINK:EIGER:image3:ArraySize0_RBV", "PINK:EIGER:image3:ArraySize1_RBV"],
    ["Double", "EIG_ManualTrig", "PINK:EIGER:cam1:ManualTrigger"],
    ["Double", "EIG_Trig", "PINK:EIGER:cam1:Trigger"],
]