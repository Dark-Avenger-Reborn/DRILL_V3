var socket = io();
socket.connect(window.location.origin);
const pageSID = window.location.pathname.split("/")[2];

send_mouse_input = false
send_keyboard_input = false

if (!show_logout_button) {
  document.querySelector('li > a[href="/logout"]').parentElement.style.display = 'none';
}

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
  send_mouse_input = !send_keyboard_input;
});

document.getElementById("keyboardInput").addEventListener("click", () => {
  send_keyboard_input = !send_keyboard_input
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

// Handle screenshot event with zlib decompression
socket.on("screenshot", function (response) {
  if (response["uid"] == pageSID && response["image"]) {
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

// Sending information
var element = document.getElementById("capturedImage");

if (element.matches(":hover")) {
  console.log("Mouse is over the element now.");
}

document.getElementById("capturedImage").onmousemove = function (e) {
  if (send_mouse_input) {
    // e = Mouse click event.
    var rect = e.target.getBoundingClientRect();
    var x = e.clientX - rect.left; // x position within the element.
    var y = e.clientY - rect.top; // y position within the element.

    var percentX = (x / rect.width); // Percentage of width
    var percentY = (y / rect.height); // Percentage of height

    sio.emit("mouse_input", { uid: pageSID, x: percentX, y:percentY })
    console.log("Left? : " + percentX*100 + " ; Top? : " + percentY*100 + ".");
  }
};
