let width = window.innerWidth;
let height = window.innerHeight;
let canvas = document.getElementById("myCanvas");
var c = canvas;
var ctx = c.getContext("2d");

canvas.width = width * 0.2;
canvas.height = height * 0.2;

let SIZE = 5;
let RANGE = 40;
let MASS = 1;
const SLOW = 2;
draw = (x, y, c, s) => { //Most basic drawing rectangles
    ctx.fillStyle = c;
    ctx.fillRect(x, y, s, s);
}

random = (axis) => { //Random generation for init pos
    switch (axis) {
        case 'x':
            return Math.random() * canvas.width;
        case 'y':
            return Math.random() * canvas.height;
    }
}

createAtom = (x,y,c,s,r,m) => { //Create an object
    return {x: x, y: y, color: c, velx: 0, vely: 0, size: s, range: r, mass: m}; // Return a dict containing all the info and a X/Y vel of init 0
}

allAtoms = [];

createGroup = (num, color) => {
    group = [];
    for (let i = 0; i < num; i++){
        let currAtom = createAtom(random('x'), random('y'), color, SIZE, RANGE, MASS);
        group.push(currAtom);
        allAtoms.push(currAtom);
    }
    return group;
}

runRule = (group1, group2, attraction) => {
    for (let i = 0; i < group1.length; i++){
        let forcex = 0;
        let forcey = 0;

        for(let j = 0; j < group2.length; j++){
            let distance = 0;
            let mainAtom = group1[i];
            let affectingAtom = group2[j];
            let xChange = mainAtom.x - affectingAtom.x;
            let yChange = mainAtom.y - affectingAtom.y;
            distance = Math.sqrt((xChange*xChange) + (yChange*yChange));

            // Debugging log
            console.log(`Distance: ${distance}, Main Atom Mass: ${mainAtom.mass}, Affecting Atom Mass: ${affectingAtom.mass}`);

            if (distance <= mainAtom.range){
                let f = attraction * (mainAtom.mass * affectingAtom.mass / ((distance * distance) + Number.EPSILON)); // Added EPSILON to avoid division by zero
                forcex += f * xChange;
                forcey += f * yChange;
            } else { continue; }

            // Debugging log
            console.log(`ForceX: ${forcex}, ForceY: ${forcey}`);

            mainAtom.velx = (mainAtom.velx + forcex) * SLOW;
            mainAtom.vely = (mainAtom.vely + forcey) * SLOW;

            mainAtom.x += mainAtom.velx;
            mainAtom.y += mainAtom.vely;

            // if (mainAtom.x < 0 || mainAtom.x > canvas.width) { mainAtom.velx *= -1; }
            // if (mainAtom.y < 0 || mainAtom.y > canvas.height) { mainAtom.vely *= -1; }
            if (mainAtom.x < 0 || mainAtom.x > canvas.width) { mainAtom.x = 0; }
            if (mainAtom.y < 0 || mainAtom.y > canvas.height) { mainAtom.y = 0; }
            console.log(distance, xChange, yChange, forcex, forcey, mainAtom.velx, mainAtom.vely, mainAtom.x, mainAtom.y);
        }
    }
}

yellow = createGroup(50, "yellow");
red = createGroup(50, "red");
green = createGroup(50, "green");

function update() {
    // Clear the canvas
    ctx.fillStyle = 'white';
    ctx.fillRect(0, 0, canvas.width, canvas.height);

    // Run the simulation rule
    runRule(green, green, -0.32);
    runRule(green, red, -0.17);
    runRule(green, yellow, 0.34);
    runRule(red, red, -0.1);
    runRule(red, green, -0.34);
    runRule(yellow, yellow, 0.15);
    runRule(yellow, green, -0.2);

    // Draw the updated positions of all atoms
    for (let i = 0; i < allAtoms.length; i++) {
        draw(allAtoms[i].x, allAtoms[i].y, allAtoms[i].color, 5);
    }

    // Request the next animation frame to continuously update
    requestAnimationFrame(update);
}

// Start the animation loop
update();

