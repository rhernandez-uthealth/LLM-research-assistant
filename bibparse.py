import bibtexparser
import os
import re

def getvalue(value):
    try:
        findit = re.findall("`(.*?)`", str(value))
        found = findit[1]
    except:
        found = ""
    return found

def zot_bibparser(dir):
    outdict=[]
    dirpath = './zotero_libraries/{}/'.format(dir)
    zotbib = './zotero_libraries/{}/{}.bib'.format(dir, dir)
    library = bibtexparser.parse_file(zotbib)
    for i in range(0, len(os.listdir(dirpath+"/files/"))):
        print(i)
        entry= library.entries[i].fields_dict
        tempdict = {
            'author':re.sub('[^0-9a-zA-Z]+', ', ', getvalue(entry.get('author', 'missing'))),
            'year':getvalue(entry.get('year',"")),
            'file_path':dirpath+getvalue(entry.get('file','missing'))
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