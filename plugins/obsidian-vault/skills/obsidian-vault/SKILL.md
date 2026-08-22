---
name: obsidian-vault
description: Read, search, create, edit, move, and delete Markdown notes in a local Obsidian vault. Use when the user asks to work with their Obsidian notes, vault, daily notes, or Markdown knowledge base.
---

# Obsidian Vault

Use the `obsidian_vault` MCP tools for all vault operations.

## Vault selection

- Use `OBSIDIAN_VAULT_PATH` when configured.
- Otherwise ask for the absolute vault path once and pass it as `vault_path` in each tool call.
- Never guess among multiple vaults.

## Workflow

1. Use `list_notes` or `search_notes` to locate notes.
2. Use `read_note` before changing an existing note.
3. Use `write_note` with `mode: "create"` for new notes, `mode: "append"` to add material, or `mode: "overwrite"` only when the user clearly wants replacement.
4. Use `move_note` for renames or folder changes.
5. Use `delete_note` only when explicitly requested. Pass `confirm: true`; deletion moves the note into `.trash/` inside the vault so it remains recoverable.

Paths are relative to the vault and normally end in `.md`. Preserve YAML frontmatter, wiki links, embeds, tags, and Markdown structure unless the user asks to change them.
