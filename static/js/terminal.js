document.getElementById("terminal").src =
  window.location.origin + "/term/" + window.location.pathname.split("/")[2];

function fullscreen() {
  window.location.href = "/term/" + window.location.pathname.split("/")[2];
}

function ctrl() {
  fetch("/ctrl", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      device_id: window.location.pathname.split("/")[2],
    }),
  })
    .then((response) => {
      console.log("Response from server:", response);
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
    .then((response) => {
      console.log("Response from server:", response);
      window.location.href = "/";
    })
    .catch((error) => {
      console.error("Error sending delete request:", error);
    });
}
