pink.ge_SEC_EL_continous_exposure_speed(10, 2000, 750, 4, -7900, 7900, 200, passes=10, sample='Ru(CN)6K4')
pink.ge_SEC_EL_continous_exposure_speed(10, -15100, 750, 4, -7000, 7900, 200, passes=10, sample='Ru(bpy)(FP6)2')
pink.ge_SEC_EL_continous_exposure_speed(10, 37700, 750, 4, -7900, 7900, 200, passes=10, sample='Ru(DMAP)6Cl2')
pink.shutter_hard_CLOSE()
caput("PINK:PLCVAC:V11close", 1)
caput("PINK:PLCVAC:V10close", 1)
#caput("PINK:GEYES:cam1:Temperature", 20)1)