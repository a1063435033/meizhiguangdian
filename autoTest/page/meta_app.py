#coding:utf-8
import uiautomator2 as u2
import time,datetime
import os
from page.fileOperations import FileOperations
from contextlib import contextmanager




class AppautoTest:

    def __init__(self, drive, log_path):
        print(f"Connecting to device: {drive}")
        self.driver = u2.connect(drive)
        self.appPackage = 'com.marspro.meizhi'
        self.fileOperations = FileOperations(log_path)
        self.pages = {
            "home": {"id": "com.thinkar.aiglasses:id/tv_glass_name", "id2": "com.thinkar.aiglasses:id/tv_contacts"},
            "contacts": {"id": "com.thinkar.aiglasses:id/tv_contacts"},
            "chatGpt": {"id": "com.thinkar.aiglasses:id/tv_chatgpt"},
            "teleprompter": {"id": "com.thinkar.aiglasses:id/btn_start_sync", "id2": "Teleprompter"},
            # Add more page configurations if needed
        }

    # 连接手机，打开app
    def start_app(self):
        self.fileOperations.write_log(f"Starting app: {self.appPackage}")
        self.driver.app_start(self.appPackage)
        time.sleep(10)  # Adjust the sleep time as per your requirements

    def stop_app(self):
        self.fileOperations.write_log(f"Stopping app: {self.appPackage}")
        self.driver.app_stop(self.appPackage)



    # 获得机器屏幕大小x,y
    def getSize(self):
        x = self.driver.window_size()[0]
        y = self.driver.window_size()[1]
        return x, y
    
    # 屏幕向上滑动
    def swipeUp(self, t=0.1):
        l = self.getSize()
        x1 = int(l[0] * 0.5)  # x坐标
        y1 = int(l[1] * 0.75)  # 起始y坐标
        y2 = int(l[1] * 0.25)  # 终点y坐标
        self.driver.swipe(x1, y1, x1, y2, t)

    # 截屏
    def screenshot(self, screenshot_path, times=""):
        screenshot_name = screenshot_path + str(times) + "--" + datetime.datetime.now().strftime(
            "%Y%m%d_%H%M%S") + ".png"
        self.driver.screenshot(screenshot_name)

    def click_button(self, pageText, buttonText, wait_time):
        if self.driver(text = pageText).exists(timeout = wait_time):
            time.sleep(1)
            self.driver(text = buttonText).click()

    def log_test_result(self, num, message, success):
        timestamp = time.strftime("%Y-%m-%d %X", time.localtime())
        result = "PASS" if success else "FAIL"
        log_message = f"[{timestamp}] 第{num}次 {message} {result}"
        self.fileOperations.write_log(log_message)
   
    # 打开提词器   
    def open_teleprompter_app(self):
        self.start_app()
        teleprompter = self.click_text_element_with_retry(self.driver, 'text', '提词器', max_attempts=3, retry_delay=1)
        is_teleprompter = 'com.metabounds.glass:id/btn_start_sync'
        if teleprompter:
            if self.driver(resourceId = is_teleprompter).wait(timeout = 3):
                self.fileOperations.write_log('进入提词器首页成功')
                return True
            else:
                self.fileOperations.write_log('进入提词器首页失败')
                return True
        else:
            self.fileOperations.write_log('首页点击提词器按钮失败')
            
    # 打开日程
    def open_schedule_app(self):
        self.start_app()
        if self.click_text_element_with_retry(self.driver, 'resourceid', f"{self.appPackage}:id/cl_programme", max_attempts=3, retry_delay=1):
            self.log_test_result(1, "进入日程界面", True)
        else:
            self.log_test_result(1, "进入日程界面", False)


    def click_text_element_with_retry(self, driver, element, resourceid, max_attempts = 3, retry_delay = 1):
        while True:
            try:
                if element == 'text':
                    if driver(text = resourceid).exists(timeout = 1):
                        driver(text = resourceid).click()
                        return True
                else:
                    if driver(resourceId = resourceid).exists(timeout = 1):
                        driver(resourceId = resourceid).click()
                        return True
                retry_delay += 1
                time.sleep(1)
                if retry_delay > max_attempts:
                    self.fileOperations.write_log(f'点击元素报错，尝试重新点击第{retry_delay}次')
            except:
                self.fileOperations.write_log(f'点击元素报错，尝试重新点击第{retry_delay}次')
                retry_delay += 1
                time.sleep(1)
                if retry_delay > max_attempts:
                    break







        



        
    




    # def bind_device(self):
    #     self.connect_phone(self.appname)
    #     if self.driver(text="立即添加").exists(timeout=10):
    #         self.file_operate.write_log(f'成功打开{self.appname}APP')


                
    















                
    # def finish_guide_page(self, modelType):

    #     self.click_button("设置设备名称及使用位置","完成",5)
    #     self.click_button("请将设备放置在最终安装的位置，检查Wi-Fi信号的强度","下一步",10)
    #     if modelType == '摄像机':
    #         pageNum = 5
    #         self.click_button("请选择设备的使用方式", "跳过", 10)
    #     elif modelType == '门铃':
    #         pageNum = 6
        
    #     for page in range(1, pageNum + 1):
    #         if page == pageNum and modelType == '摄像机':
    #             self.click_button(f"{page}/{pageNum}", "完成", 10)
    #         elif page == pageNum and modelType == '门铃':
    #             # self.click_button(f"{page}/{pageNum}", "下一步", 10)
    #             self.click_button(f"{page}/{pageNum}", "完成", 10)
    #             self.click_button("是否打开拆除报警功能？", "关闭", 5)
    #             self.click_button("是否打开拆除报警功能？", "确定", 10)
    #         else:
    #             self.click_button(f"{page}/{pageNum}", "下一步", 10)

    # def add_and_bind_device(self, deviceSn, wifiPassword):
    #     self.driver(text="立即添加").click()
    #     self.file_operate.write_log("点击立即添加")

    #     # 添加设备
    #     if self.driver(text="开启设备").exists(timeout=10):
    #         self.file_operate.write_log("勾选听到了提示音或看到指示灯亮起")
    #         self.driver(text="听到了提示音或看到指示灯亮起").click()
    #         time.sleep(1)
    #         self.file_operate.write_log("点击下一步")
    #         self.driver(text="下一步").click()
    #         start_select_bluetooth_time = datetime.datetime.now()
    #         # 选择要连接的设备
    #         if self.driver(text="请选择要连接的设备").exists(timeout=10):
    #             if self.driver(text="S/N:"+deviceSn).exists(timeout=30):
    #                 end_select_bluetooth_time = datetime.datetime.now()
    #                 self.file_operate.write_log("点击SN进入配网")
    #                 select_bluetooth_time = (end_select_bluetooth_time - start_select_bluetooth_time).total_seconds()
    #                 self.driver(text="S/N:"+deviceSn).click()

    #         elif self.driver(text="发现其他新设备").exists(timeout=20):
    #             time.sleep(0.5)
    #             self.driver(text="发现其他新设备").click()
    #             if self.driver(text="S/N:"+deviceSn).exists(timeout=30):
    #                 end_select_bluetooth_time = datetime.datetime.now()
    #                 select_bluetooth_time = (end_select_bluetooth_time - start_select_bluetooth_time).total_seconds()
    #                 self.file_operate.write_log("点击SN进入配网")
    #                 self.driver(text="S/N:"+deviceSn).click()
    #         # 输入密码
    #         if self.driver(text="请选择2.4GHz Wi-Fi并输入密码，目前暂不支持5GHz Wi-Fi和企业级认证Wi-Fi。了解更多 >>").exists(timeout=10):
    #             self.file_operate.write_log("输入密码")
    #             time.sleep(1)
    #             while True:
    #                 if self.driver(text="Wi-Fi搜索中").exists(timeout=2):
    #                     self.file_operate.write_log("Wi-Fi搜索中......")
    #                     time.sleep(0.5)
    #                 else:
    #                     self.driver(text="下一步").click()
    #                     break
    #             if self.driver(text="提示").exists(timeout=10):
    #                 time.sleep(1)
    #                 self.driver(text="确认").click()
    #                 current_time = datetime.datetime.now()
    #                 start_bind_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                
    #             if self.driver(text="设置设备名称及使用位置").exists(timeout = 90):
    #                 test_pass_time = datetime.datetime.now()
    #                 end_bind_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #                 self.file_operate.write_log("绑定成功")
    #                 test_pass_elapsed_time = (test_pass_time - current_time).total_seconds()
    #                 return test_pass_elapsed_time, start_bind_time, end_bind_time, start_select_bluetooth_time,end_select_bluetooth_time, select_bluetooth_time

    #             elif self.driver(text='听到“密码错误”提示音').exists(timeout = 90):
    #                 test_fail_time = datetime.datetime.now()
    #                 end_bind_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #                 self.file_operate.write_log("绑定失败，听到“密码错误”提示音")
    #                 test_fail_elapsed_time = (test_fail_time - current_time).total_seconds()
    #                 return test_fail_elapsed_time, start_bind_time, end_bind_time, start_select_bluetooth_time,end_select_bluetooth_time, select_bluetooth_time

    #             elif self.driver(text='听到“云服务连接失败”提示音').exists(timeout = 90):
    #                 test_fail_time = datetime.datetime.now()
    #                 end_bind_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #                 self.file_operate.write_log("绑定失败，听到“云服务连接失败”提示音")
    #                 test_fail_elapsed_time = (test_fail_time - current_time).total_seconds()
    #                 return test_fail_elapsed_time, start_bind_time, end_bind_time, start_select_bluetooth_time,end_select_bluetooth_time, select_bluetooth_time
                    
    #             elif self.driver(text='听到“认证方式错误”提示音').exists(timeout = 90):
    #                 test_fail_time = datetime.datetime.now()
    #                 end_bind_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    #                 self.file_operate.write_log("绑定失败，听到“认证方式错误”提示音")
    #                 test_fail_elapsed_time = (test_fail_time - current_time).total_seconds()
    #                 return test_fail_elapsed_time, start_bind_time, end_bind_time, start_select_bluetooth_time,end_select_bluetooth_time, select_bluetooth_time

                
                
                
        

  
