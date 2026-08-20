// Altostrat HR Portal Frontend Javascript interaction handler
document.addEventListener("DOMContentLoaded", () => {
    const chatPane = document.getElementById("chatPane");
    const chatForm = document.getElementById("chatForm");
    const userInput = document.getElementById("userInput");

    // Marked options configuration
    marked.setOptions({
        gfm: true,
        breaks: true,
        sanitize: false
    });

    const appendMessage = (sender, text, role, status = "SUCCESS") => {
        const bubble = document.createElement("div");
        bubble.className = `flex items-start space-x-3 max-w-3xl ${role === 'user' ? 'ml-auto justify-end' : ''}`;
        
        let headerColor = role === 'user' ? 'text-blue-200' : 'text-blue-700';
        let bodyBg = role === 'user' ? 'bg-blue-600 text-white border-transparent' : 'bg-white border-slate-200';
        let senderName = role === 'user' ? 'You' : 'Altostrat Assistant';
        
        if (status === "BLOCKED") {
            bodyBg = "bg-amber-50 text-amber-900 border-amber-200 border";
            headerColor = "text-amber-700 font-semibold";
            senderName = "Safety Shield / Assistant";
        } else if (status === "ERROR") {
            bodyBg = "bg-rose-50 text-rose-950 border-rose-200 border";
            headerColor = "text-rose-700 font-semibold";
            senderName = "System Error";
        }

        const avatar = role === 'user' 
            ? `<div class="bg-blue-800 text-blue-200 rounded-full h-8 w-8 flex items-center justify-center font-bold text-sm shrink-0 order-2 ml-3">ME</div>`
            : `<div class="bg-blue-100 text-blue-600 rounded-full h-8 w-8 flex items-center justify-center font-bold text-sm shrink-0">AI</div>`;

        // Render Markdown content safely
        const renderedHtml = marked.parse(text);

        bubble.innerHTML = `
            ${role !== 'user' ? avatar : ''}
            <div class="${bodyBg} border rounded-2xl p-4 shadow-sm text-sm ${role === 'user' ? 'rounded-tr-none' : 'rounded-tl-none'}">
                <p class="font-medium ${headerColor} mb-1">${senderName}</p>
                <div class="prose prose-sm max-w-none leading-relaxed">${renderedHtml}</div>
            </div>
            ${role === 'user' ? avatar : ''}
        `;

        chatPane.appendChild(bubble);
        chatPane.scrollTop = chatPane.scrollHeight;
    };

    chatForm.addEventListener("submit", async (e) => {
        e.preventDefault();
        const msg = userInput.value.trim();
        if (!msg) return;

        // Clear input field
        userInput.value = "";

        // Append user query bubble
        appendMessage("user", msg, "user");

        // Prepare context parameters
        const selectedUser = "EMP-386";

        // Append loader bubble
        const loader = document.createElement("div");
        loader.id = "chatLoader";
        loader.className = "flex items-start space-x-3 max-w-3xl";
        loader.innerHTML = `
            <div class="bg-blue-100 text-blue-600 rounded-full h-8 w-8 flex items-center justify-center font-bold text-sm shrink-0">AI</div>
            <div class="bg-white border border-slate-200 rounded-2xl rounded-tl-none p-4 shadow-sm text-sm">
                <p class="font-medium text-blue-500 mb-1">Altostrat Assistant</p>
                <p class="italic text-slate-400">Processing query...</p>
            </div>
        `;
        chatPane.appendChild(loader);
        chatPane.scrollTop = chatPane.scrollHeight;

        try {
            const res = await fetch("/api/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    message: msg,
                    user_id: selectedUser,
                    session_id: `web-session-${selectedUser}`
                })
            });

            // Remove loader
            const loaderElem = document.getElementById("chatLoader");
            if (loaderElem) loaderElem.remove();

            if (!res.ok) {
                const data = await res.json();
                appendMessage("assistant", data.detail || "Server communication failed.", "assistant", "ERROR");
                return;
            }

            const data = await res.json();
            appendMessage("assistant", data.response, "assistant", data.status);

        } catch (err) {
            console.error(err);
            const loaderElem = document.getElementById("chatLoader");
            if (loaderElem) loaderElem.remove();
            appendMessage("assistant", "Unable to reach the server. Please check that app.py is running.", "assistant", "ERROR");
        }
    });
});
