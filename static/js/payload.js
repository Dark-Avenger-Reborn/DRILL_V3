const osDropdown = document.getElementById("os-dropdown");
const archDropdown = document.getElementById("arch-dropdown");

// Define architecture options for each OS
const archOptions = {
  Windows: ["x64"], // x86 is cuming soon
  Linux: ["x64"], // i386 is soon too
  OSX: ["arm64"], // chill so is x86 and x86_64
};

function parseAndFormatTime(dateString) {
  // Parse the dateString in the given format "%Y-%m-%d-%H-%M-%S"
  const dateParts = dateString.split("-");

  // Extract individual components
  const year = dateParts[0];
  const month = parseInt(dateParts[1], 10) - 1; // JavaScript months are 0-based
  const day = dateParts[2];
  const hour = dateParts[3];
  const minute = dateParts[4];
  const second = dateParts[5];

  // Create a new Date object as UTC
  const date = new Date(Date.UTC(year, month, day, hour, minute, second));

  // Convert the UTC date to local time
  const formattedTime = date.toLocaleString(); // Automatically converts to local time

  return formattedTime;
}

// Function to update architecture dropdown
function updateArchDropdown() {
  const selectedOS = osDropdown.value;
  const architectures = archOptions[selectedOS];

  // Clear existing options
  archDropdown.innerHTML = "";

  // Add new options
  architectures.forEach((arch) => {
    const option = document.createElement("option");
    option.value = arch;
    option.textContent = arch;
    archDropdown.appendChild(option);
  });
}

function deepEqual(obj1, obj2) {
  return JSON.stringify(obj1) === JSON.stringify(obj2);
}

// Initial update of architecture dropdown
updateArchDropdown();

// Add event listener to OS dropdown
osDropdown.addEventListener("change", updateArchDropdown);

old_data = [];
function createDownload() {
  fetch("/list_payloads", {
    method: "POST",
  })
    .then((response) => {
      if (!response.ok) {
        throw new Error("Network response was not ok");
      }
      return response.text(); // This returns a promise
    })
    .then((text) => {
      text = text.replace(/'/g, '"');
      directory = JSON.parse(text);

      if (!deepEqual(directory, old_data)) {
        old_data = directory;

        const tableBody = document.getElementById("download-table");
        tableBody.innerHTML = "";

        for (file in directory) {
          file_split = directory[file].split("_");
          console.log(file_split);

          // Simulate download creation
          const row = document.createElement("tr");
          row.innerHTML = `
                <td>${file_split[1]}</td>
                <td>${file_split[2]}</td>
                <td>${parseAndFormatTime(file_split[3])}</td>
                <td><button onclick="download('${
                  directory[file]
                }')">Download</button></td>
            `;
          tableBody.appendChild(row);
        }
      }
    })
    .catch((error) => {
      console.error("There was a problem with the fetch operation:", error);
    });
}

createDownload();

setInterval(createDownload, 1000);

function downloadFile() {
  const os = document.getElementById("os-dropdown").value;
  const arch = document.getElementById("arch-dropdown").value;

  alert("Download started this may take a minute");

  fetch("/download", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      os: os,
      arch: arch,
      ip: window.location.origin + "/",
    }),
  })
    .then((response) => {
      console.log("Response from server:", response);
      createDownload();
    })
    .catch((error) => {
      console.error("Error sending delete request:", error);
    });
}

function download(file) {
  window.location.href = "/get_payloads/" + file;
}
