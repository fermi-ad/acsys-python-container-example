import json
import re


def parse_flexible_mapping(text: str) -> dict | None:
    try:
        normalized = to_valid_json(text)
        parsed = json.loads(normalized)
        if isinstance(parsed, dict):
            return parsed
    except json.JSONDecodeError:
        pass

    return None


def quote_unquoted_top_level_keys(text: str) -> str:
    pattern = re.compile(r'([,{]\s*)([A-Za-z_][A-Za-z0-9_\-]*)(\s*:)')

    def replacer(match: re.Match) -> str:
        prefix, key, suffix = match.groups()
        return f'{prefix}"{key}"{suffix}'

    return pattern.sub(replacer, text)


def to_valid_json(text: str) -> str:
    text = quote_unquoted_top_level_keys(text)

    text = re.sub(r'\bNone\b', 'null', text)
    text = re.sub(r'\bTrue\b', 'true', text)
    text = re.sub(r'\bFalse\b', 'false', text)

    text = re.sub(r'"stamp"\s*:\s*([^",}\]][^,}\]]*)', r'"stamp": "\1"', text)

    text = text.replace("'", '"')
    return text
