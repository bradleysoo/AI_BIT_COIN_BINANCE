import os
from dotenv import load_dotenv
load_dotenv ()

print(os.getenv("BINACE_ACCESS_API_KEY"))
print(os.getenv("BINACE_SECRET_API_KEY"))
print(os.getenv("GEMINI_API_KEY"))