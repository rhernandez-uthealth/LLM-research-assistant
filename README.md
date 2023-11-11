# LLM-research-assistant
 A python application leveraging ChatGPT to generate long-form responses of content extracted from academic articles (PDF)

 This application reads a Zotero collection of academic articles exported using BetterBibtex to create a ChromaDB database which may be queried to retrieve text-similar-matches. Each article is seperated into 1000 character "chunks" and parsed using natural language processing using the python Spacy library to remove content other than the article's main text. Each query retrieves the 10 most closely-matched chunks and interprets the retrieval using OpenAI ChatGPT-3.5-turbo generative-ai Large Language Model (llm).

 

# Prerequisites:
 Anaconda - https://www.anaconda.com/download/
 
 Zotero - https://www.zotero.org
 
 Zotero add-on, BetterBibtex - https://github.com/retorquere/zotero-better-bibtex/releases  (Note that the parent items in Zotero must have the correct metadata. If you've tried uploading a PDF to your Zotero collection, right click the file in Zotero, click "Create parent item...", and copy and paste the DOI at the top of the article in the pop-up)

 OpenAI API-key - https://platform.openai.com/api-keys  (Note that you must have a paid OpenAI account and use their API key)

# Install:
Copy your OpenAI API key from  https://platform.openai.com/api-keys, open "keys.txt" and paste your key between the quotations

Create Python 3.10 environment
```bash
conda create -n LLM-research-helper python=3.10
conda activate LLM-research-helper
```
Clone this repository
```bash
# Clone this repository
git clone https://github.com/rhernandez-uthealth/LLM-research-assistant.git
cd papermark
```
Install dependencies
```bash
pip install -r requirements.txt
pip install spacy
python -m spacy download en

```

# Usage:

Export your Zotero collection to the ./zotero_libraries/ folder:

 ![](/images/ExportCollection.png)

Export the collection as BetterBibtex likeso:

 ![](/images/BetterBibtex.png)

Start up the program:

 ```bash
 # In the main directory containing "app.py":
 conda activate LLM-research-helper
 streamlit run app.py
 ```

A webpage should open automatically. In the "CreateDB" page, enter the name of the exported Zotero collection and the name of the database you would like to create. Click "CreateDB" to create the database:
Create the database:

 ![](/images/CreateDB_interface.png)
 
Load the database and query the articles:

 ![](/images/QAInterface.png)


