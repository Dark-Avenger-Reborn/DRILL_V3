document.addEventListener("DOMContentLoaded", function () {
  const socket = io();
  socket.connect(window.location.origin);

  const term = new Terminal({
    cursorBlink: true, // Make cursor blink
    fontSize: 14,
    theme: {
      background: getComputedStyle(document.documentElement).getPropertyValue("--background"),
      foreground: getComputedStyle(document.documentElement).getPropertyValue("--color"),
    }
  });

  term.open(document.getElementById("terminal"));

  const pageUID = window.location.pathname.split("/")[2];

  function isSpecialKey(data) {
    return [
      "\x1B[A", "\x1B[B", "\x1B[C", "\x1B[D",  // Arrow keys
      "\x1B[1~", "\x1B[4~", "\x1B[5~", "\x1B[6~",  // Home, End, Page Up, Page Down
      "\x1B[H", "\x1B[F",  // Alternative Home/End keys
      "\x03", "\x1A",  // Ctrl+C, Ctrl+Z (handled by the shell)
      "\t"  // Tab key
    ].includes(data);
  }

  // Send raw keystrokes to the server
  term.onData((data) => {
    if (data === "\r") {  
        term.write("\r\n");  // Enter key: Move to new line
    } else if (data === "\x7F") {  
        // Handle backspace (remove the last character if possible)
        term.write("\b \b");
    } else if(!(isSpecialKey(data))) {  
        term.write(data);  // Echo input locally unless it's a special key
    }
    socket.emit("command", { cmd: data, uid: pageUID });
  });
  // Receive output from server
  socket.on("result", function (response) {
    if (response["uid"] === pageUID) {
      term.write(response["result"]);
    }
  });
});