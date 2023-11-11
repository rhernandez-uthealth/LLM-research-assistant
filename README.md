# LLM-research-assistant
 A python application leveraging ChatGPT to generate long-form responses using a Chroma database of content extracted from academic articles

 This application reads a Zotero collection exported using BetterBibtex to create a ChromaDB database which may be queried to retrieve text-similar-matches, interpreted and communicated using OpenAI ChatGPT-3.5-turbo generative ai Large Language Model (llm)

# Prerequisites:
 Anaconda - https://www.anaconda.com/download/
 
 Zotero - https://www.zotero.org
 
 Zotero add-on, BetterBibtex - https://github.com/retorquere/zotero-better-bibtex/releases


# Install:
Create Python 3.10 environment
```bash
conda create -n LLM-research-helper python=3.10
activate LLM-research-helper
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
pip install https://github.com/explosion/spacy-models/releases/download/en_core_web_sm-1.2.0/en_core_web_sm-1.2.0.tar.gz
```

# Usage:
Export your Zotero collection to the ./zotero_libraries/ folder
[](./images/ExportCollection.png)

