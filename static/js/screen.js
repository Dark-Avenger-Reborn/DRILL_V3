var socket = io();
socket.connect(window.location.origin);
const pageSID = window.location.pathname.split("/")[2];

send_mouse_input = false;
send_keyboard_input = false;

screen_or_camera = true;
josh_allen = false;

if (!show_logout_button) {
  document.querySelector('li > a[href="/logout"]').parentElement.style.display =
    "none";
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

// Input toggle buttons
const mouseBtn = document.getElementById("mouseInput");
const keyboardBtn = document.getElementById("keyboardInput");

function updateInputButtonVisuals() {
  if (send_mouse_input) {
    mouseBtn.classList.add("toggle-enabled");
    mouseBtn.classList.remove("toggle-disabled");
    mouseBtn.textContent = "Disable Mouse Input";
  } else {
    mouseBtn.classList.remove("toggle-enabled");
    mouseBtn.classList.add("toggle-disabled");
    mouseBtn.textContent = "Enable Mouse Input";
  }

  if (send_keyboard_input) {
    keyboardBtn.classList.add("toggle-enabled");
    keyboardBtn.classList.remove("toggle-disabled");
    keyboardBtn.textContent = "Disable Keyboard Input";
  } else {
    keyboardBtn.classList.remove("toggle-enabled");
    keyboardBtn.classList.add("toggle-disabled");
    keyboardBtn.textContent = "Enable Keyboard Input";
  }
}

function disableInputButtons() {
  mouseBtn.disabled = true;
  keyboardBtn.disabled = true;
  mouseBtn.classList.remove("toggle-enabled", "toggle-disabled");
  keyboardBtn.classList.remove("toggle-enabled", "toggle-disabled");
}

function enableInputButtonsIfValid() {
  if (screen_or_camera && screenDropdown.value === "1") {
    mouseBtn.disabled = false;
    keyboardBtn.disabled = false;
    updateInputButtonVisuals();
  } else {
    disableInputButtons();
  }
}

// Mouse toggle
mouseBtn.addEventListener("click", () => {
  if (mouseBtn.disabled || screenDropdown.value !== "1" || !screen_or_camera) return;
  send_mouse_input = !send_mouse_input;
  updateInputButtonVisuals();
});

// Keyboard toggle
keyboardBtn.addEventListener("click", () => {
  if (keyboardBtn.disabled || screenDropdown.value !== "1" || !screen_or_camera) return;
  send_keyboard_input = !send_keyboard_input;
  updateInputButtonVisuals();
});

// Slider button logic
const sliderHighlight = document.getElementById("sliderHighlight");
const screenButton = document.getElementById("screenButton");
const cameraButton = document.getElementById("cameraButton");

screenButton.addEventListener("click", () => {
  socket.emit("switch_screen", { screen: "screen", uid: pageSID });
  sliderHighlight.style.left = "0";
  screenButton.style.color = "#fff";
  cameraButton.style.color = "#1e1e1e";
  screen_or_camera = true;

  enableInputButtonsIfValid();
});

cameraButton.addEventListener("click", () => {
  socket.emit("switch_screen", { screen: "camera", uid: pageSID });
  sliderHighlight.style.left = "50%";
  cameraButton.style.color = "#fff";
  screenButton.style.color = "#1e1e1e";
  screen_or_camera = false;

  disableInputButtons();
});

// Screenshot event
socket.on("screenshot", function (response) {
  response = JSON.parse(response);
  if (String(response["uid"]).trim() == String(pageSID).trim() && response["image"] && josh_allen) {
    function latin1ToByteArray(str) {
      const arr = new Uint8Array(str.length);
      for (let i = 0; i < str.length; ++i) {
        arr[i] = str.charCodeAt(i) & 0xff;
      }
      return arr;
    }

    const compressedData = response["image"].data || response["image"];
    const byteArray = latin1ToByteArray(compressedData);

    let decompressedData;
    try {
      decompressedData = pako.inflate(byteArray);
    } catch (e) {
      console.error("Failed to decompress the image data:", e);
      return;
    }

    const base64String = btoa(
      decompressedData.reduce(
        (data, byte) => data + String.fromCharCode(byte),
        ""
      )
    );

    document.getElementById("capturedImage").src = `data:image/jpeg;base64,${base64String}`;
  }
});

document.onvisibilitychange = function () {
  if (document.visibilityState === "hidden") {
    socket.emit("screen_status", { status: "stop", uid: pageSID });
  }
};

// Screen dropdown logic
const screenDropdown = document.getElementById("screenDropdown");
let previousScreenCount = null;

socket.on("screen_count", function (response) {
  response = JSON.parse(response);
  if (String(response["uid"]).trim() == String(pageSID).trim()) {
    const screenCount = response["screen_count"];
    if (screenCount !== previousScreenCount) {
      previousScreenCount = screenCount;
      screenDropdown.innerHTML = "";
      for (let i = 1; i <= screenCount; i++) {
        const option = document.createElement("option");
        option.value = i;
        option.textContent = `Screen ${i}`;
        screenDropdown.appendChild(option);
      }
    }
  }
});

screenDropdown.addEventListener("change", (event) => {
  const selectedScreen = event.target.value;
  socket.emit("change_screen_number", {
    screenNumber: selectedScreen,
    uid: pageSID,
  });
  enableInputButtonsIfValid();
});

// Mouse movement input
document.getElementById("capturedImage").addEventListener("mousemove", function (e) {
  if (send_mouse_input && screen_or_camera) {
    var rect = e.target.getBoundingClientRect();
    var x = e.clientX - rect.left;
    var y = e.clientY - rect.top;
    var percentX = x / rect.width;
    var percentY = y / rect.height;
    socket.emit("mouse_input", { uid: pageSID, x: percentX, y: percentY });
  }
});

function handleMouseEvent(e) {
  if (send_mouse_input && screen_or_camera) {
    if (event.which == 3) {
      socket.emit("mouse_click_right", { uid: pageSID, going: true });
    } else {
      socket.emit("mouse_click", { uid: pageSID, going: true });
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

document.getElementById("capturedImage").addEventListener("mousedown", handleMouseEvent);
document.getElementById("capturedImage").addEventListener("mouseup", handleMouseEvent2);

document.querySelectorAll(".screenshot").forEach(function (image) {
  image.addEventListener("contextmenu", function (e) {
    e.preventDefault();
  });
});

document.getElementById("capturedImage").addEventListener("wheel", function (e) {
  if (send_mouse_input && screen_or_camera) {
    var scrollDelta = e.deltaY || e.detail || e.wheelDelta;
    socket.emit("mouse_scroll", { uid: pageSID, delta: scrollDelta });
  }
  e.preventDefault();
});

document.querySelector("img").addEventListener("dragstart", function (event) {
  event.preventDefault();
});

let keyDownTime = {};

document.addEventListener("keydown", function (event) {
  if (send_keyboard_input && screen_or_camera) {
    const currentTime = Date.now();
    const key = event.key;

    if (!keyDownTime[key]) {
      keyDownTime[key] = currentTime;
    }

    setTimeout(() => {
      if (keyDownTime[key] && Date.now() - keyDownTime[key] >= 200) {
        socket.emit("key_press", { uid: pageSID, key: event.key, going: true });
      }
    }, 200);

    event.preventDefault();
  }
});

document.addEventListener("keyup", function (event) {
  if (send_keyboard_input && screen_or_camera) {
    const key = event.key;
    const keyPressedDuration = Date.now() - keyDownTime[key];

    if (keyPressedDuration < 200) {
      socket.emit("key_press_short", { uid: pageSID, key: event.key });
    } else {
      socket.emit("key_press", { uid: pageSID, key: event.key, going: false });
    }

    delete keyDownTime[key];
    event.preventDefault();
  }
});

function showPopupAlert(message, type) {
  const popup = document.getElementById("popup-alert");
  const popupMessage = document.getElementById("popup-message");
  popupMessage.textContent = message;

  popup.classList.remove("success", "error");
  popup.classList.add(type);

  popup.style.display = "block";

  setTimeout(() => {
    popup.style.display = "none";
  }, 3000);
}

document.getElementById("popup-ok-btn").addEventListener("click", function () {
  const popup = document.getElementById("popup-alert");
  popup.style.display = "none";
});
