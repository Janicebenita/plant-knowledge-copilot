import json
from pathlib import Path

from dotenv import load_dotenv

from plant_copilot.config import Settings
from plant_copilot.knowledge import KnowledgeBase

load_dotenv()
settings = Settings()
kb = KnowledgeBase(settings.chroma_path, settings.collection, settings.embedding_model)
cases = json.loads(Path("evaluation/questions.json").read_text(encoding="utf-8"))
passed = 0
for case in cases:
    hits = kb.search(case["question"], settings.top_k, settings.threshold)
    found = {hit.source for hit in hits}
    expected = set(case["expected_sources"])
    ok = bool(found & expected) if expected else not hits
    passed += int(ok)
    print(f"{case['id']}: {'PASS' if ok else 'FAIL'} expected={sorted(expected)} retrieved={sorted(found)}")
print(f"Retrieval: {passed}/{len(cases)} passed. Answer quality was not evaluated by this script.")

