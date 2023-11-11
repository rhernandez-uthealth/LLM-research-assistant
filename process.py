import numpy as np
import chromadb
import os
from chromadb.config import Settings
import spacy
import bibparse
from pypdf import PdfReader
from langchain.vectorstores import Chroma
from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.text_splitter import RecursiveCharacterTextSplitter
from stqdm import stqdm
# Retrieve OpenAI api-key from text file
import re

# PDF reader function
def readPDF(filename):
    reader = PdfReader(filename)
    doctext = ''
    for page in reader.pages:
        doctext+=page.extract_text()
    return doctext.replace('\n', '')

# Splitter function which splits text from articles to 1000-character chunks, with 200 overlapping
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=200)

# Functions for reducing chunks containing irrelevant information using Spacy natural language processing
# /// English-language nlp model to categorize textual content
nlp = spacy.load('en_core_web_sm')


# /// Count the number of sentence-entities recognized as "persons" or "organizations"; (ents)
def ent_count(chunk):
    sents = nlp(chunk)
    ents = sents.ents
    entity_count=len([e for e in ents if e.label_=="PERSON"])+len([e for e in ents if e.label_=="ORG"])
    return entity_count

# /// Reduce the initial list of chunks with counts of persons/organizations higher than the mean counts of persons/organizations+ 1 standard-deviation of counts among all documents' chunks
# // (ents) > (mean(ents)+1*standard-deviation(ents))
def ent_cutoff(chunks):
    ent_count_list=[ent_count(chunk) for chunk in chunks]
    cutlevel = np.mean(ent_count_list)+np.std(ent_count_list)
    filtered = [chunk for chunk in chunks if ent_count(chunk)<cutlevel]
    return filtered

def delete_multiple_element(list_object, indices):
    indices = sorted(indices, reverse=True)
    for idx in indices:
        if idx < len(list_object):
            list_object.pop(idx)


def main(project_name, DIRECTORY, OPENAI_API_KEY):
    print("Enter the name of the Zotero library export (using Better-Bibtext)")
    bibdata = bibparse.main(project_name)
    embeddings=OpenAIEmbeddings(openai_api_key=OPENAI_API_KEY, model="text-embedding-ada-002")
    import re
    import pandas as pd
    for i in stqdm(range(0, len(bibdata))):
        meta = bibdata[i]
        metadata=[]
        text = readPDF(meta['file_path'])
        text = re.split(r'(?i)abstract', text)[-1]
        chunks = text_splitter.split_text(text)
        reduced_chunks = ent_cutoff(chunks)
        for n, chunk in enumerate(chunks):
            meta['text']=chunks[n]
            meta['id'] = "ID-{}-{}".format(str(i),str(n))
            metadata.append(dict(meta)) 
        omissions = []
        for index, value in enumerate(chunks):
            if value not in reduced_chunks:
                omissions.append(index)
        delete_multiple_element(chunks, omissions)
        delete_multiple_element(metadata, omissions)
        vector_index = Chroma.from_texts(
            texts=chunks, 
            embedding=embeddings, 
            persist_directory=DIRECTORY, 
            metadatas=metadata
            )
    print("Database created from {} at {}".format(len(bibdata), DIRECTORY))