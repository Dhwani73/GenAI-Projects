// import 'dotenv/config';
// import OpenAI from 'openai';

// const openai = new OpenAI({
//   apiKey: process.env.OPENROUTER_API_KEY,
//   baseURL: process.env.OPENROUTER_BASE_URL,
// });

// async function testConnection() {
//   try {
//     const response = await openai.chat.completions.create({
//       model: "mistralai/mistral-7b-instruct",
//       messages: [
//         {
//           role: "user",
//           content: "Hi! Can you confirm you're working?",
//         },
//       ],
//     });

//     console.log("✅ AI responded:");
//     console.log(response.choices[0].message.content.trim());
//   } catch (err) {
//     console.error("❌ API request failed:", err);
//   }
// }

// testConnection();
