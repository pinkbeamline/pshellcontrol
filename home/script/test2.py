print("Test 2")

devlist = [
    ["mydev1", "PINK:ANC01:ACT0:POSITION"]
    ["mydev2", "PINK:SMA01:m4.RBV"]
    ]

for dev in devlist:
    chk = get_device(dev[0])
    if chk == None:
        add_device(ch.psi.pshell.epics.ChannelDouble(dev[0],dev[1]))
        mydev.setMonitored(True)
    print("Device added")
else:
    print("Device already exist")

for i in range(3):
    print(str(i) + ": " + str(mydev.take()))
    sleep(1)

remove_device(mydev)
print("OK")

    