import time
from  device import *
from loguru import logger
from page import meta_app



#  开启bluetooth的方法
def open_bluetooth(device_sn):
    cmd = "adb -s %s shell su -c 'svc bluetooth enable'" %device_sn
    if device_sn=="10AD4J22FX001HD":
        cmd = "adb -s %s shell svc bluetooth enable" %device_sn
    run_cmd(cmd)
    # print('执行一次打开bluetooth')

    bluetooth_result=get_bluetooth_Statu(device_sn)
    
    if bluetooth_result=='1':
        return True
    else:
        return False
def get_system_version():
    cmd = "adb shell getprop ro.build.version.release" 
    sysVersion = run_cmd(cmd)
    return sysVersion

    
# 关闭bluetooth的方法
def close_bluetooth(device_sn):
    cmd = "adb -s %s shell su -c 'svc bluetooth disable'" %device_sn
    if device_sn=="10AD4J22FX001HD":
        cmd = "adb -s %s shell svc bluetooth disable" %device_sn
    # print(cmd)
    run_cmd(cmd)
    # print('执行一次关闭bluetooth')
    # time.sleep(5)
    bluetooth_result=get_bluetooth_Statu(device_sn)
    # print(bluetooth_result)
    if bluetooth_result=='0':
        return True
    else:
        return False
    

#获取bluetooth当前开关状态
def get_bluetooth_Statu(device_sn):
    cmd='adb -s %s shell settings get global bluetooth_on' %device_sn
    bluetooth_result = run_cmd(cmd)
    return bluetooth_result

def bluetooth_test(device_sn, test_times, tester_name):
    fail_count=0
    suc_count=0
    if get_bluetooth_Statu(device_sn)!='0':
        close_bluetooth(device_sn)
    for i in range(test_times):
        
        open_bluetooth_result = open_bluetooth(device_sn)
        close_bluetooth_result = close_bluetooth(device_sn)
        if open_bluetooth_result and close_bluetooth_result:
            suc_count+=1
            logger.info('设备ID：%s  第%s次执行bluetooth测试|执行结果:成功' % (device_sn,i+1))
        else:
            fail_count+=1
            logger.info('设备ID：%s  第%s次执行bluetooth测试|执行结果:失败' % (device_sn,i+1))
    logger.info(device_sn,suc_count,fail_count)
    result_list=[[device_sn,"bluetooth_test",suc_count,fail_count,test_times,tester_name]]
    return device_sn, suc_count, fail_count


def get_device_info(mac_address, output):
    '''
    获取手机设备名称
    adb shell dumpsys bluetooth_manager
    '''
    bluetooth_name, deviceName = None, None
    if output is None:
        print("命令执行结果为空或出错")
        return None
    for line in output.splitlines(): 
        if '(Connected)' in line:
            start_index = line.find('[ DUAL ]') + len('[ DUAL ]')
            end_index = line.find('(', start_index)
            bluetooth_name = line[start_index:end_index].strip()
            break
        elif f'{mac_address} [ DUAL ]' in line:
            start_index = line.find('[ DUAL ]') + len('[ DUAL ]')
            end_index = line.find('(', start_index)
            bluetooth_name = line[start_index:end_index].strip()
            break
    for line in output.splitlines(): 
        if 'name' in line:
            deviceName = line
            break
    return bluetooth_name, deviceName
  

def get_bluetooth_status(mac_address, output):
    '''
    adb shell dumpsys bluetooth_manager
    '''
    if output is None:
        print("命令执行结果为空或出错")
        return None   
    current_state = None
    in_bonded_devices_section = False
    for line in output.splitlines():
        if "ConnectionState: STATE_CONNECTED" in line:
            current_state = "Connected"
            break
        elif "ConnectionState: STATE_DISCONNECTED" in line:
            current_state = "Disconnected"
            break
        elif "Bonded devices:" in line:
            in_bonded_devices_section = True
            continue
        elif not in_bonded_devices_section:
            continue
        elif mac_address in line:
            if "STATE_CONNECTED" in line or "Connected" in line:
                current_state = "Connected"
                break
            elif "STATE_DISCONNECTED" in line or "Disconnected" in line:
                current_state = "Disconnected"
                break

    return current_state


def reon_and_off_bluetooth(appPackage, deviceSn, screenshot_path, mac_address, output):
    app = meta_app.AppautoTest()
    d = app.driver
    close_bluetooth(deviceSn)
    element_exists = d.xpath(r'//*[@resource-id="com.metabounds.glass:id/recycler_view"]/android.view.ViewGroup[1]/android.widget.TextView[2]').wait(timeout=10)
    if element_exists:
        app.fileOperations.write_log( "蓝牙以断开" +str(deviceSn))
        time.sleep(5)
    open_bluetooth(deviceSn)
    num = 0
    bluetooth_status = get_bluetooth_status(mac_address, output)
    while True:
        if bluetooth_status == "Connected":
            app.fileOperations.write_log( "蓝牙以连接" +str(deviceSn))
            time.sleep(10)
            return True
        elif num == 30:
            app.fileOperations.write_log("设备超过30s未连接上设备" +str(deviceSn))
            return False
        time.sleep(1)
        num +=1
        



# print(get_bluetooth_Statu('9284275a'))
# a = close_bluetooth('9284275a')
# if a == 1:
#     time.sleep(1)
#     b = open_bluetooth('9284275a')
#     time.sleep(5)
#     print(get_bluetooth_Statu('9284275a'))
#     if b == 0:
#         pass
#     else:
#         print(222222222)
# adb_cmd = 'adb shell dumpsys bluetooth_manager'
# output = run_cmdlist(adb_cmd)
# mac_address = "F4:1A:79:50:03:7F"

# deviceSn = get_devices_sn()[0]
# cmd = 'adb shell dumpsys window | findstr mCurrentFocus'
# appPackage = 'com.metabounds.glass'
# screenshot_path = r'D:\log'
# # # reon_and_off_bluetooth(appPackage, deviceSn, screenshot_path, mac_address, output)
# # print(get_device_info(mac_address, output))
# reon_and_off_bluetooth(appPackage, deviceSn, screenshot_path, mac_address, output)
# close_bluetooth('10AD4J22FX001HD')


