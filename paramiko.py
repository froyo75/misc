#!/usr/bin/python

import sys,os,time
import paramiko

srv_ansible = '192.168.1.130'
login_ansible = 'test'
password_ansible = 'test'
password_root_ansible = 'test'
temp_pkey_name = 'ansi_pkeys'

def connect_ssh(host, port, login, password, rootpassword):
    try:
        c = paramiko.HostKeys()
        c.clear()
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(host, port, username=login, password=password,timeout=20)
        (stdin, stdout, stderr) = ssh.exec_command("id")
        result = stdout.read()
        if result.find('uid=0(root)') == 0:
            chan = ssh.invoke_shell()
            if copy_sshd_config(chan):
                if copy_ssh_key(chan):
                    if service_sshd_reload(chan):
                        print 'Install Success.'
                    else:
                        print "service_sshd_reload failed !"
                        return 0
                else:
                    print "copy_sshd_key failed !"
                    return 0
            else:
                print "copy_sshd_config failed !"
                return 0

        else:
            buff = ""
            chan = ssh.invoke_shell()
            chan.send('su\n')
            while not buff.endswith('Mot de passe : '): #
                resp = chan.recv(9999)
                buff += resp
            time.sleep(3)
            chan.send(rootpassword + '\n')
            buff = ''
            while buff.find('#') < 0 :
                resp = chan.recv(9999)
                buff += resp
            time.sleep(3)
            #cmd = 'ls'
            #chan.send(cmd+'\n')
            if copy_sshd_config(chan):
                if copy_ssh_key(chan):
                    if service_sshd_reload(chan):
                        print 'Install Success.'
                        if test_ssh_pubkey_auth(chan, login, host):
                            print 'Test Success.'
                        else:
                            print 'Test Connection Failed !'
                            return 0
                    else:
                        print "service_sshd_reload failed !"
                        return 0
                else:
                    print "copy_sshd_key failed !"
                    return 0
            else:
                print "copy_sshd_config failed !"
                return 0

        time.sleep(3)
        ssh.close()
        return 1

    except Exception, e:
        print '*** Caught exception: %s: %s' % (e.__class__, e)
        try:
            ssh.close()
        except:
            pass

def copy_ssh_key(chan):
    try:
        buff = ''
        chan.send('scp '+login_ansible+'@'+srv_ansible+':'+temp_pkey_name+' /tmp/\n')
        while buff.find('password:') < 0 :
            resp = chan.recv(9999)
            buff += resp
        chan.send(password_ansible+ '\n')
        time.sleep(3)
        chan.send('cat /tmp/'+temp_pkey_name+' >> /home/test/.ssh/authorized_keys\n')#root ?
        time.sleep(2)
        return 1

    except Exception, e:
                print '*** Caught exception: %s: %s' % (e.__class__, e)


def copy_sshd_config(chan):
    try:
        buff = ''
        chan.send('scp '+login_ansible+'@'+srv_ansible+':test .\n') #:sshd_config /etc/ssh/sshd_config
        #while not buff.endswith('Are you sure you want to continue connecting (yes/no)? '):
        #    resp = chan.recv(9999)
        #    buff += resp
        #chan.send('yes\n')
        time.sleep(1)
        buff = ''
        while buff.find('password:') < 0 :
            resp = chan.recv(9999)
            buff += resp
        chan.send(password_ansible+ '\n')
        time.sleep(2)
        return 1;

    except Exception, e:
                print '*** Caught exception: %s: %s' % (e.__class__, e)

def service_sshd_reload(chan):
    try:
        chan.send('/etc/init.d/ssh reload\n') #service sshd centos
        time.sleep(3)
        return 1
    except Exception, e:
                print '*** Caught exception: %s: %s' % (e.__class__, e)

def test_ssh_pubkey_auth(chan, login_host, srv_host):
    try:
        chan.send('ssh root@'+srv_ansible+'\n')
        time.sleep(1)
        buff = ''
        while buff.find('password:') < 0 :
            resp = chan.recv(9999)
            buff += resp
        chan.send(password_root_ansible+ '\n')
        time.sleep(1)
        buff = ''
        chan.send('ssh '+login_host+'@'+srv_host+'\n')
        while buff.find('~$') < 0 :
                resp = chan.recv(9999)
                buff += resp
        time.sleep(1)
        chan.send('exit\n')
        time.sleep(1)
        chan.send('exit\n')
        time.sleep(2)
        return 1;

    except Exception, e:
                print '*** Caught exception: %s: %s' % (e.__class__, e)

if __name__ == "__main__":

    try:
        with open( "listip", "r" ) as ins:
            for line in ins:
                line = line.strip()
                values = line.split(";")
                host = values[0]
                port = int(values[1])
                login = values[2]
                password = values[3]
                rootpassword = values[4]
                if connect_ssh(host, port, login, password, rootpassword):
                    print host + "==> Config Done.\n"
                    #test success or failed
                time.sleep(3)


    except Exception, e:
                print '*** Caught exception: %s: %s' % (e.__class__, e)