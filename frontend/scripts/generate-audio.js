// scripts/generate-audio.js
// Run from frontend: node scripts/generate-audio.js
// Load .env from frontend root
import fs from "fs";
import path from "path";
import { fileURLToPath } from "url";
import dotenv from "dotenv";
import { ElevenLabsClient } from "@elevenlabs/elevenlabs-js";

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const envPath = path.resolve(__dirname, "..", ".env");
dotenv.config({ path: envPath });

const API_KEY = process.env.ELEVENLABS_API_KEY;
const VOICE_ID = "21m00Tcm4TlvDq8ikWAM"; // Rachel
const OUTPUT_DIR = path.resolve(__dirname, "..", "public", "audio");

// Premade messages for app; generated on each build
const PHRASES = {
  account1: "Account 1",
  cards: "Cards",
  physical_cards: "Physical cards",
  virtual_cards: "Virtual cards",
};

async function streamToBuffer(stream) {
  const chunks = [];
  for await (const chunk of stream) {
    chunks.push(chunk);
  }
  return Buffer.concat(chunks);
}

async function generateAudio(key, text) {
  const filePath = path.join(OUTPUT_DIR, `${key}.mp3`);

  if (fs.existsSync(filePath)) {
    console.log(`Skipping ${key} (exists)`);
    return;
  }

  if (!API_KEY) {
    console.warn("Missing ELEVENLABS_API_KEY in .env; skipping audio generation.");
    return;
  }

  console.log(`Generating: "${text}"...`);

  try {
    const elevenlabs = new ElevenLabsClient({ apiKey: API_KEY });
    const response = await elevenlabs.textToSpeech.convert(VOICE_ID, {
      text,
      model_id: "eleven_monolingual_v1",
      voice_settings: { stability: 0.5, similarity_boost: 0.75 },
    });

    const buffer = await streamToBuffer(response.data);
    fs.writeFileSync(filePath, buffer);
    console.log(`Wrote ${key}.mp3`);
  } catch (err) {
    console.warn(`Skipping ${key} (API error):`, err.message);
    // Build continues; audio will be missing until ELEVENLABS_API_KEY is valid
  }
}

(async () => {
  if (!fs.existsSync(OUTPUT_DIR)) {
    fs.mkdirSync(OUTPUT_DIR, { recursive: true });
  }

  for (const [key, text] of Object.entries(PHRASES)) {
    await generateAudio(key, text);
  }
})();
