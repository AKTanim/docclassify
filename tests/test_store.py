import pytest

from docclassify.errors import DocumentNotFound, DocumentTooLarge
from docclassify.store import LocalDocumentStore


def test_url_path_picks_the_file(tmp_path):
    (tmp_path / "abc.pdf").write_bytes(b"%PDF-1.4 test")
    store = LocalDocumentStore(tmp_path, max_bytes=1000)
    url = "https://docstore.example.com/f/abc.pdf?exp=1&sig=x"
    assert store.fetch(url) == b"%PDF-1.4 test"


def test_missing_file_is_not_found(tmp_path):
    store = LocalDocumentStore(tmp_path, max_bytes=1000)
    with pytest.raises(DocumentNotFound):
        store.fetch("https://docstore.example.com/f/missing.pdf")


def test_url_without_file_name_is_not_found(tmp_path):
    store = LocalDocumentStore(tmp_path, max_bytes=1000)
    with pytest.raises(DocumentNotFound):
        store.fetch("https://docstore.example.com/")


def test_path_tricks_stay_inside_the_folder(tmp_path):
    folder = tmp_path / "store"
    folder.mkdir()
    (tmp_path / "secret.txt").write_text("do not serve")
    store = LocalDocumentStore(folder, max_bytes=1000)
    with pytest.raises(DocumentNotFound):
        store.fetch("https://docstore.example.com/f/../secret.txt")


def test_backslash_tricks_are_refused(tmp_path):
    folder = tmp_path / "store"
    folder.mkdir()
    store = LocalDocumentStore(folder, max_bytes=1000)
    with pytest.raises(DocumentNotFound):
        store.fetch("https://docstore.example.com/f/..\\secret.txt")


def test_large_file_is_refused(tmp_path):
    (tmp_path / "big.pdf").write_bytes(b"x" * 1001)
    store = LocalDocumentStore(tmp_path, max_bytes=1000)
    with pytest.raises(DocumentTooLarge):
        store.fetch("https://docstore.example.com/f/big.pdf")
