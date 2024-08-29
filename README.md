# MicroMotion - A Particle Life Simulator
#### Video Demo:  <URL HERE>
### Thanks:
I just wanted to thank all the cs50 staff for giving me this oppurtunity.
As someone doing this in their Sophmore summer, I've been quickly outgrowing what my school's
Engineering departmnet is capable of teaching me. This course has allowed me to continue
learning more practical code than just Arduino. Im planning to take more online cs courses by
you guys and i'm so grateful to you all for putting it online (I was smiling ear to ear when I saw all
the options during the week 10 lecture).

Once again, thank you and zeveryone on the team.
If you have any comments, please feel free to contact me at eliezer@dimbert.net

SMALL DISCLAIMER:

THIS PROJECT WAS GREATLY INSPIRED BY A YOUTUBE VIDEO (see below).
ALTHOUGH HE DOES OFFER A REPOSITORY THAT INCLUDES THIS SIMULATION IN PYTHON,
I DID NOT USE THAT AND HAVE ONLY ADAPTED HIS JAVASCRIPT VERSION. IN THE FILES
YOU WILL SEE particleLife.js. THIS WAS MY FIRST ATTEMPT TO UNDERSTAND HIS CODE
BEFORE ADAPTING TO PYTHON.
https://www.youtube.com/watch?v=0Kx4Y9TVMGg

## Description:
### simulationHelpers
To begin, id like to direct attention to __simulationHelpers__ file. This file holds all the backbone for the actual mathamatical operations that my project requires. I am a fan of programming base functions that can be built upon over a series of steps. That way, it allows me to break down the problem easier and overall have a better workflow.
#### createAtom()
First we must start in the very simple *createAtom()* function that will simply return a dict holding all the values required to simulate an atom. I decided to do this instead of creating a class because I was "brought up" on Arduino and we almost never used Object Oriented Programming. Just to make my life simpler, I thought that having a dict would be eaiser as I am more comfortable manipluating it.
#### createGroup() / randomPoint()
*createGroup()* and *randomPoint()* go together to create a randomly populated screen which serves to create a more interesting simulation as the whole point is to see how life emerges in differing conditions. What we end up with in the end is a fully costimizable "group" which is a list of dicts, each randomly positioned.
#### runRule()
Now comes time for the first actually complicated function, *runRule()*.

First, some criticization: this function is ran by far the most often and yet it has a time complexity of $\theta$(n<sub>1</sub> * n<sub>2</sub>) which really is quite innifecient. This can lead to some serious lag spikes in simulation but with the time I devoted to this project, I had more important things to focus on. With more time this is something I would definitely come back to.

Past that, this function is really quite simple. For every atom in the main group, we initilize some accumalators and loop through every atom of the other group. If the secondary atom is within the range of the first, calculate the force with a simplified version of gravity ($attraction / distance$ as opposed to $(G * m_1 * m_2)/d^2$). Then we do the calculation for work in both X and Y directions  ($work = force * \Delta X/Y$) and accumulate it. After we have looped through all of the attraction atoms, we add this accumulated number to our current velocity.

```python
#Code for the last paragraph b/c I know I didnt do a good job explaining:
for mainAtom in group1:
    forcex = 0
    forcey = 0
    for affectingAtom in group2:
        xChange = mainAtom['x'] - affectingAtom['x']
        yChange = mainAtom['y'] - affectingAtom['y']
        # Pythag theorem
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
#Rest of func...
```
After updating the velocities for the next frame, we need to make sure no particle is going too fast/slow. If they do end up moving too fast, they might jump off screen or teleport around. If they are too slow, its uniteresting. Thus we can do some cool expressions where we check if the X/Y velocities are too high/low. If so, we set them to the top/low speed. However, this does not account for negitive speeds (moving to the left/down) so we have to get fancy and get to use the *abs()* and *copysign()* funcs to retain the direction.
```python
if abs(mainAtom['velx']) > TOP_SPEED:
    mainAtom['velx'] = TOP_SPEED * math.copysign(1, mainAtom['velx'])
# Copied 3 more times for min speed cap of X and for Y velocity
```
Finally we can apply the velocities by just adding them to the X/Y coord respectively.

But what if they get off screen? Thus we add a "wall bounce" mechanic which checks the X/Y of the atom. If the atom is above/below the high/low bounds, we bring them back to the "wall" and offset by a random amount and turn them around so if a big group comes they dont just move back and run into the wall in the same way.
```python
# Wall repulsion mechanism
if mainAtom['x'] < LOW_BOUND:
    mainAtom['x'] = LOW_BOUND + (random.random() * getReflection())
    mainAtom['velx'] *= -1
# Again, copied 3 times for low bound for X and checking high/low bounds for Y coord
```

The final function called *resetGroup()* is to reset a group by randomizing their position again and setting velocities to 0. This is activated only when the user presses the "Reset" button on the page.


### index.html
Before delving into the backend of the socketIO, I think understanding the frontend is a better place to start.

#### body
The body can be split into 3 parts: the canvas, the attraction form, and the atom specification form.

The canvas is simple as it's just a 700x700 place where the simulation will be shown.

The first form that you see is a table where the first column represents  the target group (aka "group1" in the *runRule()*). Then there are 3 sliders ranging from -100 to 100 repersenting the attraction (or repulsion if negitive) between the target group and the the respective other atoms (aka "group2" in *runRule()*).

The second form is where the user can manipulate the number, size, and range of each group. There is a checkbox signifying the activation of said group. In the HTML you can see that right before this checkbox is another hidden input of the same name. The point of this is to avoid any errors in the backend where the code attempts to acsess a key that does not exist (because a checkbox does not add itself to a form as "off" if left unchecked). If the checkbox is pressed, the procedure will go on as normal and since they have the same name, the hidden input will be ignored. However, if the checkbox is left unchecked, the hidden input will add itself to the JSON file.
```HTML
<input type="hidden" name="green-activate-form" value="off">
<td><input type="checkbox" name="green-activate-form"></td>
```
#### Script
Firstly we set up some constants connecting to the canvas and socketIO as well as attaching runctions to all the forms and buttons.

The script for both forms are in essence the same as they find the form by Id, and begin to collect the data set by the user. Then they package the data and emit it through socketIO as a dict. The only change in the attraction changing form is that the value set by the user is put into the dict like this:
``` javascript
data[key] = value/100 * -1;
```
We divide by 100 to get the decimal value as any value > 1 (or < -1) rapidly move the atoms so fast it ruins the simulation. Then its multiplied by -1 as technically, according to the calculations a negitive value attracts and a positive one repels. However, this is unintuitive so I changed it so nobody would be confused.

Each form emits its data to the server with a unique name. This just made the backend eaiser to split.

When the server tells the client its reciving a 'message', the client will parse the file and pass it into the *drawData()* function as a dict. This function clears the screen and lopps through the data and draws each atom as specified in it's key-value pairs.

Finally and least importat, there is a tiny function that updates the spans next to every slider. When the slider changes, it passes its name and value to thsi function. Since every span is just the name of the slider next to it + 'Value' at the end, we can target the correct span by concatenating the slider name and 'Value'. Then it's just a process of update the text of the span to be the value of the slider.
``` javascript
    function updateValue(val, name) {
        document.getElementById(name + 'Value').textContent = val;
    }
```

### app,py
Here is where everything comes together! I will take this time to explain why I used socketIO. I remember in the lecture when speaking about Flask, there was a demonstration of an ordered list appearing seamlessly as a autofill. I was frankly amazed and when theorizing my project, I relized I needed a similar seamless transition if I wanted anything taht looked like Brainxyz's video. Thus I asked cs50 Duck and got some examples to start playing with.

There are 3 major parts of the backend: dealing with each form and the *runFrame()* function
#### Form 1: Changing Atoms
Although this is technically form number 2, it's easier to explain. First things first we need to set flags True or False depending on if the checkboxes are pressed. This will save us time if we dont need to even think about a group. Next we go through each color and create a group to replace whatever values was saved to the group before.

#### Run Frame
Again, this may feel out of order but the second form deals with some of the things in this function. Before anything took place, we created a 'stop event' which will be used to interupt this function. So while this stop event is set, we are continiously runing any rules set by the user. Since this function has no communication with the frontend, it has to be ready to accept anywhere from 0-9 rules. Thus there are 9 if-else checks to see if that 'rule' needs to be ran or not. If the attraction is 0, we ignore that specific rule. Now we can take these groups that have been updated for the next frame, bring them into one file, 'jsonify' the data and emit it. Then we sleep according to the frame rate.

#### Form 2: Changing Attractions
You may have noticed that when you open the website for the first time, the simulation does not run until you change the attractions (even if you do input through the other form). I will now explain why. *runFrame()* is a function that is running on a Thread, meaning that the Thread must be stopped to input new data. We dont need to stop it for the Changing Atoms form because lists/dicts are always mutatable and data can effictively be 'sent' without interuption. however, when attraction values need to change, we need to end the thread, place new attraction values, and start it up again. This is why Changing Attractions is the one to initially start the simulation.

Dealing with this form is quite easy. All we need to do is stop the the Thread running the *runFrame()* function, wait for the last of it to end, then pass the new collected info in as a new Thread and start it.


### Some Extra Notes:
<list>
    <ol>There is a file called **sharedVars** that is really just a connection between **simulationHelpers** and **app**. While making the project I kept getting import loops so I resorted to this. </ol>
    <ol> The project can oly handle one client. If multiple connect then they will get the same simulation.</ol>
    <ol> A recomendation: limit number of atoms at 200, size at 20, and range at 200. I allowed higher numbers but they arent recomended. </ol>
</list>
