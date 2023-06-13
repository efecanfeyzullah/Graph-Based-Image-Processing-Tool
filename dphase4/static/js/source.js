// Mapping of button IDs to titles
const buttonMapping = {
  CropImage: { name: "CropImage", inports: ["Image", "left_int", "top_int", "right_int", "bottom_int"], outports: ["Image"] },
  LoadImage: { name: "LoadImage", inports: [], outports: ["Image"] },
  GetFloat: { name: "GetFloat", inports: ["input_float"], outports: ["float"] },
  GetInteger: { name: "GetInteger", inports: ["input_int"], outports: ["int"] },
  GetString: { name: "GetString", inports: ["input_string"], outports: ["string"] },
  DupImage: { name: "DupImage", inports: ["Image"], outports: ["Image", "Image"] },
};

const nodeTopPadding = 30;
const nodeVerticalPadding = 20;

let lineStart = { x:0, y:0 };
let lineFinish = { x:0, y:0 };

var connectionStart = { node:"", port:"" };
var connectionFinish = { node:"", port:"" };
var connections = []
var nodes = []

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
canvas.width = dropArea.offsetWidth * 2;
canvas.height = dropArea.offsetHeight * 2;

// Position the canvas on top of the drop-area
canvas.style.position = 'absolute';
canvas.style.top = dropArea.offsetTop + 'px';
canvas.style.left = dropArea.offsetLeft + 'px';
canvas.style.pointerEvents = 'none';
// Append the canvas to the document body
document.body.appendChild(canvas);

// drawConnections();


////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
// functions below
////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////////
function startDrawing(event) {
  event.preventDefault();
  lineStart = { x:event.clientX, y:event.clientY };
  const target = event.target;
  target.classList.add('selected');
  connectionStart = { node:target.parentNode, port:target};
  // console.log(connectionStart);
}

function endDrawing(event) {
  const target = event.target;

  lineFinish = { x:event.clientX, y:event.clientY };
  connectionFinish = { node:target.parentNode, port:target};

  let connection = {start:connectionStart, finish:connectionFinish};
  let finishPortId = connectionFinish.node.getAttribute('id');

  if (connectionStart == null) {
    connectionFinish = null;
    return;
  }

  connectionStart.port.classList.remove('selected');

  if (connectionFinish == null || 
    connectionStart.node.getAttribute('id') == finishPortId) {
    connectionStart = null;
    connectionFinish = null;
    return;
  }
  
  if (connectionStart.port.getAttribute('type') != connectionFinish.port.getAttribute('type')) {
    connectionStart = null;
    connectionFinish = null;
    return;
  }

  const connectionCheck = isPortAvailable(connectionFinish.node.getAttribute('id'), connectionFinish.port.getAttribute('id'));
  
  if (connectionCheck.isAvailable) {
    const node0Id = connectionStart.node.getAttribute('id').split('-')[1];
    const node1Id = connectionFinish.node.getAttribute('id').split('-')[1];
    const port0Id = connectionStart.port.getAttribute('id').split('-')[1];
    const port1Id = connectionFinish.port.getAttribute('id').split('-')[1];

    $.ajax({
      url: '',
      type: 'POST',
      headers: {
        'X-CSRFToken': getCookie('csrftoken')
      },
      data: {
        'command': `connect ${node0Id} ${port0Id} ${node1Id} ${port1Id}`
      },
      success: function(response) {
        connections.push(connection);
        const finishPort = connectionFinish.port;
        connectionStart.port.classList.remove('selected');

        const enableHover = function(event) { event.preventDefault(); finishPort.classList.add('hovered');};
        const disableHover = function(event) { event.preventDefault(); finishPort.classList.remove('hovered');};
        const enableClick = function(event) {
          event.preventDefault();
          $.ajax({
            url: '',
            type: 'POST',
            headers: {
              'X-CSRFToken': getCookie('csrftoken')
            },
            data: {
              'command': `disconnect ${node0Id} ${port0Id} ${node1Id} ${port1Id}`
            },
            success: function(response) {
              // edit this
              const existingEntry = isPortAvailable(connection.finish.node.getAttribute('id'), connection.finish.port.getAttribute('id'));

              connections.splice(existingEntry.foundIdx, 1);
              drawConnections();

              finishPort.classList.remove('hovered');
              finishPort.removeEventListener("mouseover", enableHover);
              finishPort.removeEventListener("mouseout", disableHover);
              finishPort.removeEventListener("mousedown", enableClick);
            },
            error: function(xhr, status, error) {
              // Handle error response
            }
          });
          
        };
        finishPort.addEventListener("mouseover", enableHover);
        finishPort.addEventListener("mouseout", disableHover);
        finishPort.addEventListener("mousedown", enableClick);
        connectionStart = null;
        connectionFinish = null;

        drawConnections();
        console.log(connections);
        console.log(response);
      },
      error: function(xhr, status, error) {
        // Handle error response
      }
    });
   
    }

    
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
      $.ajax({
        url: '',
        type: 'POST',
        headers: {
          'X-CSRFToken': getCookie('csrftoken')
        },
        data: {
          'command': `newnode ${buttonMapping[data].name}`
        },
        success: function(response) {
          const nodeId = response['serverresponse']['node_id'];
          const newNode = createNode(event, data, nodeId);
          nodes.push(newNode);
          dropArea.appendChild(newNode);
          console.log(response);
        },
        error: function(xhr, status, error) {
          // Handle error response
        }
      });
      
  }
  else if (classList.contains("node")){
      const targetPos = { x:event.clientX - 50, y:event.clientY - 25 };
      moveNode(targetPos, droppedElement);
      console.log(droppedElement.getAttribute("id"));
      drawConnections();
  }
}

function createNode(event, data, nodeId) {
  const offsetX = event.clientX - 50;
  const offsetY = event.clientY - 25;

  const newNode = document.createElement('div');
  newNode.className = 'node';
  newNode.textContent = buttonMapping[data].name;
  const nodeIdFull = `node-${nodeId}`;
  newNode.setAttribute('id', nodeIdFull);
  newNode.style.left = offsetX + 'px';
  newNode.style.top = offsetY + 'px';

  newNode.draggable = true;
  newNode.addEventListener('dragstart', handleDragStart);
  newNode.addEventListener('dragend', handleDragEnd);

  createDeleteButton(newNode);

  const inports = buttonMapping[data].inports;
  const outports = buttonMapping[data].outports;
  newNode.style.height = Math.max(inports.length, outports.length) * 
      nodeVerticalPadding + nodeTopPadding + 'px';

  newNode.inports = [];
  newNode.outports = [];
  for (let i = 0; i < inports.length; i++) {
    var port = createPort(newNode, i, inports[i], false);
    newNode.inports.push(port);
  }
  for (let i = 0; i < outports.length; i++) {
    var port = createPort(newNode, i, outports[i], true);
    newNode.outports.push(port);
  }

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
    }
    
  }

  node.appendChild(port);
  return port;
}

function createDeleteButton(node) {
  const deleteBtn = document.createElement('div');
  deleteBtn.className = 'delete-button';
  deleteBtn.style.top = 0 + 'px';
  deleteBtn.addEventListener('mousedown', function(event) {
    event.preventDefault();
    $.ajax({
      url: '',
      type: 'POST',
      headers: {
        'X-CSRFToken': getCookie('csrftoken')
      },
      data: {
        'command': `deletenode ${node.getAttribute('id').split('-')[1]}`
      },
      success: function(response) {
        const conns = response['serverresponse']['connections'];
        const newConnections = []
        conns.forEach (function(conn) {
          var node0 = findNode(conn[0]).node;
          var node1 = findNode(conn[2]).node;
          var connStart = {node:node0, port:node0.outports[conn[1]]};
          var connFinish = {node:node1, port:node1.inports[conn[3]]};
          newConnections.push({start:connStart, finish:connFinish});
        });
        connections = newConnections;
        console.log(connections);
        drawConnections();
        node.remove();
      },
      error: function(xhr, status, error) {
        // Handle error response
      }
    });
  });  

  node.appendChild(deleteBtn);

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
  let result = { isAvailable:true, foundIdx:-1 };
  for (let i = 0; i < connections.length; i++) {
    const lconn = connections[i];
    const lFinishNode = lconn.finish.node.getAttribute('id');

    if (node == lFinishNode) {
      const lFinishPort = lconn.finish.port.getAttribute('id');

      if (port == lFinishPort) {
        result.isAvailable = false;
        result.foundIdx = i;
        break;
      }
    }
  }

  return result;
}


$(document).ready(function() {
  // Retrieve the newGraphButton element by its ID
  const newGraphButton = $("#NewGraph");
  const csrfToken = $('[name=csrfmiddlewaretoken]').val();
  console.log(csrfToken);
  // Attach an event listener to the newGraphButton
  newGraphButton.on("click", function() {
    $.ajax({
      url: '',
      type: 'POST',
      headers: {
        'X-CSRFToken': getCookie('csrftoken')
      },
      data: {
        'command': 'newgraph'
      },
      success: function(response) {
        // Handle success response
        console.log(response);
      },
      error: function(xhr, status, error) {
        // Handle error response
      }
    });
    
  });

  const openGraphButton = $("#OpenGraph");
  const graphIdText = $("#GraphIdText");
  openGraphButton.on("click", function() {
    $.ajax({
      url: '',
      type: 'POST',
      headers: {
        'X-CSRFToken': getCookie('csrftoken')
      },
      data: {
        'command': `open ${graphIdText.val()}`
      },
      success: function(response) {
        // Handle success response
        console.log(response);
      },
      error: function(xhr, status, error) {
        // Handle error response
      }
    });
  });
});

function getCookie(name) {
  var value = '; ' + document.cookie,
      parts = value.split('; ' + name + '=');
  if (parts.length == 2) return parts.pop().split(';').shift();
}

function resetConnections() {
  connections.forEach(function(conn) {
    var finishPort = conn.finish.port;
    // finishPort.removeEventListener('mousedown')
  });
}

function findNode(nodeId) {
  var found = false;
  var idx = -1;
  var node = null;
  for (let i = 0; i < nodes.length; i++) {
    if (nodes[i].getAttribute('id').split('-')[1] == nodeId) {
      found = true;
      idx = i;
      node = nodes[i];
      break;
    }
  }

  return {found:found, idx:idx, node:node};
}






