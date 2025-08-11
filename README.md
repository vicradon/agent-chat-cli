# Agent Chat CLI

A simple CLI built with Python that allows you to set system and personality prompts and use that to chat with different "AI agents".

## Features

1. Prompt saving 
2. Prompt loading
3. Conversation saving/loading (sqlite-based)
4. Conversation export (soon)

## Project Structure

<details>

<summary>Open to view the project structure</summary>

```
.
├── config
│   └── cli_config.py
├── core
│   ├── ai_models.py
│   ├── cleanup.py
│   ├── database.py
│   ├── input.py
│   ├── models.py
│   ├── prompt.py
│   ├── state.py
│   └── welcome.py
├── database.db
├── .env
├── .env.example
├── .gitignore
├── main.py
├── pyproject.toml
├── .python-version
├── README.md
└── uv.lock
```

</details>

## Running

1. Clone the project locally
2. Install dependencies via [`uv`](https://docs.astral.sh/uv/#installation)
    ```sh
    uv sync
    ```
3. Create an .env file from the example file: 
    ```sh
    cp .env.example .env
    ```
4. Populate the Gemini API key and model name in the .env file
5. Run the main.py file:
    ```
    uv run main.py
    ```

You can find the project's config in the `config/cli_config.py` file.

