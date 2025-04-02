document.getElementById("terminal").src =
  window.location.origin + "/term/" + window.location.pathname.split("/")[2];

function fullscreen() {
  window.location.href = "/term/" + window.location.pathname.split("/")[2];
}

if (!show_logout_button) {
  document.querySelector('li > a[href="/logout"]').parentElement.style.display = 'none';
}

function generateRandomKey(length) {
  const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+[]{}|;:,.<>?';
  let result = '';
  for (let i = 0; i < length; i++) {
    result += characters.charAt(Math.floor(Math.random() * characters.length));
  }
  return result;
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

let userKey = getCookie('userKey');
if (!userKey) {
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
    .then(async (response) => {
      const data = await response.json();
      if (response.status != 200) {
        showPopupAlert("An error occurred : "+data.result, 'error')
      } else {
        showPopupAlert(data.result, "success")
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
    .then(async (response) => {
      console.log("Response from server:", response);
      const data = await response.json();
      if (response.status != 200) {
        showPopupAlert("An error occurred : "+data.result, 'error')
      }
      window.location.href = "/";
    })
    .catch((error) => {
      showPopupAlert("An error occurred : "+error, 'error')
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