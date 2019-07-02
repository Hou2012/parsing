#!/usr/bin/env python
"""
coding=utf-8

Code Template

"""
# import logging
#import textract
from parse import parseFunctions

from flask import jsonify

import sys
import datetime

import requests
from io import StringIO


def parse(request):
    if request.method == 'OPTIONS':
        # Allows GET requests from any origin with the Content-Type
        # header and caches preflight response for an 3600s
        headers = {
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Allow-Methods': 'GET, POST',
            'Access-Control-Allow-Headers': 'content-type',
            'Access-Control-Max-Age': '3600'
        }

        return ('', 204, headers)

    # Set CORS headers for the main request
    headers = {
        'Access-Control-Allow-Origin': '*',
        'Access-Control-Allow-Methods': 'GET, POST',
        'Access-Control-Allow-Headers': 'content-type',
        'Access-Control-Max-Age': '3600'
    }
    try:
        request_json = request.get_json(silent=True)
        stringdate = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
        r = requests.get(request_json['fileURL'], allow_redirects=True)
        extension = request_json['file_extension']
        if extension == 'vnd.openxmlformats-officedocument.wordprocessingml.document':
            extension = 'docx'
        elif extension == 'msword':
            extension = 'doc'
        elif extension == 'plain':
            extension = 'txt'
        fileName = '/tmp/cv'+ stringdate + '.' + extension
        print('this is the content:', r.content)
        open(fileName, 'wb').write(r.content)
        response = parseFunctions.Parse(fileName, extension)
        response= response.drop(columns=['text'])
        response= response.drop(columns=['file_path'])
        response= response.drop(columns=['extension'])
        return (response.to_json(orient='records'), 200, headers)
    except:
        return ('an error has occured', 500, headers)
    


    # return response[2]
    # return response[0].iloc[0].str()
if __name__ == '__main__':
#     # Map command line arguments to function arguments.
    result = parseFunctions.Parse('D:/pepit/parsing-matching/data/input/example_resumes_fr/DataValue - CV - HEL.pdf', 'pdf')
   
    print(result)
    