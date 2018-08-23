# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from django.http import HttpResponse
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from sysconf.models import room_bandwidth, Module, Module_group, GrpGroup, ClassMod
from r_csv import load_csv
from userauth.models import Profile, GroupProfile
from userauth.is_group import is_group
from userauth.in_module import return_module
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from HcGraph import mysql
from top10 import mysql_falcon
from django.contrib.auth.models import User, Group
import re, xml.dom.minidom
import logging,json
from logging.handlers import TimedRotatingFileHandler
# Create your views here.

db = mysql.db_operate()
db_falcon = mysql_falcon.db_operate()

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


@is_group('Manager')
def show0(request,):
    return "true"


def show(request,):
    if show0(request,) == "true":
        return "true"
    else:
        return "false"


@login_required
def room_band(request,):
    r = room_bandwidth.objects.exclude(province=u'省份').exclude(idc_name=None).values()
    paginator = Paginator(r, 12)
    page = request.GET.get('page')
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        contacts = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        contacts = paginator.page(paginator.num_pages)
    return render(request, 'sysconf/room_band.html', locals())


@is_group('sys')
def uploadFile(request,):
    if request.method == "POST":
        f_path = '/systemfalcon/systemfalcon/static/sysconf/'
        myFile = request.FILES.get("myfile", None)
        if not myFile:
            return HttpResponse("no files for upload!")
        with open(f_path+myFile.name, 'wb+') as destination:
            for chunk in myFile.chunks():
                destination.write(chunk)
        ok = myFile.name+u'文件已上传'
        load_csv()
        r = room_bandwidth.objects.exclude(province=u'省份').exclude(idc_name=None).values()
        return render(request, 'sysconf/room_band.html', locals())

@is_group('sys')
def user_import(request,):
    if request.method == "POST":
        #-----form方式提交,return不方便弹窗提示,后续可以改redirect刷新相同页面
        #myFile = request.FILES.get("myfile", None)
        #if not myFile:
        #    return HttpResponse("no files for upload!")
        #s = [chunk for chunk in myFile.chunks()]

        #--ajax方式,数据传递,不刷新页面,返回可弹窗
        myFile = request.POST['myfile']
        r = []
        for i in myFile.split():
            try:
                if '@' in i:
                    if '@gosun.com' in i or '@gw500.com' in i:
                        is_a = User.objects.get(email=i).is_active
                    else:
                        is_a = User.objects.get(username=str(i.split('@')[0])).is_active
                else:
                    is_a = User.objects.get(username=i).is_active
                r +=[i,is_a]
            except User.DoesNotExist:
                if '@' in i:
                    if '@gosun.com' in i:
                        user = User.objects.create_user(username=str(i.split('@')[0]),email=str(i.split('@')[0])+'@gosun.com', password='123456')
                    elif '@gw500.com' in i:
                        user = User.objects.create_user(username=str(i.split('@')[0]),
                                                        email=str(i.split('@')[0]) + '@gw500.com', password='123456')
                    else:
                        user = User.objects.create_user(username=str(i),email=str(i)+'@gosun.com',password='123456')
                else:
                    user = User.objects.create_user(username=str(i),email=str(i)+'@gosun.com', password='123456')
                user.is_active = True
                user.save()
        if r == []:
            return HttpResponse("用户已全部导入")
        else:
            return HttpResponse("{0} 用户或者邮箱已存在,其他用户已导入".format(r))

@is_group('sys')
def user_del(request,):
    if request.method == "POST":
        id = request.POST['Id']
        user_name = request.POST['user_name']
        User.objects.filter(id=id).delete()
        logger.info("{0} delete group named {1}".format(request.user, user_name))
        return HttpResponse("用户已删除")

@is_group('sys')
def updateband(request,):
    input_content = request.POST['input_content']
    col = request.POST['Col']
    id = request.POST['tdId']
    old_col = request.POST['old_content']
    update_sql = "update sysconf_room_bandwidth set {0} = '{1}' where id = {2} ;".format(col,input_content,id)
    db.mysql_command(update_sql)
    logger.info("user {3} update {0} from '{4}' to {1}' where idcname = {2}".format(col, input_content, room_bandwidth.objects.get(id=id),request.user, old_col))
    return HttpResponse("数据已更新")


@login_required
def user_manage(request,):
    return render(request, 'sysconf/user_manage.html', locals())

@login_required
def user_manage_op(request,):
    return render(request, 'sysconf/user_manage.html', locals())

@login_required
def user_center(request,):
    return render(request, 'sysconf/user_center.html', locals())

@login_required
def user_show(request,):
    sql_ug = "select u.username,g.name,u.email,u.is_active,u.last_login,u.date_joined \
    from auth_user_groups as ug,auth_user as u, auth_group as g \
    where u.id = ug.user_id and g.id = ug.group_id;"
    ug = db.mysql_command(sql_ug)

    if request.GET.has_key('account'):
        account = request.GET['account']
        request.session['account'] = account
    else:
        account = ""
    if request.GET.has_key('account_id'):
        account_id = request.GET['account_id']
        request.session['account_id'] = account_id
    else:
        account_id = ""
    if request.GET.has_key('email'):
        email = request.GET['email']
        request.session['email'] = email
    else:
        email = ""

    try:
        account = request.session['account']
    except KeyError:
        account = ""
    try:
        account_id = request.session['account_id']
    except KeyError:
        account_id = ""
    try:
        email = request.session['email']
    except KeyError:
        email = ""
    u = User.objects.filter(username__contains=account).filter(id__contains=account_id).filter(email__contains=email).values('id', 'username', 'email', 'is_active', 'last_login', 'date_joined').order_by('id')
    height = 5
    if request.GET.has_key('height'):
        height = request.GET['height']
    paginator = Paginator(u, height)
    page = request.GET.get('page')
    if request.method == "POST":
        height = request.POST['height']
        paginator = Paginator(u, height)
        try:
            contacts = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            contacts = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            contacts = paginator.page(paginator.num_pages)
        return render(request, 'sysconf/log_list.html', locals())
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        contacts = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        contacts = paginator.page(paginator.num_pages)
    return render(request, 'sysconf/user_show.html', locals())

@is_group('sys')
def user_active(request,):
    if request.method == "POST":
        id  = request.POST['id']
        active = request.POST['active']
        sql  = "update auth_user set is_active = {0} where id ={1};".format(active,id)
        db.mysql_command(sql)
    return HttpResponse("用户登录权限变更")


@login_required
def groupAdd(request,):
    per = Module.objects.all()
    grp_sql = "select id,grp_name from grp"
    grp_name = db_falcon.mysql_command(grp_sql)
    is_show = show(request,)
    return render(request, 'sysconf/groupAdd.html', locals())


@is_group('sys')
def group_add(request,):

    if request.method == 'POST':
        id_name = request.POST['id_name']
        mod_id = request.POST['mod_id']
        grp = request.POST['grp']
        des = request.POST['des']
        if str(id_name) == '' or re.match(' ', str(id_name)):
            return HttpResponse("对不起，请输入组名（或者删除空格）")
        else:
            try:
                group = Group.objects.create(name=id_name)
                group.save()
                gid = int(Group.objects.get(name=id_name).id)
                GroupProfile.objects.filter(group_id=gid).update(description=des.split('"')[1])
                logger.info("{0} create group named {1}".format(request.user, id_name))
            except Exception as e:
                print(e)
                return HttpResponse("对不起，组名以存在,请勿重复建组")

        for i in list(eval(mod_id)):
            mod_name = Module.objects.get(id=int(i)).module_name
            Module_group.objects.create(group_id=gid, module_id=int(i))
            logger.info("{0} add module {1} into group {2} ".format(request.user, mod_name, id_name))

        for i in list(eval(grp)):
            grp_sql = "insert into sysconf_grpgroup(group_id,grp)values({0},{1});".format(gid,int(i))
            grp_exist_sql = "select * from sysconf_grpgroup where group_id = {0} and grp ={1};".format(gid,int(i))
            if db.mysql_command(grp_exist_sql) == []:
                grp_name_sql = "select grp_name from grp where id={0}".format(int(i))
                grp_name = db_falcon.mysql_command(grp_name_sql)[0][0]
                db.mysql_command(grp_sql)
                logger.info("{0} add device_group {1} into group {2} ".format(request.user, grp_name.encode('UTF-8') , id_name))
    return HttpResponse("数据已更新")


@login_required
def group_manage(request,):
    usr = User.objects.values_list('username','id')
    return render(request, 'sysconf/group_manage.html', locals())

@login_required
def user_manage_op(request,):
    if request.method == "GET":
        id = request.GET['id']
        username = request.GET['name']
    usr = User.objects.filter(username=username).values()[0]
    group_ori = Group.objects.values()
    try:
        group = Group.objects.filter(user=id).values()[0]
    except Exception as e:
        group = Group.objects.filter(user=id).values()
    try:
        profile = Profile.objects.filter(user__username=username).values()[0]
    except Exception as e:
        profile = Profile.objects.filter(user__username=username).values()
    group_in = Group.objects.filter(user=id).values_list('id', 'name')
    group_no = Group.objects.exclude(user=id).values_list('id', 'name')
    l = ['id', 'value']
    group_i = json.dumps([dict(zip(l, i)) for i in group_in])
    group_n = json.dumps([dict(zip(l, i)) for i in group_no])
    return render(request, 'sysconf/user_manage_op.html', locals())

@login_required
def user_detail_op(request,):
    if request.method == "GET":
        id = request.GET['id']
        username = request.GET['username']
    usr = User.objects.filter(username=username).values()[0]
    group = Group.objects.filter(user=id).values()
    module = return_module(request,id)
    try:
        profile = Profile.objects.filter(user__username=username).values()[0]
    except Exception as e:
        profile = Profile.objects.filter(user__username=username).values()
    group_in = Group.objects.filter(user=id).values_list('id', 'name')
    return render(request, 'sysconf/user_detail_op.html', locals())

@login_required
def group_change(request,):
    user = request.GET['user']
    username = request.GET['username']
    group_in = Group.objects.filter(user=user).values_list('id','name')
    group_no = Group.objects.exclude(user=user).values_list('id','name')
    is_show = show(request, )
    return render(request, 'sysconf/group_change.html', locals())


@is_group('sys')
def group_save(request,):
    if request.method == "POST":
        uid = request.POST["uId"]
        gid = request.POST['gId']
        username = request.POST['username']

        new_real_name = request.POST["new_real_name"]
        new_phone = request.POST["new_phone"]
        new_role = request.POST["new_role"]
    try:
        Profile.objects.filter(user=uid).update(realName=new_real_name,phone=new_phone,is_director=new_role)
    except Exception as e:
        print e
    sql_old = "select group_id from auth_user_groups where user_id = {0}".format(int(uid))
    ug_old = db.mysql_command(sql_old)
    for i in list(eval(gid)):
        sql_exits = "select user_id,group_id from auth_user_groups where user_id = {0} and group_id = {1};".format(int(uid), int(i))
        ug = db.mysql_command(sql_exits)
        if ug == []:
            sql_add = "insert into auth_user_groups(user_id,group_id)values(%s,%s)" %(int(uid), int(i))
            db.mysql_command(sql_add)
            groupname = Group.objects.get(id=int(i)).name
            logger.info("{0} add user {1} into group {2}".format(request.user, username, groupname))
    for i in ug_old:
        import operator
        if not any([operator.eq(int(i[0]), int(x)) for x in list(eval(gid))]):
            sql_del = "delete from auth_user_groups where user_id = {0} and group_id = {1}".format(int(uid), int(i[0]))
            db.mysql_command(sql_del)
            groupname = Group.objects.get(id=int(i[0])).name
            logger.info("{0} delete user {1} from group {2}".format(request.user, username, groupname))
    return HttpResponse("数据已更新")

@login_required
def group_center(request,):
    return render(request, 'sysconf/group_center.html', locals())

@login_required
def groupManage(request,):
    l = ['id', 'value']
    per = Module.objects.values_list('id','module_name')
    per_all = json.dumps([dict(zip(l, i)) for i in per])

    grp_sql = "select id,grp_name from grp"
    grp_name = db_falcon.mysql_command(grp_sql)
    device_group = json.dumps([dict(zip(l, i)) for i in grp_name])
    #---将参数保存到会话，便于页面高度调整不丧失查询结果
    if request.GET.has_key('account'):
        account = request.GET['account']
        request.session['account'] = account
    else:
        account = ""
    if request.GET.has_key('group_name'):
        group_name = request.GET['group_name']
        request.session['group_name'] = group_name
    else:
        group_name = ""

    #---将会话保存的键值提取方便过滤
    try:
        group_name = request.session['group_name']
    except KeyError:
        group_name = ""
    try:
        account = request.session['account']
        name_id = User.objects.filter(username=account).values_list('id')
        all_id = [i[0] for i in name_id]
        if account == "":
            grp = Group.objects.filter(name__contains=group_name).values()
        else:
            grp = Group.objects.filter(name__contains=group_name).filter(user__in=all_id).values()
    except User.DoesNotExist:
        grp = []
    except KeyError:
        grp = Group.objects.filter(name__contains=group_name).values()

    grpprofile= GroupProfile.objects.values()
    user_group = []
    for i in grp:
        obj = User.objects.filter(groups=i['id']).values('username')
        mod = Module.objects.filter(module_group__group=i['id']).values('module_name')
        module = [y['module_name'] for y in mod]
        user = [x['username'] for x in obj]
        user_group += [(i['id'],user,module)]
    height = 5
    if request.GET.has_key('height'):
        height = request.GET['height']
    paginator = Paginator(sorted(grp), height)
    if request.method == "POST":
        height = request.POST['height']
        paginator = Paginator(grp, height)
        page = request.GET.get('page')
        try:
            contacts = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            contacts = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            contacts = paginator.page(paginator.num_pages)
        return render(request, 'sysconf/groupManage.html', locals())
    page = request.GET.get('page')
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        contacts = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        contacts = paginator.page(paginator.num_pages)
    return render(request, 'sysconf/groupManage.html', locals())


@login_required
def group_manage_op(request,):
    if request.GET.has_key('id'):
        id = request.GET['id']
    if request.GET.has_key('name'):
        name = request.GET['name']
    description = GroupProfile.objects.filter(group=int(id)).values_list('description')
    sql_uid = "select a.id, a.username from auth_user as a,auth_user_groups as b where a.id = b.user_id and b.group_id = {0}".format(int(id))
    sql_nouid = "select id,username from auth_user where id not in(select user_id from auth_user_groups where group_id={0})".format(int(id))
    usr_in = db.mysql_command(sql_uid)
    usr_no = db.mysql_command(sql_nouid)
    l = ['id', 'value']
    usr_n = json.dumps([dict(zip(l, i)) for i in usr_no])
    usr_i = json.dumps([dict(zip(l, i)) for i in usr_in])
    mod_no = Module.objects.exclude(module_group__group=int(id)).values_list('id','module_name')
    mod_in = Module.objects.filter(module_group__group=int(id)).values_list('id','module_name')
    mod_i = json.dumps([dict(zip(l, i)) for i in mod_in])
    mod_n = json.dumps([dict(zip(l, i)) for i in mod_no])
    group_in = GrpGroup.objects.filter(group=int(id)).values_list('grp')
    if group_in.__len__() > 1:
        temp =  tuple([int(i[0]) for i in group_in])
        device_group_sql1 = "select id,grp_name from grp where id not in {0};".format(temp)
        device_group_sql2 = "select id,grp_name from grp where id in {0};".format(temp)
    elif group_in.__len__() == 1:
        temp = int(group_in[0][0])
        device_group_sql1 = "select id,grp_name from grp where id != {0};".format(temp)
        device_group_sql2 = "select id,grp_name from grp where id = {0};".format(temp)
    else:
        device_group_sql1 = "select id,grp_name from grp;"
        device_group_sql2 = "select id,grp_name from grp where id = 0;"
    grp_no = db_falcon.mysql_command(device_group_sql1)
    grp_in = db_falcon.mysql_command(device_group_sql2)
    grp_i = json.dumps([dict(zip(l, i)) for i in grp_in])
    grp_n = json.dumps([dict(zip(l, i)) for i in grp_no])
    return render(request, 'sysconf/group_manage_op.html', locals())

@login_required()
def group_change2(request,):
    if request.method == "POST":
        id = request.POST['id']
        new_name = request.POST['new_name']
        new_des = request.POST['new_description']
        old_name = request.POST['old_name']
        #old_des = request.POST['old_des']
        if old_name== str(new_name.split('"')[1]):
            pass
        else:
            Group.objects.filter(id=id).update(name=new_name.split('"')[1])
            logging.info("{0} change group_name from {1} to {2}".format(request.user, old_name, new_name))
        if not GroupProfile.objects.filter(group_id=id).values_list('date').exists():
            GroupProfile.objects.create(group_id=id)
        GroupProfile.objects.filter(group_id=id).update(description=new_des.split('"')[1])
        logging.info("{0} change group_description from  to {1}".format(request.user, new_des))
        return HttpResponse(u'组名\描述已更新')

@is_group('sys')
def group_save2(request,):
    if request.method == "POST":
        uid = request.POST["user"]
        gid = request.POST['gId']
        grp_name = request.POST['grp_name']
        per_id = request.POST["per_id"]
        grp_id = request.POST['grp']
        from userauth.tasks import add_del_group_grp, add_del_group_module,add_del_group_user
        user = request.user
        #-------组关联用户增删
        sql_old = "select user_id from auth_user_groups where group_id = {0}".format(int(gid))
        uid_old = db.mysql_command(sql_old)
        #add_del_group_user.delay(user,uid,gid,uid_old,grp_name)
        add_del_group_user(user,uid,gid,uid_old,grp_name)
        #-------组关联模块增删
        sql_old = "select module_id from sysconf_module_group where group_id = {0}".format(int(gid))
        ug_old = db.mysql_command(sql_old)
        #add_del_group_module.delay(user,per_id,gid,ug_old,grp_name)
        add_del_group_module(user,per_id,gid,ug_old,grp_name)
        #---------组关联设备组增删
        device_old = GrpGroup.objects.filter(group=int(gid)).values_list('grp')
        #add_del_group_grp.delay(user,gid,grp_id,device_old,grp_name)
        add_del_group_grp(user,gid,grp_id,device_old,grp_name)
    return HttpResponse("组属已提交异步更新，请过后查看")


@is_group('sys')
def group_del(request,):
    if request.method == "POST":
        gid = request.POST['gId']
        grp_name = request.POST['grp_name']
    Group.objects.filter(id=gid).delete()
    logger.info("{0} delete group named {1}".format(request.user, grp_name))
    return HttpResponse("用户组已删除")


@is_group('sys')
def group_c_name(request,):
    if request.method == "POST":
        idname = request.POST['idname']
        gid = request.POST['gid']
        gname = request.POST['gname']
    if str(idname) == '' or re.match(' ', str(idname)):
        return HttpResponse("对不起，请输入组名（或者删除空格）")
    else:
        Group.objects.filter(id=gid).update(name=idname)
        logger.info("{0} change group_name from {1} to {2}".format(request.user, gname, idname))
        return HttpResponse("组名已更新,请刷新查看")


@login_required
def read_user_xml(request,):
    doc = xml.dom.minidom.Document()
    root = doc.createElement('用户')
    doc.appendChild(root)
    user = User.objects.all()
    for i in user:
        nodeusername = doc.createElement(i.username)
        nodeid = doc.createElement('ID')
        nodegid = doc.createElement('GID')
        nodename = doc.createElement('用户名')
        nodeemail = doc.createElement('用户邮箱')
        nodephone = doc.createElement('用户手机号')
        #nodecompany = doc.createElement('公司')
        #nodedepartment = doc.createElement('部门')
        #nodestation = doc.createElement('岗位')
        nodeid.appendChild(doc.createTextNode(str(i.id)))
        for g in Group.objects.filter(user=i.id):
            nodegroupid = doc.createElement('groupID')
            nodegroupid.appendChild(doc.createTextNode(str(g.id)))
            nodegid.appendChild(nodegroupid)
        nodename.appendChild(doc.createTextNode(str(i.username)))
        nodeemail.appendChild(doc.createTextNode(str(i.email)))

        nodephone.appendChild(doc.createTextNode(str(Profile.objects.get(user=i.id).phone)))
        nodeusername.appendChild(nodeid)
        nodeusername.appendChild(nodegid)
        nodeusername.appendChild(nodename)
        nodeusername.appendChild(nodeemail)
        nodeusername.appendChild(nodephone)
        #nodeusername.appendChild(nodecompany)
        #nodeusername.appendChild(nodedepartment)
        #nodeusername.appendChild(nodestation)
        root.appendChild(nodeusername)
    with open('/systemfalcon/systemfalcon/sysconf/templates/sysconf/用户.xml', 'w') as fp:
        doc.writexml(fp, indent='\t', addindent='\t', newl='\n', encoding="utf-8")
    return render(request,'sysconf/用户.xml', content_type="xml")


@login_required
def read_group_xml(request,):
    doc = xml.dom.minidom.Document()
    root = doc.createElement('用户组')
    doc.appendChild(root)
    group = Group.objects.all()
    for i in group:
        nodegroupname = doc.createElement(i.name)
        nodegid = doc.createElement('GID')
        nodename = doc.createElement('用户组名')
        #nodedes = doc.createElement('用户组描述')
        nodegid.appendChild(doc.createTextNode(str(i.id)))
        nodename.appendChild(doc.createTextNode(str(i.name)))
        #nodedes.appendChild(doc.createTextNode(str(i.description)))
        nodegroupname.appendChild(nodegid)
        nodegroupname.appendChild(nodename)
        root.appendChild(nodegroupname)
    with open('/systemfalcon/systemfalcon/sysconf/templates/sysconf/用户组.xml', 'w') as fp:
        doc.writexml(fp, indent='\t', addindent='\t', newl='\n', encoding="utf-8")
    return render(request,'sysconf/用户组.xml', content_type="xml")


@login_required
def module_add(request,):
    if request.method == "POST":
        m_name = request.POST['module_name']
        remarks = request.POST['remarks']
        temp =  Module.objects.get_or_create(module_name=m_name,remarks=remarks.split('"')[1])
        if not temp[1]:
            return HttpResponse('版块已存在')
        else:
            logger.info("{0} add module named {1}".format(request.user, m_name))
            return HttpResponse('已增加版块')
    is_show = show(request,)
    mod = Module.objects.values()
    return render(request,'sysconf/module_add.html',locals())


@is_group('sys')
def module_del(request,):
    if request.method == "POST":
        m_name = request.POST['module_name']
        try:
            Module.objects.filter(module_name=m_name).delete()
            logger.info("{0} delete module named {1}".format(request.user, m_name))
            return HttpResponse("版块已删除")
        except Exception as e:
            print e
            return HttpResponse("版块删除失败")

@is_group('sys')
def module_change(request,):
    if request.method == "POST":
        m_name = request.POST['module_name']
        new_name = request.POST['new_name']
        try:
            Module.objects.filter(module_name=m_name).update(module_name=new_name)
            logger.info("{0} change module_name from {1} to {2}".format(request.user, m_name, new_name))
            return HttpResponse("版块名已更新")
        except Exception as e:
            print e
            return HttpResponse("版块更新失败")

@login_required
def log_center(request,):
    return render(request, 'sysconf/log_center.html', locals())

@login_required
def log_list(request,):
    log = []
    row_nu = 0
    max_nu = 30
    if request.GET.has_key('account'):
        account = request.GET['account']
        request.session['account'] = account
    else:
        account = ""
    if request.GET.has_key('begin'):
        begin = request.GET['begin']
        request.session['begin'] = begin
    else:
        begin = ""
    if request.GET.has_key('over'):
        over = request.GET['over']
        request.session['over'] = over
    else:
        over = ""
    import os,time
    try:
        account = request.session['account']
    except KeyError:
        account = ""
    try:
        begin = request.session['begin']
    except KeyError:
        begin = ""
    try:
        over = request.session['over']
    except KeyError:
        over = ""
    try:
        begin_unix = time.mktime(time.strptime(begin,"%Y-%m-%d %H:%M"))
    except ValueError:
        begin_unix = 1503178400.0
    try:
        over_unix = time.mktime(time.strptime(over, "%Y-%m-%d %H:%M"))
    except ValueError:
        over_unix = time.time()
    for i in os.walk(os.path.dirname(LOG_FILENAME)):
        logfile = sorted(i[2],reverse=True)[-1]
        logfile_old = sorted(i[2],reverse=True)[:-1]
    with open(os.path.dirname(LOG_FILENAME)+'/'+logfile) as logFile:
        for row in reversed(logFile.readlines()):
            try:
                if  row.split(" ",)[5] == "root" and account in row.split(" ", )[7]:
                    if row_nu < max_nu:
                        s = row.split(" ", )[:2]
                        log_time = time.mktime(
                            time.strptime(str(s[0] + " " + s[1].split(",", )[0]), "%Y-%m-%d %H:%M:%S"))
                        if begin_unix < log_time < over_unix:
                            row_nu += 1
                            log += [[row.split(" ", ), (row.split("-")[5],)]]
                    else:
                        break
            except Exception as e:
                #print e
                pass
    for s in logfile_old:
        with open(os.path.dirname(LOG_FILENAME)+'/'+s) as logFile_old:
            for row in reversed(logFile_old.readlines()):
                try:
                    if  row.split(" ",)[5] == "root" and account in row.split(" ", )[7]:
                        if row_nu < max_nu:
                            s = row.split(" ",)[:2]
                            log_time = time.mktime(time.strptime(str(s[0] + " " + s[1].split(",", )[0]), "%Y-%m-%d %H:%M:%S"))
                            if begin_unix < log_time < over_unix:
                                row_nu += 1
                                log += [[row.split(" ", ), (row.split("-")[5],)]]
                        else:
                            break
                except Exception as e:
                    #print e
                    pass
    height = 5
    if request.GET.has_key('height'):
        height = request.GET['height']
    paginator = Paginator(log, height)
    page = request.GET.get('page')
    if request.method == "POST":
        height = request.POST['height']
        paginator = Paginator(log, height)
        try:
            contacts = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            contacts = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            contacts = paginator.page(paginator.num_pages)
        return render(request, 'sysconf/log_list.html', locals())
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        contacts = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        contacts = paginator.page(paginator.num_pages)
    return render(request, 'sysconf/log_list.html', locals())

@is_group('sys')
@login_required
def classmod_man(request,):
    if request.method == "POST":
        m_name = request.POST['class_mod']
        parameter = request.POST['parameter']
        result = request.POST['result']
        api = request.POST['api']
        remarks = request.POST['remarks']
        temp =  ClassMod.objects.get_or_create(class_mod=m_name,parameter=parameter,result=result,api=api,remarks=remarks.split('"')[1])
        if not temp[1]:
            return HttpResponse('模块已存在')
        else:
            logger.info("{0} add class_mod named {1}".format(request.user, m_name))
            return HttpResponse('已增加模块')
    is_show = show(request,)
    mod = ClassMod.objects.values()
    return render(request,'sysconf/classmod_man.html',locals())


@is_group('sys')
def class_mod_del(request,):
    if request.method == "POST":
        m_name = request.POST['classmod']
        try:
            ClassMod.objects.filter(class_mod=m_name).delete()
            logger.info("{0} delete class_mod named {1}".format(request.user, m_name))
            return HttpResponse("模块已删除")
        except Exception as e:
            print(e)
            return HttpResponse("模块删除失败")

@is_group('sys')
def class_mod_change(request,):
    if request.method == "POST":
        m_name = request.POST['module_name']
        new_name = request.POST['new_name']
        try:
            ClassMod.objects.filter(class_mod=m_name).update(class_mod=new_name)
            logger.info("{0} change class_mod from {1} to {2}".format(request.user, m_name, new_name))
            return HttpResponse("模块名已更新")
        except Exception as e:
            print(e)
            return HttpResponse("模块更新失败")


@login_required
def classmod_list(request,):
    class_mod = ClassMod.objects.all().order_by('id')
    height = 5
    if request.GET.has_key('height'):
        height = request.GET['height']
    paginator = Paginator(class_mod, height)
    page = request.GET.get('page')
    if request.method == "POST":
        height = request.POST['height']
        paginator = Paginator(class_mod, height)
        try:
            contacts = paginator.page(page)
        except PageNotAnInteger:
            # If page is not an integer, deliver first page.
            contacts = paginator.page(1)
        except EmptyPage:
            # If page is out of range (e.g. 9999), deliver last page of results.
            contacts = paginator.page(paginator.num_pages)
        return render(request, 'sysconf/classmod_list.html', locals())
    try:
        contacts = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        contacts = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        contacts = paginator.page(paginator.num_pages)
    return render(request, 'sysconf/classmod_list.html', locals())


def ce_shi(request,):
    return render(request,'sysconf/ce_shi.html',locals())

