# DSH Plugins

![DSH Plugins — 发现、构建、扩展](assets/social-preview.jpg)

[English](README.md) | 中文

> 一个独立维护、双语呈现、持续更新的 [DeepSeek Harness](https://github.com/deepseek-ai/deepseek-harness)（`dsh`）插件目录。

当前整理 **94 个插件**，统一归入四个大类。每个插件只出现一次，并按照最主要的使用价值进行分类。最近一次目录复核：**2026 年 8 月 13 日**。

## 从这里开始

- **正在找插件？** 从下方分类进入；安装前请检查插件仓库、权限、依赖和回滚方式。
- **开发了插件？** 使用[插件提交表单](https://github.com/HackSing/dsh-plugins/issues/new?template=submit-plugin.yml)申请收录。
- **发现信息过期？** [提交信息更新](https://github.com/HackSing/dsh-plugins/issues/new?template=update-plugin.yml)，或[报告失效链接](https://github.com/HackSing/dsh-plugins/issues/new?template=report-broken-link.yml)。
- **希望收到更新？** Watch 本仓库，并通过 [Releases](https://github.com/HackSing/dsh-plugins/releases)查看月度快照。

### 当前快照

这是目录的首个公开快照：共 **94 个插件**、**4 个大类**，中英文条目一一对应。后续新增、移除和修正统一记录在 [CHANGELOG.md](CHANGELOG.md)。

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
- [dsh-sidechain](https://github.com/Buyi-wsgzg/dsh-sidechain) — 在不改变主会话历史的情况下运行持续侧会话或一次性侧问。
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

## 自动化与智能体

- [dsh_workflow](https://github.com/icetomoyo/dsh_workflow) — 提供可复用、可观察、可治理并支持恢复的多智能体工作流层。
- [dsh-agent-teams](https://github.com/NanmiCoder/dsh-agent-teams) — 将多个智能体组织为协作团队。
- [dsh-automation](https://github.com/titanwings/dsh-automation) — 在全新智能体会话中定时执行编码任务，并保留可审计记录。
- [dsh-plannotator](https://github.com/titanwings/dsh-plannotator) — 对计划原文进行锚定批注，并把结构化反馈送回智能体。
- [dsh-loop](https://github.com/vlln/dsh-loop) — 通过 `/loop` 命令、循环工具和活动指示器实现周期执行。
- [dsh-sentinel](https://github.com/fuhefei/dsh-sentinel) — 持续监视文件、命令、HTTP、进程或 Webhook，并在条件满足时唤醒智能体。
- [dsh-deep-research](https://github.com/omdsh-dev/dsh-deep-research) — 基于工作流引擎编排自适应深度研究。
- [dsh-inspect](https://github.com/omdsh-dev/dsh-inspect) — 执行发现问题、修复和复查的对抗式闭环。
- [dsh-track](https://github.com/fakechris/dsh-track) — 内置决策跟踪、想法收集及 Linear 风格的问题管理。
- [dsh-advisor](https://github.com/btspoony/dsh-advisor) — 配置第二个模型逐轮审查主智能体并补充建议。

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

## 如何选择插件

安装前建议检查五项信息：插件解决的问题、支持的 DSH 版本与平台、安装和卸载步骤、所需权限，以及近期维护活跃度。被本目录收录只代表项目可被发现，不代表已经完成兼容性或安全性验证。

## 新增或更新插件

欢迎提交贡献。请在 `data/plugins.json` 中新增或更新插件，将其放入一个最符合主要用途的分类，然后运行 `python3 scripts/sync_topic_plugins.py render` 重新生成中英文目录。正式条目采用以下格式：

```markdown
- [插件名称](https://github.com/owner/repository) — 用一句清晰的话说明插件的主要价值。
```

建议同时为插件仓库添加 [`dsh-plugin`](https://github.com/topics/dsh-plugin) 主题，方便其他用户发现。

自动化任务每天扫描该 Topic，通过结构规则和已配置的模型服务生成分类及事实性的双语描述。任务首先以观察模式运行；开启自动发布后，只有被高置信度确认且通过全部目录校验的候选项目才会发布。每次成功收录都会生成仓库报告并通过 GitHub Issue 通知维护者。

详细收录标准、审核规则和贡献流程请参阅 [CONTRIBUTING.md](CONTRIBUTING.md)。

## 使用说明

本仓库只提供信息索引，不代表推荐或安全审查结论。插件的可用性、兼容性和实际行为可能发生变化，安装前请自行检查对应仓库及其权限要求。

本目录的原创编辑内容采用 [CC BY 4.0](LICENSE) 许可；所链接插件及第三方材料仍遵循各自权利人和许可证。
