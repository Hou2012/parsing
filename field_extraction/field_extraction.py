import logging

import warnings
warnings.filterwarnings(action='ignore', category=UserWarning, module='gensim') #to avoid this warning msg: warnings.warn("detected Windows; aliasing chunkize to chunkize_serial)

from gensim.utils import simple_preprocess

from lib import lib

import nltk # this is to process text document and look for person name

import re

try:
    nltk.data.find('tokenizers/punkt')
except:
    nltk.download('punkt')

try:
    nltk.data.find('tokenizers/averaged_perceptron_tagger')
except:
    nltk.download('averaged_perceptron_tagger')
EMAIL_REGEX = r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,4}"
PHONE_REGEX_US = r"\(?(\d{3})?\)?[\s\.-]{0,2}?(\d{3})[\s\.-]{0,2}(\d{4})" # this is a pattern for US phone number..i used for test
PHONE_REGEX_FR=r"\(*(?:(?:\+|00)33|0)\)*\s*[1-9](?:[\s.-]*\d{2}){4}"
#PHONE_REGEX_FR=r"(?:\+33|\(\+33\)|\(\+33\)\s|\+33\s|0)[1-9](?:(?:\.\d{2})(?:\.\d{2})(?:\.\d{2})(?:\.\d{2})|(?:\s\d{2})(?:\s\d{2})(?:\s\d{2})(?:\s\d{2})|\d{8})"

#nltk.download('punkt') # c'est à télécharger pour une fois: la première fois ou on appel le répertoire depuis main
#nltk.download('averaged_perceptron_tagger') # c'est à télécharger pour une fois: la première fois ou on appel le répertoire depuis main

def preprocess(document):
    '''
    Information Extraction: Preprocess a document with the necessary POS tagging.
    Returns three lists, one with tokens, one with POS tagged lines, one with POS tagged sentences.
    Modules required: nltk
    '''
    try:
        # Try to get rid of special characters: faut revoir cette partie qui peut poser des soucis 
        try:
            document = document.decode('utf-8', 'ignore')
        except:
            document = document.encode('utf-8', 'ignore')
        # Newlines are one element of structure in the data
        # Helps limit the context and breaks up the data as is intended in resumes - i.e., into points
        lines = [el.strip() for el in document.decode('utf-8', 'ignore').split("\n") if len(el) > 0]  # Splitting on the basis of newlines 
        lines = [nltk.word_tokenize(el) for el in lines]    # Tokenize the individual lines
        lines = [nltk.pos_tag(el) for el in lines]  # Tag them
        # Below approach is slightly different because it splits sentences not just on the basis of newlines, but also full stops 
        # - (barring abbreviations etc.)
        # But it fails miserably at predicting names, so currently using it only for tokenization of the whole document
        sentences = nltk.sent_tokenize(document.decode('utf-8', 'ignore'))    # Split/Tokenize into sentences (List of strings)
        sentences = [nltk.word_tokenize(sent) for sent in sentences]    # Split/Tokenize sentences into words (List of lists of strings)
        tokens = sentences
        sentences = [nltk.pos_tag(sent) for sent in sentences]    # Tag the tokens - list of lists of tuples - each tuple is (<word>, <tag>)
        # Next 4 lines convert tokens from a list of list of strings to a list of strings; basically stitches them together
        dummy = []
        for el in tokens:
            dummy += el
        tokens = dummy
        # tokens - words extracted from the doc, lines - split only based on newlines (may have more than one sentence)
        # sentences - split on the basis of rules of grammar
        return tokens, lines, sentences
    except Exception as e:
        print ('preprocess execption process', e) 
        return [], [], []

def getName(inputString, debug=False):
        '''
        Given an input string, returns possible matches for names. Uses regular expression based matching.
        Needs an input string, a dictionary where values are being stored, and an optional parameter for debugging.
        Modules required: clock from time, code.
        '''
        # Reads Indian Names from the file, reduce all to lower case for easy comparision [Name lists]
        # PeopleNames = open("../allNames/allNames.txt", "r").read().lower()
        # Lookup in a set is much faster
        #print('inputString////////////////////', inputString)
        PeopleNames='Mohamed Mehdi Mahdi Badr Sofia Othmane Bassma Yacine Houriya Rostand Nada Abderrahim SRIDHARAMURTY aabha aabharana aabheer aachman aadab aadarsh aadarshini aadepu aadesh aadhira aadhya aadi aadidev aadil aadinath aadit aadita aaditeya aaditiyaa aaditya aadrika aafreen aagam aagney aagneya'
        PeopleNames = set(PeopleNames.lower().split())
        
        #print('People Names', PeopleNames)
        #otherNameHits = []
        nameHits = []
        name = None

        try:
            tokens, lines, sentences = preprocess(inputString)
            # tokens, lines, sentences = tokens, lines, sentences
            # Try a regex chunk parser
            # grammar = r'NAME: {<NN.*><NN.*>|<NN.*><NN.*><NN.*>}'
            grammar = r'NAME: {<NN.*><NN.*><NN.*>*}'
            # Noun phrase chunk is made out of two or three tags of type NN. (ie NN, NNP etc.) - 
            # typical of a name. {2,3} won't work, hence the syntax
            # Note the correction to the rule. Change has been made later.
            chunkParser = nltk.RegexpParser(grammar)
            #print(chunkParser)
            all_chunked_tokens = []
            for tagged_tokens in lines:
                # Creates a parse tree
                if len(tagged_tokens) == 0: continue # Prevent it from printing warnings
                chunked_tokens = chunkParser.parse(tagged_tokens)
                all_chunked_tokens.append(chunked_tokens)
                for subtree in chunked_tokens.subtrees():
                    #  or subtree.label() == 'S' include in if condition if required
                    if subtree.label() == 'NAME':
                        for ind, leaf in enumerate(subtree.leaves()):
                            if leaf[0].lower() in PeopleNames and 'NN' in leaf[1]:
                                # Case insensitive matching, as PeopleNames have names in lowercase
                                # Take only noun-tagged tokens
                                # Surname is not in the name list, hence if match is achieved add all noun-type tokens
                                # Pick upto 3 noun entities
                                hit = " ".join([el[0] for el in subtree.leaves()[ind:ind+3]])
                                # Check for the presence of commas, colons, digits - usually markers of non-named entities 
                                if re.compile(r'[\d,:]').search(hit): continue
                                nameHits.append(hit)
                                # Need to iterate through rest of the leaves because of possible mis-matches
            # Going for the first name hit
            if len(nameHits) > 0:
                nameHits = [re.sub(r'[^a-zA-Z \-]', '', el).strip() for el in nameHits] 
                name = " ".join([el[0].upper()+el[1:].lower() for el in nameHits[0].split() if len(el)>0])
                # otherNameHits = nameHits[1:]
                return name

        except Exception as e:
            print ("Can't process or detect name")
            print ('exception in getName',e)
            return ''       

        #infoDict['name'] = name
        #infoDict['otherNameHits'] = otherNameHits

        # if debug:
        #     print ("\n", pprint(infoDict), "\n")
        #     code.interact(local=locals())
        # return name  


def extract_fields(df):
    for extractor, items_of_interest in lib.get_conf('Informations professionnelles').items():
        df[extractor] = df['text'].apply(lambda x: extract_skills(x, extractor, items_of_interest))
    for extractor, items_of_interest in lib.get_conf('Hard skills').items():
        if isinstance(items_of_interest, list) == False : 
           for item in items_of_interest:
               df[item] = df['text'].apply(lambda x: extract_skills(x, item, items_of_interest[item]))
        else : 
            #print("aaaa")
            #print(items_of_interest)
            df[extractor] = df['text'].apply(lambda x: extract_skills(x, extractor, items_of_interest))
    df.to_json('D:/pepit/parsing-matching/data/houriyaparsing.json')
    return df


def extract_skills(resume_text, extractor, items_of_interest):
    potential_skills_dict = dict()
    matched_skills = set()

    # TODO This skill input formatting could happen once per run, instead of once per observation.
    for skill_input in items_of_interest:

        # Format list inputs
        if type(skill_input) is list and len(skill_input) >= 1:
            potential_skills_dict[skill_input[0]] = skill_input

        # Format string inputs
        elif type(skill_input) is str:
            potential_skills_dict[skill_input] = [skill_input]
        else:
            logging.warn('Unknown skill listing type: {}. Please format as either a single string or a list of strings'
                         ''.format(skill_input))

    for (skill_name, skill_alias_list) in potential_skills_dict.items():

        skill_matches = 0
        # Iterate through aliases
        for skill_alias in skill_alias_list:
            # Add the number of matches for each alias
            skill_matches += lib.term_count(resume_text, skill_alias.lower())

        # If at least one alias is found, add skill name to set of skills
        if skill_matches > 0:
            matched_skills.add(skill_name)

    return matched_skills
