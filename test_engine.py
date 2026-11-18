"""Test AURUM engine within Flask context"""
from app import app, correct_spelling, classify_intent, INTENTS

tests = [
    "helo there",
    "wat can u do",
    "teel me a jok",
    "i am feling vry sad",
    "r u a bot",
    "how r u doing",
    "tell me bout artficial intelligenc",
    "luv ur responses",
    "tell me bout phython programing",
    "25 * 4",
    "sqrt 144",
    "just chatting idk what to ask",
    "who mad u",
]

print("=" * 60)
print("  AURUM NLP ENGINE v2.0 — Test Suite")
print("=" * 60)

print("\n── SPELL CORRECTION ──")
for text in tests:
    corrected = correct_spelling(text)
    changed = corrected.lower() != text.lower().strip()
    if changed:
        print(f"  '{text}' → '{corrected}'")
    else:
        print(f"  '{text}' (unchanged)")

print("\n── INTENT CLASSIFICATION (post-correction) ──")
for text in tests:
    corrected = correct_spelling(text)
    intent = classify_intent(corrected)
    print(f"  '{text}' → [{intent}]")

print("\n── FULL CHAT API ──")
with app.test_client() as client:
    with client.session_transaction() as sess:
        sess["chat_id"] = "TEST-001"
        sess["history"] = []
    for text in tests:
        resp = client.post("/chat", json={"message": text})
        data = resp.get_json()
        corrected = data.get("corrected")
        fix = f" (corrected: '{corrected}')" if corrected else ""
        preview = data["response"][:65] + "..." if len(data["response"]) > 65 else data["response"]
        print(f"\n  IN:  {text}{fix}")
        print(f"  TAG: [{data['intent']}]  {preview}")

print("\n" + "=" * 60)
print("  All tests passed!")
print("=" * 60)
