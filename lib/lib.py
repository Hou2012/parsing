"""
coding=utf-8
"""
import logging # just to print a logg info while error in try exception

import os
import pandas
import re
import yaml
import pickle

CONFS = {
    'resume_directory': 'D:/pepit/pep/parsing-matching/data/input/example_resumes',
    'summary_output_directory': 'D:/pepit/pep/parsing-matching/data/output',

'Informations professionnelles' :  
   
	{
		"Poste":[
         ['Data Scientist', 'data-scientist', 'data scientist'],
        ['developer', 'software developer', 'software engineer', 'dev', 'dévellopeur'],
        ['trader', 'traideur'],
        ['Consultant Fonctionnel', 'consultante' 'focntionnel', 'consultante' 'fonctionnel' 'ERP'],
        ['Consultant', 'Consultante'],
    ],
		"Langues": [
                'Espagnol',
                'English',
                 'German',
                  'Spanish',
                  ['Chinese', 'Mandarin'],
                  'Dutsh',
                  'Français',
                  'Anglais',
   ]	
   }, 
'Hard skills': 
	{
		"Formations":[['Centrale de Paris', 'ECP'],
                  ['Univerité de Rennes'],
                      ['Université Paris 11', 'université Paris-Saclay'],
                     ['Université de Nice Sophia Antipolis', 'Université de Nice-Sophia-Antipolis'],
                   'Supélec'],
		"Certification" : ["Udemy IA","Certification CGP", "Certification Cloudera"],
	
		"Technologie" : {
					"Bureautique" : ["word", "Excel","Powerpoint","PackOffice"],
					"Système d'exploitation / OS":[
                                 ['Linux', 'Ubuntu'],
                                 'Windows',
                                    ['Mac', 'MacOS']],
					"Base de données":[['SQL', 'SQL' 'SERVER'],
                     'MySQL',
                     ['Postgress', 'Postgresql'],
                        'Oracle'],
					"Langage de programmation":[['java', 'JavaEE'],
    'C',
    'C++',
    'C#',
    '.NET',
    'Matlab',
    'R',
    'python',
    'VHDL',
    'SAS'],
					
					
					"Langage de programmation web" : ['PHP',
    'JavaScript',
    ['React', 'ReactJS', 'React JS', 'react']],
					"Gestion de developpement" : ["github","bitbucket","gitlab", "sourceforge", 							"gitkraken"],
					"Analyse de qualité code" : ["Sonar"]
					}, 
		"BI" : {
				"ETL" : ["Talend", "Informatica"], 
				"ERP" : ["Oracle", "SAP"], 
				"Outils Data Viz" : ["Tableau",	['QlikView', 'qlikview'],	"Business Object"]
		         }, 
		"Big data": {
					 "Technologie Clouds": ["AWS","GCP","Azure"],
					 "Outils Big data" : ["Cassandra"	,"Hortonworks"	,"Hadoop","Elasticserach",	"Logstash",	"Kibana",	"Spark"	,"Hive"		,	"Hbase"	,"Docker","HDFS"	,"nifi",	"Kafka"	,"Biginsight"	,"Cloudera"],
					 "Outils Statistiques" : ["SPSS", "SAS"],
					 "Machine learning" : ["Spark-Mlib"	,"tensorflow"	,"keras"	,"PySpark",							"Pandas",	"Numpy",				"SKLearn"	,						"RNN",	"CNN"	,		"K-means"	,"CAH"	,							"Random forest"	,"Regression logistique"	,						"SVM"	,"Grid search",	"NLP",	"Web sraping"]
					}, 
		"Gestion de projet" : ["MS Project",	"UML",	"Scrum"	,"Cycle en V"],
		"Conseil" : ["Conduite au changement"	,"conseil"],
		"AMOA" : ["Redaction de spec",	"expression de besoin"	,"receuil de besoin" ,	"études d’opportunités et de faisabilités"	,	"Pilotage de projet ",	"études fonctionnelles" ,	"redaction des specifications"	,"communication ecrite"	,"communication orale",	"Analyse de l’existant" ,	"étude des besoins métier"	,"business case"	,"stratégie Recette"	,"Plan de recette"	,"Test"],
		"Loisirs" : [['Natation', 'swimming', 'swim'],
                   ['football', 'soccer'],
                  'painting',
                  'reading',
                  'tennis',
                   'Karaté',
                  ['jeux vidéo', 'video games', 'video game'],
                  'Voyage',
                     'basketball' ,
                  'volleyball' ,
                     'Musique',
                  'Lecture',]
		
	
}

}

AVAILABLE_EXTENSIONS = {'.csv', '.doc', '.docx', '.eml', '.epub', '.gif', '.htm', '.html', '.jpeg', '.jpg', '.json',
                        '.log', '.mp3', '.msg', '.odt', '.ogg', '.pdf', '.png', '.pptx', '.ps', '.psv', '.rtf', '.tff',
                        '.tif', '.tiff', '.tsv', '.txt', '.wav', '.xls', '.xlsx'} # it s possible to have all this extension yes sir


def load_confs(confs_path='../config/config.yaml'):
    # TODO Docstring
    global CONFS

    # if CONFS is None:
    #     try:
    #         CONFS = yaml.load(open(confs_path, encoding="utf-8"))
    #     except IOError:
    #         confs_template_path = confs_path + '.template'
    #         logging.warn(
    #             'Confs path: {} does not exist. Attempting to load confs template, '
    #             'from path: {}'.format(confs_path, confs_template_path))
    #         CONFS = yaml.load(open(confs_template_path))
    return CONFS

def load_obj(name ):
    with open(name + '.pkl', 'rb') as f:

        return pickle.load(f)    

def get_conf(conf_name):
    return load_confs()[conf_name]


def term_count(string_to_search, term):
    """
    A utility function which counts the number of times `term` occurs in `string_to_search`
    :param string_to_search: A string which may or may not contain the term.
    :type string_to_search: str
    :param term: The term to search for the number of occurrences for
    :type term: str
    :return: The number of times the `term` occurs in the `string_to_search`
    :rtype: int
    """
    try:
        regular_expression = re.compile(term, re.IGNORECASE)
        result = re.findall(regular_expression, string_to_search)
        return len(result)
    except Exception as exception_instance:
        #logging.error('Error occurred during regex search: {}'.format(exception_instance))
        return 0


def term_match(string_to_search, term):
    """
    A utility function which return the first match to the `regex_pattern` in the `string_to_search`
    :param string_to_search: A string which may or may not contain the term.
    :type string_to_search: str
    :param term: The term to search for the number of occurrences for
    :type term: str
    :return: The first match of the `regex_pattern` in the `string_to_search`
    :rtype: str
    """
    try:
        regular_expression = re.compile(term, re.IGNORECASE)
        result = re.findall(regular_expression, string_to_search)
        if len(result) > 0:
            return result[0]
        else:
            return None
    except Exception as exception_instance:
        #logging.error('Error occurred during regex search: {}'.format(exception_instance))
        return None

