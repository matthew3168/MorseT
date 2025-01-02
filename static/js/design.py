from flask import url_for

def get_js_content():
    """
    Returns the JavaScript content as a string that will be served by Flask
    """
    return """
document.addEventListener('DOMContentLoaded', function() {
 
    const EMERGENCY_KEYWORDS = ['SOS', 'MAYDAY', 'REQUESTING ASSISTANCE'];
    const WARNING_KEYWORDS = ['WARNING', 'CAUTION', 'ALERT'];

    function applyMessageHighlighting(messageElement, messageText) {
        console.log('Checking message:', messageText);
        
        const upperText = messageText.toUpperCase();
        
        if (EMERGENCY_KEYWORDS.some(keyword => upperText.includes(keyword))) {
            console.log('Emergency message detected');
            messageElement.classList.add('emergency');
        } else if (WARNING_KEYWORDS.some(keyword => upperText.includes(keyword))) {
            console.log('Warning message detected');
            messageElement.classList.add('warning');
        }
    }

    // Add CSS styles programmatically to ensure highlighting takes precedence
    const style = document.createElement('style');
    style.textContent = `
        .message-bubble.message-received.emergency {
            background-color: #ff4444 !important;
            color: white !important;
            border: 1px solid #cc0000 !important;
        }

        .message-bubble.message-received.warning {
            background-color: #ffbb33 !important;
            color: black !important;
            border: 1px solid #cc9900 !important;
        }
    `;
    document.head.appendChild(style);

    // Menu search functionality
    const searchInput = document.querySelector('.search input[type="text"]');
    const messageInput = document.getElementById('messageInput');
    const vesselBtns = document.querySelectorAll('.vessel-btn');

    let activeInput = searchInput;

    searchInput.addEventListener('focus', () => {
        activeInput = searchInput;
    });

    messageInput.addEventListener('focus', () => {
        activeInput = messageInput;
    });

    // Function to update messages
    function updateMessages(vessel) {
        console.log('Updating messages for vessel:', vessel);

        if (!vessel || vessel.toLowerCase() === 'all' || vessel.toLowerCase() === 'all channels') {
            console.log('No valid vessel selected');
            return;
        }
        
        const url = `/get_messages/${encodeURIComponent(vessel)}`;
        
        fetch(url)
            .then(response => response.json())
            .then(data => {
                const chatArea = document.querySelector('.chat-area');
                chatArea.innerHTML = '';
                
                const messages = Array.isArray(data) ? data : data.messages;
                console.log('Received messages:', messages);
                
                messages.reverse().forEach(message => {
                    const messageGroup = document.createElement('div');
                    messageGroup.className = 'message-group';
                    
                    if (message.message_received !== '[No Message Received]') {
                        const receivedDiv = document.createElement('div');
                        receivedDiv.className = 'message-bubble message-received';
                        receivedDiv.textContent = message.message_received;
                        applyMessageHighlighting(receivedDiv, message.message_received);
                        messageGroup.appendChild(receivedDiv);
                        console.log('Created received message:', message.message_received);
                    }
                    
                    if (message.message_sent && message.message_sent !== '[No Message Sent]') {
                        const sentDiv = document.createElement('div');
                        sentDiv.className = 'message-bubble message-sent';
                        if (message.message_received !== '[No Message Received]') {
                            sentDiv.textContent = `Response: ${message.message_sent}`;
                        } else {
                            sentDiv.textContent = message.message_sent;
                        }
                        applyMessageHighlighting(sentDiv, message.message_sent);
                        messageGroup.appendChild(sentDiv);
                        console.log('Created sent message:', message.message_sent);
                    }
                    
                    const timestampDiv = document.createElement('div');
                    timestampDiv.className = `timestamp ${message.message_sent && message.message_sent !== '[No Message Sent]' ? 'timestamp-sent' : 'timestamp-received'}`;
                    timestampDiv.textContent = message.formatted_time;
                    messageGroup.appendChild(timestampDiv);
                    
                    chatArea.appendChild(messageGroup);
                });
                
                chatArea.scrollTop = chatArea.scrollHeight;
            })
            .catch(error => {
                console.error('Error updating messages:', error);
            });
    }

    // Function to add single message to UI
    function addMessageToUI(message) {
        const chatArea = document.querySelector('.chat-area');
        const messageGroup = document.createElement('div');
        messageGroup.className = 'message-group';
        
        if (message.message_received !== '[No Message Received]') {
            const receivedDiv = document.createElement('div');
            receivedDiv.className = 'message-bubble message-received';
            receivedDiv.textContent = message.message_received;
            applyMessageHighlighting(receivedDiv, message.message_received);
            messageGroup.appendChild(receivedDiv);
        }
        
        if (message.message_sent && message.message_sent !== '[No Message Sent]') {
            const sentDiv = document.createElement('div');
            sentDiv.className = 'message-bubble message-sent';
            sentDiv.textContent = message.message_sent;
            applyMessageHighlighting(sentDiv, message.message_sent);
            messageGroup.appendChild(sentDiv);
        }
        
        const timestampDiv = document.createElement('div');
        timestampDiv.className = `timestamp ${message.message_sent ? 'timestamp-sent' : 'timestamp-received'}`;
        timestampDiv.textContent = message.formatted_time;
        messageGroup.appendChild(timestampDiv);
        
        chatArea.appendChild(messageGroup);
        chatArea.scrollTop = chatArea.scrollHeight;
    }

    // Event listeners for input toggling
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Tab') {
            event.preventDefault();
            if (activeInput === searchInput) {
                messageInput.focus();
                activeInput = messageInput;
            } else {
                searchInput.focus();
                activeInput = searchInput;
            }
        }
    });

    // Handle virtual keyboard
    document.querySelectorAll('.key').forEach(key => {
        key.addEventListener('click', function(event) {
            if (event.target.classList.contains('switch')) {
                event.preventDefault();
                return;
            }

            event.stopPropagation();

            const keyText = this.textContent;
            const activeInputField = activeInput;

            if (keyText === ' ' || keyText === '') {
                return;
            }

            if (this.classList.contains('delete')) {
                activeInputField.value = activeInputField.value.slice(0, -1);
            } else if (this.classList.contains('space')) {
                activeInputField.value += ' ';
            } else {
                activeInputField.value += keyText;
            }

            activeInputField.focus();

            if (activeInputField === searchInput) {
                const searchQuery = searchInput.value.toLowerCase();
                vesselBtns.forEach(btn => {
                    const vesselName = btn.textContent.toLowerCase();
                    btn.style.display = vesselName.includes(searchQuery) ? 'block' : 'none';
                });
            }

            event.preventDefault();
        });
    });

    // Special characters keyboard
    const specialCharMap = {
        '1': '&', 
        '2': "'", 
        '3': '@', 
        '4': '(', 
        '5': ')', 
        '6': ':', 
        '7': '=',
        '8': '!', 
        '9': '-', 
        '0': '×', 
        'Q': '%', 
        'W': '+', 
        'E': '"', 
        'R': '?',
        'T': '/', 
        'Y': ' ', 
        'U': ' ', 
        'I': ' ', 
        'O': ' ', 
        'P': ' ', 
        'A': ' ',
        'S': ' ', 
        'D': ' ', 
        'F': ' ', 
        'G': ' ', 
        'H': ' ', 
        'J': ' ', 
        'K': ' ',
        'L': ' ', 
        'Z': ' ', 
        'X': ' ', 
        'C': ' ', 
        'V': ' ', 
        'B': ' ', 
        'N': ' ',
        'M': ' ', 
        '.': ',', 
        ' ': ' '
    };

    let isSpecial = false;

    document.querySelector('.switch').addEventListener('click', function(event) {
        event.stopPropagation();
        event.preventDefault();
        toggleSpecial();
    });

    function toggleSpecial() {
        const keys = document.querySelectorAll('.key');
        const switchButton = document.querySelector('.switch');

        keys.forEach(key => {
            const originalKeyText = key.getAttribute('data-original');
            if (specialCharMap[originalKeyText]) {
                key.textContent = isSpecial ? originalKeyText : specialCharMap[originalKeyText];
            }
        });

        switchButton.textContent = isSpecial ? 'SPECIAL' : 'NORMAL';
        isSpecial = !isSpecial;
    }

    // Search functionality
    searchInput.addEventListener('input', function(event) {
        const searchQuery = searchInput.value.toLowerCase();
        vesselBtns.forEach(btn => {
            const vesselName = btn.textContent.toLowerCase();
            btn.style.display = vesselName.includes(searchQuery) ? 'block' : 'none';
        });
    });

    // Duration slider functionality
    const slider = document.getElementById('durationSlider');
    const speedDisplay = document.getElementById('speedDisplay');
    const settingDisplay = document.getElementById('settingDisplay');

    function updateSliderDisplay(value) {
        let speed = '';
        let speedColor = '';

        if (value == 50) {
            speed = 'Fast';
            speedColor = 'blue';
        } else if (value >= 100 && value <= 200) {
            speed = 'Normal';
            speedColor = 'green';
        } else if (value >= 200 && value <= 350) {
            speed = 'Slow';
            speedColor = 'orange';
        } else if (value >= 400 && value <= 500) {
            speed = 'Very Slow';
            speedColor = 'red';
        }

        speedDisplay.innerHTML = `<p>Speed:</p><span style="color: ${speedColor};">${speed}</span>`;
        settingDisplay.innerHTML = `<p>Current Setting:</p> <span style="color: ${speedColor};">${value}ms</span>`;
    }

    if (slider) {
        updateSliderDisplay(slider.value);
        slider.addEventListener('input', function() {
            updateSliderDisplay(this.value);
        });
    }

    // Quick message buttons highlighting
    document.querySelectorAll('.quick-msg-btn').forEach(btn => {
        const buttonText = btn.textContent.toUpperCase();
        if (EMERGENCY_KEYWORDS.some(keyword => buttonText === keyword)) {
            btn.classList.add('emergency');
        } else if (WARNING_KEYWORDS.some(keyword => buttonText === keyword)) {
            btn.classList.add('warning');
        }
    });

    // Vessel selection
    vesselBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            vesselBtns.forEach(b => b.classList.remove('selected'));
            this.classList.add('selected');
            
            const vesselName = this.getAttribute('data-vessel');
            currentChannelDisplay.textContent = vesselName;
            
            updateMessages(vesselName);
            
            if (window.innerWidth <= 768) {
                menuOpen = false;
                menuPanel.classList.remove('active');
                mainContent.classList.remove('shifted');
            }
        });
    });

    // Menu functionality
    const menuBtn = document.querySelector('.menu-btn');
    const menuPanel = document.getElementById('menuPanel');
    const mainContent = document.getElementById('mainContent');
    const rightPanel = document.getElementById('rightPanel');
    const rightPanelToggle = document.getElementById('rightPanelToggle');
    const currentChannelDisplay = document.getElementById('currentChannel');
    let menuOpen = false;
    let rightPanelOpen = false;

    if (rightPanelToggle) {
        rightPanelToggle.addEventListener('click', function(event) {
            event.stopPropagation();
            rightPanelOpen = !rightPanelOpen;
            
            if (rightPanel) {
                rightPanel.classList.toggle('active');
                mainContent.classList.toggle('shifted-right');
                rightPanelToggle.textContent = rightPanelOpen ? '→' : '←';
            }
        });
    }

    // Panel functionality
    const expandBtn = document.getElementById('expandBtn');
    const expandedPanel = document.getElementById('expandedPanel');
    const durationPanel = document.getElementById('durationPanel');
    const repeatPanel = document.getElementById('repeatPanel');
    const expandDRBtn = document.getElementById('expandDRBtn');
    const expandRBtn = document.getElementById('expandRBtn');
    let isPanelOpen = false;

    function closeAllPanels() {
        expandedPanel.style.display = 'none';
        durationPanel.style.display = 'none';
        repeatPanel.style.display = 'none';
        expandBtn.classList.remove('active');
        expandDRBtn.classList.remove('active');
        expandRBtn.classList.remove('active');
        isPanelOpen = false;
    }

    // Panel event listeners
    expandBtn.addEventListener('click', function(event) {
        event.stopPropagation();
        const isCurrentlyOpen = expandedPanel.style.display === 'block';
        closeAllPanels();
        isPanelOpen = !isCurrentlyOpen;
        expandedPanel.style.display = isPanelOpen ? 'block' : 'none';
        this.classList.toggle('active', isPanelOpen);
    });

    expandDRBtn.addEventListener('click', function(event) {
        event.stopPropagation();
        const isCurrentlyOpen = durationPanel.style.display === 'block';
        closeAllPanels();
        isPanelOpen = !isCurrentlyOpen;
        durationPanel.style.display = isPanelOpen ? 'block' : 'none';
        this.classList.toggle('active', isPanelOpen);
    });

    expandRBtn.addEventListener('click', function(event) {
        event.stopPropagation();
        const isCurrentlyOpen = repeatPanel.style.display === 'block';
        closeAllPanels();
        isPanelOpen = !isCurrentlyOpen;
        repeatPanel.style.display = isPanelOpen ? 'block' : 'none';
        this.classList.toggle('active', isPanelOpen);
    });

    // Quick messages
    const quickMsgBtns = document.querySelectorAll('.quick-msg-btn');
    quickMsgBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            messageInput.value = this.textContent;
            messageInput.focus();
            isPanelOpen = false;
            expandedPanel.style.display = 'none';
            expandBtn.classList.remove('active');
        });
    });
    
     const repeatSlider = document.getElementById('repeatSlider');
    const settingDisplay2 = document.getElementById('settingDisplay2');

    function updateRepeatText() {
        const value = repeatSlider.value;
        console.log('Slider value:', value);
        const timeText = value === "1" ? "time" : "times";
        settingDisplay2.textContent = `Repeat: ${value} ${timeText}`;
    }

    if (repeatSlider) {
        repeatSlider.addEventListener('input', updateRepeatText);
        updateRepeatText();
    }

    // Message sending functionality
    const sendBtn = document.querySelector('.send-btn');

    function calculateTransmissionTime(message, duration, repeat) {
        const ditDuration = parseInt(duration); // Base unit time in ms
        let totalUnits = 0;

        // Morse code patterns and their unit lengths
        const MORSE_PATTERNS = {
            'A': '.-',     'B': '-...',   'C': '-.-.', 
            'D': '-..',    'E': '.',      'F': '..-.',
            'G': '--.',    'H': '....',   'I': '..',
            'J': '.---',   'K': '-.-',    'L': '.-..',
            'M': '--',     'N': '-.',     'O': '---',
            'P': '.--.',   'Q': '--.-',   'R': '.-.',
            'S': '...',    'T': '-',      'U': '..-',
            'V': '...-',   'W': '.--',    'X': '-..-',
            'Y': '-.--',   'Z': '--...',
            '0': '-----',  '1': '.----',  '2': '..---',
            '3': '...--',  '4': '....-',  '5': '.....',
            '6': '-....',  '7': '--...',  '8': '---..',
            '9': '----.',
            '.': '.-.-.-', ',': '--..--', ':': '---...',
            '?': '..--..', '&': '.-...', "'": '.----.',
            '@': '.--.-.', ')': '-.--.-', '(': '-.--.',
            '=': '-...-',  '!': '-.-.--', '-': '-....-',
            '+': '.-.-.', '/': '-..-.'
        };

        // Calculate units for each character
        for (let i = 0; i < message.length; i++) {
            const char = message[i].toUpperCase();
            
            if (char === ' ') {
                // Word space (7 units)
                totalUnits += 7;
            } else if (MORSE_PATTERNS[char]) {
                const pattern = MORSE_PATTERNS[char];
                
                // Calculate units for dots and dashes
                for (let j = 0; j < pattern.length; j++) {
                    // Dot = 1 unit, Dash = 3 units
                    totalUnits += (pattern[j] === '.') ? 1 : 3;
                    
                    // Add 1 unit space between elements (dots/dashes)
                    if (j < pattern.length - 1) totalUnits += 1;
                }
                
                // Add 3 units space between characters
                if (i < message.length - 1) totalUnits += 3;
            }
    }

    // Calculate total time including repeats
    let totalTime = totalUnits * ditDuration;
    
    // Add time for repeats
    if (repeat > 1) {
        // Add 7 units space between repeats
        totalTime = (totalTime + (7 * ditDuration)) * repeat;
    }

    // Add a small buffer (500ms)
    return totalTime + 500;
    }

    function startCountdownTimer(duration) {
        const timerElement = document.getElementById('countdownTimer');
        const endTime = Date.now() + duration;
        
        // Show and activate timer
        timerElement.classList.add('active');
        
        // Update timer every 100ms
        const timerInterval = setInterval(() => {
            const timeLeft = Math.ceil((endTime - Date.now()) / 1000);
            
            if (timeLeft <= 0) {
                clearInterval(timerInterval);
                timerElement.classList.remove('active');
                return;
            }
            
            // Format time remaining
            const minutes = Math.floor(timeLeft / 60);
            const seconds = timeLeft % 60;
            const timeString = `Transmitting: ${minutes}:${seconds.toString().padStart(2, '0')}`;
            
            timerElement.textContent = timeString;
        }, 100);
    }

    let canSend = true;

    function disableSendButton(button, delay) {
    button.disabled = true;
    button.style.backgroundColor = '#cccccc';
    button.style.cursor = 'not-allowed';
    canSend = false;
    
    setTimeout(() => {
        button.disabled = false;
        button.style.backgroundColor = 'cornflowerblue';
        button.style.cursor = 'pointer';
        canSend = true;
    }, delay);
    }
    
    function getCurrentChannel() {
        const selectedVessel = document.querySelector('.vessel-btn.selected');
        return selectedVessel ? selectedVessel.getAttribute('data-vessel') : null;
    }

    sendBtn.addEventListener('click', async function() {
        if (!canSend) {
        return; // Don't process if we can't send yet
        }

        const message = messageInput.value.trim();
        const currentChannel = getCurrentChannel();
        
        if (!message) return;
        
        if (!currentChannel) {
            alert('Please select a channel first');
            return;
        }
        
        // Get values from sliders
        const duration = document.getElementById('durationSlider').value;
        const repeat = document.getElementById('repeatSlider').value;
       
        // Calculate transmission time
        const transmissionTime = calculateTransmissionTime(message, duration, repeat);

        // Start countdown timer
        startCountdownTimer(transmissionTime);
        
        // Disable the send button immediately
        disableSendButton(this, transmissionTime);

        // Create a temporary message object for immediate display
        const tempMessage = {
            message_sent: message,
            message_received: '[No Message Received]',
            formatted_time: new Date().toLocaleString('en-GB', { 
                year: 'numeric', 
                month: '2-digit', 
                day: '2-digit',
                hour: '2-digit',
                minute: '2-digit',
                second: '2-digit'
            }),
            vessel_sender: currentChannel,
            vessel_recipient: 'All'
        };

        // Immediately add the message to UI
        addMessageToUI(tempMessage);
        messageInput.value = '';

        try {
            const response = await fetch('/send_message', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: message,
                    sender: currentChannel,
                    duration: parseInt(duration),
                    repeat: parseInt(repeat)
                })
            });
            
            const data = await response.json();
            
            if (data.status !== 'success') {
                console.error('Error sending message:', data.message);
            } 
        } catch (error) {
            console.error('Error sending message:', error);
        }
    });

    // Enter key functionality
    messageInput.addEventListener('keypress', function(event) {
        if (event.key === 'Enter') {
            sendBtn.click();
        }
    });

    // Menu button click handler
    menuBtn.addEventListener('click', function(event) {
        event.stopPropagation();
        menuOpen = !menuOpen;
        
        menuPanel.classList.toggle('active');
        mainContent.classList.toggle('shifted');
        
        fetch('/toggle_menu', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ menuOpen: menuOpen })
        });
    });

    // Close menu when clicking outside
    document.addEventListener('click', function(event) {
        if (menuOpen && 
            !menuPanel.contains(event.target) && 
            !menuBtn.contains(event.target)) {
            menuOpen = false;
            menuPanel.classList.remove('active');
            mainContent.classList.remove('shifted');
            
            fetch('/toggle_menu', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ menuOpen: false })
            });
        }
    });

    // Close panels when clicking outside
    document.addEventListener('click', function(event) {
        const clickedInsideKeys = Array.from(document.querySelectorAll('.key')).some(key => key.contains(event.target));
        if (!expandedPanel.contains(event.target) &&
            !expandBtn.contains(event.target) &&
            !durationPanel.contains(event.target) &&
            !expandDRBtn.contains(event.target) &&
            !repeatPanel.contains(event.target) &&
            !expandRBtn.contains(event.target) &&
            !clickedInsideKeys) {
            closeAllPanels();
        }
    });

    // Set initial channel and load messages
    const initialChannel = currentChannelDisplay.textContent || 'All';
    const initialVesselBtn = document.querySelector(`.vessel-btn[data-vessel="${initialChannel}"]`);
    if (initialVesselBtn) {
        initialVesselBtn.classList.add('selected');
    }
    updateMessages(initialChannel);

    // Window resize handler
    window.addEventListener('resize', function() {
        if (window.innerWidth > 768) {
            mainContent.classList.toggle('shifted', menuOpen);
        } else {
            mainContent.classList.remove('shifted');
        }
    });
});
"""

def setup_js_route(app):
    """Setup the JavaScript route for Flask"""
    @app.route('/static/js/design.js')
    def serve_js():
        return get_js_content(), 200, {'Content-Type': 'text/javascript'}