# Setup Prompt — paste into any AI

If you have Research OS installed and want an AI to handle the rest (IDE
wiring, first project scaffold, configuration), paste the prompt below into
any AI chat (Claude, ChatGPT, Cursor inline, Aider, OpenCode, Antigravity, …).

It does NOT require a project to exist yet. Use it to prep your environment
when you're between projects.

---

## The prompt

> I want to install and configure **Research OS** on this machine so I can
> use it later when I'm ready to start a research project. Research OS is
> an MCP-native research operating system hosted at
> <https://github.com/VibhavSetlur/Research-OS>.
>
> Please walk me through ALL of the following, asking me before any
> destructive action:
>
> 1. **Check Python ≥ 3.10**. If missing, suggest how to install it for my
>    OS (macOS / Linux / Windows / WSL — please ask which I'm on).
>
> 2. **Install Research OS** with all optional extras:
>    ```bash
>    pip install "research-os[all] @ git+https://github.com/VibhavSetlur/Research-OS.git"
>    ```
>    Use a virtual environment if I tell you to; otherwise install to the
>    user site-packages (`pip install --user`).
>
> 3. **Verify install**: run `research-os --help` and `research-os init --help`
>    and show me the output.
>
> 4. **Detect my AI IDE**. Ask me which I'm using (Claude Code / OpenCode /
>    Antigravity / Cursor / Claude Desktop / VS Code with MCP / Windsurf /
>    Continue / Aider / other). For the chosen IDE:
>    * Tell me what file Research OS will drop on `init` for that IDE.
>    * If it's Claude Desktop or a globally-configured IDE, show me the
>      JSON snippet I'd need to add to my global config (DO NOT modify
>      global configs without my approval).
>
> 5. **Show me the two-command workflow** I'll use when I start a project:
>    ```bash
>    mkdir my-project && cd my-project
>    research-os init                    # scaffolds the workspace + IDE config
>    # then open the IDE on the folder and start chatting
>    ```
>    Mention that `research-os start` is what the IDE auto-launches; I
>    rarely run it manually.
>
> 6. **Show me the 5 essential prompts** I'll use most often:
>    * "fill out the intake"
>    * "what should I do next?"
>    * "run a baseline EDA"
>    * "write the paper for a journal submission"
>    * "make me a dashboard"
>
> 7. **Optional credentials**. Research OS does NOT manage LLM provider
>    keys — my IDE owns model access. The only optional credentials are
>    for literature / web search providers (Semantic Scholar, PubMed,
>    Crossref, Firecrawl, SerpAPI). Tell me where to put them when I
>    eventually want them (`inputs/researcher_config.yaml api_keys.*`),
>    but DON'T ask me for them now.
>
> 8. **Point me at the docs**:
>    * `docs/QUICKSTART.md` — 5 min start.
>    * `docs/RESEARCHER_GUIDE.md` — non-technical walkthrough.
>    * `docs/GUIDE.md` — full tool + protocol reference.
>    * `docs/TOOLS.md` — every MCP tool.
>    * `docs/FAQ.md` — common questions.
>
> Be concise. Don't dump everything in one wall of text. Ask me one question
> at a time when you need input. After step 4 (IDE detection), stop and let
> me confirm before proceeding.

---

## Tips for power users

* If you want a different install path (uv, poetry, conda), say so at the
  start: *"Install via uv instead of pip."* — the AI will adjust.
* If you're on a shared HPC and want it installed in a module: *"I'm on a
  shared cluster; install into ~/.local using `pip install --user`."*
* If you want to skip the IDE wiring step entirely: *"Just install
  Research OS, I'll handle IDE config myself."*
