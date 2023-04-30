const messageInput = document.getElementById('message-input');
const sendButton = document.getElementById('send-button');
const chatBox = document.getElementById('chat-box');

sendButton.addEventListener('click', () => {
    const message = messageInput.value;
    if (message) {
        addMessage(message, true);
        sendMessage(message);
        messageInput.value = '';
    }
});

function addMessage(message, isRight) {
    const messageDiv = document.createElement('div');
    messageDiv.classList.add('chat-message');
    if (isRight) {
        messageDiv.classList.add('chat-message-right');
    }
    const messageP = document.createElement('p');
    messageP.textContent = message;

    messageDiv.appendChild(messageP);
    chatBox.appendChild(messageDiv);
    chatBox.scrollTop = chatBox.scrollHeight;
}

async function sendMessage(message) {
    const response = await fetch('/chatgptdemo', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            s: message
        })
    });
    const data = await response.json();
    // debugger
    addMessage(data, false);
}

