# Newsagent: News Article Processing and Analysis System

## Overview

Newsagent is a comprehensive system for crawling, processing, analyzing, and evaluating news articles. The project focuses on news articles from BBC and AP News, with capabilities for semantic search, historical information retrieval, and automated news report generation using various AI models.

## Project Structure

```
Newsagent/
├── Crawl_code/           # Web crawling and data collection
├── evaluation/           # Model evaluation and comparison
├── Generate_json/        # Data preprocessing and JSON generation
├── react/               # ReAct-based news generation system
├── Statistic/           # Data analysis and statistics
└── README.md
```

## Complete Execution Flow

### Step 1: Crawl News Data

First, crawl news articles from BBC and AP News:

```bash
cd Crawl_code

# Crawl AP News articles from 2025
python APNews_crawler.py

# Crawl BBC News articles from 2025  
python bbc_crawler.py
```

This creates:
- `APNews_output/` - AP News articles with images and metadata
- `bbc_output/` - BBC articles with images and metadata

### Step 2: Collect and Filter Articles

Collect June and July articles and renumber them:

```bash
cd Generate_json

# Collect June/July articles from both sources
python collect.py

# Check date ranges in crawled data
python get_date_range.py
```

This creates `Crawl_data/june_july_news/` with sequentially numbered articles.

### Step 3: Generate Structured Data

Process articles through GPT to extract structured information:

```bash
cd Generate_json

# Process articles and extract Report_info, Firsthand_Information, Historical_Information
python request.py
```

This creates `_data_june_july.json` with structured article data.

### Step 4: Create Final Dataset

Combine and tokenize the data:

```bash
cd Statistic

# Filter for English articles only
python filter_english_news.py

# Optionally rewrite historical information for parallel data
python rewrite_historical_info.py

# Combine and tokenize all data
python tokenize_and_combine_json.py
```

This creates `report_dataset.json` - the main dataset for the ReAct system.

## Running the ReAct Systems

### Single-Step ReAct Approach

```bash
cd react

# Set your LLM provider and API keys
export LLM_PROVIDER="DEEPINFRA"  # or "GPT" or "GEMINI"
export LLM_MODEL="google/gemma-3-27b-it"  # or your preferred model

# Run single-step ReAct (processes articles 0-100)
python react_1_step.py
```

**Features:**
- Single prompt for all actions (search, insert, remove, modify)
- Up to 20 query iterations per article
- Supports GPT, DeepInfra providers
- Generates `output_async_react_[model]/` with draft reports

### Two-Step ReAct Approach

```bash
cd react

# Set your LLM provider and API keys
export LLM_PROVIDER="DEEPINFRA"
export LLM_MODEL="Qwen/Qwen3-32B"

# Run two-step ReAct (processes specific article ranges)
python react_2_step.py
```

**Features:**
- Separate specialized prompts for search, insert, and remove actions
- Better action detection and execution
- Supports GPT, DeepInfra, and Gemini providers
- Generates `output_async_100_[model]/` with draft reports

### Rule-Based Alternative

```bash
cd react

# Run rule-based approach (no LLM calls, faster)
python rule_base.py
```

**Features:**
- Automated query generation from article content
- Direct semantic search with score thresholds
- No LLM intervention - predictable results
- Generates `output_async_react_rule/`

## Evaluation System Differences

### 1. `gpt_evaluation.py` - Comprehensive Model Comparison

**Purpose:** Full pairwise evaluation of all models
```bash
cd evaluation
python gpt_evaluation.py
```

**What it does:**
- Compares 9+ models in round-robin fashion
- 8 evaluation dimensions (Factual Consistency, Logical Consistency, etc.)
- Uses GPT-4o as judge for automated evaluation
- Generates win/loss matrices and summary statistics
- Supports checkpointing and resume functionality

**Output:** Complete evaluation results in `eval_results/`

### 2. `evaluate_f1.py` - Search Quality Metrics

**Purpose:** F1 score evaluation for search and retrieval
```bash
cd evaluation
python evaluate_f1.py
```

**What it does:**
- Calculates precision, recall, and F1 scores
- Compares search strategies across models
- Focuses on historical information overlap
- Evaluates search quality, not content quality

**Output:** F1 scores and overlap metrics

### 3. `evaluation_react.py` - ReAct-Specific Evaluation

**Purpose:** Enhanced evaluation for ReAct systems
```bash
cd evaluation
python evaluation_react.py
```

**What it does:**
- Handles both old and new ReAct output schemas
- Enhanced text extraction from various data structures
- Action-specific performance tracking
- Better handling of ReAct-specific data formats

**Output:** ReAct-optimized evaluation metrics

### 4. `anal_raw.py` - Raw Result Analysis

**Purpose:** Analysis of raw evaluation outputs
```bash
cd evaluation
python anal_raw.py --outdir eval_results
```

**What it does:**
- Processes raw judge JSON files
- Counts wins/losses/ties per dimension
- Generates per-model performance statistics
- Creates CSV files for further analysis

**Output:** Processed statistics and CSV files

## Key Differences Summary

| Evaluation File | Purpose | Scope | Judge | Output |
|----------------|---------|-------|-------|---------|
| `gpt_evaluation.py` | Full model comparison | All models, all dimensions | GPT-4o | Complete evaluation matrices |
| `evaluate_f1.py` | Search quality | Search/retrieval only | None | F1 scores and overlap metrics |
| `evaluation_react.py` | ReAct optimization | ReAct outputs only | None | ReAct-specific metrics |
| `anal_raw.py` | Raw data processing | Post-evaluation analysis | None | Statistics and CSV files |

## Quick Start Workflow

```bash
# 1. Crawl data
cd Crawl_code && python APNews_crawler.py && python bbc_crawler.py

# 2. Process data
cd Generate_json && python collect.py && python request.py

# 3. Create dataset
cd Statistic && python filter_english_news.py && python tokenize_and_combine_json.py

# 4. Run ReAct
cd react && python react_1_step.py

# 5. Evaluate results
cd evaluation && python gpt_evaluation.py
```

## Configuration

### Environment Variables
```bash
export LLM_PROVIDER="DEEPINFRA"  # GPT, DEEPINFRA, or GEMINI
export LLM_MODEL="google/gemma-3-27b-it"
export LLM_CONCURRENCY="3"
export EVAL_CONCURRENCY="3"
export OPENAI_API_KEY="your_key_here"
```

### Supported Models
- **OpenAI:** GPT-4o, GPT-4o-mini
- **DeepInfra:** Google Gemma, Qwen, Meta Llama models
- **Gemini:** Google's Gemini models

## Dependencies

```bash
pip install fundus sentence-transformers openai pandas matplotlib ijson
pip install torch transformers scipy numpy langdetect requests
```

## Research Applications

This system enables research in:
- **Automated News Generation** using ReAct reasoning
- **Content Quality Evaluation** across multiple dimensions
- **Model Comparison** through systematic evaluation
- **Semantic Search** for historical information retrieval
- **Multi-step Reasoning** in news generation tasks
