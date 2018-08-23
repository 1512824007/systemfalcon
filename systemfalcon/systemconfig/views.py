# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render,HttpResponse,HttpResponseRedirect
from django.contrib.auth.decorators import login_required,permission_required
from systemconfig.models import Tool,Host,ParameterGroup,HostGroup,Private_file,Parameter,Private_Template,Pack,SLS,Pub_File
from django.db.models import Q
import mysql_salt
from openfalcon import mysql_falcon,mysql_oms
from HcGraph import mysql
#from django.core.paginator import Paginator,InvalidPage,EmptyPage
import json
import os
import time
from userauth.is_group import is_group
#import salt
import local
import sync_file
import shutil
import stat
#import commands
import conf_dir
#from django.http import JsonResponse
import logging
from logging.handlers import TimedRotatingFileHandler
from django.contrib import messages

# Create your views here.
db = mysql.db_operate()
db_falcon = mysql_falcon.db_operate()
db_oms = mysql_oms.db_operate()
db_salt = mysql_salt.db_operate()

pub_dir = conf_dir.conf['pub_dir']
prv_dir = conf_dir.conf['prv_dir']
pub_sls = conf_dir.conf['pub_sls']
prv_sls = conf_dir.conf['prv_sls']
root_dir = conf_dir.conf['root_dir']
plugin_path = conf_dir.conf['plugin_path']
client_plugin_path = conf_dir.conf['client_plugin_path']
git = conf_dir.conf['plugin_git']

#打印日志到文件中
LOG_FILENAME = "/systemfalcon/systemfalcon/sysconf/log/ChangeLog.txt"
logger = logging.getLogger()
handler = TimedRotatingFileHandler(LOG_FILENAME,
                                  when='D',interval=1,backupCount=40,
                                  )
fmt = '%(asctime)s - %(filename)s:%(lineno)s - %(name)s - %(message)s'
formatter = logging.Formatter(fmt)
handler.setFormatter(formatter)
logger.addHandler(handler)
logger.setLevel(logging.NOTSET)


@permission_required('openfalcon.change')
def MonitorManage(request):
    '''系统配置'''
    return render(request, 'view/MonitorManage.html',locals())

@login_required
def ConfigCreat(request):
    """配置添加管理"""
    if request.method == "POST":
        if request.POST.get("adding",None):
            try:
                info = request.POST['info']
                filename = request.POST['filename']
                dir_info='{0}/{1}'.format(prv_dir,filename)
                dir_name = os.path.split(dir_info)
                if os.path.isdir(dir_name[0]):
                    f = open('{0}/{1}'.format(prv_dir,filename),'w')
                    f.write(info)
                    f.close()
                    messages.success(request,'提交成功')
                    return HttpResponseRedirect('/monitor/MonitorManage/ConfigCreat/')
                else:
                    os.makedirs(dir_name[0])
                    f = open('{0}/{1}'.format(prv_dir,filename), 'w')
                    f.write(info)
                    f.close()
                    messages.success(request, '提交成功')
                    return HttpResponseRedirect('/monitor/MonitorManage/ConfigCreat/')
            except Exception as e:
                print(e)
                messages.error(request, '提交失败')
                return HttpResponseRedirect('/monitor/MonitorManage/ConfigCreat/')
    return render(request,'view/systemconfig/ConfigCreate.html')


@login_required
def ConfigManag(request,args):
    """配置下发管理"""
    if args.startswith('/'): args = args[1:]
    f = open('{1}/{0}'.format(args,prv_dir), "r")
    file = f.read()
    f.close()
    if request.method == "POST":
        if request.POST.get("updating",None):
            try:
                info = request.POST['info']
                f = open('{1}/{0}'.format(args,prv_dir), 'w')
                f.write(info)
                f.close()
                messages.success(request, '提交成功')
                return HttpResponseRedirect('/monitor/MonitorManage/ConfigManag/{0}/'.format(args))
            except Exception as e:
                print(e)
                messages.error(request, '提交失败')
                return HttpResponseRedirect('/monitor/MonitorManage/ConfigManag/{0}/'.format(args))
        elif request.POST.get('pushing',None):
            try:
                add = os.system('cd {1} && git add {0}'.format(args,prv_dir))
                commit = os.system('cd {1} &&  git commit -m "/{0}"'.format(args,prv_dir))
                push = os.system('cd {0} && git push'.format(prv_dir))
                if add == 0 and push==0 and commit==0:
                    messages.success(request, '提交成功')
                    return HttpResponseRedirect('/monitor/MonitorManage/ConfigFileList/')
                else:
                    messages.error(request, '提交失败')
                    return HttpResponseRedirect('/monitor/MonitorManage/ConfigManag/{0}/'.format(args))
            except Exception as e:
                print (e)
                messages.error(request, '提交失败')
                return HttpResponseRedirect('/monitor/MonitorManage/ConfigManag/{0}/'.format(args))
    return render(request,'view/systemconfig/ConfigManage.html',{'file':file,'file_name':args})

@login_required
def ConfigFileList(request):
    """配置文件目录列表管理"""
    def del_rw(action, name, exc):
        os.chmod(name, stat.S_IWRITE)
        os.remove(name)
    files_list=[]
    if request.method == "POST":
        if request.POST.get('loading',None):
            shutil.rmtree('{0}'.format(plugin_path),onerror=del_rw)
            output = os.system('cd {0} && git clone {1}'.format(root_dir,git))
            if output==0:
                messages.success(request,'Clone成功！')
                return HttpResponseRedirect('/monitor/MonitorManage/ConfigFileList/')
            else:
                print(output)
                messages.error(request,'clone失败')
                return HttpResponseRedirect('/monitor/MonitorManage/ConfigFileList/')
        elif request.POST.get('pulling',None):
            try:
                os.system('cd {0} && git pull '.format(prv_dir))
                messages.success(request,'提交成功')
                return HttpResponseRedirect('/monitor/MonitorManage/ConfigFileList/')
            except Exception as e:
                print(e)
                pass
        elif request.POST.get('deleting', None):
            try:
                list_info = request.POST.getlist('id')
                if len(list_info):
                    for i in list_info:
                        os.system('cd {1} && rm {0}'.format(i[1:],prv_dir))
                        Private_Template.objects.filter(private_template_dir=i).delete()
                return HttpResponseRedirect('/monitor/MonitorManage/ConfigFileList/')
            except Exception as e:
                print(e)
                return HttpResponseRedirect('/monitor/MonitorManage/ConfigFileList/')
        '''
        elif request.POST.get('pushing_all',None):
            try:
                dirlist = '{0}'.format(prv_dir)
                info = sync_file.get_filepaths(dirlist)
                for i in info:
                    timeStamp = os.stat(i).st_mtime
                    timeTuple = time.localtime(timeStamp)
                    file_time = time.strftime("%Y-%m-%d %H:%M:%S", timeTuple)
                    files = os.path.split(i)
                    data = [file_time, files]
                    if files[1].find('.cfg') != -1:
                        files_list.append(data)
                    elif files[0].find('pub_plugin') != -1:
                        pass
                add_mod =""
                add_mod_error =""
                add_mod_other_error =""
                list_info = request.POST.getlist('id')
                if len(list_info):
                    for i in list_info:
                        add = os.system('cd {1} && git add {0}'.format(i,prv_dir))
                        commit = os.system('cd {1} &&  git commit -m "{0}"'.format(i,prv_dir))
                        push = os.system('cd {0} && git push'.format(prv_dir))

                        if add == 0 and push==0 and commit==0:
                            add_mod += i + "\n"
                        elif add == 0 and push == 0 and commit == 1:
                            add_mod_error += i+" "+"状态码:"+"git add:{0}".format(add)+" "+"git commit：{0}".format(commit)+" "+"git push:{0}".format(push)
                        else:
                            add_mod_other_error += i+" "+"状态码:"+"git add:{0}".format(add)+" "+"git commit:{0}".format(commit)+" "+"git push:{0}".format(push)
                    return render(request,'view/systemconfig/ConfigFileList.html',{'add_mod_error':add_mod_error,'add_mod':add_mod,'files_list':files_list,'add_mod_other_error':add_mod_other_error})
                else:
                    return HttpResponseRedirect('/monitor/MonitorManage/ConfigFileList/')
            except Exception as e:
                print(e)
                messages.error(request, '提交失败')
                return HttpResponseRedirect('/monitor/MonitorManage/ConfigFileList/')
        '''
    else:
        dirlist = '{0}'.format(prv_dir)
        info = sync_file.get_filepaths(dirlist)
        for i in info:
            timeStamp= os.stat(i).st_mtime
            timeTuple = time.localtime(timeStamp)
            file_time = time.strftime("%Y-%m-%d %H:%M:%S", timeTuple)
            files = os.path.split(i.replace(prv_dir,''))
            data = [file_time,files]
            files_list.append(data)
    return render(request,'view/systemconfig/ConfigFileList.html',{'files_list':files_list})

@login_required
def ConfigGitdiff(request,obj1):
    if obj1.startswith('/'):obj1 = obj1[1:]
    s = os.popen('cd {0}&&git diff {1}'.format(prv_dir,obj1)).read()
    d = s.split('\n')
    return render(request,'view/systemconfig/ConfigGitdiff.html',locals())


@login_required
def ConfigGitstatus(request,):
    if request.method == 'POST':
        os.chdir(plugin_path)
        if request.POST.get('git_add', None):
            u_list = request.POST['add1']
            add_file = list(eval(u_list))
            for i in add_file:
                os.system('git add {0}'.format(i.split('\t')[1]))
            return HttpResponseRedirect('/monitor/MonitorManage/ConfigGitstatus/')
        elif request.POST.get('git_add2', None):
            c_n_list = request.POST['add2']
            for i in list(eval(c_n_list)):
                if 'deleted:' in i:
                    del_file = i.split('deleted:    ')[1]
                    os.system('git rm {0} -f'.format(del_file))
                elif 'modified:' in i:
                    mod_file = i.split('modified:   ')[1]
                    os.system('git add {0}'.format(mod_file))
            return HttpResponseRedirect('/monitor/MonitorManage/ConfigGitstatus/')
        elif request.POST.get('git_push', None):
            c_c_list = request.POST['commit']
            os.system('git commit -m "{0}" && git push '.format(c_c_list))
            return HttpResponseRedirect('/monitor/MonitorManage/ConfigGitstatus/')
    s = os.popen('cd {0} &&git status'.format(plugin_path)).read()
    d = s.split('\n')
    c_c_index = u_index = c_n_index = len(d)
    c_c_list ,u_list, c_n_list = [],[],[]
    for index, i in enumerate(d):
        if i.startswith('# Changes to be committed:'):
            c_c_index = index
        elif i.startswith('# Changed but not updated:'):
            c_n_index = index
        elif i.startswith('# Untracked files:'):
            u_index = index
    for index, i in enumerate(d):
        if 'falcon_plugin' in i:
            if index < c_n_index and c_n_index <= u_index <= len(d) and index > c_c_index:
                c_c_list += [i]
            elif index < u_index <= len(d):
                c_n_list += [i]
            elif index > u_index :
                u_list += [i]
        else:
            continue
    return render(request,'view/systemconfig/ConfigGitstatus.html',locals())


@login_required
def ConfigPush(request,args,kargs):
    """单文件Push操作"""
    try:
        add = os.system('cd {2} && git add {0}/{1}'.format(args.replace('/','',1), kargs,prv_dir))
        if add == 0:
            commit = os.system('cd {2} &&  git commit -m "{0}/{1}"'.format(args.replace('/','',1), kargs,prv_dir))
            if commit == 0:
                push = os.system('cd {0} && git push'.format(prv_dir))
                if push == 0 :
                    messages.success(request, '提交成功')
                    return HttpResponseRedirect('/monitor/MonitorManage/ConfigFileList/')
        messages.error(request, '提交失败')
        return HttpResponseRedirect('/monitor/MonitorManage/ConfigFileList')
    except Exception as e:
        print(e)
        messages.error(request, '提交失败')
        return HttpResponseRedirect('/monitor/MonitorManage/ConfigFileList')

@login_required
def ConfigToolPush(request,args,kargs):
    """单文件Push操作"""
    try:
        add = os.system('cd {2} && git add {0}/{1} &>>./log.log'.format(args, kargs,prv_dir))
        commit = os.system('cd {2} &&  git commit -m "{0}/{1}" &>>./log.log'.format(args, kargs,prv_dir))
        push = os.system('cd {2} && git push &>>./log.log'.format(prv_dir))

        if add == 0 and push == 0 and commit == 0:
            messages.success(request, '提交成功')
            return HttpResponseRedirect('/monitor/MonitorManage/ConfigToolList/')
        else:
            messages.error(request, '提交失败')
            return HttpResponseRedirect('/monitor/MonitorManage/ConfigToolList')
    except Exception as e:
        print e
        messages.error(request, '提交失败')
        return HttpResponseRedirect('/monitor/MonitorManage/ConfigToolList')



@login_required
def ConfigFileUpload(request):
    """上传文件列表"""
    dirs = '{0}'.format(prv_dir)
    file_dir = sync_file.get_filepaths(dirs)
    files_list =[]
    for i in file_dir:
        files =  os.path.split(i)
        if files[0].find('.git') == -1:
            files_list.append(files[0])
        elif files[0].find('.git') != -1:
            pass
    files_list_uniq = list(set(files_list))
    print files_list_uniq
    return render(request,'view/systemconfig/ConfigFileUpload.html',{'files_list_uniq':files_list_uniq})

@login_required
def ConfigFileUploadInput(request,args):
    """具体上传的文件"""
    if request.method == "POST":
        dstatus=""
        myFile = request.FILES.getlist("file_name", None)  # 获取上传的文件，如果没有文件，则默认为None
        for i in myFile:
            if not i:
                dstatus = "<label style='color: #E74C3C'>请选择需要上传的文件!</label>"
            else:
                path_dst_file = '{0}/{1}'.format(args,i)
                if os.path.isfile(path_dst_file):
                    dstatus += "\n"+"<label style='color: #E74C3C'>%s 已存在,请重名名或者重新选择文件。</label>" % (i)+"\n"
                else:
                    destination = open('{0}/{1}'.format(args,i), 'wb+')  # 打开特定的文件进行二进制的写操作
                    for chunk in i.chunks():  # 分块写入文件
                        destination.write(chunk)
                    destination.close()
                    os.system('dos2unix {0}'.format(path_dst_file))
                    dstatus += "\n"+"<label style='color: #2ECC71'>%s 文件上传成功!&nbsp;&nbsp;&nbsp;</label>" % (i)+"\n"
                    # messages.success(request,'上传成功')
        return render(request, 'view/systemconfig/ConfigFileUploadInput.html',{'dstatus':dstatus,'args':args})
    return render(request,'view/systemconfig/ConfigFileUploadInput.html',{'args':args})

@is_group('sys')
def ConfigHost(request):
    """设备监控列表"""
    group_list = HostGroup.objects.all()
    host_list = Host.objects.all()
    falcon_host_list_sql = 'select  hostname,ip from host;'
    room_list_sql = 'select d.hostname,i.name from idc_idc as i,device_server as d where d.idc_id=i.id;'
    room_list0 = db_oms.mysql_command(room_list_sql)
    room_list =  json.dumps(room_list0)
    falcon_host_list = db_falcon.mysql_command(falcon_host_list_sql)
    salt_key_list ,salt_minions_pre = [],[]
    for root, dir, file in os.walk('/etc/salt/pki/master/minions'):
        salt_key_list += file
    for root, dir, file in os.walk('/etc/salt/pki/master/minions_pre'):
        salt_minions_pre += file
    def sync_node_group_of_salt(node_group):
        p = conf_dir.conf['salt-master_conf']
        with open(p, 'r') as f:
            c = f.read()
            start = c.find('nodegroups:\n')+len('nodegroups:')
            pos = c.find('#nodegroups:\n')
            end = c.find('#  group1:')
        with open(p, 'w') as f:
            if pos == -1:
                content = c[:start] + node_group + c[end:]
            else:
                content = c[:start] +'\nnodegroups:\n'+ node_group + c[end:]
            f.write(content)

    if request.method == "POST":
        if request.POST.get('host_add',None):
            hostname = request.POST['hostname']
            ip = request.POST['ip']
            host_room = request.POST['host_room']
            host_grp = request.POST['host_grp']
            if len(hostname) and len(ip) and len(host_room) and len(host_grp):
                try:
                    _id = HostGroup.objects.get(id=int(host_grp))
                    Host.objects.create(hostname=hostname,ip=ip,host_room=host_room,host_grp=_id)
                except Exception as e:
                    print(e)
                    messages.error(request,'提交失败')
                    return HttpResponseRedirect('/monitor/MonitorManage/ConfigHost/')
            else:
                error = "请填写全部内容！！"
                return render(request, 'view/systemtools/ConfigHostList.html',
                              {'group_list': group_list, 'error': error,'host_list':host_list,
                                'falcon_host_list':falcon_host_list,'room_list':room_list})

        elif request.POST.get('deleting',None):
            host_id = request.POST.getlist('id')
            if len(host_id):
                try:
                    Host.objects.filter(id__in=host_id).delete()

                    host_grp = HostGroup.objects.all()
                    node_group = ''
                    for i in host_grp:
                        h_tmp = ''
                        for x in Host.objects.filter(host_grp=i.id).values_list('hostname'):
                            h_tmp += x[0] + ','
                        node_group += "  {0}: 'L@{1}'\n".format(i.host_group,h_tmp)
                    sync_node_group_of_salt(node_group)
                    messages.success(request,'提交成功')
                    return HttpResponseRedirect('/monitor/MonitorManage/ConfigHost/')
                except Exception as e:
                    print(e)
                    messages.error(request,'提交失败')
                    return HttpResponseRedirect('/monitor/MonitorManage/ConfigHost/')
            else:
                return HttpResponseRedirect('/monitor/MonitorManage/ConfigHost/')
        elif not request.POST.has_key('host_add') and  request.POST.has_key('hostadd'):
                host_messsage = eval(request.POST.get('hostadd',None).encode('UTF-8').replace('null',''))
                ip = host_messsage[0]
                hostname = host_messsage[1]
                host_grp = host_messsage[2]
                try:
                    host_room = host_messsage[3]
                except Exception as e:
                    host_room = ""
                if len(hostname) and len(ip) and len(host_grp):
                    _id = HostGroup.objects.get(host_group=host_grp)
                    Host.objects.create(hostname=hostname, ip=ip, host_room=host_room, host_grp=_id)

                    host_grp = HostGroup.objects.all()
                    node_group = ''
                    for i in host_grp:
                        h_tmp = ''
                        for x in Host.objects.filter(host_grp=i.id).values_list('hostname'):
                            h_tmp += x[0] + ','
                        node_group += "  {0}: 'L@{1}'\n".format(i.host_group, h_tmp)
                    sync_node_group_of_salt(node_group)
                return HttpResponse('提交成功')

        elif not request.POST.has_key('host_add') and  request.POST.has_key('groupname'):
                host_grp = request.POST.get('groupname',None)
                _id = HostGroup.objects.get(host_group=host_grp)
                host_name_list_sql = "select h.hostname,h.ip from host as h,grp_host as gh,grp as g where h.id=gh.host_id and gh.grp_id = g.id and g.grp_name = '{0}';".format(host_grp)
                host_name_list = db_falcon.mysql_command(host_name_list_sql)
                create_list = []
                for i in host_name_list:
                    hostname = i[0]
                    ip = i[1] 
                    create_list.append(Host(hostname=hostname, ip=ip, host_room='temp_room', host_grp=_id))
                    #for j in room_list0:
                    #    if j[0]== hostname:
                    #        host_room = j[1]
                    #        create_list.append(Host(hostname=hostname, ip=ip, host_room=host_room, host_grp=_id))
                try:
                    Host.objects.bulk_create(create_list)
                    return HttpResponse('添加成功')
                except Exception as e:
                    print(e)
                    messages.error(request, '提交失败')
                    return HttpResponse('批量添加失败（可能已有设备同步过）')
        elif request.POST.get('acceptrsa', None):
            host_id = request.POST.getlist('id')
            if len(host_id):
                try:
                    for i in host_id:
                        os.system('salt-key -a {0} -y'.format(Host.objects.get(id=int(i)).hostname))
                    messages.success(request, '提交成功')
                    return HttpResponseRedirect('/monitor/MonitorManage/ConfigHost/')
                except Exception as e:
                    print(e)
                    messages.error(request,'提交失败')
                    return HttpResponseRedirect('/monitor/MonitorManage/ConfigHost/')
    return render(request, 'view/systemtools/ConfigHostList.html',locals())

@login_required
def ConfigHostListStatus(request):
    if request.POST.has_key('host'):
        host = request.POST['host'].encode('UTF-8')
        import salt.client
        salt_local = salt.client.LocalClient()
        try:
            result = salt_local.cmd(host,'test.ping').values()
            if result[0] == True:
                return HttpResponse("True")
        except Exception as e:
            print(e)
            return HttpResponse("False")
    return HttpResponse("False")

@login_required
def ConfigHostDetail(request,pk):
    """主机列表详情管理"""
    host_list = Host.objects.filter(id=pk)
    b = Host.objects.get(id=pk)
    tool_list = Private_Template.objects.all()
    config_pak = b.private_file_set.filter(private_class='config')
    config_tool = b.private_file_set.filter(private_class='tool')
    config_sls = b.private_file_set.filter(private_class='sls')
    return render(request,'view/systemtools/ConfigHostDetail.html',{'host_list':host_list,'config_pak':config_pak,'config_tool':config_tool,'pk':pk,'config_sls':config_sls,'tool_list':tool_list})


@login_required
def ConfigHostDetailAddUpdateDelete(request):
    """采集工具及参数配置包管理"""
    if request.method == "POST":
        hostname_id = request.POST['hostname_id']
        if request.POST.get('tool_del',None):
            pk_id = request.POST['pk_id']
            host_id = request.POST['host_id']
            tool_dir = request.POST['tool_dir']

            pack_id = request.POST['pack_id']
            pack_dir = request.POST['pack_dir']

            sls_id = request.POST['sls_id']
            sls_dir = request.POST['sls_dir']
            try:
                git_status = 'cd {0} && git status 2&>/dev/null'.format(prv_dir)
                git_exist = os.system(git_status)
                if git_exist == 0:
                    os.system('cd {1} && git rm {0} && git rm {2}'.format(pack_dir,prv_dir,sls_dir))
                    os.system('cd {1} &&  git commit -m "remove {0}" && git commit -m "remove {2}"'.format(pack_dir,prv_dir,sls_dir))
                    os.system('cd {0} && git push'.format(prv_dir))
                else:
                    os.system('cd {1} &&  rm {0} && rm {2}'.format(pack_dir, prv_dir, sls_dir))
                Private_file.objects.filter(id=pack_id).filter(private_host_id=host_id).delete()
                Private_file.objects.filter(id=sls_id).filter(private_host_id=host_id).delete()
                Private_file.objects.filter(id=pk_id).filter(private_host_id=host_id).delete()
                messages.success(request,'提交成功')
            except:
                messages.error(request,'提交失败')
                return HttpResponseRedirect('/monitor/MonitorManage/ConfigHost/detail/%s/' % (host_id))
        if request.POST.get('tool_add',None):
            #绑定工具
            dstatus=""
            hostname = request.POST['hostname']
            hostname_id = request.POST['hostname_id']
            template_name = request.POST['template_name']
            paramater_dict = request.POST['paramater_dict']

            if paramater_dict == "":
                return  HttpResponseRedirect('/monitor/MonitorManage/ConfigHost/detail/%s/'% (hostname_id))
            try:
                template_tool = Private_Template.objects.filter(
                    private_template_name=template_name).values_list('private_template_name',
                                                                     'private_template_file_name',
                                                                     'private_template_dir', 'private_template_class',
                                                                     'private_template_context')
                template_conf = Private_Template.objects.filter(
                    private_template_file_name__startswith=template_name).filter(
                    private_template_class='config').values_list('private_template_name', 'private_template_file_name',
                                                                 'private_template_dir', 'private_template_class',
                                                                 'private_template_context')

                #配置文件生成
                f = open('{0}'.format(template_conf[0][2]),'r')
                config_info = f.read()
                data = (eval(config_info))
                para_list= (eval(paramater_dict))
                for key,value in para_list.items():
                    if key in data:
                        data[key]=value
                DB = data
                data_result = json.dumps(DB,indent=4, sort_keys=False, ensure_ascii=False)
                conf_dir='{0}/{1}/{2}'.format(prv_dir,hostname,template_conf[0][1])
                os.system('mkdir -p {0}/{1}'.format(prv_dir,hostname))
                if os.path.isfile(conf_dir):
                    messages.error(request,'提交失败,配置文件冲突,请先删除')
                    return HttpResponseRedirect('/monitor/MonitorManage/ConfigHost/detail/%s/' % (hostname_id))
                else:
                    f1 = open(conf_dir, 'a')
                    f1.write(data_result)
                    f1.close()
                    git_status = 'cd {0} && git status 2&>/dev/null'.format(prv_dir)
                    git_exist = os.system(git_status)
                    if git_exist == 0:
                        add = os.system('cd {1} && git add {0}'.format(conf_dir, prv_dir))
                        commit = os.system('cd {1} &&  git commit -m "{0}"'.format(conf_dir, prv_dir))
                        push = os.system('cd {0} && git push'.format(prv_dir))
                        if add == 0 and push == 0 and commit == 0:
                            Private_file.objects.create(private_name=hostname+'_'+template_conf[0][1],private_host=Host.objects.get(id=int(hostname_id)),private_dir=conf_dir
                                                                    ,private_file_name=template_conf[0][1],private_class=template_conf[0][3],private_context=template_conf[0][4])
                        else:
                            messages.error(request, '提交失败')
                            return HttpResponseRedirect('/monitor/MonitorManage/ConfigHost/detail/%s/' % (hostname_id))
                    else:
                        Private_file.objects.create(private_name=hostname + '_' + template_conf[0][1],
                                                                private_host=Host.objects.get(
                                                                    id=int(hostname_id)), private_dir=conf_dir
                                                                , private_file_name=template_conf[0][1],
                                                                private_class=template_conf[0][3],
                                                                private_context=template_conf[0][4])
                #sls文件生成
                toolname = str(template_tool[0][1]).split('.')[0]+'.sls'
                sls_info_tool = """falcon_{1}_sh:
                                file.managed:
                                - name: /usr/local/open-falcon/GS-falcon-agent-5.1.1/plugin/net/{0}
                                - source: 
                                  - salt://business/falcon_plugin/pub_plugin/{0}
                                - user: root
                                - group: root
                                - mode: 755
                                - makedirs: true\n""".format(template_tool[0][1],template_tool[0][0])
                sls_info_config = """falcon_{1}_conf:
                                file.managed:
                                - name: /usr/local/open-falcon/GS-falcon-agent-5.1.1/plugin/net/{0}
                                - source: 
                                  - salt://business/falcon_plugin/pub_plugin/{0}
                                - user: root
                                - group: root
                                - mode: 644
                                - makedirs: true""".format(template_conf[0][1],template_tool[0][0])

                path_dst_file = '{0}/{1}/{2}'.format(prv_dir,hostname,toolname)
                print(path_dst_file)
                if os.path.isfile(path_dst_file):
                    messages.error(request,'提交失败')
                    return HttpResponseRedirect('/monitor/MonitorManage/ConfigHost/detail/%s/' % (hostname_id))
                else:
                    try:
                        sls_file = open(path_dst_file, 'a')
                        sls_file.write(sls_info_tool)
                        sls_file.write(sls_info_config)
                        sls_file.close()
                        git_status = 'cd {0} && git status 2&>/dev/null'.format(prv_dir)
                        git_exist = os.system(git_status)
                        if git_exist == 0:
                            add = os.system('cd {1} && git add {0}'.format(path_dst_file, prv_dir))
                            commit = os.system('cd {1} &&  git commit -m "{0}"'.format(path_dst_file, prv_dir))
                            push = os.system('cd {0} && git push'.format(prv_dir))
                            if add == 0 and push == 0 and commit == 0:
                                Private_file.objects.create(private_name=hostname + '_' + toolname,
                                                                        private_host=Host.objects.get(
                                                                            id=int(hostname_id)),
                                                                        private_dir=path_dst_file
                                                                        , private_file_name=toolname,
                                                                        private_class='sls',
                                                                        private_context='sls文件是saltstack配置文件')
                            else:
                                messages.error(request, '提交失败')
                                return HttpResponseRedirect('/monitor/MonitorManage/ConfigHost/detail/%s/' % (hostname_id))
                        else:
                            Private_file.objects.create(private_name=hostname + '_' + toolname,
                                                                    private_host=Host.objects.get(
                                                                        id=int(hostname_id)),
                                                                    private_dir=path_dst_file
                                                                    , private_file_name=toolname,
                                                                    private_class='sls',
                                                                    private_context='sls文件是saltstack配置文件')
                    except Exception as e:
                        print(e)
                        messages.error(request, '提交失败')
                        return HttpResponseRedirect('/monitor/MonitorManage/ConfigHost/detail/%s/' % (hostname_id))

                # 工具处理
                Private_file.objects.create(private_name=hostname + '_' + template_tool[0][1],
                                                                private_host=Host.objects.get(
                                                                    id=int(hostname_id)),
                                                                private_dir=template_tool[0][2]
                                                                , private_file_name=template_tool[0][1],
                                                                private_class=template_tool[0][3],
                                                                private_context=template_tool[0][4])

                messages.success(request, '提交成功')
                return HttpResponseRedirect('/monitor/MonitorManage/ConfigHost/detail/%s/' % (hostname_id))
            except Exception as e:
                print(e)
                messages.error(request, '提交失败')
                return HttpResponseRedirect('/monitor/MonitorManage/ConfigHost/detail/%s/' % (hostname_id))
    return HttpResponseRedirect('/monitor/MonitorManage/ConfigHost/detail/%s/'%(hostname_id))


@login_required
def ConfigHostInfoDetail(request,pk):
    """主机信息管理"""
    host_list = Host.objects.filter(id=pk)
    group_list = HostGroup.objects.all()
    if request.method == "POST":
        hostname = request.POST['hostname']
        ip = request.POST['ip']
        host_room = request.POST['host_room']
        host_group = request.POST['host_group']
        try:
            Host.objects.filter(id=pk).update(hostname=hostname,ip=ip,host_room=host_room,host_grp=host_group)
            messages.success(request,'提交成功！')
            return HttpResponseRedirect('/monitor/MonitorManage/ConfigHost/hostdetail/%s/' % (pk))
        except Exception as e:
            print(e)
        return HttpResponseRedirect('/monitor/MonitorManage/ConfigHost/hostdetail/%s/'%(pk))
    return render(request,'view/systemtools/ConfigHostInfoDetail.html',{'host_list':host_list,'pk':pk,'group_list':group_list})

@login_required
def ConfigHostPack(request,host_id):
    """主机参数包添加管理"""
    host_list = Host.objects.filter(id=host_id)
    parameter = Parameter.objects.filter(parameter_default_id=0)
    parameter_default = Parameter.objects.filter(parameter_default_id=1)
    add_mod = ""
    add_mod_error = ""
    add_mod_other_error = ""
    if request.method == "POST":
        if request.POST.get('adding',None):
            para_name = request.POST['para_name']
            para = request.POST.getlist('para')
            para_default = request.POST.getlist('para_default')
            hostname = host_list.values_list('hostname')[0][0]
            para_count = Pack.objects.filter(pack_host=host_id).filter(pack_name=para_name)

            if len(para_count):
                info = '该参数包已经存在，请重新命名或者修改该参数包内容即可！'
                return render(request, 'view/systemtools/ConfigHostPack.html',
                              {'host_id': host_id, 'host_list': host_list, 'parameter': parameter,
                               'parameter_default': parameter_default, 'info': info})
            else:
                data = (
                    Q(id__in=para)|
                    Q(id__in=para_default)
                )
                para_info = Parameter.objects.filter(data).values_list('parameter_context')
                ret=""
                for i in para_info:
                    ret += i[0]+"\n"
                try:
                    path_dst_file = "{2}/{0}/{1}".format(hostname, para_name,prv_dir)
                    dir_info = '{1}/{0}/'.format(hostname,prv_dir)
                    dir_name = os.path.split(dir_info)
                    # print dir_name[0]

                    config_host_detail = '/monitor/MonitorManage/ConfigHost/detail/{0}/'.format(host_id)
                    if not os.path.isdir(dir_name[0]):
                        os.makedirs(dir_name[0])

                    add_mod += path_dst_file + "\n"
                    Pack.objects.create(pack_name=para_name, pack_context=",".join(para),
                                                    pack_base_context=",".join(para_default),
                                                    pack_host=Host.objects.get(id=host_id),
                                                    pack_dir=path_dst_file)
                    f = open('{0}'.format(path_dst_file), 'w')
                    f.write(ret)
                    f.close()
                    messages.success(request, '提交成功')
                    return HttpResponseRedirect(config_host_detail)
                except Exception as e:
                    print(e)
                    messages.error(request,'提交失败')
                    return HttpResponseRedirect('/monitor/MonitorManage/ConfigHost/{0}/ConfigHostPack/'.format(host_id))


    return render(request,'view/systemtools/ConfigHostPack.html',{'host_id':host_id,'host_list':host_list,'parameter':parameter,'parameter_default':parameter_default,'add_mod':add_mod,'add_mod_error':add_mod_error,'add_mod_other_error':add_mod_other_error})

@login_required
def ConfigHostSls(request,host_id):
    """SLS文件添加管理"""
    host_list = Host.objects.filter(id=host_id)
    add_mod = ""
    add_mod_error = ""
    add_mod_other_error = ""
    if request.method == "POST":
        if request.POST.get('adding',None):
            sls_name = request.POST['sls_name']
            sls_info = request.POST['sls_info']
            sls_context = request.POST['sls_context']
            hostname = host_list.values_list('hostname')[0][0]
            sls_count = SLS.objects.filter(sls_host=host_id).filter(sls_name=sls_name)

            if len(sls_count):
                info = '该参数包已经存在，请重新命名或者修改该参数包内容即可！'
                return render(request, 'view/systemtools/ConfigHostSls.html',
                              {'host_id': host_id, 'host_list': host_list, 'info': info})
            else:
                try:
                    path_dst_file = "{2}/{0}/{1}".format(hostname, sls_name,prv_dir)
                    dir_info = '{1}/{0}/'.format(hostname,prv_dir)
                    dir_name = os.path.split(dir_info)
                    # print dir_name[0]

                    if os.path.isdir(dir_name[0]):
                        f = open('{0}'.format(path_dst_file), 'w')
                        f.write(sls_info)
                        f.close()

                        add_mod += path_dst_file + "\n"
                        SLS.objects.create(sls_name=sls_name, sls_context=sls_context,
                                                       sls_host=Host.objects.get(id=host_id),
                                                       sls_dir=path_dst_file)
                        messages.success(request, '提交成功')
                        return HttpResponseRedirect('/monitor/MonitorManage/ConfigHost/detail/{0}/'.format(host_id))

                    else:
                        os.makedirs(dir_name[0])
                        f = open('{0}'.format(path_dst_file), 'w')
                        f.write(sls_info)
                        f.close()

                        add_mod += path_dst_file + "\n"
                        SLS.objects.create(sls_name=sls_name, sls_context=sls_context,
                                                       sls_host=Host.objects.get(id=host_id),
                                                       sls_dir=path_dst_file)
                        messages.success(request, '提交成功')
                        return HttpResponseRedirect('/monitor/MonitorManage/ConfigHost/detail/{0}/'.format(host_id))

                except Exception as e:
                    print(e)
                    messages.error(request,'提交失败')
                    return HttpResponseRedirect('/monitor/MonitorManage/ConfigHost/{0}/ConfigHostSls/'.format(host_id))


    return render(request,'view/systemtools/ConfigHostSls.html',{'host_id':host_id,'host_list':host_list,'add_mod':add_mod,'add_mod_error':add_mod_error,'add_mod_other_error':add_mod_other_error})


@login_required
def ConfigHostSlsUpdate(request,host_id,pk):
    """SLS文件修改管理"""
    pack = Private_file.objects.filter(private_host=Host.objects.get(id=host_id)).filter(id=pk)
    host_list = Host.objects.filter(id=host_id)
    config_dir=pack.values_list('private_dir')[0][0]
    f1 = open(config_dir, 'r')
    info = f1.read()
    f1.close()
    if request.method == "POST":
        hostname = host_list.values_list('hostname')[0][0]
        config_file_content = request.POST['config_file_content']
        try:
            add_mod_error =""
            add_mod_other_error =""
            path_dst_file = config_dir
            dir_info = '{1}/{0}/'.format(hostname,prv_dir)
            dir_name = os.path.split(dir_info)
            if os.path.isdir(dir_name[0]):
                f = open('{0}'.format(path_dst_file), 'w')
                f.write(config_file_content)
                f.close()
                add = os.system('cd {1} && git add {0}'.format(path_dst_file,prv_dir))
                commit = os.system('cd {1} &&  git commit -m "{0}"'.format(path_dst_file,prv_dir))
                push = os.system('cd {0} && git push'.format(prv_dir))
                if add == 0 and push == 0 and commit == 0:
                    messages.success(request, '提交成功')
                    return HttpResponseRedirect('/monitor/MonitorManage/ConfigHost/detail/{0}/'.format(host_id))
                elif add == 0 and push == 0 and commit == 1:
                    add_mod_error += path_dst_file + " " + "状态码:" + "git add:{0}".format(
                        add) + " " + "git commit：{0}".format(commit) + " " + "git push:{0}".format(push)
                    messages.error(request, '提交失败')
                    return HttpResponseRedirect('/monitor/MonitorManage/ConfigHost/detail/{0}/'.format(host_id))
                else:
                    add_mod_other_error += path_dst_file + " " + "状态码:" + "git add:{0}".format(
                        add) + " " + "git commit:{0}".format(commit) + " " + "git push:{0}".format(push)
                    messages.error(request, '提交失败')
                    return HttpResponseRedirect('/monitor/MonitorManage/ConfigHost/detail/{0}/'.format(host_id))

        except Exception as e:
            print(e)
            messages.error(request, '提交失败')
            return HttpResponseRedirect('/monitor/MonitorManage/ConfigHost/detail/{0}/'.format(host_id))
    return render(request,'view/systemtools/ConfigHostSlsDetail.html',{'host_id': host_id, 'host_list': host_list,'pack':pack,'info':info})

@login_required
def ConfigHostPackParameter(request):
    """采集参数详情"""
    parameter = Parameter.objects.all().order_by('-id')
    param_group = ParameterGroup.objects.all()
    if request.method == "POST":
        if request.POST.get('para_add',None):
            para_name = request.POST['para_name']
            para_default = request.POST['para_default']
            para_context = request.POST['para_context']
            param_group_name = request.POST['param_group_name']
            try:
                if len(para_name) and len(para_default) and len(para_context) and len(param_group_name):
                    param_group_id = ParameterGroup.objects.get(param_group_name=param_group_name)
                    Parameter.objects.create(parameter_name=para_name,parameter_context=para_context,parameter_default_id=para_default,parameter_group=param_group_id)
                    messages.success(request,'提交成功')
                    return HttpResponseRedirect('/monitor/MonitorManage/ConfigHostPackParameter/')
                else:
                    return HttpResponseRedirect('/monitor/MonitorManage/ConfigHostPackParameter/')
            except Exception as e:
                print(e)
                messages.error(request,'提交失败')
                return HttpResponseRedirect('/monitor/MonitorManage/ConfigHostPackParameter/')
        elif request.POST.get('deleting',None):
            p_id = request.POST.getlist('id')
            if len(p_id):
                try:
                    Parameter.objects.filter(id__in=p_id).delete()
                    messages.success(request,'提交成功')
                    return HttpResponseRedirect('/monitor/MonitorManage/ConfigHostPackParameter/')
                except Exception as e:
                    print(e)
                    if 'referenced through a protected foreign key' in e[0]:
                        messages.error(request, '提交失败:所删除有关联信息')
                    else:
                        messages.error(request,'提交失败')
                    return HttpResponseRedirect('/monitor/MonitorManage/ConfigHostPackParameter/')
            else:
                return HttpResponseRedirect('/monitor/MonitorManage/ConfigHostPackParameter/')
    return render(request,'view/systemtools/ConfigHostPackParameter.html',{'parameter':parameter,'param_group':param_group})


@login_required
def ConfigHostPackParameterGroup(request):
    """采集参数组管理"""
    param_group = ParameterGroup.objects.all()
    if request.method == "POST":
        if request.POST.get('para_add',None):
            para_group_name = request.POST['para_group_name']
            para_group_content = request.POST['para_group_content']
            para_group_dir = request.POST['para_group_dir']
            try:
                if len(para_group_name) and len(para_group_content):
                    ParameterGroup.objects.create(param_group_name=para_group_name,
                                                              param_group_content=para_group_content,
                                                              param_group_dir=para_group_dir)
                    if not os.path.exists(prv_dir):
                        os.mkdir(prv_dir)
                    if not os.path.exists(prv_dir+para_group_dir):
                        os.chdir(plugin_path+'falcon_plugin')
                        os.mkdir(para_group_dir)
                    messages.success(request,'提交成功')
                    return HttpResponseRedirect('/monitor/MonitorManage/ConfigHostPackParameterGroup/')
                else:
                    return HttpResponseRedirect('/monitor/MonitorManage/ConfigHostPackParameterGroup/')
            except Exception as e:
                print(e)
                messages.error(request,'提交失败')
                return HttpResponseRedirect('/monitor/MonitorManage/ConfigHostPackParameterGroup/')
        elif request.POST.get('deleting',None):
            p_group_id = request.POST.getlist('id')
            if len(p_group_id):
                try:
                    ParameterGroup.objects.filter(id__in=p_group_id).delete()
                    messages.success(request,'提交成功')
                    return HttpResponseRedirect('/monitor/MonitorManage/ConfigHostPackParameterGroup/')
                except Exception as e:
                    print(e)
                    if 'referenced through a protected foreign key' in e[0]:
                        messages.error(request, '提交失败:所删除组有关联信息')
                    else:
                        messages.error(request,'提交失败')
                    return HttpResponseRedirect('/monitor/MonitorManage/ConfigHostPackParameterGroup/')
            else:
                return HttpResponseRedirect('/monitor/MonitorManage/ConfigHostPackParameterGroup/')
    return render(request,'view/systemtools/ConfigHostPackParameterGroup.html',{'param_group':param_group})


@login_required
def ConfigHostPackParameterGroupDetail(request,pk):
    """采集参数组信息维护"""
    parameter = ParameterGroup.objects.filter(id=pk)
    if request.method == "POST":
        if request.POST.get('para_group_update',None):
            para_group_name = request.POST['para_group_name']
            para_group_context = request.POST['para_group_context']
            try:
                if len(para_group_name) and len(para_group_context):
                    ParameterGroup.objects.filter(id=pk).update(param_group_name=para_group_name,param_group_content=para_group_context)
                    messages.success(request,'提交成功')
                    return HttpResponseRedirect('/monitor/MonitorManage/ConfigHostPackParameterGroup/')
                else:
                    return HttpResponseRedirect('/monitor/MonitorManage/ConfigHostPackParameterGroup/')
            except Exception as e:
                print(e)
                messages.error(request,'提交失败')
                return HttpResponseRedirect('/monitor/MonitorManage/ConfigHostPackParameterGroup/')
    return render(request,'view/systemtools/ConfigHostPackParameterGroupDetail.html',{'parameter':parameter})



@login_required
def ConfigHostPackParameterDetail(request,para_id):
    """采集参数修改"""
    parameter = Parameter.objects.filter(id=int(para_id))
    param_group = ParameterGroup.objects.all()
    if request.method == "POST":
        if request.POST.get('para_update',None):
            para_name = request.POST['para_name']
            para_default = request.POST['para_default']
            para_context = request.POST['para_context']
            param_group_name = request.POST['param_group_name']
            try:
                if len(para_name) and len(para_default) and len(para_context) and len(param_group_name):
                    param_group_id = ParameterGroup.objects.get(param_group_name=param_group_name)
                    Parameter.objects.filter(id=int(para_id)).update(parameter_name=para_name,parameter_context=para_context,parameter_default_id=para_default,parameter_group=param_group_id)
                    messages.success(request,'提交成功')
                    return HttpResponseRedirect('/monitor/MonitorManage/ConfigHostPackParameter/')
                else:
                    return HttpResponseRedirect('/monitor/MonitorManage/ConfigHostPackParameter/')
            except Exception as e:
                print(e)
                messages.error(request,'提交失败')
                return HttpResponseRedirect('/monitor/MonitorManage/ConfigHostPackParameter/')
    return render(request,'view/systemtools/ConfigHostPackParameterDetail.html',{'parameter':parameter,'param_group':param_group})


@login_required
def ConfigHostTool(request,host_id):
    """采集工具管理"""
    args = Host.objects.filter(id=host_id).values_list('hostname')[0][0]
    if request.method == "POST":
        dstatus = ""
        tool_name = request.POST['tool_name']
        tool_context = request.POST['tool_context']
        tool_version = request.POST['tool_version']
        myFile = request.FILES.getlist("file_name", None)  # 获取上传的文件，如果没有文件，则默认为None
        for i in myFile:
            if not i:
                dstatus = "<label style='color: #E74C3C'>请选择需要上传的文件!</label>"
            else:
                path_dst_file = '{2}/{0}/{1}'.format(args, i,prv_dir)
                if os.path.isfile(path_dst_file):
                    dstatus += "\n" + "<label style='color: #E74C3C'>%s 已存在,请重名名或者重新选择文件。</label>" % (i) + "\n"
                else:
                    try:
                        dir_info = '{1}/{0}/'.format(args,prv_dir)
                        dir_name = os.path.split(dir_info)
                        if os.path.isdir(dir_name[0]):
                            destination = open(path_dst_file, 'wb+')  # 打开特定的文件进行二进制的写操作
                            for chunk in i.chunks():  # 分块写入文件
                                destination.write(chunk)
                            destination.close()
                            os.system('dos2unix {0}'.format(path_dst_file))
                            dstatus += "\n" + "<label style='color: #2ECC71'>%s 文件上传成功!&nbsp;&nbsp;&nbsp;</label>" % (
                                 i) + "\n"
                            Tool.objects.create(tool_host=Host.objects.get(id=host_id),
                                                                tool_name=tool_name,tool_dir=path_dst_file,
                                                                tool_version=tool_version,tool_context=tool_context)
                        else:
                            os.makedirs(dir_info)
                            destination = open(path_dst_file, 'wb+')  # 打开特定的文件进行二进制的写操作
                            for chunk in i.chunks():  # 分块写入文件
                                destination.write(chunk)
                            destination.close()
                            os.system('dos2unix {0}'.format(path_dst_file))
                            dstatus += "\n" + "<label style='color: #2ECC71'>%s 文件上传成功!&nbsp;&nbsp;&nbsp;</label>" % (i) + "\n"
                            Tool.objects.create(tool_host=Host.objects.get(id=host_id),
                                                                tool_name=tool_name, tool_dir=path_dst_file,
                                                                tool_version=tool_version, tool_context=tool_context)
                    except Exception as e:
                        print(e)
                        messages.error(request,'提交失败')
                        return HttpResponseRedirect('/monitor/MonitorManage/ConfigHost/{0}/ConfigHostTool/'.format(host_id))
        return render(request, 'view/systemtools/ConfigHostTool.html', {'dstatus': dstatus, 'args': args,'host_id':host_id})
    return render(request, 'view/systemtools/ConfigHostTool.html', {'args': args,'host_id':host_id})


@login_required
def ConfigHostGroup(request):
    """主机组信息"""
    grp_name_list_sql = 'select grp_name,id from grp;'
    grp_name_list = db_falcon.mysql_command(grp_name_list_sql)
    group_list = HostGroup.objects.all()
    if request.method =="POST":
        if request.POST.get('group_add',None):
            groupname = request.POST['groupname']
            print(len(groupname))
            if len(groupname):
                try:
                    HostGroup.objects.create(host_group=groupname)
                    messages.success(request,'提交成功')
                    return HttpResponseRedirect('/monitor/MonitorManage/ConfigHostGroup/')
                except Exception as e:
                    print(e)
                    messages.error(request,'提交失败')
                    return HttpResponseRedirect('/monitor/MonitorManage/ConfigHostGroup/')
            else:
                return HttpResponseRedirect('/monitor/MonitorManage/ConfigHostGroup/')
        elif request.POST.get('deleting',None):
            group_id = request.POST.getlist('id')
            if len(group_id):
                try:
                    HostGroup.objects.filter(id__in=group_id).delete()
                    messages.success(request,'提交成功')
                    return HttpResponseRedirect('/monitor/MonitorManage/ConfigHostGroup/')
                except Exception as e:
                    if 'referenced through a protected foreign key' in e[0]:
                        messages.error(request, '提交失败:所删除组有关联信息')
                    else:
                        messages.error(request,'提交失败')
                    return HttpResponseRedirect('/monitor/MonitorManage/ConfigHostGroup/')
            else:
                return HttpResponseRedirect('/monitor/MonitorManage/ConfigHostGroup/')
        else:
            if not request.POST.has_key('group_add') and request.POST.has_key('groupname'):
                groupname = request.POST['groupname']
                if len(groupname):
                    try:
                        HostGroup.objects.create(host_group=groupname)
                        messages.success(request,'提交成功')
                        return HttpResponse('提交成功')
                    except Exception as e:
                        if 'Duplicate entry' in e[1]:
                            messages.error(request,'提交失败')
                            return HttpResponse('提交失败:{0}'.format(e[1]))
                        else:
                            messages.error(request, '提交失败')
                            return HttpResponse('提交失败')
                else:
                    return HttpResponse('无设备组添加')

    return render(request, 'view/systemtools/ConfigHostGroup.html', {'group_list':group_list,'grp_name_list':grp_name_list})

@login_required
def ConfigHostGroupUpdate(request,pk):
    """主机组修改"""
    host_group = HostGroup.objects.get(id=pk).host_group
    grp_id = pk
    l = ['id', 'value']
    par_in = ParameterGroup.objects.filter(param_group_device_group=pk).values_list('id','param_group_name')
    par_out = ParameterGroup.objects.exclude(param_group_device_group=pk).values_list('id', 'param_group_name')
    par_i = json.dumps([dict(zip(l, i)) for i in par_in])
    par_n = json.dumps([dict(zip(l, i)) for i in par_out])
    user = request.user
    if request.method == "POST":
        groupname = request.POST['groupname']
        group_id = request.POST['group_id']
        par_grp_id = request.POST["par_grp_id"]
        parameter_group_obj = ParameterGroup.objects.filter(param_group_device_group=int(group_id)).values_list('id')
        try:
            HostGroup.objects.filter(id=pk).update(host_group=groupname)
            for i in list(eval(par_grp_id)):
                ug_obj = ParameterGroup.objects.filter(id=int(i)).filter(param_group_device_group=int(group_id)).values_list()
                if list(ug_obj) == []:
                    a = ParameterGroup(id=int(i))

                    plugin_dir = './{0}'.format(ParameterGroup.objects.filter(id=int(i)).values_list('param_group_dir')[0][0])
                    grp_id_sql = 'select id from grp where grp_name="{0}"'.format(groupname)
                    grp_id = db_falcon.mysql_command(grp_id_sql)[0][0]
                    plugin_dir_exist_sql = 'select count(*) from plugin_dir where grp_id = {0} and dir = "{1}"'.format(grp_id,plugin_dir)
                    if db_falcon.mysql_command(plugin_dir_exist_sql)[0][0] == 0:
                        plugin_dir_update_sql = 'insert into plugin_dir(grp_id,dir,create_user) values({0},"{1}","{2}")'.format(grp_id,plugin_dir,user.username)
                        db_falcon.mysql_command(plugin_dir_update_sql)

                    b = HostGroup(id=int(group_id))
                    a.param_group_device_group.add(b)
                    p_name = ParameterGroup.objects.get(id=i).param_group_name
                    logger.info("{0} add parametergroup {1} into monitor_device_group {2}".format(user, p_name, host_group))
            for i in parameter_group_obj:
                import operator
                if not any([operator.eq(int(i[0]), int(x)) for x in list(eval(par_grp_id))]):
                    a1 = ParameterGroup(id=int(i[0]))

                    plugin_dir = './{0}'.format(
                        ParameterGroup.objects.filter(id=int(i[0])).values_list('param_group_dir')[0][0])
                    grp_id_sql = 'select id from grp where grp_name="{0}"'.format(groupname)
                    grp_id = db_falcon.mysql_command(grp_id_sql)[0][0]
                    plugin_dir_del_sql = 'delete from plugin_dir where grp_id={0} and dir="{1}"'.format(
                        grp_id, plugin_dir)
                    db_falcon.mysql_command(plugin_dir_del_sql)

                    b1 = HostGroup(id=int(group_id))
                    a1.param_group_device_group.remove(b1)
                    p_name = ParameterGroup.objects.get(id=int(i[0])).param_group_name
                    logger.info("{0} delete parametergroup {1} into monitor_device_group {2}".format(user, p_name, host_group))
            messages.success(request, '提交成功')
            return HttpResponse('提交成功')
        except Exception as e:
            print(e)
            messages.error(request, '提交失败')
            return HttpResponse('提交失败')
    return render(request, 'view/systemtools/ConfigHostGroupUpdate.html',locals())

@login_required
def ConfigToolList(request):
    last_dict = []
    class dynamic:
        def __init__(self):
            self.db_dir =[i[0] for i in ParameterGroup.objects.all().values_list('param_group_dir')]+['pub_plugin']
        def tree(self,path,*op):
            roots, dirs, files, roots_init = [], [], [], []
            import re
            for root, dir, file in os.walk(path+'falcon_plugin'):
                if root.replace(path+'falcon_plugin/','').startswith('.'):
                    continue
                roots_init += [root]
                roots += [re.split('/',root.replace(path+'falcon_plugin',''))]
                dirs += [dir]
                files += [file]
            tmp,child = [],[]
            for s in dirs[0]:
                tmp += [{'name':s,'children':self.s_dir(0,s,roots_init,roots,dirs,files)}]
            try:
                child = [
                            {'name': y,
                             'click': "iframe_load('/monitor/MonitorManage/ConfigPrivateFileDetail_core/{0}')".format(
                                 Private_Template.objects.filter(
                                     private_template_dir=roots_init[0] + '/' + y).values_list('id')[0][
                                     0])
                             } for y in files[0]
                        ] + tmp
            except:
                try:
                    child = [
                                {'name': y,
                                 'click': "iframe_load('/monitor/MonitorManage/ConfigPluginFileDetail/{0}')".format(y)
                                 } for y in files[0]
                            ] + tmp
                except:
                    return []
            tree_data = [{'name':'falcon_plugin','children':child}]
            return tree_data
        def s_dir(self,i,s,roots_init,roots,dirs,files,):
            if i == 0:
                if s not in self.db_dir:
                    return []
            if s.startswith('.'):
                return []
            index = roots.index(roots[i] + [s])
            edge, tmp, child = [], [], []
            for cc in files[index]:
                try:
                    id = Private_Template.objects.get(private_template_dir=roots_init[index] + '/' + cc).id
                    edge += [
                        {
                            'name': cc,
                            'click': "iframe_load('/monitor/MonitorManage/ConfigPrivateFileDetail_core/{0}')".format(id)
                        }
                    ]
                except:
                    edge += [
                        {
                            'name': cc,
                            'click': "iframe_load('/monitor/MonitorManage/ConfigPluginFileDetail{1}/{0}')".format(
                                cc, roots_init[index].replace(prv_dir, ''))
                        }
                    ]
            for s2 in dirs[index]:
                tmp += [{'name': s2, 'children': self.s_dir(index, s2, roots_init, roots, dirs, files)}]
            child = edge + tmp
            return child
    s = dynamic()
    last_dict = s.tree(plugin_path)
    znode = json.dumps(last_dict)
    return render(request, 'view/systemtools/ConfigToolList.html', locals())


@login_required
def ConfigHostPackUpdate(request,host_id,pack_id):
    """参数配置文件更新管理"""
    pack = Private_file.objects.filter(private_host=Host.objects.get(id=host_id)).filter(id=pack_id)
    host_list = Host.objects.filter(id=host_id)
    config_dir=pack.values_list('private_dir')[0][0]
    f1 = open(config_dir, 'r')
    info = f1.read()
    f1.close()
    if request.method == "POST":
        hostname = host_list.values_list('hostname')[0][0]
        config_file_content = request.POST['config_file_content']
        try:
            add_mod_error =""
            add_mod_other_error =""
            path_dst_file = config_dir
            dir_info = '{1}/{0}/'.format(hostname,prv_dir)
            dir_name = os.path.split(dir_info)
            if os.path.isdir(dir_name[0]):
                f = open('{0}'.format(path_dst_file), 'w')
                f.write(config_file_content)
                f.close()
                add = os.system('cd {1} && git add {0}'.format(path_dst_file,prv_dir))
                commit = os.system('cd {1} &&  git commit -m "{0}"'.format(path_dst_file,prv_dir))
                push = os.system('cd {0} && git push'.format(prv_dir))
                if add == 0 and push == 0 and commit == 0:
                    messages.success(request, '提交成功')
                    return HttpResponseRedirect('/monitor/MonitorManage/ConfigHost/detail/{0}/'.format(host_id))
                elif add == 0 and push == 0 and commit == 1:
                    add_mod_error += path_dst_file + " " + "状态码:" + "git add:{0}".format(
                        add) + " " + "git commit：{0}".format(commit) + " " + "git push:{0}".format(push)
                    messages.error(request, '提交失败')
                    return HttpResponseRedirect('/monitor/MonitorManage/ConfigHost/detail/{0}/'.format(host_id))
                else:
                    add_mod_other_error += path_dst_file + " " + "状态码:" + "git add:{0}".format(
                        add) + " " + "git commit:{0}".format(commit) + " " + "git push:{0}".format(push)
                    messages.error(request, '提交失败')
                    return HttpResponseRedirect('/monitor/MonitorManage/ConfigHost/detail/{0}/'.format(host_id))

        except Exception as e:
            print(e)
            messages.error(request, '提交失败')
            return HttpResponseRedirect('/monitor/MonitorManage/ConfigHost/detail/{0}/'.format(host_id))

    return render(request, 'view/systemtools/ConfigHostPackDetail.html',
                  {'host_id': host_id, 'host_list': host_list,'pack':pack,'info':info})


@login_required
def ConfigHostToolUpdate(request,host_id):
    return render(request,'view/systemtools/ConfigHostToolDetail.html')


@login_required
def SaltManagement(request):
    group_list = HostGroup.objects.all()
    host_list = Host.objects.all()
    if request.method == "POST":
        if request.POST.get('host_add',None):
            hostname = request.POST['hostname']
            ip = request.POST['ip']
            host_room = request.POST['host_room']
            host_grp = request.POST['host_grp']
            if len(hostname) and len(ip) and len(host_room) and len(host_grp):
                try:
                    _id = HostGroup.objects.get(id=int(host_grp))
                    Host.objects.create(hostname=hostname,ip=ip,host_room=host_room,host_grp=_id)
                except Exception as e:
                    print(e)
                    messages.error(request,'提交失败')
                    return HttpResponseRedirect('/monitor/MonitorManage/ConfigHost/')
            else:
                error = "请填写全部内容！！"
                return render(request, 'view/systemtools/ConfigHostList.html',
                              {'group_list': group_list, 'error': error,'host_list':host_list})
    return render(request, 'view/systemsalt/saltsta.html',{'group_list':group_list,'host_list':host_list})


@login_required
def SaltManagementManage(request):
    """salt文件下发管理"""
    info = sync_file.get_filepaths(pub_dir)
    files_list=[]
    tmp = '{0}/systemfalcon/systemconfig/tmp'.format(conf_dir.conf['project_dir'])
    for i in info:
        files = os.path.split(i)
        if files[1].find('.sls') != -1:
            files_list.append(files)
        else:
            pass
    if request.method == "POST":
        public_para = request.POST['public_para']
        private_para = request.POST['private_para']
        if public_para=="*" and private_para=="*":
            if request.POST.get('btn_exec', None):
                try:
                    tgt = request.POST.getlist('id')
                    fun = request.POST['fun']
                    arg = request.POST['arg']
                    hostname_list = request.POST['hostname_list']
                    expr_form = request.POST['expr_form']
                    select_host = Host.objects.filter(id__in=tgt)
                    host = select_host.values_list('hostname')
                    _host = ""
                    for h in host:
                         _host+=","+h[0]
                    hostname_lists = hostname_list+_host
                    content = local.post(hostname_lists, fun, arg, expr_form)
                    jid= content['jid']
                    hosts = hostname_lists.split(',')
                    if '' in list(hosts):
                        hosts.remove('')
                    f=open(tmp,'w')
                    for a in list(hosts):
                        f.write(str(jid) + " " + str(a)+"\n")
                    f.close()
                    messages.success(request, '提交成功')
                    return HttpResponseRedirect('/monitor/MonitorManage/SaltManagementManage/')
                except Exception as e:
                    print(e)
                    messages.error(request, '提交失败')
                return HttpResponseRedirect('/monitor/MonitorManage/SaltManagementManage/')
        elif public_para=="*" and private_para=="自定义":
            if request.POST.get('btn_exec', None):
                try:
                    tgt = request.POST.getlist('id')
                    list_sls = request.POST.getlist('list_sls')
                    fun = "state.sls"
                    hostname_list = request.POST['hostname_list']
                    expr_form = "list"
                    f = open(tmp, 'w')
                    f.write('')
                    f.close()
                    a = open(tmp, 'a')
                    for i in list(list_sls):
                        if i:
                            id= i.split('|')[0]
                            sls= i.split('|')[1]
                            if id in tgt:
                                select_host = Host.objects.filter(id=id)
                                host = select_host.values_list('hostname')
                                hostname_lists = host[0][0]
                                arg = prv_sls + "." + hostname_lists+"."+sls.split('.')[0]
                                content = local.post(hostname_lists, fun, arg, expr_form)
                                jid = content['jid']
                                a.write(str(jid) + " " + str(hostname_lists) + "\n")
                        else:
                            print('null')
                    a.close()
                    messages.success(request, '提交成功')
                    return HttpResponseRedirect('/monitor/MonitorManage/SaltManagementManage/')
                except Exception as e:
                    print(e)
                    messages.error(request, '提交失败')
                    return HttpResponseRedirect('/monitor/MonitorManage/SaltManagementManage/')
        elif 'sls' in public_para:
            if request.POST.get('btn_exec', None):
                tgt = request.POST.getlist('id')
                fun = "state.sls"
                arg = pub_sls+"."+public_para.split(".")[0]
                hostname_list = request.POST['hostname_list']
                expr_form = "list"
                select_host = Host.objects.filter(id__in=tgt)
                host= select_host.values_list('hostname')
                _host = ""
                try:
                    for h in host:
                         _host+=","+h[0]
                    hostname_lists = hostname_list+_host
                    content = local.post(hostname_lists, fun, arg, expr_form)
                    jid= content['jid']
                    hosts = hostname_lists.split(',')
                    if '' in list(hosts):
                        hosts.remove('')
                    f=open(tmp,'w')
                    for a in list(hosts):
                        f.write(str(jid) + " " + str(a)+"\n")
                    f.close()
                    messages.success(request, '提交成功')
                    return HttpResponseRedirect('/monitor/MonitorManage/SaltManagementManage/')
                except Exception as e:
                    print(e)
                    messages.error(request, '提交失败')
                return HttpResponseRedirect('/monitor/MonitorManage/SaltManagementManage/')
    if request.method =="GET":
        host_list = Host.objects.all()

        f = open(tmp, 'r')
        info = f.readlines()
        ret = []
        for i in info:
            sql = "select `fun`,`jid`,`return`,`id`,`success`,`full_ret`,`alter_time` from salt_returns where jid='%s' and id='%s';" \
                  % (i.strip().split()[0], i.strip().split()[1])
            try:
                sql_info = db_salt.mysql_command(sql)
                sql_list = [sql_list for sql_list in sql_info]
                full_ret = sql_list[0][5]
                full_ret_dict = json.loads((full_ret).replace('[]', '""').replace('["', '"').replace('"]', '"'))
                result = [sql_list[0][3], full_ret_dict["success"], sql_list[0][1]]
                ret.append(result)
            except Exception as e:
                print(e)
                pass
        data = list(ret)
        return render(request, 'view/systemsalt/salt.html', {'host_list': host_list,'ret':data,'files_list':files_list})


@login_required
def SaltManagementManageDetail(request,hostname):
    """salt日志详情"""
    sql = "select full_ret from salt_returns where id='%s' order by jid desc limit 30;" %(hostname)
    try:
        sql_info = db_salt.mysql_command(sql)
        sql_list = [dict(eval(i[0].replace('true','\'true\'').replace('false','\'false\'').replace('null','\'null\''))) for i in sql_info]
        return render(request,'view/systemsalt/salt_hostdetail.html',locals())
    except Exception as e:
        print(e)
        # return HttpResponseRedirect('/monitor/MonitorManage/SaltManagementManage/detail/%s/%s/'%(hostname,jid))
        return HttpResponse('数据异常')


@csrf_exempt
@login_required
def SaltMessage(request):
    """salt实时日志"""
    if request.method == "POST":
        f=open('{0}/systemfalcon/systemconfig/tmp'.format(conf_dir.conf['project_dir']),'r')
        info = f.readlines()
        ret = []
        for i in info:
            sql = "select `fun`,`jid`,`return`,`id`,`success`,`full_ret`,`alter_time` from salt_returns where jid='%s';" \
                  % (i.strip().split()[0])
            try:
                sql_info = db_salt.mysql_command(sql)
                sql_list = [sql_list for sql_list in sql_info]
                for i in sql_list:
                    full_ret = i[5]
                    full_ret_dict = json.loads((full_ret).replace('[]','""').replace('["','"').replace('"]','"'))
                    # print full_ret_dict
                    result = {
                         "hostname":i[3],
                         "fun":i[0],
                         "jid":i[1],
                         "return":str(i[2]).replace('"','').replace("\\n","<br>"),
                         "alter_time":str(i[6]),
                         "fun_args":full_ret_dict["fun_args"],
                         "success":full_ret_dict["success"],
                    }
                    ret.append(result)
            except Exception as e:
                print(e)
                result = {
                    "hostname": i.strip().split()[1],
                    "jid":  i.strip().split()[0],
                    "fun":"<span style='color:red'>No data</span>",
                    "return": "<span style='color:red'>No data</span>",
                    "fun_args": "<span style='color:red'>No data</span>",
                    "alter_time": "<span style='color:red'>No data</span>",
                    "success": "<span style='color:red'>No</span>",
                }
                ret.append(result)
                # return HttpResponse('数据库查询异常')
        # print ret
        data = json.dumps(ret)
        return HttpResponse(data)
    return render(request,'view/systemsalt/salt_log.html')

@is_group('sys')
def SaltControlRsa(request):
    if request.method == 'POST':
        host = request.POST['host']
        op = request.POST['op']
        if op == 'cancel':
            os.system('salt-key -d {0} -y'.format(host))
            return HttpResponse('已取消认证')
        elif op == 'accept':
            os.system('salt-key -a {0} -y'.format(host))
            return HttpResponse('已接受认证')
        elif op == 'reject':
            os.system('salt-key -r {0} -y'.format(host))
            return HttpResponse('已拒绝认证')


@login_required
def ConfigPluginFile(request):
    """公共配置、工具文件管理，绑定相关文件"""
    parameter = Parameter.objects.all()
    file_list = ['ss','dd']
    if request.method == "POST":
        dstatus = ""
        tool_para = request.POST['tool_parameter']
        tmp_dir = ParameterGroup.objects.get(parameter__id=int(tool_para)).param_group_dir
        myFile = request.FILES.getlist("tool_file_name", None)  # 获取上传的工具文件，如果没有文件，则默认为None
        for i in myFile:
            if not i:
                dstatus = "<label style='color: #E74C3C'>请选择需要上传的文件!</label>"
            else:
                path_dst_file = '{0}/{1}/{2}'.format(prv_dir,tmp_dir,i)
                if os.path.isfile(path_dst_file):
                    dstatus += "\n" + "<label style='color: #E74C3C'>%s 已存在,请重名名或者重新选择文件。</label>" % (i) + "\n"
                    return render(request, 'view/systemtools/ConfigPluginFile.html',
                                  {'file_list': file_list, 'parameter': parameter,'dstatus':dstatus})
                else:
                    try:
                        dir_info = '{0}/{1}'.format(prv_dir,tmp_dir)
                        if not os.path.exists(dir_info):
                            os.makedirs(dir_info)
                        destination = open(path_dst_file, 'wb+')  # 打开特定的文件进行二进制的写操作
                        for c_index,chunk in enumerate(i.chunks()):  # 分块写入文件
                            destination.write(chunk)
                        destination.close()
                        os.system('dos2unix {0}'.format(path_dst_file))
                        dstatus += "\n" + "<label style='color: #2ECC71'>%s 文件上传成功!&nbsp;&nbsp;&nbsp;</label>" % (i) + "\n"
                    except Exception as e:
                        print(e)
                        messages.error(request,'提交失败')
                        return HttpResponseRedirect('/monitor/MonitorManage/ConfigPluginFile/')
        messages.success(request, '提交成功!')
        return HttpResponseRedirect('/monitor/MonitorManage/ConfigPluginFile/')
    return render(request,'view/systemtools/ConfigPluginFile.html',{'file_list':file_list,'parameter':parameter})


@login_required
def ConfigHttpFile(request):
    """一般存储目录"""
    parameter = Parameter.objects.all()
    file_list = ['ss','dd']
    if request.method == "POST":
        dstatus = ""
        tmp_dir = 'http_dir'
        myFile = request.FILES.getlist("tool_file_name", None)  # 获取上传的工具文件，如果没有文件，则默认为None
        for i in myFile:
            if not i:
                dstatus = "<label style='color: #E74C3C'>请选择需要上传的文件!</label>"
            else:
                path_dst_file = '{0}/{1}/{2}'.format(prv_dir,tmp_dir,i)
                if os.path.isfile(path_dst_file):
                    dstatus += "\n" + "<label style='color: #E74C3C'>%s 已存在,请重名名或者重新选择文件。</label>" % (i) + "\n"
                    return render(request, 'view/systemtools/ConfigPluginFile.html',
                                  {'file_list': file_list, 'parameter': parameter,'dstatus':dstatus})
                else:
                    try:
                        dir_info = '{0}/{1}'.format(prv_dir,tmp_dir)
                        if not os.path.exists(dir_info):
                            os.makedirs(dir_info)
                        destination = open(path_dst_file, 'wb+')  # 打开特定的文件进行二进制的写操作
                        for c_index,chunk in enumerate(i.chunks()):  # 分块写入文件
                            destination.write(chunk)
                        destination.close()
                        if not path_dst_file.endswith('.gz'):
                            os.system('dos2unix {0}'.format(path_dst_file))
                        dstatus += "\n" + "<label style='color: #2ECC71'>%s 文件上传成功!&nbsp;&nbsp;&nbsp;</label>" % (i) + "\n"
                    except Exception as e:
                        print(e)
                        messages.error(request,'提交失败')
                        return HttpResponseRedirect('/monitor/MonitorManage/ConfigHttpFile/')
        messages.success(request, '提交成功!')
        return HttpResponseRedirect('/monitor/MonitorManage/ConfigHttpFile/')
    return render(request,'view/systemtools/ConfigHttpFile.html',{'file_list':file_list,'parameter':parameter})


@login_required
def ConfigPluginFileDetail(request,file_name):
    """公有文件详情管理"""
    parameter = Parameter.objects.all()
    file_info = prv_dir+'/'+file_name
    try:
        f = open(file_info, 'r')
        info_ = f.read()
        f.close()
    except IOError:
        messages.error(request, '文件损坏')
        return HttpResponseRedirect('/monitor/MonitorManage/ConfigPluginFileDetail/{0}/'.format(file_name))
    if request.method == "POST":
        dstatus = ""
        pub_file_name = request.POST['pub_file_name']
        if request.POST.get('pub_update_tool', None):
            myFile = request.FILES.getlist('pub_file_dir', None)
            if myFile == "":
                return HttpResponseRedirect('/monitor/MonitorManage/ConfigPluginFileDetail/{0}/'.format(file_name))
            for i in myFile:
                try:
                    destination = open(file_info, 'wb+')  # 打开特定的文件进行二进制的写操作
                    for chunk in i.chunks():  # 分块写入文件
                        destination.write(chunk)
                    destination.close()
                    os.system('dos2unix {0}'.format(file_info))
                    dstatus += "\n" + "<label style='color: #2ECC71'>%s 文件上传成功!&nbsp;&nbsp;&nbsp;</label>" % (
                        i) + "\n"
                    messages.success(request, '提交成功')
                    return HttpResponseRedirect('/monitor/MonitorManage/ConfigPluginFileDetail/{0}/'.format(file_name))
                except Exception as e:
                    messages.error(request, '提交失败')
                    return HttpResponseRedirect('/monitor/MonitorManage/ConfigPluginFileDetail/{0}/'.format(file_name))
        elif request.POST.get('pub_update_conf', None):
            file_content = request.POST['file_content']
            f1 = open(file_info, 'w')
            f1.write(file_content)
            f1.close()
            os.system('dos2unix {0}'.format(file_info))
            messages.success(request, '提交成功')
            return HttpResponseRedirect('/monitor/MonitorManage/ConfigPluginFileDetail/{0}/'.format(file_name))
        elif request.POST.get('pub_file_del', None):
            os.system('cd {1} && rm {0}'.format(file_name, prv_dir))
            return HttpResponse('已删除')

    return render(request,'view/systemtools/ConfigPluginFileDetail.html',locals())



@login_required
def ConfigPublicFile(request):
    """公共配置、工具文件管理，绑定相关文件"""
    parameter = Parameter.objects.all()
    file_list = Pub_File.objects.all()
    if request.method == "POST":
        dstatus = ""
        tool_class = request.POST['tool_class']
        tool_context = request.POST['tool_context']
        tool_parameter = request.POST.getlist('tool_parameter')

        myFile = request.FILES.getlist("tool_file_name", None)  # 获取上传的工具文件，如果没有文件，则默认为None
        print("myFile: {0}".format(myFile))
        myFile_conf = request.FILES.getlist("config_file_name", None)  # 获取上传的配置文件，如果没有文件，则默认为None
        config_class = request.POST['config_class']
        config_context = request.POST['config_context']
        if tool_parameter == []:
            dstatus = "<label style='color: #E74C3C'>请选择参数!</label>"
            return render(request, 'view/systemtools/ConfigPublicFile.html',
                          {'dstatus': dstatus, 'file_list': file_list, 'parameter': parameter})
        tool_name_info = Pub_File.objects.filter(pub_name=myFile[0]).count()
        if tool_name_info>0:
            dstatus = "<label style='color: #E74C3C'>输入的工具名称或者配置文件名称有重复，请重新输入!</label>"
            return render(request, 'view/systemtools/ConfigPublicFile.html',
                          {'dstatus': dstatus, 'file_list': file_list, 'parameter': parameter})

        tool_parameter_id = tool_parameter  #parameter table is id list
        for i in myFile:
            print(i)
            tool_name = i
            if not i:
                dstatus = "<label style='color: #E74C3C'>请选择需要上传的文件!</label>"
            else:
                path_dst_file = '{0}/{1}'.format(pub_dir,i)
                if os.path.isfile(path_dst_file):
                    dstatus += "\n" + "<label style='color: #E74C3C'>%s 已存在,请重名名或者重新选择文件。</label>" % (i) + "\n"
                    return render(request, 'view/systemtools/ConfigPublicFile.html',
                                  {'file_list': file_list, 'parameter': parameter,'dstatus':dstatus})
                else:
                    try:
                        dir_info = '{0}/'.format(pub_dir)
                        dir_name = os.path.split(dir_info)
                        if not os.path.isdir(dir_name[0]):
                            os.makedirs(dir_info)

                        destination = open(path_dst_file, 'wb+')  # 打开特定的文件进行二进制的写操作
                        for chunk in i.chunks():  # 分块写入文件
                            destination.write(chunk)
                        destination.close()
                        if not path_dst_file.endswith('.gz'):
                            os.system('dos2unix {0}'.format(path_dst_file))
                        dstatus += "\n" + "<label style='color: #2ECC71'>%s 文件上传成功!&nbsp;&nbsp;&nbsp;</label>" % (i) + "\n"

                        Pub_File.objects.create(pub_name=tool_name, pub_class=tool_class,
                                                            pub_dir=path_dst_file
                                                            , pub_file_name=i, pub_context=tool_context)
                        pub_id = Pub_File.objects.filter(pub_name=tool_name).values('id')
                        id_ = pub_id[0]['id']
                        pub_file_id = Pub_File.objects.get(id=id_)
                        pub_file_id.pub_parameter.add(*tool_parameter_id)
                    except Exception as e:
                        print(e)
                        messages.error(request,'提交失败')
                        return HttpResponseRedirect('/monitor/MonitorManage/ConfigPublicFile/')
        for i in myFile_conf:
            config_name = i
            if not i:
                dstatus = "<label style='color: #E74C3C'>请选择需要上传的文件!</label>"
                pass
            else:
                path_dst_file = '{0}/{1}'.format(pub_dir,i)
                #print(path_dst_file)
                if os.path.isfile(path_dst_file):
                    dstatus += "\n" + "<label style='color: #E74C3C'>%s 已存在,请重名名或者重新选择文件。</label>" % (i) + "\n"
                    return render(request, 'view/systemtools/ConfigPublicFile.html',
                                  {'file_list': file_list, 'parameter': parameter, 'dstatus': dstatus})
                else:
                    try:
                        dir_info = '{0}/'.format(pub_dir)
                        dir_name = os.path.split(dir_info)
                        if not os.path.isdir(dir_name[0]):
                            os.makedirs(dir_info)

                        destination = open(path_dst_file, 'wb+')  # 打开特定的文件进行二进制的写操作
                        for chunk in i.chunks():  # 分块写入文件
                            destination.write(chunk)
                        destination.close()
                        dstatus += "\n" + "<label style='color: #2ECC71'>%s 文件上传成功!&nbsp;&nbsp;&nbsp;</label>" % (i) + "\n"

                        Pub_File.objects.create(pub_name=config_name, pub_class=config_class,
                                                                pub_dir=path_dst_file
                                                                , pub_file_name=i,
                                                                pub_context=config_context)
                    except Exception as e:
                        print(e)
                        messages.error(request,'提交失败')
                        return HttpResponseRedirect('/monitor/MonitorManage/ConfigPublicFile/')
        #-----------------sls文件生成
        file_name = myFile[0]
        toolname = file_name + '.sls'
        sls_info_tool="""falcon_{0}_sh:
        file.managed:
        - name: {1}net/{0}
        - source: 
          - salt://falcon_plugin/pub_plugin/{0}
        - user: root
        - group: root
        - mode: 755
        - makedirs: true\n""".format(file_name,client_plugin_path)
        sls_info_config="""falcon_{0}_conf:
        file.managed:
        - name: {1}net/{0}
        - source: 
          - salt://falcon_plugin/pub_plugin/{0}
        - user: root
        - group: root
        - mode: 644
        - makedirs: true""".format(myFile_conf[0],client_plugin_path)
        path_dst_file = '{0}/{1}'.format(pub_dir,toolname)
        if os.path.isfile(path_dst_file):
            dstatus += "\n" + "<label style='color: #E74C3C'>%s 已存在,请重名名或者重新选择文件。</label>" % (toolname) + "\n"
        else:
            try:
                Pub_File.objects.create(pub_name=toolname, pub_class='sls',
                                                    pub_dir=path_dst_file
                                                    , pub_file_name=toolname,
                                                    pub_context='sls配置文件')
                sls_file = open('{0}/{1}'.format(pub_dir, toolname), 'a')
                sls_file.write(sls_info_tool)
                if config_name:
                    sls_file.write(sls_info_config)
                sls_file.close()
            except Exception as e:
                print(e)
                messages.error(request, '提交失败')
                return HttpResponseRedirect('/monitor/MonitorManage/ConfigPublicFile/')
        messages.success(request, '提交成功!')
        return HttpResponseRedirect('/monitor/MonitorManage/ConfigPublicFile/')
    return render(request,'view/systemtools/ConfigPublicFile.html',{'file_list':file_list,'parameter':parameter})


@login_required
def ConfigPublicFileDetail(request,pk):
    """公有文件详情管理"""
    public_info = Pub_File.objects.filter(id=int(pk))
    parameter = Parameter.objects.all()
    file_info = public_info.values_list('pub_dir')[0][0]
    pub_name = public_info.values_list('pub_name')[0][0]
    try:
        f = open(file_info, 'r')
        info_ = f.read()
        f.close()
    except IOError:#--------一旦实体文件打不开，自动删除数据库记录信息
        Pub_File.objects.filter(id=int(pk)).delete()
        return HttpResponseRedirect('/monitor/MonitorManage/ConfigPublicFile/')
    #print(parameter)
    if request.method == "POST":
        dstatus = ""
        pub_file_name = request.POST['pub_file_name']
        if request.POST.get('pub_update_tool', None):
            myFile = request.FILES.getlist('pub_file_dir', None)
            if myFile == "":
                return HttpResponseRedirect('/monitor/MonitorManage/ConfigPublicFile/')
            for i in myFile:
                path_dst_file = '{0}/{1}'.format(pub_dir,i)
                try:
                    dir_info = '{0}'.format(pub_dir)
                    dir_name = os.path.split(dir_info)
                    if not os.path.isdir(dir_name[0]):
                        os.makedirs(dir_info)
                    destination = open(path_dst_file, 'wb+')  # 打开特定的文件进行二进制的写操作
                    for chunk in i.chunks():  # 分块写入文件
                        destination.write(chunk)
                    destination.close()
                    dstatus += "\n" + "<label style='color: #2ECC71'>%s 文件上传成功!&nbsp;&nbsp;&nbsp;</label>" % (
                        i) + "\n"
                    git_status = 'cd {0} && git status 2&>/dev/null'.format(pub_dir)
                    git_exist = os.system(git_status)
                    if git_exist == 0:
                        add = os.system('cd {1} && git add {0}'.format(path_dst_file, pub_dir))
                        commit = os.system('cd {1} &&  git commit -m "{0}"'.format(path_dst_file, pub_dir))
                        push = os.system('cd {0} && git push'.format(pub_dir))
                        if add == 0 and push == 0 and commit == 0:
                            Pub_File.objects.filter(id=int(pk)).update(
                                pub_dir=path_dst_file)
                    else:  # -----------pub_dir目录没有git仓库视为开发环境,开发环境不测试git----
                        Pub_File.objects.filter(id=int(pk)).update(
                            pub_dir=path_dst_file)
                    messages.success(request, '提交成功')
                    return HttpResponseRedirect('/monitor/MonitorManage/ConfigPublicFile/')
                except Exception as e:
                    messages.error(request, '提交失败')
                    return HttpResponseRedirect('/monitor/MonitorManage/ConfigPublicFile/')
        elif request.POST.get('pub_update_conf', None):
            file_content = request.POST['file_content']
            f1 = open(file_info, 'w')
            f1.write(file_content)
            f1.close()
            git_status = 'cd {0} && git status 2&>/dev/null'.format(pub_dir)
            git_exist = os.system(git_status)
            if git_exist == 0:
                add = os.system('cd {1} && git add {0}'.format(file_info, pub_dir))
                commit = os.system('cd {1} &&  git commit -m "{0}"'.format(file_info, pub_dir))
                push = os.system('cd {0} && git push'.format(pub_dir))
                if add == 0 and commit == 0 and push == 0:
                    messages.success(request, '提交成功')
                    return HttpResponseRedirect('/monitor/MonitorManage/ConfigPublicFile/')
                else:
                    messages.error(request, '提交失败')
                    return HttpResponseRedirect('/monitor/MonitorManage/ConfigPublicFile/')
            else:#-----------pub_dir目录没有git仓库视为开发环境,开发环境不测试git----
                messages.success(request, '提交成功')
                return HttpResponseRedirect('/monitor/MonitorManage/ConfigPublicFile/')
        elif request.POST.get('pub_file_del', None):
            tmp_dir = Pub_File.objects.filter(pub_name=pub_name)
            template_dir = tmp_dir.values_list('pub_file_name')
            git_status = 'cd {0} && git status 2&>/dev/null'.format(pub_dir)
            git_exist = os.system(git_status)
            if git_exist == 0:
                for i in template_dir:
                    print(i[0])
                    rm = os.system('cd {1} && git rm {0}'.format(i[0], pub_dir))
                    commit = os.system('cd {1} &&  git commit -m "remove {0}"'.format(i[0], pub_dir))
                    push = os.system('cd {0} && git push'.format(pub_dir))
                    if rm == 0 and commit == 0 and push == 0:
                        Pub_File.objects.filter(
                            pub_name=pub_name).filter(pub_dir=i[0]).delete()
                    else:
                        messages.error(request, '提交失败')
                        return HttpResponseRedirect('/monitor/MonitorManage/ConfigPublicFile/')
            else:#-----------pub_dir目录没有git仓库视为开发环境,开发环境不测试git----
                #print(tmp_dir,template_dir)
                for i in template_dir:
                    os.system('cd {1} && rm {0}'.format(str(i[0]).replace(" ","\ "), pub_dir))
                    Pub_File.objects.filter(
                        pub_name=pub_name).filter(pub_dir=i[0]).delete()
            messages.success(request, '提交成功')
            return HttpResponseRedirect('/monitor/MonitorManage/ConfigPublicFile/')

    return render(request,'view/systemtools/ConfigPublicFileDetail.html',{'public_info':public_info,'parameter':parameter,'info_':info_})


@login_required
def ConfigPrivateFile(request):
    """自定义私有文件管理"""
    args = "template"
    private_list = Private_Template.objects.all()
    parameter = Parameter.objects.all()
    if request.method =="POST":
        dstatus = ""
        tool_name = request.POST['tool_name']
        tool_class = request.POST['tool_class']
        tool_context = request.POST['tool_context']
        tool_parameter = request.POST.getlist('tool_parameter')
        myFile = request.FILES.getlist("tool_file_name", None)  # 获取上传的工具文件，如果没有文件，则默认为None
        myFile_conf = request.FILES.getlist("config_file_name", None)  # 获取上传的配置文件，如果没有文件，则默认为None
        config_name = request.POST['config_name']
        config_class = request.POST['config_class']
        config_context = request.POST['config_context']
        if tool_parameter == []:
            dstatus = "<label style='color: #E74C3C'>请选择参数!</label>"
            return render(request, 'view/systemtools/ConfigPrivateFile.html',
                          {'dstatus': dstatus, 'parameter': parameter})
        tool_name_info = Private_Template.objects.filter(private_template_name=tool_name).count()
        if tool_name_info>0:
            dstatus = "<label style='color: #E74C3C'>输入的工具名称或者配置文件名称有重复，请重新输入!</label>"
            return render(request, 'view/systemtools/ConfigPrivateFile.html',
                          {'dstatus': dstatus, 'parameter': parameter})

        tool_parameter_id = tool_parameter  #parameter table is id list
        for i in myFile:
            if not i:
                dstatus = "<label style='color: #E74C3C'>请选择需要上传的文件!</label>"
                return render(request, 'view/systemtools/ConfigPrivateFile.html',
                              {'private_list': private_list, 'parameter': parameter,'dstatus':dstatus})
            else:
                # path_dst_file = '{2}/{0}/{1}'.format(args, i, prv_dir)
                path_dst_file = '{0}/{1}'.format(pub_dir,i)
                print (path_dst_file)
                if os.path.isfile(path_dst_file):
                    dstatus += "\n" + "<label style='color: #E74C3C'>%s 已存在,请重名名或者重新选择文件。</label>" % (i) + "\n"
                    return render(request, 'view/systemtools/ConfigPrivateFile.html',
                                  {'private_list': private_list, 'parameter': parameter, 'dstatus': dstatus})
                else:
                    try:
                        dir_info = '{0}/'.format(pub_dir)
                        dir_name = os.path.split(dir_info)
                        if not os.path.isdir(dir_name[0]):
                            os.makedirs(dir_info)
                        destination = open(path_dst_file, 'wb+')  # 打开特定的文件进行二进制的写操作

                        Private_Template.objects.create(private_template_name=tool_name,
                                                                        private_template_class=tool_class,
                                                                        private_template_dir=path_dst_file,
                                                                        private_template_file_name=i,
                                                                        private_template_context=tool_context)
                        prv_id = Private_Template.objects.filter(
                            private_template_name=tool_name).values('id')
                        id_ = prv_id[0]['id']
                        tmp_file_id = Private_Template.objects.get(id=id_)
                        tmp_file_id.private_parameter.add(*tool_parameter_id)
                        for chunk in i.chunks():  # 分块写入文件
                            destination.write(chunk)
                        destination.close()
                        os.system('dos2unix {0}'.format(path_dst_file))
                        dstatus += "\n" + "<label style='color: #2ECC71'>%s 文件上传成功!&nbsp;&nbsp;&nbsp;</label>" % (
                            i) + "\n"
                    except Exception as e:
                        print(e)
                        messages.error(request, '提交失败')
                        return HttpResponseRedirect('/monitor/MonitorManage/ConfigPrivateFile/')
        for i in myFile_conf:
            if not i:
                dstatus = "<label style='color: #E74C3C'>请选择需要上传的文件!</label>"
            else:
                path_dst_file = '{2}/{0}/{1}'.format(args, i, prv_dir)
                print(path_dst_file)
                if os.path.isfile(path_dst_file):
                    dstatus += "\n" + "<label style='color: #E74C3C'>%s 已存在,请重名名或者重新选择文件。</label>" % (i) + "\n"
                else:
                    try:
                        dir_info = '{1}/{0}/'.format(args, prv_dir)
                        dir_name = os.path.split(dir_info)
                        if not os.path.isdir(dir_name[0]):
                            os.makedirs(dir_info)
                        Private_Template.objects.create(private_template_name=config_name,
                                                                        private_template_class=config_class,
                                                                        private_template_dir=path_dst_file,
                                                                        private_template_file_name=i,
                                                                        private_template_context=config_context)
                        destination = open(path_dst_file, 'wb+')  # 打开特定的文件进行二进制的写操作
                        for chunk in i.chunks():  # 分块写入文件
                            destination.write(chunk)
                        destination.close()
                        os.system('dos2unix {0}'.format(path_dst_file))
                        dstatus += "\n" + "<label style='color: #2ECC71'>%s 文件上传成功!&nbsp;&nbsp;&nbsp;</label>" % (
                            i) + "\n"
                    except Exception as e:
                        print (e)
                        messages.error(request, '提交失败')
                        return HttpResponseRedirect('/monitor/MonitorManage/ConfigPrivateFile/')
        # sls文件生成
        print (myFile[0])
        file_name = myFile[0]
        toolname = file_name + '.sls'
        sls_info_tool = """falcon_{0}_sh:
                file.managed:
                - name: {1}net/{0}.sh
                - source: 
                  - salt://business/falcon_plugin/pub_plugin/{0}
                - user: root
                - group: root
                - mode: 755
                - makedirs: true\n""".format(file_name,client_plugin_path)
        sls_info_config = """falcon_{0}_conf:
                file.managed:
                - name: {1}net/{0}
                - source: 
                  - salt://business/falcon_plugin/pub_plugin/{0}.cfg
                - user: root
                - group: root
                - mode: 644
                - makedirs: true""".format(file_name,client_plugin_path)
        path_dst_file = '{2}/{0}/{1}'.format(args, toolname, prv_dir)
        print(path_dst_file)
        if os.path.isfile(path_dst_file):
            dstatus += "\n" + "<label style='color: #E74C3C'>%s 已存在,请重名名或者重新选择文件。</label>" % (toolname) + "\n"
        else:
            try:
                Private_Template.objects.create(private_template_name=toolname,
                                                                private_template_class='sls',
                                                                private_template_dir=path_dst_file,
                                                                private_template_file_name=toolname,
                                                                private_template_context='sls配置文件')
                sls_file = open('{0}/{1}/{2}'.format(prv_dir, args, toolname), 'a')
                if config_name:
                    sls_file.write(sls_info_tool)
                sls_file.write(sls_info_config)
                sls_file.close()
            except Exception as e:
                print (e)
                messages.error(request, '提交失败')
                return HttpResponseRedirect('/monitor/MonitorManage/ConfigPrivateFile/')
        messages.success(request, '提交成功!')
        return HttpResponseRedirect('/monitor/MonitorManage/ConfigPrivateFile/')
    return render(request,'view/systemtools/ConfigPrivateFile.html',{'private_list':private_list,'parameter':parameter})

@login_required
def ConfigPrivateFileDetail(request,pk):
    """私有文件详情管理"""
    args = "template"
    private_info = Private_Template.objects.filter(id=int(pk))
    p = Private_Template.objects.get(id=int(pk))
    parameter = p.private_parameter.all()
    file_info = private_info.values_list('private_template_dir')[0][0]
    template_name = private_info.values_list('private_template_name')[0][0]
    try:
        f=open(file_info,'r')
        info_ = f.read()
        f.close()
    except IOError:
        Private_Template.objects.filter(id=int(pk)).delete()
        return HttpResponseRedirect('/monitor/MonitorManage/ConfigPrivateFile/')
    if request.method =="POST":
        dstatus=""
        #private_file_name = request.POST['private_file_name']
        if request.POST.get('private_update_tool',None):
            myFile = request.FILES.getlist('private_file_dir', None)
            print(myFile)
            if myFile =="":
                return HttpResponseRedirect('/monitor/MonitorManage/ConfigPrivateFile/')
            for i in myFile:
               path_dst_file = '{2}/{0}/{1}'.format(args, i, prv_dir)
               print(path_dst_file)
               # if os.path.isfile(path_dst_file):
               #     dstatus += "\n" + "<label style='color: #E74C3C'>%s 已存在,请重名名或者重新选择文件。</label>" % (i) + "\n"
               #     return render(request, 'view/systemtools/ConfigPrivateFile.html',
               #                   {'private_list': private_list, 'parameter': parameter, 'dstatus': dstatus})
               # else:
               try:
                   dir_info = '{0}/{1}/'.format(prv_dir,args)
                   dir_name = os.path.split(dir_info)
                   if not os.path.isdir(dir_name[0]):
                       os.makedirs(dir_info)
                   destination = open(path_dst_file, 'wb+')  # 打开特定的文件进行二进制的写操作
                   for chunk in i.chunks():  # 分块写入文件
                       destination.write(chunk)
                   destination.close()
                   os.system('dos2unix {0}'.format(path_dst_file))
                   dstatus += "\n" + "<label style='color: #2ECC71'>%s 文件上传成功!&nbsp;&nbsp;&nbsp;</label>" % (
                       i) + "\n"

                   Private_Template.objects.filter(id=int(pk)).update(
                       private_template_dir=path_dst_file)
                   messages.success(request, '工具更新成功')
                   return HttpResponseRedirect('/monitor/MonitorManage/ConfigPrivateFile/')
               except Exception as e:
                   messages.error(request, '提交失败')
                   return HttpResponseRedirect('/monitor/MonitorManage/ConfigPrivateFile/')
        elif request.POST.get('private_update_conf',None):
            file_content = request.POST['file_content']
            f1 = open(file_info,'w')
            f1.write(file_content)
            f1.close()
            messages.success(request, '配置更改成功')
            return HttpResponseRedirect('/monitor/MonitorManage/ConfigPrivateFile/')
        elif request.POST.get('private_file_del',None):
            tmp_dir = Private_Template.objects.filter(private_template_name=template_name)
            template_dir = tmp_dir.values_list('private_template_file_name')

            for i in template_dir:
                os.system('cd {1} && rm {0}'.format(str(i[0]).replace(" ","\ "), pub_dir))
                Private_Template.objects.filter(private_template_name=template_name).filter(
                    private_template_dir=i[0]).delete()
            messages.success(request, '提交成功')
            return HttpResponseRedirect('/monitor/MonitorManage/ConfigPrivateFile/')
    return render(request,'view/systemtools/ConfigPrivateFileDetail.html',{'private_info':private_info,'parameter':parameter,'info_':info_})

@login_required
def ConfigPrivateFileDetail_core(request,pk):
    """私有文件详情管理"""
    args = "template"
    private_info = Private_Template.objects.filter(id=int(pk))
    p = Private_Template.objects.get(id=int(pk))
    parameter = p.private_parameter.all()
    file_info = private_info.values_list('private_template_dir')[0][0]
    template_name = private_info.values_list('private_template_name')[0][0]
    try:
        f=open(file_info,'r')
        info_ = f.read()
        f.close()
    except IOError:
        Private_Template.objects.filter(id=int(pk)).delete()
        return HttpResponseRedirect('/monitor/MonitorManage/ConfigPrivateFile/')
    if request.method =="POST":
        dstatus=""
        #private_file_name = request.POST['private_file_name']
        if request.POST.get('private_update_tool',None):
            myFile = request.FILES.getlist('private_file_dir', None)
            print(myFile)
            if myFile =="":
                return HttpResponseRedirect('/monitor/MonitorManage/ConfigPrivateFile/')
            for i in myFile:
               path_dst_file = '{2}/{0}/{1}'.format(args, i, prv_dir)
               try:
                   dir_info = '{0}/{1}/'.format(prv_dir,args)
                   dir_name = os.path.split(dir_info)
                   if not os.path.isdir(dir_name[0]):
                       os.makedirs(dir_info)
                   destination = open(path_dst_file, 'wb+')  # 打开特定的文件进行二进制的写操作
                   for chunk in i.chunks():  # 分块写入文件
                       destination.write(chunk)
                   destination.close()
                   os.system('dos2unix {0}'.format(path_dst_file))
                   dstatus += "\n" + "<label style='color: #2ECC71'>%s 文件上传成功!&nbsp;&nbsp;&nbsp;</label>" % (
                       i) + "\n"

                   Private_Template.objects.filter(id=int(pk)).update(
                       private_template_dir=path_dst_file)
                   messages.success(request, '工具更新成功')
                   return HttpResponseRedirect('/monitor/MonitorManage/ConfigPrivateFile/')
               except Exception as e:
                   messages.error(request, '提交失败')
                   return HttpResponseRedirect('/monitor/MonitorManage/ConfigPrivateFile/')
        elif request.POST.get('private_update_conf',None):
            file_content = request.POST['file_content']
            f1 = open(file_info,'w')
            f1.write(file_content)
            f1.close()

            messages.success(request, '配置更改成功')
            return HttpResponseRedirect('/monitor/MonitorManage/ConfigPrivateFile/')
        elif request.POST.get('private_file_del',None):
            tmp_dir = Private_Template.objects.filter(private_template_name=template_name)
            template_dir = tmp_dir.values_list('private_template_file_name')

            for i in template_dir:
                os.system('cd {1} && rm {0}'.format(str(i[0]).replace(" ","\ "), pub_dir))
                Private_Template.objects.filter(private_template_name=template_name).filter(
                    private_template_dir=i[0]).delete()
            messages.success(request, '提交成功')
            return HttpResponseRedirect('/monitor/MonitorManage/ConfigPrivateFile/')
    return render(request,'view/systemtools/ConfigPrivateFileDetail_core.html',{'private_info':private_info,'parameter':parameter,'info_':info_})

@login_required
def one_click_sync_salt(request,):
    dev_file_list = []
    if request.method == 'POST':
        host_list_obj = Host.objects.filter(host_grp_id=int(request.POST['Id'])).all()
        dev_file_list = [i.hostname for i in host_list_obj]
        para_group_obj = ParameterGroup.objects.filter(param_group_device_group__id=int(request.POST['Id'])).all()
        para_group_list = [i.param_group_dir for i in para_group_obj]
        import salt.client
        salt_local = salt.client.LocalClient()
        for x in dev_file_list:
            s = salt_local.run_job(x,'test.ping')
            if s.has_key('jid'):
                try:#----直接目录同步，不再查询数据库关联信息
                    for i in para_group_list:
                        for root, dir, file in os.walk(prv_dir+'/'+i):
                            for File in file:
                                salt_local.cmd(x, 'cp.get_file',['salt://{0}'.format(i+'/'+File), '{0}'.format(client_plugin_path+i+'/'+File), 'gzip=9','makedirs=True'])
                                salt_local.cmd(x, 'cmd.run',['chmod 755 {0}'.format(client_plugin_path+i+'/'+File)])
                except Exception as e:
                    print(e)
                    pass
            else:
                print(x+' has No minions')
    return HttpResponse('一键同步绑定参数组目录内采集工具到边缘节点上')


@login_required
def AddHostTogrp(request,):
    if request.method == "POST":
        host_name = request.POST['host_name']
        groupname = request.POST['groupname']
        grp_id = int(request.POST['id'])

        host_id_sql = 'select id,ip from host where hostname ="{0}"'.format(host_name)
        host_id = db_falcon.select_table(host_id_sql)
        if host_id == []:
            host_add_sql = 'insert ignore into host(hostname) values("{0}")'.format(host_name)
            db_falcon.mysql_command(host_add_sql)
            host_id = db_falcon.select_table(host_id_sql)
            host_grp_exist_sql = 'select count(*) from grp_host where grp_id = {0} and host_id = {1}'.format(grp_id,
                                                                                                             int(host_id[0]))
            if db_falcon.select_table(host_grp_exist_sql)[0] == 0:
                host_grp_sql = 'insert ignore into grp_host(grp_id,host_id) values({0},{1})'.format(grp_id, int(host_id[0]))
                db_falcon.mysql_command(host_grp_sql)
            return HttpResponse(u'重要提示：{0} 未安装falcon客户端，已添加到 {1} 设备组中'.format(host_name, groupname))
        else:
            host_grp_exist_sql = 'select count(*) from grp_host where grp_id = {0} and host_id = {1}'.format(grp_id,
                                                                                                             int(host_id[0]))
            if db_falcon.select_table(host_grp_exist_sql)[0] == 0:
                host_grp_sql = 'insert ignore into grp_host(grp_id,host_id) values({0},{1})'.format(grp_id, int(host_id[0]))
                db_falcon.mysql_command(host_grp_sql)
            if host_id[1] == '':
                return HttpResponse(u'{0} 未安装falcon客户端，已添加到 {1} 设备组中'.format(host_name, groupname))
    return HttpResponse(u'{0} 已安装falcon客户端，已添加到 {1} 设备组中'.format(host_name,groupname))
