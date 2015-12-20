#!/usr/bin/python
import MySQLdb
import random
import subprocess
import xmlrpclib
import lxml.etree as etree
import sys
import warnings

# one xmlrpc config
server = 'http://<one_server>:2633/RPC2'
user = "oneadmin"
password = "oneadmin"
one_auth = '{0}:{1}'.format(user, password)

# database connection
db = MySQLdb.connect("<database server>", "<db_user>", "<db_pass>", "<db>")
# create cursor
cursor = db.cursor()
# execute query
with warnings.catch_warnings():
    warnings.simplefilter("ignore")
    cursor.execute("select * from (select concat(d.name, '.', if (b.name is null, '', b.name + '.'), a.name) as hostname  from `dns` d, `domains` a left join `domains` b on b.id=a.parent_id where d.domain_id=a.id) base where hostname like 'node-%connective.be'")
# disconnect from server
db.close()
# existing node list
nodelist = [x[0] for x in cursor.fetchall()]

# dcm script location
dcm = "ona/bin/dcm.pl"
# subnet = "172.20.16.0"
# vmid = 76
vmid = int(sys.argv[1])


class node:

    def newnodenum(self):
        newnum = str(random.getrandbits(16))
        while len(newnum) < 5:
            newnum = "0" + newnum
        newnode = "node-" + str(newnum)
        return newnode

    def new(self):
        newnode = self.newnodenum()
        while newnode in nodelist:
            newnode = self.newnodenum()
        return newnode

    # def newip(self):
    #     newip = subprocess.check_output(dcm + " -r subnet_nextip subnet=" + subnet + " output=dotted", shell=True)
    #     return newip

    def add(self, host, iplist, note="bla"):
        if len(iplist) == 1:
            ip = iplist[0]
            subprocess.check_call(dcm + " -l admin -p admin -r host_add type='2' host=" + host + " ip=" + ip + " notes=" + note, shell=True)
        else:
            subprocess.check_call(dcm + " -l admin -p admin -r host_add type='2' host=" + host + " ip=" + iplist[0] + " notes=" + note, shell=True)
            for ip in iplist[1:]:
                subprocess.check_call(dcm + " -l admin -p admin -r interface_add host=" + host + " ip=" + ip, shell=True)



class vm:

    def getProxy(self):
        return xmlrpclib.ServerProxy(server)

    def getVMInfo(self, vmid):
        response = self.getProxy().one.vm.info(one_auth, vmid)
        if response[0]:
            return response[1]
        else:
            raise Exception(response[1])

    def getVMIP(self, vmid):
        vmxml = self.getVMInfo(vmid)
        vmtree = etree.fromstring(vmxml)
        iplist = [item.text for item in vmtree.iter('IP')]
        return iplist




# add node
node = node()
newnode = str(node.new()) + ".connective.be"
vm = vm()
iplist = vm.getVMIP(vmid)
node.add(newnode, iplist)
