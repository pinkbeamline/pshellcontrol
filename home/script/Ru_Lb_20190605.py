pink.ge_SEC_EL_continous_exposure_speed(10, -16000, 800, 5, -8000, 8000, 200, passes=5, sample='Ru_CT 2,3 S#2.78a')
pink.ge_SEC_EL_continous_exposure_speed(10, 19000, 800, 5, -8000, 8000, 200, passes=5, sample='Ru_CT 2,3 S#78d')
pink.ge_SEC_EL_continous_exposure_speed(10, 37000, 800, 5, -8000, 8000, 200, passes=5, sample='Ru_CT 2.3 S#b')
pink.shutter_hard_CLOSE()
caput("PINK:PLCVAC:V11close", 1)
caput("PINK:PLCVAC:V10close", 1)
#caput("PINK:GEYES:cam1:Temperature", 20)