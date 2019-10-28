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
