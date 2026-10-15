# I Interviewed an Agentic AI Developer — Hands-On Demos

Demo code for the VC Tech Talks series on [YouTube @VCTechTalks](https://www.youtube.com/@VCTechTalks).

Everything runs **locally and free** with [Ollama](https://ollama.com). You don't need an account, an API key or a credit card.

## Setup
```bash
git clone https://github.com/VikasChoataHP/vctechtalks-demo.git
cd vctechtalks-demo/agentic-ai/interview-lessons
uv sync

ollama pull qwen2.5:7b
ollama pull nomic-embed-text
ollama pull all-minilm
ollama pull mxbai-embed-large

uv run 00_check_setup.py
```

- **8 GB RAM:** use a smaller chat model: `ollama pull qwen2.5:3b`, then `CHAT_MODEL=qwen2.5:3b uv run ...`
- **No local models:** use the Google Gemini API free tier. Copy `.env.example` to `.env`, add your key, then run `uv run --env-file .env <script>`. Use demo data only, because Google may use free-tier prompts to improve its products.

## Scripts
| Video | Script | What it shows |
|---|---|---|
| 0 | `00_check_setup.py` | Checks that the models and the API are working |
| 1 | `01_rag_basic.py` | A minimal RAG pipeline |
| 2 | `02_compare_embeddings.py` | Compares embedding models using Hit@1, Hit@3 and MRR on your own data |
| 3 | `03_evaluate_rag.py` | A golden test set plus LLM-as-judge (faithfulness and correctness) |
| 4 | `04_agent_from_scratch.py` | An agent loop with tools and human approval, no framework |
| 5 | `05_langgraph_router.py` | A LangGraph graph with conditional edges and a rewrite loop |

`common.py` holds the shared model client, chunking, embeddings and vector search code. `data/` holds the fictional "Nimbus Platform" docs and `golden.json` (12 test questions).

## Configuration
All settings are environment variables: `LLM_BASE_URL`, `LLM_API_KEY`, `CHAT_MODEL`, `EMBED_MODEL`, `JUDGE_MODEL` and `WEAK_EMBED_MODEL`. The defaults point to Ollama at `http://localhost:11434/v1`.
