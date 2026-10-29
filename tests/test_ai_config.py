import asyncio
import os
import sys

# Ensure project root is on sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from server.utils.ai_config import (
    ai_vault,
    mask_api_key,
    sanitize_log_message,
    validate_api_key_format,
    set_request_ai_context,
    reset_request_ai_context
)

async def test_ai_config_security():
    print("=" * 60)
    print("TESTING AI CONFIGURATION & KEY SECURITY VAULT")
    print("=" * 60)

    # 1. Test Key Masking
    raw_gemini_key = "AIzaSyD9876543210abcdefGHIJKL9x2Q"
    masked = mask_api_key(raw_gemini_key)
    print(f"[Step 1] Masked Key: {masked}")
    assert raw_gemini_key not in masked, "Raw key must never appear in masked output"
    assert masked.startswith("AIza") and masked.endswith("9x2Q"), "Should keep only 4-char prefix/suffix"

    # 2. Test Log Sanitization
    dirty_log = f"Error calling https://generativelanguage.googleapis.com/v1beta?key={raw_gemini_key} with Bearer gsk_1234567890abcdef12345"
    clean_log = sanitize_log_message(dirty_log)
    print(f"[Step 2] Sanitized Log: {clean_log}")
    assert raw_gemini_key not in clean_log, "Gemini key must be scrubbed from logs"
    assert "gsk_1234567890abcdef12345" not in clean_log, "Groq key must be scrubbed from logs"

    # 3. Test Key Format Validation
    ok_valid, _ = validate_api_key_format("gemini", raw_gemini_key)
    ok_invalid, _ = validate_api_key_format("gemini", "short_key")
    ok_wrong_prefix, _ = validate_api_key_format("groq", raw_gemini_key)
    assert ok_valid is True
    assert ok_invalid is False
    assert ok_wrong_prefix is False
    print("[Step 3] Key format validation passed.")

    # 4. Test Encrypted Runtime Vault
    status = ai_vault.set_user_key(provider="gemini", api_key=raw_gemini_key, model="gemini-2.0-flash")
    assert status["has_active_key"] is True
    assert status["active_provider"] == "gemini"
    assert status["masked_active_key"] == masked
    assert raw_gemini_key not in str(status), "Public status must never expose raw key"

    stored_cipher = ai_vault._store["gemini"]["ciphertext"]
    assert raw_gemini_key not in stored_cipher, "Ciphertext must not contain plaintext key"
    decrypted = ai_vault.get_decrypted_key("gemini")
    assert decrypted == raw_gemini_key, "Vault should accurately decrypt key in memory"
    print("[Step 4] Encrypted runtime vault encryption & decryption verified.")

    # 5. Test Per-Request Context Isolation
    raw_groq_key = "gsk_abcdefghijklmnop1234567890ABCD"
    tokens = set_request_ai_context("groq", raw_groq_key, "llama-3.3-70b-versatile")
    try:
        prov, key, mod, src = ai_vault.resolve_active_credentials()
        assert prov == "groq"
        assert key == raw_groq_key
        assert mod == "llama-3.3-70b-versatile"
        assert src == "user_request"
    finally:
        reset_request_ai_context(tokens)

    # After context reset, should revert to vault key
    prov_after, _, _, src_after = ai_vault.resolve_active_credentials()
    assert prov_after == "gemini"
    assert src_after == "user_vault"
    print("[Step 5] Per-request ContextVar isolation verified.")

    # 6. Test Key Revocation
    cleared_status = ai_vault.clear_keys()
    assert len(ai_vault._store) == 0, "Vault store should be empty after revocation"
    print("[Step 6] Key revocation verified.")

    print("\nALL AI CONFIG & SECURITY TESTS PASSED!")

if __name__ == "__main__":
    asyncio.run(test_ai_config_security())
