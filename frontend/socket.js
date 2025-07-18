// frontend/socket.js
window.addEventListener('load', () => {
    const socket = io();

    const chatBox = document.getElementById("chat-box");
    const form = document.getElementById("email-form");
    const subjectInput = document.getElementById("subject");
    const bodyInput = document.getElementById("body");

    function addMessage(text) {
        const div = document.createElement("div");
        div.className = "chat-message";
        div.innerText = text;
        chatBox.appendChild(div);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    function addImage(src) {
        const img = document.createElement("img");
        img.src = src;
        img.className = "chat-image";
        chatBox.appendChild(img);
        chatBox.scrollTop = chatBox.scrollHeight;
    }

    // Handle messages from backend
    socket.on("text", (data) => {
        addMessage(data);
    });

    socket.on("image", (imgDataUrl) => {
        addImage(imgDataUrl);
    });

    socket.on("generated_email", (data) => {
        subjectInput.value = data.subject;
        bodyInput.value = data.body;
        addMessage("✍️ Email draft generated and autofilled.");
    });

    // Send email form to backend
    form.addEventListener("submit", (e) => {
        e.preventDefault();
        const to = document.getElementById("to").value;
        const subject = subjectInput.value;
        const body = bodyInput.value;

        socket.emit("send_email", { to, subject, body });

        addMessage(`🧠 Sending email to ${to}...`);
    });

    window.requestEmailDraft = function() {
        const intent = document.getElementById("intent").value;
        socket.emit("generate_email", { intent });
    };
});
