# AutoDevFlow Orchestrator

An AI agent that creates full-stack applications from UI screenshots and natural language specifications using research-backed capabilities.

## Overview

AutoDevFlow combines:
- **AI UI Builder**: Screenshot → React/Tailwind components
- **Backend Automation Paper2Code**: Research papers → FastAPI endpoints
- **End-to-end orchestration**: Complete runnable applications

## Architecture

```
autodevflow/
├─ agent/                 # orchestration
│  ├─ tools/              # tool wrappers
│  │  ├─ vision_detect.py
│  │  ├─ ocr.py
│  │  ├─ ui2code.py
│  │  ├─ nl2api.py
│  │  ├─ quality.py
│  │  ├─ doc_gen.py
│  │  └─ file_ops.py
│  ├─ planner.py          # high-level task planner + DAG
│  ├─ router.py           # tool selection policy
│  └─ memory.py           # RAG & scratchpad
├─ models/
│  ├─ maskrcnn/           # weights & config
│  ├─ pix2code/
│  └─ codet5/             # tokenizer, adapters, LoRA
├─ datasets/
│  ├─ rico/               # UI screenshots + metadata
│  └─ ui_annotations/     # COCO-format labels
├─ services/
│  ├─ backend/            # FastAPI app generator outputs
│  └─ frontend/           # React app generator outputs
├─ tests/
│  ├─ unit/
│  └─ e2e/
└─ docker/
   ├─ docker-compose.yml
   └─ Dockerfile
```

## Capabilities

1. **Vision Detection**: Mask R-CNN for UI component detection
2. **OCR**: Scene text recognition from screenshots
3. **UI2Code**: pix2code-style React/Tailwind generation
4. **NL2API**: CodeT5+ for FastAPI endpoint generation
5. **Code Quality**: CodeBERT + linters for validation
6. **Documentation**: API spec → natural language docs
7. **Packaging**: Docker Compose deployment

## Quick Start

```bash
# Setup
python setup_autodevflow.py

# Run orchestrator
python -m autodevflow.agent.planner --input screenshot.png --spec "Create login system"

# Deploy
docker-compose up --build
```

## Integration Points

- **AI UI Builder**: `/ai-ui-builder/backend/` for existing UI generation
- **Paper2Code**: `/backend-automation-paper2code/` for research-backed code generation
- **Research Papers**: `/backend-automation-paper2code/Papers/mypapers/frontend/` for capabilities