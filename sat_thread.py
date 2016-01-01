#!/usr/bin/env python3  
# -*- coding:utf-8 -*-
# 

import threading
import time
import queue
import sys,os


debug=False
#debug=True

class SAT_Threads(object):
    def __init__(self, workNum=10, timeout = 1):
        self.n = 0
        self.workQueue = queue.Queue()   
        self.threads = []
        self.workNum = workNum
        self.timeout=timeout
        self.name = 'Manager Thread_' + str(self.workNum)
        if (debug): print("init threads ",self.name, ' workNum=', self.workNum, ' timeout= ', self.timeout)
        start = time.time()
        self.init_thread_pool() #预创建线程
        end = time.time()
        print('threads init ms ', end-start)
        
    def init_thread_pool(self):
        for i in range(0, self.workNum):
            self.threads.insert(0, SAT_ChildThread(self.workQueue, self.timeout))
        if(debug): print('workQueue size = ', self.workQueue.qsize(),'threads size', len(self.threads))
    
    #args is list? 不应该对args做任何假设
    def add_job(self ,func, args=''):
        self.n+=1 #为线程名称
        self.workQueue.put((func, args, self.n))
        if (debug): print(func,' name= ',  self.n)
    
    def checkTaskEmpty(self):
        if self.workQueue.empty():
            if (debug): print("task empty")
            return True
        return False

    def wait_allcomplete(self):
        if (debug): print("start wait child thread run")
        for t in self.threads:
            if t.isAlive() :
                t.join(self.timeout)
        if(debug): print("all child thread exit")
                
                
class SAT_ChildThread(threading.Thread):
      def __init__(self, workQueue, timeout=1): 
          threading.Thread.__init__(self)
          self.setDaemon(True)
          self.workQueue=workQueue
          self.timeout=timeout
          self.name = ''
          self.startRunTime = time.time()
          self.maxseconds = timeout #这个值是让所有线程做完事情之后，能够退出，而不是等待
          self.start()
      def run(self):
          while True:
            try:
                if not self.workQueue.empty():
                    do,args,name=self.workQueue.get(True)
                    if (self.name != ''):
                        self.name=name
                        if(debug): print(self.name)
                    do(args)
                    self.workQueue.task_done()
                else:
                    time.sleep(0.05)
                    continue
#        if SAT_Threads.getFlag():
#            cur = time.time()
#            if ((cur - self.startRunTime) > self.maxseconds): #这种判断不是非常精确
#                if (debug): print('timeout exit ','thread ', self.name, ' exit ', 'child thread', sys.exc_info()) 
#                break
#        else :
#            #if (debug): print('run continue, not start work yet ')
#                #time.sleep(0.1) # 让线程一直检测是否运行
#            continue 
            except queue.Empty:
                print("queue empty")
                break
          

#具体要做的任务
def do_job(args):
    time.sleep(0.1)#模拟处理时间
    print('do_job ', threading.current_thread())

def do_jobs(args):
    print('do_jobs: ', threading.current_thread())

        
def TestRun(workNum=4, timeout=1):
    #h=int(time.strftime("%H"))
    #m=int(time.strftime("%M"))
    #print(type(h), h)
    #while True and ((h>=9 and h<12) or (h >=16  and h <18 ) or (h==15 and m < 2)):
    
    t = SAT_Threads(workNum, timeout)
    t.add_job(do_job)
    t.add_job(do_jobs)
    t.wait_allcomplete()
    
def TestWhileRun():
    c = 0
    while True and c < 5:
        TestRun()
        #time.sleep(1)
        c += 1
        print('again get') 

def TestAddJobsRun():
    c = 0
    t = SAT_Threads(10, 0.5)
    task=0
    while True:
        h=int(time.strftime("%H"))
        m=int(time.strftime("%M"))
        if c < 3:
            if t.checkTaskEmpty():
                t.add_job(do_job)
                task += 1
        else:
            break
        c+=1
        #time.sleep(0.1) # 这种情况会导致饿死
    print(c, 'wait end', ' task num', task)
    t.wait_allcomplete()
        

def TestDeadWhile():
    task = 0
    t = SAT_Threads(100, 1)
    while True:
        while True:
            if True and t.checkTaskEmpty():
                #t.add_job(do_job)
                task += 1
            if (task > 5):
                #time.sleep(0.1)
                break
        print("again")
        if (task > 50):
            break
    print("task num=", task)
    t.wait_allcomplete()

if __name__ == '__main__':
    start = time.time()
    #TestRun(4, 1)
    #TestWhileRun()
    #TestAddJobsRun()
    TestDeadWhile()
    end = time.time()
    print("cost all time: %s" % (end-start))
    #print(type(None))



