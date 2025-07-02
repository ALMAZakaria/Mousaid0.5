import { useState, useEffect } from 'react';
import { marked } from 'marked';

export default function Home() {
  const [userInput, setUserInput] = useState('');
  const [chatMessages, setChatMessages] = useState([]);
  const [greeting, setGreeting] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [selectedLanguage, setSelectedLanguage] = useState('');

  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/greeting")
      .then(res => res.json())
      .then(data => setGreeting(data.message))
      .catch(err => console.error("Failed to fetch greeting:", err));
  }, []);

  useEffect(() => {
    const chatMessagesDiv = document.getElementById('chat-messages');
    if (chatMessagesDiv) {
      chatMessagesDiv.scrollTop = chatMessagesDiv.scrollHeight;
    }
  }, [chatMessages]);

  const sendMessage = async () => {
    if (userInput.trim() === '') return;

    const newUserMessage = `
      <div class="flex justify-end mb-4">
        <div class="bg-blue-600 text-white p-3 rounded-lg max-w-xs md:max-w-md">
          ${userInput}
        </div>
      </div>
    `;
    setChatMessages((prevMessages) => [...prevMessages, newUserMessage]);
    const currentInput = userInput;
    setUserInput('');

    try {
      setIsLoading(true);
      const response = await fetch('http://127.0.0.1:8000/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: [{ role: 'user', content: currentInput }],
          session_id: localStorage.getItem('session_id'),
          language: selectedLanguage,
        }),
      });

      const data = await response.json();
      if (data.session_id) {
        localStorage.setItem('session_id', data.session_id);
      }
      const botMessageHtml = `
        <div class="flex justify-start mb-4">
          <div class="bg-gray-700 text-white p-3 rounded-lg max-w-xs md:max-w-md">
            ${marked.parse(data.response)}
          </div>
        </div>
      `;
      setChatMessages((prevMessages) => [...prevMessages, botMessageHtml]);
    } catch (error) {
      console.error('Error:', error);
      const errorMessage = `
        <div class="flex justify-start mb-4">
          <div class="bg-red-700 text-white p-3 rounded-lg max-w-xs md:max-w-md">
            Error: Could not connect to the chatbot. Please ensure the backend is running.
          </div>
        </div>
      `;
      setChatMessages((prevMessages) => [...prevMessages, errorMessage]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      sendMessage();
    }
  };

  const handleLanguageChange = (e) => {
    setSelectedLanguage(e.target.value);
  };

  return (
    <div className="bg-gray-900 min-h-screen">
      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <h1 className="text-3xl font-bold text-center mb-8 text-gray-100">Hi, My name's Mousaid! How may I help you today?</h1>
        <div className="rounded-lg shadow-lg p-6">
          <div id="chat-messages" className="h-96 overflow-y-auto mb-4 space-y-4">
            {greeting && (
              <div className="bg-gray-700 text-white p-3 rounded-lg max-w-xs md:max-w-md">
                <span dangerouslySetInnerHTML={{ __html: marked.parse(greeting) }} />
              </div>
            )}
            {chatMessages.map((message, index) => (
              <div key={index} dangerouslySetInnerHTML={{ __html: message }} />
            ))}
            {isLoading && (
              <div className="flex justify-start mb-4">
                <div className="bg-gray-600 text-white p-3 rounded-lg max-w-xs md:max-w-md animate-pulse">
                  Loading...
                </div>
              </div>
            )}
          </div>
        </div>
        <div className="rounded-lg shadow-lg p-6">
          <div className="flex gap-2">
            <select
              value={selectedLanguage}
              onChange={handleLanguageChange}
              style={{ marginRight: '1rem', marginBottom: '1rem' }}
            >
              <option value="">🌐 Choose language</option>
              <option value="en">English</option>
              <option value="fr">Francais</option>
              <option value="ar">العربية</option>
              <option value="darija">Darija (Moroccan Arabic)</option>
            </select>
            <input
              type="text"
              id="user-input"
              className="flex-1 p-2 border border-gray-300 rounded-lg focus:outline-none focus:border-blue-500"
              placeholder="Type your message here..."
              value={userInput}
              onChange={(e) => setUserInput(e.target.value)}
              onKeyPress={handleKeyPress}
            />
            <button
              onClick={sendMessage}
              className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition-colors"
            >
              Send
            </button>
          </div>
        </div>
      </div>
    </div>
  );
} 