const violationGrid = document.getElementById(
    "violationGrid"
);

const totalViolations = document.getElementById(
    "totalViolations"
);

const todayViolations = document.getElementById(
    "todayViolations"
);

const searchInput = document.getElementById(
    "searchInput"
);

let violationsData = [];

// ==========================================
// LOAD VIOLATIONS JSON
// ==========================================
async function loadViolations() {

    // FIX #6 — Show loading state before fetch
    violationGrid.innerHTML = `
        <p style="color:#94a3b8; padding:20px; font-size:16px;">
            ⏳ Loading violations...
        </p>
    `;

    try {

        const response = await fetch(
            "./violations/violations.json"
        );

        const data = await response.json();

        violationsData = data;

        displayViolations(data);

        updateStats(data);

    } catch (error) {

        console.error(
            "Error loading violations:",
            error
        );

        // FIX #5 — Show error state if fetch fails
        violationGrid.innerHTML = `
            <p style="color:#f87171; padding:20px; font-size:16px;">
                ❌ Failed to load violations. Make sure violations.json exists.
            </p>
        `;
    }
}

// ==========================================
// DISPLAY VIOLATION CARDS
// ==========================================
function displayViolations(data) {

    violationGrid.innerHTML = "";

    // FIX #5 — Show empty state when no results
    if (data.length === 0) {
        violationGrid.innerHTML = `
            <p style="color:#94a3b8; padding:20px; font-size:16px;">
                🔍 No violations found.
            </p>
        `;
        return;
    }

    // Latest first
    [...data].reverse().forEach((violation) => {

        const card = document.createElement("div");

        card.classList.add("vehicle-card");

        card.innerHTML = `

            <img
                src="${violation.vehicle_image}"
                alt="Vehicle Evidence"
            />

            <div class="card-content">

                <h3>
                    ${violation.plate_number}
                </h3>

                <div class="info-row">
                    <span class="label">Vehicle ID: </span>
                    ${violation.vehicle_id}
                </div>

                <div class="info-row">
                    <span class="label">Timestamp: </span>
                    ${violation.timestamp}
                </div>

                <!-- FIX #7 — Removed duplicate plain-text status info-row.
                     The styled badge below already shows the status. -->

                <div class="status">
                    ${violation.status}
                </div>

                <div class="button-group">

                    <!-- FIX #2 — Renamed buttons to clarify what each opens/downloads -->
                    <button
                        class="btn view-btn"
                        onclick="viewEvidence('${violation.frame_image}')"
                    >
                        View Frame
                    </button>

                    <button
                        class="btn download-btn"
                        onclick="downloadImage('${violation.vehicle_image}')"
                    >
                        Download Vehicle
                    </button>

                </div>

            </div>
        `;

        violationGrid.appendChild(card);
    });
}

// ==========================================
// UPDATE STATS
// ==========================================
function updateStats(data) {

    totalViolations.innerText = data.length;

    // FIX #1 — Calculate today's violations properly by matching date
    const today = new Date().toISOString().slice(0, 10); // "YYYY-MM-DD"

    const todayCount = data.filter(
        (v) => v.timestamp.startsWith(today)
    ).length;

    todayViolations.innerText = todayCount;
}

// ==========================================
// SEARCH FUNCTIONALITY
// ==========================================
searchInput.addEventListener("input", (e) => {

    const value = e.target.value.toLowerCase().trim();

    const filtered = violationsData.filter((item) => {

        // FIX #3 — Extended search: plate number, status, and timestamp
        return (
            item.plate_number.toLowerCase().includes(value) ||
            item.status.toLowerCase().includes(value) ||
            item.timestamp.includes(value)
        );
    });

    displayViolations(filtered);

    // FIX #4 — Update stats to reflect filtered results
    updateStats(filtered);
});

// ==========================================
// VIEW FULL EVIDENCE (Frame Image)
// ==========================================
function viewEvidence(imagePath) {

    window.open(imagePath, "_blank");
}

// ==========================================
// DOWNLOAD IMAGE (Vehicle Image)
// ==========================================
function downloadImage(imagePath) {

    const link = document.createElement("a");

    link.href = imagePath;

    link.download = "vehicle_evidence.jpg";

    document.body.appendChild(link);

    link.click();

    document.body.removeChild(link);
}

// ==========================================
// INITIAL LOAD
// ==========================================
loadViolations();
