import json
import logging
import os
from pathlib import Path
from tools.passive_extraction_workflow_latest import PassiveExtractionWorkflow


def test_save_category_manifest(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    wf = PassiveExtractionWorkflow.__new__(PassiveExtractionWorkflow)
    wf.log = logging.getLogger("test")
    manifest_path = wf._save_category_manifest(
        "demo", "https://example.com/cat", ["u1", "u2", "u3"]
    )
    data = json.loads(Path(manifest_path).read_text())
    assert data["count"] == 3
    assert len(data["product_urls"]) == 3
