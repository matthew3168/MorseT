from flask import url_for

def get_js_content():
    """
    Returns the JavaScript content as a string that will be served by Flask
    """
    return """
document.addEventListener('DOMContentLoaded', function() {

    const EMERGENCY_KEYWORDS = ['SOS', 'MAYDAY'];
    const WARNING_KEYWORDS = ['WARNING', 'REQUESTING ASSISTANCE'];

    function applyMessageHighlighting(messageElement, messageText) {
    const upperText = messageText.toUpperCase();
    
    if (EMERGENCY_KEYWORDS.some(keyword => upperText.includes(keyword))) {
        messageElement.classList.add('emergency');
    } else if (WARNING_KEYWORDS.some(keyword => upperText.includes(keyword))) {
        messageElement.classList.add('warning');
    }
}

    function updateMessages(vessel) {
        const url = vessel && vessel !== 'All' ? 
            `/get_messages/${encodeURIComponent(vessel)}` : 
            '/get_messages';
        
        fetch(url)
            .then(response => response.json())
            .then(data => {
                const chatArea = document.querySelector('.chat-area');
                chatArea.innerHTML = '';
                
                const messages = Array.isArray(data) ? data : data.messages;
                
                messages.reverse().forEach(message => {
                    const messageGroup = document.createElement('div');
                    messageGroup.className = 'message-group';
                    
                    let messageHTML = '';
                    
                    if (message.message_received !== '[No Message Received]') {
                        const receivedDiv = document.createElement('div');
                        receivedDiv.className = 'message-bubble message-received';
                        receivedDiv.textContent = message.message_received;
                        applyMessageHighlighting(receivedDiv, message.message_received);
                        messageHTML += receivedDiv.outerHTML;
                    }
                    
                    if (message.message_sent && message.message_sent !== '[No Message Sent]') {
                        const sentDiv = document.createElement('div');
                        if (message.message_received !== '[No Message Received]') {
                            sentDiv.textContent = `Response: ${message.message_sent}`;
                        } else {
                            sentDiv.textContent = message.message_sent;
                        }
                        sentDiv.className = 'message-bubble message-sent';
                        applyMessageHighlighting(sentDiv, message.message_sent);
                        messageHTML += sentDiv.outerHTML;
                    }
                    
                    messageHTML += `<div class="timestamp ${message.message_sent && message.message_sent != '[No Message Sent]' ? 'timestamp-sent' : 'timestamp-received'}">${message.formatted_time}</div>`;
                    
                    messageGroup.innerHTML = messageHTML;
                    chatArea.appendChild(messageGroup);
                });
                
                chatArea.scrollTop = chatArea.scrollHeight;
            });
    }

    // Duration Slider Functionality
    const slider = document.getElementById('durationSlider');
    const speedDisplay = document.getElementById('speedDisplay');
    const settingDisplay = document.getElementById('settingDisplay');

    function updateSliderDisplay(value) {
        let speed = '';
        let speedColor = '';

        // Determine speed category based on slider value
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

        // Update the display text
    speedDisplay.innerHTML = `<p>Speed:</p><span style="color: ${speedColor};">${speed}</span>`;
    settingDisplay.innerHTML = `<p>Current Setting:</p> <span style="color: ${speedColor};">${value}ms</span>`;

    }

    // Initial display when the page loads
    updateSliderDisplay(slider.value);

    // Add event listener for slider input
    slider.addEventListener('input', function () {
        updateSliderDisplay(this.value);
    });
    
    document.querySelectorAll('.quick-msg-btn').forEach(btn => {
    const buttonText = btn.textContent.toUpperCase();
    if (EMERGENCY_KEYWORDS.some(keyword => buttonText === keyword)) {
        btn.classList.add('emergency');
    } else if (WARNING_KEYWORDS.some(keyword => buttonText === keyword)) {
        btn.classList.add('warning');
    }
    });

    // Menu functionality
    const menuBtn = document.querySelector('.menu-btn');
    const menuPanel = document.getElementById('menuPanel');
    const mainContent = document.getElementById('mainContent');
    const rightPanel = document.getElementById('rightPanel');
    const rightPanelToggle = document.getElementById('rightPanelToggle');
    let rightPanelOpen = false;

    if (rightPanelToggle) {  // Check if element exists
        rightPanelToggle.addEventListener('click', function(event) {
            event.stopPropagation();
            rightPanelOpen = !rightPanelOpen;
            
            if (rightPanel) {
                rightPanel.classList.toggle('active');
                mainContent.classList.toggle('shifted-right');
                
                // Change arrow direction
                rightPanelToggle.textContent = rightPanelOpen ? '→' : '←';
            }
        });

        // Close panel when clicking outside
        document.addEventListener('click', function(event) {
            if (rightPanelOpen && 
                rightPanel && 
                !rightPanel.contains(event.target) && 
                !rightPanelToggle.contains(event.target)) {
                rightPanelOpen = false;
                rightPanel.classList.remove('active');
                mainContent.classList.remove('shifted-right');
                rightPanelToggle.textContent = '←';
            }
        });
    }
    const currentChannelDisplay = document.getElementById('currentChannel');
    let menuOpen = false;

    // Panel expansion functionality
    const expandBtn = document.getElementById('expandBtn');
    const expandedPanel = document.getElementById('expandedPanel');
    const quickMsgBtns = document.querySelectorAll('.quick-msg-btn');
    const messageInput = document.getElementById('messageInput');
    let isPanelOpen = false;

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

    // Function to close all panels
    function closeAllPanels() {
        expandedPanel.style.display = 'none';
        durationPanel.style.display = 'none';
        repeatPanel.style.display = 'none';

        expandBtn.classList.remove('active');
        expandDRBtn.classList.remove('active');
        expandRBtn.classList.remove('active');
        isPanelOpen = false;

    }

    // Expand panel button click handler
    expandBtn.addEventListener('click', function(event) {
        event.stopPropagation();
        const isCurrentlyOpen = expandedPanel.style.display === 'block';
        closeAllPanels(); // Close all panels first
        isPanelOpen = !isCurrentlyOpen; // Toggle the target panel
        expandedPanel.style.display = isPanelOpen ? 'block' : 'none';
        this.classList.toggle('active', isPanelOpen);
    });

    // Duration panel
    expandDRBtn.addEventListener('click', function(event) {
        event.stopPropagation();
        const isCurrentlyOpen = durationPanel.style.display === 'block';
        closeAllPanels();
        isPanelOpen = !isCurrentlyOpen;
        durationPanel.style.display = isPanelOpen ? 'block' : 'none';
        this.classList.toggle('active', isPanelOpen);
    });

    // Repeat
    expandRBtn.addEventListener('click', function(event) {
        event.stopPropagation();
        const isCurrentlyOpen = repeatPanel.style.display === 'block';
        closeAllPanels();
        isPanelOpen = !isCurrentlyOpen;
        repeatPanel.style.display = isPanelOpen ? 'block' : 'none';
        this.classList.toggle('active', isPanelOpen);
    });

    // Repeat Slider functionality
    const repeatSlider = document.getElementById('repeatSlider'); 
    const settingDisplayRepeat = document.getElementById('settingDisplay2');  // Updated reference for the repeat slider

    function updateRepeatText() {
        const value = repeatSlider.value;  
        console.log('Slider value:', value);  // Debugging: Log the slider value
        const timeText = value === "1" ? "time" : "times";
        settingDisplayRepeat.textContent = `Repeat: ${value} ${timeText}`;  // Update the display text
    }

    // Add event listener to update the text when the repeat slider value changes
    repeatSlider.addEventListener('input', updateRepeatText);

    // Initialize the repeat text on page load
    updateRepeatText();
    
    // Close panels when clicking outside
    document.addEventListener('click', function(event) {
        if (!expandedPanel.contains(event.target) && 
            !expandBtn.contains(event.target) &&
            !durationPanel.contains(event.target) &&
            !expandDRBtn.contains(event.target) &&
            !repeatPanel.contains(event.target) &&
            !expandRBtn.contains(event.target)) {
            closeAllPanels();
        }
    });
    

    // Quick message button functionality
    quickMsgBtns.forEach(btn => {
        btn.addEventListener('click', function() {
            messageInput.value = this.textContent;
            messageInput.focus();
            // Close the panel after selection
            isPanelOpen = false;
            expandedPanel.style.display = 'none';
            expandBtn.classList.remove('active');
        });
    });

    // Close panel when clicking outside
    document.addEventListener('click', function(event) {
        if (isPanelOpen && 
            !expandedPanel.contains(event.target) && 
            !expandBtn.contains(event.target)) {
            isPanelOpen = false;
            expandedPanel.style.display = 'none';
            expandBtn.classList.remove('active');
        }
    });

    // Virtual keyboard functionality
    const keys = document.querySelectorAll('.key');
    
    keys.forEach(key => {
        key.addEventListener('click', function() {
            const keyText = this.textContent;
            if (this.classList.contains('delete')) {
                messageInput.value = messageInput.value.slice(0, -1);
            } else if (this.classList.contains('space')) {
                messageInput.value += ' ';
            } else {
                messageInput.value += keyText;
            }
            messageInput.focus();
        });
    });

// Message sending functionality
    const sendBtn = document.querySelector('.send-btn');
    
    function getCurrentChannel() {
        const selectedVessel = document.querySelector('.vessel-btn.selected');
        return selectedVessel ? selectedVessel.getAttribute('data-vessel') : null;
    }
    
    function addMessageToUI(message) {
        const chatArea = document.querySelector('.chat-area');
        const messageGroup = document.createElement('div');
        messageGroup.className = 'message-group';
        
        let messageHTML = '';
        
        if (message.message_received !== '[No Message Received]') {
            const receivedDiv = document.createElement('div');
            receivedDiv.className = 'message-bubble message-received';
            receivedDiv.textContent = message.message_received;
            applyMessageHighlighting(receivedDiv, message.message_received);
            messageHTML += receivedDiv.outerHTML;
        }
        
        if (message.message_sent && message.message_sent !== '[No Message Sent]') {
            const sentDiv = document.createElement('div');
            sentDiv.className = 'message-bubble message-sent';
            sentDiv.textContent = message.message_sent;
            applyMessageHighlighting(sentDiv, message.message_sent);
            messageHTML += sentDiv.outerHTML;
        }
        
        messageHTML += `<div class="timestamp ${message.message_sent ? 'timestamp-sent' : 'timestamp-received'}">${message.formatted_time}</div>`;
        
        messageGroup.innerHTML = messageHTML;
        chatArea.appendChild(messageGroup);
        chatArea.scrollTop = chatArea.scrollHeight;
    }
    
    sendBtn.addEventListener('click', async function() {
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

    // Vessel selection functionality
    const vesselBtns = document.querySelectorAll('.vessel-btn');
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

    // Message sending functionality
    sendBtn.addEventListener('click', function() {
        // Get values from the input fields and sliders
        const message = messageInput.value.trim();
        const duration = durationSlider.value; // Duration from the slider (in ms)
        const repeat = repeatSlider.value; // Repeat count from the slider

        // Check if message is not empty
        if (message) {
            // Create a JSON object with the required fields
            const jsonMessage = {
                message: message,
                duration: parseInt(duration), 
                repeat: parseInt(repeat) 
            };

            // Log the JSON message for debugging
            console.log("Created JSON message:", JSON.stringify(jsonMessage));

            // You can send this JSON message via HTTP POST (this is commented for now)
            // Example of sending to the ESP32 (replace URL with actual ESP32 endpoint)
            /*
            fetch('http://esp32-ip-address/send_message', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(jsonMessage)
            })
            .then(response => response.json())
            .then(data => {
                console.log('Message sent successfully:', data);
            })
            .catch(error => {
                console.error('Error sending message:', error);
            });
            */

            // Optionally clear the message input after sending
            messageInput.value = '';
        }
    });

    // Function to update messages
    function updateMessages(vessel) {
        const url = vessel && vessel !== 'All' ? 
            `/get_messages/${encodeURIComponent(vessel)}` : 
            '/get_messages';
        
        fetch(url)
            .then(response => response.json())
            .then(data => {
                const chatArea = document.querySelector('.chat-area');
                chatArea.innerHTML = '';
                
                const messages = Array.isArray(data) ? data : data.messages;
                
                messages.reverse().forEach(message => {
                    const messageGroup = document.createElement('div');
                    messageGroup.className = 'message-group';
                    
                    let messageHTML = '';
                    
                    if (message.message_received !== '[No Message Received]') {
                        messageHTML += `<div class="message-bubble message-received">${message.message_received}</div>`;
                    }
                    
                    if (message.message_sent && message.message_sent !== '[No Message Sent]') {
                        if (message.message_received !== '[No Message Received]') {
                            messageHTML += `<div class="message-bubble message-sent">Response: ${message.message_sent}</div>`;
                        } else {
                            messageHTML += `<div class="message-bubble message-sent">${message.message_sent}</div>`;
                        }
                    }
                    
                    messageHTML += `<div class="timestamp ${message.message_sent && message.message_sent != '[No Message Sent]' ? 'timestamp-sent' : 'timestamp-received'}">${message.formatted_time}</div>`;
                    
                    messageGroup.innerHTML = messageHTML;
                    chatArea.appendChild(messageGroup);
                });
                
                chatArea.scrollTop = chatArea.scrollHeight;
            });
    }

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