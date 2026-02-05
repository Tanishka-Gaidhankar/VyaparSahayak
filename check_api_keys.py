import os

print("=" * 60)
print("API KEY CONFIGURATION CHECK")
print("=" * 60)

groq_key = os.getenv("GROQ_API_KEY")

print(f"\nGROQ_API_KEY: {'SET' if groq_key else 'NOT SET'}")
if groq_key:
    print(f"  Preview: {groq_key[:15]}...{groq_key[-5:]}")
    print(f"  Length: {len(groq_key)} characters")
else:
    print("  ⚠️  GROQ API key is not set!")

print("\n" + "=" * 60)
print("INSTRUCTIONS:")
print("=" * 60)
print("\nTo set environment variables in Windows:")
print("1. In PowerShell/CMD where you run uvicorn:")
print("   set GROQ_API_KEY=your_actual_key_here")
print("\n2. Then restart the server:")
print("   uvicorn backend.main:app --reload")
print("\n3. The key will only work in that terminal session")
print("\nAlternatively, add GROQ_API_KEY to backend/.env file")
print("=" * 60)
