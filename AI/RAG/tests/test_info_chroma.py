import importlib.util
from pathlib import Path
import unittest


class InfoChromaUsesConcreteVectorDBTest(unittest.TestCase):
    def test_script_imports_chroma_vector_db(self):
        project_root = Path(__file__).resolve().parents[1]
        spec = importlib.util.spec_from_file_location(
            "info_chroma_module",
            project_root / "scripts" / "info_chroma.py",
        )
        module = importlib.util.module_from_spec(spec)
        assert spec is not None and spec.loader is not None
        spec.loader.exec_module(module)
        self.assertTrue(hasattr(module, "ChromaVectorDB"))
        self.assertEqual(module.ChromaVectorDB.__name__, "ChromaVectorDB")


if __name__ == "__main__":
    unittest.main()
