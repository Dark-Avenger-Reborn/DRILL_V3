document.getElementById("terminal").src =
  window.location.origin + "/term/" + window.location.pathname.split("/")[2];

function fullscreen() {
  window.location.href = "/term/" + window.location.pathname.split("/")[2];
}

if (!show_logout_button) {
  document.querySelector('li > a[href="/logout"]').parentElement.style.display = 'none';
}

function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
  return null;
}

function setCookie(name, value, days = 1) {
  const d = new Date();
  d.setTime(d.getTime() + (days * 24 * 60 * 60 * 1000));
  const expires = "expires=" + d.toUTCString();
  document.cookie = `${name}=${value}; ${expires}; path=/`;
}

// Check if the key exists in cookies
let userKey = getCookie('userKey');

if (!userKey) {
  // If no key, generate one and set it in cookies
  userKey = generateRandomKey(32);
  setCookie('userKey', userKey);
  console.log('Generated new key:', userKey);
} else {
  console.log('Existing key:', userKey);
}

function ctrl() {
  fetch("/ctrl", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      device_id: window.location.pathname.split("/")[2],
      key: userKey,
    }),
  })
    .then((response) => {
      if (response.status != 200) {
        showPopupAlert("An error occurred : "+response.json().result, 'error')
      } else {
        showPopupAlert(response.json().result, "success")
      }
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
      if (response.status != 200) {
        showPopupAlert("An error occurred : "+response.json().result, 'error')
      }
      window.location.href = "/";
    })
    .catch((error) => {
      showPopupAlert("An error occurred : "+response.json().json(), 'error')
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