# Newsagent: News Article Processing and Analysis System

Our dataset on osf : https://osf.io/nq83p/overview?view_only=c027289281964472aed2b8122ca46acc

Download the zip file `report_dataset.zip` and unzip it to get the dataset `report_dataset.json`.
Place the dataset file `report_dataset.json` under the main folder `/Newsagent`.

Newsagent is a benchmark and framework for evaluating how large language models (LLMs) and agentic systems can perform real-world newswriting tasks. The system simulates the workflow: given a news title, release date, and initial firsthand data, agents must:
1. Identify narrative perspectives
2. Search historical content (time-aware retrieval)
3. Insert/remove contextual evidence
4. Rephrase drafts into final news articles

view of dataset:
```
{
'0':
{
    "Title": "Harvey Weinstein is back on trial in New York. Jury selection begins Tuesday.",
    "Firsthand_Information": (
        "Firsthand_Information": {
            "Speaker": [
                {
                    "Speaker": "Gloria Allred",
                    "Text": "It’s painful, to go through the process again about a traumatic event.",
                    "Citation": {
                        "Paragraph": 5,
                        "StartChar": 151,
                        "EndChar": 207
                    },
                    "Encdoe":[]
                },
                {
                    "Speaker": "Lindsay Goldbrum",
                    "Text": "She is one of the bravest, strongest women that I have ever had the pleasure of knowing.",
                    "Citation": {
                        "Paragraph": 9,
                        "StartChar": 40,
                        "EndChar": 98
                    },
                    "Encdoe":[]
                }
            ],
            "Description": [
                {
                    "Description": "Prosecutors have also added a new accuser in the retrial.",
                    "Citation": {
                        "Paragraph": 9,
                        "StartChar": 0,
                        "EndChar": 76
                    },
                    "Encdoe":[]
                }
            ],
            "Image": []
        },
    )
}
}
```

## Project Structure

```
Newsagent/
├── Crawl_code/           # Web crawling and data collection
├── evaluation/           # Model evaluation and comparison
├── Generate_json/        # Data preprocessing and JSON generation
├── react/               # ReAct-based news generation system
├── Statistic/           # Data analysis and statistics
├── report_dataset.json
└── README.md
```

## Complete Execution Flow

### Step 1: Crawl News Data

First, crawl news articles from BBC and AP News:

```bash
# Crawl AP News articles from 2025
python Crawl_code/APNews_crawler.py

# Crawl BBC News articles from 2025  
python Crawl_code/bbc_crawler.py
```

This creates:
- `APNews_output/` - AP News articles with images and metadata
- `bbc_output/` - BBC articles with images and metadata

### Step 2: Collect and Filter Articles

Collect June and July articles and renumber them:

```bash
# Collect June/July articles from both sources
python Generate_json/collect.py

# Check date ranges in crawled data
python Generate_json/get_date_range.py
```

This creates `Crawl_data/june_july_news/` with sequentially numbered articles.

### Step 3: Generate Structured Data

Process articles through GPT to extract structured information:

```bash
# Process articles and extract Report_info, Firsthand_Information, Historical_Information
python Generate_json/request.py
```

This creates `_data_june_july.json` with structured article data.

### Step 4: Create Final Dataset

Combine and tokenize the data:

```bash
# Filter for English articles only
python Statistic/filter_english_news.py

# Optionally rewrite historical information for parallel data
python Statistic/rewrite_historical_info.py

# Combine and tokenize all data
python Statistic/tokenize_and_combine_json.py
```

This creates `report_dataset.json` - the main dataset for the ReAct system.

## Running the ReAct Systems

### Single-Step ReAct Approach

```bash
# Set your LLM provider and API keys
export LLM_PROVIDER="DEEPINFRA"  # or "GPT" 
export LLM_MODEL="google/gemma-3-27b-it"  # or your preferred model

# Run single-step ReAct (processes articles 0-100)
python react/react_1_step.py
```

- Single prompt for all actions (search, insert, remove, modify)
- Generates `1_step_[model]/` with draft reports

### Two-Step ReAct Approach

```bash
# Set your LLM provider and API keys
export LLM_PROVIDER="DEEPINFRA"
export LLM_MODEL="Qwen/Qwen3-32B"

# Run two-step ReAct (processes specific article ranges)
python react/react_2_step.py
```

- Separate specialized prompts for search, insert, and remove actions
- Generates `2_step_[model]/` with draft reports

### Rule-Based Alternative

```bash
# Run rule-based approach (no LLM calls, faster)
python react/rule_base.py
```
- Automated query generation from article content
- Direct semantic search with score thresholds
- No LLM intervention - predictable results
- Generates `rule_base/`

## Evaluation System Differences

### 1. `LLM_evaluation.py` - Comprehensive Model Comparison

**Purpose:** Full pairwise evaluation of all models
```bash
python evaluation/LLM_evaluation.py
```
- Compares 9+ models in round-robin fashion
- 6 main evaluation dimensions (Factual Consistency, Logical Consistency, etc.)
- Uses GPT-4o as judge for automated evaluation
- Generates win/loss matrices and summary statistics
- Supports checkpointing and resume functionality

**Output:** Complete evaluation results in `eval_results/`

### 2. `2_step_evaluation.py.py` - Search Quality Metrics

**Purpose:** F1 score evaluation for search and retrieval
```bash
python evaluation/2_step_evaluation.py
```

- Calculates precision, recall, and F1 scores
- Compares search strategies across models
- Focuses on historical information overlap
- Evaluates search quality, not content quality

**Output:** F1 scores and overlap metrics

### 3. `1_step_evaluation.py` - ReAct-Specific Evaluation

**Purpose:** Enhanced evaluation for ReAct systems
```bash
python evaluation/1_step_evaluation.py
```

- Handles both old and new ReAct output schemas
- Enhanced text extraction from various data structures
- Action-specific performance tracking
- Better handling of ReAct-specific data formats

**Output:** ReAct-optimized evaluation metrics

### 4. `anal_raw.py` - Raw Result Analysis

**Purpose:** Analysis of raw evaluation outputs
```bash
python evaluation/anal_raw.py --outdir eval_results
```

- Processes raw judge JSON files
- Counts wins/losses/ties per dimension
- Generates per-model performance statistics
- Creates CSV files for further analysis

**Output:** Processed statistics and CSV files

## Quick Start Workflow

```bash
# 1. Crawl data
python Crawl_code/APNews_crawler.py && python Crawl_code/bbc_crawler.py

# 2. Process data
python Generate_json/collect.py && python Generate_json/request.py

# 3. Create dataset
python Statistic/filter_english_news.py && python Statistic/tokenize_and_combine_json.py

# 4. Run ReAct
python react/react_1_step.py

# 5. Evaluate results
python evaluation/LLM_evaluation.py
python evaluation/1_step_evaluation.py
python evaluation/2_step_evaluation.py
```

## Configuration

### Environment Variables
```bash
export LLM_PROVIDER="DEEPINFRA"  # GPT, DEEPINFRA
export LLM_MODEL="google/gemma-3-27b-it"
export LLM_CONCURRENCY="3"
export EVAL_CONCURRENCY="3"
export OPENAI_API_KEY="your_key_here"
```

### Supported Models
- **OpenAI:** GPT-4o, GPT-4o-mini
- **DeepInfra:** Google Gemma, Qwen, Meta Llama models

## Dependencies

```bash
pip install fundus sentence-transformers openai pandas matplotlib ijson
pip install torch transformers scipy numpy langdetect requests
```
