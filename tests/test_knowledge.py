from plant_copilot.knowledge import KnowledgeBase


def build_kb(tmp_path, embedding):
    return KnowledgeBase(str(tmp_path / "db"), "test_collection", "test-deterministic-v1", embedding)


def test_repeat_ingestion_is_idempotent_and_change_replaces(tmp_path, embedding):
    kb = build_kb(tmp_path, embedding)
    first = kb.ingest("pump.txt", b"Pump Alpha seal pressure is four bar. " * 12, 120, 20)
    count = kb.collection.count()
    repeated = kb.ingest("pump.txt", b"Pump Alpha seal pressure is four bar. " * 12, 120, 20)
    assert first["status"] == "indexed"
    assert repeated["status"] == "unchanged"
    assert kb.collection.count() == count
    changed = kb.ingest("pump.txt", b"Pump Alpha seal pressure is six bar after retrofit.", 120, 20)
    assert changed["status"] == "replaced"
    documents = kb.collection.get(where={"source": "pump.txt"}, include=["documents"])["documents"]
    assert documents == ["Pump Alpha seal pressure is six bar after retrofit."]


def test_retrieval_returns_source_and_rejects_low_relevance(tmp_path, embedding):
    kb = build_kb(tmp_path, embedding)
    kb.ingest("compressor.md", b"Compressor C-12 high vibration alarm threshold is 8 mm/s.", 150, 20)
    hits = kb.search("What is the C-12 vibration alarm threshold?", 3, 0.05)
    assert hits and hits[0].source == "compressor.md"
    assert "8 mm/s" in hits[0].text
    assert kb.search("unrelated cafeteria menu", 3, 0.99) == []

