# Obsidian Vault plugin for Codex

A local Codex plugin and dependency-free MCP server for reading, searching, creating, editing, moving, and safely deleting Markdown notes in an Obsidian vault.

## Install

Clone this repository:

```sh
git clone https://github.com/Barak31/Obsidian_Chatgpt.git
```

Add its marketplace and install the plugin:

```sh
codex plugin marketplace add /absolute/path/to/Obsidian_Chatgpt
codex plugin add obsidian-vault@barak31
```

Start a new Codex task after installation. Give Codex the absolute vault path when asked, or set `OBSIDIAN_VAULT_PATH` before launching Codex.

## Capabilities

- List and search Markdown notes
- Read, create, append to, and overwrite notes
- Rename and move notes
- Recoverable deletion to `.trash/`
- Vault-bound path validation

## Privacy

The server runs locally and does not upload notes to an external service. Codex receives only the note content needed for requested operations.

## License

MIT
