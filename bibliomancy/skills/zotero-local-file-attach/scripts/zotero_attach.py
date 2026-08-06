#!/usr/bin/env python3
"""Attach files to Zotero through the desktop app's loopback servers on port 23119.

Two independent servers share the port and neither touches api.zotero.org:

  /api/        the local Web-API mirror. Writes need Zotero 10 and a key minted
               by an approval dialog. Can target an item that already exists.
  /connector/  what the browser extension talks to. No version floor, no key,
               no dialog. Only reaches items it created in the same session.
"""

import argparse
import hashlib
import json
import mimetypes
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
import uuid

HOST = "http://localhost:23119"
API = HOST + "/api"
CONNECTOR = HOST + "/connector"
APP_NAME = "Claude Code"
KEY_CACHE = os.path.join(
    os.environ.get("XDG_CACHE_HOME") or os.path.expanduser("~/.cache"),
    "zotero-attach", "local-api-keys.json",
)


def request(method, url, data=None, headers=None):
    req = urllib.request.Request(url, data=data, method=method)
    for k, v in (headers or {}).items():
        req.add_header(k, v)
    try:
        with urllib.request.urlopen(req) as r:
            return r.status, dict(r.headers), r.read()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read()
    except urllib.error.URLError as e:
        sys.exit(f"Zotero is not reachable on {HOST}: {e.reason}. Is the app running?")


def content_type(path):
    return mimetypes.guess_type(path)[0] or "application/octet-stream"


# --- /api/ route -----------------------------------------------------------


def read_cache():
    try:
        with open(KEY_CACHE) as f:
            return json.load(f)
    except (OSError, ValueError):
        return {}


def write_cache(cache):
    os.makedirs(os.path.dirname(KEY_CACHE), exist_ok=True)
    fd = os.open(KEY_CACHE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        json.dump(cache, f)


class LocalAPI:
    """Holds the server ID and a write key.

    A remembered key (Always Allow) is cached under the server ID, which lives
    in the Zotero database and survives restarts, so the dialog appears once
    per machine. A plain Allow is single-use and stays out of the cache, so
    every write re-authorizes on the 401 and shows another dialog.
    """

    def __init__(self):
        _, headers, _ = request("GET", API + "/")
        self.server_id = headers.get("Zotero-Server-ID")
        self.version = headers.get("X-Zotero-Version", "?")
        if not self.server_id:
            sys.exit(
                f"No Zotero-Server-ID from {API}/ (version {self.version}). "
                "Local API writes need Zotero 10 or newer; use `save` instead."
            )
        self.key = read_cache().get(self.server_id)

    def authorize(self):
        status, _, body = request(
            "POST", f"{API}/local/authorize",
            data=json.dumps({"appName": APP_NAME}).encode(),
            headers={"Content-Type": "application/json",
                     "Zotero-Server-ID": self.server_id},
        )
        if status == 403:
            sys.exit("Zotero denied the write authorization request.")
        if status != 200:
            sys.exit(f"authorize failed: {status} {body!r}")
        grant = json.loads(body)
        self.key = grant["key"]
        if grant.get("remember"):
            cache = read_cache()
            cache[self.server_id] = self.key
            write_cache(cache)

    def forget(self):
        """Drop a cached key Zotero no longer honors (user cleared authorizations)."""
        cache = read_cache()
        if cache.pop(self.server_id, None):
            write_cache(cache)

    def write(self, method, path, data=None, extra=None):
        if not self.key:
            self.authorize()
        for attempt in range(2):
            h = {"Zotero-API-Key": self.key, "Zotero-Server-ID": self.server_id}
            h.update(extra or {})
            status, headers, body = request(method, API + path, data=data, headers=h)
            if status == 401 and attempt == 0:
                self.forget()
                self.authorize()
                continue
            return status, headers, body


def attach(parent, path, title=None):
    path = os.path.abspath(path)
    data = open(path, "rb").read()
    filename = os.path.basename(path)
    api = LocalAPI()

    # A file cannot be posted to the parent; it needs its own attachment item.
    item = {
        "itemType": "attachment",
        "parentItem": parent,
        "linkMode": "imported_file",
        "title": title or filename,
        "filename": filename,
        "contentType": content_type(path),
    }
    status, _, body = api.write(
        "POST", "/users/0/items",
        data=json.dumps([item]).encode(),
        extra={"Content-Type": "application/json"},
    )
    result = json.loads(body)
    if status != 200 or not result.get("successful"):
        sys.exit(f"item creation failed: {status} {json.dumps(result, indent=2)}")
    key = result["successful"]["0"]["key"]
    print(f"attachment item: {key}")

    form = urllib.parse.urlencode({
        "md5": hashlib.md5(data).hexdigest(),
        "filename": filename,
        "filesize": len(data),
        "mtime": int(os.path.getmtime(path) * 1000),
    }).encode()
    status, _, body = api.write(
        "POST", f"/users/0/items/{key}/file", data=form,
        extra={"Content-Type": "application/x-www-form-urlencoded",
               "If-None-Match": "*"},
    )
    if status != 200:
        sys.exit(f"upload registration failed: {status} {body!r}")
    reg = json.loads(body)

    if reg.get("exists"):
        print("identical file already on disk; registration was enough")
    else:
        # The upload key in the returned URL is the authorization here.
        status, _, body = request("POST", reg["url"], data=data,
                                  headers={"Content-Type": reg["contentType"]})
        if status != 201:
            sys.exit(f"upload failed: {status} {body!r}")
        status, _, body = api.write(
            "POST", f"/users/0/items/{key}/file",
            data=urllib.parse.urlencode({"upload": reg["uploadKey"]}).encode(),
            extra={"Content-Type": "application/x-www-form-urlencoded",
                   "If-None-Match": "*"},
        )
        if status != 204:
            sys.exit(f"upload completion failed: {status} {body!r}")
        print(f"uploaded {len(data)} bytes")

    print(f"attached to {parent} as {key}")


# --- /connector/ route -----------------------------------------------------


def connector_post(path, data, headers):
    h = {"X-Zotero-Connector-API-Version": "3"}
    h.update(headers)
    status, _, body = request("POST", CONNECTOR + path, data=data, headers=h)
    return status, body


def save(metadata_path, path, title=None):
    path = os.path.abspath(path)
    data = open(path, "rb").read()
    item = json.load(open(metadata_path))
    if isinstance(item, list):
        if len(item) != 1:
            sys.exit("metadata must describe exactly one item")
        item = item[0]

    session = str(uuid.uuid4())
    uri = item.get("url") or (f"https://doi.org/{item['DOI']}" if item.get("DOI")
                              else f"http://localhost/zotero-attach/{session}")
    # Zotero matches the upload to the declaration by this URL, and never
    # fetches it. Keeping it distinct from the item URI avoids a collision
    # with a snapshot of the page itself.
    attachment_url = uri + f"#file-{session}"
    attachment_title = title or "Full Text PDF"
    mime = content_type(path)

    item = dict(item, attachments=[{
        "title": attachment_title,
        "url": attachment_url,
        "mimeType": mime,
        "snapshot": False,
    }])
    status, body = connector_post(
        "/saveItems",
        json.dumps({"sessionID": session, "uri": uri, "items": [item]}).encode(),
        {"Content-Type": "application/json"},
    )
    if status not in (200, 201):
        sys.exit(f"saveItems failed: {status} {body!r}")
    print(f"item created (session {session})")

    # Metadata rides in the header; the body is the raw bytes.
    status, body = connector_post(
        "/saveAttachment", data,
        {"Content-Type": mime, "X-Metadata": json.dumps({
            "sessionID": session,
            "url": attachment_url,
            "title": attachment_title,
            "contentType": mime,
        })},
    )
    if status not in (200, 201, 204):
        sys.exit(f"saveAttachment failed: {status} {body!r}. "
                 "A bare 500 usually means the declaration did not match.")
    print("file attached; Zotero renamed it per its own filename template")


# --- probe -----------------------------------------------------------------


def probe():
    status, headers, _ = request("GET", API + "/")
    version = headers.get("X-Zotero-Version", "unknown")
    server_id = headers.get("Zotero-Server-ID")
    print(f"zotero {version} (GET /api/ -> {status})")
    print(f"local API writes: {'yes' if server_id else 'no (needs Zotero 10+)'}")
    if server_id:
        cached = server_id in read_cache()
        print(f"remembered write key: {'yes' if cached else 'no (dialog on next write)'}")

    status, body = connector_post("/ping", b"{}", {"Content-Type": "application/json"})
    try:
        prefs = json.loads(body).get("prefs", {})
    except ValueError:
        prefs = {}
    supported = prefs.get("supportsAttachmentUpload")
    print(f"connector upload: {supported} (POST /connector/ping -> {status})")


def main():
    p = argparse.ArgumentParser(description=__doc__)
    sub = p.add_subparsers(dest="cmd", required=True)

    a = sub.add_parser("attach", help="attach a file to an existing item")
    a.add_argument("item_key")
    a.add_argument("file")
    a.add_argument("--title", help="attachment title (default: the filename)")

    s = sub.add_parser("save", help="create an item from metadata and attach a file")
    s.add_argument("metadata", help="JSON file holding one Zotero item")
    s.add_argument("file")
    s.add_argument("--title", help="attachment title (default: Full Text PDF)")

    sub.add_parser("probe", help="report which routes this Zotero supports")

    args = p.parse_args()
    if args.cmd == "attach":
        attach(args.item_key, args.file, args.title)
    elif args.cmd == "save":
        save(args.metadata, args.file, args.title)
    else:
        probe()


if __name__ == "__main__":
    main()
