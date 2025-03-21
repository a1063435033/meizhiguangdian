import requests
import json

def upload_file_to_wechat(file_path, file_name_with_extension, key, type='file'):
    """
    上传文件到企业微信，并返回media_id。
    
    :param file_path: 文件在本地的路径
    :param file_name_with_extension: 文件名包括扩展名
    :param key: 机器人webhook的key
    :param type: 文件类型，默认为'file'
    :return: media_id 或者 None（如果上传失败）
    """
    upload_url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/upload_media?key={key}&type={type}"
    
    try:
        with open(file_path, 'rb') as f:
            files = {
                'media': (file_name_with_extension, f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            }
            
            response = requests.post(upload_url, files=files)
            
            if response.status_code == 200:
                result = response.json()
                if result['errcode'] == 0:
                    return result['media_id']
                else:
                    print(f"Error: {result.get('errmsg', '未知错误')}")
            else:
                print(f"HTTP 请求失败，状态码: {response.status_code}, 错误信息: {response.text}")
    except FileNotFoundError:
        print(f"找不到文件: {file_path}")
    except Exception as e:
        print(f"发生了一个错误: {e}")
    return None


def send_file_message_by_media_id(media_id, key):
    """
    使用media_id发送文件消息到群聊中。
    
    :param media_id: 从上传文件获得的media_id
    :param key: 机器人webhook的key
    """
    send_url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={key}"
    message_body = {
        "msgtype": "file",
        "file": {
            "media_id": media_id
        }
    }
    headers = {'Content-Type': 'application/json'}
    
    response = requests.post(send_url, headers=headers, data=json.dumps(message_body))
    if response.status_code == 200:
        result = response.json()
        if result['errcode'] == 0:
            print("文件发送成功")
        else:
            print(f"发送文件时出错: {result['errmsg']}")
    else:
        print(f"发送文件HTTP请求失败，状态码: {response.status_code}")

def send_markdown_message_type(content, key):
    """
    发送Markdown类型的消息到企业微信群聊中。
    
    :param content: Markdown格式的内容字符串
    :param key: 机器人webhook的key
    """
    send_url = f"https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={key}"
    message_body = {
        "msgtype": "markdown",
        "markdown": {
            "content": content
        }
    }
    headers = {'Content-Type': 'application/json'}
    
    response = requests.post(send_url, headers=headers, data=json.dumps(message_body))
    
    if response.status_code == 200:
        result = response.json()
        if result['errcode'] == 0:
            print("Markdown消息发送成功")
        else:
            print(f"发送Markdown消息时出错: {result['errmsg']}")
    else:
        print(f"发送Markdown消息HTTP请求失败，状态码: {response.status_code}")


def send_markdown_message(feedback_total, normal_feedback_count, vip_feedback_count, key):
    """
    发送Markdown格式的消息到指定的群组。

    :param webhook_url: 机器人的webhook地址
    :param feedback_total: 总共新增的用户反馈数量
    :param normal_feedback_count: 普通用户的反馈数量
    :param vip_feedback_count: VIP用户的反馈数量
    """
    webhook_url = f'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key={key}'
    markdown_content = f"控制器灯光测试报告<font color=\"warning\">文件</font>。\n" \
                       f">手动测试报告文件:<font color=\"comment\">{feedback_total}</font>\n" \
                       f">自动测试报告文件:<font color=\"comment\">{normal_feedback_count}例</font>\n" \
                       f">PPFD测试报告文件:<font color=\"comment\">{vip_feedback_count}例</font>"
    
    message = {
        "msgtype": "markdown",
        "markdown": {
            "content": markdown_content
        }
    }

    headers = {'Content-Type': 'application/json'}
    response = requests.post(webhook_url, headers=headers, data=json.dumps(message))
    
    if response.status_code == 200:
        print("消息发送成功")
    else:
        print(f"消息发送失败，状态码：{response.status_code}, 响应内容：{response.text}")

# # 示例调用
# if __name__ == '__main__':
#     webhook_url = 'https://qyapi.weixin.qq.com/cgi-bin/webhook/send?key=你的key'  # 替换成你自己的webhook URL
#     total = 132
#     normal = 117
#     vip = 15
    
# # 示例调用
# if __name__ == "__main__":
#     key = 'ab98304c-d5a4-4840-8d66-d6d564a43dcf'
#     file_path = r"D:\meizhiguangdian\autoTest\MH_autotest\output_with_charts.xlsx"
#     file_name_with_extension = "自动模式测试报告.xlsx"

#     # # 第一步：上传文件并获取media_id
#     # media_id = upload_file_to_wechat(file_path, file_name_with_extension, key)

#     # # 第二步：使用media_id发送文件消息
#     # if media_id:
#     #     send_file_message_by_media_id(media_id, key)
#     markdown_content = """
#     # 标题一
#     这是一个一级标题。

#     ## 标题二
#     这是一个二级标题。

#     ### 标题三
#     这是一个三级标题。

#     #### 标题四
#     这是一个四级标题。

#     ##### 标题五
#     这是一个五级标题。

#     ###### 标题六
#     这是一个六级标题。
#     """
    
#     # 调用方法发送Markdown消息
#     send_markdown_message(markdown_content, key)