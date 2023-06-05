var canvas = document.getElementById('canvas');
var ctx = canvas.getContext('2d');

var nodes = []; // Array to store nodes and their connections
var isDrawing = false;
var startPoint = { x: 0, y: 0 };
var endPoint = { x: 0, y: 0 };

var tmpStartPoint = { x:0, y:0};
var tmpEndPoint = { x:0, y:0};

var startNode = null;
var endNode = null;

var fixedNodes = [
  { x: 100, y: 100 }, // Fixed node 1 position
  { x: 400, y: 300 }  // Fixed node 2 position
];

canvas.addEventListener('mousedown', startDrawing);
canvas.addEventListener('mousemove', drawLine);
canvas.addEventListener('mouseup', stopDrawing);
canvas.addEventListener('mouseout', stopDrawing);
canvas.addEventListener('mouseleave', stopDrawing);

window.addEventListener('DOMContentLoaded', function() {
  createNode(fixedNodes[0]);
  createNode(fixedNodes[1]);
  redrawCanvas();
});

function startDrawing(event) {
  startNode = findNode(startPoint);
  if (true)
  {
    isDrawing = true;
    startPoint.x = event.clientX - canvas.offsetLeft;
    startPoint.y = event.clientY - canvas.offsetTop;
    tmpStartPoint = startPoint;
  }
}


function drawLine(event) {
  if (!isDrawing) return;

  tmpEndPoint.x = event.clientX - canvas.offsetLeft;
  tmpEndPoint.y = event.clientY - canvas.offsetTop;
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  ctx.beginPath();
  ctx.moveTo(tmpStartPoint.x, tmpStartPoint.y);
  ctx.lineTo(tmpEndPoint.x, tmpEndPoint.y);
  ctx.stroke();

  endPoint = tmpEndPoint;
  redrawCanvas();
}

function stopDrawing() {
  if (isDrawing) {
    isDrawing = false;

    var endNode = findNode(endPoint);
    console.log(startPoint);
    console.log(endPoint);
    
    if (endNode && !isSamePoint(startPoint, endPoint)) {
      // Create a connection between the start and end nodes
      createConnection(startNode, endNode);
    }

    ctx.clearRect(0, 0, canvas.width, canvas.height);
    redrawCanvas();
  }
}

function createNode(position) {
  var node = {
    position: { ...position },
    connections: []
  };

  nodes.push(node);
  return node;
}

function isSamePoint(p0, p1)
{
  var dx = Math.abs(p0.x - p1.x);
  var dy = Math.abs(p0.y - p1.y);
  
  return dx < 10 && dy < 10;
}

function findNode(position) {
  var proximityThreshold = 10; // Adjust the threshold as needed

  return nodes.find(function(node) {
    var dx = Math.abs(node.position.x - position.x);
    var dy = Math.abs(node.position.y - position.y);
    return dx <= proximityThreshold && dy <= proximityThreshold;
  });
}

function createConnection(startNode, endNode) {
  startNode.connections.push(endNode);
}

function redrawCanvas() {
  // ctx.clearRect(0, 0, canvas.width, canvas.height);

  nodes.forEach(function(node) {
    node.connections.forEach(function(connection) {
      ctx.beginPath();
      ctx.moveTo(node.position.x, node.position.y);
      ctx.lineTo(connection.position.x, connection.position.y);
      ctx.stroke();
    });
  });

  nodes.forEach(function(node) {
    ctx.beginPath();
    ctx.arc(node.position.x, node.position.y, 4, 0, 2 * Math.PI);
    ctx.fillStyle = 'red';
    ctx.fill();
    ctx.stroke();
  });

  ctx.beginPath();
  ctx.arc(fixedNodes[0].x, fixedNodes[0].y, 4, 0, 2 * Math.PI);
  ctx.fillStyle = 'blue';
  ctx.fill();
  ctx.stroke();

  ctx.beginPath();
  ctx.arc(fixedNodes[1].x, fixedNodes[1].y, 4, 0, 2 * Math.PI);
  ctx.fillStyle = 'blue';
  ctx.fill();
  ctx.stroke();
}

function drawNodes()
{

}