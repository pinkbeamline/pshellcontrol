try:
    if args[0]==11:
        print("Text: " + args[1] + "\tNum: " + str(args[2]))
    else:
        print("Wrong type argument")
except:
    print("Global variable not available")