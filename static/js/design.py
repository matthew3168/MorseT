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

    // Menu search functionality
    const searchInput = document.querySelector('.search input[type="text"]');
    const messageInput = document.getElementById('messageInput');
    const vesselBtns = document.querySelectorAll('.vessel-btn');

    let activeInput = searchInput;

    // Focus on the search input when 'Tab' is pressed
    searchInput.addEventListener('focus', () => {
        activeInput = searchInput;
    });

    messageInput.addEventListener('focus', () => {
        activeInput = messageInput;
    });

    // Listen for keydown event to toggle between inputs
    document.addEventListener('keydown', function(event) {
        if (event.key === 'Tab') {
            event.preventDefault();  // Prevent default tab behavior
            
            // Switch between search input and message input
            if (activeInput === searchInput) {
                messageInput.focus();
                activeInput = messageInput;
            } else {
                searchInput.focus();
                activeInput = searchInput;
            }
        }
    });

    // Handle virtual keyboard input
    document.querySelectorAll('.key').forEach(key => {
        key.addEventListener('click', function(event) {
            // Prevent the click from bubbling up and closing panels
            if (event.target.classList.contains('switch')) {
                event.preventDefault();  // Prevent the "SPECIAL" or "NORMAL" text from being inserted
                return;  // Do nothing if the switch button is clicked
            }

            event.stopPropagation();  // Prevent the click from bubbling up

            const keyText = this.textContent;
            const activeInputField = activeInput;  // Get the active input field (search or message)

            // Check if the keyText is a space or an empty string, do nothing if it is
            if (keyText === ' ' || keyText === '') {
                return;  // If the key should not do anything (space or empty), just return
            }

            // Handle delete, space, or other key inputs
            if (this.classList.contains('delete')) {
                activeInputField.value = activeInputField.value.slice(0, -1);  // Remove last character
            } else if (this.classList.contains('space')) {
                activeInputField.value += ' ';  // Add space
            } else {
                activeInputField.value += keyText;  // Add key text
            }

            activeInputField.focus();  // Keep focus on the active input field

            // Trigger search filtering only when typing in the search input
            if (activeInputField === searchInput) {
                const searchQuery = searchInput.value.toLowerCase();
                vesselBtns.forEach(btn => {
                    const vesselName = btn.textContent.toLowerCase();
                    if (vesselName.includes(searchQuery)) {
                        btn.style.display = 'block';
                    } else {
                        btn.style.display = 'none';
                    }
                });
            }

            // Prevent default keydown event from triggering another input
            event.preventDefault();
        });
    });


    // Keyboard for special characters
    document.querySelector('.switch').addEventListener('click', function(event) {
        event.stopPropagation();  // Prevent the click from propagating to the input handling

        // Prevent text input into the input field
        event.preventDefault();

        toggleSpecial();  // Toggle the special characters mode
    });

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
        ' ': ' ',
    };

    let isSpecial = false;

    // Function to toggle the special characters and the "SPECIAL" button text
    function toggleSpecial() {
        const keys = document.querySelectorAll('.key');
        const switchButton = document.querySelector('.switch');

        keys.forEach(key => {
            const originalKeyText = key.getAttribute('data-original');
            const currentKeyText = key.textContent;

            if (specialCharMap[originalKeyText]) {
                // Toggle between special characters and regular ones
                key.textContent = isSpecial ? originalKeyText : specialCharMap[originalKeyText];
            }
        });

        // Toggle the "SPECIAL"/"NORMAL" button text
        if (isSpecial) {
            switchButton.textContent = 'SPECIAL';
        } else {
            switchButton.textContent = 'NORMAL';
        }

        // Toggle the isSpecial flag
        isSpecial = !isSpecial;
    }



    // Event listener for search input to filter vessel names (case-insensitive)
    searchInput.addEventListener('input', function(event) {
        // Get the search query (case-insensitive)
        const searchQuery = searchInput.value.toLowerCase();
        
        vesselBtns.forEach(btn => {
            const vesselName = btn.textContent.toLowerCase();
            // Show or hide vessel buttons based on the search query
            if (vesselName.includes(searchQuery)) {
                btn.style.display = 'block';  // Show vessel
            } else {
                btn.style.display = 'none';   // Hide vessel
            }
        });
    });

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

    // Vessel selection functionality
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
    let rightPanelOpen = false;

    const keys = document.querySelectorAll('.key');

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

    // Close panels except when clicking the keyboard
    document.addEventListener('click', function(event) {
        const clickedInsideKeys = Array.from(keys).some(key => key.contains(event.target));
        if (!expandedPanel.contains(event.target) &&
            !expandBtn.contains(event.target) &&
            !durationPanel.contains(event.target) &&
            !expandDRBtn.contains(event.target) &&
            !repeatPanel.contains(event.target) &&
            !expandRBtn.contains(event.target) &&
            !clickedInsideKeys) { // Don't close when clicking on keyboard keys
            closeAllPanels();
        }
    });
}

    const currentChannelDisplay = document.getElementById('currentChannel');
    let menuOpen = false;

    // Panel expansion functionality
    const expandBtn = document.getElementById('expandBtn');
    const expandedPanel = document.getElementById('expandedPanel');
    const quickMsgBtns = document.querySelectorAll('.quick-msg-btn');
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