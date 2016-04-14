#coding: utf-8
'''
Created on 2016-03-12

@author: yangchuangliang
'''
from multiprocessing import Process, Queue
from Queue import Empty
import socket
import select
import time
import os, base64, binascii
import httplib, urllib
from python_oath import totp

'''
*    统计类，负责统计相关数据
'''
class class_static_data(object):
    def __init__(self):
        self.queue = Queue()

    def update_data(self, total, success, fail, runtime_sum, real_runtime):
        self.queue.put({'total':total, 'success':success, 'fail':fail, 'runtime_sum':runtime_sum, 'real_runtime':real_runtime})

    def get_static_data(self):
        total = 0
        success = 0
        fail = 0
        runtime_sum = 0.0
        real_runtime = 0.0

        for i in xrange(0, self.queue.qsize()):
            try:
                data = self.queue.get(False)
                total += data['total']
                success += data['success']
                fail += data['fail']
                runtime_sum += data['runtime_sum']

                if real_runtime < data['real_runtime']:
                    real_runtime = data['real_runtime']
            except Empty as e:
                continue

        if total != 0 and real_runtime != 0.0:
            avg_resp_time = runtime_sum / total
            qps = total / real_runtime
        else:
            avg_resp_time = 0
            qps = 0

        return (total, success, fail, avg_resp_time, qps)

'''
*    客户端代理控制类，负责各个进程的启动和关闭等管理操作
'''
class class_proxy_ctrl(object):
    def __init__(self, log_queue, p_2_s_q, static_data):
        self.log_queue = log_queue
        self.p2s = p_2_s_q
        self.static_data = static_data
        self.press_list = []

    def check_process_list(self):
        stop_num = 0
        for p in self.press_list:
            if not p.is_alive():
                stop_num += 1

        if len(self.press_list) == stop_num and stop_num !=0:
            self.press_list = []
            return True
        else:
            return False

    def start_press_process(self, threadnum, filename):
        press_threads_list=[]

        try:
            usr_list = file(filename, 'r')
        except IOError as e:
            print e
            return False

        line_num = 0
        for line in usr_list:
            line_num += 1
        usr_list = file(filename, 'r')
        base_num = line_num / int(threadnum)
        extra_num = line_num % int(threadnum)
        step = extra_num - 1 if extra_num !=0 else 0


        for i in xrange(threadnum):
            num = base_num+ (extra_num - step)
            extra_num = step
            step = step - 1 if step !=0 else 0
            press_list = []

            for j in xrange(num):
                line = usr_list.readline()
                press_list.append(line.strip())

            p = class_press_process(self.log_queue, self.p2s, self.static_data, press_list, True)
            press_threads_list.append(p)

        for p in press_threads_list:
            p.start()

        self.press_list = press_threads_list
        return True

    def stop_press_process(self):
        for p in self.press_list:
            self.p2s.put('FIN')

        for p in self.press_list:
            p.join()

        #self.check_process_list()

'''
*    log写入进程
'''
class class_logwrite_process(Process):
    def __init__(self, log_queue, p2s_queue):
        super(class_logwrite_process, self).__init__()
        self.log_queue = log_queue
        self.p2s = p2s_queue
        filename = 'perf_run.log'
        self.__file = file(filename, 'w')

    def run(self):
        starttime = time.time()
        while True:
            try:
                try:
                    tmp = self.p2s.get(False)
                    if tmp == "FIN":
                        break
                except Empty as e:
                    pass

                try:
                    endtime = time.time()

                    if endtime - starttime > 5:
                        self.__file.flush()

                    log_str = self.log_queue.get(False)
                    self.__file.write(log_str)
                    continue
                except Empty as e:
                    pass

                time.sleep(0.5)
            except KeyboardInterrupt as e:
                pass

        self.__file.flush()
        self.__file.close()
        print self.__class__.__name__, " is exit"

'''
*    发起压力操作进程，根据压力数量进行创建，并进行压力操作
'''
class class_press_process(Process):
    def __init__(self, log_queue, p2s_queue, static_data, press_list, isLoopPress):
        super(class_press_process, self).__init__()
        self.log_queue = log_queue
        self.p2s = p2s_queue
        self.static_data = static_data
        self.press_list = press_list
        self.isLoopPress = isLoopPress
        self.total = 0
        self.success = 0
        self.fail = 0
        self.runtime_sum=0.0

        #self.httpconn = httplib.HTTPConnection(url)
        self.httpconn = None

    def run(self):
        i = 0
        press_num = len(self.press_list)
        start_time = time.time()

        while self.isLoopPress:
            try:
                try:
                    tmp = self.p2s.get(False)
                    if tmp == 'FIN':
                        break
                except Empty as e:
                    pass

                if i == press_num:
                    i = 0

                press_param = self.press_list[i]
                i += 1

                press_param = press_param.split()
                result, runtime, descstr, token = self.run_once_press(press_param[0], press_param[1])
                self.log_queue.put('%s, %s, %s, %s, %s, %s, %s\n' %(time.strftime("%Y/%m/%d %H:%M:%S", time.localtime()), os.getpid(), press_param[0], result, runtime, repr(descstr), token))
                self.total += 1
                if int(result) == 200:
                    self.success += 1
                else:
                    self.fail += 1

                self.runtime_sum += runtime
            except KeyboardInterrupt as e:
                pass

        end_time = time.time()
        runtime = end_time - start_time

        self.static_data.update_data(self.total, self.success, self.fail, self.runtime_sum, runtime)

        self.httpconn.close()
        #self.s2p.put('COMPELET')

    def run_once_press(self, username, key):
        url = "cq01-ssl-auth01.cq01.baidu.com"
        #根据key产生passcode
        token = totp(binascii.b2a_hex(base64.b64decode(key)))

        #格式化参数
        param = urllib.urlencode({"passcode" : token})
        path = "%s/%s" % ("/otpd/api/rest/token", username)
        headers = {
                    "Content-type": "application/x-www-form-urlencoded",
                    "Connection": "close"
                  }
        #使用长连接模型
        if self.httpconn == None:
            self.httpconn = httplib.HTTPConnection(url, timeout=120)
        ret = None
        p = None
        #记录启动时间
        starttime = time.time()
        try:
            self.httpconn.request("POST", path, param, headers)
            resp = self.httpconn.getresponse(buffering=True)
        except Exception as e:
            print self.name, e
            print self.name, 'will reconnect'
            self.httpconn = httplib.HTTPConnection(url, timeout=120)
            ret = 600
            p = "HTTP ERROR %s %s" % (self.name, e)
            #sys.exit(1)
        #记录完成时间
        endtime = time.time()
        ret = resp.status if ret == None else ret
        p = resp.read(1024) if p == None else p

        runtime = endtime - starttime
        return (ret, runtime, p, token)

def _deal_socket_error(c_sock, sock_except):
    print sock_except, ' will sleep 5s'
    time.sleep(5)
    if c_sock[0]:
        c_sock[0].close()
        c_sock[0] = None

is_run = True

host = '127.0.0.1'
port = 8888
c_sock = [None]
buf_len =64
press_status = 'init'

log_queue = Queue()
parent_2_sub_queue = Queue()
parent_2_log_queue = Queue()


static_data = class_static_data()

proxy_ctrl = class_proxy_ctrl(log_queue,parent_2_sub_queue,static_data)
log_process = None

try:
    while is_run:
        if c_sock[0] == None:
            try:
                c_sock[0] = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                c_sock[0].connect((host, port))
                print "connect server sucess"
            except socket.error as e:
                _deal_socket_error(c_sock, e)
                continue

        if log_process == None:
            log_process = class_logwrite_process(log_queue, parent_2_log_queue)
            log_process.start()

        r_s, w_s, e_s = select.select([c_sock[0]], [], [], 0.5)
        if len(r_s):
            try:
                cmd = c_sock[0].recv(buf_len)
            except socket.error as e:
                _deal_socket_error(c_sock, e)
                continue

            print cmd
            if press_status == 'init':
                if cmd[0:5] == 'start':
                    cmd = cmd.split()
                    ret = proxy_ctrl.start_press_process(int(cmd[1]), cmd[2])
                    if not ret:
                        print "start press fail"
                    else:
                        press_status = 'running'

            elif press_status == 'running':
                if cmd == 'stop':
                    proxy_ctrl.stop_press_process()

            elif cmd == '':
                _deal_socket_error(c_sock, "server is close,will wait server restart")
            elif cmd == 'exit':
                print "Server ask the client to Exit"
                raise SystemExit

        if press_status == 'running'and proxy_ctrl.check_process_list():
            a,b,c,d,e=static_data.get_static_data()

            if c_sock[0]:
                c_sock[0].send("complete%s,%s,%s,%0.6f,%0.6f" % (a,b,c,d,e))
            press_status = 'init'


except (KeyboardInterrupt, SystemExit) as e:
    is_run = False

    if log_process and log_process.is_alive():
        parent_2_log_queue.put('FIN')

    if press_status == 'running':
            proxy_ctrl.stop_press_process()
    if log_process:
        log_process.join()
    if c_sock[0]:
        c_sock[0].close()

