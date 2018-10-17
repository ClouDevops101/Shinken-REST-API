# Shinken-REST-API
<a href="http://bitly.com/2grT54q"><img src="https://cdn.codementor.io/badges/i_am_a_codementor_dark.svg" alt="I am a codementor" style="max-width:100%"/></a><a href="http://bitly.com/2grT54q"><img src="http://www.shinken-monitoring.org/img/LogoFrameworkBlack.png" height="50"> 
 [![Donate](https://www.paypalobjects.com/en_US/i/btn/btn_donateCC_LG.gif)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=WX4EKLLLV49WG)




Description : a python script to push event to kinesis

HOW It WORKS
================
The configuration is inside the python script : 

Requierements
================
Probably a shinken installation would be benefit 
then install requirements :
```
pip install -r requirements.txt 
```
Documentation
=============
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
###Commonn Error : 
'id' : 'SHNK-002' (See error table)

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

###Commonn Error : 
'id' : 'SHNK-001' (See error table)


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

###Commonn Error : 
'id' : 'SHNK-004' (See error table)


ERROR TABLE : 
=============
```
'id' : 'SHNK-001', 'Message' : 'Missing requeried field : Please note that "use" and "host_name" and "address" are mandatory '
'id' : 'SHNK-002', 'Message' : 'Unknow Action please use : /v3/shinken/Action = [start | restart | stop ]'
'id' : 'SHNK-003', 'Message' : 'Value can not be empty or a space'
'id' : 'SHNK-004', 'Message' : 'Unknown range format'
'id' : 'SHNK-005', 'Message' : 'No host is matching the ' + ip 
'id' : 'SHNK-006', 'Message' : 'HOST unreachable through ssh'
```

