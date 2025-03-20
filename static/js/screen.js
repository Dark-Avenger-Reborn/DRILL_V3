var socket = io();
socket.connect(window.location.origin);
const pageSID = window.location.pathname.split("/")[2];

send_mouse_input = false;
send_keyboard_input = false;

screen_or_camera = true;
josh_allen = false;

if (!show_logout_button) {
  document.querySelector('li > a[href="/logout"]').parentElement.style.display = 'none';
}

const startButton = document.getElementById("start");
const stopButton = document.getElementById("stop");

startButton.addEventListener("click", () => {
  socket.emit("screen_status", { status: "start", uid: pageSID });
  josh_allen = true;
});

stopButton.addEventListener("click", () => {
  socket.emit("screen_status", { status: "stop", uid: pageSID });
  document.getElementById("capturedImage").src = ``;
  josh_allen = false;
});

// New button listeners
document.getElementById("mouseInput").addEventListener("click", () => {
  send_mouse_input = !send_mouse_input;
});

document.getElementById("keyboardInput").addEventListener("click", () => {
  send_keyboard_input = !send_keyboard_input;
});

/*
document.getElementById("lockKeyboard").addEventListener("click", () => {
  socket.emit("lock_keyboard", { uid: pageSID });
});

document.getElementById("lockMouse").addEventListener("click", () => {
  socket.emit("lock_mouse", { uid: pageSID });
});
*/

// Slider button event listeners
const sliderHighlight = document.getElementById("sliderHighlight");
const screenButton = document.getElementById("screenButton");
const cameraButton = document.getElementById("cameraButton");

screenButton.addEventListener("click", () => {
  socket.emit("switch_screen", { screen: "screen", uid: pageSID });
  sliderHighlight.style.left = "0"; // Move highlight to Screen
  screenButton.style.color = "#fff"; // Change text color to white
  cameraButton.style.color = "#1e1e1e"; // Reset Camera button text color
  screen_or_camera = true;
});

cameraButton.addEventListener("click", () => {
  socket.emit("switch_screen", { screen: "camera", uid: pageSID });
  sliderHighlight.style.left = "50%"; // Move highlight to Camera
  cameraButton.style.color = "#fff"; // Change text color to white
  screenButton.style.color = "#1e1e1e"; // Reset Screen button text color
  screen_or_camera = false;
});

// Handle screenshot event with zlib decompression
socket.on("screenshot", function (response) {
  if (response["uid"] == pageSID && response["image"] && josh_allen) {
    const compressedData = response["image"].data || response["image"];
    const byteArray = new Uint8Array(compressedData);

    try {
      // Decompress the data using pako
      const decompressedData = pako.inflate(byteArray);

      // Convert the decompressed data to a Base64 string
      const base64String = btoa(
        decompressedData.reduce(
          (data, byte) => data + String.fromCharCode(byte),
          ""
        )
      );

      // Update the image source with the decompressed data
      document.getElementById("capturedImage").src = `data:image/jpeg;base64,${base64String}`;
    } catch (error) {
      console.error("Failed to decompress the image data:", error);
    }
  }
});

document.onvisibilitychange = function () {
  if (document.visibilityState === "hidden") {
    socket.emit("screen_status", { status: "stop", uid: pageSID });
  }
};

// Dropdown functionality for screen selection
const screenDropdown = document.getElementById("screenDropdown");

let previousScreenCount = null; // Initialize a variable to store the previous screen count

socket.on("screen_count", function (response) {
  if (response["uid"] == pageSID) {
    const screenCount = response['screen_count'];

    // Check if the screen count has changed
    if (screenCount !== previousScreenCount) {
      previousScreenCount = screenCount; // Update the previous screen count

      // Clear existing options
      screenDropdown.innerHTML = '';

      // Populate the dropdown with options
      for (let i = 1; i <= screenCount; i++) {
        const option = document.createElement("option");
        option.value = i;
        option.textContent = `Screen ${i}`;
        screenDropdown.appendChild(option);
      }
    }
  }
});


// Event listener for dropdown change
screenDropdown.addEventListener("change", (event) => {
  const selectedScreen = event.target.value;
  socket.emit("change_screen_number", { screenNumber: selectedScreen, uid: pageSID });
});

// Sending mouse input
document.getElementById("capturedImage").addEventListener("mousemove", function (e) {
  if (send_mouse_input && screen_or_camera) {
    var rect = e.target.getBoundingClientRect();
    var x = e.clientX - rect.left; // x position within the element.
    var y = e.clientY - rect.top; // y position within the element.

    var percentX = (x / rect.width); // Percentage of width
    var percentY = (y / rect.height); // Percentage of height

    socket.emit("mouse_input", { uid: pageSID, x: percentX, y: percentY });
  }
});

/* Mouse click events
document.getElementById("capturedImage").onclick = function (e) {
  if (send_mouse_input && screen_or_camera) {
    socket.emit("mouse_click", { uid: pageSID });
  }
}; */

function handleMouseEvent(e) {
  if (send_mouse_input && screen_or_camera) {
    if (event.which == 3) {
      socket.emit("mouse_click_right", { uid: pageSID, going: true });
    } else {
      socket.emit("mouse_click", { uid: pageSID, going: true});
    }
  }
}

function handleMouseEvent2(e) {
  if (send_mouse_input && screen_or_camera) {
    if (event.which == 3) {
      socket.emit("mouse_click_right", { uid: pageSID, going: false });
    } else {
      socket.emit("mouse_click", { uid: pageSID, going: false });
    }
  }
}

capturedImage.addEventListener("mousedown", handleMouseEvent);
capturedImage.addEventListener("mouseup", handleMouseEvent2);

/*document.getElementById("capturedImage").oncontextmenu = function (e) {
  if (send_mouse_input && screen_or_camera) {
    socket.emit("mouse_click_right", { uid: pageSID });
  }
};*/

document.querySelectorAll('.screenshot').forEach(function(image) {
  image.addEventListener('contextmenu', function(e) {
    e.preventDefault();
  });
});

document.getElementById("capturedImage").addEventListener("wheel", function (e) {
  if (send_mouse_input && screen_or_camera) {
    var scrollDelta = e.deltaY || e.detail || e.wheelDelta; // Get the scroll delta (scroll direction)

    // You can emit the scroll data to the server if necessary
    socket.emit("mouse_scroll", { uid: pageSID, delta: scrollDelta });

    // Prevent the default scrolling behavior (if needed)
  }
  e.preventDefault();
});


document.querySelector('img').addEventListener('dragstart', function(event) {
  event.preventDefault(); // Prevents the default dragging behavior
});





let keyDownTime = {};  // To store the time when each key is pressed

document.addEventListener('keydown', function(event) {
  if (send_keyboard_input && screen_or_camera) {
    const currentTime = Date.now();
    const key = event.key;

    // Record the time when the key is pressed down
    if (!keyDownTime[key]) {
      keyDownTime[key] = currentTime;
    }

    console.log('Key Down:', event.key);

    // Emit key_press only after waiting 200ms (if key is still being held down)
    setTimeout(() => {
      if (keyDownTime[key] && (Date.now() - keyDownTime[key] >= 200)) {
        socket.emit("key_press", { uid: pageSID, key: event.key, going: true });
      }
    }, 200);

    event.preventDefault();
  }
});

document.addEventListener('keyup', function(event) {
  if (send_keyboard_input && screen_or_camera) {
    const key = event.key;
    const keyPressedDuration = Date.now() - keyDownTime[key];

    console.log('Key Up:', event.key);

    // Emit key_press_short if the key was held for less than 200ms
    if (keyPressedDuration < 200) {
      socket.emit("key_press_short", { uid: pageSID, key: event.key });
    } else {
      // Emit key_press with going: false to indicate key release
    socket.emit("key_press", { uid: pageSID, key: event.key, going: false });
    }

    // Reset the keyDownTime for the key after it's released
    delete keyDownTime[key];

    event.preventDefault();
  }
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
