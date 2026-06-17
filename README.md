# Customer Support Agent

A graph-based workflow agent built with the **Agent Development Kit (ADK 2.0)** that acts as a customer support representative for a shipping company.

The agent classifies incoming user queries and routes them dynamically:
- **Shipping-related queries** (rates, tracking, delivery, returns) are routed to a specialized shipping FAQ agent.
- **Unrelated queries** are politely declined.

---

## 🏗️ Project Structure

```
customer-support-agent/
├── app/                  # Core agent code
│   ├── agent.py          # Main agent routing logic and sub-agents
│   └── app_utils/        # App utilities and helpers
├── tests/                # Unit and integration tests
├── .env                  # Local environment configuration (API keys)
├── GEMINI.md             # AI-assisted development guide
└── pyproject.toml        # Project dependencies & configurations
```

---

## ⚙️ Requirements

Ensure you have the following installed:
- **uv**: Fast Python package manager ([Installation Guide](https://docs.astral.sh/uv/getting-started/installation/))
- **agents-cli**: Google Agents CLI (Install via `uv tool install google-agents-cli`)

---

## 🚀 Quick Start

### 1. Configure the Environment
Create a `.env` file in the root of the project (if not already present) and add your Gemini API Key:
```env
GEMINI_API_KEY=your_actual_api_key_here
```

### 2. Install Dependencies
Initialize the virtual environment and install all packages:
```bash
agents-cli install
```

### 3. Run the Local Playground
Launch the interactive web playground to chat with the agent:
```bash
agents-cli playground
```
Once started, open [http://127.0.0.1:8080](http://127.0.0.1:8080) in your browser.

---

## 🛠️ Key CLI Commands

| Command | Description |
|---------|-------------|
| `agents-cli playground` | Launches the interactive web-based UI for manual conversation. |
| `agents-cli run "prompt"` | Smoke-tests the agent with a single prompt directly in your terminal. |
| `agents-cli lint` | Runs formatting and code quality checks. |
| `agents-cli eval run` | Evaluates agent response quality, tool paths, and behavior. |
| `uv run pytest` | Runs unit and integration code correctness tests. |

---

## 🤖 Agent Flow & Logic

The agent is implemented as a stateful graph workflow in [app/agent.py](app/agent.py):
1. **`save_query`**: Saves the incoming user question to the conversation state.
2. **`classifier_agent`**: Classifies whether the query is shipping-related or unrelated.
3. **`router`**: Inspects the classification result and routes the execution flow.
4. **`shipping_faq_agent` / `decline_node`**: Responds to the user query based on the routed path.
