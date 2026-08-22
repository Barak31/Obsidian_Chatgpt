#!/usr/bin/env python3
"""Dependency-free MCP server for a local Obsidian vault."""

import json
import os
import shutil
import sys
from pathlib import Path


def schema(properties, required=()):
    return {"type": "object", "properties": properties, "required": list(required), "additionalProperties": False}


VAULT = {"vault_path": {"type": "string", "description": "Absolute vault path; optional when OBSIDIAN_VAULT_PATH is set."}}
TOOLS = [
    {"name": "list_notes", "description": "List Markdown notes in an Obsidian vault.", "inputSchema": schema({**VAULT, "folder": {"type": "string", "default": ""}, "limit": {"type": "integer", "minimum": 1, "maximum": 1000, "default": 200}})},
    {"name": "search_notes", "description": "Search note paths and contents (case-insensitive).", "inputSchema": schema({**VAULT, "query": {"type": "string"}, "limit": {"type": "integer", "minimum": 1, "maximum": 100, "default": 20}}, ["query"])},
    {"name": "read_note", "description": "Read one Markdown note.", "inputSchema": schema({**VAULT, "path": {"type": "string"}}, ["path"])},
    {"name": "write_note", "description": "Create, append to, or overwrite a Markdown note.", "inputSchema": schema({**VAULT, "path": {"type": "string"}, "content": {"type": "string"}, "mode": {"type": "string", "enum": ["create", "append", "overwrite"], "default": "create"}}, ["path", "content"])},
    {"name": "move_note", "description": "Rename or move a note inside the vault.", "inputSchema": schema({**VAULT, "source": {"type": "string"}, "destination": {"type": "string"}}, ["source", "destination"])},
    {"name": "delete_note", "description": "Move a note to the vault .trash folder. Requires confirm=true.", "inputSchema": schema({**VAULT, "path": {"type": "string"}, "confirm": {"type": "boolean", "default": False}}, ["path", "confirm"])},
]


def vault(args):
    raw = args.get("vault_path") or os.environ.get("OBSIDIAN_VAULT_PATH")
    if not raw:
        raise ValueError("Provide vault_path or set OBSIDIAN_VAULT_PATH.")
    root = Path(raw).expanduser().resolve()
    if not root.is_dir():
        raise ValueError(f"Vault directory does not exist: {root}")
    return root


def inside(root, relative, markdown=False):
    rel = str(relative).strip().replace("\\", "/")
    if not rel or rel.startswith("/"):
        raise ValueError("Use a non-empty path relative to the vault.")
    if markdown and not rel.lower().endswith(".md"):
        rel += ".md"
    target = (root / rel).resolve()
    if target != root and root not in target.parents:
        raise ValueError("Path escapes the vault.")
    return target


def rel(root, path):
    return path.relative_to(root).as_posix()


def call(name, args):
    root = vault(args)
    if name == "list_notes":
        base = inside(root, args.get("folder") or ".")
        if not base.is_dir():
            raise ValueError("Folder does not exist.")
        limit = int(args.get("limit", 200))
        notes = [rel(root, p) for p in base.rglob("*.md") if ".trash" not in p.parts]
        return {"notes": sorted(notes)[:limit], "count": min(len(notes), limit), "truncated": len(notes) > limit}
    if name == "search_notes":
        query = args["query"].casefold()
        limit = int(args.get("limit", 20))
        matches = []
        for path in root.rglob("*.md"):
            if ".trash" in path.parts:
                continue
            text = path.read_text(encoding="utf-8", errors="replace")
            haystack = (rel(root, path) + "\n" + text).casefold()
            if query in haystack:
                index = haystack.find(query)
                excerpt = (rel(root, path) + "\n" + text)[max(0, index - 100):index + len(query) + 180].replace("\n", " ")
                matches.append({"path": rel(root, path), "excerpt": excerpt})
                if len(matches) >= limit:
                    break
        return {"matches": matches, "count": len(matches)}
    if name == "read_note":
        path = inside(root, args["path"], True)
        return {"path": rel(root, path), "content": path.read_text(encoding="utf-8")}
    if name == "write_note":
        path = inside(root, args["path"], True)
        mode = args.get("mode", "create")
        if mode == "create" and path.exists():
            raise ValueError("Note already exists; use append or overwrite.")
        if mode == "append" and not path.exists():
            raise ValueError("Note does not exist; use create.")
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("a" if mode == "append" else "w", encoding="utf-8") as handle:
            handle.write(args["content"])
        return {"path": rel(root, path), "mode": mode, "bytes": len(args["content"].encode("utf-8"))}
    if name == "move_note":
        source = inside(root, args["source"], True)
        destination = inside(root, args["destination"], True)
        if not source.is_file():
            raise ValueError("Source note does not exist.")
        if destination.exists():
            raise ValueError("Destination already exists.")
        destination.parent.mkdir(parents=True, exist_ok=True)
        source.rename(destination)
        return {"source": rel(root, source), "destination": rel(root, destination)}
    if name == "delete_note":
        if args.get("confirm") is not True:
            raise ValueError("Deletion requires confirm=true.")
        source = inside(root, args["path"], True)
        if not source.is_file():
            raise ValueError("Note does not exist.")
        destination = inside(root, ".trash/" + rel(root, source))
        destination.parent.mkdir(parents=True, exist_ok=True)
        if destination.exists():
            destination = destination.with_name(destination.stem + "-deleted" + destination.suffix)
        shutil.move(str(source), str(destination))
        return {"deleted": rel(root, source), "recoverable_at": rel(root, destination)}
    raise ValueError(f"Unknown tool: {name}")


def result(request_id, value=None, error=None):
    payload = {"jsonrpc": "2.0", "id": request_id}
    if error is not None:
        payload["error"] = {"code": -32000, "message": str(error)}
    else:
        payload["result"] = value
    sys.stdout.write(json.dumps(payload, ensure_ascii=False) + "\n")
    sys.stdout.flush()


def main():
    for line in sys.stdin:
        try:
            request = json.loads(line)
            method = request.get("method")
            request_id = request.get("id")
            if request_id is None:
                continue
            if method == "initialize":
                value = {"protocolVersion": request.get("params", {}).get("protocolVersion", "2025-03-26"), "capabilities": {"tools": {}}, "serverInfo": {"name": "obsidian-vault", "version": "0.1.0"}}
            elif method == "tools/list":
                value = {"tools": TOOLS}
            elif method == "tools/call":
                params = request.get("params", {})
                data = call(params.get("name", ""), params.get("arguments") or {})
                value = {"content": [{"type": "text", "text": json.dumps(data, ensure_ascii=False, indent=2)}], "structuredContent": data, "isError": False}
            elif method == "ping":
                value = {}
            else:
                raise ValueError(f"Unsupported method: {method}")
            result(request_id, value=value)
        except Exception as exc:
            result(request.get("id") if isinstance(request, dict) else None, error=exc)


if __name__ == "__main__":
    main()
