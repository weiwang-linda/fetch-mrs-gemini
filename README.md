# GitLab Merge Request Client Powered by Gemini Assistant

## Prerequisites

- Python 3.12+
- GitLab MCP Server
- Google Gemini API Key

## Installation

1.  **Clone the repository**:
    ```bash
    git clone <repository-url>
    cd fetch-mrs-gemini
    ```

2.  **(Optional) Create and activate a virtual environment**:
    ```bash
    # Install uv if not already installed
    # curl -LsSf https://astral.sh/uv/install.sh | sh

    uv venv
    source .venv/bin/activate
    ```

3.  **Install dependencies**:
    ```bash
    uv sync
    ```

## Configuration

1.  **Environment Variables**:
    Copy `example.env` to `.env` and fill in the required values:
    ```bash
    cp example.env .env
    ```
    
    Edit `.env`:
    ```ini
    # Gemini API Configuration
    GEMINI_API_KEY=<your-api-key>
    ```

2.  **MCP Server Config**:
    Edit `.rh-gitlab-mcp.env` to fill the required values:
    ```ini
    # GitLab personal access token
    MCP_GITLAB_TOKEN=<your-personal-token>

    # Comma-separated list of allowed group and project IDs (numeric IDs only)
    MCP_ALLOWED_REPOS=<id>
    
    ...
    ```

## Local Execute

**Prerequisites**
1.  Ensure `.rh-gitlab-mcp.env` is present in the home directory. This file contains the configuration for the GitLab MCP server (GitLab token, allowed repos, etc.).
2.  (For Red Hat internal access) Ensure `tls-ca-bundle.pem` is present in the '/etc/pki/ca-trust/extracted/pem/' directory. This certificate bundle is required to access internal GitLab instances.

You can use the helper script:
```bash
python client.py
```

Or run it directly:
```bash
uv run client.py <mcp-server-script>
```

The client starts up, connects to the MCP server, then enters a loop waiting for query input.
