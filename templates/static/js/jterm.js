const socket = io();
socket.connect(window.location.origin);
const pageUID = window.location.pathname.split("/")[2];

$(function () {
  $("body").terminal(
    function (command, term) {
      socket.emit("command", { cmd: command, uid: pageUID });
    },
    {
      greetings: document.getElementById("greetings").innerHTML,
      //prompt: '>',
      completion: false,
      ansi: true,
    }
  );

  socket.on("result", function (response) {
    if (response["uid"] === pageUID) {
      console.log(response["result"]);
      const cleanedResult = response["result"];
      $("body").terminal().echo(cleanedResult);
    }
  });
});
