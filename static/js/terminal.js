document.getElementById("terminal").src =
  window.location.origin + "/term/" + window.location.pathname.split("/")[2];

function fullscreen() {
  window.location.href = "/term/" + window.location.pathname.split("/")[2];
}

if (!show_logout_button) {
  document.querySelector('li > a[href="/logout"]').parentElement.style.display = 'none';
}

function ctrl() {
  fetch("/ctrl", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      device_id: window.location.pathname.split("/")[2],
    }),
  })
    .then((response) => {
      console.log("Response from server:", response);
    })
    .catch((error) => {
      console.error("Error sending delete request:", error);
      window.location.href = "/";
    });
}

function disconnect() {
  fetch("/delete", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      device_id: window.location.pathname.split("/")[2],
    }),
  })
    .then((response) => {
      console.log("Response from server:", response);
      window.location.href = "/";
    })
    .catch((error) => {
      console.error("Error sending delete request:", error);
    });
}


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