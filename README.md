# telegram bot
基于 PTB (python telegram bot) 开发的 Telegram 群组广告管理机器人，用于自动化处理群组垃圾信息。

[官方文档](https://docs.python-telegram-bot.org/en/stable/index.html) | [官方 WiKi](https://github.com/python-telegram-bot/python-telegram-bot/wiki/)
-|-

代理参考 https://github.com/python-telegram-bot/python-telegram-bot/wiki/Working-Behind-a-Proxy

Python >= 3.10（开发环境为 3.12）
```properties
# requirements.txt
python-telegram-bot
python-telegram-bot[http2]
python-telegram-bot[job-queue]
python-telegram-bot[rate-limiter]
httpx[socks]
PyYAML
pillow
```

## Main features
- 记录所有消息
- 检测加入群组用户的用户名, 简介等是否包含屏蔽词
- 检测群消息是否有屏蔽词
- 使用普通验证码和自定义入群验证问题验证
- ...

## Todo List
1. 标记一位 `user`, 在下次发消息前须完成验证
1. 在终端输入指令控制 `python telegram bot`
1. 新用户间隔一段时间(如1天)后, 再次检查用户列表
1. 禁言短时间发送相同消息的 `user`
1. 对 "发送 quote 消息的来源群组名称" 进行屏蔽词检测
1. 检测 `block_words.yaml` 修改后, 自动重新加载屏蔽词列表
1. 通过对比图片相似度, 实现 ban 发送广告图片的用户
1. 更先进的屏蔽词检测
1. 将屏蔽词检测封装到一个函数, 参数中包含(context, message, verified:是否查询用户页)
1. 自动读取管理员列表, 管理员变化时自动更新, 不再依赖配置文件

- 目前无法实现 (`Bot API` 没有该功能, 需要使用 `User API`)
1. 获取群组成员列表
1. 消息被删除的更新消息
1. 根据 `@username` 获取 `user_id`
1. 获取 bot 的创建者是谁

## Known bugs
1. 使用 `http` 代理时, 会不定时出现无响应, 需要手动关闭再重新启动. 使用 `socks` 代理不会出现问题. (不确定, 不易测试\复现, 未找到原因)
1. 在无网络时启动, 连接网络后不能完成启动, 需要终止后重新启动
