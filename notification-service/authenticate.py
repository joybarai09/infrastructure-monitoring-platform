
import os
import msal

CLIENT_ID = "447b2dbd-af83-4bc5-83be-665feb98af23"
AUTHORITY = "https://login.microsoftonline.com/consumers"

SCOPES = [
    "User.Read",
    "Mail.Send",
]

CACHE_FILE = "/data/msal_cache.bin"


def main():
    os.makedirs("/data", exist_ok=True)

    cache = msal.SerializableTokenCache()

    if os.path.exists(CACHE_FILE):
        with open(CACHE_FILE, "r") as file:
            cache.deserialize(file.read())

    app = msal.PublicClientApplication(
        CLIENT_ID,
        authority=AUTHORITY,
        token_cache=cache,
    )

    flow = app.initiate_device_flow(scopes=SCOPES)

    if "user_code" not in flow:
        raise RuntimeError(f"Device flow failed: {flow}")

    print(flow["message"], flush=True)

    result = app.acquire_token_by_device_flow(flow)

    if "access_token" not in result:
        raise RuntimeError(
            f"Authentication failed: {result.get('error_description')}"
        )

    with open(CACHE_FILE, "w") as file:
        file.write(cache.serialize())

    os.chmod(CACHE_FILE, 0o600)

    print("Microsoft authentication successful.")
    print("Token cache saved securely.")


if __name__ == "__main__":
    main()
