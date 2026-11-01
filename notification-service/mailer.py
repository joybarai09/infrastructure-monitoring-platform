
import os
import msal
import requests

CLIENT_ID = "447b2dbd-af83-4bc5-83be-665feb98af23"
AUTHORITY = "https://login.microsoftonline.com/consumers"

SCOPES = ["User.Read", "Mail.Send"]

CACHE_FILE = "/data/msal_cache.bin"
OUTLOOK_EMAIL = "joy.barai@live.com"

GRAPH_URL = "https://graph.microsoft.com/v1.0/me/sendMail"


def get_access_token():
    cache = msal.SerializableTokenCache()

    with open(CACHE_FILE, "r") as file:
        cache.deserialize(file.read())

    app = msal.PublicClientApplication(
        CLIENT_ID,
        authority=AUTHORITY,
        token_cache=cache,
    )

    accounts = app.get_accounts()

    if not accounts:
        raise RuntimeError("No Microsoft account found. Authenticate again.")

    result = app.acquire_token_silent(
        SCOPES,
        account=accounts[0],
    )

    if not result or "access_token" not in result:
        raise RuntimeError(
            "Could not obtain an access token. Re-authentication required."
        )

    if cache.has_state_changed:
        with open(CACHE_FILE, "w") as file:
            file.write(cache.serialize())
        os.chmod(CACHE_FILE, 0o600)

    return result["access_token"]


def send_email(subject, body):
    token = get_access_token()

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json",
    }

    payload = {
        "message": {
            "subject": subject,
            "body": {
                "contentType": "Text",
                "content": body,
            },
            "toRecipients": [
                {
                    "emailAddress": {
                        "address": OUTLOOK_EMAIL,
                    }
                }
            ],
        },
        "saveToSentItems": True,
    }

    response = requests.post(
        GRAPH_URL,
        headers=headers,
        json=payload,
        timeout=30,
    )

    if response.status_code != 202:
        raise RuntimeError(
            f"Microsoft Graph email failed: "
            f"{response.status_code} {response.text}"
        )

    print("Email accepted by Microsoft Graph.")
