import json

from src.file_io import FileIO


def test_load_from_json_supports_block_comments(tmp_path):
    sample = tmp_path / "case_with_comments.json"
    sample.write_text(
        """/* case data comment */
[
  {"date":"2026-04-20","amount":45.0,"category":"Food","description":"CYM Mixian"}
]
""",
        encoding="utf-8",
    )

    data = FileIO.load_from_json(str(sample), dict)
    assert len(data) == 1
    assert data[0]["category"] == "Dining"


def test_save_and_load_roundtrip(tmp_path):
    sample = tmp_path / "plain.json"
    payload = [{"date": "2026-04-20", "amount": 10.0, "category": "Dining", "description": "x"}]

    ok = FileIO.save_to_json(payload, str(sample))
    assert ok is True

    raw = json.loads(sample.read_text(encoding="utf-8"))
    assert len(raw) == 1
