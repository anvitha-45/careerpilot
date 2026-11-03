import os
import re
import json
import hmac
import time
import base64
import hashlib
import secrets
from contextvars import ContextVar
from typing import Dict, Any, Optional, List, Tuple
import httpx
from server.config import settings

# Supported AI Providers & Current Production Models Catalog
SUPPORTED_PROVIDERS: Dict[str, Dict[str, Any]] = {
    "gemini": {
        "name": "Google Gemini",
        "default_model": "gemini-2.5-flash",
        "models": [
            {"id": "gemini-2.5-flash", "label": "Gemini 2.5 Flash (Recommended)"},
            {"id": "gemini-2.5-pro", "label": "Gemini 2.5 Pro (Advanced Reasoning)"},
            {"id": "gemini-2.0-flash", "label": "Gemini 2.0 Flash (Fast)"}
        ],
        "key_prefix_hint": "AIza... or AQ....",
        "docs_url": "https://aistudio.google.com/app/apikey"
    },
    "groq": {
        "name": "Groq Cloud",
        "default_model": "llama-3.3-70b-versatile",
        "models": [
            {"id": "llama-3.3-70b-versatile", "label": "Llama 3.3 70B Versatile (Recommended)"},
            {"id": "llama-3.1-8b-instant", "label": "Llama 3.1 8B Instant (Ultra-Fast)"},
            {"id": "gemma2-9b-it", "label": "Gemma 2 9B IT"}
        ],
        "key_prefix_hint": "gsk_...",
        "docs_url": "https://console.groq.com/keys"
    },
    "openai": {
        "name": "OpenAI",
        "default_model": "gpt-4o-mini",
        "models": [
            {"id": "gpt-4o-mini", "label": "GPT-4o Mini (Fast & Recommended)"},
            {"id": "gpt-4o", "label": "GPT-4o (Flagship Reasoning)"},
            {"id": "gpt-4.1-mini", "label": "GPT-4.1 Mini"}
        ],
        "key_prefix_hint": "sk-...",
        "docs_url": "https://platform.openai.com/api-keys"
    }
}

# Retired/decommissioned model mappings to automatically upgrade legacy model IDs
LEGACY_MODEL_UPGRADES: Dict[str, str] = {
    "gemini-1.5-flash": "gemini-2.5-flash",
    "gemini-1.5-pro": "gemini-2.5-pro",
    "gemini-pro": "gemini-2.5-flash",
    "llama-3.1-70b-versatile": "llama-3.3-70b-versatile",
    "llama3-70b-8192": "llama-3.3-70b-versatile",
    "llama3-8b-8192": "llama-3.1-8b-instant",
    "mixtral-8x7b-32768": "llama-3.3-70b-versatile",
}

# Per-request async context variables so user keys passed via HTTP headers
# are strictly isolated to the current request and never leaked across sessions.
_req_provider_ctx: ContextVar[Optional[str]] = ContextVar("ai_req_provider", default=None)
_req_api_key_ctx: ContextVar[Optional[str]] = ContextVar("ai_req_api_key", default=None)
_req_model_ctx: ContextVar[Optional[str]] = ContextVar("ai_req_model", default=None)


def normalize_model_for_provider(provider: str, model: Optional[str] = None) -> str:
    """
    Ensures the selected model ID is compatible with the target provider and
    automatically upgrades any retired/decommissioned model IDs.
    """
    prov = (provider or "").lower().strip()
    if prov not in SUPPORTED_PROVIDERS:
        return "deterministic-heuristics"

    default_model = SUPPORTED_PROVIDERS[prov]["default_model"]
    raw_model = (model or "").strip()
    if not raw_model:
        return default_model

    # Upgrade retired model names automatically
    if raw_model in LEGACY_MODEL_UPGRADES:
        raw_model = LEGACY_MODEL_UPGRADES[raw_model]

    # Validate provider compatibility so a Gemini model is never sent to Groq/OpenAI or vice versa
    if prov == "gemini":
        return raw_model if raw_model.startswith("gemini-") else default_model
    if prov == "openai":
        return raw_model if raw_model.startswith(("gpt-", "o1", "o3", "o4")) else default_model
    if prov == "groq":
        if raw_model.startswith(("gemini-", "gpt-", "o1", "o3")):
            return default_model
        return raw_model

    return default_model


def extract_json_from_llm(raw_text: str) -> Any:
    """
    Robustly extract and parse JSON (object or array) from LLM responses,
    handling markdown code fences or leading/trailing prose.
    """
    if not raw_text or not raw_text.strip():
        return None
    text = raw_text.strip()

    # 1. Try fenced ```json ... ``` block first
    fence_match = re.search(r"```(?:json)?\s*([\s\S]*?)```", text, re.IGNORECASE)
    if fence_match:
        candidate = fence_match.group(1).strip()
        try:
            return json.loads(candidate)
        except Exception:
            pass

    # 2. Try direct parse
    try:
        return json.loads(text)
    except Exception:
        pass

    # 3. Try locating the outermost JSON array or object
    for start_char, end_char in [("[", "]"), ("{", "}")]:
        start_idx = text.find(start_char)
        end_idx = text.rfind(end_char)
        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
            snippet = text[start_idx : end_idx + 1]
            try:
                return json.loads(snippet)
            except Exception:
                continue

    return None


def mask_api_key(key: str) -> str:
    """Return a safe masked representation of an API key. Never reveals the raw key."""
    if not key or not key.strip():
        return ""
    clean = key.strip()
    if len(clean) <= 8:
        return "•" * len(clean)
    return f"{clean[:4]}{'•' * 8}{clean[-4:]}"


def sanitize_log_message(message: str) -> str:
    """Scrub any potential API keys or bearer tokens from log/exception strings."""
    if not message:
        return ""
    sanitized = str(message)
    sanitized = re.sub(r"([?&]key=)[^&\s\"']+", r"\1[REDACTED]", sanitized, flags=re.IGNORECASE)
    sanitized = re.sub(r"\b(AIza[0-9A-Za-z\-_]{10,})\b", "AIza[REDACTED]", sanitized)
    sanitized = re.sub(r"\b(AQ\.[0-9A-Za-z\-_.]{10,})\b", "AQ.[REDACTED]", sanitized)
    sanitized = re.sub(r"\b(gsk_[0-9A-Za-z\-_]{10,})\b", "gsk_[REDACTED]", sanitized)
    sanitized = re.sub(r"\b(sk-[0-9A-Za-z\-_]{10,})\b", "sk-[REDACTED]", sanitized)
    sanitized = re.sub(r"(Bearer\s+)[^\s\"']+", r"\1[REDACTED]", sanitized, flags=re.IGNORECASE)
    return sanitized


def infer_provider_from_key(api_key: str) -> str:
    """Automatically detect provider from key prefix if provider is 'auto'."""
    k = (api_key or "").strip()
    if k.startswith(("AIza", "AQ.")):
        return "gemini"
    if k.startswith("gsk_"):
        return "groq"
    if k.startswith("sk-"):
        return "openai"
    return "gemini"


def validate_api_key_format(provider: str, api_key: str) -> Tuple[bool, str]:
    """Validate API key structure without logging or exposing the key."""
    clean = (api_key or "").strip()
    if not clean:
        return False, "API key cannot be empty."
    if len(clean) < 12:
        return False, "API key is too short. Please enter a valid API key."
    if any(c.isspace() for c in clean):
        return False, "API key must not contain spaces or line breaks."

    prov = (provider or "auto").lower()
    if prov == "gemini" and not clean.startswith(("AIza", "AQ.")):
        return False, "Google Gemini API keys typically start with 'AIza' (AI Studio) or 'AQ.' (Vertex AI Express)."
    if prov == "groq" and not clean.startswith("gsk_"):
        return False, "Groq API keys typically start with 'gsk_'."
    if prov == "openai" and not clean.startswith("sk-"):
        return False, "OpenAI API keys typically start with 'sk-'."

    return True, "Valid key format."


class EncryptedKeyVault:
    """
    In-memory authenticated encryption vault for runtime API keys.
    Keys are encrypted with an ephemeral 256-bit secret key + HMAC-SHA256 integrity tag
    and are never written in plaintext to disk or database files.
    """

    def __init__(self):
        seed = (settings.AI_SECRET_SALT or "").encode("utf-8") + secrets.token_bytes(32)
        self._master_key = hashlib.sha256(seed).digest()
        self._store: Dict[str, Dict[str, Any]] = {}
        self._active_provider: str = settings.AI_PROVIDER.lower() if settings.AI_PROVIDER else "auto"
        self._active_model: str = settings.AI_MODEL or ""
        self._temperature: float = settings.AI_TEMPERATURE

    def _keystream(self, nonce: bytes, length: int) -> bytes:
        out = bytearray()
        counter = 0
        while len(out) < length:
            block = hmac.new(
                self._master_key,
                nonce + counter.to_bytes(4, "big"),
                hashlib.sha256
            ).digest()
            out.extend(block)
            counter += 1
        return bytes(out[:length])

    def _encrypt(self, plaintext: str) -> str:
        raw = plaintext.encode("utf-8")
        nonce = secrets.token_bytes(16)
        stream = self._keystream(nonce, len(raw))
        ciphertext = bytes(a ^ b for a, b in zip(raw, stream))
        mac = hmac.new(self._master_key, nonce + ciphertext, hashlib.sha256).digest()
        return base64.urlsafe_b64encode(nonce + mac + ciphertext).decode("ascii")

    def _decrypt(self, token: str) -> str:
        try:
            blob = base64.urlsafe_b64decode(token.encode("ascii"))
            if len(blob) < 48:
                return ""
            nonce = blob[:16]
            mac = blob[16:48]
            ciphertext = blob[48:]
            expected_mac = hmac.new(self._master_key, nonce + ciphertext, hashlib.sha256).digest()
            if not hmac.compare_digest(mac, expected_mac):
                return ""
            stream = self._keystream(nonce, len(ciphertext))
            plaintext = bytes(a ^ b for a, b in zip(ciphertext, stream))
            return plaintext.decode("utf-8")
        except Exception:
            return ""

    def set_user_key(
        self,
        provider: str,
        api_key: str,
        model: str = "",
        temperature: Optional[float] = None
    ) -> Dict[str, Any]:
        prov = (provider or "auto").lower().strip()
        clean_key = (api_key or "").strip()

        if clean_key and prov == "auto":
            prov = infer_provider_from_key(clean_key)

        if prov not in SUPPORTED_PROVIDERS and prov not in ("auto", "heuristic"):
            prov = "gemini"

        if clean_key and prov in SUPPORTED_PROVIDERS:
            self._store[prov] = {
                "ciphertext": self._encrypt(clean_key),
                "masked": mask_api_key(clean_key),
                "updated_at": int(time.time())
            }

        self._active_provider = prov
        if prov in SUPPORTED_PROVIDERS:
            self._active_model = normalize_model_for_provider(prov, model or self._active_model)
        else:
            self._active_model = ""

        if temperature is not None:
            self._temperature = max(0.0, min(1.0, float(temperature)))

        return self.get_public_status()

    def get_decrypted_key(self, provider: str) -> str:
        prov = (provider or "").lower().strip()
        entry = self._store.get(prov)
        if entry and entry.get("ciphertext"):
            decrypted = self._decrypt(entry["ciphertext"])
            if decrypted:
                return decrypted

        # Fallback to environment variable keys if not in user runtime vault
        if prov == "gemini" and settings.GEMINI_API_KEY:
            return settings.GEMINI_API_KEY.strip()
        if prov == "groq" and settings.GROQ_API_KEY:
            return settings.GROQ_API_KEY.strip()
        if prov == "openai" and settings.OPENAI_API_KEY:
            return settings.OPENAI_API_KEY.strip()
        return ""

    def clear_keys(self, provider: Optional[str] = None) -> Dict[str, Any]:
        if provider and provider.lower() in self._store:
            del self._store[provider.lower()]
        else:
            self._store.clear()
            self._active_provider = "auto"
            self._active_model = ""
        return self.get_public_status()

    def resolve_active_credentials(self) -> Tuple[str, str, str, str]:
        """
        Resolve (provider, api_key, model, source) in priority order:
        1. Per-request HTTP headers (X-AI-Key / X-AI-Provider / X-AI-Model)
        2. User-configured runtime encrypted vault
        3. Server .env keys (GEMINI_API_KEY, GROQ_API_KEY, OPENAI_API_KEY)
        4. Heuristic fallback ('heuristic', '', 'deterministic-heuristics', 'heuristic')
        """
        req_key = (_req_api_key_ctx.get() or "").strip()
        req_prov = (_req_provider_ctx.get() or "").lower().strip()
        req_model = (_req_model_ctx.get() or "").strip()

        if req_prov == "heuristic":
            return ("heuristic", "", "deterministic-heuristics", "heuristic")

        if req_key:
            prov = req_prov if req_prov in SUPPORTED_PROVIDERS else infer_provider_from_key(req_key)
            mod = normalize_model_for_provider(prov, req_model or self._active_model)
            return (prov, req_key, mod, "user_request")

        # Check active provider in vault
        target_prov = req_prov if req_prov in SUPPORTED_PROVIDERS else self._active_provider
        if target_prov == "heuristic":
            return ("heuristic", "", "deterministic-heuristics", "heuristic")

        if target_prov in SUPPORTED_PROVIDERS:
            vault_entry = self._store.get(target_prov)
            if vault_entry and vault_entry.get("ciphertext"):
                dec = self._decrypt(vault_entry["ciphertext"])
                if dec:
                    mod = normalize_model_for_provider(target_prov, req_model or self._active_model)
                    return (target_prov, dec, mod, "user_vault")
            env_key = self.get_decrypted_key(target_prov)
            if env_key:
                mod = normalize_model_for_provider(target_prov, req_model or self._active_model)
                return (target_prov, env_key, mod, "env")

        # Auto-detect across any user-configured vault keys first, then .env keys
        for p in ("gemini", "groq", "openai"):
            if p in self._store:
                dec = self._decrypt(self._store[p]["ciphertext"])
                if dec:
                    mod = normalize_model_for_provider(p, req_model or self._active_model)
                    return (p, dec, mod, "user_vault")

        for p in ("gemini", "groq", "openai"):
            env_key = self.get_decrypted_key(p)
            if env_key:
                mod = normalize_model_for_provider(p, req_model or self._active_model)
                return (p, env_key, mod, "env")

        return ("heuristic", "", "deterministic-heuristics", "heuristic")

    def get_public_status(self) -> Dict[str, Any]:
        """Return safe, masked AI configuration status for the frontend UI."""
        prov, key, model, source = self.resolve_active_credentials()
        providers_status = {}
        for p_id, meta in SUPPORTED_PROVIDERS.items():
            k = ""
            src = "none"
            if p_id in self._store:
                k = self._decrypt(self._store[p_id]["ciphertext"])
                src = "user"
            elif self.get_decrypted_key(p_id):
                k = self.get_decrypted_key(p_id)
                src = "env"
            providers_status[p_id] = {
                "name": meta["name"],
                "has_key": bool(k),
                "masked_key": mask_api_key(k) if k else "",
                "source": src,
                "default_model": meta["default_model"],
                "models": meta["models"],
                "key_prefix_hint": meta["key_prefix_hint"],
                "docs_url": meta["docs_url"]
            }

        return {
            "active_provider": prov,
            "configured_provider": self._active_provider,
            "active_model": model,
            "temperature": self._temperature,
            "has_active_key": bool(key),
            "masked_active_key": mask_api_key(key) if key else "",
            "key_source": source,
            "providers": providers_status
        }


ai_vault = EncryptedKeyVault()


def set_request_ai_context(
    provider: Optional[str] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None
) -> Tuple[Any, Any, Any]:
    t1 = _req_provider_ctx.set(provider.strip() if provider else None)
    t2 = _req_api_key_ctx.set(api_key.strip() if api_key else None)
    t3 = _req_model_ctx.set(model.strip() if model else None)
    return (t1, t2, t3)


def reset_request_ai_context(tokens: Tuple[Any, Any, Any]) -> None:
    t1, t2, t3 = tokens
    _req_provider_ctx.reset(t1)
    _req_api_key_ctx.reset(t2)
    _req_model_ctx.reset(t3)


async def _call_gemini(
    api_key: str,
    model: str,
    prompt: str,
    system_prompt: str,
    temperature: float,
    max_tokens: int
) -> Tuple[bool, str, str]:
    """
    Call Google Gemini REST API passing the API key securely via x-goog-api-key header.
    Uses systemInstruction properly and handles Gemini 2.5 thinking/multi-part responses safely.
    """
    primary_model = normalize_model_for_provider("gemini", model)
    models_to_try = [primary_model]
    for fallback_m in ("gemini-2.5-flash", "gemini-2.0-flash"):
        if fallback_m not in models_to_try:
            models_to_try.append(fallback_m)

    headers = {
        "Content-Type": "application/json",
        "x-goog-api-key": api_key
    }
    # Ensure sufficient token budget so Gemini 2.5 thinking tokens never truncate text output
    effective_max_tokens = max(max_tokens, 512)
    payload = {
        "systemInstruction": {
            "parts": [{"text": system_prompt}]
        },
        "contents": [
            {
                "role": "user",
                "parts": [{"text": prompt}]
            }
        ],
        "generationConfig": {
            "temperature": temperature,
            "maxOutputTokens": effective_max_tokens
        }
    }

    last_err = ""
    is_vertex_express = api_key.startswith("AQ.")
    async with httpx.AsyncClient(timeout=20.0) as client:
        for m in models_to_try:
            endpoints = (
                [
                    f"https://aiplatform.googleapis.com/v1/publishers/google/models/{m}:generateContent",
                    f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent",
                ]
                if is_vertex_express
                else [f"https://generativelanguage.googleapis.com/v1beta/models/{m}:generateContent"]
            )
            for url in endpoints:
                try:
                    resp = await client.post(url, headers=headers, json=payload)
                    if resp.status_code == 200:
                        data = resp.json()
                        candidates = data.get("candidates") or []
                        if candidates:
                            content_obj = candidates[0].get("content") or {}
                            parts = content_obj.get("parts") or []
                            # Filter out internal thought parts if present, keeping output text parts
                            text_chunks = [
                                p.get("text", "")
                                for p in parts
                                if isinstance(p, dict) and p.get("text") and not p.get("thought", False)
                            ]
                            if not text_chunks:
                                text_chunks = [
                                    p.get("text", "")
                                    for p in parts
                                    if isinstance(p, dict) and p.get("text")
                                ]
                            combined = "\n".join(text_chunks).strip()
                            if combined:
                                return True, combined, ""
                        last_err = "Gemini returned an empty response."
                    else:
                        err_body = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {}
                        err_msg = err_body.get("error", {}).get("message") or f"HTTP {resp.status_code}"
                        last_err = sanitize_log_message(err_msg)
                except Exception as e:
                    last_err = sanitize_log_message(str(e))
    return False, "", last_err or "Gemini request failed."


async def _call_groq(
    api_key: str,
    model: str,
    prompt: str,
    system_prompt: str,
    temperature: float,
    max_tokens: int
) -> Tuple[bool, str, str]:
    """Call Groq OpenAI-compatible Chat Completions endpoint with active production models."""
    target_model = normalize_model_for_provider("groq", model)
    models_to_try = [target_model]
    for fallback_m in ("llama-3.3-70b-versatile", "llama-3.1-8b-instant"):
        if fallback_m not in models_to_try:
            models_to_try.append(fallback_m)

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }

    last_err = ""
    async with httpx.AsyncClient(timeout=20.0) as client:
        for m in models_to_try:
            payload = {
                "model": m,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "temperature": temperature,
                "max_tokens": max(max_tokens, 256)
            }
            try:
                resp = await client.post("https://api.groq.com/openai/v1/chat/completions", headers=headers, json=payload)
                if resp.status_code == 200:
                    choices = resp.json().get("choices") or []
                    if choices:
                        content = choices[0].get("message", {}).get("content", "")
                        if content:
                            return True, content, ""
                else:
                    err_body = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {}
                    err_msg = err_body.get("error", {}).get("message") or f"HTTP {resp.status_code}"
                    last_err = sanitize_log_message(err_msg)
                    if resp.status_code in (401, 403):
                        break
            except Exception as e:
                last_err = sanitize_log_message(str(e))
    return False, "", last_err or "Groq request failed."


async def _call_openai(
    api_key: str,
    model: str,
    prompt: str,
    system_prompt: str,
    temperature: float,
    max_tokens: int
) -> Tuple[bool, str, str]:
    """Call OpenAI Chat Completions endpoint."""
    target_model = normalize_model_for_provider("openai", model)
    models_to_try = [target_model]
    if "gpt-4o-mini" not in models_to_try:
        models_to_try.append("gpt-4o-mini")

    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    last_err = ""
    async with httpx.AsyncClient(timeout=20.0) as client:
        for m in models_to_try:
            payload = {
                "model": m,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                "temperature": temperature,
                "max_tokens": max(max_tokens, 256)
            }
            try:
                resp = await client.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)
                if resp.status_code == 200:
                    choices = resp.json().get("choices") or []
                    if choices:
                        content = choices[0].get("message", {}).get("content", "")
                        if content:
                            return True, content, ""
                err_body = resp.json() if resp.headers.get("content-type", "").startswith("application/json") else {}
                err_msg = err_body.get("error", {}).get("message") or f"HTTP {resp.status_code}"
                last_err = sanitize_log_message(err_msg)
                if resp.status_code in (401, 403):
                    break
            except Exception as e:
                last_err = sanitize_log_message(str(e))
    return False, "", last_err or "OpenAI request failed."


async def call_llm(
    prompt: str,
    system_prompt: str = "You are a helpful technical career assistant.",
    temperature: Optional[float] = None,
    max_tokens: int = 1200,
    caller_name: str = "CareerPilot AI"
) -> str:
    """
    Unified secure LLM caller used across all CareerPilot agents and extractors.
    Automatically selects user-provided key (request header or encrypted vault) or .env key,
    and falls back safely if unavailable.
    """
    prov, api_key, model, _ = ai_vault.resolve_active_credentials()
    if prov == "heuristic" or not api_key:
        return ""

    temp = temperature if temperature is not None else ai_vault._temperature

    if prov == "gemini":
        ok, text, err = await _call_gemini(api_key, model, prompt, system_prompt, temp, max_tokens)
        if ok:
            return text
        print(f"[{caller_name}] Gemini call failed: {sanitize_log_message(err)}")

    elif prov == "groq":
        ok, text, err = await _call_groq(api_key, model, prompt, system_prompt, temp, max_tokens)
        if ok:
            return text
        print(f"[{caller_name}] Groq call failed: {sanitize_log_message(err)}")

    elif prov == "openai":
        ok, text, err = await _call_openai(api_key, model, prompt, system_prompt, temp, max_tokens)
        if ok:
            return text
        print(f"[{caller_name}] OpenAI call failed: {sanitize_log_message(err)}")

    return ""


async def verify_ai_connection(
    provider: Optional[str] = None,
    api_key: Optional[str] = None,
    model: Optional[str] = None
) -> Dict[str, Any]:
    """
    Verify an API key with the target provider using a lightweight test prompt.
    Never returns or logs the raw key.
    """
    clean_key = (api_key or "").strip()
    prov = (provider or "").lower().strip()

    if not clean_key:
        res_prov, res_key, res_model, _ = ai_vault.resolve_active_credentials()
        if prov and prov in SUPPORTED_PROVIDERS and prov != res_prov:
            clean_key = ai_vault.get_decrypted_key(prov)
        else:
            prov = res_prov
            clean_key = res_key
            model = model or res_model

    if not clean_key or prov == "heuristic":
        return {
            "success": False,
            "provider": prov or "none",
            "message": "No API key provided to verify. Please enter a Gemini, Groq, or OpenAI API key."
        }

    if prov not in SUPPORTED_PROVIDERS:
        prov = infer_provider_from_key(clean_key)

    valid_fmt, fmt_msg = validate_api_key_format(prov, clean_key)
    if not valid_fmt:
        return {
            "success": False,
            "provider": prov,
            "masked_key": mask_api_key(clean_key),
            "message": fmt_msg
        }

    target_model = normalize_model_for_provider(prov, model)
    start_ts = time.perf_counter()

    test_sys = "You are a connectivity check assistant."
    test_prompt = "Reply with the single word READY."

    if prov == "gemini":
        ok, text, err = await _call_gemini(clean_key, target_model, test_prompt, test_sys, 0.1, 256)
    elif prov == "groq":
        ok, text, err = await _call_groq(clean_key, target_model, test_prompt, test_sys, 0.1, 64)
    else:
        ok, text, err = await _call_openai(clean_key, target_model, test_prompt, test_sys, 0.1, 64)

    latency_ms = round((time.perf_counter() - start_ts) * 1000)

    if ok:
        return {
            "success": True,
            "provider": prov,
            "provider_name": SUPPORTED_PROVIDERS[prov]["name"],
            "model": target_model,
            "masked_key": mask_api_key(clean_key),
            "latency_ms": latency_ms,
            "message": f"Connected to {SUPPORTED_PROVIDERS[prov]['name']} ({target_model}) in {latency_ms}ms."
        }
    else:
        return {
            "success": False,
            "provider": prov,
            "provider_name": SUPPORTED_PROVIDERS[prov]["name"],
            "model": target_model,
            "masked_key": mask_api_key(clean_key),
            "message": f"Verification failed: {sanitize_log_message(err)}"
        }
