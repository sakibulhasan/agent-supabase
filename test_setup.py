import os
from dotenv import load_dotenv
import google.generativeai as genai
from supabase import create_client

# Load environment variables from .env file
load_dotenv()

print("✅ Libraries imported successfully!")

# Check if keys are being read (we won't print the actual keys for security)
if os.getenv("GEMINI_API_KEY"):
    print("✅ GEMINI_API_KEY found.")
else:
    print("❌ Error: GEMINI_API_KEY not found in .env")

if os.getenv("SUPABASE_URL") and os.getenv("SUPABASE_ANON_KEY"):
    print("✅ Supabase credentials found.")
else:
    print("❌ Error: Supabase credentials not found in .env")

print("\nEnvironment setup complete! You are ready for Section 4.")