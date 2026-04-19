import pytest
from unittest.mock import patch, MagicMock
from envoy import tag

BASE = "envoy.tag.storage"


@pytest.fixture
def fake_store():
    """Simple in-memory store."""
    db = {}

    def fake_load(project, env):
        key = (project, env)
        if key not in db:
            raise FileNotFoundError
        return dict(db[key])

    def fake_save(project, env, data):
        db[(project, env)] = dict(data)

    def fake_list(project):
        return [e for (p, e) in db if p == project]

    return db, fake_load, fake_save, fake_list


def test_add_tag_new(fake_store):
    db, fl, fs, flist = fake_store
    db[("proj", "dev")] = {"KEY": "val"}
    with patch(f"{BASE}.load", fl), patch(f"{BASE}.save", fs):
        result = tag.add_tag("proj", "dev", "staging")
    assert "staging" in result


def test_add_tag_no_duplicates(fake_store):
    db, fl, fs, flist = fake_store
    db[("proj", "dev")] = {"__tags__": "staging"}
    with patch(f"{BASE}.load", fl), patch(f"{BASE}.save", fs):
        tag.add_tag("proj", "dev", "staging")
        result = tag.get_tags("proj", "dev")
    assert result.count("staging") == 1


def test_remove_tag(fake_store):
    db, fl, fs, flist = fake_store
    db[("proj", "dev")] = {"__tags__": "a,b,c"}
    with patch(f"{BASE}.load", fl), patch(f"{BASE}.save", fs):
        result = tag.remove_tag("proj", "dev", "b")
    assert "b" not in result
    assert "a" in result and "c" in result


def test_get_tags_empty(fake_store):
    db, fl, fs, flist = fake_store
    db[("proj", "dev")] = {"KEY": "val"}
    with patch(f"{BASE}.load", fl):
        result = tag.get_tags("proj", "dev")
    assert result == []


def test_find_by_tag(fake_store):
    db, fl, fs, flist = fake_store
    db[("proj", "dev")] = {"__tags__": "production"}
    db[("proj", "staging")] = {"__tags__": "staging"}
    db[("proj", "prod")] = {"__tags__": "production"}
    with patch(f"{BASE}.load", fl), patch(f"{BASE}.list_environments", flist):
        result = tag.find_by_tag("proj", "production")
    assert set(result) == {"dev", "prod"}
