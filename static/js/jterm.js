const socket = io();
socket.connect(window.location.origin);
const pageUID = window.location.pathname.split("/")[2];

$(function () {
  $("body").terminal(
    function (command, term) {
      socket.emit("command", { cmd: command, uid: pageUID });
    },
    {
      greetings: document.getElementById("greetings").innerHTML,
      //prompt: '>',
      completion: false,
      ansi: true,
      background: color,
    }
  );

  socket.on("result", function (response) {
    if (response["uid"] === pageUID) {
      console.log(response["result"]);
      const cleanedResult = response["result"];
      $("body").terminal().echo(cleanedResult);
    }
  });
});


function showPopupAlert(message, type) {
  const popup = document.getElementById('popup-alert');
  const popupMessage = document.getElementById('popup-message');
  popupMessage.textContent = message;
  
  // Add the type class (success or error)
  popup.classList.remove('success', 'error');
  popup.classList.add(type);

  // Show the popup
  popup.style.display = 'block';

  // Hide the popup after 3 seconds or when OK is clicked
  setTimeout(() => {
    popup.style.display = 'none';
  }, 3000);
}

// Example usage of showPopupAlert
document.getElementById('popup-ok-btn').addEventListener('click', function () {
  const popup = document.getElementById('popup-alert');
  popup.style.display = 'none';
});