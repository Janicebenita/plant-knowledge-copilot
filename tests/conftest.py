import hashlib
import math
import re

import pytest


class DeterministicEmbedding:
    """Small deterministic embedding used only in tests; production uses MiniLM."""

    def __call__(self, input):
        vectors = []
        for text in input:
            vector = [0.0] * 64
            for token in re.findall(r"[a-z0-9]+", text.lower()):
                digest = hashlib.sha256(token.encode()).digest()
                vector[int.from_bytes(digest[:2], "big") % 64] += 1.0
            norm = math.sqrt(sum(v * v for v in vector)) or 1.0
            vectors.append([v / norm for v in vector])
        return vectors

    def name(self):
        return "test-deterministic-v1"


@pytest.fixture
def embedding():
    return DeterministicEmbedding()

