// // server/routes/generate.js

// const express = require("express");               //Sets up an Express router to define your custom API route /api/generate
// const router = express.Router();

// const axios = require("axios");                   //Imports axios for making HTTP requests
// require("dotenv").config();

// const OPENROUTER_API_KEY = process.env.OPENROUTER_API_KEY;              //Reads your secret OpenRouter key from the .env file
// const MODEL = "mistralai/mistral-7b-instruct"; // ✅ Free model         //Sets the model that will be used

// router.post("/", async (req, res) => {                  //Defines the POST route /api/generate
//   const { requirement } = req.body;                     //Use to get the user-input

//   if (!requirement) {                                   // If no input is given, return a 400 Bad Request with an error
//     return res.status(400).json({ error: "Requirement is required" });
//   }

//   try {
//     const prompt = `
// You are a software testing expert. Based on the requirement below, generate a **concise set** of meaningful test cases.
// Each test case should include:
// - Test ID
// - Scenario
// - Input
// - Expected Output
// - Type (Positive, Negative, Edge)

// Requirement:
// ${requirement}
// `;

//     const response = await axios.post(                          //Calls the OpenRouter API endpoint for chat models and Sends the prompt as a message to the selected model
//       "https://openrouter.ai/api/v1/chat/completions",
//       {
//         model: MODEL,
//         messages: [
//           { role: "user", content: prompt }
//         ],
//       },
//       {
//         headers: {                                              //Adds required headers: Authorization: uses your API key, Referer: your app URL (can be localhost), X-Title: a label for tracking on OpenRouter dashboard
//           Authorization: `Bearer ${OPENROUTER_API_KEY}`,
//           "Content-Type": "application/json",
//           "HTTP-Referer": "http://localhost:3000", // or your actual domain
//           "X-Title": "Testcase Generator",
//         },
//       }
//     );

//     console.log("Received input:", requirement);

//     const output = response.data.choices[0].message.content;

// // Split the full response into chunks per test case
// const rawCases = output.trim().split(/\n\s*\n/);// double line break = new test case

// const testCases = rawCases.map((block, index) => {
//   const lines = block.split("\n");
//   const details = {};
//   let title = ``; // fallback title

//   lines.forEach((line) => {
//   const [key, ...rest] = line.split(":");
//   const value = rest.join(":").trim();

//   if (!key.trim() || !value) return; // ❌ skip empty keys or values

//   if (key.toLowerCase().includes("scenario")) {
//     title = value;
//   } else {
//     details[key.trim()] = value;
//   }
//   });

  
//     if (!title) {
//     title = `Test Case ${index + 1}`; // fallback ONLY if no scenario found
//     }

//     return { title, details };
//   });

//   res.json({ testCases });
//   console.log("Structured test cases:", JSON.stringify(testCases, null, 2));
//   } catch (error) {                                                 //Handles error
//     console.error("OpenRouter error:", error.response?.data || error.message);
//     res.status(500).json({ error: "Something went wrong while generating test cases." });
//   }
// });

// module.exports = router; //Exports the router so it can be used in index.js

// server/routes/generate.js

const express = require("express");
const router = express.Router();
const axios = require("axios");
const xlsx = require("xlsx");
const fs = require("fs");
const path = require("path");
require("dotenv").config();

const OPENROUTER_API_KEY = process.env.OPENROUTER_API_KEY;
const MODEL = "mistralai/mistral-7b-instruct";

router.post("/", async (req, res) => {
  const { requirement } = req.body;

  if (!requirement) {
    return res.status(400).json({ error: "Requirement is required" });
  }

  try {
    const prompt = `
You are a software testing expert. Generate 10 test cases from the following requirement:
- Each test case must have:
  - Test ID
  - Scenario
  - Input
  - Expected Output
  - Type (Positive, Negative, Edge)

Requirement: ${requirement}
`;

    const response = await axios.post(
      "https://openrouter.ai/api/v1/chat/completions",
      {
        model: MODEL,
        messages: [{ role: "user", content: prompt }],
      },
      {
        headers: {
          Authorization: `Bearer ${OPENROUTER_API_KEY}`,
          "Content-Type": "application/json",
          "HTTP-Referer": "http://localhost:3000",
          "X-Title": "Testcase Generator",
        },
      }
    );

    const output = response.data.choices[0].message.content;
    const rawCases = output.split(/\n(?=\d+\.?\s*[-]*)/); // Split per test case

    const testCases = rawCases.map((block, index) => {
      const details = {};
      const lines = block.split("\n");
      lines.forEach(line => {
        const [k, ...v] = line.split(":");
        if (!v.length) return;
        const key = k.trim().toLowerCase();
        const value = v.join(":").trim();
        if (key.includes("test id")) details["Test ID"] = value;
        else if (key.includes("scenario")) details["Scenario"] = value;
        else if (key.includes("input")) details["Input"] = value;
        else if (key.includes("expected")) details["Expected Output"] = value;
        else if (key.includes("type")) details["Type"] = value;
      });

      return {
        "Test ID": details["Test ID"] || `TC_${index + 1}`,
        "Scenario": details["Scenario"] || `Test Case ${index + 1}`,
        "Input": details["Input"] || "",
        "Expected Output": details["Expected Output"] || "",
        "Type": details["Type"] || "",
      };
    });

    // Create Excel workbook
    const wb = xlsx.utils.book_new();
    const ws = xlsx.utils.json_to_sheet(testCases);
    xlsx.utils.book_append_sheet(wb, ws, "TestCases");

    const outputPath = path.join(__dirname, "../downloads/testcases.xlsx");
    xlsx.writeFile(wb, outputPath);

    res.download(outputPath, "testcases.xlsx");
  } catch (error) {
    console.error("OpenRouter error:", error?.response?.data || error.message);
    res.status(500).json({ error: "Failed to generate test cases." });
  }
});

module.exports = router;
