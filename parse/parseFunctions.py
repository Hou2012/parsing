#!/usr/bin/env python
"""
coding=utf-8

Code Template

"""
# import logging
import os
import pandas
from lib import lib
#import textract
from werkzeug.utils import secure_filename
from field_extraction import field_extraction
#import spacy
# Import of get_docx_text
try:
    from xml.etree.cElementTree import XML
except ImportError:
    from xml.etree.ElementTree import XML
import zipfile
import datetime
try:
    from xml.etree.cElementTree import XML
except ImportError:
    from xml.etree.ElementTree import XML
import zipfile
# import for pdfminer
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfpage import PDFPage
from io import StringIO

import sys

WORD_NAMESPACE = '{http://schemas.openxmlformats.org/wordprocessingml/2006/main}'
PARA = WORD_NAMESPACE + 'p'
TEXT = WORD_NAMESPACE + 't'

def Parse(fileName, extension):
    print('hi')
    # print(downloaded_CV)
    """
    Main function 
    :input:PDF or Docx example: c:/Users/MBOUZIAN/Documents/projets/parsing-matching/data/input/example_resumes_fr/Cv_Houriya_Elrhayti_(1).pdf
    :return: JSON 
    :rtype: None
    """
    #logging.getLogger().setLevel(logging.INFO)
    observations = extract(fileName, extension) 
    observations = transform(observations)
    return observations
    #pass

def get_docx_text(fileName):
    """
    Take the path of a docx file as argument, return the text in unicode.
    """
    document = zipfile.ZipFile(fileName)
    xml_content = document.read('word/document.xml')
    print('xml_content', xml_content)
    document.close()
    tree = XML(xml_content)

    paragraphs = []
    for paragraph in tree.getiterator(PARA):
        texts = [node.text
                 for node in paragraph.getiterator(TEXT)
                 if node.text]
        if texts:
            paragraphs.append(''.join(texts))

    return '\n\n'.join(paragraphs)

def convertPDFToText(fileName):
    """
    The first two lines of logging is:
    It sets the root logger to level Error. This will stop PDFMiner warn logging, 
    since it logs to the root logger, but not your own logging.
    I needed to set propagation to False, because after PDFMiner usage, 
    I had duplicate logging entries. This was caused by the root logger.
    """ 
    #logging.propagate = False 
    #logging.getLogger().setLevel(logging.ERROR)
    rsrcmgr = PDFResourceManager()
    retstr = StringIO()
    codec = 'utf-8'
    laparams = LAParams()
    device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
    fp = open(fileName, 'rb')
    interpreter = PDFPageInterpreter(rsrcmgr, device)
    password = ""
    maxpages = 0
    caching = True
    pagenos=set()
    for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, password=password,caching=caching, check_extractable=True):
        interpreter.process_page(page)
    fp.close()
    device.close()
    string = retstr.getvalue()
    retstr.close()
    return string

def readFile(fileName):
        '''
        Read a file given its name as a string.
        Modules required: os
        UNIX packages required: antiword, ps2ascii
        '''
        extension = fileName.split(".")[-1]
        print('extension from readfile', extension)
        if extension == "txt":
            f = open(fileName, 'r')
            string = f.read()
            f.close() 
            return string
        elif extension == "doc":
            # Run a shell command and store the output as a string
            # Antiword is used for extracting data out of Word docs. Does not work with docx, pdf etc.
            return subprocess.Popen(['antiword', fileName], stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0], extension
        elif extension == "docx":
            try:
                return get_docx_text(fileName)
            except:
                return ''
        #elif extension == "rtf":
        #    try:
        #        return convertRtfToText(fileName), extension
        #    except:
        #        return ''
        #        pass
        elif extension == "pdf":
            # ps2ascii converst pdf to ascii text
            # May have a potential formatting loss for unicode characters
            # return os.system(("ps2ascii %s") (fileName))
            try:
                return convertPDFToText(fileName)
            except:
                return ''
        else:
            print ('Unsupported format')
            return ''



def extract(fileName, extension):
    #logging.info('Begin extract')

    # Reference variables
    candidate_file_agg = list()

    # # Create list of candidate files
    # for root, subdirs, files in os.walk(lib.get_conf('resume_directory')):
    #     folder_files = map(lambda x: os.path.join(root, x).replace("\\","/"), files)
    candidate_file_agg.append(fileName)
    # print(candidate_file_agg)

    # Convert list to a pandas DataFrame
    #logging.info('Found {} candidate files'.format(len(observations.index)))

    # Subset candidate files to supported extensions
    # observations = observations[observations['extension'].isin(lib.AVAILABLE_EXTENSIONS)]
    #logging.info('Subset candidate files to extensions w/ available parsers. {} files remain'.
                 #format(len(observations.index)))

    # Attempt to extract text from files
    #print('hello extension', extension)

    observations = pandas.DataFrame(data=candidate_file_agg, columns=['file_path'])
    observations['extension'] = observations['file_path'].apply(lambda x: os.path.splitext(x)[1])
    observations['text'] = observations['file_path'].apply(readFile)

    #print('hello again',  observations['text'])

    # Archive schema and return
    #lib.archive_dataset_schemas('extract', locals(), globals())
    #logging.info('End extract')
    return observations


def transform(observations):
    # TODO Docstring
    # logging.info('Begin transform')

    # Extract candidate name
    observations['candidate_name'] = observations['text'].apply(lambda x:field_extraction.getName(x)) #field_extraction.getName(x)


    # Extract contact fields
    observations['email'] = observations['text'].apply(lambda x: lib.term_match(x, field_extraction.EMAIL_REGEX))
    observations['phone'] = observations['text'].apply(lambda x: lib.term_match(x, field_extraction.PHONE_REGEX_FR))

    # Extract skills
    observations = field_extraction.extract_fields(observations)

    # Archive schema and return
    # lib.archive_dataset_schemas('transform', locals(), globals())
    # logging.info('End transform')
    return observations

# # load is to load the result of parsing on csv format
# def load(observations):
#     # logging.info('Begin load')
#     output_path = os.path.join(lib.get_conf('summary_output_directory'), 'resume_summary.csv').replace("\\","/")
#     output_path_json = os.path.join(lib.get_conf('summary_output_directory'), 'resume_summary.json')

#     # logging.info('Results being output to {}'.format(output_path))
#     # print('Results output to {}'.format(output_path))

#     observations.to_csv(path_or_buf=output_path, index_label='index', encoding='utf-8', sep=";")
#     observations.to_json(output_path_json, orient='records', lines=True)
#     # logging.info('End transform')
#     pass


if __name__ == '__main__':
#     # Map command line arguments to function arguments.
    resume = dict({
        'candidate_name': '', 
        'email': '', 
        'phone': '', 
      'Informations professionnelles': [], 
#         'platforms': [],  
#         'database': [], 
#         'programming':  [], 
#         'machinelearning': [], 
#         'universities': [], 
#         'languages': [], 
#         'hobbies': [], 
#         'open_source': [],
    })
            
    response = Parse('D:/pepit/parsing-matching/data/input/example_resumes_fr/DataValue - CV - HEL.pdf', 'pdf')
#     # result = response[0].to_dict('records')
    # print('result', response['candidate_name'])
    resume['candidate_name']=response['candidate_name']
    resume['email']=response['email']
    resume['phone']=response['phone']
    resume['Informations professionnelles']=response['Informations professionnelles']
    print(resume)
#     resume['experience']=response['experience']
#     resume['platforms']= response['platforms']
#     resume['database']=response['database']
#     resume['programming']=response['programming']
#     resume['machinelearning']=response['machinelearning']
#     resume['universities']=response['universities']
#     resume['languages']=response['languages']
#     resume['hobbies']=response['hobbies']
#     resume['open_source']=response['open-source']