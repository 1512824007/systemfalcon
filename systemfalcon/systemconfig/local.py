#!/usr/bin/python2.6.6
# -*- coding:utf-8 -*-
import salt.client

def post(tgt,fun,arg,expr_form):
    CMD = [
        'cmd.run', 'cmd.script', 'cp.get_dir', 'cp.get_file', 'cp.get_url', 'cron.ls',
        'disk.usage',
        'grains.item', 'grains.items',
        'network.interfaces',
        'service.status', 'service.start', 'service.restart', 'service.get_all',
        'state.running', 'state.sls', 'state.highstate',
        'status.uptime', 'status.meminfo',
        'system.halt', 'system.init', 'system.poweroff', 'system.reboot', 'system.shutdown',
        'test.ping'
    ]
    timeout = None
    Arg = [arg]
    local = salt.client.LocalClient()
    FL = CMD
    if fun in FL:
        if fun in ['disk.usage', 'network.interfaces', 'grains.items', 'test.ping', 'state.running', 'status.meminfo',
                   'status.uptime', 'service.get_all', 'system.halt', 'system.init', 'system.poweroff', 'system.reboot',
                   'system.shutdown']:
            Arg = []
        elif fun in ['cp.get_dir', 'cp.get_file', 'cp.get_url', 'cron.ls']:
            Arg = arg.split()
        elif fun == 'cmd.script':
            a = arg.split()
            a1 = a[0]
            a2 = ' '.join(a[1:])
            Arg = [a1, a2]
        try:
            rt = local.run_job(tgt=tgt, fun=fun, arg=Arg, timeout=timeout, expr_form=expr_form)
        except Exception as e:
            print("SaltStack Exception: ", Exception, ":", e)
        return(rt)
