// Mapping of button IDs to titles
const buttonMapping = {
    button1: { name: "CropImage", inports: ["Image", "input_left", "input_top", "input_right", "input_bottom"], outports: ["Image"] },
    button2: { name: "Title 2", inports: [], outports: ["Image"] },
    button3: { name: "Title 3", inports: ["Image"], outports: [] },
    button4: { name: "Title 4", inports: [], outports: [] },
    button5: { name: "Title 5", inports: [], outports: [] }
  };
  
  const rectangleTopPadding = 30;
  const rectangleVerticalPadding = 20;
  let rectangleIdCounter = 0;
  // Function to handle the drag start event
function handleDragStart(event) {
    const target = event.target;
        event.dataTransfer.setData('text/plain', target.id);
        target.classList.add('dragging');
}
  
function handleRectangleDragStart(event) {
    const target = event.target;
    event.dataTransfer.setData('text/plain', 'rectangle');
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

    if (droppedElement.classList.contains("menu-button")) {
        const dropArea = event.currentTarget;
        const newRectangle  = createRectangle(event, data);
        dropArea.appendChild(newRectangle);
    }
    else if (droppedElement.classList.contains("rectangle")){
        const targetPos = { x:event.clientX - 50, y:event.clientY - 25 };
        moveRectangle(targetPos, droppedElement);
        console.log(droppedElement.getAttribute("id"));
    }
  }
  
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

function createRectangle(event, data) {
    const offsetX = event.clientX - 50;
    const offsetY = event.clientY - 25;

    const newRectangle = document.createElement('div');
    newRectangle.className = 'rectangle';
    newRectangle.textContent = buttonMapping[data].name;
    const rectangleId = `rectangle-${rectangleIdCounter}`;
    newRectangle.setAttribute('id', rectangleId);
    newRectangle.style.left = offsetX + 'px';
    newRectangle.style.top = offsetY + 'px';

    newRectangle.draggable = true;
    newRectangle.addEventListener('dragstart', handleDragStart);
    newRectangle.addEventListener('dragend', handleDragEnd);

    const inports = buttonMapping[data].inports;
    const outports = buttonMapping[data].outports;
    newRectangle.style.height = inports.length * rectangleVerticalPadding + rectangleTopPadding + 'px';

    for (let i = 0; i < inports.length; i++) {
      createPort(newRectangle, i, inports[i], false);
    }
    for (let i = 0; i < outports.length; i++) {
      createPort(newRectangle, i, outports[i], true);
    }
    rectangleIdCounter++;
    return newRectangle ;
}

function createPort(rectangle, idx, portName, isOutport) {
    const port = document.createElement('div');
    port.className = 'circle';
    
    port.style.top = rectangleTopPadding + idx * rectangleVerticalPadding + 'px';
    const text = document.createElement('div');
    text.className = 'circle-text';
    port.appendChild(text);

    if (isOutport) {
      port.style.left = 100 + 'px';
      text.style.left = -30 + 'px';
      text.textContent = portName;
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
      }
      
    }

    rectangle.appendChild(port);
}

function createTextbox() {
  const textbox = document.createElement("input");
  textbox.type = "text";
  textbox.className = "textbox";
  return textbox;
}

function moveRectangle(targetPos, rectangle){
    rectangle.style.left = targetPos.x + 'px';
    rectangle.style.top = targetPos.y + 'px';

}
  