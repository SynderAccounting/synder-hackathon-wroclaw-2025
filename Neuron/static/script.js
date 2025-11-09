// Tab Switching Functionality
document.addEventListener('DOMContentLoaded', function() {
    const tabButtons = document.querySelectorAll('.tab-button');
    const tabContents = document.querySelectorAll('.tab-content');

    tabButtons.forEach(button => {
        button.addEventListener('click', function() {
            const targetTab = this.getAttribute('data-tab');

            // Remove active class from all buttons and contents
            tabButtons.forEach(btn => btn.classList.remove('active'));
            tabContents.forEach(content => content.classList.remove('active'));

            // Add active class to clicked button and corresponding content
            this.classList.add('active');
            document.getElementById(targetTab).classList.add('active');

            // If switching to sales tab, ensure predictions are loaded
            if (targetTab === 'sales' && typeof generatePredictions === 'function') {
                // Check if predictions are already loaded
                const predictionsGrid = document.getElementById('predictionsGrid');
                if (predictionsGrid && predictionsGrid.children.length === 0) {
                    setTimeout(() => generatePredictions(), 100);
                }
            }
        });
    });
    
    // Chatbot functionality
    const globalChatbotBtn = document.getElementById('global-chatbot-btn');
    const globalChatbotModal = document.getElementById('global-chatbot-modal');
    const closeGlobalChatbot = document.getElementById('close-global-chatbot');
    const globalChatbotInput = document.getElementById('global-chatbot-input');
    const sendGlobalChatbot = document.getElementById('send-global-chatbot');
    const globalChatbotMessages = document.getElementById('global-chatbot-messages');

    if (globalChatbotBtn && globalChatbotModal && closeGlobalChatbot && globalChatbotInput && sendGlobalChatbot && globalChatbotMessages) {
        // Open chatbot modal
        globalChatbotBtn.addEventListener('click', function() {
            globalChatbotModal.style.display = 'flex';
            // Add a welcome animation when opening
            setTimeout(() => {
                const lastMessage = globalChatbotMessages.lastElementChild;
                if (lastMessage && lastMessage.classList.contains('bot-message')) {
                    lastMessage.style.opacity = '1';
                }
            }, 100);
        });

        // Close chatbot modal
        closeGlobalChatbot.addEventListener('click', function() {
            globalChatbotModal.style.display = 'none';
        });

        // Close modal when clicking outside content
        globalChatbotModal.addEventListener('click', function(e) {
            if (e.target === globalChatbotModal) {
                globalChatbotModal.style.display = 'none';
            }
        });

        // Send message on button click
        sendGlobalChatbot.addEventListener('click', function() {
            const userInput = globalChatbotInput.value.trim();
            if (!userInput) return;
            
            addGlobalMessage(userInput, 'user');
            globalChatbotInput.value = '';
            
            // Show typing indicator with personality
            const typingMessage = addGlobalMessage('Synder Assistant is thinking...', 'bot', true);

            // Use the knowledge base chatbot (app_chatbot) by default
            // This chatbot explains features and provides help without SQL queries
            let apiEndpoint = '/api/app_chatbot';

            // Send to backend API
            fetch(apiEndpoint, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ question: userInput })
            })
            .then(response => response.json())
            .then(data => {
                // Remove typing indicator
                typingMessage.remove();

                if (data.error) {
                    addGlobalMessage('Sorry, I encountered an error: ' + data.error, 'bot');
                } else {
                    if (data.result) {
                        addGlobalMessage(data.result, 'bot');
                    } else if (data.message) {
                        addGlobalMessage(data.message, 'bot');
                    } else {
                        addGlobalMessage("I couldn't understand your question. Could you try rephrasing? I'm here to help with CRM tasks, customer data, or product information!", 'bot');
                    }
                }
            })
            .catch(error => {
                // Remove typing indicator
                typingMessage.remove();
                addGlobalMessage('Sorry, I had trouble processing your request: ' + error.message + '. Please try again!', 'bot');
            });
        });

        // Handle Enter key in chatbot input
        globalChatbotInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                sendGlobalChatbot.click();
            }
        });
    }

    function addGlobalMessage(text, sender, isTyping = false) {
        const messagesContainer = globalChatbotMessages;
        const messageDiv = document.createElement('div');
        
        if (!isTyping) {
            messageDiv.className = `message ${sender}-message`;
            
            // Add personality to bot messages
            if (sender === 'bot') {
                messageDiv.innerHTML = `<strong>🤖 Synder Assistant:</strong> ${text}`;
            } else {
                messageDiv.innerHTML = `<strong>👤 You:</strong> ${text}`;
            }
        } else {
            messageDiv.className = `message ${sender}-message typing-container`;
            messageDiv.innerHTML = `<strong>🤖 Synder Assistant:</strong> <span class="typing"><span></span><span></span><span></span></span>`;
        }

        messagesContainer.appendChild(messageDiv);
        // Scroll to bottom with smooth animation
        messagesContainer.scrollTop = messagesContainer.scrollHeight;

        return messageDiv;
    }
    
    function containsStructuredData(text) {
        // Check if text contains multiple lines with similar patterns (indicating structured data)
        const lines = text.split('<br>');
        
        if (lines.length < 2) return false;
        
        // Look for key-value patterns across multiple lines
        let structuredLineCount = 0;
        for (let line of lines) {
            if (line.includes(':')) {
                // Count how many colons (key-value indicators) are in the line
                const colonCount = (line.match(/:\s/g) || []).length;
                if (colonCount >= 2) { // At least 2 key-value pairs
                    structuredLineCount++;
                }
            }
        }
        
        // If at least 2 lines have structured data, return true
        return structuredLineCount >= 2;
    }
    
    function createInteractiveTable(text) {
        // Create a container for the table
        const tableContainer = document.createElement('div');
        tableContainer.className = 'chatbot-table-container';
        tableContainer.style.marginTop = '10px';
        tableContainer.style.overflowX = 'auto';
        
        // Parse the text to identify table structure
        const lines = text.split('<br>');
        if (lines.length <= 1) {
            // If no line breaks, just return the text as is
            const textNode = document.createElement('div');
            textNode.innerHTML = text;
            return textNode;
        }
        
        // Identify common keys from all lines to create headers
        const allKeys = new Set();
        lines.forEach(line => {
            if (line.trim() && !line.startsWith('<strong>')) {
                // Extract keys from key-value pairs like "Key: value"
                const keyMatches = line.match(/(\w+(?:\s+\w+)*?):\s/g) || [];
                keyMatches.forEach(match => {
                    const key = match.replace(':','').trim();
                    allKeys.add(key);
                });
            }
        });
        
        const headers = Array.from(allKeys);
        if (headers.length < 2) {
            const textNode = document.createElement('div');
            textNode.innerHTML = text;
            return textNode;
        }
        
        // Create table
        const table = document.createElement('table');
        table.className = 'chatbot-table';
        table.style.width = '100%';
        table.style.borderCollapse = 'collapse';
        table.style.marginTop = '5px';
        
        // Create header row
        const thead = document.createElement('thead');
        const headerRow = document.createElement('tr');
        headers.forEach(header => {
            const th = document.createElement('th');
            th.style.padding = '8px';
            th.style.border = '1px solid #ddd';
            th.style.backgroundColor = '#f2f2f2';
            th.style.textAlign = 'left';
            th.textContent = header;
            headerRow.appendChild(th);
        });
        thead.appendChild(headerRow);
        table.appendChild(thead);
        
        // Create body rows
        const tbody = document.createElement('tbody');
        lines.forEach(line => {
            if (line.trim() && !line.startsWith('<strong>')) {
                const row = document.createElement('tr');
                row.style.borderBottom = '1px solid #ddd';
                
                // For each header, find the corresponding value in the line
                headers.forEach(header => {
                    const cell = document.createElement('td');
                    cell.style.padding = '8px';
                    cell.style.borderBottom = '1px solid #ddd';
                    cell.style.borderRight = headers.length > 1 ? '1px solid #ddd' : 'none';
                    
                    // Try to find value for this header in the current line
                    const escapedHeader = header.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'); // Escape special regex chars
                    const pattern = new RegExp(`${escapedHeader}:\\s*([^,]+?)(?:,|$|<br>)`, 'i');
                    const match = line.match(pattern);
                    
                    if (match) {
                        cell.textContent = match[1].trim();
                    } else {
                        cell.textContent = 'N/A'; // Default value if not found
                    }
                    
                    row.appendChild(cell);
                });
                
                tbody.appendChild(row);
            }
        });
        
        table.appendChild(tbody);
        tableContainer.appendChild(table);
        
        return tableContainer;
    }

    // Handle filter form submission in products page
    const filterForm = document.querySelector('.search-form');
    if (filterForm) {
        filterForm.addEventListener('submit', function(e) {
            // Check if the submit button clicked is the filter button
            const submitter = e.submitter;
            if (submitter && submitter.classList.contains('btn-primary')) {
                // For filter button, submit the form normally
                return;
            }
        });
    }

    // For filter options in product page, prevent default form submission when clicking filter button
    const filterButton = document.querySelector('.filter-options .btn-primary');
    if (filterButton) {
        filterButton.addEventListener('click', function(e) {
            e.preventDefault(); // Prevent default form submission
            
            // This will submit the form with the GET method
            // The form will be submitted with all the filter parameters
            const form = document.querySelector('.search-form');
            if (form) {
                // Combine the search form and filter options into one form
                // Add the filter values to the URL parameters
                const category = document.getElementById('category');
                const minPrice = document.getElementById('min_price');
                const maxPrice = document.getElementById('max_price');
                const minStock = document.getElementById('min_stock');
                const maxStock = document.getElementById('max_stock');
                const searchInput = document.querySelector('input[name="search"]');

                let url = new URL(window.location);
                
                // Update URL parameters based on form values
                if (searchInput && searchInput.value) {
                    url.searchParams.set('search', searchInput.value);
                } else {
                    url.searchParams.delete('search');
                }
                
                if (category && category.value) {
                    url.searchParams.set('category', category.value);
                } else {
                    url.searchParams.delete('category');
                }
                
                if (minPrice && minPrice.value) {
                    url.searchParams.set('min_price', minPrice.value);
                } else {
                    url.searchParams.delete('min_price');
                }
                
                if (maxPrice && maxPrice.value) {
                    url.searchParams.set('max_price', maxPrice.value);
                } else {
                    url.searchParams.delete('max_price');
                }
                
                if (minStock && minStock.value) {
                    url.searchParams.set('min_stock', minStock.value);
                } else {
                    url.searchParams.delete('min_stock');
                }
                
                if (maxStock && maxStock.value) {
                    url.searchParams.set('max_stock', maxStock.value);
                } else {
                    url.searchParams.delete('max_stock');
                }

                // Redirect to URL with new parameters
                window.location.href = url.toString();
            }
        });
    }
});
