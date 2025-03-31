// Initialize socket connection
const socket = io();
socket.connect(window.location.origin);
const pageUID = window.location.pathname.split("/")[2];

// Function to generate a random key
function generateRandomKey(length) {
  const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+[]{}|;:,.<>?';
  let result = '';
  for (let i = 0; i < length; i++) {
    result += characters.charAt(Math.floor(Math.random() * characters.length));
  }
  return result;
}

// Function to retrieve a cookie by name
function getCookie(name) {
  const value = `; ${document.cookie}`;
  const parts = value.split(`; ${name}=`);
  if (parts.length === 2) return parts.pop().split(';').shift();
  return null;
}

// Function to set a cookie
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

// Ensure xterm.js and the FitAddon are loaded
document.addEventListener("DOMContentLoaded", function () {
  const term = new Terminal({
    cursorBlink: true,
    fontSize: 14,
    theme: {
      background: getComputedStyle(document.documentElement).getPropertyValue("--background"),
      foreground: getComputedStyle(document.documentElement).getPropertyValue("--color"),
    }
  });

  // Initialize the fit addon
  const fitAddon = new window.FitAddon.FitAddon();
  term.loadAddon(fitAddon);

  // Open the terminal
  const terminalContainer = document.getElementById("terminal");
  term.open(terminalContainer);

  // Fit the terminal to the container
  fitAddon.fit();

  // Resize terminal when window resizes
  window.addEventListener("resize", () => {
    fitAddon.fit();
  });

  // Listen for data from the server and write it to the terminal
  socket.on("result", function (response) {
    if (response["result"]["uid"] === pageUID && response["result"]['key'] === userKey) {
      console.log(response["result"]);
      const cleanedResult = response["result"]["result"];
      term.write(cleanedResult);
    }
  });

  // Send every keystroke directly to the backend (including Ctrl commands)
  term.onData(data => {
    console.log(data);
    socket.emit("command", { cmd: data, uid: pageUID, key: userKey });
  });
});
