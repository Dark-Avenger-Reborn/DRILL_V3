const socket = io();
socket.connect(window.location.origin)
const pageUID = window.location.pathname.split("/")[2];

function generateRandomKey(length) {
  const characters = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789!@#$%^&*()_+[]{}|;:,.<>?';
  let result = '';
  const charactersLength = characters.length;
  for (let i = 0; i < length; i++) {
    result += characters.charAt(Math.floor(Math.random() * charactersLength));
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


const term = new Terminal({
    cursorBlink: true,
    fontSize: 14,
    theme: {
      background: getComputedStyle(document.documentElement).getPropertyValue("--background"),
      foreground: getComputedStyle(document.documentElement).getPropertyValue("--color"),
    }
});
term.open(document.getElementById("terminal"));

socket.on("result", function (response) {
  if (response["result"]["uid"] === pageUID && response["result"]['key'] === userKey) {
    console.log(response["result"]);
    const cleanedResult = response["result"]["result"];
    term.write(cleanedResult);
  }
});

// Send every keystroke directly to the backend (including Ctrl commands)
term.onData(data => {
  console.log(data)
  socket.emit("command", { cmd: data, uid: pageUID, key: userKey });
});