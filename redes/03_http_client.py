"""
HTTP Client — talking to web servers the way browsers do.

HTTP (HyperText Transfer Protocol) is a request-response protocol that runs
on top of TCP. Every time your browser loads a page, it's doing exactly this:
  1. Open a TCP connection to the server
  2. Send an HTTP request (a structured text message)
  3. Receive an HTTP response (status code + headers + body)
  4. Close the connection

This script uses urllib (standard library, no pip needed) to make real
HTTP requests and inspect what comes back — status codes, headers, and body.

Status code cheat sheet:
  2xx → success (200 OK, 201 Created)
  3xx → redirect (301 Moved Permanently, 302 Found)
  4xx → client error (400 Bad Request, 404 Not Found, 403 Forbidden)
  5xx → server error (500 Internal Server Error)
"""

import urllib.request
import urllib.error
import json


def get(url: str, timeout: int = 5) -> dict:
    """
    Send an HTTP GET request and return a dict with status, headers, and body.
    We set a timeout so the script doesn't hang forever if the server is slow.
    """
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            return {
                "status": response.status,
                "url": response.url,          # final URL after any redirects
                "headers": dict(response.headers),
                "body": response.read().decode("utf-8"),
            }
    except urllib.error.HTTPError as e:
        # HTTPError means we got a response, but with an error status (4xx/5xx).
        # The server replied — it just said "no" or "broken".
        return {"status": e.code, "error": str(e), "body": ""}
    except urllib.error.URLError as e:
        # URLError is lower-level: DNS failure, no route, connection refused.
        # The server never even replied.
        return {"status": 0, "error": str(e.reason), "body": ""}


def inspect_response(result: dict) -> None:
    """Print a human-readable summary of an HTTP response."""
    status = result["status"]

    # Map status codes to simple labels so the output is readable.
    labels = {200: "OK", 201: "Created", 301: "Redirect",
              302: "Redirect", 400: "Bad Request", 404: "Not Found",
              403: "Forbidden", 500: "Server Error"}
    label = labels.get(status, "Unknown")

    print(f"  Status:       {status} {label}")

    if "url" in result:
        print(f"  Final URL:    {result['url']}")

    if "error" in result:
        print(f"  Error:        {result['error']}")
        return

    # Show a few interesting headers — Content-Type tells us what kind of
    # data the server sent back (HTML, JSON, image, etc.)
    headers = result.get("headers", {})
    for key in ("Content-Type", "Server", "Content-Length"):
        if key in headers:
            print(f"  {key:<16}{headers[key]}")

    # Only show body preview so we don't flood the terminal.
    body = result.get("body", "")
    preview = body[:200].replace("\n", " ")
    print(f"  Body preview: {preview}...")


def fetch_json(url: str) -> dict | list | None:
    """
    Fetch a JSON API endpoint and parse the response.
    JSONPlaceholder (jsonplaceholder.typicode.com) is a free fake REST API
    — perfect for practicing HTTP requests without needing a real backend.
    """
    result = get(url)
    if result["status"] == 200:
        return json.loads(result["body"])
    return None


if __name__ == "__main__":
    print("══ HTTP Client ═════════════════════════════════════\n")

    # Test 1: A real website
    print("  ── GET https://httpbin.org/get ─────────────────")
    result = get("https://httpbin.org/get")
    inspect_response(result)

    print()

    # Test 2: A public JSON API — fetch one fake post
    print("  ── JSON API: fetch a post ──────────────────────")
    post = fetch_json("https://jsonplaceholder.typicode.com/posts/1")
    if post:
        print(f"  Title:  {post['title']}")
        print(f"  Body:   {post['body'][:80]}...")
        print(f"  UserID: {post['userId']}")

    print()

    # Test 3: Intentional 404 to see how errors look
    print("  ── 404 example ─────────────────────────────────")
    result = get("https://httpbin.org/status/404")
    inspect_response(result)
