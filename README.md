# TimelineKGQA++

TimelineKGQA is an improved version of TimelineKGQA. This repository is based on [the original TimelineKGQA work of Sun et. al](https://github.com/PascalSun/TimelineKGQA).


# Development Setup

## Installation

If you have uv, you can simply use one of these line:

```bash
# torch cuda 12.8 version
uv sync --extra cuda128
# torch rocm 6.4 version
uv sync --extra rocm64
# torch cpu version
uv sync --extra cpu
```

If you need the development dependencies:

```sh
uv sync --dev
```

If you are doing development, you will also need a database to store the knowledge graph.

```bash
# spin up the database
docker-compose up -d

# After this we need to load the data

# for ICEWS
# first, one needs to download the raw ICEWS data from
# - ICEWS Coded Event Data: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/28075
#   should be placed under data/ICEWS/ICEWS Coded Event Data/
# ICEWS Dictionaries: https://dataverse.harvard.edu/dataset.xhtml?persistentId=doi:10.7910/DVN/28118
#   should be placed under data/ICEWS/ICEWS Dictionaries/ 
# then, we can use 
source venv/bin/activate
# this will load the icews data into the database
python3 -m TimelineKGQA.data_loader.load_icews --mode load_data --data_name all
# this will create the unified knowledge graph
python3 -m TimelineKGQA.data_loader.load_icews --mode actor_unified_kg

# this will generate the question answering pairs
export OPENAI_API_KEY=sk-proj-xxx
python3 -m TimelineKGQA.generator --paraphrased
```


# RAG-only baseline 

See `python -m TimelineKGQA.rag.inference --help` for details.

```sh
python -m TimelineKGQA.rag.inference --preprocess --benchmark naive
```
