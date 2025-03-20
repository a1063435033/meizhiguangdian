import json
import time
from serial_data_parser import SerialDataParser

def get_manual_light_adjust_mode_Cmd(pid, on, dim):
    """
    获取手动调节灯光模式指令。

    :param pid: MH控制器PID
    :param on: 开关状态 (0: 关, 1: 开)
    :param dim: 亮度值 (0-100)
    :return: JSON格式的命令字符串
    """
    command = {"method": "ctlLightSet","pid": pid,"params": {"mod": 0,"on": on,"dim": dim}}
    return json.dumps(command)

def get_auto_light_adjust_mode_Cmd(pid, st, et, dim, darkenT, offT, sunTime):
    """
    获取自动调节灯光模式命令。
    
    :param pid: MH控制器PID
    :param st: 开始时间
    :param et: 结束时间
    :param dim_min: 最小亮度
    :param dim_max: 最大亮度
    :param ppfd: PPFD值
    :param darkenT: 变暗时间
    :param offT: 关闭时间
    :param sunTime: 日照时间
    :return: JSON格式的命令字符串
    """
    command = {
        "method": "ctlLightSet",
        "pid": pid,
        "params": {
            "mod": 1,
            "st": st,
            "et": et,
            "dim": dim,
            "darkenT": darkenT,
            "offT": offT,
            "sunTime": sunTime
        }
    }
    return json.dumps(command)

def get_ppfd_light_adjust_mode_Cmd(pid, st, et, dim_min, dim_max, ppfd, darkenT, offT, sunTime):
    """
    获取PPFD灯光模式命令。
    
    :param pid: MH控制器PID
    :param st: 开始时间
    :param et: 结束时间
    :param dim_min: 最小亮度
    :param dim_max: 最大亮度
    :param ppfd: PPFD值
    :param darkenT: 变暗时间
    :param offT: 关闭时间
    :param sunTime: 日照时间
    :return: JSON格式的命令字符串
    """
    command = {
        "method": "ctlLightSet",
        "pid": pid,
        "params": {
            "mod": 2,
            "st": st,
            "et": et,
            "dim_min": dim_min,
            "dim_max": dim_max,
            "ppfd": ppfd,
            "darkenT": darkenT,
            "offT": offT,
            "sunTime": sunTime
        }
    }
    return json.dumps(command)
def get_iHub4Set_light_manual_mode_Cmd(pid, on, dim):
    """
    获取四孔排插灯组手动模式命令。
    :param pid: MH控制器PID
    :param on: 开关状态 (0: 关, 1: 开)
    :param dim: 亮度值 (0-100)
    :return: JSON格式的命令字符串
    """
    command = {"method": "iHub4Set","pid": pid,"params": {"light":{"mod": 0,"on": on,"dim": dim}}}
    return json.dumps(command)

def get_iHub4Set_light_auto_mode_Cmd(pid, st, et, dim, darkenT, offT, sunTime):
    """
    获取四孔排插灯组自动调节灯光模式命令。
    
    :param pid: MH控制器PID
    :param st: 开始时间
    :param et: 结束时间
    :param dim_min: 最小亮度
    :param dim_max: 最大亮度
    :param ppfd: PPFD值
    :param darkenT: 变暗时间
    :param offT: 关闭时间
    :param sunTime: 日照时间
    :return: JSON格式的命令字符串
    """
    command = {
        "method": "iHub4Set",
        "pid": pid,
        "params": {
            "light":{
                "mod": 1,
                "st": st,
                "et": et,
                "dim": dim,
                "darkenT": darkenT,
                "offT": offT,
                "sunTime": sunTime
            }
        }
    }
    return json.dumps(command)

def get_iHub4Set_light_ppfd_mode_Cmd(pid, st, et, dim_min, dim_max, ppfd, darkenT, offT, sunTime):
    """
    获取四孔排插灯组PPFD模式命令。
    
    :param pid: MH控制器PID
    :param st: 开始时间
    :param et: 结束时间
    :param dim_min: 最小亮度
    :param dim_max: 最大亮度
    :param ppfd: PPFD值
    :param darkenT: 变暗时间
    :param offT: 关闭时间
    :param sunTime: 日照时间
    :return: JSON格式的命令字符串
    """
    command = {
        "method": "iHub4Set",
        "pid": pid,
        "params": {
            "light":{
                "mod": 2,
                "st": st,
                "et": et,
                "dim_min": dim_min,
                "dim_max": dim_max,
                "ppfd": ppfd,
                "darkenT": darkenT,
                "offT": offT,
                "sunTime": sunTime
            }
        } 
    }
    return json.dumps(command)

def get_iHub4Set_switch_manual_mode_Cmd(ser, ihub, pid, on):
    command = json.dumps({"method": "iHub4Set","pid": pid,"params": {ihub:{"mod": 0,"on": on}}})
    ser.write(command.encode('utf-8'))
    time.sleep(0.5)
    buffer = SerialDataParser.read_serial_succeed_data(ser, 6)
    print(buffer)
    if buffer["code"] == 200:
        return True
    else:
        return False

def get_iHub4Set_switch_auto_mode_Cmd(ser, pid):
    command = json.dumps({"method": "iHub4Set","pid": pid,"params": {"UV":{"mod": 1}}})
    ser.write(command.encode('utf-8'))
    time.sleep(0.5)
    buffer = SerialDataParser.read_serial_succeed_data(ser, 6)
    if buffer["code"] == 200:
        return True
    else:
        return False

def get_iHub4Set_switch_autoMod_mode_Cmd(ser, pid, ihub, st, rd, ed, times):
    command = json.dumps({"method":"iHub4Set","pid":pid,"params":{ihub:{"mod":1,"autoMod":1,"st":st,"rd":rd,"ed":ed,"times":times}}})
    ser.write(command.encode('utf-8'))
    time.sleep(0.5)
    buffer = SerialDataParser.read_serial_succeed_data(ser, 6)
    if buffer["code"] == 200:
        return True
    else:
        return False

def get_iHub4Set_switch_moreAutoMod_mode_Cmd(ser, pid, st, et, on):
    """
    获取四孔排插孔位开关多段模式模式命令。
    
    :param pid: MH控制器PID
    :param st: 开始时间 [101,102,103,104,105,106,107,108,109,110,111,112]
    :param et: 结束时间 [101,102,103,104,105,106,107,108,109,110,111,112]
    :param on: 最小亮度 [0,0,0,0,0,0,0,0,0,0,0,0]
    """
    command = json.dumps({"method": "iHub4Set","pid": pid,"params": {"UV":{"autoMod":1, "timing":{ "st":st, "et": et, "on": on}}}})
    ser.write(command.encode('utf-8'))
    time.sleep(0.5)
    buffer = SerialDataParser.read_serial_succeed_data(ser, 6)
    if buffer["code"] == 200:
        return True
    else:
        return False