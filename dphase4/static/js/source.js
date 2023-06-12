// Mapping of button IDs to titles
const buttonMapping = {
  CropImage: { name: "CropImage", inports: ["Image", "left_int", "top_int", "right_int", "bottom_int"], outports: ["Image"] },
  LoadImage: { name: "LoadImage", inports: [], outports: ["Image"] },
  GetFloat: { name: "GetFloat", inports: ["input_float"], outports: ["float"] },
  GetInteger: { name: "GetInteger", inports: ["input_int"], outports: ["int"] },
  GetString: { name: "GetString", inports: ["input_string"], outports: ["string"] }
};

const nodeTopPadding = 30;
const nodeVerticalPadding = 20;
let nodeIdCounter = 0;

let lineStart = { x:0, y:0 };
let lineFinish = { x:0, y:0 };

var connectionStart = { node:"", port:"" };
var connectionFinish = { node:"", port:"" };
var connections = []


// Add event listeners to the menu buttons
const menuButtons = document.getElementsByClassName("menu-button");

for (let i = 0; i < menuButtons.length; i++) {
  menuButtons[i].addEventListener("dragstart", handleDragStart);
  menuButtons[i].addEventListener("dragend", handleDragEnd);
  
}

// Add event listeners to the drop area
const dropArea = document.getElementById("drop-area");
dropArea.addEventListener("dragover", handleDragOver);
dropArea.addEventListener("drop", handleDrop);

// Create a canvas element
const canvas = document.createElement('canvas');
canvas.id = 'canvas';

// Set the canvas size to match the drop-area
canvas.width = dropArea.offsetWidth;
canvas.height = dropArea.offsetHeight;

// Position the canvas on top of the drop-area
canvas.style.position = 'absolute';
canvas.style.top = dropArea.offsetTop + 'px';
canvas.style.left = dropArea.offsetLeft + 'px';
canvas.style.pointerEvents = 'none';
// Append the canvas to the document body
document.body.appendChild(canvas);

// drawConnections();
// functions below
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
function startDrawing(event) {
  event.preventDefault();
  lineStart = { x:event.clientX, y:event.clientY };
  const target = event.target;
  connectionStart = { node:target.parentNode, port:target};
  // console.log(connectionStart);
}

function endDrawing(event) {
  const target = event.target;

  lineFinish = { x:event.clientX, y:event.clientY };
  connectionFinish = { node:target.parentNode, port:target};

  let connection = {start:connectionStart, finish:connectionFinish};
  let finishPortId = connectionFinish.node.getAttribute('id');

  if (connectionStart.node == null || 
    connectionFinish.node == null || 
    connectionStart.node.getAttribute('id') == finishPortId) {
    return;
  }
  
  if (connectionStart.port.getAttribute('type') != connectionFinish.port.getAttribute('type')) {
    return;
  }

  const isAvailable = isPortAvailable(connectionFinish.node.getAttribute('id'), connectionFinish.port.getAttribute('id'));
  
  if (isAvailable) {
    connections.push(connection);
  }

  drawConnections();
}

// Function to handle the drag start event
function handleDragStart(event) {
  const target = event.target;
  event.dataTransfer.setData('text/plain', target.id);
  target.classList.add('dragging');
}

// Function to handle the drag end event
function handleDragEnd(event) {
  const target = event.target;
  target.classList.remove("dragging");
}

// Function to handle the drag over event
function handleDragOver(event) {
  event.preventDefault();
}

// Function to handle the drop event
function handleDrop(event) {
  event.preventDefault();

  const data = event.dataTransfer.getData('text/plain');
  const droppedElement = document.getElementById(data);
  const classList = droppedElement.classList;

  if (classList.contains("menu-button")) {
      const dropArea = event.currentTarget;
      const newNode  = createNode(event, data);
      dropArea.appendChild(newNode);
  }
  else if (classList.contains("node")){
      const targetPos = { x:event.clientX - 50, y:event.clientY - 25 };
      moveNode(targetPos, droppedElement);
      console.log(droppedElement.getAttribute("id"));
      drawConnections();
  }
}

function createNode(event, data) {
  const offsetX = event.clientX - 50;
  const offsetY = event.clientY - 25;

  const newNode = document.createElement('div');
  newNode.className = 'node';
  newNode.textContent = buttonMapping[data].name;
  const nodeId = `node-${nodeIdCounter}`;
  newNode.setAttribute('id', nodeId);
  newNode.style.left = offsetX + 'px';
  newNode.style.top = offsetY + 'px';

  newNode.draggable = true;
  newNode.addEventListener('dragstart', handleDragStart);
  newNode.addEventListener('dragend', handleDragEnd);

  const inports = buttonMapping[data].inports;
  const outports = buttonMapping[data].outports;
  newNode.style.height = Math.max(inports.length, outports.length) * 
      nodeVerticalPadding + nodeTopPadding + 'px';

  for (let i = 0; i < inports.length; i++) {
    createPort(newNode, i, inports[i], false);
  }
  for (let i = 0; i < outports.length; i++) {
    createPort(newNode, i, outports[i], true);
  }
  nodeIdCounter++;
  return newNode ;
}

function createPort(node, idx, portName, isOutport) {
  const port = document.createElement('div');
  port.className = 'circle';
  const portId = `port-${idx}`;
  port.setAttribute('id', portId);
  let portType = portName;
  if (portName.includes('_')) {
    portType = portName.split('_')[1]
  }
  port.setAttribute('type', portType);
  port.style.top = nodeTopPadding + idx * nodeVerticalPadding + 'px';
  const text = document.createElement('div');
  text.className = 'circle-text';
  port.appendChild(text);

  if (isOutport) {
    port.style.left = 100 + 'px';
    text.style.left = -30 + 'px';
    text.textContent = portName;
    port.addEventListener('mousedown', startDrawing);

    // port.addEventListener('mousedown', function(event) {
    //   event.preventDefault();
    // });
  }
  else {
    if (portName.includes("input_")) {
      text.textContent = portName.split('_')[1];
      const textbox = createTextbox();
      port.appendChild(textbox);
    }
    else {
      text.textContent = portName;
      port.addEventListener('mousedown', function(event) {
        event.preventDefault();
      });
      port.addEventListener('mouseup', endDrawing);
      // port.addEventListener('mouseup', function(event) {
      //   event.preventDefault();

      // })
    }
    
  }

  node.appendChild(port);
}

function createTextbox() {
const textbox = document.createElement("input");
textbox.type = "text";
textbox.className = "textbox";
return textbox;
}

function moveNode(targetPos, node){
  node.style.left = targetPos.x + 'px';
  node.style.top = targetPos.y + 'px';

}

function drawConnections() {
  const canvas = document.getElementById("canvas");
  const ctx = canvas.getContext('2d');

  ctx.clearRect(0, 0, canvas.width, canvas.height);
  connections.forEach(function(conn) {

    const pos0 = conn.start.port.getBoundingClientRect();
    const pos1 = conn.finish.port.getBoundingClientRect();

    const startPos = { x:pos0.left + pos0.width / 2 - dropArea.offsetLeft, y:pos0.top + pos0.height / 2 - dropArea.offsetTop};
    const endPos = { x:pos1.left + pos1.width / 2 - dropArea.offsetLeft, y:pos1.top + pos1.height / 2 - dropArea.offsetTop };

    // console.log(startPos);
    // console.log(endPos);
    ctx.beginPath();
    ctx.moveTo(startPos.x, startPos.y);
    ctx.lineTo(endPos.x, endPos.y);
    // ctx.moveTo(100, 100);
    // ctx.lineTo(200, 200);
    ctx.strokeStyle = 'red';
    ctx.lineWidth = 2;
    ctx.stroke();
  });
  
  
}

function isPortAvailable(node, port) {
  let isAvailable = true;
  for (let i = 0; i < connections.length; i++) {
    const lconn = connections[i];
    const lFinishNode = lconn.finish.node.getAttribute('id');

    if (node == lFinishNode) {
      const lFinishPort = lconn.finish.port.getAttribute('id');

      if (port == lFinishPort) {
        isAvailable = false;
        break;
      }
    }
  }

  return isAvailable;
}
