# 综合模块，整个代理池的调度模块

import time
from multiprocessing import Process
from api import app
from getter import Getter
from tester import Tester
from datetime import datetime
from settings import *

class Scheduler(object):
    def schedule_tester(self, cycle=TESTER_CYCLE):
        tester = Tester()
        while True:
            print("Tester is starting.... at", datetime.now().strftime("%y-%b-%d %H:%M:%S"))
            tester.run()
            time.sleep(cycle)


    def scheduler_getter(self, cycle=GETTER_CYCLE):
        getter = Getter()
        while True:
            print("Getter is starting.... at", datetime.now().strftime("%y-%b-%d %H:%M:%S"))
            getter.run()
            time.sleep(cycle)

    def scheduler_api(self):
        app.run(API_HOST, API_PORT)


    def run(self):
        print("The whole proxy pool is starting.... at", datetime.now().strftime("%y-%b-%d %H:%M:%S"))
        if TESTER_ENABLED:
            tester_process = Process(target=self.schedule_tester)
            tester_process.start()

        if GETTER_ENABLED:
            getter_process = Process(target=self.scheduler_getter)
            getter_process.start()

        if API_ENABLED:
            api_process = Process(target=self.scheduler_api)
            api_process.start()
