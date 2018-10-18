# The Monitoring Stack as a Microservice
<a href="http://bitly.com/2grT54q"><img src="https://cdn.codementor.io/badges/i_am_a_codementor_dark.svg" alt="I am a codementor" style="max-width:100%"/></a><a href="http://bitly.com/2grT54q"><img src="http://www.shinken-monitoring.org/img/LogoFrameworkBlack.png" height="50"> 
 [![Donate](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WX4EKLLLV49WG)


Description : The purpose of this project is to build an intelligent monitoring / supervision  infrastructure  microservice based, able to handle the challenge of adding, plugging ad unplugging microservice and system in a cloud like environment
![The_Monitoring_Stack_as_a_Microservice]](The_Monitoring_Stack_as_a_Microservice.jpg "The_Monitoring_Stack_as_a_Microservice")

Shinken is a nagios fork written in Python Made in France

'''Disclamer''' : Supervision and monitoring terms are interchangeable in this topic.
Devs : " Get rid of sending an excel sheet with information to the ops monitoring guy to get your host/service monitored with an assumed margin of humain erreur."
Ops : "Get rid of adding a bunch of hosts generating alarm that blinks like a christmas tree, caused by montoring ghost hosts that dosen't exit yet or hosts in to be deployed status. "
Wouldn't be simple to send in time, a JSON request once and notify the whole monitoring system to welcome warmly the fresh new deployed app, or remove magically the old one.

Indeed, it could be nice and very efficient to send a JSON request to a system that register my new application, container or service. it's seem like a technology comming from space but it's not, at my current compagny Euronext, we build a system that makes the ops worklife easy by managing the monitoring infrastructure only and enjoying the autopilot mode.

This simple request is enough to get you straightfroward to desired state :
```json
{
 "use" : "linux-ssh",
 "contact_groups": "admins",
 "host_name" : "Mesos-Agent007",
 "address" : "10.0.X.X",
 "hostgroups" : "MESOS",
  "_SSH_KEY" : ".ssh/id_rsa",
  "_SSH_USER" : "bbiswatchingyou" 
}
```
Once the rest api get the request, it's able to do the work and the magic happens:

1 - Is this information correct ? :
```json
{
 "host_name" : "Mesos-Agent007",
 "address" : "10.0.X.X"
The api is smart enough to quickly decide wether this host could be registred or not by :
```
Checking if the DNS registry is aware about this host
Doing a simple ping to check if the host system is Up
2 - Following the supervision template :

you may notice the first line indicate to the monitoring system to pic the appropriate pattern to use :
```json
{
"use" : "linux-ssh",
```
We did write a couple of template to cover the common monitoring use cases.

The linux-ssh tells the API that this system is in Agentless mode (Thanks to Shinken (The nagios fork) , so SSH protocole is engouh to monitor, no need to install and configure an NRPE agent or collectD or a telegraph on the target system.

Here again the system will process to the next level of tests. Testing the ssh connexion, if the sshd is not misconfigured or the ssh key is invalid, you'll got a nice error message from the API with a 471 HTTP code : expectation failed.

3 - Adding the host/service :

If the step 2 succeed, the host is associated with the described group, following the previous example :
```json
{
"hostgroups" : "MESOS"﻿
```
a monitoring groupe called MESOS will be created (if not exist) and the new host is associated to.

Requierements
================
Probably a shinken installation would be benefit 
then install requirements :
```bash
pip install -r requirements.txt 
```
Documentation
=============
## STOP'N'START

Start / Stop / Restart Shinken from the api : 
Start : 
```bash
curl https://MyAPI:5000/v3/shinken/restart
```
Stop : 
```bash
curl https://MyAPI:5000/v3/shinken/stop
```
Restart : 
```bash
curl https://MyAPI:5000/v3/shinken/restart
```
### Common Error : 
'id' : 'SHNK-002' (See error table)

## ADDING HOST
Adding a host to Shinken : 
```bash
     echo '
        {
        "use":"Web",
        "host_name":"Host to monitor",
        "address":"10.0.0.1",
        "contact_groups":"DevOps",
        "hostgroups":"WebApp",
        "_SSH_KEY":"rsa_webapp_.pub",
        "_SSH_USER":"admin"
        }
        ' | curl -d @- https://MyAPI:5000/v3/hosts
```
This command will add the host to the shinken configuration and will cleanly reload the shinken-arbiter responsble for handeling configuration

### Common Error : 
'id' : 'SHNK-001' (See error table)

##  ADDING GROUP OF HOST BY IP RANGE
Adding a group of host to Shinken by an ip range : 
```bash
     echo '
        {
        "address_range":"10.0.0.1-10.0.0.22",
        "contact_groups":"DevOps",
        "hostgroups":"WebApp",
        "_SSH_KEY":"rsa_webapp_.pub",
        "_SSH_USER":"admin"
        "use":"Web"
        }
        ' | curl -d @- https://MyAPI:5000/v3/hostsbyiprl
```
This command will add the host to the shinken configuration and will cleanly reload the shinken-arbiter responsble for handeling configuration

### Common Error : 
'id' : 'SHNK-004' (See error table)

##  ADDING GROUP OF HOST BY RANGE
Adding a group of host to Shinken by a host range : 
```bash
    curl https://MyAPI:5000/v3/hosts/search/HDP
```
This command will add the groupe of host Hadopspark19[702-711]v-int to the shinken as follow : 
Hadopspark19702v-int
Hadopspark19703v-int
Hadopspark19704v-int
...
Hadopspark19711v-int
 
 And will cleanly reload the shinken-arbiter responsble for handeling configuration

### Common Error : 
'id' : 'SHNK-004' (See error table)

## SEARCHING HOST

Adding a group of host to Shinken by an ip range : 
```bash
  curl https://MyAPI:5000/v3/hosts/search/HDP
```
This command will seek host from the shinken configuration and will display the result in a nesty json

### Common Error : 
'id' : 'SHNK-004' (See error table)


## DELETE HOST(S) /!\

This feature is propably the most dangerous one, please make sure you're realy want to remove a bunch of host configuration from the shinken /!\ !!! /!\ : 
```bash
  curl https://MyAPI:5000/v3/hosts/deletematch/HDP
```
This command will seek hosts from the shinken configuration and will try to remove the host if the search match more than one host than you need to force the command by doing this command /!\ : 
```bash
  curl https://MyAPI:5000/v3/hosts/deletematch/HDP/force
```


#### Common Error : 
'id' : 'SHNK-004' (See error table)


ERROR TABLE : 
=============
| CODE          | Message  |
|:-------------:| -----:|
| SHNK-001     | Missing requeried field : Please note that "use" and "host_name" and "address" are mandatory  |
|SHNK-002     | Unknow Action please use : /v3/shinken/Action = [start | restart | stop ]      |  
| SHNK-003 | Value can not be empty or a space   |  
| SHNK-004 | Unknown range format  |
|SHNK-005 | No host is matching the ' + ip  |
|SHNK-006|HOST unreachable through ssh|


