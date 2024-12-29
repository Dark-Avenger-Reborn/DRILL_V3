var socket = io();
socket.connect(window.location.origin);
const pageSID = window.location.pathname.split("/")[2];

const startButton = document.getElementById("start");
const stopButton = document.getElementById("stop");

startButton.addEventListener("click", () => {
  socket.emit("screen_status", { status: "start", uid: pageSID });
});

stopButton.addEventListener("click", () => {
  socket.emit("screen_status", { status: "stop", uid: pageSID });
});

// New button listeners
document.getElementById("mouseInput").addEventListener("click", () => {
  socket.emit("mouse_input", { uid: pageSID });
});

document.getElementById("keyboardInput").addEventListener("click", () => {
  socket.emit("keyboard_input", { uid: pageSID });
});

document.getElementById("lockKeyboard").addEventListener("click", () => {
  socket.emit("lock_keyboard", { uid: pageSID });
});

document.getElementById("lockMouse").addEventListener("click", () => {
  socket.emit("lock_mouse", { uid: pageSID });
});

// Slider button event listeners
const sliderHighlight = document.getElementById("sliderHighlight");
const screenButton = document.getElementById("screenButton");
const cameraButton = document.getElementById("cameraButton");

screenButton.addEventListener("click", () => {
  socket.emit("switch_screen", { screen: "screen", uid: pageSID });
  sliderHighlight.style.left = "0"; // Move highlight to Screen
  screenButton.style.color = "#fff"; // Change text color to white
  cameraButton.style.color = "#1e1e1e"; // Reset Camera button text color
});

cameraButton.addEventListener("click", () => {
  socket.emit("switch_screen", { screen: "camera", uid: pageSID });
  sliderHighlight.style.left = "50%"; // Move highlight to Camera
  cameraButton.style.color = "#fff"; // Change text color to white
  screenButton.style.color = "#1e1e1e"; // Reset Screen button text color
});

socket.on("screenshot", function (response) {
  if (response["uid"] == pageSID && response["image"]) {
    const imageData = response["image"].data || response["image"];
    const byteArray = new Uint8Array(imageData);
    const blob = new Blob([byteArray], { type: "image/jpeg" });
    const imageUrl = URL.createObjectURL(blob);

    // Create a temporary image element to preload the image
    const tempImage = new Image();
    tempImage.onload = function () {
      // Once the image is loaded, set it as the source of the displayed image
      document.getElementById("capturedImage").src = imageUrl;
      // Optionally revoke the object URL after a short delay
      setTimeout(() => URL.revokeObjectURL(imageUrl), 1000);
    };
    tempImage.src = imageUrl; // Trigger image preload
  }
});

document.onvisibilitychange = function () {
  if (document.visibilityState === "hidden") {
    socket.emit("screen_status", { status: "stop", uid: pageSID });
  }
};

//sending information
var element = document.getElementById("capturedImage");

if (element.matches(":hover")) {
  console.log("Mouse is over the element now.");
}

document.getElementById("capturedImage").onclick = function (e) {
  // e = Mouse click event.
  var rect = e.target.getBoundingClientRect();
  var x = e.clientX - rect.left; //x position within the element.
  var y = e.clientY - rect.top; //y position within the element.
  console.log("Left? : " + x + " ; Top? : " + y + ".");
};
