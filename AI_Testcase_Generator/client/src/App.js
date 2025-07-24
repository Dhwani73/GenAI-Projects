// import React, { useState } from "react";              //Imports React (needed for JSX and component functions), useState is a React hook to manage internal component state
// import "./App.css";

// function App() {                                            
//   const [requirement, setRequirement] = useState("");       //requirement – stores what user types in the textarea. 
//   const [testCases, setTestCases] = useState("");           //testCases – stores what AI returns. 
//   const [loading, setLoading] = useState(false);            //loading – tracks whether the API is running so we can show “Generating…”
//   const [showPanel, setShowPanel] = useState(false);


//   const handleGenerate = async () => {               //Starts the function when user clicks “Generate” and throws error if empty
//     if (!requirement.trim()) return alert("Please enter a requirement.");

//     setLoading(true);         //Sets loading to true → disables the button and shows spinner text
//     try {
//       const response = await fetch("http://localhost:5000/api/generate", {
//         method: "POST",
//         headers: {
//           "Content-Type": "application/json",
//         },
//         body: JSON.stringify({ requirement }),
//       });

//       const data = await response.json();
//       setTestCases(data.testCases || "No test cases generated.");
//     } catch (error) {
//       console.error("Error:", error);
//       setTestCases("Error generating test cases.");
//     } finally {
//       setLoading(false);
//     }
//   };

import React, { useState } from "react";
import 'bootstrap/dist/css/bootstrap.min.css';
import "./App.css";

function App() {
  const [requirement, setRequirement] = useState("");
  const [loading, setLoading] = useState(false);

  const handleGenerate = async () => {
    if (!requirement.trim()) return alert("Please enter a requirement.");
    setLoading(true);

    try {
      const response = await fetch("http://localhost:5000/api/generate", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({ requirement }),
      });

      const blob = await response.blob();
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = "testcases.xlsx";
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error("Error:", error);
      alert("Something went wrong while generating test cases.");
    } finally {
      setLoading(false);
    }
  };

  const handleClear = () => {
    setRequirement("");
  };

  return (
    <div className="container py-5">
      <h1 className="text-center mb-4">AI Test Case Generator</h1>
      <div className="row justify-content-center">
        <div className="col-md-8">
          <textarea
            className="form-control mb-3"
            placeholder="Enter your requirement here..."
            value={requirement}
            rows={6}
            onChange={(e) => setRequirement(e.target.value)}
          />
          <div className="d-flex justify-content-between">
            <button
              className="btn btn-primary"
              onClick={handleGenerate}
              disabled={loading}
            >
              {loading ? "Generating..." : "✨ Generate"}
            </button>
            <button
              className="btn btn-secondary"
              onClick={handleClear}
              disabled={loading}
            >
              🧹 Clear
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}

export default App;
