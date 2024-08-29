import random, math
from sharedVars import getReflection

# SLOW var discontinued since it made simulation less fun
# SLOW = .5 # Should never really go over 1. Becomes very hard to see.
LOW_BOUND = 10 # LOW/HIGH_BOUND act as the 'walls' of the canvas.
HIGH_BOUND = 690
TOP_SPEED = 1 # Really anything going over 1 is just going to be teleporting and not looking good
LOW_SPEED = .8 # We dont want any atoms to never move so we give them a really slow drift
REFLECTION_BOUND = 50 #How random a reflection off the wall is.


def createAtom(x,y,c,s,r): # The basis of everything. returns a dict holding information.
    return {'x':x, 'y':y, 'velx':0, 'vely':0, 'color':c, 'size':s, 'range':r}

def randomPoint(): # Random returns 0-1 so we * by 800 to fill the whole canvas
    return random.random() * 800

# A small func but is the backbone of everything. returns a list of dicts
# symbolizing all atoms of a color (or group)
def createGroup(num, color, size, affectingZone):
    currGroup = []
    for i in range(num):
        currAtom = createAtom(randomPoint(), randomPoint(), color, size, affectingZone)
        currGroup.append(currAtom)
    return currGroup

# OVERVEIW:
# The most complicated func here. Runs the whole simulation.
# Group1 is the target and group2 are the affectors.
# This func is theta(n^2). Not efficent at all but it gets the job done.
# This is one of the things I would definetly change with more time
# Overall, it accumulates the force of attraction (see line where we define 'f')
# and then applies that force through changing the X/Y value (after making sure it sising going too fast).
# Then we check for a wall bounce (where we offset the atom by a random amount and switch velocity direction)
def runRule(group1, group2, attraction):
    for mainAtom in group1:
        forcex = 0
        forcey = 0
        for affectingAtom in group2:
            xChange = mainAtom['x'] - affectingAtom['x']
            yChange = mainAtom['y'] - affectingAtom['y']
            distance = math.sqrt((xChange ** 2) + (yChange ** 2))
            if distance <= mainAtom['range'] and distance > 0:
                f = attraction / distance
                forcex += f * xChange
                forcey += f * yChange
            else:
                continue

            # Apply accumulated force
            mainAtom['velx'] = (mainAtom['velx'] + forcex)
            mainAtom['vely'] = (mainAtom['vely'] + forcey)

            global TOP_SPEED, LOW_SPEED
            # Ensure velocity doesn't exceed bounds
            if abs(mainAtom['velx']) > TOP_SPEED:
                mainAtom['velx'] = TOP_SPEED * math.copysign(1, mainAtom['velx']) # if vel is -, apply that to 1 to keep it -
            if abs(mainAtom['vely']) > TOP_SPEED:
                mainAtom['vely'] = TOP_SPEED * math.copysign(1, mainAtom['vely'])

            if abs(mainAtom['velx']) < LOW_SPEED:
                mainAtom['velx'] = LOW_SPEED * math.copysign(1, mainAtom['velx'])
            if abs(mainAtom['vely']) < LOW_SPEED:
                mainAtom['vely'] = LOW_SPEED * math.copysign(1, mainAtom['vely'])

            # Apply velocity
            mainAtom['x'] += mainAtom['velx']
            mainAtom['y'] += mainAtom['vely']

            # Wall repulsion mechanism
            if mainAtom['x'] < LOW_BOUND:
                mainAtom['x'] = LOW_BOUND + (random.random() * getReflection())
                mainAtom['velx'] *= -1
            elif mainAtom['x'] > HIGH_BOUND:
                mainAtom['x'] = HIGH_BOUND - (random.random() * getReflection())
                mainAtom['velx'] *= -1

            if mainAtom['y'] < LOW_BOUND:
                mainAtom['y'] = LOW_BOUND + (random.random() * getReflection())
                mainAtom['vely'] *= -1
            elif mainAtom['y'] > HIGH_BOUND:
                mainAtom['y'] = HIGH_BOUND - (random.random() * getReflection())
                mainAtom['vely'] *= -1

# Simply sets X/Y randomly and gets rid of any velocity
def resetGroup(myGroup):
    for particle in myGroup:
        particle['x'] = randomPoint()
        particle['y'] = randomPoint()
        particle['velx'] = 0
        particle['vely'] = 0
