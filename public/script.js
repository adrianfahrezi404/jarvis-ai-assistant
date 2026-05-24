document.addEventListener('DOMContentLoaded', () => {
    const chatContainer = document.getElementById('chatContainer');
    const textInput = document.getElementById('textInput');
    const sendBtn = document.getElementById('sendBtn');
    const micBtn = document.getElementById('micBtn');
    const arcReactor = document.getElementById('arcReactor');
    const statusDot = document.getElementById('statusDot');
    const statusText = document.getElementById('statusText');

    let isListening = false;
    let isProcessing = false;

    // Initialize state
    setReactorState('idle');

    // Speech Recognition Setup
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
    let recognition = null;
    
    if (SpeechRecognition) {
        recognition = new SpeechRecognition();
        recognition.continuous = false;
        recognition.interimResults = false;
        recognition.lang = 'id-ID';

        recognition.onstart = () => {
            isListening = true;
            micBtn.classList.add('listening');
            setReactorState('listening');
            setStatus('LISTENING...', 'online');
        };

        recognition.onresult = (event) => {
            const transcript = event.results[0][0].transcript;
            textInput.value = transcript;
            sendMessage();
        };

        recognition.onerror = (event) => {
            console.error('Speech recognition error', event.error);
            stopListening();
            appendSystemMessage('Speech Recognition Error: ' + event.error);
        };

        recognition.onend = () => {
            stopListening();
            if (!isProcessing) setReactorState('idle');
        };
    } else {
        micBtn.style.display = 'none';
        appendSystemMessage('Browser tidak mendukung Web Speech API. Gunakan text input.');
    }

    // TTS Setup
    const synth = window.speechSynthesis;

    function speakText(text) {
        if (!synth) return;
        
        // Remove markdown or symbols for speech
        const cleanText = text.replace(/[*#]/g, '');
        
        const utterance = new SpeechSynthesisUtterance(cleanText);
        utterance.lang = 'id-ID';
        utterance.rate = 1.0;
        utterance.pitch = 1.0;

        utterance.onstart = () => {
            setReactorState('speaking');
            setStatus('SPEAKING', 'speaking');
        };

        utterance.onend = () => {
            setReactorState('idle');
            setStatus('SYSTEM ONLINE', 'online');
        };

        synth.speak(utterance);
    }

    // Interactions
    micBtn.addEventListener('click', () => {
        if (isProcessing) return;
        if (isListening) {
            recognition.stop();
        } else {
            try {
                recognition.start();
            } catch(e) {
                console.error(e);
            }
        }
    });

    sendBtn.addEventListener('click', sendMessage);
    textInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });

    async function sendMessage() {
        const text = textInput.value.trim();
        if (!text || isProcessing) return;

        // UI Updates
        textInput.value = '';
        appendMessage('user', 'YOU', text);
        isProcessing = true;
        setReactorState('thinking');
        setStatus('PROCESSING', 'thinking');

        try {
            // Call Vercel API
            const response = await fetch('/api/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: text })
            });

            const data = await response.json();

            if (response.ok) {
                appendMessage('bot', 'J.A.R.V.I.S', data.reply);
                speakText(data.reply);
            } else {
                appendSystemMessage('Error: ' + data.error);
                setReactorState('idle');
                setStatus('SYSTEM ONLINE', 'online');
            }
        } catch (error) {
            appendSystemMessage('Connection Error: ' + error.message);
            setReactorState('idle');
            setStatus('ERROR', 'error');
        } finally {
            isProcessing = false;
        }
    }

    function stopListening() {
        isListening = false;
        micBtn.classList.remove('listening');
        if (!isProcessing) setStatus('SYSTEM ONLINE', 'online');
    }

    function setReactorState(state) {
        // states: idle, listening, thinking, speaking
        arcReactor.className = 'arc-reactor ' + state;
    }

    function setStatus(text, dotClass) {
        statusText.innerText = text;
        statusDot.className = 'dot ' + dotClass;
    }

    function appendMessage(type, label, text) {
        // Simple markdown bold replacement for display
        const htmlText = text.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
        
        const msgDiv = document.createElement('div');
        msgDiv.className = `message ${type}`;
        msgDiv.innerHTML = `
            <span class="msg-label">${label}</span>
            <div class="msg-content">${htmlText}</div>
        `;
        chatContainer.appendChild(msgDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    function appendSystemMessage(text) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `message system`;
        msgDiv.innerHTML = `
            <div class="msg-content">
                <span class="system-title">SYSTEM ALERT</span>
                <p>${text}</p>
            </div>
        `;
        chatContainer.appendChild(msgDiv);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
});
