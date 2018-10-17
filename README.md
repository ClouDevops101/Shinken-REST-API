# Shinken-REST-API
<a href="http://bitly.com/2grT54q"><img src="https://cdn.codementor.io/badges/i_am_a_codementor_dark.svg" alt="I am a codementor" style="max-width:100%"/></a><a href="http://bitly.com/2grT54q"><img src="http://www.shinken-monitoring.org/img/LogoFrameworkBlack.png" height="50"> 
 [![Donate](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WX4EKLLLV49WG)




Description : Shinken is a nagios fork written in Python Made in France

Requierements
================
Probably a shinken installation would be benefit 
then install requirements :
```shell
pip install -r requirements.txt 
```
Documentation
=============
## STOP'N'START

Start / Stop / Restart Shinken from the api : 
Start : 
```
curl https://MyAPI:5000/v3/shinken/restart
```
Stop : 
```
curl https://MyAPI:5000/v3/shinken/stop
```
Restart : 
```
curl https://MyAPI:5000/v3/shinken/restart
```
### Common Error : 
'id' : 'SHNK-002' (See error table)

## ADDING HOST
Adding a host to Shinken : 
```
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
```
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
```
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
```
  curl https://MyAPI:5000/v3/hosts/search/HDP
```
This command will seek host from the shinken configuration and will display the result in a nesty json

### Common Error : 
'id' : 'SHNK-004' (See error table)


## DELETE HOST(S) /!\

This feature is propably the most dangerous one, please make sure you're realy want to remove a bunch of host configuration from the shinken /!\ !!! /!\ : 
```
  curl https://MyAPI:5000/v3/hosts/deletematch/HDP
```
This command will seek hosts from the shinken configuration and will try to remove the host if the search match more than one host than you need to force the command by doing this command /!\ : 
```
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


