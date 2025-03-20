import threading
import time
import os
from MH_light_control import LightControl
from power_strip_control import PowerStripControl
from datetime import datetime, timedelta
import serial

def lightControlTest(log_path):
    lightControl = LightControl(log_path)
    lightControl.run_light_control_test()

def powerStripControlTest(log_path):
    ser = serial.Serial('com3', 115200, timeout=1)
    powerStripControl = PowerStripControl(log_path)
    print('开始四孔排插手动开关测试')
    print('-----------------------------------------------')
    powerStripControl.iHub4Set_switch_manual_mode(ser, 'AC15188261E0')
    print('开始四孔排插自动循环开关测试')
    print('-----------------------------------------------')
    powerStripControl.iHub4Set_switch_autoMod_mode(ser, 'AC15188261E0')
    ser.close()



def main():
# 获取当前路径并设置日志文件夹路径
    current_path = os.getcwd()
    now_time = datetime.now().strftime("%Y%m%d_%H%M%S")  # 当前时间
    result_path = os.path.join(current_path, f"MH控制器测试日志{now_time}")
    if not os.path.exists(result_path):
        os.makedirs(result_path)
    log_path = result_path

    # 创建线程对象
    # thread1 = threading.Thread(target=lightControlTest, args=(log_path,))
    thread2 = threading.Thread(target=powerStripControlTest, args=(log_path,))

    # 启动线程
    # thread1.start()
    thread2.start()

    # 等待所有线程完成
    # thread1.join()
    thread2.join()

    print("Both methods have completed.")

if __name__ == "__main__":
    main()