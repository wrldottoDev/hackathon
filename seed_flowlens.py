import os
from typing import Any

import httpx


BANK_A_URL = os.getenv("FLOWLENS_BANK_A_URL", "http://127.0.0.1:8001")
BANK_B_URL = os.getenv("FLOWLENS_BANK_B_URL", "http://127.0.0.1:8002")
ANALYTICS_URL = os.getenv("FLOWLENS_ANALYTICS_URL", "http://127.0.0.1:8003")
ANALYTICS_API_KEY = os.getenv("FLOWLENS_ANALYTICS_API_KEY", "flowlens-analytics-key-dev")
DEFAULT_PASSWORD = "DemoPass123"


def request_json(
    client: httpx.Client,
    method: str,
    url: str,
    *,
    headers: dict[str, str] | None = None,
    json: dict[str, Any] | None = None,
) -> Any:
    response = client.request(method, url, headers=headers, json=json)
    response.raise_for_status()
    if response.content:
        return response.json()
    return None


def login(client: httpx.Client, base_url: str, email: str) -> tuple[str, list[dict[str, Any]]]:
    payload = request_json(
        client,
        "POST",
        f"{base_url}/auth/login",
        json={"email": email, "password": DEFAULT_PASSWORD},
    )
    token = payload["access_token"]
    accounts = request_json(
        client,
        "GET",
        f"{base_url}/accounts/my",
        headers={"Authorization": f"Bearer {token}"},
    )
    return token, accounts


def create_interbank_transfer(
    client: httpx.Client,
    base_url: str,
    token: str,
    source_account_number: str,
    destination_account_number: str,
    amount: float,
    *,
    channel: str,
    location: str,
    description: str,
):
    return request_json(
        client,
        "POST",
        f"{base_url}/transactions/interbank",
        headers={"Authorization": f"Bearer {token}"},
        json={
            "source_account_number": source_account_number,
            "destination_account_number": destination_account_number,
            "amount": amount,
            "channel": channel,
            "location": location,
            "description": description,
        },
    )


def register_banks_in_analytics(client: httpx.Client):
    headers = {"X-Analytics-Key": ANALYTICS_API_KEY}
    for bank_name, bank_code, api_url in [
        ("Banco A", "BKA", BANK_A_URL),
        ("Banco B", "BKB", BANK_B_URL),
    ]:
        request_json(
            client,
            "POST",
            f"{ANALYTICS_URL}/banks/register",
            headers=headers,
            json={
                "bank_name": bank_name,
                "bank_code": bank_code,
                "api_url": api_url,
                "status": "active",
            },
        )
    return request_json(
        client,
        "GET",
        f"{ANALYTICS_URL}/transactions/fetch",
        headers=headers,
    )


def main():
    with httpx.Client(timeout=10.0) as client:
        a_token, a_accounts = login(client, BANK_A_URL, "demo@bancoa.com")
        b_token, b_accounts = login(client, BANK_B_URL, "demo@bancob.com")

        a_primary = a_accounts[0]["account_number"]
        a_secondary = a_accounts[1]["account_number"] if len(a_accounts) > 1 else a_primary
        b_primary = b_accounts[0]["account_number"]
        b_secondary = b_accounts[1]["account_number"] if len(b_accounts) > 1 else b_primary

        create_interbank_transfer(
            client,
            BANK_A_URL,
            a_token,
            a_primary,
            b_primary,
            13_500,
            channel="api",
            location="Cross-bank API",
            description="Transferencia interbancaria de alto monto",
        )
        for amount in [180, 195, 210, 225]:
            create_interbank_transfer(
                client,
                BANK_A_URL,
                a_token,
                a_secondary,
                b_secondary,
                amount,
                channel="mobile",
                location="San Jose, CR",
                description="Ráfaga interbancaria de montos pequeños",
            )
        create_interbank_transfer(
            client,
            BANK_B_URL,
            b_token,
            b_secondary,
            a_primary,
            780,
            channel="web",
            location="Heredia, CR",
            description="Salida rápida tras ingresos interbancarios",
        )

        analytics_summary = register_banks_in_analytics(client)
        print("Interbank seed completado")
        print(analytics_summary)


if __name__ == "__main__":
    main()
