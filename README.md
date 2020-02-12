# Autofill and submit webforms

## User story

In some cases, you need to do online registrations on regular basis. It requests to open a web page, fill up a set of fields, and submit the page. Number of web pages can be more than one and each web page contains a bunch of fields along with validating of entered data. A real-life sample is a parking permit in a condo. Your kid has grown up and he buys a car. His car can't be accommodated in your parking lots because of limit. Your kid comes home 3 times per week from university. You have an allowance to park your guest cars overnight on visitor parking. You need to remember to obtain the parking permit for your kid's car every week. Also, you need to follow the same boring procedure every time when you submit your application. How it sounds?

It can be solved automating this routine.

## Introduction

The tool is designed in a form of execution engine with a setup file. We tell what we need to do in the setup file. The instructions are arranged as a set of workflow steps. Each step opens or submits a web page. It's flexible in terms of customizing to fit a wide range of registration systems.

## Setup file

### Header section

```json
"setup": {
		"caption": "Parking permit",
		"sendsuccessemail": "yes"
	}
```
This is applicable globally to all workflow steps. 
* `caption` - your name for a registration system in your notification emails. 
* `sendsuccessemail` - flag to notify you with an email if all steps completed successfully.

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
* `url` - url to open or submit a web page.
* `validationtext` - a list of messages which expected to receive in the current web form. If a list is matched, we can be sure that we are on a right web form. It can help identify cases when system has been modified. Validation messages can include `regexp`, for example, `(?:Left 1|Left 2|Left 3) books available out of your weekly allowance of \\d{1}\\.`.   
* `parameters` - list of parameters as name and value pairs for POST submission. A macro is acceptable in value fields. The macro is `$()`. Everything contained in macro is executed, for example, `STARTING": "$((date.today()+timedelta(days=1)).strftime('%Y-%m-%d') + ' 00:01')"`. We get the current date, add 1 day, convert into string, and add time.  
* `submithidden` - a received web form can include some hidden fields. Those fields can be extracted and submitted in following POST command.
* `successmessage` - it's applicable to final step in workflow to make sure that a submission has been completed successfully. It contains a successful message returned by POST submission.

## Setup

Install `requests` library

```bash
pip install requests
```

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

## Return codes

0 - success.

1 - setup file is not found.

2 - a web page validation is failed. It can be encountered if `validationtext` list doesn't match with a response received.
 
3 - this is applicable to final step when we don't receive expected text during the last response. The setup file key is `successmessage`.

4 - everything is completed successfully but the final step in the setup file doesn't have value for `successmessage` key.

127 - run-time error.

## Implementation

The final step is to establish a process of running of the tool at specified times. There are many possibilities to come up with. The easiest ways are crontab in Unix or Task Scheduler in Windows. More advanced level is systemd in Unix. The best implementation is to run it in an isolated environment with minimum resources consumed. It's containerization topic with Docker.

### Crontab in Unix

The description is based on CentOS 7 distribution.

* Validate if crontab daemon running.

```bash
sudo systemctl status crond
```
 
```text
crond.service - Command Scheduler
   Loaded: loaded (/usr/lib/systemd/system/crond.service; enabled; vendor preset: enabled)
   Active: active (running) since Tue 2020-02-11 20:24:44 EST; 25min ago
 Main PID: 1569 (crond)
    Tasks: 1
   CGroup: /system.slice/crond.service
           └─1569 /usr/sbin/crond -n
```

* Add a new job to crontab.

```bash
crontab -e
```

Enter the command. It runs the tool Friday, Monday, and Tuesday at 7:00 pm and directs any output to a log file.

```text
* 19 * * fri,mon,tue python3.6 /home/developer/auto-fill-submit-webform/submit_webform.py -f /home/developer/auto-fill-submit-webform/data_parking.json >> /home/developer/auto-fill-submit-webform/log/parking.log
```

* Validate the job.

```bash
crontab -l
```