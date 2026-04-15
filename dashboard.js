// ==========================
// ADMIN BADGE
// ==========================
const adminBadge = document.getElementById("adminBadge");

if (localStorage.getItem("role") === "admin") {
    adminBadge.style.display = "inline-block";
}

// ==========================
// FIXED HOME BUTTON
// ==========================
function goHome() {
    if (window.location.pathname.includes("dashboard.html")) {
        location.reload(); // refresh if already on dashboard
    } else {
        window.location.href = "dashboard.html";
    }
}

// ==========================
// VOICE SYSTEM (JARVIS)
// ==========================
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const recognition = new SpeechRecognition();

recognition.lang = "en-US";
recognition.continuous = false;

const output = document.getElementById("output");

// START LISTEN
function listen() {
    output.innerText = "Listening...";
    recognition.start();
}

// GET RESULT
recognition.onresult = function(event) {
    const text = event.results[0][0].transcript.toLowerCase();
    output.innerText = "You said: " + text;
    processCommand(text);
};

// SPEAK
function speak(msg) {
    const speech = new SpeechSynthesisUtterance(msg);
    speech.lang = "en-US";
    window.speechSynthesis.speak(speech);
}

// COMMAND LOGIC
function processCommand(text) {

    if (text.includes("home") || text.includes("dashboard")) {
        speak("Opening home");
        goHome();
    }

    else if (text.includes("diploma")) {
        speak("Opening diploma page");
        window.location.href = "diploma.html";
    }

    else if (text.includes("diploma info")) {
        showDiplomas();
    }

    else if (text.includes("time")) {
        speak("Current time is " + new Date().toLocaleTimeString());
    }

    else if (text.includes("date")) {
        speak("Today is " + new Date().toDateString());
    }

    else if (text.includes("logout")) {
        speak("Logging out");
        localStorage.clear();
        window.location.href = "index.html";
    }

    else {
        speak("Sorry, I did not understand");
    }
}

// ==========================
// SHOW DIPLOMA DATA
// ==========================
function showDiplomas() {
    let diplomas = JSON.parse(localStorage.getItem("diplomas")) || [];

    if (diplomas.length === 0) {
        output.innerHTML = "No diploma data available";
        speak("No diploma data found");
        return;
    }

    let html = "<h3>Available Diplomas:</h3>";

    diplomas.forEach(d => {
        html += `
            <p>
            <b>${d.title}</b><br>
            Seats: ${d.availableSeats}/${d.totalSeats}<br>
            Duration: ${d.duration}
            </p><hr>
        `;
    });

    output.innerHTML = html;
    speak("Here are available diploma courses");
}