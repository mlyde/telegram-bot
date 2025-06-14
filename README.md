# telegram bot
基于 PTB (python telegram bot) 开发的 Telegram 群组广告管理机器人，用于自动化处理群组垃圾信息。

[官方文档](https://docs.python-telegram-bot.org/en/stable/index.html) | [官方 WiKi](https://github.com/python-telegram-bot/python-telegram-bot/wiki/)
-|-

代理参考 https://github.com/python-telegram-bot/python-telegram-bot/wiki/Working-Behind-a-Proxy

```properties
# requirements.txt
python-telegram-bot[http2]
python-telegram-bot[rate-limiter]
httpx[socks]
PyYAML
```

## Features

- 记录消息日志
- 检测加入群组用户的用户名, 简介等是否包含屏蔽词
- 检测群消息是否有屏蔽词
- ...

## Todo List
1. 标记一位 `user`, 在下次发消息前须完成验证
1. 在终端输入指令控制 `python telegram bot`
1. 设置定时器, 指定时间后, 执行函数
1. 新用户间隔一段时间(1天等)后, 检查用户列表
1. 禁言短时间发送相同消息的 `user`
1. 入群验证: 用户入群后, 以 user_id, group_id, 随机数, 创建一条数据, 创建一个 5 分钟定时, 定时结束后, 将用户移出群; 用户通过访问有随机数的 /start 开启验证, 判断用户访问的随机数是否与数据库中随机数匹配, 验证成功后, 删除定时, 解除封禁, 标记为已通过验证. `start=captcha_chatid`
1. 检测 block_words.yaml 修改后, 自动重新加载屏蔽词列表
1. bot 发送消息的日志

- 目前无法实现 (bot API 没有该功能)
1. 获取群成员列表
1. 根据 @username 获取 id
1. 检测消息被删除
1. 获取群组成员列表, 删除 `Delete Account`

## bugs
1. 使用 http 代理时, 会不定时出现无响应, 需要手动关闭再重新启动. 使用 socks 代理不会出现问题. (不确定, 不易测试\复现, 未找到原因)
