

key = 'ab98304c-d5a4-4840-8d66-d6d564a43dcf'
file_path = er.main()
file_name_with_extension = "自动模式测试报告.xlsx"

# 第一步：上传文件并获取media_id
media_id = sendWechat.upload_file_to_wechat(file_path, file_name_with_extension, key)
# 第二步：使用media_id发送文件消息
if media_id:
    sendWechat.send_file_message_by_media_id(media_id, key)