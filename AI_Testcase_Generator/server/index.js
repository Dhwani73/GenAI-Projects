// server/index.js

const express = require("express");                 //express: The web server library used to define routes (like /api/generate)
const cors = require("cors");                       //Cors allows frontend-backend interactions
const bodyParser = require("body-parser");          //Middleware to read JSON bodies from POST requests (e.g., the user’s input requirement)
require("dotenv").config();                         //used to read our env file

const app = express();                              //Creates the main Express app instance
const PORT = process.env.PORT || 5000;              //Used to read port saved in env file (if any) or sets to default

// --- Middleware ---
app.use(cors());                                    // allow cross-origin requests     
app.use(bodyParser.json());                         // parse JSON bodies (required for POST requests)

// --- Routes ---
const generateRoute = require("./routes/generate");     
app.use("/api/generate", generateRoute);

// --- Start Server ---
app.listen(PORT, () => {
  console.log(`Server is running on port ${PORT}`);
});
 
