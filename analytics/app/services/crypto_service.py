import base64
import hashlib
import json
from functools import lru_cache
from pathlib import Path

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

from ..schemas.secure_alert import EncryptedAlertEnvelope
from ..settings import SECURE_ALERTS_PRIVATE_KEY_PATH, SECURE_ALERTS_PUBLIC_KEY_PATH


class SecureAlertCryptographyError(Exception):
    pass


@lru_cache(maxsize=1)
def load_private_key():
    return serialization.load_pem_private_key(
        Path(SECURE_ALERTS_PRIVATE_KEY_PATH).read_bytes(),
        password=None,
    )


@lru_cache(maxsize=1)
def load_public_key_pem() -> str:
    return Path(SECURE_ALERTS_PUBLIC_KEY_PATH).read_text(encoding="utf-8").strip()


@lru_cache(maxsize=1)
def load_public_key_fingerprint() -> str:
    pem = load_public_key_pem()
    der_bytes = base64.b64decode(
        "".join(
            line.strip()
            for line in pem.splitlines()
            if "BEGIN" not in line and "END" not in line
        )
    )
    return hashlib.sha256(der_bytes).hexdigest()


def decrypt_alert_envelope(envelope: EncryptedAlertEnvelope) -> dict:
    try:
        if envelope.key_fingerprint != load_public_key_fingerprint():
            raise SecureAlertCryptographyError("key fingerprint mismatch")

        private_key = load_private_key()
        encrypted_key = base64.b64decode(envelope.encrypted_key, validate=True)
        nonce = base64.b64decode(envelope.nonce, validate=True)
        ciphertext = base64.b64decode(envelope.ciphertext, validate=True)
        mac = base64.b64decode(envelope.mac, validate=True)
        session_key = private_key.decrypt(
            encrypted_key,
            padding.OAEP(
                mgf=padding.MGF1(algorithm=hashes.SHA256()),
                algorithm=hashes.SHA256(),
                label=None,
            ),
        )
        plaintext_bytes = AESGCM(session_key).decrypt(nonce, ciphertext + mac, None)
        payload = json.loads(plaintext_bytes.decode("utf-8"))
    except Exception as exc:  # noqa: BLE001
        raise SecureAlertCryptographyError("encrypted payload rejected") from exc

    if not isinstance(payload, dict):
        raise SecureAlertCryptographyError("decrypted payload must be an object")
    return payload
