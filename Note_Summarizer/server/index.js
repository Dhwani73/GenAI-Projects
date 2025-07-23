import 'dotenv/config'; //Without this line, your API key and base URL wouldn't be read from the .env file
console.log("KEY:", process.env.OPENROUTER_API_KEY);
console.log("BASE URL:", process.env.OPENROUTER_BASE_URL);
import express from 'express'; //Imports the Express.js web framework. Used to build your backend API routes (/summarize, etc.).It helps create a server and handle HTTP requests.
import cors from 'cors'; //Cross-Origin Resource Sharing Allows your frontend (React) to talk to your backend (Node/Express) even if they run on different ports (like 3000 and 5000). Without this, browsers would block requests from frontend to backend due to security rules.
import bodyParser from 'body-parser'; // Middleware that allows you to parse JSON sent in the body of HTTP requests. Without this, req.body would be undefined.
import OpenAI from 'openai';  //This is the official OpenAI SDK v4, which you're using to call the OpenRouter AP

const app = express(); //Initializing Express app
app.use(cors()); // Enables CORS for all routes so the frontend can safely communicate with the backend.
app.use(bodyParser.json()); //Ensures that any JSON data sent in the request body (like a note to summarize) is properly read.


//This creates an API client: Uses your OpenRouter API key, Sets OpenRouter’s API base URL, Makes requests just like with OpenAI.
const openai = new OpenAI({
  apiKey: process.env.OPENROUTER_API_KEY,
  baseURL: process.env.OPENROUTER_BASE_URL,
});

app.post('/summarize', async (req, res) => {  //Defines a POST endpoint /summarize. It expects a JSON body like { text: "your note here" }.
  const { text } = req.body;
  try { //Makes a call to OpenRouter: Uses Chat API, Asks it to "Summarize this" and passes your note
    const response = await openai.chat.completions.create({
      model: "mistralai/mistral-7b-instruct",
      messages: [{ role: 'user', content: `Summarize the following text concisely and try to keep it short:\n\n${text}` }],
    });
    res.json({ summary: response.choices[0].message.content.trim() }); //Extracts the summarized result from the API response and sends it back to your frontend.
  } catch (err) {   //Handles errors gracefully and returns a 500 status if something goes wrong.
    console.error(err);
    res.status(500).json({ error: 'AI request failed' });
  }
});

// POST route to handle translation requests from the frontend
app.post('/translate', async (req, res) => {
  // Extract the text to translate and the target language from the request body
  const { text, targetLang } = req.body;
  console.log("Received for translation:", { text, targetLang }); // Logs input for debugging

  try {
    // Call OpenRouter's mistral-7b model to translate the text
    const response = await openai.chat.completions.create({
      model: "mistralai/mistral-7b-instruct", // Using Mistral model via OpenRouter
      messages: [
        { role: 'system', content: `Translate the following text to ${targetLang}` }, // Instruction to model
        { role: 'user', content: text } // Text that needs to be translated
      ]
    });

    // Log the translation result for debugging
    console.log("Translation response:", response.choices[0].message.content);

    // Send the translated text back to the frontend
    res.json({ translation: response.choices[0].message.content.trim() });
  } catch (err) {
    // Log and return an error if translation fails
    console.error("❌ Translation Error:", err);
    res.status(500).json({ error: 'Translation failed' });
  }
});


app.listen(5000, () => console.log('✅ Server running at http://localhost:5000'));  //Starts the server on port 5000, and logs a message when it’s ready.

