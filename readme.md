# Newsagent: News Article Processing and Analysis System (ACL 2026 findings)
Official code of the paper Newsagent: News Article Processing and Analysis System. 

## Overview
Newsagent is a benchmark and framework for evaluating how large language models (LLMs) and agentic systems can perform real-world newswriting tasks. The system simulates the workflow: given a news title, release date, and initial firsthand data, agents must:
1. Identify narrative perspectives
2. Search historical content (time-aware retrieval)
3. Insert/remove contextual evidence
4. Rephrase drafts into final news articles
## Setup
- Build environment
    ```
    conda env create -f environment.yml
    ```
- Dataset

    Our dataset on osf : https://osf.io/nq83p/overview?view_only=c027289281964472aed2b8122ca46acc.
    To run the code:
    1. Download ```report_dataset.zip```
    2. Unzip to obtain ```report_dataset.json```
    3. Place it under the root directory ```/Newsagent```

- Set API key
    ```
    export OPENAI_API_KEY="your_key_here"
    export DEEPINFRA_API_KEY_1="your_key_here"
    export DEEPINFRA_API_KEY_2="your_key_here"
    export DEEPINFRA_API_KEY_3="your_key_here"
    export GEMINI_API_KEY_1="your_key_here"
    export GEMINI_API_KEY_2="your_key_here"
    export GEMINI_API_KEY_3Y="your_key_here"
    ```

## Code structure

- Crawl News Data and Generate Dataset (If you only want to test ReAct flow and Evaluation, download the dataset above and skip this section.)

    - Crawl data
    ```bash
    # Crawl AP News articles from 2025, create `Crawl_data/APNews_output/`
    python Crawl_code/APNews_crawler.py

    # Crawl BBC News articles from 2025, , create `Crawl_data/BBC_output/` 
    python Crawl_code/bbc_crawler.py

    # Collect June/July articles from both sources
    python Generate_json/collect.py

    # Check date ranges in crawled data, create `Crawl_data/june_july_news/`
    python Generate_json/get_date_range.py
    ```


    - Process articles through GPT to extract structured information
    ```bash
    # Process articles and extract Report_info, Firsthand_Information, Historical_Information, create `_data_june_july.json`
    python Generate_json/request.py
    ```

    - Combine and tokenize the data:

    ```bash
    # Filter for English articles only
    python Statistic/filter_english_news.py

    # Optionally rewrite historical information for parallel data
    python Statistic/rewrite_historical_info.py

    # Combine and tokenize all data, create `report_dataset.json`
    python Statistic/tokenize_and_combine_json.py

    # Generate 'historical_search_results.json' for evalauation
    python Statistic/semantic_search_historical_parallel.py
    ```

- 1-step and 2-step ReAct flow

    ```bash
    # Run 1-step ReAct (processes articles 0-100)
    python react/react_1_step.py

    # Run 2-step ReAct
    python react/react_2_step.py

    # Run rule-based approach 
    python react/rule_base.py
    ```

- Evaluation

    ```bash
    # Full pairwise evaluation of all models, results in evaluation/LLM_eval
    python evaluation/LLM_evaluation.py

    # F1 score evaluation for search and retrieval for 1-step ReAct, results in evaluation/1_step_eval
    python evaluation/1_step_evaluation.py

    # F1 score evaluation for search and retrieval for 2-step ReAct, results in evaluation/2_step_eval
    python evaluation/2_step_evaluation.py

    # Analysis of raw evaluation outputs, results in evaluation/LLM_eval/analysis
    python evaluation/anal_raw.py
    ```

## View of Dataset:
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

