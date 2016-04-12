#coding: utf-8
'''
Created on 2016-03-12

@author: yangchuangliang
'''
from threading import Thread,Lock
import datetime
import socket
import select
import time
import os
import re

'''
*    控制线程，复制与所有的proxy 客户端通信，控制压力进行测试
'''
class ctrl_thread(Thread):
    def __init__(self, host, port):
        Thread.__init__(self)
        self.socket = None
        self.addr = (host, int(port))
        self.proxys = {}
        self.run_state = 'init'

    def _deal_socket_error(self, sock_except):
        print sock_except, ' will sleep 5s'
        self.socket.close()
        self.socket = None

    def run(self):
        while self.run_state != 'stop':
            if self.socket == None:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                try:
                    self.socket.bind(self.addr)
                    self.socket.listen(5)
                except socket.error as e:
                    self._deal_socket_error(e)
                    time.sleep(5)
                    continue

            rs_l, ws_l, es_l = select.select([self.socket], [], [], 5)
            if len(rs_l):
                (proxy, addr) =self.socket.accept()
                self.proxys[proxy] = [addr, 'init']

            rs_l, ws_l, es_l = select.select(self.proxys.keys(), [], [], 5)
            for proxy in rs_l:
                try:
                    cmd = proxy.recv(1024)
                except socket.error as e:
                    print e
                    self.proxys.pop(proxy)
                    proxy.close()
                    continue

                if cmd[0:8] == 'complete':
                    self.proxys[proxy][1] = 'init'
                    print ''
                    print self.proxys[proxy][0], "is complete test"
                    print "statistic data"
                    cmd = cmd[8:]
                    cmd = cmd.split(',')
                    print "total->%s, success->%s, fail->%s, average response time->%s, query per sencond->%s" % tuple(cmd)

                elif cmd == '':
                    print ''
                    print self.proxys[proxy][0], "is exit"
                    self.proxys.pop(proxy)
                    proxy.close()

    def start_proxy_test(self, threadnum, file):
        proxy_num = len(self.proxys)
        base_num = int(threadnum) / proxy_num
        extra_num = int(threadnum) % proxy_num
        step = extra_num - 1 if extra_num !=0 else 0

        for proxy in self.proxys:
            num = base_num+ (extra_num - step)
            extra_num = step
            step = step - 1 if step !=0 else 0

            proxy.send('start '+str(num)+' '+file)
            if num != 0:
                self.proxys[proxy][1] = 'running'

    def stop_proxy_test(self):
        for proxy in self.proxys:
            if self.proxys[proxy][1] == 'running':
                proxy.send('stop')
                self.proxys[proxy][1] = 'init'

    def print_proxy_status(self):
        for proxy in self.proxys:
            print "%s is %s" % tuple(self.proxys[proxy])

    def check_proxy_stauts(self):
        if len(self.proxys) == 0:
            print "no proxy connected, can't run test"
            return False

        for proxy in self.proxys:
            if self.proxys[proxy][1] == 'running':
                print "%s is running test" % self.proxys[proxy][0][0]
                return False

        return True

    def stop(self):
        self.run_state = 'stop'

'''
*    交互线程，负责与用户进行交互
'''
class user_inter_thread(Thread):
    def __init__(self, ctrlthread):
        Thread.__init__(self)
        self.ctrlthread = ctrlthread
        self.need_exit = False

    def run(self):
        while not self.need_exit:
            cmd = raw_input("[cmd]->")
            if cmd == 'help':
                print '''Usage:
    status                             -> 查询所有连接上的proxy的状态
    start {threadnum} {file} {time}    -> 启动压力测试
                   threadnum                  : 所有proxy的总线程数
                   file                       : 压力部署的文件名，进行压力测试时，会根据文件内容进行替换
                   time                       : 测试总时长，如果为0，则为不限制时间

    stop                               -> 停止所有proxy正在进行的
    close                              -> 关闭所有的客户端
    quit(exit)                         -> 退出
                      '''
            elif re.match("start +\\d{0,4} +\\S+", cmd):
                cmd = cmd.split()
                if self.ctrlthread.check_proxy_stauts():
                    self.ctrlthread.start_proxy_test(cmd[1], cmd[2])

            elif cmd == 'status':
                self.ctrlthread.print_proxy_status()

            elif cmd == 'stop':
                self.ctrlthread.stop_proxy_test()

            elif cmd == 'quit':
                self.ctrlthread.stop()
                self.stop()
            elif cmd == 'close':
                continue
            elif cmd == '':
                continue
            else:
                print "error cmd"

    def stop(self):
        self.need_exit = True

def main():
    host = '127.0.0.1'
    port = 8888

    ctrlthread = ctrl_thread(host, port)
    interthread = user_inter_thread(ctrlthread)

    ctrlthread.start()
    interthread.start()

main()
