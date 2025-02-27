let eventSource = null;

async function sendMessage() {
    const input = document.getElementById('userInput');
    const chatMessages = document.getElementById('chatMessages');
    const query = input.value.trim();
    
    if (!query) return;

    // Clear previous connection if exists
    if (eventSource) {
        eventSource.close();
    }

    // Add user message
    const userDiv = document.createElement('div');
    userDiv.className = 'message user-message';
    userDiv.textContent = query;
    chatMessages.appendChild(userDiv);
    
    // Add typing indicator
    const typingDiv = document.createElement('div');
    typingDiv.className = 'typing-indicator';
    typingDiv.innerHTML = `
        <div class="dot"></div>
        <div class="dot"></div>
        <div class="dot"></div>
    `;
    chatMessages.appendChild(typingDiv);
    
    input.value = '';
    chatMessages.scrollTop = chatMessages.scrollHeight;

    // Create new EventSource connection
    eventSource = new EventSource(`/chat?query=${encodeURIComponent(query)}`);

    // Create bot message container
    const botDiv = document.createElement('div');
    botDiv.className = 'message bot-message';
    chatMessages.appendChild(botDiv);

    let buffer = '';
    let images = [];

    eventSource.onmessage = (event) => {
        try {
            const data = JSON.parse(event.data);
            
            if (data.error) {
                botDiv.innerHTML = `<div class="error-message">${data.error}</div>`;
                eventSource.close();
                return;
            }

            if (data.images) {
                images = data.images;
                return;
            }

            if (data.token) {
                buffer += data.token;
                botDiv.innerHTML = formatResponse(buffer);
                chatMessages.scrollTop = chatMessages.scrollHeight;
            }
        } catch (error) {
            console.error('Parsing error:', error);
            botDiv.innerHTML = `<div class="error-message">Error processing response</div>`;
            eventSource.close();
        }
    };

    eventSource.onerror = (error) => {
        console.error('EventSource error:', error);
        chatMessages.removeChild(typingDiv);
        if (buffer === '') {
            botDiv.innerHTML = `<div class="error-message">Connection failed. Please try again.</div>`;
        }
        eventSource.close();
    };

    eventSource.addEventListener('done', () => {
        chatMessages.removeChild(typingDiv);
        if (images.length > 0) {
            const imageGrid = document.createElement('div');
            imageGrid.className = 'image-grid';
            images.forEach(img => {
                const imgElem = document.createElement('img');
                imgElem.src = img;
                imgElem.className = 'response-image';
                imageGrid.appendChild(imgElem);
            });
            botDiv.appendChild(imageGrid);
            chatMessages.scrollTop = chatMessages.scrollHeight;
        }
        eventSource.close();
    });
}

function formatResponse(text) {
    return text
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/\*(.*?)\*/g, '<em>$1</em>')
        .replace(/`(.*?)`/g, '<code>$1</code>')
        .replace(/\n/g, '<br>');
}

// Event listener for input
document.getElementById('userInput').addEventListener('keypress', (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
        e.preventDefault();
        sendMessage();
    }
});
