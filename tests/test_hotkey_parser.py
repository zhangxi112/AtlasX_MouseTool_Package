from services.tray_hotkey_manager import MOD_ALT, MOD_CONTROL, describe_hotkey_sequence, parse_hotkey_sequence


def test_parse_hotkey_sequence_for_ctrl_alt_letter() -> None:
    modifiers, key_code = parse_hotkey_sequence("Ctrl+Alt+M")
    assert modifiers == MOD_CONTROL | MOD_ALT
    assert key_code == ord("M")


def test_describe_hotkey_sequence_prefers_single_function_key() -> None:
    assert "单键触发" in describe_hotkey_sequence("F8")
