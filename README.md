# TimelineKGQA

# Development Setup

## Installation

```bash
# cd to current directory
cd TimelineKGQA
python3 -m venv venv
pip install -r requirements.txt
# if you are doing development
pip install -r requirements.dev.txt

# and then install the package
pip install -e .
```

## Usage

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
python3 -m TimelineKGQA.generator --paraphrase True

```

## Folder Structure

```bash
TimelineKGQA/
├── TimelineKGQA/
│   ├── __init__.py
│   ├── generator.py
│   ├── processor.py
│   └── utils.py
├── tests/
│   ├── __init__.py
│   ├── test_generator.py
│   └── test_processor.py
├── docs/
│   └── ...
├── examples/
│   └── basic_usage.py
├── setup.py
├── requirements.txt
├── README.md
└── LICENSE
```

