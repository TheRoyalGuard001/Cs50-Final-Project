let width = window.innerWidth;
let height = window.innerHeight;
let canvas = document.getElementById("myCanvas");
var c = canvas
var ctx = c.getContext("2d");

canvas.width = width * 50 / 100;
canvas.height = height * 50 / 100;

let numRows = 10;
let numCols = 10;
let colStep = canvas.width / numCols;
let rowStep = canvas.height / numRows;

function drawTable() {
    for (let i = 0; i < numCols; i++) {
        ctx.moveTo(colStep * i, 0);
        ctx.lineTo(colStep * i, canvas.height);
        ctx.stroke();
    }
    for (let i = 0; i < numRows; i++) {
        ctx.moveTo(0, rowStep * i);
        ctx.lineTo(canvas.width, rowStep * i);
        ctx.stroke();
    }
}

drawTable(numRows, numCols);

function setCell(x, y, color) {
ctx.fillStyle = color;
const startX = x * colStep;
const startY = y * rowStep;
const rectWidth = colStep;
const rectHeight = rowStep;
ctx.fillRect(startX, canvas.height - startY - rectHeight, rectWidth, rectHeight);
}
setCell(5,5,'red')
