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
 

//   return (
//   <div className="App">
//     <h1>Test Case Generator</h1>

//     <textarea
//       placeholder="Drop your feature or requirement here..."
//       value={requirement}
//       onChange={(e) => setRequirement(e.target.value)}
//     />

//     <div className="buttons">
//       <button onClick={handleGenerate} disabled={loading}>
//         {loading ? "Generating..." : "✨ Generate"}
//       </button>
//       <button onClick={() => { setRequirement(""); setTestCases(""); }}>
//         🧹 Clear
//       </button>
//     </div>

//     <div className="output">
//       {testCases ? testCases : "⚡ Your test cases will show up here..."}
//     </div>

//     <div className="icon-buttons">
//       {/* We'll add copy/download later here */}
//     </div>
//   </div>
// );
// }

// export default App;

// import React, { useState } from "react";
// import "./App.css";

// function App() {
//   const [requirement, setRequirement] = useState("");
//   const [testCases, setTestCases] = useState([]);
//   const [expandedIndex, setExpandedIndex] = useState(null);
//   const [loading, setLoading] = useState(false);

//   const handleGenerate = async () => {
//     if (!requirement.trim()) return alert("Please enter a requirement.");

//     setLoading(true);
//     setTestCases([]);
//     setExpandedIndex(null);

//     try {
//       const response = await fetch("http://localhost:5000/api/generate", {
//         method: "POST",
//         headers: {
//           "Content-Type": "application/json",
//         },
//         body: JSON.stringify({ requirement }),
//       });

//       const data = await response.json();
//       setTestCases(data.testCases || []);
//     } catch (error) {
//       console.error("Error:", error);
//       setTestCases([
//         { title: "Error", details: { Message: "Failed to generate test cases." } },
//       ]);
//     } finally {
//       setLoading(false);
//     }
//   };

//   const handleClear = () => {
//     setRequirement("");
//     setTestCases([]);
//     setExpandedIndex(null);
//   };

//   const toggleExpand = (index) => {
//     setExpandedIndex(index === expandedIndex ? null : index);
//   };

//   return (
//     <div className="app-container">
//       <div className="input-panel">
//         <h1>AI Test Case Generator</h1>
//         <textarea
//           placeholder="Enter your requirement..."
//           value={requirement}
//           onChange={(e) => setRequirement(e.target.value)}
//         />
//         <div className="buttons">
//           <button onClick={handleGenerate} disabled={loading}>
//             {loading ? "Generating..." : "✨ Generate"}
//           </button>
//           <button onClick={handleClear} disabled={loading}>
//             🧹 Clear
//           </button>
//         </div>
//       </div>

//       <div className="output-panel">
//         {testCases.length > 0 && (
//           <>
//             <h2>Generated Test Cases</h2>
//             <div className="testcase-grid">
//               {testCases.map((test, index) => (
//                 <div className="testcase-card" key={index}>
//                   <div className="testcase-header">
//                     <strong>{test.title}</strong>
//                     <button onClick={() => toggleExpand(index)}>
//                       {expandedIndex === index ? "Hide" : "Expand"}
//                     </button>
//                   </div>
//                   {expandedIndex === index && (
//                     <div className="testcase-details">
//                       {Object.entries(test.details).map(([key, value], i) => (
//                         <p key={i}>
//                           <span className="label">{key}:</span>{" "}
//                           <span className="value">{value}</span>
//                         </p>
//                       ))}
//                     </div>
//                   )}
//                 </div>
//               ))}
//             </div>
//           </>
//         )}
//       </div>
//     </div>
//   );
// }

// export default App;


// import React, { useState } from "react";
// import "./App.css";

// function App() {
//   const [requirement, setRequirement] = useState("");
//   const [loading, setLoading] = useState(false);

//   const handleGenerate = async () => {
//     if (!requirement.trim()) return alert("Please enter a requirement.");
//     setLoading(true);

//     try {
//       const response = await fetch("http://localhost:5000/api/generate", {
//         method: "POST",
//         headers: { "Content-Type": "application/json" },
//         body: JSON.stringify({ requirement }),
//       });

//       const blob = await response.blob();
//       const url = window.URL.createObjectURL(blob);
//       const a = document.createElement("a");
//       a.href = url;
//       a.download = "testcases.xlsx";
//       document.body.appendChild(a);
//       a.click();
//       a.remove();
//     } catch (err) {
//       alert("Error downloading file");
//     } finally {
//       setLoading(false);
//     }
//   };

//   return (
//     <div className="main-container">
//       <h1 className="heading">Test Case Generator</h1>
//       <textarea
//         className="input-box"
//         rows={8}
//         placeholder="Enter requirement or scenario here..."
//         value={requirement}
//         onChange={(e) => setRequirement(e.target.value)}
//       />
//       <div className="button-group">
//         <button onClick={handleGenerate} disabled={loading}>
//           {loading ? "Generating..." : "✨ Generate Excel"}
//         </button>
//         <button onClick={() => setRequirement("")}>🧹 Clear</button>
//       </div>
//     </div>
//   );
// }

// export default App;

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
