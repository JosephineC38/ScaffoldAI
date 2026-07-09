# ScaffoldAI
## Installation 
First, install the requirements.

```
pip install -r requirements.txt
# or
python -m pip install -r requirements.txt
```

To run the app on your browser. You must have an OpenAI API key to use the chatbot features.
```
python -m streamlit run prototype\app.py 
# or
streamlit run prototype\app.py 
```

## OpenAI API Key
* https://platform.openai.com/api-keys -> Sign in -> Create New Secret Key 
    * Copy and save your Secret Key because you can't access it after the popup
    * You need at least $5 in your OpenAI account 
    * https://platform.openai.com/settings/organization/billing/overview -> To add money into your OpenAI account.
      
## Enviroment Variable
* Create an .env file in your directory
* Add the line OPENAI_API_KEY={KEY}
  * Replace {KEY} with your own OpenAI API Key
