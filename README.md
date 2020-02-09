# Autofill and submit webforms

## User story

In some cases, you need to do online registrations on regular basis. It requests to open a web page, fill up a set of fields, and submit the page. Number of web pages can be more than one and each web page contains a bunch of fields along with validating of entered data. A real-life sample is a parking permit in a condo. Your kid has grown up and he buys a car. His car can't be accommodated in your parking lots because of limit. Your kid comes home 3 times per week from university. You have an allowance to park your guest cars overnight on visitor parking. You need to remember to obtain the parking permit for your kid's car every week. Also, you need to follow the same boring procedure every time when you submit your application. How it sounds?

It can be solved automating this routine with a tool.

## Introduction

The tool is designed in form of execution engine with a definition file. We need to tell what we need to do in the definition file. The instructions are arranged as a set of workflow steps. Each step opens or submits a web page. It's flexible in terms of customizing it to fit a wide range of registration systems.

## Definition file

### Header section

```json
"setup": {
		"caption": "Parking permit",
		"sendsuccessemail": "yes"
	}
```
This is applicable globally to all workflow steps. `caption` is your name to a registration system in your notification emails. `sendsuccessemail` notifies you with an email if all steps completed successfully.

### Email section

```
"emailsetup": {
		"from": "abcd@abcd.ca",
		"to": "zxc@opu.com",
		"server": "smtp.live.com",
		"port": "587",
		"user": "abcd@abcd.ca",
		"password": "password"
	}
```
The tool communication is established by sending notification or error emails. You need to provide information for your smtp client and your destination email. It works for hotmail smtp and it should work for gmail or other clients which use SSL encryption.

### Workflow steps

```
"urls": []
```
It can be any number of steps in your workflow. They are included in a list.

###  Workflow step

```
{
	"url": "http://reserve.localhost",
	"validationtext": [
		"Welcome to Reserve Room System\\.",
		"Please enter your access code #"
	],
	"parameters": {
	},
	"submithidden": "no",
	"successmessage": ""
}
```
`url` - url to open or submit a web page.
`validationtext` - a list of messages which expected to receive in the current web form. If a list is matched, we can be sure that we are on a right web form. It can help identify cases when system has been modified. Validation messages can include `regexp`, for example, `(?:Left 1|Left 2|Left 3) books available out of your weekly allowance of \\d{1}\\.`.   
`parameters` - list of parameters as name and value pairs for POST submission. A macro is acceptable in value fields. The macro is `$()`. Everything contained in macro is executed, for example, `STARTING": "$((date.today()+timedelta(days=1)).strftime('%Y-%m-%d') + ' 00:01')"`. We get the current data, add 1 day, convert into string, and add time.  
`submithidden` - a received web form can include some hidden fields. Those fields can be extracted and submitted in POST command.
`successmessage` - it's applicable to final step in workflow to make sure that a submission has been completed successfully. It contains a successful message returned by POST submission.

## Usage
```text
usage: submit_webform.py [-h] -f FILE

Autofill and submit webforms

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  Definition file path
```

## Usage sample
```bash
python3.6 submit_webform.py -f data_parking.json
```

## Setup
Install requests library

```bash
pip install requests
```
 