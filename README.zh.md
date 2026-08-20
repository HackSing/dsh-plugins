# DSH Plugins

![DSH Plugins — 发现、构建、扩展](assets/social-preview.jpg)

[English](README.md) | 中文

> 一个独立维护、双语呈现、持续更新的 [DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness)（`dsh`）插件目录。

当前整理 **171 个插件**，统一归入四个大类。每个插件只出现一次，并按照最主要的使用价值进行分类。最近一次目录复核：**2026 年 8 月 20 日**。

## 从这里开始

- **正在找插件？** 从下方分类进入；安装前请检查插件仓库、权限、依赖和回滚方式。
- **开发了插件？** 使用[插件提交表单](https://github.com/HackSing/dsh-plugins/issues/new?template=submit-plugin.yml)申请收录。
- **发现信息过期？** [提交信息更新](https://github.com/HackSing/dsh-plugins/issues/new?template=update-plugin.yml)，或[报告失效链接](https://github.com/HackSing/dsh-plugins/issues/new?template=report-broken-link.yml)。
- **希望收到更新？** Watch 本仓库，并通过 [Releases](https://github.com/HackSing/dsh-plugins/releases)查看月度快照。

### 当前快照

这是目录的首个公开快照：共 **171 个插件**、**4 个大类**，中英文条目一一对应。后续新增、移除和修正统一记录在 [CHANGELOG.md](CHANGELOG.md)。

## 分类浏览

- [交互与体验](#交互与体验)：界面、会话、导航、分享及趣味体验
- [工具与能力](#工具与能力)：视觉、数据、文档、通用工具及模型能力扩展
- [自动化与智能体](#自动化与智能体)：工作流、多智能体、定时执行及研究闭环
- [开发与生态集成](#开发与生态集成)：平台集成、运行时、沙箱、诊断及插件开发

## 交互与体验

- [dsh-tianshu-tui](https://github.com/huiliyi37/dsh-tianshu-tui) — 为 DeepSeek Harness 提供终端交互界面。
- [dsh-at-file](https://github.com/omdsh-dev/dsh-at-file) — 支持通过 `@file` 搜索工作区文件，并把文件内容带入提示词。
- [ui-status-label](https://github.com/alingalingling/ui-status-label) — 可将默认思考状态文案替换成自定义内容。
- [dsh-openpencil](https://github.com/ZSeven-W/dsh-openpencil) — 提供 OpenPencil 设计预览与编辑能力。
- [dsh-visualize](https://github.com/Nagi-ovo/dsh-visualize) — 在对话中渲染交互式 HTML 卡片，支持流式预览与沙箱隔离。
- [dsh-side-panel](https://github.com/ccq1/dsh-side-panel) — 在侧边栏集中提供文件浏览、终端操作和 Git 审查。
- [dsh-focus-chat](https://github.com/dingyi222666/dsh-focus-chat) — 提供只突出最终结果的精简会话视图。
- [dsh-genui](https://github.com/omdsh-dev/dsh-genui) — 在回复中嵌入布局、图表、表单、测验、Mermaid 和 3D 场景等交互组件。
- [dsh-annotation](https://github.com/omdsh-dev/dsh-annotation) — 将选中文本的批注随消息发送，并让回复与各条批注对应。
- [dsh-navbar](https://github.com/vlln/dsh-navbar) — 增加会话节点导航条，便于快速跳转到不同用户消息。
- [dsh-task-status](https://github.com/vlln/dsh-task-status) — 在会话页展示后台任务进度和实时输出片段。
- [dsh-web-archive](https://github.com/renat3u/dsh-web-archive) — 折叠 Think、Bash 等容易干扰阅读的会话消息。
- [dsh-spotlight](https://github.com/0xsline/dsh-spotlight) — 为 DSH Web 界面增加键盘优先的命令面板。
- [dsh-101](https://github.com/bill9109/dsh-101) — 提供专门的文档阅读模式。
- [dsh-drag-and-drop](https://github.com/bill9109/dsh-drag-and-drop) — 跨平台拖入文件并插入原始路径，无需复制文件。
- [dsh-deeplink](https://github.com/qyw233/dsh-deeplink) — 通过查询参数深链直达指定会话或工作区。
- [dsh-diff-viewer](https://github.com/lehhair/dsh-diff-viewer) — 使用 PiUI 风格查看器替换写入和编辑操作的默认 DiffBlock。
- [ex-setting](https://github.com/omdsh-dev/ex-setting) — 扩展 DSH 的设置项。
- [web-components](https://github.com/omdsh-dev/web-components) — 为 DSH 增加 Web Components 支持。
- [dsh-turn-navigator](https://github.com/vibeinging/dsh-turn-navigator) — 支持在不同对话轮次之间快速导航。
- [dsh-turn-rewind](https://github.com/Anionex/dsh-turn-rewind) — 基于持久化变更账本恢复到更早的会话和工作区状态。
- [distill](https://github.com/LoserFox/distill) — 通过后台子智能体复盘及技能更新完成会话蒸馏。
- [dsh-share](https://github.com/hellodigua/dsh-share) — 提供一键分享完整会话的能力。
- [dsh-message-edit](https://github.com/Moeblack/dsh-message-edit) — 支持基于分支的消息编辑、重新生成、重试及版本回溯。
- [dsh-mnemon](https://github.com/omdsh-dev/dsh-mnemon) — 集成本地运行时记忆、可检索文档和受监督记忆空间。
- [dsh-sidechain](https://github.com/omdsh-dev/dsh-sidechain) — 在不改变主会话历史的情况下运行持续侧会话或一次性侧问。
- [dsh-conversation-share](https://github.com/bill9109/dsh-conversation-share) — 可只分享会话中的指定片段。
- [dsh-explain](https://github.com/yuezengwu/dsh-explain) — 提供本地优先的学习线程，并按信息来源组织讲解。
- [dsh-prompt-studio](https://github.com/Moeblack/dsh-prompt-studio) — 可分节编辑用户及内置系统提示词，并实时预览效果。
- [dsh-ads](https://github.com/Nagi-ovo/dsh-ads) — 加入具有 2000 年代中文网站风格的虚构趣味广告。
- [dsh-gomoku](https://github.com/omdsh-dev/dsh-gomoku) — 支持玩家与 AI 下五子棋，也可观看两个 AI 对局。
- [dsh-stock-market](https://github.com/AnacondaKC/dsh-stock-market) — 在编码过程中加入带幽默感的模拟股票体验。
- [dsh-emoji](https://github.com/hellodigua/dsh-emoji) — 自动为 AI 回复补充表情符号。
- [dsh-minigames](https://github.com/lhh010/dsh-minigames) — 在侧边栏提供 18 款可离线运行的小游戏。
- [dsh-stickers](https://github.com/william-jin-cmu/dsh-stickers) — 支持用户与智能体双向发送贴纸反馈。
- [whale-girl](https://github.com/vlln/whale-girl) — 增加可拖拽、投喂和互动的桌面宠物。
- [deepseek-manners](https://github.com/Moeblack/deepseek-manners) — 自动追加感谢语，让会话表达更有礼貌。
- [dsh-plugin-d399](https://github.com/HuanLinOTO/dsh-plugin-d399) — 在模型生成期间打开可扩展的小游戏菜单。
- [dsh-auto-chess](https://github.com/omdsh-dev/dsh-auto-chess) — 提供人机或双 AI 自走棋对局。
- [dsh-douyin](https://github.com/AnacondaKC/dsh-douyin) — 增加短视频侧栏，支持原生播放、系列导航和历史续播。
- [dsh-model-modes](https://github.com/DTSFO/dsh-model-modes) — 为DeepSeek Harness Web 编辑器添加快速模式开关与可配置的推理努力档位。
- [dsh-drop-to-path](https://github.com/loudMore/dsh-drop-to-path) — 在 DeepSeek Harness 聊天中将拖放或粘贴的图片和文件转换为工作区路径，供纯文本模型使用。
- [dsh-agent-message](https://github.com/GengDaPeng/dsh-agent-message) — 为 DeepSeek Harness 提供跨会话 Agent 间消息传递，支持离线投递、回执和会话导航。
- [ikanban](https://github.com/isomoes/ikanban) — 为 DeepSeek Harness 提供面向键盘操作的看板界面，用于管理多智能体编码工作空间。
- [mosaic_compress](https://github.com/TuringCorp-net/mosaic_compress) — 提供无状态对话压缩，使对话上下文保持有界。
- [working-activity](https://github.com/ccch1mneyyy/working-activity) — 提供一个 DeepSeek Harness 插件，用于在运行状态行中实时展示代理活动、工具进度和上下文警告。
- [computer-control](https://github.com/JohnXu22786/computer-control) — 为 DSH 智能体提供桌面控制能力，包括屏幕截图、指针与键盘注入以及无障碍树语义操作。

## 工具与能力

- [dsh-vision-toolkit](https://github.com/Anionex/dsh-vision-toolkit) — 为纯文本模型补充图片问答、长截图 OCR、UI 还原、定位及像素比较能力。
- [dsh-custom-tool](https://github.com/omdsh-dev/dsh-custom-tool) — 通过 Monaco 编辑器创建和管理沙箱化 JavaScript 工具。
- [dsh-computer-use](https://github.com/Anionex/dsh-computer-use) — 提供无障碍优先的 macOS 控制，并包含状态新鲜度检查和权限约束。
- [dsh-data-agent](https://github.com/omdsh-dev/dsh-data-agent) — 让 AI 工作流连接数据库并编写 SQL。
- [dsh-toolkit](https://github.com/omdsh-dev/dsh-toolkit) — 集成时间、编码、JSON、计算、CSV、正则、Markdown、差异、统计和 Schema 十类零依赖工具。
- [dsh-tool-csv](https://github.com/omdsh-dev/dsh-tool-csv) — 零依赖解析、查询、聚合和转换 RFC 4180 CSV。
- [dsh-tool-calculator](https://github.com/omdsh-dev/dsh-tool-calculator) — 使用递归下降解析器安全计算数学表达式。
- [dsh-tool-diff](https://github.com/omdsh-dev/dsh-tool-diff) — 对文本、JSON、CSV 和 Markdown 进行结构化比较并生成统一差异。
- [dsh-tool-encoding](https://github.com/omdsh-dev/dsh-tool-encoding) — 处理 Base64、URL、十六进制编解码，以及哈希和 UUID 生成。
- [dsh-tool-json](https://github.com/omdsh-dev/dsh-tool-json) — 使用受支持的 JMESPath 子集查询 JSON。
- [dsh-tool-markdown](https://github.com/omdsh-dev/dsh-tool-markdown) — 完成 HTML 与 Markdown 转换、GFM 表格整理及目录生成。
- [dsh-tool-regex](https://github.com/omdsh-dev/dsh-tool-regex) — 提供正则测试、提取、安全替换和静态解释。
- [dsh-tool-schema](https://github.com/omdsh-dev/dsh-tool-schema) — 支持 JSON Schema 验证、路径查看、解释及规范化。
- [dsh-tool-stat](https://github.com/omdsh-dev/dsh-tool-stat) — 计算描述统计、百分位数、频数分布和相关性。
- [dsh-tool-time](https://github.com/omdsh-dev/dsh-tool-time) — 解析 ISO 8601 时间、转换 IANA 时区并执行 UTC 日历运算。
- [dsh-kb-sieve](https://github.com/omdsh-dev/dsh-kb-sieve) — 从文本、Markdown、DOCX 和 PDF 构建可审计的 SQLite FTS5 知识库包。
- [dsh-plugin-mineru](https://github.com/HuanLinOTO/dsh-plugin-mineru) — 将 MineRU 文档解析工具提供给模型使用。
- [dsh-tool-search](https://github.com/vibeinging/dsh-tool-search) — 为每个智能体提供按需工具发现和渐进式 Schema 展开。
- [dsh-openmaic](https://github.com/THU-MAIC/dsh-openmaic) — 通过 OpenMAIC 提供课堂、幻灯片、交互组件和苏格拉底式教学流程。
- [dsh-scholar](https://github.com/lzszq/dsh-scholar) — 提供面向学术场景的辅助能力。
- [dsh-email](https://github.com/STARDUSTLC666/dsh-email) — 为 DeepSeek Harness 提供六个邮件工具（列表、读取、搜索、发送、文件夹、附件），支持多账号及常见邮箱服务商预设。
- [widget-dock](https://github.com/MorGogh/widget-dock) — 为 DeepSeek Harness 提供可拖拽的小组件面板，展示余额、令牌、统计、命令、目标和成本。
- [dsh-enhance](https://github.com/vcxmug/dsh-enhance) — 提供两个 DeepSeek Harness 插件：dsh-vision 用于图像理解，dsh-native-web 用于网页搜索和抓取。
- [dsh-plugins-store](https://github.com/ZASENJC/dsh-plugins-store) — 自动收录和分类 GitHub dsh-plugin Topic 项目的静态目录网站，并提供用于在 DSH 中浏览目录的可选 Web 插件。
- [dsh-telemetry-redactor](https://github.com/030611/dsh-telemetry-redactor) — 在导出前对 DeepSeek Harness 会话遥测中的敏感值进行脱敏处理。
- [dsh-chat-import](https://github.com/Nwflower/dsh-chat-import) — 将多种AI代理工具的历史会话导入DeepSeek Harness以继续对话。
- [amber-protocol](https://github.com/Bandersnatch0x/amber-protocol) — 为编码代理提供仓库本地治理，并包含 DeepSeek Harness 补丁覆盖层。
- [argo](https://github.com/taxueseek/argo) — 为 AI Agent 提供多语言搜索与证据核验工具。
- [craft-mermaid](https://github.com/chunkithwang/craft-mermaid) — 为AI编程代理生成、渲染和视觉复检Mermaid图表。
- [deepseek-harness-skillx](https://github.com/drowned-fish1/deepseek-harness-skillx) — 一个 DeepSeek Harness 插件，指导智能体安全地发现、评估并采用外部 Agent Skills。
- [knowlp-rag](https://github.com/wly8691-jpg/knowlp-rag) — 实现基于双知识图谱的Markdown笔记检索，提供MCP搜索与反馈工具。
- [modlens](https://github.com/liustack/modlens) — 一个 DeepSeek Harness 插件，通过将粘贴的图片转换为结构化 JSON 证据来提供图像理解能力。
- [modsearch](https://github.com/liustack/modsearch) — 为 DeepSeek Harness 添加网页搜索、X（推特）搜索与页面抓取工具，支持多种引擎。
- [pptfast](https://github.com/liustack/pptfast) — 通过可安装的 DeepSeek Harness 插件，从语义中间表示生成可编辑的 PPTX 演示文稿。
- [pptkit-presentation](https://github.com/openHacking/pptkit-presentation) — 提供一个 DeepSeek Harness 插件包，注册 pptkit-presentation 技能，用于从源材料创建可编辑的 PowerPoint 演示文稿。
- [uagent-sync](https://github.com/severin-ye/uagent-sync) — 提供命令行工具，用于备份、恢复和同步代理工作区配置与数据。
- [dsh-passwords](https://github.com/slywalker2006/dsh-passwords) — 为 DeepSeek Harness 提供登录网关和多用户账户管理功能。
- [agent-jit](https://github.com/sybolization/agent-jit) — 提供一个 DeepSeek Harness 插件，将确定性代理执行路径编译为 DSL 程序并直接执行。
- [clawock](https://github.com/KCNyu/clawock) — 提供可移植的投资决策工作流插件套件，包含 Python 源码和命令行工具。
- [DeepSeek-PPT-skill](https://github.com/lecutu/dsh-slide-reflex) — 通过确定性布局引擎，根据AI声明的布局意图生成PowerPoint演示文稿，并提供用于实时预览和反馈的DSH插件。
- [DeepSeek_Prism](https://github.com/YOGEMOW/DeepSeek_Prism) — 为 DeepSeek Harness 添加 prism_see 工具和图片识别能力。
- [gongwen-skill](https://github.com/linhut/gongwen-skill) — 提供中文公文处理工具，支持 DSH 技能与 Cordis 插件集成。
- [sandbase-harness](https://github.com/sandbaseai/sandbase-harness) — 提供 DeepSeek Harness 插件包，通过 MCP 暴露代理运行时管理工具。
- [sidesight](https://github.com/ZhuXinAI/sidesight) — 提供CLI命令，使用多模态模型分析截图、示意图、图表、UI差异和视频。
- [write-chinese-long-screenplay](https://github.com/mudden2380078550-creator/write-chinese-long-screenplay) — 提供中文长剧本创作技能，包含项目初始化、上下文构建、校验与审查脚本，适用于兼容 SKILL.md 的智能体。
- [docs-retriever](https://github.com/JohnXu22786/docs-retriever) — 实现一个MCP服务器，用于检索版本化库文档，提供目录查询、版本列表和文档提取工具。
- [codegraph](https://github.com/JohnXu22786/codegraph) — 提供代码知识图谱，将符号、调用点和导入索引到SQLite，并通过CLI或stdio MCP工具服务器回答结构性问题。
- [file-planning](https://github.com/JohnXu22786/file-planning) — 提供基于磁盘持久化的执行规划，包含里程碑、步骤状态机和审计事件。
- [fs-mcp](https://github.com/JohnXu22786/fs-mcp) — 为代理提供受限的文件系统 MCP 服务器，在可配置区域内提供文件读写、搜索和元数据操作。
- [task-board](https://github.com/JohnXu22786/task-board) — 为 DeepSeek Harness 提供跨会话事件溯源任务面板，支持任务跟踪、审计历史和看板导出。
- [pty-runner](https://github.com/JohnXu22786/pty-runner) — 为 DeepSeek Harness 提供后台终端作业管理，支持 PTY 进程启动、输入、输出分页和作业控制。
- [github-mcp](https://github.com/JohnXu22786/github-mcp) — 一个 DeepSeek Harness 插件，打包了暴露 GitHub 仓库、议题、拉取请求、审查和搜索工具的 MCP 服务器。
- [worktree-mgr](https://github.com/JohnXu22786/worktree-mgr) — 为 DeepSeek Harness 提供任务隔离的 git 工作区管理工具，包括创建、同步、收尾和批量清理操作。
- [command-scout](https://github.com/JohnXu22786/command-scout) — 扫描项目构建声明文件并将发现的命令作为代理工具暴露。
- [dsh-Api-monitor](https://github.com/linshufan21/dsh-Api-monitor) — 在 DeepSeek Harness 设置面板中新增 API 余额与 Token 用量监测模块。
- [local-shell-mcp](https://github.com/fwerkor/local-shell-mcp) — 提供一个DeepSeek Harness插件包，通过MCP服务器暴露shell、文件、浏览器和远程机器工具。
- [Stata-AI-Skill](https://github.com/ZihaoVistonWang/Stata-AI-Skill) — 提供本地 HTTP 服务，使 AI 代理能够运行 Stata，并以 DeepSeek Harness 插件形式分发。
- [Vibe-Mathematics](https://github.com/ChongCyrus/Vibe-Mathematics) — 在 DeepSeek Harness 中提供多代理数学问题求解与验证框架。
- [TokenLedger](https://github.com/zh667/TokenLedger) — 为 DeepSeek Harness 记录令牌用量并按中转站归属，支持余额与配额查询。
- [agentshim](https://github.com/possible055/agentshim) — 为编码代理提供代码库工具和进程执行功能，并包含 DSH 原生适配器。
- [gamify-edu](https://github.com/BinLe1988/gamify-edu) — 作为DeepSeek Harness客户端插件，提供游戏化教育平台。
- [geo-content-optimizer](https://github.com/wangzhuo-coding/geo-content-optimizer) — 为DeepSeek Harness提供GEO内容优化能力，包括文档解析、流水线执行和联网搜索工具。
- [ouroboros](https://github.com/Q00/ouroboros) — 通过内置的 dsh 插件，在 DeepSeek Harness 聊天中启用 Ouroboros 的 interview 和 auto 工作流命令。
- [beautiCode](https://github.com/starsstreaming/beautiCode) — 为DeepSeek Harness网页界面添加可定制的图片和视频背景。
- [Co-Engram](https://github.com/Co-Engram/Co-Engram) — 为AI代理和团队提供自进化记忆系统，以Markdown文件存储记忆，并随时间进行强化和衰减。
- [dsh-riskproof](https://github.com/onlyqzq/dsh-riskproof) — 实现一个风险感知的审批层，在DeepSeek Harness中追踪数据来源并在工具执行前应用策略决策。
- [MemOS](https://github.com/MemTensor/MemOS) — 为AI智能体提供持久记忆管理的记忆操作系统，包含本地和云插件组件。
- [OpenFlowFrames](https://github.com/ZeroHackz/OpenFlowFrames) — 为DeepSeek Harness代理提供基于RIFE模型的视频帧插值工具。
- [AI-Novel-Writer](https://github.com/EthanYoQ/AI-Novel-Writer) — 仓库包含桌面版 AI 小说创作应用及用于 DeepSeek Harness Web 的小说创作插件。
- [dsh-memory-evolve](https://github.com/csyangwen/dsh-memory-evolve) — 为 DeepSeek Harness 添加跨会话记忆、待办管理、技能管理器、会话协作等功能增强。
- [sandbase-skills](https://github.com/sandbaseai/sandbase-skills) — 一个包含88个智能体技能的集合，涵盖研究、社交智能、营销和业务流程。
- [rss-digest](https://github.com/JohnXu22786/rss-digest) — 提供RSS/Atom订阅、定时抓取、去重、LLM摘要和每日Markdown简报功能。
- [docindex](https://github.com/JohnXu22786/docindex) — 提供工作区文档的本地语义索引，支持词法和语义混合检索及行号引用。
- [net-debug](https://github.com/JohnXu22786/net-debug) — 为 DeepSeek Harness 提供 HTTP 调试工具，包括通用 HTTP 客户端、带重放功能的请求历史以及响应检查。

## 自动化与智能体

- [dsh_workflow](https://github.com/omdsh-dev/dsh_workflow) — 提供可复用、可观察、可治理并支持恢复的多智能体工作流层。
- [dsh-agent-teams](https://github.com/NanmiCoder/dsh-agent-teams) — 将多个智能体组织为协作团队。
- [dsh-automation](https://github.com/titanwings/dsh-automation) — 在全新智能体会话中定时执行编码任务，并保留可审计记录。
- [dsh-plannotator](https://github.com/titanwings/dsh-plannotator) — 对计划原文进行锚定批注，并把结构化反馈送回智能体。
- [dsh-loop](https://github.com/vlln/dsh-loop) — 通过 `/loop` 命令、循环工具和活动指示器实现周期执行。
- [dsh-sentinel](https://github.com/fuhefei/dsh-sentinel) — 持续监视文件、命令、HTTP、进程或 Webhook，并在条件满足时唤醒智能体。
- [dsh-deep-research](https://github.com/omdsh-dev/dsh-deep-research) — 基于工作流引擎编排自适应深度研究。
- [dsh-inspect](https://github.com/omdsh-dev/dsh-inspect) — 执行发现问题、修复和复查的对抗式闭环。
- [dsh-track](https://github.com/fakechris/dsh-track) — 内置决策跟踪、想法收集及 Linear 风格的问题管理。
- [dsh-advisor](https://github.com/btspoony/dsh-advisor) — 配置第二个模型逐轮审查主智能体并补充建议。
- [DeepJIT](https://github.com/fly3366/DeepJIT) — 用于 deepseek-harness 的 JIT 编译器插件，挖掘智能体执行轨迹并将重复工作流编译为可复用的技能和流程模板。
- [dsh-continual-evolve](https://github.com/ZK-Andy/dsh-continual-evolve) — 为 DeepSeek Harness 实现持续自我进化，持久化并优化提示笔记、记忆、技能和子代理规格，支持回滚和基准验证。
- [context-pruner](https://github.com/JohnXu22786/context-pruner) — 用于 DeepSeek Harness 的会话上下文分诊插件，修剪过期、重复、失败和过大的上下文以节省 token 预算。
- [allinluna](https://github.com/zenx0x/allinluna) — 为 DeepSeek Harness 提供资源感知的多智能体编排。
- [dsh-browser](https://github.com/Lum1104/dsh-browser) — 提供 Chrome 扩展和桥接插件，使 DeepSeek Harness 能够通过基于文本的工具操控浏览器。

## 开发与生态集成

- [dsh-open-in-vscode](https://github.com/omdsh-dev/dsh-open-in-vscode) — 从 DSH Web 界面直接在 VS Code 中打开工作区。
- [dsh-notification](https://github.com/omdsh-dev/dsh-notification) — 根据回合结果和关键词规则发送可配置的桌面通知。
- [dsh-acp-for-bitfun](https://github.com/bobleer/dsh-acp-for-bitfun) — 通过 ACP 打通 BitFun 与 DSH。
- [telegram](https://github.com/LoserFox/telegram) — 连接 Telegram Bot API，支持独立聊天会话和 HTML 格式化。
- [dsh-session-notification](https://github.com/dingyi222666/dsh-session-notification) — 通过浏览器通知和提示反馈四种会话状态。
- [dsh-web-ui-notify](https://github.com/bill9109/dsh-web-ui-notify) — 从 Web 界面触发桌面提醒。
- [dsh-webbridge](https://github.com/bill9109/dsh-webbridge) — 将 DSH 与 Kimi WebBridge 连接起来。
- [fabric](https://github.com/omdsh-dev/fabric) — 提供类似 MC Fabric 的 Hook 处理机制。
- [dsh-git-identity](https://github.com/LoserFox/dsh-git-identity) — 通过覆盖式环境变量固定 Git 提交的作者身份。
- [dsh-context-doctor](https://github.com/Zhenyu98/dsh-context-doctor) — 审计注入上下文的 Token 成本、重复内容以及指令或 Schema 冲突。
- [dsh-plugin-check](https://github.com/omdsh-dev/dsh-plugin-check) — 零依赖、只读检查插件清单、补丁格式和构建风险。
- [dsh-security-audit](https://github.com/omdsh-dev/dsh-security-audit) — 针对配置、插件来源、会话和网络暴露生成脱敏的本地安全报告。
- [dsh-session-health](https://github.com/omdsh-dev/dsh-session-health) — 从帧级别诊断截断、损坏或空白的会话文件。
- [dsh-evolve](https://github.com/william-jin-cmu/dsh-evolve) — 让智能体在会话过程中动态挂载或移除持久化插件。
- [dsh-trace](https://github.com/vibeinging/dsh-trace) — 将会话轮次、模型步骤和工具调用导出至 yiTrace 遥测后端。
- [sandbox-micro](https://github.com/omdsh-dev/sandbox-micro) — 增加 microsandbox 运行环境支持。
- [sandbox-mxc](https://github.com/omdsh-dev/sandbox-mxc) — 增加微软跨平台沙箱支持。
- [sandbox-nono](https://github.com/omdsh-dev/sandbox-nono) — 增加 nono 沙箱支持。
- [dsh-agent-budget](https://github.com/vibeinging/dsh-agent-budget) — 管理智能体树的 Token 预算。
- [dsh-llm-fallbacks](https://github.com/btspoony/dsh-llm-fallbacks) — 按角色配置语言模型重试及备用策略。
- [dsh-tool-approval](https://github.com/ilharp/dsh-tool-approval) — 为工具调用增加手动审批模式。
- [plugin-template](https://github.com/omdsh-dev/plugin-template) — 提供用于开发 DSH 插件的起步模板。
- [Qwen-MM-Plugins](https://github.com/omdsh-dev/Qwen-MM-Plugins) — 增加 Qwen 多模态插件支持。
- [dsh-tps](https://github.com/Small-tailqwq/dsh-tps) — 展示 TPS 性能指标。
- [Code2Skill](https://github.com/leechen298/Code2Skill) — 从现有源代码生成功能、MCP 工具、Agent 技能和离线测试。
- [conservative-code-edits](https://github.com/addxing/conservative-code-edits) — 为 AI 编程代理提供在现有项目中进行小范围、最小必要代码修改的技能。
- [embedded-workbench](https://github.com/AmethystLuna/embedded-workbench) — 提供嵌入式 C/C++ 固件开发技能（FreeRTOS、Keil MDK、HardFault 故障排查、状态机）及 agent 纪律工作流。
- [function-extraction](https://github.com/addxing/function-extraction) — 从代码库中提取完整功能实现链路并生成技术开发文档的技能。
- [function-testing](https://github.com/addxing/function-testing) — 根据PRD、Git提交记录或用户故事生成功能测试用例，并导出Excel风格测试报告。
- [mstar-harness](https://github.com/btspoony/mstar-harness) — 实现了一个由技能驱动的工作流引擎，提供多智能体代码交付技能。
- [replicate-android-feature](https://github.com/addxing/replicate-android-feature) — 一个代理技能，用于在其他项目或平台中复刻现有 Android 功能，保持行为、界面和可复用资源一致。
- [spec-driven](https://github.com/JohnXu22786/spec-driven) — 提供规格驱动开发技能包，包括五个技能和三个工具。
- [skill-framework](https://github.com/JohnXu22786/skill-framework) — 为 DeepSeek Harness dsh 提供作为 Cordis 插件的工程方法论技能库。
- [agent-dev-skills](https://github.com/ddtcorex/agent-dev-skills) — 为 DeepSeek Harness 提供开发技能集合和代理预设。
- [GraphFlow](https://github.com/Roarpeng/GraphFlow) — 一个DSH插件，为编码代理提供本地优先的代码知识图谱和上下文工具。

## 如何选择插件

安装前建议检查五项信息：插件解决的问题、支持的 DSH 版本与平台、安装和卸载步骤、所需权限，以及近期维护活跃度。被本目录收录只代表项目可被发现，不代表已经完成兼容性或安全性验证。

## 提交或更新插件

插件开发者统一使用[插件提交表单](https://github.com/HackSing/dsh-plugins/issues/new?template=submit-plugin.yml)申请收录；这是唯一官方提交入口，不需要修改目录文件或创建 PR。发现已有条目需要修正时，请使用[信息更新表单](https://github.com/HackSing/dsh-plugins/issues/new?template=update-plugin.yml)。

建议同时为插件仓库添加 [`dsh-plugin`](https://github.com/topics/dsh-plugin) 主题，方便生态用户发现项目。Topic 不替代正式提交表单。

目录通过自动化规则持续维护；正式收录结果以中英文目录和 [CHANGELOG.md](CHANGELOG.md) 为准。

详细收录标准、审核规则和贡献流程请参阅 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 使用说明

本仓库只提供信息索引，不代表推荐或安全审查结论。插件的可用性、兼容性和实际行为可能发生变化，安装前请自行检查对应仓库及其权限要求。

本目录的原创编辑内容采用 [CC BY 4.0](LICENSE) 许可；所链接插件及第三方材料仍遵循各自权利人和许可证。
