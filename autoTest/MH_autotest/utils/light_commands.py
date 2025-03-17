import json

def get_manual_light_adjust_mode_command(pid, on, dim):
    """
    获取手动调节灯光模式指令。

    :param pid: MH控制器PID
    :param on: 开关状态 (0: 关, 1: 开)
    :param dim: 亮度值 (0-100)
    :return: JSON格式的命令字符串
    """
    command = {"method": "ctlLightSet","pid": pid,"params": {"mod": 0,"on": on,"dim": dim}}
    return json.dumps(command)

def get_auto_light_adjust_mode_command(pid, st, et, dim, darkenT, offT, sunTime):
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

def get_ppfd_light_adjust_mode_command(pid, st, et, dim_min, dim_max, ppfd, darkenT, offT, sunTime):
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
def get_sync_time_command(timestamp):
    """
    获取时间同步命令。
    
    :param timestamp: 时间戳
    :return: JSON格式的命令字符串
    """
    command = {
        "method": "syncTime",
        "pid": "AC15188261E0",
        "params": {
            "timestamp": timestamp
        }
    }
    return json.dumps(command)

# 其他命令可以根据需要继续添加...