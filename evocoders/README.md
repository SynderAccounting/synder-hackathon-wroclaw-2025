# BOOB - Back Office Operations Bots Solution

> Automate routine back-office operations with intelligent bots

> This isn’t a one-off bot for a single form. We built the **core of a back-office bot platform** that handles product cards, returns, expenses, supplier requests, and any other operational form with equal confidence.

Every back-office process is captured as a configuration: fields, types, mandatory logic, validation rules, data sources. On top sits a unified LLM layer that pulls data from integrations, assembles a structured answer, and returns a ready draft to the operator. The product-card bot is showcased as the **first module** on this platform, not the only use case.

### Why the Platform Beats "Just One Bot"

1. **Bridge operators and makers.** The platform connects non-technical back-office workers with their routine tasks and operational challenges to any technical specialist who can create AI bots on the Dify low-code platform. These specialists can solve problems or simplify routine work — from streamlining marketplace form filling and competitor insights to tax reports. Built bots become products that can be sold on our platform.
2. **Unified form model.** Any form lives in a single format: fields → type → required → validation rules → AI hints. The core doesn't care whether it is a product form or a return — just different configurations.
3. **Reusable AI stack.** One LLM layer handles prompting, structured JSON output, validation, logging. To launch a new bot you describe the form, connect data sources, and lightly tailor the prompt.
4. **Process scalability.** Today we demo product onboarding. Tomorrow returns, supplier requests, expenses. The architecture already lets us "stamp" bots via configuration instead of rewriting projects.
5. **Single operator workspace.** All back-office bots live in one interface: today the operator onboards products, tomorrow files a return, next week prepares an expense report — without system hopping.

### How It Lands in the Business Story

> For the business this is a **platform play**: integrate with data once, sign off security and access once, then spin up new processes without heavy rollouts. Each incremental use case gets cheaper and the roadmap stays predictable.

**The foundation already runs.** During the hackathon we shipped the platform core for product onboarding: forms are configuration-driven, the backend is field-agnostic, the LLM layer is universal. New bots land on the same foundation without rewriting the system.

> Our “form filler” isn’t a script for one scenario but the **first brick of an ecosystem of back-office bots** that strip routine from the entire operational cycle.

This is a submodule of the main repository: [BOBHack](git@github.com:Fl0p/BOBHack.git)

## Getting Started

### Initialize and Pull Submodule

If you cloned the main repository without submodules:

```bash
# Initialize submodule
git submodule init

# Pull submodule content
git submodule update
```

Or in one command:

```bash
git submodule update --init --recursive
```

To clone the main repository with all submodules at once:

```bash
git clone --recursive git@github.com:Fl0p/BOBHack.git
```

To update submodule to the latest commit:

```bash
git submodule update --remote
```

## About

Created during **synder-hackathon-wroclaw-2025** hackathon, this project provides a comprehensive platform for creating and managing intelligent bots to automate back-office operations.

## Team

- [Fl0p](https://github.com/Fl0p)
- [itbeard](https://github.com/itbeard)
- [gamezovladislav](https://github.com/gamezovladislav)

## Technology Stack

**AI Engine:** [Dify.ai](https://dify.ai/) - Production-ready AI Agent platform for building agentic workflows, RAG pipelines, and intelligent automation.

- **Backend:** Node.js + Express + TypeScript
- **Frontend:** React + Vite + TypeScript
- **Browser Extension:** JavaScript
- **Database:** PostgreSQL
- **Package Manager:** Yarn 4.10.3 with workspaces
- **Networking:** Cloudflare Tunnel
- **Containerization:** Docker (all services in a single yamlИ)
- **CI/CD:** Automated deployment pipeline
- **Documentation:** AI-generated documentation

## Demo

Check out the live demo: [https://bob.aignite.pl/](https://bob.aignite.pl/)

## Features

- Intelligent bot creation and management
- Automated back-office operations
- Auto-fill forms functionality
- AI-powered workflow automation
- Plug-and-play support for any LLM
- Integration with multiple systems
- Google OAuth2 authentication
- Easy-to-use interface

---

*Built with ❤️💀🤖 during synder-hackathon-wroclaw-2025*

