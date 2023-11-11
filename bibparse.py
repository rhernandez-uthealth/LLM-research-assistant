import bibtexparser
import os
import re

def getvalue(value):
    findit = re.findall("`(.*?)`", str(value))
    return findit[1]

def zot_bibparser(dir):
    outdict=[]
    dirpath = './zotero_libraries/{}/'.format(dir)
    zotbib = './zotero_libraries/{}/{}.bib'.format(dir, dir)
    library = bibtexparser.parse_file(zotbib)
    for i in range(0, len(os.listdir(dirpath+"/files/"))):
        entry = library.entries[i].fields_dict
        # print(entry.keys())
        tempdict = {
            'author':re.sub('[^0-9a-zA-Z]+', ', ', getvalue(entry['author'])),
            'year':getvalue(entry['year']),
            'file_path':dirpath+getvalue(entry['file'])
        }
        try:
            tempdict['citation']="{}, {}".format(tempdict['author'].split(',')[0], tempdict['year'])
            tempdict['abstract']=getvalue(entry['abstract'])
        except:
            tempdict['citation']="{}, {}".format(tempdict['author'].split(',')[0], tempdict['year'])
            tempdict['abstract']='not found'
           
        outdict.append(tempdict)
    return outdict

def main(dir):
    return zot_bibparser(dir)