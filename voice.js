// Initialize Speech Recognition and Speech Synthesis
const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
const recognition = new SpeechRecognition();
const synth = window.speechSynthesis;

// Configure recognition settings
recognition.lang = "en-US"; // Default language
recognition.interimResults = false;
recognition.continuous = false;

// Function to start voice recognition
function startVoiceRecognition() {
    recognition.start();
    console.log("Voice recognition started...");
}

// Handle recognition results
recognition.onresult = (event) => {
    const transcript = event.results[0][0].transcript;
    console.log("Recognized speech:", transcript);
    handleVoiceCommand(transcript);
};

// Handle recognition errors
recognition.onerror = (event) => {
    console.error("Voice recognition error:", event.error);
};

// Function to handle voice commands
function handleVoiceCommand(command) {
    command = command.toLowerCase();

    if (command.includes("login")) {
        document.querySelector("button").click();
    } else if (command.includes("refresh")) {
        location.reload();
    } else {
        speakText("Sorry, I didn't understand that command.");
    }
}

// Function to speak text
function speakText(text) {
    if (synth.speaking) {
        console.error("Speech synthesis is already in progress.");
        return;
    }

    const utterance = new SpeechSynthesisUtterance(text);
    utterance.lang = "en-US"; // Default language
    synth.speak(utterance);
}

// Initialize voice module
function initVoiceModule() {
    const voiceButton = document.getElementById("voice-button");
    if (voiceButton) {
        voiceButton.addEventListener("click", startVoiceRecognition);
    }
}

// Initialize the voice module when the DOM is fully loaded
document.addEventListener("DOMContentLoaded", initVoiceModule);