# ScaffoldAI

Prototype Architecture
your_project/
│
├── app.py                      # Main Streamlit application
├── requirements.txt            # Package dependencies (streamlit, etc.)
│
├── prototype/                  # Initial scratchpads and experiments
│   └── sandbox.py
│
├── thermo_pack/                # Core thermodynamic physics & calculations
│   └── __init__.py
│
├── lit_review/                 # Academic papers, references, and notes
│   └── documentation.md
│
├── instruments/                # Hardware interfacing or data ingestion modules
│   └── __init__.py
│
└── eval/                       # Evaluation scripts, logs, and metrics
    └── logs/                   # Directory where local CSV/JSON will be saved

## Installation 
First, install the requirements

```
pip install -r requirements.txt
# or
python -m pip install -r requirements.txt
```

To run the app on your browser
```
python -m streamlit run prototype\app.py 
# or
streamlit run prototype\app.py 
```

## OpenAI Key
* https://platform.openai.com/api-keys -> Sign in -> Create New Secret Key 
    * Copy and save your Secret Key because you can't access it after the popup
    * You need at least $5 in your OpenAI account 
    * https://platform.openai.com/settings/organization/billing/overview -> To add money into your OpenAI account.