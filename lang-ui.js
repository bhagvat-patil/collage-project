// Object to store translations for different languages
const translations = {
    en: {
        username: "Username",
        password: "Password",
        login: "Login",
        role: "Role",
        student: "Student",
        admin: "Admin"
    },
    hi: {
        username: "उपयोगकर्ता नाम",
        password: "पासवर्ड",
        login: "लॉगिन",
        role: "भूमिका",
        student: "छात्र",
        admin: "प्रशासक"
    },
    mr: {
        username: "वापरकर्तानाव",
        password: "पासवर्ड",
        login: "लॉगिन",
        role: "भूमिका",
        student: "विद्यार्थी",
        admin: "प्रशासक"
    }
};

// Function to set the language and update the UI
function setLanguage(language) {
    const elements = {
        username: document.getElementById("username"),
        password: document.getElementById("password"),
        login: document.querySelector("button"),
        role: document.getElementById("role")
    };

    const selectedTranslations = translations[language];

    if (selectedTranslations) {
        elements.username.placeholder = selectedTranslations.username;
        elements.password.placeholder = selectedTranslations.password;
        elements.login.textContent = selectedTranslations.login;

        // Update role dropdown options
        const roleOptions = elements.role.options;
        roleOptions[0].textContent = selectedTranslations.student;
        roleOptions[1].textContent = selectedTranslations.admin;
    }
}