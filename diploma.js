// Function to fetch diploma data from a server or local source
async function fetchDiplomaData() {
    try {
        const response = await fetch("/api/diploma-data"); // Replace with actual API endpoint
        if (!response.ok) {
            throw new Error("Failed to fetch diploma data");
        }
        const data = await response.json();
        displayDiplomaData(data);
    } catch (error) {
        console.error("Error fetching diploma data:", error);
    }
}

// Function to display diploma data in the UI
function displayDiplomaData(data) {
    const diplomaContainer = document.getElementById("diploma-container");
    diplomaContainer.innerHTML = ""; // Clear existing content

    data.forEach((diploma) => {
        const diplomaElement = document.createElement("div");
        diplomaElement.classList.add("diploma-item");
        diplomaElement.innerHTML = `
            <h3>${diploma.title}</h3>
            <p>${diploma.description}</p>
            <span>Issued on: ${diploma.issueDate}</span>
        `;
        diplomaContainer.appendChild(diplomaElement);
    });
}

// Function to initialize diploma-related operations
function initDiplomaModule() {
    const refreshButton = document.getElementById("refresh-diploma");
    if (refreshButton) {
        refreshButton.addEventListener("click", fetchDiplomaData);
    }

    // Fetch data on page load
    fetchDiplomaData();
}

// Initialize the diploma module when the DOM is fully loaded
document.addEventListener("DOMContentLoaded", initDiplomaModule);