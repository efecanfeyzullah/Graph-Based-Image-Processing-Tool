// Mapping of button IDs to titles
const buttonMapping = {
    button1: { name: "Title 1", inports: ["Image", "left", "right", "top", "bottom"], outports: [] },
    button2: { name: "Title 2", inports: [], outports: [] },
    button3: { name: "Title 3", inports: [], outports: [] },
    button4: { name: "Title 4", inports: [], outports: [] },
    button5: { name: "Title 5", inports: [], outports: [] }
  };
  
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
    newRectangle.style.height = inports.length * 15 + 15 + 'px';
    for (let i = 0; i < inports.length; i++) {
        createPort(newRectangle, i, inports[i]);
    }
    rectangleIdCounter++;
    return newRectangle ;
}

function createPort(rectangle, idx, inport) {
    const port = document.createElement('div');
    port.className = 'circle';
    const padding = 15;
    port.style.top = padding + idx * padding + 'px';
    const text = document.createElement('div');
    text.className = 'circle-text';
    text.textContent = inport;
    port.appendChild(text);
    port.addEventListener('mousedown', function(event) {
        event.preventDefault();
    });

    rectangle.appendChild(port);
}

function moveRectangle(targetPos, rectangle){
    rectangle.style.left = targetPos.x + 'px';
    rectangle.style.top = targetPos.y + 'px';

}
  