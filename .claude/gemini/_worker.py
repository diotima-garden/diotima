#!/usr/bin/env python3
import sys
import os

mode = sys.argv[1]   # "text", "video", "list", "probe"
model = sys.argv[2] if len(sys.argv) > 2 else None
url = sys.argv[3] if mode == "video" else None

prompt = sys.stdin.read()

api_key = os.environ.get("GOOGLE_API_KEY")
if not api_key:
    print("GOOGLE_API_KEY not set", file=sys.stderr)
    sys.exit(1)

from google import genai  # noqa: E402 — requires venv Python
from google.genai import types

client = genai.Client(api_key=api_key)

if mode == "text":
    response = client.models.generate_content(model=model, contents=prompt)
elif mode == "video":
    response = client.models.generate_content(
        model=model,
        contents=[
            types.Part(file_data=types.FileData(file_uri=url)),
            types.Part(text=prompt),
        ],
    )
elif mode == "list":
    import json
    models = []
    for m in client.models.list():
        methods = getattr(m, "supported_actions", []) or []
        if "generateContent" in methods:
            models.append({
                "name": m.name,
                "display_name": getattr(m, "display_name", m.name),
            })
    print(json.dumps(models))
    sys.exit(0)

elif mode == "probe":
    import json
    from google.genai import errors
    try:
        client.models.generate_content(model=model, contents="hi")
        print(json.dumps({"status": "ok", "model": model}))
    except errors.ClientError as e:
        code = getattr(e, "code", None)
        status = "rate_limited" if code == 429 else "error"
        violations, retry_delay = [], None
        inner = (getattr(e, "details", None) or {}).get("error", {}).get("details", [])
        for detail in inner:
            t = detail.get("@type", "")
            if t.endswith("QuotaFailure"):
                violations = [v.get("quotaId", "") for v in detail.get("violations", [])]
            elif t.endswith("RetryInfo"):
                retry_delay = detail.get("retryDelay")
        print(json.dumps({
            "status": status, "model": model, "code": code,
            "violations": list(dict.fromkeys(violations)),
            "retry_delay": retry_delay,
            "message": getattr(e, "message", str(e))[:200],
        }))
    except Exception as e:
        print(json.dumps({"status": "error", "model": model, "message": str(e)[:300]}))
    sys.exit(0)

else:
    print(f"Unknown mode: {mode}", file=sys.stderr)
    sys.exit(1)

print(response.text.strip())
