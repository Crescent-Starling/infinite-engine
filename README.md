# Infinite Engine · 无限引擎

**From Zero to Infinite Possibilities.**

*从零开始，探索无限。*

> An AI-powered personal knowledge exploration and learning system, designed to turn curiosity into structured understanding.

**无限引擎（Infinite Engine）** 是一个以兴趣驱动的知识探索与自主学习为核心、以发展领域专业能力为长期愿景的 AI 知识学习与管理系统。

我们希望借助 AI 降低进入陌生领域的门槛，让用户从好奇出发，逐步建立系统性理解，并持续积累自己的问题、思考与发现。知识管理是支撑学习的基础设施；我们关注的不只是知识如何被存储，更是它如何被**理解、组织、应用，以及在未来重新发现和使用**。

## Why Infinite Engine?

获得答案不等于形成理解，拥有丰富的知识库也不等于掌握其中的知识。对于希望深入探索陌生领域的学习者，仍有几个重要问题：

- **从哪里开始？** 找到可靠来源，认识领域结构，识别基础概念。
- **如何深入理解？** 在即时问答之外，理解概念之间的层级、依赖与语义关系。
- **如何减少管理负担？** 减少反复搜集资料、搭建框架和整理笔记的工作。
- **如何持续积累？** 在兴趣转移或学习中断后，恢复过去的理解并继续探索。

**让 AI 辅助处理重复性的知识管理工作，让用户将更多精力投入理解、探索和判断。**

## Core Ideas

以下是产品的设计方向，功能将逐步实现；实际进展见下方 Project Status。

### 01. Explore Freely · 自由探索

以好奇心为起点，而不是以固定课程为边界。用户可以从一个领域、一种现象或一个问题出发，选择两种互补入口：

- **Conversation-first：** 与 AI 对话，获得解释、讨论和学习建议。
- **Structure-first：** 从知识树和概念关系出发，建立领域整体认识。

两种入口计划共享同一套知识基础，并在切换时保留探索上下文。

### 02. Understand Systematically · 系统理解

将底层知识表示与学习视图分离，按任务呈现领域知识树、概念依赖图、局部语义网络、参考学习路径和来源证据视图。领域分类、概念依赖和教学顺序各有含义，不能互相替代。

知识图谱服务于理解，不是用户必须阅读的唯一界面。

### 03. Learn with AI · 人机共同建构

通过规划中的 AI 导师、可选学习模板和 Skills，支持概念解释、资料阅读、知识比较与证据审查。AI 生成的结构是可以检查、修改和补充的**候选建议**。

个人视图调整、个人解释、候选知识修订和已审核知识分别保存；AI 输出或个人理解不会被自动提升为已验证知识。

**AI 辅助组织知识，用户参与建构理解。**

### 04. Grow Progressively · 渐进式知识生长

以广覆盖的 **Domain Registry**、有来源依据的 **Source Registry** 和小规模审核过的 **Domain Seeds** 为起点，随着实际探索按需提取、校验和扩展知识，而非一次性构建庞大的知识库。

目录收录不代表知识种子已就绪。知识网络增长与个人理解积累分别管理，不能用图谱规模或完成度证明专业能力。

### 05. Remember What Matters · 长期知识积累

计划将个人问题、解释、知识关联与学习历史连接到稳定的知识对象，让用户可以自由开始、暂停和重返不同领域，重新找到过去的思考。

**每一次探索都可以成为下一次探索的起点。**

## System Architecture

系统采用 **local-first、single-user** 定位，围绕三个通过稳定 ID 关联、但职责独立的层次设计：

| Layer | Responsibility |
| --- | --- |
| **Knowledge Representation** | 管理知识对象、类型化关系、来源证据与版本 |
| **Knowledge Views** | 根据学习任务提供知识树、依赖图、学习路径等视图 |
| **Personal Cognition** | 保存个人定义、问题、解释与学习历史 |

规划中的检索与工具接口将连接 LLM、知识服务和个人记录，支持自然语言交互。模块包括 Domain Registry、Source Registry、Knowledge View Engine、RAG、Learning Engine 及 Agent & Skills。

详见 [系统架构](docs/ARCHITECTURE.md) 与 [数据契约](docs/DATA_CONTRACTS.md)。

## Initial Domains

无限引擎面向可扩展的通用知识基础设施。广覆盖领域目录将通过 AI 辅助整理、来源追踪与人工审核逐步积累；初期选择四类领域验证不同知识结构：

| Domain | Focus |
| --- | --- |
| **Astronomy · 天文学** | 领域结构、概念依赖、多模态资料及完整学习闭环 |
| **Latin · 拉丁语** | 词形变化、语法规则与领域专属知识模型 |
| **Fitness & Nutrition · 健身与营养** | 数值、单位、适用条件及证据关系 |
| **Stellaris** | 复杂规则、版本适用性与增量更新 |

天文学计划作为主要端到端 Demo，其余领域初期用于验证模型扩展能力，均不代表已有完整知识库。详见 [演示规划](docs/DEMOS.md)。

## Project Status

**Early Development · 基础工程与 Registry 候选存储阶段**

- **已实现：** 最小 FastAPI 健康检查、React 导航骨架、自动化工程检查；Registry R1 的候选存储与版本记录，以及 R2 的本地 CSV 人工审阅、明确批准导入和离线演示。
- **尚未实现：** 四领域试点数据、已验证 Domain Seeds、完整知识图谱、RAG、AI 导师、学习视图和个人学习历史服务。

当前界面是明确标注功能未实现的工程骨架，并非可用的完整学习产品。完整愿景将分阶段交付，参见 [路线图与验收标准](PLANS.md) 和 [验证记录](docs/VALIDATION.md)。

## Development & Documentation

本项目主要借助 **OpenAI Codex** 进行 AI 辅助开发，采用模块化设计与增量实现策略。已有安装、运行、测试和故障排查说明，见 [开发指南](docs/DEVELOPMENT.md)；基础测试无需付费 API。

| Document | Description |
| --- | --- |
| [产品规格](docs/PROJECT_SPEC.md) | 完整愿景、核心需求与功能范围 |
| [Domain Registry](docs/DOMAIN_REGISTRY.md) | 领域数据资产、来源追踪与人工审核流程 |
| [Learning Engine](docs/LEARNING_ENGINE.md) | 学习动机、目标、活动与人机共同建构 |
| [AGENTS.md](AGENTS.md) | Codex 开发约束与工程规范 |
| [PROMPTS.md](PROMPTS.md) | 有界开发任务的提示词参考 |
| [CHANGELOG.md](CHANGELOG.md) | 已交付变更记录 |

> Preserve the full product vision while implementing small, testable, and verifiable increments.

---

**Curiosity drives exploration. Knowledge enables understanding.**
