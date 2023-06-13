$(document).ready(function() {
    // Retrieve the button element by its ID
    var button = $("#sendcommandbutton");
    var csrfToken = $('[name=csrfmiddlewaretoken]').val();
    console.log(csrfToken);
    // Attach an event listener to the button
    button.on("click", function() {
  
      $.ajax({
        url: '',
        type: 'POST',
        headers: {
          'X-CSRF-Token': csrfToken,
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
  });