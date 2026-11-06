# Architecture Code Agent

一个根据架构文档和PlantUML视图生成项目代码的简易Coding Agent。使用 **DeepSeek V4 Pro官方API**，无需下载模型权重。提供Windows桌面界面、文件工具、依赖安装、测试和反馈修复。

本项目为毕业设计前期作业。实现借助AI辅助完成；作者应理解实现并核对实验结果。包含的生成案例是**分数学习游戏的后端API**，目前没有浏览器答题页面。

## 1. 目录

```text
app.py                  桌面界面与后台任务
core.py                 官方API调用、Agent循环和文件工具
runner.py               npm依赖安装、Python/Node测试执行
selfcheck.py            固定模拟响应的离线检查
bootstrap_runtime.py    下载并校验官方Node运行时
examples/               作业提供的两份原始架构输入
tests/                  Agent自身的测试
sample-output/project/  真实DeepSeek生成的Game项目
sample-output/report.json  该次运行的结果与测试输出
sample-output/events.jsonl  模型轮次、Token与工具记录
docs/                   设计、实验与验收说明
```

密钥、exe、Node/npm二进制、node_modules和新运行缓存不提交到Git。公开的样例只保留源码和必要证据。

## 2. 运行Coding Agent

### 方式A：Windows exe

若仓库Releases中提供CodeAgent.exe，下载后双击。exe包含Python/Tk、Node和npm；目标电脑不必预装Python或Node。仍需联网及有效的DeepSeek官方API Key。

没有Release附件时请采用下方源码方式，或按第7节自行打包。不能把仓库公开等同于已有exe下载。

### 方式B：源码

Windows x64，安装Python 3.11或以上（包含Tkinter），在仓库根目录运行：

```powershell
python bootstrap_runtime.py
python app.py
```

也可双击`Start-Agent.cmd`。第一次会从nodejs.org下载固定版本Node 24.22.1，按脚本内置SHA256校验并准备npm，不会下载任何模型。运行Agent本身只使用Python标准库。下载需要网络。

## 3. 用Agent真实生成Game

1. 打开程序，在API Key栏填入自己的DeepSeek官方密钥。密钥不写入文件，不提交到GitHub。
2. 架构文档选择`examples/Architecture_Documentation.md`。
3. 架构视图选择`examples/Architecture_View.md`。
4. 选择输出目录，默认是程序旁边的`generated_runs/`。
5. 点击“预览结构化输入”，核对原文、章节和13个PlantUML代码块。
6. 勾选“允许安装项目依赖、运行生成测试并反馈修复”。这会运行生成代码，使用当前用户权限；每组测试限时60秒，依赖安装限时180秒，不是隔离环境。
7. 保留默认50轮上限，将下面的要求粘贴到“任务补充”，然后点击开始。
8. 等待结束，查看每次run目录中的`report.json`，然后检查`project/`下的源码、README、依赖和测试。

API请求地址为`https://api.deepseek.com/chat/completions`，模型固定为`deepseek-v4-pro`。请求是非流式，单次网络超时120秒；停止请求会在当前API请求结束后生效。每次真实生成都会产生账户费用，轮数上限不是人民币预算。

### 在“任务补充”中要求生成 Web 界面

复制下面的内容到程序的“任务补充”文本框。

```text
请依据两份架构文档生成 Space Fractions 游戏。Web 操作界面是必交项。使用 Node.js + Express 启动后端并提供网页，保留 package.json 的 start 命令。服务支持通过 PORT 环境变量指定端口。

打开根地址 / 时，应看到可直接操作的游戏首页。使用原生 HTML、CSS 和 JavaScript 即可。页面支持开始游戏、查看当前题目、选择并提交答案、查看答题反馈、进入下一题、查看最终成绩和重新开始。网页应调用真实的游戏接口，并在请求失败时显示错误提示。

请把前端文件、后端源码、依赖声明、测试和 README 一起交付。运行测试，检查根地址返回 HTML、前端资源可以加载、游戏接口能够完成答题到结算的流程。README 写清依赖安装、启动命令和浏览器地址。请保留实际测试结果。
```

生成完成后，进入本次输出的 `project/`，按其 README 安装依赖并启动。若项目的 `start` 命令和端口设置符合上面的要求，可在该目录使用以下 PowerShell 命令。源码方式需要 Node 和 npm 在 PATH 中，或使用本仓库准备的 `runtime`。

```powershell
npm install --ignore-scripts --no-audit --no-fund
$env:PORT = '3001'
npm start
```

打开 [http://localhost:3001/](http://localhost:3001/)，依次操作开始游戏、提交答案、查看反馈、答完题目、查看分数和重新开始。生成报告和接口测试用于检查程序运行情况，网页交互以浏览器实际操作为准。已提交的 `sample-output/project/` 是此前的 API 案例。按本节重新生成可得到带网页的版本。

### 如何确认成功

```json
{
  "status": "artifacts_ready",
  "runtime_tests": "PASSED"
}
```

同时检查`test_execution.results`中的退出码和实际输出。`NOT_RUN`表示没有执行测试；`error`、`cancelled`、`limit_reached`不表示完成。`validation.runtime_tests`仅说明静态检查器不执行测试，以顶层`runtime_tests`和`test_execution`为实际运行结果。

新生成结果不保证与样例逐字相同，也不保证每次都通过。失败时保留原始日志，并说明错误。测试通过不等于所有架构约束已落实。

## 4. 运行仓库附带的真实Game项目

它是已生成的后端API，运行它**不调用DeepSeek、不需要API Key**。先运行一次`python bootstrap_runtime.py`准备运行时，然后双击`Start-Sample-Game.cmd`。

或在**仓库根目录**的PowerShell依次执行：

```powershell
Set-Location sample-output/project
& "../../runtime/node.exe" "../../runtime/npm/bin/npm-cli.js" ci --ignore-scripts --no-audit --no-fund
& "../../runtime/node.exe" --test
& "../../runtime/node.exe" server.js
```

必须先安装依赖，否则会出现`Cannot find module 'express'`。`npm ci`按package-lock.json安装；Windows上这里用附带的node与npm，不要求npm在PATH中。

看到`Space Fractions API listening on port 3000`后打开：

- http://localhost:3000/health ：服务状态。
- http://localhost:3000/play ：开始一次游戏，返回gameId和首题。
- http://localhost:3000/help ：帮助文本。

返回JSON是预期行为。使用终端或HTTP客户端继续答题。另开一个PowerShell：

```powershell
$game = Invoke-RestMethod 'http://localhost:3000/play'
Invoke-RestMethod -Method Post -Uri "http://localhost:3000/games/$($game.gameId)/answer" -ContentType 'application/json' -Body '{"answer":"3/4"}'
Invoke-RestMethod "http://localhost:3000/games/$($game.gameId)/question"
```

查看当前题目后继续提交答案，结束后用`GET /games/{gameId}/score`查看分数。接口详见`sample-output/project/openapi.yaml`。在服务窗口按Ctrl+C停止；端口被占用时先关闭之前启动的服务。

## 5. 运行Agent自身测试

在**仓库根目录**执行：

```powershell
python -m unittest discover -s tests -v
python app.py --self-test
```

先准备runtime，Node执行器测试需要它。自检使用固定模拟响应，验证“错误代码→检查反馈→修复”，不是模型生成结果，不产生API费用。

## 6. 实现机制与实验结果

模型返回工具请求，由Python宿主执行，再把结果作为tool消息交回模型。工具包括文件读写、列目录、静态检查、安装Node依赖、实际测试和结束。启用执行后，最新文件必须测试通过才能正常结束。

文件工具拒绝目录越界、Windows保留设备名和依赖目录。npm安装禁用安装脚本。运行测试仍会执行生成代码，以当前用户身份运行；没有任意终端工具或操作系统级隔离。Python第三方依赖暂不自动安装。

本地验收：Agent自身13项测试通过；附带案例真实官方API调用14轮，自动安装依赖，Game项目21项测试通过并正常结束。模型随机性、网络和API变化会影响复现。Token为API报告的累计223883（含缓存命中），不是费用金额。

附带案例采用内存存储，数据库、OAuth2以及Redis/RabbitMQ等架构组件尚未完整接入。API和业务逻辑测试通过不表示生产系统完成。`sample-output/project/ASSUMPTIONS.md`记录差异。

## 7. 打包Windows exe

在仓库根目录运行：

```powershell
powershell -ExecutionPolicy Bypass -File build.ps1
```

脚本准备运行时、安装PyInstaller，生成`dist/CodeAgent.exe`。这是Agent自身免预装环境；它生成的项目可能仍需依赖或数据库服务。exe可作为GitHub Release附件，避免提交大型二进制到源码仓库。

## 8. 参考资料

- https://github.com/ultraworkers/claw-code
- https://github.com/Windy3f3f3f3f/how-claude-code-works
- https://github.com/Windy3f3f3f3f/claude-code-from-scratch
- https://github.com/anthropics/claude-code
- https://api-docs.deepseek.com/guides/tool_calls/

参考资料用于理解Agent循环、工具和调用限制；本仓库独立实现，不代表Claude Code或MAAD官方内部实现。
