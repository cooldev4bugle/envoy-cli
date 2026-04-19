"""Template support: render .env files with variable substitution."""

import re
from typing import Optional

_PLACEHOLDER = re.compile(r"\{\{\s*(\w+)\s*\}\}")


def render(template: dict, context: dict) -> dict:
    """Substitute {{KEY}} placeholders in values using context dict."""
    result = {}
    for key, value in template.items():
        def replacer(m):
            name = m.group(1)
            if name not in context:
                raise KeyError(f"Missing template variable: {name}")
            return context[name]
        result[key] = _PLACEHOLDER.sub(replacer, value)
    return result


def find_placeholders(template: dict) -> list[str]:
    """Return sorted list of unique placeholder names in a template dict."""
    found = set()
    for value in template.values():
        for m in _PLACEHOLDER.finditer(value):
            found.add(m.group(1))
    return sorted(found)


def apply_template(template: dict, overrides: Optional[dict] = None) -> dict:
    """Render template using its own values as context, plus optional overrides."""
    context = {k: v for k, v in template.items() if not _PLACEHOLDER.search(v)}
    if overrides:
        context.update(overrides)
    return render(template, context)
