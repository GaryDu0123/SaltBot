还没去问授权, 

[![Powered by Wechaty](https://img.shields.io/badge/Powered%20By-Wechaty-brightgreen.svg)](https://wechaty.js.org)

项目以及构建设计来源自[hoshino](https://github.com/Ice-Cirno/HoshinoBot)

基于Wechaty, 还未实现大部分功能, 仅供自我学习

### 首先安装依赖
```bash
pip3 install -r requirement.txt
```

### 启动程序
1. docker运行, 并登陆微信
```shell
bash wechaty.sh
```

2. 启动项目

    **linux**
    ```shell
    python3 run.py
    ```
    **windows**
    ```shell
    py run.py
    ```

## 进度
- [x] 服务分群管理
- [x] 分群管理记录恢复(可能有bug)
- [x] 插件管理
- [x] 消息触发
- [ ] 权限控制
- [x] 帮助列表扩展, 分模块的详细帮助