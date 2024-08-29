# This file only serves to be a connection between two files to avoid import loops

allGroups = []
SLOW = 1
REFLECTION_BOUNCE = 50

# SLOW var discontinued since it made simulation less fun
# def setSlow(value):
#     global SLOW
#     SLOW = value

# def getSlow():
#     global SLOW
#     return SLOW

def setReflection(value):
    global REFLECTION_BOUNCE
    REFLECTION_BOUNCE = value

def getReflection():
    global REFLECTION_BOUNCE
    return int(REFLECTION_BOUNCE)
