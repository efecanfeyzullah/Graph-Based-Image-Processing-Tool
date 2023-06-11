// Mapping of button IDs to titles
const buttonMapping = {
    button1: "Title 1",
    button2: "Title 2",
    button3: "Title 3",
    button4: "Title 4",
    button5: "Title 5",
  };
  
  // Function to handle the drag start event
  function handleDragStart(event) {
    const target = event.target;
    event.dataTransfer.setData("text/plain", target.id);
    target.classList.add("dragging");
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
  
    const data = event.dataTransfer.getData("text/plain");
    const droppedElement = document.getElementById(data);
  
    if (droppedElement) {
      const dropArea = event.currentTarget;

  
      const newRectangle = document.createElement("div");
      newRectangle.className = "rectangle";
      const offsetX = event.clientX - 50;
      const offsetY = event.clientY - 25;
      newRectangle.textContent = buttonMapping[data];
      newRectangle.style.left = offsetX + "px";
      newRectangle.style.top = offsetY + "px";
  
      dropArea.appendChild(newRectangle);
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
  