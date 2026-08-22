# Obsidian Vault for Codex

Local Codex plugin for reading, searching, creating, editing, moving, and safely deleting Markdown notes in an Obsidian vault.

## Features

- List and search Markdown notes.
- Read, create, append to, and overwrite notes.
- Rename and move notes within the vault.
- Recoverable deletion into the vault's `.trash/` folder.
- Path validation that prevents operations outside the selected vault.

## Configuration

Set `OBSIDIAN_VAULT_PATH` to the absolute path of your vault before launching Codex. If it is not set, provide the vault path when prompted in a task.

Example on macOS/Linux:

```sh
export OBSIDIAN_VAULT_PATH="/Users/you/Documents/My Vault"
```

Deletion is recoverable: notes are moved to `.trash/` inside the vault.

## Privacy

This MCP server runs locally and does not upload your notes to an external service. Codex receives the note content needed to perform the operations you request.

## License

MIT
