from services.enhancement_manager import parse_app_theme_rules, serialize_app_theme_rules


def test_parse_app_theme_rules_accepts_comments_and_builtin_ids() -> None:
    rules = parse_app_theme_rules("# comment\npowerpnt.exe = highlight_arrow\ncode.exe = crosshair")
    assert len(rules) == 2
    assert rules[0].process_name == "powerpnt.exe"
    assert rules[0].theme.theme_id == "highlight_arrow"
    assert rules[1].theme.theme_id == "crosshair"


def test_serialize_app_theme_rules_round_trips() -> None:
    text = "powerpnt.exe = highlight_arrow\ncode.exe = crosshair"
    rules = parse_app_theme_rules(text)
    serialized = serialize_app_theme_rules(rules)
    assert serialized == text
