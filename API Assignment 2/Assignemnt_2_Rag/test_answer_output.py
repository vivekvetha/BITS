import importlib
import sys
import types
import unittest

if "pypdf" not in sys.modules:
    pypdf_stub = types.ModuleType("pypdf")
    pypdf_stub.PdfReader = object
    sys.modules["pypdf"] = pypdf_stub
if "openai" not in sys.modules:
    openai_stub = types.ModuleType("openai")

    class _DummyOpenAI:
        def __init__(self, *args, **kwargs):
            pass

    openai_stub.OpenAI = _DummyOpenAI
    sys.modules["openai"] = openai_stub
if "chromadb" not in sys.modules:
    chromadb_stub = types.ModuleType("chromadb")

    class _DummyPersistentClient:
        def __init__(self, *args, **kwargs):
            pass

    chromadb_stub.PersistentClient = _DummyPersistentClient
    sys.modules["chromadb"] = chromadb_stub

rag_module = importlib.import_module("rag")
RAGSystem = rag_module.RAGSystem


class TestAnswerOutputNormalization(unittest.TestCase):
    def setUp(self):
        self.rag = RAGSystem(api_key="test-key")
        self.fallback = (
            "This information is not available in the provided documents."
        )

    def test_remove_fallback_when_grounded_answer_exists(self):
        mixed = (
            "The fiscal deficit is estimated at 4.3 percent of GDP. "
            + self.fallback
        )
        normalized = self.rag.normalize_answer_output(mixed)
        self.assertEqual(
            normalized, "The fiscal deficit is estimated at 4.3 percent of GDP."
        )

    def test_keep_fallback_when_it_is_the_only_content(self):
        normalized = self.rag.normalize_answer_output(self.fallback)
        self.assertEqual(normalized, self.fallback)


if __name__ == "__main__":
    unittest.main()
