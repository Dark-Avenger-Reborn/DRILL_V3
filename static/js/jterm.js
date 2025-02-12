const socket = io();
socket.connect(window.location.origin)
const pageUID = window.location.pathname.split("/")[2];

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
  if (response["uid"] === pageUID) {
    console.log(response["result"]);
    const cleanedResult = response["result"];
    term.write(cleanedResult);
  }
});

// Send every keystroke directly to the backend (including Ctrl commands)
term.onData(data => {
  console.log(data)
  socket.emit("command", { cmd: data, uid: pageUID });
});