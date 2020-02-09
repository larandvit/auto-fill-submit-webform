from os import path
import sys

import json
import re
import argparse

import requests

from datetime import date
from datetime import timedelta

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

class CompletionCode:
    SUCCESS = 0
    DATA_FILE_NOT_FOUND = 1
    FAILED_VALIDATION = 2
    FINAL_VALIDATION_FAILED = 3
    NOT_VALIDATED_SUBMITTION = 4
    RUNTIME_ERROR = 127

def calculate_parameters(parameter_list):
    params = {}
    
    for param_name in parameter_list.keys():
        param_value = parameter_list[param_name].strip()
        
        pattern = '^\$\((.*)\)$'
        matched = re.search(pattern, param_value)

        if matched:
            param_value = eval(matched.group(1))
            
        params[param_name] = param_value
        
    return params

def send_email(subject, body, email_setup):
    
    message = MIMEMultipart()
    
    message['Subject'] = subject
    message['From'] = email_setup['from']
    message['To'] = email_setup['to']
        
    body_text = MIMEText(body, "plain")
    message.attach(body_text)
    
    with smtplib.SMTP(email_setup['server'], email_setup['port']) as server:
        server.ehlo()
        server.starttls()
        server.ehlo()
        server.login(email_setup['user'], email_setup['password'])
        server.sendmail(email_setup['from'], email_setup['to'], message.as_string())
        
def collect_hidden_values(web_text):
    pattern = 'input type="hidden" name="(.*)" value="(.*)"'
    
    hidden_parameter_list = {}
    
    matched = re.findall(pattern, web_text)
    
    if matched:
        for hidden_value in matched:
            name, value = hidden_value
            name = name.strip()
            value = value.strip()
            hidden_parameter_list[name] = value
            
    return hidden_parameter_list

if __name__ == '__main__':
    
    parser = argparse.ArgumentParser(description="Autofill and submit webforms")

    parser.add_argument("-f", "--file", dest='file',
                        required=True,
                        help="Definition file path")
    
    args = parser.parse_args()
    
    data_json_path = path.abspath(args.file)
    
    if path.exists(data_json_path) and path.isfile(data_json_path):
    
        data_json = json.load(open(data_json_path))
        
        email_setup = data_json['emailsetup']
        
        caption = data_json['setup']['caption']
        send_success_email = (data_json['setup']['sendsuccessemail']).lower()
        
        error_message = None
        web_response = None
        web_text = None
        
        completion_code = CompletionCode.RUNTIME_ERROR
        
        hidden_parameter_list = {}
        
        for webform in data_json['urls']:
            url = webform['url']
            validation_text_list = webform['validationtext']
            parameter_list = webform['parameters']
            submit_hidden = webform['submithidden'].lower()
            success_mesage = webform['successmessage']
            
            is_post = len(parameter_list)>0 or submit_hidden=='yes'
            
            if is_post:
                params = calculate_parameters(parameter_list)
                
                # add hidden values as parameters
                if submit_hidden=='yes':
                    for hidden_parameter in hidden_parameter_list.keys():
                        if not hidden_parameter in params:
                            params[hidden_parameter] = hidden_parameter_list[hidden_parameter]
                    
                web_response = requests.post(url, data=params)
            else:
                web_response = requests.get(url)
                
            web_text= web_response.text
            
            hidden_parameter_list = collect_hidden_values(web_text)
            
            found_validation_text_list = {}
            for validation_text in validation_text_list:
                matched = re.search(validation_text, web_text)
                if matched:
                    found_validation_text_list[validation_text] = matched.group(0)
                else:
                    error_message = 'Failed validation "{}" in "{}"'.format(validation_text, url)
                    break
            
                    
            if not error_message==None:
                break
        
        if error_message:
            body = error_message
            if web_response:
                body += '\n\n' + str(web_response)
            if web_text:
                body += '\n\n' + web_text
            send_email(caption + ' - Error', body, email_setup)
            completion_code = CompletionCode.FAILED_VALIDATION
        else:
            if success_mesage:
                matched = re.search(success_mesage, web_text)
                if matched:
                    if send_success_email=='yes':
                        body = web_text
                        send_email(caption + ' - Success', body, email_setup)
                    completion_code = CompletionCode.SUCCESS
                else:
                    body = web_text
                    send_email(caption + ' - Error', body, email_setup)
                    completion_code = CompletionCode.FINAL_VALIDATION_FAILED
            else:
                body = 'Succesful message is not found in data setup file'
                if web_response:
                    body += '\n\n' + str(web_response)
                if web_text:
                    body += '\n\n' + web_text
                send_email(caption + ' - Not validated submittion', body, email_setup)
                completion_code = CompletionCode.NOT_VALIDATED_SUBMITTION
    else:
        print('Error. "{}" data file not found'.format(data_json_path))
        completion_code = CompletionCode.DATA_FILE_NOT_FOUND
        
    sys.exit(completion_code)
        