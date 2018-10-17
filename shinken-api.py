import os
import socket
import platform
import glob
import re
import time
try: 
    import paramiko
except:
    print ("Syntaxe test only this module parmaiko is not installed")
from flask.helpers import make_response
try: 
    import dbus
except:
    print ("Syntaxe test only this module dbus does not exist on Windows")
import random
from flask import Flask, redirect, url_for, request, render_template
from flask import jsonify
from flasgger import Swagger
#from pymongo import MongoClient

def ipRange(start_ip, end_ip):
   start = list(map(int, start_ip.split(".")))
   end = list(map(int, end_ip.split(".")))
   temp = start
   ip_range = []

   ip_range.append(start_ip)
   while temp != end:
      start[3] += 1
      for i in (3, 2, 1):
         if temp[i] == 256:
            temp[i] = 0
            temp[i-1] += 1
      ip_range.append(".".join(map(str, temp)))

   return ip_range

def hostRange(hostrange):
    # dsdciits19[702-711]v-int
 p = re.compile('\[(.*)\]')
 number = p.findall(hostrange)
    
 range_number = number[0].split("-")
 range_number = map(int, range_number)
 start = range_number[0] 
 end = range_number[1]
 host_list = []
 while start <= end:
     host_list.append(p.sub(str(start), hostrange))
     start += 1
 return host_list

def lookup_ip(addr):
   try:
       return socket.gethostbyaddr(addr)
   except socket.herror:
       return None, None, None

def lookup_host(host):
   try:
       return socket.gethostbyname(host)
   except socket.gaierror:
       return None

def check_ssh(ip, user, key_file, initial_wait=0, interval=0, retries=1):
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    time.sleep(initial_wait)

    for x in range(retries):
        try:
            ssh.connect(ip, username=user, key_filename=key_file)
            return True
        #except (BadHostKeyException, AuthenticationException, SSHException, socket.error) as e:
        except:
            #print e
            time.sleep(interval)
    return False

app = Flask(__name__)
Swagger(app)


# {"use" : "linux-ssh", "contact_groups": "admins", "host_name" : "dsdciits19701v-int", "address" : "172.27.87.186", "hostgroups" : "Shinken_Stack" , "_SSH_KEY" : "/home/shinken/.ssh/id_rsa", "_SSH_USER" : "aheddar" }"""


@app.route('/<string:version>/shinken/<string:action>', methods=['GET'])
def controle_shinken_(action,version):
    """
    This is the language awesomeness API
    Call this api passing a language name and get back its features
    ---
    tags:
      - Awesomeness Language API
    parameters:
      - name: language
        in: path
        type: string
        required: true
        description: The language name
      - name: size
        in: query
        type: integer
        description: size of awesomeness
    responses:
      500:
        description: Error The language is not awesome!
      200:
        description: A language with its awesomeness
        schema:
          id: awesome
          properties:
            language:
              type: string
              description: The language name
              default: Lua
            features:
              type: array
              description: The awesomeness list
              items:
                type: string
              default: ["perfect", "simple", "lovely"]

    """

    output = [] 

    if action == 'restart' and version.lower() == 'v3':
        sysbus = dbus.SystemBus()
        systemd1 = sysbus.get_object('org.freedesktop.systemd1', '/org/freedesktop/systemd1')
        manager = dbus.Interface(systemd1, 'org.freedesktop.systemd1.Manager')
        job = manager.RestartUnit('shinken-arbiter.service', 'fail') 
        output.append({'Shinken' : "Shinken restarted" })
    elif  action == 'stop':
        sysbus = dbus.SystemBus()
        systemd1 = sysbus.get_object('org.freedesktop.systemd1', '/org/freedesktop/systemd1')
        manager = dbus.Interface(systemd1, 'org.freedesktop.systemd1.Manager')
        job = manager.StopUnit('shinken-arbiter.service', 'fail')
        output.append({'Shinken' : "Shinken stopped" })
    elif  action == 'start':
        sysbus = dbus.SystemBus()
        systemd1 = sysbus.get_object('org.freedesktop.systemd1', '/org/freedesktop/systemd1')
        manager = dbus.Interface(systemd1, 'org.freedesktop.systemd1.Manager')
        job = manager.StartUnit('shinken-arbiter.service', 'fail')
        output.append({'Shinken' : "Shinken started" })
    else: 
        output.append({ 'id' : 'SHNK-002', 'Message' : 'Unknow Action please use : /v3/shinken/Action = [start | restart | stop ]'})
        #return jsonify({ 'Error' : output })
        response = make_response(jsonify({'Error' : output }), 404)
        return response
    return jsonify({'Notification' : output })
  
@app.route('/<string:version>/hosts', methods=['POST'])
def add_host(version):
#  star = db.shinken_config

 contact_groups = request.json['contact_groups']
 hostgroups     = request.json['hostgroups']
 _SSH_KEY       = request.json['_SSH_KEY']
 _SSH_USER      = request.json['_SSH_USER']
  
 output = []
 
 if 'host_name' in request.json and 'address' in  request.json and 'use' in request.json:
     host_name      = request.json['host_name']
     address        = request.json['address']
     use            = request.json['use']
    
     host_name = host_name.replace(" ", "")
     address =  address.replace(" ", "")
     use = use.replace(" ", "")
     
     if use and host_name and address: 
         if check_ssh(address, _SSH_USER, _SSH_KEY):
             output = {'use' :  use, 'contact_groups': contact_groups, 'host_name' : host_name, 'address' : address, 'hostgroups' : hostgroups, '_SSH_KEY' : _SSH_KEY, '_SSH_USER' : _SSH_USER} 

             # write to file
             f = open('/etc/shinken/hosts/' + host_name + '.cfg' , 'w+')
             # modele f.write( 'dict = ' + repr(dict) + '\n' )
             f.write('define host {\n\tuse\t\t\t\t' + use + '\n\tcontact_groups\t\t\t' + contact_groups + '\t\n\thost_name\t\t\t' + host_name + '\n\taddress\t\t\t\t' + address + '\n\thostgroups\t\t\t' + hostgroups + '\n\t_SSH_KEY\t\t\t' + _SSH_KEY + '\n\t_SSH_USER\t\t\t' + _SSH_USER + '\n}\n')
             f.close() 
             #f.seek(0,0)
             #for index in range(6):
             #    line = f.next()
             #    print "Line No %d - %s" % (index, line)

             # Close opend file
             #f.close()
             sysbus = dbus.SystemBus()
             systemd1 = sysbus.get_object('org.freedesktop.systemd1', '/org/freedesktop/systemd1')
             manager = dbus.Interface(systemd1, 'org.freedesktop.systemd1.Manager')
             job = manager.RestartUnit('shinken-arbiter.service', 'fail')
             #return jsonify({'define host' : output})
             response = make_response(jsonify({'define host' : output }), 201)
             return response
         else:
             output.append({ 'id' : 'SHNK-006', 'Message' : 'HOST unreachable through ssh'})
             #return jsonify({ 'Error' : output })
             response = make_response(jsonify({'Error' : output }), 417)
             return response
             
     else:
         output.append({ 'id' : 'SHNK-003', 'Message' : 'Value can not be empty or a space'})
         #return jsonify({ 'Error' : output })
         response = make_response(jsonify({'Error' : output }), 417)
         return response
 else:
     output.append({ 'id' : 'SHNK-001', 'Message' : 'Missing requeried field : Please note that "use" and "host_name" and "address" are mandatory '})
     #return jsonify({ 'Error' : output })
     response = make_response(jsonify({'Error' : output }), 417)
     return response
  
@app.route('/<string:version>/hostsbyiprl', methods=['POST'])
def add_host_by_ip_range(version):

 contact_groups = request.json['contact_groups']
 hostgroups     = request.json['hostgroups']
 _SSH_KEY       = request.json['_SSH_KEY']
 _SSH_USER      = request.json['_SSH_USER']
  
 output = []
 
 if 'address_range' in  request.json and 'use' in request.json:
     
     address_range = request.json['address_range']
     use           = request.json['use']
    
     address_range =  address_range.replace(" ", "")
     use = use.replace(" ", "")
     
     if use and address_range:
         if "-" in address_range:
             #172.27.87.184-172.27.87.184
         
             # sample usage
             ip_range = ipRange(str(address_range.split('-')[0]) , str(address_range.split('-')[1]))
             for ip in ip_range:
                 #print(ip)
                 print (str(address_range.split('-')[0]))
                 print (str(address_range.split('-')[1]))
                 name,alias,addresslist = lookup_ip(ip)
                 if not name:
                     output.append({ 'id' : 'SHNK-005', 'Message' : 'No host is matching the ' + ip })
                     continue
                 elif not check_ssh(ip, _SSH_USER, _SSH_KEY):
                     output.append({ 'id' : 'SHNK-006', 'Message' : 'HOST unreachable through ssh'})
                     continue
                 else:
                     host_name = name.split('.')[0]
                 address = ip
                 output.append({'use' :  use, 'contact_groups': contact_groups, 'host_name' : host_name, 'address' : address, 'hostgroups' : hostgroups, '_SSH_KEY' : _SSH_KEY, '_SSH_USER' : _SSH_USER}) 

                  # write to file
                 f = open('/etc/shinken/hosts/' + host_name + '.cfg' , 'w+')
                 # modele f.write( 'dict = ' + repr(dict) + '\n' )
                 f.write('define host {\n\tuse\t\t\t\t' + use + '\n\tcontact_groups\t\t\t' + contact_groups + '\t\n\thost_name\t\t\t' + host_name + '\n\taddress\t\t\t\t' + address + '\n\thostgroups\t\t\t' + hostgroups + '\n\t_SSH_KEY\t\t\t' + _SSH_KEY + '\n\t_SSH_USER\t\t\t' + _SSH_USER + '\n}\n')
                 f.close()
 
         #return jsonify({'define host' : output"})
             response = make_response(jsonify({'define host' : output }), 201)
             return response
         elif "," in address_range:
             #for list 172.27.87.184,172.27.87.184
             ip_range = address_range.split(',')
             for ip in ip_range:
                 #print(ip)
                 name,alias,addresslist = lookup_ip(ip)
                 if not name:
                     output.append({ 'id' : 'SHNK-005', 'Message' : 'No host is matching the ' + ip })
                     continue
                 elif not check_ssh(ip, _SSH_USER, _SSH_KEY):
                     output.append({ 'id' : 'SHNK-006', 'Message' : 'HOST unreachable through ssh'})
                     continue  
                 else:
                     host_name = name.split('.')[0]
                 address = ip
                 output.append({'use' :  use, 'contact_groups': contact_groups, 'host_name' : host_name, 'address' : address, 'hostgroups' : hostgroups, '_SSH_KEY' : _SSH_KEY, '_SSH_USER' : _SSH_USER}) 

                  # write to file
                 f = open('/etc/shinken/hosts/' + host_name + '.cfg' , 'w+')
                 # modele f.write( 'dict = ' + repr(dict) + '\n' )
                 f.write('define host {\n\tuse\t\t\t\t' + use + '\n\tcontact_groups\t\t\t' + contact_groups + '\t\n\thost_name\t\t\t' + host_name + '\n\taddress\t\t\t\t' + address + '\n\thostgroups\t\t\t' + hostgroups + '\n\t_SSH_KEY\t\t\t' + _SSH_KEY + '\n\t_SSH_USER\t\t\t' + _SSH_USER + '\n}\n')
                 f.close()
                 
         #return jsonify({'define host' : output"})
             response = make_response(jsonify({'define host' : output }), 201)
             return response
         else:
             output.append({ 'id' : 'SHNK-004', 'Message' : 'Unknown range format'})
             #return jsonify({ 'Error' : output })
             response = make_response(jsonify({'Error' : output }), 417)
             return response
     else:
         output.append({ 'id' : 'SHNK-003', 'Message' : 'Value can not be empty or a space'})
         #return jsonify({ 'Error' : output })
         response = make_response(jsonify({'Error' : output }), 417)
         return response
 else:
     output.append({ 'id' : 'SHNK-001', 'Message' : 'Missing requeried field : Please note that "use" and "host_name" and "address" are mandatory '})
     #return jsonify({ 'Error' : output })
     response = make_response(jsonify({'Error' : output }), 417)
     return response

@app.route('/<string:version>/hostsbyhostr', methods=['POST'])
def add_host_by_host_range(version):

 contact_groups = request.json['contact_groups']
 hostgroups     = request.json['hostgroups']
 _SSH_KEY       = request.json['_SSH_KEY']
 _SSH_USER      = request.json['_SSH_USER']
  
 output = []
 
 if 'host_range' in  request.json and 'use' in request.json:
     
     host_range = request.json['host_range']
     use           = request.json['use']
    
     host_range =  host_range.replace(" ", "")
     use = use.replace(" ", "")
     
     if use and host_range:
         if "-" in host_range and "[" in host_range and "]" in host_range:
             #172.27.87.184-172.27.87.184
         
             # sample usage
             #  add function 
             host_list = hostRange(host_range)
            
             for host in host_list:
                 #print(ip)
                 ip = lookup_host(host)
                 if not ip:
                     output.append({ 'id' : 'SHNK-005', 'Message' : 'No ip is matching the ' + host })
                     continue
                 elif not check_ssh(ip, _SSH_USER, _SSH_KEY):
                     output.append({ 'id' : 'SHNK-006', 'Message' : 'HOST unreachable through ssh'})
                     continue  
                 else:
                     address = ip
                 host_name = host
                 output.append({'use' :  use, 'contact_groups': contact_groups, 'host_name' : host_name, 'address' : address, 'hostgroups' : hostgroups, '_SSH_KEY' : _SSH_KEY, '_SSH_USER' : _SSH_USER}) 

                  # write to file
                 f = open('/etc/shinken/hosts/' + host_name + '.cfg' , 'w+')
                 # modele f.write( 'dict = ' + repr(dict) + '\n' )
                 f.write('define host {\n\tuse\t\t\t\t' + use + '\n\tcontact_groups\t\t\t' + contact_groups + '\t\n\thost_name\t\t\t' + host_name + '\n\taddress\t\t\t\t' + address + '\n\thostgroups\t\t\t' + hostgroups + '\n\t_SSH_KEY\t\t\t' + _SSH_KEY + '\n\t_SSH_USER\t\t\t' + _SSH_USER + '\n}\n')
                 f.close()
 
         #return jsonify({'define host' : output"})
             response = make_response(jsonify({'define host' : output }), 201)
             return response
         elif "," in host_range:
             #for list 172.27.87.184,172.27.87.184
             host_list = host_range.split(',')
             for host in host_list:
                 #print(ip)
                 ip = lookup_host(host)
                 if not ip:
                     output.append({ 'id' : 'SHNK-005', 'Message' : 'No ip is matching the ' + host })
                     continue
                 elif not check_ssh(ip, _SSH_USER, _SSH_KEY):
                     output.append({ 'id' : 'SHNK-006', 'Message' : 'HOST unreachable through ssh'})
                     continue  
                 else:
                     address = ip
                 host_name = host
                 output.append({'use' :  use, 'contact_groups': contact_groups, 'host_name' : host_name, 'address' : address, 'hostgroups' : hostgroups, '_SSH_KEY' : _SSH_KEY, '_SSH_USER' : _SSH_USER}) 

                  # write to file
                 f = open('/etc/shinken/hosts/' + host_name + '.cfg' , 'w+')
                 # modele f.write( 'dict = ' + repr(dict) + '\n' )
                 f.write('define host {\n\tuse\t\t\t\t' + use + '\n\tcontact_groups\t\t\t' + contact_groups + '\t\n\thost_name\t\t\t' + host_name + '\n\taddress\t\t\t\t' + address + '\n\thostgroups\t\t\t' + hostgroups + '\n\t_SSH_KEY\t\t\t' + _SSH_KEY + '\n\t_SSH_USER\t\t\t' + _SSH_USER + '\n}\n')
                 f.close()
             response = make_response(jsonify({'define host' : output }), 201)
             return response
         else:
             output.append({ 'id' : 'SHNK-004', 'Message' : 'Unknown range format'})
             #return jsonify({ 'Error' : output })
             response = make_response(jsonify({'Error' : output }), 417)
             return response
     else:
         output.append({ 'id' : 'SHNK-003', 'Message' : 'Value can not be empty or a space'})
         #return jsonify({ 'Error' : output })
         response = make_response(jsonify({'Error' : output }), 417)
         return response
 else:
     output.append({ 'id' : 'SHNK-001', 'Message' : 'Missing requeried field : Please note that "use" and "host_name" and "address" are mandatory '})
     #return jsonify({ 'Error' : output })
     response = make_response(jsonify({'Error' : output }), 417)
     return response  
 
@app.route('/<string:version>/hosts/search/<string:name>', methods=['GET'])
def get_one_host_by_name(name,version):
  output = []
  for fic in glob.glob("/etc/shinken/hosts/*.cfg"):
      with open(fic) as f:
          contents = f.read()
      if name in contents:
          print (fic)
          output.append({'File' : fic , 'content' : contents.replace('\n',' ').replace('\t',' ') })
  
  return jsonify({'Result' : output })

@app.route('/<string:version>/hosts/deletematch/<string:name>', methods=['GET'])

def remove_host_by_name(name,version):
  
    output = []
    for fic in glob.glob("/etc/shinken/hosts/*.cfg"):
        with open(fic) as f:
            contents = f.read()
        if name in contents:
            print (fic)
            output.append(fic)
    # Remove all matched files
    if len(output) == 1:
        for fic2remove in output:
            # /!\ risk to remove all config
            os.remove(fic2remove)  
    else:
         output.append({'Error' : 'Too many files to be deleted use ' + request.path + '/force to complete this operation', 'count' : len(output) })
         response = make_response(jsonify({'Error' : output }), 409)
         return response
     
    return jsonify({'Deleted files' : output })

@app.route('/<string:version>/hosts/deletematch/<string:name>/force', methods=['GET'])

def remove_force_multiple_host_by_name(name,version):
  
    output = []
    for fic in glob.glob("/etc/shinken/hosts/*.cfg"):
        with open(fic) as f:
            contents = f.read()
        if name in contents:
            print (fic)
            output.append(fic)
    # Remove all matched files
    #if len(output) == 1:
    for fic2remove in output:
            # /!\ risk to remove all config
        os.remove(fic2remove)  
    #else:
    #    output.append({'Error' : 'Too many files'})
    #    return jsonify({'Error' : output })
  
    return jsonify({'Deleted files' : output })

@app.route('/<string:version>/hosts', methods=['GET'])

def seeking_for_hosts_by_name(version):
  
    output = set()
    for fic in glob.glob("/etc/shinken/hosts/*.cfg"):
        with open(fic) as f:
            for line in f:
                if 'host_name' in line:
                    output.add(line.split('\t\t\t')[1].strip())
        
    output = list(output)

        #return jsonify({'Hosts' : output , 'count' : len(output) })
    response = make_response(jsonify({'Hosts' : output , 'count' : len(output) }), 404)
    return response
@app.route('/<string:version>/packs', methods=['GET'])

def seeking_for_packs_by_name(version):
  
    output = set()
    #output = []
    for fic in glob.glob("/etc/shinken/hosts/*.cfg"):
        with open(fic) as f:
            for line in f:
                if 'use' in line:
                    line = line.replace('use','').replace('\t', '').strip()
                   # if ',' in line:
                        #line_without_comma = line.split('\t\t\t')[1].strip()
                        #print line_without_comma.split(",")
                        #output |= set(line_without_comma.split(","))
                    output |= set(line.split(","))
                    #else:
                    #output.add(line.split('\t\t\t')[1].strip())
        
    output = list(output)
  
    return jsonify({'Packs' : output , 'count' : len(output) })

@app.route('/<string:version>/hostgroups', methods=['GET'])

def seeking_for_hostgroupe_by_name(version):
  
    output = set()
    for fic in glob.glob("/etc/shinken/hosts/*.cfg"):
        with open(fic) as f:
            for line in f:
                if 'hostgroups' in line:
                    output.add(line.split('\t\t\t')[1].strip())
    output = list(output)
  
    return jsonify({'Hostgroups' : output , 'count' : len(output) })

##
###  Dependencies Block
##

@app.route('/<string:version>/hostsdependencies', methods=['POST'])
def add_hosts_dependencies_(version):
# New block
 output = []
 
 if 'host_name' in request.json and 'dependent_host_name' in  request.json:
     host_name = request.json['host_name']
     dependent_host_name = request.json['dependent_host_name']
    
     host_name = host_name.replace(" ", "")
     dependent_host_name = dependent_host_name.replace(" ", "")
     
     
     if host_name and dependent_host_name:
         output = {'host_name' :  host_name, 'dependent_host_name': dependent_host_name, 'execution_failure_criteria' : 'o', 'notification_failure_criteria' : 'u', 'dependency_period' : '24x7'} 
         # write to file
         f = open('/etc/shinken/dependencies/' + host_name + '-' + dependent_host_name  + '.cfg' , 'w+')
         # modele f.write( 'dict = ' + repr(dict) + '\n' )
         f.write('define hostdependency {\n\thost_name\t\t\t\t' +  host_name +  '\n\tdependent_host_name\t\t\t' + dependent_host_name + '\n\texecution_failure_criteria\t\t\to\n\tnotification_failure_criteria\t\t\tu\n\tdependency_period\t\t\t24x7\n}\n')
         f.close()
         response = make_response(jsonify({'define host' : output }), 201)
         return response
     else:
         output.append({ 'id' : 'SHNK-003', 'Message' : 'Value can not be empty or a space'})
         #return jsonify({ 'Error' : output })
         response = make_response(jsonify({'Error' : output }), 417)
         return response
         
 else:
     output.append({ 'id' : 'SHNK-001', 'Message' : 'Missing requeried field : Please note that "host_name" and "dependent_host_name" are mandatory '})
     #return jsonify({ 'Error' : output })
     response = make_response(jsonify({'Error' : output }), 417)
     return response
 #

@app.route('/<string:version>/dependencies/search/<string:name>', methods=['GET'])
def get_one_depencencies_by_name(name,version):
  output = []
  for fic in glob.glob("/etc/shinken/dependencies/*.cfg"):
      with open(fic) as f:
          contents = f.read()
      if name in contents:
          print (fic)
          output.append({'File' : fic , 'content' : contents.replace('\n',' ').replace('\t',' ') })
  
  return jsonify({'Dependencies' : output , 'count' : len(output) })
  
@app.route('/<string:version>/dependencies/deletematch/<string:name>', methods=['GET'])

def remove_hostdependencies_by_name(name,version):
  
    output = []
    for fic in glob.glob("/etc/shinken/dependencies/*.cfg"):
        with open(fic) as f:
            contents = f.read()
        if name in contents:
            print (fic)
            output.append(fic)
    # Remove all matched files
    if len(output) == 1:
        for fic2remove in output:
            # /!\ risk to remove all config
            os.remove(fic2remove)  
    else:
        output.append({'Error' : 'Too many files to be deleted use ' + request.path + '/force to complete this operation', 'count' : len(output) })
        return jsonify({'Error' : output })
  
    return jsonify({'Deleted files' : output })
  
@app.route('/<string:version>/dependencies/deletematch/<string:name>/force', methods=['GET'])

def remove_force_multiple_hostdependencies_by_name(name,version):
  
    output = []
    for fic in glob.glob("/etc/shinken/dependencies/*.cfg"):
        with open(fic) as f:
            contents = f.read()
        if name in contents:
            print (fic)
            output.append(fic)
    # Remove all matched files
    #if len(output) == 1:
    for fic2remove in output:
            # /!\ risk to remove all config
        os.remove(fic2remove)  
    #else:
    #    output.append({'Error' : 'Too many files to be deleted', 'count' : len(output) })
    #    return jsonify({'Error' : output })
  
    return jsonify({'Deleted Dependencies' : output })  

  
if __name__ == "__main__":
     if platform.system() == "Linux":
        app.run(host='0.0.0.0',port=5000, debug=True)
     elif platform.system() == "Windows": 
        app.run(host='0.0.0.0',port=50000, debug=True)
    


