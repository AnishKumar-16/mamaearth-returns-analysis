
# STEP 5 - TEST GEMINI API KEY AND LIST MODELS

import os
from google import genai

# Read API key from VS Code PowerShell
api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    print("ERROR: Gemini API key not found.")
    print("Please set GEMINI_API_KEY in PowerShell.")

else:
    try:
        print("Connecting to Google Gemini API...")

        with genai.Client(api_key=api_key) as client:

            print("\nConnection successful!")
            print("\nAvailable models:\n")

            count = 0

            for model in client.models.list():

                # Show models that support text generation
                actions = model.supported_actions or []

                if "generateContent" in actions and "flash" in model.name.lower():
                    print(model.name)
                    count += 1

            print("\nTotal text-generation models:", count)

    except Exception as error:
        print("\nGemini API error:")
        print(error)
