<div align="center">

# framedby.ms

### Technical Publications & Hands-on Labs

**From security concepts to reproducible experiments.**

[Explore the site](https://framedby.ms) · [Browse the first lab](https://framedby.ms/labs/authority-boundaries/) · [Share feedback](https://github.com/MANU-de/Fraimedby_ms/discussions) · [Report an issue](https://github.com/MANU-de/Fraimedby_ms/issues)

![Deploy GitHub Pages](https://github.com/MANU-de/Fraimedby_ms/actions/workflows/deploy-pages.yml/badge.svg)
![Verify site and lab](https://github.com/MANU-de/Fraimedby_ms/actions/workflows/verify.yml/badge.svg)
[![License: Apache-2.0](https://img.shields.io/badge/License-Apache--2.0-blue.svg)](LICENSE)

</div>

---

## Why framedby?

Security research is most useful when its assumptions, implementation, and observable behavior can be examined—not merely described.

**framedby.ms** is an evolving home for technical publications and locally runnable labs focused on AI security engineering. It connects research questions to small, inspectable experiments so readers can explore what a system permits, denies, or actually executes.

The platform is in **public preview**. The site and initial lab are available; additional content, interfaces, and community processes are under development. Feedback on both the concept and implementation is welcome.

## Explore the first verified lab

### Agent Authority Boundary Lab — v1.0.0

A deterministic exercise in authorization and tool execution. Predict the outcome, then verify three cases:

| Scenario | Expected behavior |
| --- | --- |
| Authorized read | Allowed; fixture returned; no writes |
| Unauthorized write | Denied before executor invocation; no writes |
| Duplicate authorized write | First delivery writes; repeat recognized as replay; one write total |

**Requirements:** Python 3.12+ and a terminal. Docker Compose is optional. The lab uses synthetic fixtures and can run offline after installation.

1. [Download the lab ZIP](https://framedby.ms/downloads/authority-boundaries-1.0.0.zip) and extract it.
2. Open a terminal in the **root of the extracted lab**.
3. Install its bundled framework and run verification:

```bash
python -m pip install ./framework/python
python -m framedby_lab verify examples/authority-boundaries
```

For installation isolation, use a Python virtual environment. See the lab's bundled README for its Docker instructions and [the interactive lab page](https://framedby.ms/labs/authority-boundaries/) for context, evidence, and the release checksum.

> **Scope:** This lab models sequential requests in a single process. It is not a production guarantee of exactly-once effects; durable state and concurrency controls are separate requirements.

## Research roadmap

The catalog also tracks planned investigations. **Planned does not mean implemented or verified.**

- Bypassing Guardrails via Indirect Multi-Turn Injection
- Steganographic Backdoors in SafeTensors Weights
- Automated Adversarial Token Optimization (AATO)
- System Prompt Extraction via Model Calibration Exploits
- Zero-Trust Proxy Gateway for Inference Endpoints
- Training Time Poisoning Mitigation Framework

See the current [public catalog](https://framedby.ms/#publications) for status updates.

## How this site works

This repository contains the **website and publication catalog**. A small Python build process renders static pages and copies verified lab downloads; GitHub Actions tests and publishes the result to GitHub Pages.

```text
content/
  labs.json              # Catalog entries, status, and lab metadata
  site.json              # Repository and site configuration
  downloads/             # Lab archives, SHA-256 digests, evidence
src/
  home.html              # Homepage template
  detail.html            # Lab detail template
  assets/                # CSS, JS, favicon, share image
build.py                 # Static site generator
tests/                  # Site and artifact validation
.github/workflows/       # Verification and deployment
```

### Build and validate locally

From the repository root with Python 3.13:

```bash
python build.py
python -m unittest discover -s tests -v
```

The generated site is written to `dist/`. Commits to `master` trigger GitHub Pages deployment; verification also runs for pull requests. The CI workflow additionally extracts the downloadable lab and executes its verification command.

## Join the conversation

**This project is being developed in the open.** Your feedback can help identify which experiments are useful, which instructions are unclear, and where the publishing experience needs improvement.

- **Questions, ideas, and general feedback:** [GitHub Discussions](https://github.com/MANU-de/Fraimedby_ms/discussions)
- **Bugs and reproducibility problems:** [GitHub Issues](https://github.com/MANU-de/Fraimedby_ms/issues/new)
- **Code or documentation improvements:** Open a pull request with a focused description and, when applicable, passing tests.

When reporting a lab reproduction, include the **lab version, operating system, Python version, executed command, expected result, and observed result**. Remove secrets, personal information, and sensitive logs before posting.

## License and project context

The repository includes the [Apache License 2.0](LICENSE). Check the license and notices bundled with individual downloadable artifacts as applicable.

framedby is part of the **NeuralStack | MS – AI Security Engineering Ecosystem**.

**Explore. Execute. Verify. Question.**
