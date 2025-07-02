import { useState, useEffect, useRef } from 'react';
import { marked } from 'marked';

export default function AIAgent() {
  const [userInput, setUserInput] = useState('');
  const [chatMessages, setChatMessages] = useState([]);
  const [greeting, setGreeting] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [darkMode, setDarkMode] = useState(() => {
    // Check localStorage for mode preference
    if (typeof window !== 'undefined') {
      return localStorage.getItem('theme') === 'dark';
    }
    return false;
  });
  const [selectedLanguage, setSelectedLanguage] = useState('');
  const chatEndRef = useRef(null);

  useEffect(() => {
    fetch("http://127.0.0.1:8000/api/greeting")
      .then(res => res.json())
      .then(data => setGreeting(data.message))
      .catch(err => console.error("Failed to fetch greeting:", err));
  }, []);

  useEffect(() => {
    if (chatEndRef.current) {
      chatEndRef.current.scrollIntoView({ behavior: 'smooth' });
    }
  }, [chatMessages]);

  useEffect(() => {
    if (darkMode) {
      document.documentElement.classList.add('dark');
      localStorage.setItem('theme', 'dark');
    } else {
      document.documentElement.classList.remove('dark');
      localStorage.setItem('theme', 'light');
    }
  }, [darkMode]);

  const toggleDarkMode = () => setDarkMode((prev) => !prev);

  const sendMessage = async () => {
    if (userInput.trim() === '') return;
    const newUserMessage = {
      type: 'user',
      content: userInput
    };
    setChatMessages((prev) => [...prev, newUserMessage]);
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
      if (response.status === 429) {
        setChatMessages((prev) => [
          ...prev,
          { type: 'error', content: data.response || "You have exceeded your daily quota for the Gemini API. Please try again tomorrow or upgrade your plan." }
        ]);
        return;
      }
      setChatMessages((prev) => [
        ...prev,
        { type: 'bot', content: data.response }
      ]);
    } catch (error) {
      setChatMessages((prev) => [
        ...prev,
        { type: 'error', content: 'Error: Could not connect to the chatbot. Please ensure the backend is running.' }
      ]);
    } finally {
      setIsLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      sendMessage();
    }
  };

  const handleLanguageChange = (e) => {
    setSelectedLanguage(e.target.value);
  };

  return (
    <div className={
      `min-h-screen flex flex-col items-center justify-center transition-colors duration-300 ` +
      (darkMode
        ? 'bg-gradient-to-br from-gray-900 to-gray-800'
        : 'bg-gradient-to-br from-blue-50 to-blue-200')
    }>
      <div
        className={
          // Responsive: 90vw on mobile, max-w-4xl on desktop
          `w-full max-w-4xl rounded-2xl shadow-xl flex flex-col overflow-hidden ` +
          'h-[80vh] sm:h-[90vh] sm:w-[90vw] sm:max-w-none sm:rounded-none sm:shadow-none ' +
          'xs:w-[100vw] xs:rounded-none xs:shadow-none ' +
          (darkMode ? 'bg-gray-900' : 'bg-white')
        }
        style={{ minHeight: '100vh' }}
      >
        <header
          className={
            `py-4 px-4 sm:py-3 sm:px-2 flex items-center gap-2 sm:gap-1 ` +
            (darkMode ? 'bg-gray-800 text-white' : 'bg-blue-600 text-white')
          }
        >
          <span className="text-2xl sm:text-xl">🚗</span>
          <h1 className="text-xl sm:text-lg font-bold flex-1 truncate">Mousaid - Car Assistant</h1>
          <select
            value={selectedLanguage}
            onChange={handleLanguageChange}
            className={
              `rounded-lg px-2 py-1 transition-colors duration-300 text-sm sm:text-xs ` +
              (darkMode
                ? 'bg-gray-700 text-blue-100 border border-gray-600'
                : 'bg-blue-100 text-gray-900 border border-blue-200')
            }
            style={{ marginRight: '0.5rem' }}
          >
            <option value="">🌐 Choose language</option>
            <option value="en">English</option>
            <option value="fr">Francais</option>
            <option value="ar">العربية</option>
            <option value="darija">Darija (Moroccan Arabic)</option>
          </select>
          <button
            onClick={toggleDarkMode}
            className={
              'rounded-full p-2 transition-colors ' +
              (darkMode
                ? 'bg-gray-700 hover:bg-gray-600 text-yellow-300'
                : 'bg-blue-100 hover:bg-blue-200 text-blue-700')
            }
            title={darkMode ? 'Switch to Light Mode' : 'Switch to Dark Mode'}
            aria-label="Toggle dark mode"
          >
            {darkMode ? (
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
              <path strokeLinecap="round" strokeLinejoin="round" d="M12 3v1.5m0 15V21m8.485-8.485l-1.06 1.06M4.515 4.515l1.06 1.06M21 12h-1.5M4.5 12H3m16.485 4.485l-1.06-1.06M4.515 19.485l1.06-1.06M16.5 12a4.5 4.5 0 11-9 0 4.5 4.5 0 019 0z" />
            </svg>
            ) : (
              <svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" strokeWidth={1.5} stroke="currentColor" className="w-6 h-6">
              <path strokeLinecap="round" strokeLinejoin="round" d="M21.752 15.002A9.718 9.718 0 0112 21.75c-5.385 0-9.75-4.365-9.75-9.75 0-4.136 2.664-7.626 6.398-9.093a.75.75 0 01.908.325.75.75 0 01-.062.954A7.501 7.501 0 0012 19.5c2.485 0 4.675-1.21 6.084-3.07a.75.75 0 01.954-.062.75.75 0 01.325.908z" />
            </svg>

            )}
          </button>
        </header>
        <main
          className={
            `flex-1 overflow-y-auto px-4 py-2 sm:px-1 sm:py-1 space-y-2 transition-colors duration-300 ` +
            (darkMode ? 'bg-gray-900' : 'bg-blue-50')
          }
          style={{ maxWidth: '100vw', overflowX: 'hidden' }}
        >
          {greeting && (
            <div className="flex justify-start">
              <div className={
                (darkMode
                  ? 'bg-gray-800 text-blue-200'
                  : 'bg-blue-100 text-blue-900') +
                ' px-4 py-2 rounded-lg shadow-sm max-w-[80%]'
              }>
                <span dangerouslySetInnerHTML={{ __html: marked.parse(greeting || "") }} />
              </div>
            </div>
          )}
          {chatMessages.map((msg, idx) => (
            <div key={idx} className={
              msg.type === 'user'
                ? 'flex justify-end'
                : msg.type === 'bot'
                  ? 'flex justify-start'
                  : 'flex justify-center'
            }>
              <div className={
                msg.type === 'user'
                  ? (darkMode
                      ? 'bg-blue-700 text-white'
                      : 'bg-blue-600 text-white') + ' px-4 py-2 rounded-lg shadow max-w-[80%]'
                  : msg.type === 'bot'
                    ? (darkMode
                        ? 'bg-gray-800 text-blue-100'
                        : 'bg-gray-100 text-gray-900') + ' px-4 py-2 rounded-lg shadow max-w-[80%]'
                    : 'bg-red-100 text-red-700 px-4 py-2 rounded-lg shadow max-w-[80%]'
              }>
                {msg.type === 'bot' || msg.type === 'error' ? (
                  <span dangerouslySetInnerHTML={{ __html: marked.parse(msg.content || "") }} />
                ) : (
                  <span>{msg.content}</span>
                )}
              </div>
            </div>
          ))}
          {isLoading && (
            <div className="flex justify-start">
              <div className={
                (darkMode
                  ? 'bg-blue-900 text-blue-200'
                  : 'bg-blue-200 text-blue-800') +
                ' px-4 py-2 rounded-lg shadow animate-pulse max-w-[80%]'
              }>
                Loading...
              </div>
            </div>
          )}
          <div ref={chatEndRef} />
        </main>
        <form
          className={
            'border-t px-4 py-2 flex gap-2 transition-colors duration-300 ' +
            'sm:px-2 sm:py-2 sm:gap-1 ' +
            (darkMode ? 'bg-gray-900 border-gray-800' : 'bg-white border-blue-100')
          }
          style={{ maxWidth: '100vw' }}
          onSubmit={e => { e.preventDefault(); sendMessage(); }}
        >
          <textarea
            className={
              'flex-1 resize-none rounded-lg px-3 py-2 focus:outline-none text-gray-900 transition-colors duration-300 text-base sm:text-sm ' +
              (darkMode
                ? 'border border-gray-700 bg-gray-800 text-white focus:border-blue-400'
                : 'border border-blue-200 bg-blue-50 focus:border-blue-400')
            }
            rows={1}
            placeholder="Type your message..."
            value={userInput}
            onChange={e => setUserInput(e.target.value)}
            onKeyDown={handleKeyDown}
            disabled={isLoading}
            style={{ minHeight: '2.5rem', maxHeight: '6rem', width: '100%' }}
          />
          <button
            type="submit"
            className={
              'font-semibold px-6 py-2 rounded-lg transition-colors disabled:opacity-50 text-base sm:text-sm ' +
              (darkMode
                ? 'bg-blue-700 hover:bg-blue-800 text-white'
                : 'bg-blue-600 hover:bg-blue-700 text-white')
            }
            disabled={isLoading || !userInput.trim()}
            style={{ minWidth: '4rem' }}
          >
            Send
          </button>
        </form>
      </div>
    </div>
  );
} 