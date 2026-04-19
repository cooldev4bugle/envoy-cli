import pytest
from envoy.template import render, find_placeholders, apply_template


DEF_TMPL = {
    "DB_HOST": "{{HOST}}",
    "DB_PORT": "5432",
    "DB_URL": "postgres://{{HOST}}:5432/{{DB}}",
}


def test_render_basic():
    result = render(DEF_TMPL, {"HOST": "localhost", "DB": "mydb"})
    assert result["DB_HOST"] == "localhost"
    assert result["DB_PORT"] == "5432"
    assert result["DB_URL"] == "postgres://localhost:5432/mydb"


def test_render_missing_variable_raises():
    with pytest.raises(KeyError, match="HOST"):
        render(DEF_TMPL, {"DB": "mydb"})


def test_render_no_placeholders():
    plain = {"KEY": "value", "OTHER": "stuff"}
    assert render(plain, {}) == plain


def test_find_placeholders_returns_sorted_unique():
    names = find_placeholders(DEF_TMPL)
    assert names == ["DB", "HOST"]


def test_find_placeholders_empty():
    assert find_placeholders({"A": "no placeholders"}) == []


def test_apply_template_self_context():
    tmpl = {
        "HOST": "localhost",
        "URL": "http://{{HOST}}/path",
    }
    result = apply_template(tmpl)
    assert result["URL"] == "http://localhost/path"


def test_apply_template_with_overrides():
    tmpl = {
        "HOST": "localhost",
        "URL": "http://{{HOST}}/path",
    }
    result = apply_template(tmpl, {"HOST": "prod.example.com"})
    assert result["URL"] == "http://prod.example.com/path"


def test_apply_template_missing_raises():
    tmpl = {"URL": "http://{{HOST}}/path"}
    with pytest.raises(KeyError):
        apply_template(tmpl)
