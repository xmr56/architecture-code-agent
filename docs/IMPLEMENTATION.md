# 架构到代码智能体：实现与验收说明

## 任务与方案

系统接收架构文档和PlantUML架构视图，调用DeepSeek V4 Pro官方API，通过受控文件工具逐步生成软件项目。桌面界面使用Tkinter，Windows单文件程序使用PyInstaller打包，模型权重不在本地部署。

本项目独立编写实现。参考资料主要用于理解Agent循环、工具调用和调用限制，没有复制Claude Code或参考教学项目的核心源码。

## 数据流

用户选择文件与输出目录 → 文档按标题和代码块预处理 → 保存含原文的input.json → 模型提出工具调用 → 宿主程序执行 → 工具结果作为消息返回 → 检查与修复 → 保存项目、日志和报告。

结构化预处理是确定性的格式解析，不把模型推断伪装成原始需求。模型补充的设计假设应另行写入ASSUMPTIONS.md。

## 模块

| 文件 | 职责 |
|---|---|
| app.py | 文件选择、密钥输入、后台线程、日志、停止与进度 |
| core.py | 官方API客户端、工具描述、目录工具、Agent循环和验收状态 |
| runner.py | 实际Python/Node测试执行、超时控制与错误回传 |
| selfcheck.py | 固定模拟模型的离线集成检查，明确不是模型生成成果 |
| tests/ | 输入边界、工具限制、反馈修复及测试执行器验证 |
| examples/ | 老师提供的原始输入，未改写 |
| runtime/ | Node测试运行时与开源许可 |

## 七个工具

write_file创建或替换项目文件；read_file读取项目文件；list_files列目录；validate_project进行交付完整性、Python语法及JSON解析检查；install_dependencies用内置npm安装Node依赖并禁用安装脚本；run_tests执行项目测试；finish申请结束。依赖目录禁止Agent读写，避免误改第三方源码。

启用测试执行后，finish要求最新文件版本已通过run_tests。测试通过后再修改文件会使原来的测试结果失效，必须复测。未启用执行时，报告保留NOT_RUN，不冒充运行成功。

## 官方API

固定地址：https://api.deepseek.com/chat/completions 。固定模型：deepseek-v4-pro。采用非思考模式和官方兼容的function tools消息结构。用户密钥仅用于Authorization，不写入任务消息或配置。每轮保存Token用量，设置调用次数和上下文大小上限。

## 测试执行

Python项目采用unittest；Node项目采用内置node:test。exe内含Python和Node测试所需运行时。测试进程使用本次生成项目为工作目录，标准输出和退出码被收集并交回模型。每组测试默认60秒，停止或超时会终止进程树。子进程环境过滤名称包含KEY、TOKEN、SECRET、PASSWORD的变量。

安装依赖和运行测试需要用户在界面明确勾选。生成代码以当前用户权限执行，当前实现不是操作系统级隔离环境。Node依赖可自动安装；数据库等服务和Python第三方依赖仍需配置。业务测试的覆盖质量仍需人工检查。

## 文件与资源控制

读写目录限定于每次独立run目录中的project。拒绝绝对路径、目录越界、Windows设备名、备用数据流等路径。单个文本文件不超过200KB，每次最多150个文件。预处理输入合计不超过15万字符。日志不保存请求密钥。

## 输出与可复核性

input.json保留输入；events.jsonl记录调用与工具执行；report.json记录状态、Token用量、静态检查与真实测试结果；project保存模型生成文件。每次创建新目录，不覆盖历史任务。

完成状态为artifacts_ready，含义是程序规定的检查已通过；其证明范围以report.json为准。该状态不代表所有需求均已正确实现，也不替代人工业务验收。

## 已执行验证与待验收

最终闭环验收记录位于generated_runs/run-20261105-144453-66b6a3：14轮真实DeepSeek调用；install_dependencies退出码0；run_tests实际运行21项测试、21项通过；finish成功；report.json为artifacts_ready/PASSED。累计API返回Token为223883，含缓存Token，不等同于按非缓存单价计算的用量。以下较早案例记录作为开发历史保留。

本地13项测试通过，包括真实Python和Node测试的成功与失败识别、固定模拟响应的错误修复链、取消及目录约束。已构建独立exe。

真实DeepSeek案例生成已有events.jsonl证据。生成的Express项目通过独立执行的15项测试；independent_acceptance.json保留输出、退出码和静态检查。原运行因依赖目录误检中止，独立验收不是原Agent的自主完成记录。最终版修正了依赖目录过滤并加入安装工具，未编造完整自主运行结论。

## 与参考项目的关系

- https://github.com/ultraworkers/claw-code ：参考其工程结构；没有整体引入。
- https://github.com/Windy3f3f3f3f/how-claude-code-works ：独立架构分析资料，不当作官方实现保证。
- https://github.com/Windy3f3f3f3f/claude-code-from-scratch ：阅读Python循环实现，对照模型、工具、反馈的主流程。
- https://github.com/anthropics/claude-code ：官方产品与操作资料。
- https://api-docs.deepseek.com/guides/tool_calls/ ：官方工具调用协议。

## 局限与后续改进

未实现多Agent、语义记忆、MCP、断点续跑或自动上下文压缩。未提供任意终端命令工具。错误修复取决于模型能力和测试质量；自动化不能消除架构输入的不完整。可继续完善依赖管理、项目启动验收、需求追溯和测试覆盖统计。
