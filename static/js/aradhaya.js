/**
 * anya.js
 * Handles chat logic, UI updates, and API integration for Anya.AI
 */

document.addEventListener('DOMContentLoaded', () => {
    // Elements
    const chatForm = document.getElementById('chat-form');
    const chatInput = document.getElementById('chat-input');
    const chatMessages = document.getElementById('chat-messages');
    const sendBtn = document.getElementById('send-btn');
    const typingIndicator = document.getElementById('typing-indicator');
    const quickPrompts = document.querySelectorAll('.quick-prompt');
    const exportPdfBtn = document.getElementById('export-pdf-btn');

    // Chat History State (for context window)
    let chatHistory = JSON.parse(sessionStorage.getItem('aradhaya_chatHistory')) || [];

    // Re-render existing history
    if (chatHistory.length > 0) {
        chatHistory.forEach(msg => {
            if (msg.role === 'user') {
                appendUserMessage(msg.content);
            } else {
                appendAIMessage(msg.content);
            }
        });
    }

    // Initialize Marked.js with highlight.js
    marked.setOptions({
        highlight: function(code, lang) {
            const language = hljs.getLanguage(lang) ? lang : 'plaintext';
            return hljs.highlight(code, { language }).value;
        },
        breaks: true, // Convert \n to <br>
        gfm: true     // GitHub Flavored Markdown
    });

    // Auto-resize textarea
    chatInput.addEventListener('input', function() {
        this.style.height = '60px'; // Reset to min-height
        const newHeight = Math.min(this.scrollHeight, 128); // Max height 128px (8rem)
        this.style.height = newHeight + 'px';
        
        // Enable/disable send button
        if (this.value.trim().length > 0) {
            sendBtn.removeAttribute('disabled');
        } else {
            sendBtn.setAttribute('disabled', 'true');
        }
    });

    // Handle Enter key to send (Shift+Enter for newline)
    chatInput.addEventListener('keydown', function(e) {
        if (e.key === 'Enter' && !e.shiftKey) {
            e.preventDefault();
            if (this.value.trim().length > 0) {
                chatForm.dispatchEvent(new Event('submit'));
            }
        }
    });

    // Handle Quick Prompts
    quickPrompts.forEach(btn => {
        btn.addEventListener('click', () => {
            chatInput.value = btn.textContent.trim();
            // Trigger input event to update button state and height
            chatInput.dispatchEvent(new Event('input'));
            // Optional: Auto-send for quick prompts
            chatForm.dispatchEvent(new Event('submit'));
        });
    });

    // Submit form
    chatForm.addEventListener('submit', async (e) => {
        e.preventDefault();
        
        const message = chatInput.value.trim();
        if (!message) return;

        // Reset input immediately
        chatInput.value = '';
        chatInput.style.height = '60px';
        sendBtn.setAttribute('disabled', 'true');

        // Add user message to UI
        appendUserMessage(message);

        // Show typing indicator and scroll
        typingIndicator.classList.remove('hidden');
        scrollToBottom();

        // Send to API
        try {
            const csrfToken = document.querySelector('meta[name="csrf-token"]').getAttribute('content');
            
            const response = await fetch('/aradhaya/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({
                    message: message,
                    history: chatHistory
                })
            });

            const data = await response.json();

            // Hide typing indicator
            typingIndicator.classList.add('hidden');

            if (response.ok) {
                // Add AI response to UI
                appendAIMessage(data.reply);
                
                // Update history
                chatHistory.push({ role: 'user', content: message });
                chatHistory.push({ role: 'assistant', content: data.reply });
                
                // Save complete session history to sessionStorage
                sessionStorage.setItem('aradhaya_chatHistory', JSON.stringify(chatHistory));
            } else {
                appendErrorMessage(data.error || "Something went wrong.");
            }

        } catch (error) {
            console.error("Chat error:", error);
            typingIndicator.classList.add('hidden');
            appendErrorMessage("Network error. Please try connecting again.");
        }
    });

    // Handle PDF Export
    exportPdfBtn.addEventListener('click', () => {
        // Prevent export if chat is empty (only has the initial greeting)
        if (chatMessages.children.length <= 1) {
            alert("Chat is empty. Please start a conversation first.");
            return;
        }
        
        const originalText = exportPdfBtn.innerHTML;
        exportPdfBtn.innerHTML = '<span class="material-symbols-rounded text-[20px] animate-spin">refresh</span> Exporting...';
        exportPdfBtn.disabled = true;

        const logoUrl = exportPdfBtn.getAttribute('data-logo');
        
        // Create an invisible container for the PDF content
        const pdfContainer = document.createElement('div');
        pdfContainer.style.padding = '20px';
        pdfContainer.style.fontFamily = "'Poppins', sans-serif";
        pdfContainer.style.color = "#1e293b";
        
        // Header HTML with the absolute logo
        const headerHtml = `
            <div style="text-align: center; margin-bottom: 30px; border-bottom: 2px solid #e2e8f0; padding-bottom: 20px;">
                <img src="${logoUrl}" alt="CampusDrive" style="display: block; margin: 0 auto 15px auto; height: 60px; object-fit: contain;" crossorigin="anonymous"/>
                <h1 style="color: #001BB7; margin: 0; font-size: 24px; font-weight: 700; font-family: 'Poppins', sans-serif;">Aradhaya.ai Academic Transcript</h1>
                <p style="color: #64748b; font-size: 14px; margin-top: 8px;">Exported on: ${new Date().toLocaleString()}</p>
            </div>
            <div style="margin-bottom: 20px;"></div>
        `;
        
        // Clone the chat messages, strip out scrollbars/heights
        const messagesClone = chatMessages.cloneNode(true);
        messagesClone.style.height = 'auto';
        messagesClone.style.overflow = 'visible';
        messagesClone.style.padding = '0';
        messagesClone.style.margin = '0';
        
        pdfContainer.innerHTML = headerHtml;
        pdfContainer.appendChild(messagesClone);

        // Options for html2pdf
        const opt = {
            margin:       15,
            filename:     `CampusDrive_Aradhaya_${new Date().toISOString().slice(0,10)}.pdf`,
            image:        { type: 'jpeg', quality: 0.98 },
            html2canvas:  { scale: 2, useCORS: true, letterRendering: true },
            jsPDF:        { unit: 'mm', format: 'a4', orientation: 'portrait' }
        };

        // Generate the PDF
        html2pdf().set(opt).from(pdfContainer).save().then(() => {
            // Restore button state
            exportPdfBtn.innerHTML = originalText;
            exportPdfBtn.disabled = false;
        }).catch(err => {
            console.error("PDF Export Error: ", err);
            exportPdfBtn.innerHTML = originalText;
            exportPdfBtn.disabled = false;
            alert("Oops! Failed to export PDF.");
        });
    });

    // UI Helpers
    function appendUserMessage(text) {
        const msgHtml = `
            <div class="message user flex gap-4 max-w-[85%] self-end ml-auto flex-row-reverse">
                <div class="message-bubble bg-brand-blue rounded-2xl rounded-tr-sm p-4 text-white text-base font-poppins leading-relaxed shadow-md">
                    <p class="m-0 text-white font-poppins">${escapeHtml(text)}</p>
                </div>
            </div>
        `;
        chatMessages.insertAdjacentHTML('beforeend', msgHtml);
        scrollToBottom();
    }

    function appendAIMessage(markdownText) {
        const parsedHtml = marked.parse(markdownText);
        
        const msgHtml = `
            <div class="message aradhaya flex gap-4 max-w-[85%]">
                <div class="w-10 h-10 rounded-xl bg-gradient-to-br from-brand-orange to-red-500 flex shrink-0 items-center justify-center text-white shadow-sm mt-1">
                    <span class="material-symbols-rounded text-lg">magic_button</span>
                </div>
                <div class="message-bubble bg-brand-blue/5 border border-brand-blue/10 rounded-2xl rounded-tl-sm p-5 text-slate-800 text-base font-poppins leading-relaxed prose prose-base prose-slate shadow-sm">
                    ${parsedHtml}
                </div>
            </div>
        `;
        chatMessages.insertAdjacentHTML('beforeend', msgHtml);
        scrollToBottom();
    }

    function appendErrorMessage(errorText) {
        const msgHtml = `
            <div class="message error flex gap-4 max-w-[85%] mx-auto justify-center w-full">
                <div class="bg-red-50 text-red-600 border border-red-100 rounded-xl px-4 py-2 text-xs font-medium flex items-center gap-2">
                    <span class="material-symbols-rounded text-base">error</span>
                    ${escapeHtml(errorText)}
                </div>
            </div>
        `;
        chatMessages.insertAdjacentHTML('beforeend', msgHtml);
        scrollToBottom();
    }

    function scrollToBottom() {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }

    function escapeHtml(unsafe) {
        return unsafe
            .replace(/&/g, "&amp;")
            .replace(/</g, "&lt;")
            .replace(/>/g, "&gt;")
            .replace(/"/g, "&quot;")
            .replace(/'/g, "&#039;");
    }
});
