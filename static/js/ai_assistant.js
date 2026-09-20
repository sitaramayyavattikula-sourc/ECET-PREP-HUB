// E-CET AI Assistant Client-side Script
document.addEventListener("DOMContentLoaded", function () {
    const aiToggle = document.getElementById("aiToggle");
    const aiDrawer = document.getElementById("aiDrawer");
    const aiClose = document.getElementById("aiClose");
    const aiForm = document.getElementById("aiForm");
    const aiInput = document.getElementById("aiInput");
    const aiMessages = document.getElementById("aiMessages");
    const promptChips = document.querySelectorAll(".prompt-chip");

    if (aiToggle && aiDrawer) {
        aiToggle.addEventListener("click", function () {
            aiDrawer.classList.add("active");
        });

        if (aiClose) {
            aiClose.addEventListener("click", function () {
                aiDrawer.classList.remove("active");
            });
        }
    }

    if (promptChips) {
        promptChips.forEach(chip => {
            chip.addEventListener("click", function () {
                if (aiInput) {
                    aiInput.value = this.innerText;
                    aiForm.dispatchEvent(new Event("submit"));
                }
            });
        });
    }

    if (aiForm) {
        aiForm.addEventListener("submit", async function (e) {
            e.preventDefault();
            const message = aiInput.value.trim();
            if (!message) return;

            // Render User Message
            appendMessage("user", message);
            aiInput.value = "";

            // Render Loading Message
            const loadingId = appendLoadingMessage();

            try {
                const response = await fetch("/api/ai_chat", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ message: message })
                });

                const data = await response.json();
                removeMessage(loadingId);

                if (data.reply) {
                    appendMessage("assistant", data.reply);
                } else if (data.error) {
                    appendMessage("assistant", "⚠️ " + data.error);
                } else {
                    appendMessage("assistant", "⚠️ Unexpected response from server.");
                }
            } catch (err) {
                removeMessage(loadingId);
                appendMessage("assistant", "⚠️ Unable to connect to AI server: " + err.message);
            }
        });
    }

    function appendMessage(sender, text) {
        const msgDiv = document.createElement("div");
        msgDiv.className = `chat-bubble ${sender}-bubble`;
        
        const textPara = document.createElement("div");
        textPara.className = "bubble-text";
        textPara.innerText = text;
        
        msgDiv.appendChild(textPara);
        aiMessages.appendChild(msgDiv);
        aiMessages.scrollTop = aiMessages.scrollHeight;
    }

    function appendLoadingMessage() {
        const id = "loading-" + Date.now();
        const msgDiv = document.createElement("div");
        msgDiv.className = "chat-bubble assistant-bubble loading-bubble";
        msgDiv.id = id;
        msgDiv.innerHTML = `<div class="typing-dots"><span></span><span></span><span></span></div>`;
        aiMessages.appendChild(msgDiv);
        aiMessages.scrollTop = aiMessages.scrollHeight;
        return id;
    }

    function removeMessage(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }
});
