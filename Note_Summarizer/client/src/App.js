// Import React and hooks for state management
import React, { useState } from 'react';
// Import icons for copy/download features
import { FiCopy, FiDownload } from 'react-icons/fi';
// Import styling
import './App.css';

function App() {
  // State to hold the user input, generated summary, loading state, and selected translation language
  const [text, setText] = useState('');
  const [summary, setSummary] = useState('');
  const [loading, setLoading] = useState(false);
  const [selectedLanguage, setSelectedLanguage] = useState('English');

  // Handles the Summarization API call
  const handleSummarize = async () => {
    if (!text.trim()) return; // Avoid sending empty input

    setLoading(true); // Show loading state while waiting
    setSummary(''); // Clear previous result

    try {
      const response = await fetch('http://localhost:5000/summarize', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text }), // Send user's notes to backend
      });

      const data = await response.json();
      if (data.summary) {
        setSummary(data.summary); // Display summarized result
      } else {
        setSummary('Error: Unable to summarize.'); // Fallback on error
      }
    } catch (err) {
      console.error(err);
      setSummary('Error: An error occurred while summarizing.');
    } finally {
      setLoading(false); // Stop loading indicator
    }
  };

  // Copies the summary to clipboard
  const handleCopy = () => {
    navigator.clipboard.writeText(summary);
    alert('Summary copied to clipboard!');
  };

  // Downloads the summary as a text file
  const handleDownload = () => {
    const blob = new Blob([summary], { type: 'text/plain' }); // Convert summary to a text Blob
    const url = URL.createObjectURL(blob); // Create download link
    const link = document.createElement('a');
    link.download = 'summary.txt';
    link.href = url;
    link.click(); // Trigger download
    URL.revokeObjectURL(url); // Clean up
  };

  // Handles translation using backend API
  const handleTranslate = async (language) => {
    setSelectedLanguage(language);

    if (!summary || language === 'English') return; // No translation if summary is empty or already English

    try {
      const response = await fetch('http://localhost:5000/translate', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          text: summary,       // Send current summary
          targetLang: language // Target translation language
        }),
      });

      const data = await response.json();
      if (data.translation) {
        setSummary(data.translation); // Update summary with translation
      } else {
        setSummary('Error: Unable to translate.');
      }
    } catch (err) {
      console.error(err);
      setSummary('Error: An error occurred during translation.');
    }
  };

  // Component JSX
  return (
    <div className="app">
      <h1>AI Notes Summarizer</h1>

      <div className="main">
        {/* Input section */}
        <div className="input-area">
          <textarea
            placeholder="Paste your notes here..."
            value={text}
            onChange={(e) => setText(e.target.value)}
          />
          <button onClick={handleSummarize} disabled={!text || loading}>
            {loading ? 'Summarizing...' : 'Summarize'}
          </button>
        </div>

        {/* Output section */}
        <div className="output-area">
          <div className="summary-header">
            <h3>Summary:</h3>

            <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
              {/* Language dropdown */}
              <select
                value={selectedLanguage}
                onChange={(e) => handleTranslate(e.target.value)}
                className="language-select"
              >
                <option value="English">English</option>
                <option value="Hindi">Hindi</option>
                <option value="Spanish">Spanish</option>
                <option value="French">French</option>
                <option value="German">German</option>
              </select>

              {/* Copy & Download icons */}
              <div className="icon-bar-inline">
                <div className="tooltip">
                  <FiCopy className="icon" onClick={handleCopy} />
                  <span className="tooltip-text">Copy the summarized text</span>
                </div>
                <div className="tooltip">
                  <FiDownload className="icon" onClick={handleDownload} />
                  <span className="tooltip-text">Download a .txt file</span>
                </div>
              </div>
            </div>
          </div>

          {/* Final summary/translation shown here */}
          <pre>{summary}</pre>
        </div>
      </div>
    </div>
  );
}

export default App;
