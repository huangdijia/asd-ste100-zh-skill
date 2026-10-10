# 中文技术文本保真与清晰化：规则说明与上游对照

适配稿版本：0.1.0-draft。核对日期：2026-10-10。

## 结论

原项目最值得保留的是“减少歧义，保留情态和全部条件”的纪律。中文版本应围绕语义与逻辑重建规则，不能把英文的词数、词性、时态和词典约束直译过来。

本包提供可直接作为技能文件使用的 `SKILL.md`，以及原版映射、保真示例和语义验收样例。使用这些文件不会自动安装技能或改变任何默认设置。

核心原则只有一句：**先保持原意，再减少歧义；句子更短不能以信息变少或结论变强为代价。**

## 1. 这次实际读取了什么

上游仓库：[danyuchn/asd-ste100-skill](https://github.com/danyuchn/asd-ste100-skill)。

- 分支：`master`
- 当前核对快照：[`32511c6992ecb5f1971e46a2943f2e6adceedafe`](https://github.com/danyuchn/asd-ste100-skill/commit/32511c6992ecb5f1971e46a2943f2e6adceedafe)
- 提交日期：2026-10-04 06:18:56 UTC
- 提交说明：`fix(lint): preserve modal perfect hedges and passive heuristic`
- 上游 `SKILL.md` 声明版本：`0.4.0`。这是文件内版本，不将其当成已经验证的 release/tag。

直接逐篇核对的固定版本来源：

1. [SKILL.md](https://github.com/danyuchn/asd-ste100-skill/blob/32511c6992ecb5f1971e46a2943f2e6adceedafe/SKILL.md)：用途、双模式、规则、流程、输出约定及边界。
2. [references/writing-rules.md](https://github.com/danyuchn/asd-ste100-skill/blob/32511c6992ecb5f1971e46a2943f2e6adceedafe/references/writing-rules.md)：上游对 STE 规则类别的概述。
3. [examples/before-after.md](https://github.com/danyuchn/asd-ste100-skill/blob/32511c6992ecb5f1971e46a2943f2e6adceedafe/examples/before-after.md)：规则例子和代理文本 A–D 改写。
4. [README.md](https://github.com/danyuchn/asd-ste100-skill/blob/32511c6992ecb5f1971e46a2943f2e6adceedafe/README.md)：项目用途、安装说明及 linter 边界。
5. [scripts/ste-lint.py](https://github.com/danyuchn/asd-ste100-skill/blob/32511c6992ecb5f1971e46a2943f2e6adceedafe/scripts/ste-lint.py) 和 [边界样例](https://github.com/danyuchn/asd-ste100-skill/blob/32511c6992ecb5f1971e46a2943f2e6adceedafe/examples/linter-edge-cases.md)：实际实现覆盖面，不把规则描述当作实现保证。
6. [LICENSE](https://github.com/danyuchn/asd-ste100-skill/blob/32511c6992ecb5f1971e46a2943f2e6adceedafe/LICENSE)：MIT 许可与版权归属。

“当前”只指上述读取时的快照；仓库后续提交不自动改变本适配稿。本稿以原仓库文件为直接来源，没有以第三方文章替代原文件。

## 2. 原项目真正做的事

它是面向英语文本的编辑技能，主要读者是代理、工具调用方或跨语言读者。它把原文拆成较短、较明确的句子，并要求保留事实、条件、范围和确定程度。它不是语言模型、编译器、语义证明器，也不执行被改写的操作。

原版分为 Strict 和 STE-flavored 两种模式，分别偏向操作/高误读成本文本与一般解释性文本。两者仍采用英文结构约束；词典相关部分只能作为建议，因为项目没有提供 ASD 官方批准词典。原版明确承认：不能保证航空或国防级 STE 合规。[来源：SKILL.md](https://github.com/danyuchn/asd-ste100-skill/blob/32511c6992ecb5f1971e46a2943f2e6adceedafe/SKILL.md)

上游自述依据 ASD-STE100 Issue 9（2025-01）的规则类别，提及 53 条写作规则、9 个章节及约 900 个批准词。这些是上游的标准概述，不是本稿对官方全文的独立合规核验，也不意味着中文规则有相同的标准地位。[来源：references/writing-rules.md](https://github.com/danyuchn/asd-ste100-skill/blob/32511c6992ecb5f1971e46a2943f2e6adceedafe/references/writing-rules.md)

### 必须区分：写作规则、检测能力、语义正确性

原版 linter 用正则等启发式方法检测部分英语结构。它没有比较原文与改写，不能验证语义等价。

- 句长实现按空格分词，统一使用 25 词阈值；并不自动识别“步骤 20 词、说明 25 词”两类文本。
- 只识别有限的英语短语动词列表，不覆盖所有短语动词。
- 被动式和完成时属于提示项；当前提交保护带情态的完成式，避免把不确定性当成需要删除的问题。
- 同义词检查基于预设词组共现，不能证明这些词在上下文中确实表达同一动作。
- 不检查中文条件作用域、否定范围、术语指代、数字保真或改写新增事实。
- `linter-edge-cases.md` 是故意不合规的测试材料，不能作为正文写法模板。

因此，本中文稿不附带或声称已有“中文 STE linter”。测试文件是人工或模型审阅用的语义验收样例。即使未来增加机械检查，零告警也只代表相应检查没发现问题。[实现来源](https://github.com/danyuchn/asd-ste100-skill/blob/32511c6992ecb5f1971e46a2943f2e6adceedafe/scripts/ste-lint.py)

## 3. 原版到中文：保留、调整、不直接适用

下表中的“原版”指上述仓库快照，不代表对 ASD 官方条款的逐条翻译。

| 原版做法 | 中文处理 | 原因与规则位置 |
|---|---|---|
| 保留事实、条件、范围限定 | 保留并细化 | 把量词、逻辑、否定、例外、状态等列为独立不变量。R1–R6 |
| 保留 may/could 等情态 | 保留并扩展 | 中文还需保护“应、建议、允许、预计、已、仍”等规范强度和状态。R5–R6 |
| Strict / STE-flavored 双模式 | 调整为步骤 / 说明 | 根据句段功能区分命令与事实，避免把错误说明改成新增指令。第 2 节 |
| 指令每句一个动作 | 保留目标，允许共同条件统领列表 | 拆句不能丢失条件，也不能给并列动作新增顺序。R3、R8 |
| 主动语态优先 | 调整为执行者明确时优先主动 | 中文状态句可自然保留；不知道是谁做的不能猜主语。R1、R7 |
| 不省略主语、动词、冠词 | 调整为不省略必要成分 | 中文没有英文冠词系统；明确场景下可以省主语，不能省逻辑。R7 |
| 步骤 20 词、说明 25 词上限 | 不照搬；改为短句软目标 | 中文分词不等同于英文空格词；长度不能作语义质量合格线。R9 |
| 简单时态限制 | 不直接适用 | 保留“已、正在、尚未、将”等时间和状态信息。R5 |
| 一个词只用一种词性 | 不直接适用 | 中文词性灵活；以语境明确和术语一致为准。R10 |
| 官方批准词与单义词典 | 不直接适用 | 不存在本稿可据以声称合规的中文 STE 批准词典。R10、第 7 节 |
| 同一概念统一叫法 | 保留，但必须先验证确实同义 | 不把“检查、验证、确认”或“错误、故障、失败”强行合并。R10 |
| 技术领域词表 | 保留，但不发明定义 | 可以建议词表条目；定义必须有依据。R10 |
| 避免名词化动作 | 按等义原则调整 | 可把“进行检查”改成“检查”；不强行改动专业名词或状态名。R10 |
| 不使用英语短语动词 | 不直接适用 | 中文改为避免难懂的行话、隐喻或空泛动词，不建立英语式禁令。R10 |
| 名词簇最多 3 词 | 不直接适用 | 检查多重定语的依附关系；不拆专名、不按词数判错。R8 |
| 禁分号 | 不照搬 | 中文分号可清晰表达同层并列；复杂逻辑仍可改列表。R8 |
| 每段一个主题、最多 6 句 | 保留主题原则，取消硬句数 | 分段应服务信息组织；不为了数字拆散条件和例外。R8 |
| 三项以上步骤/条件用列表 | 作为建议保留 | 列表必须保留“全部/任一”关系，不能把并列改成顺序。R3、R8 |
| 安全指令与条件前置 | 保留，明确约束对象 | 原有警告放在相关动作前或紧邻处，移动位置不能扩大范围或新增义务。R8 |
| 删除堆叠 hedge 和营销形容词 | 收紧为有条件编辑 | 确定程度不能删；性能主张不能偷换或编造数值。R6、R10 |
| 默认只输出改写，按需对比 | 保留并增加必要的待确认出口 | 原文歧义不能因“只输出成品”而被隐藏。第 6 节 |
| 更清楚的长句可保留并注明 | 保留 | 信息正确优先于短句。R9、第 6 节 |
| 英语机械 linter | 不直接迁移到中文 | 语义检查必须有原文—改写双向对应。第 5 节 |
| 对代码与引用的跳过处理 | 扩展为明确保护规则 | 保护 API、参数、路径、错误码、匹配字符串、引文等。R11 |

## 4. 原版示例不能全部照抄

原版原则强调“不新增事实、不改变情态”，但几个示例并不完全满足它自己的原则。中文稿选择以保真原则为准，不把每个示例都当作正确答案。[示例原文件](https://github.com/danyuchn/asd-ste100-skill/blob/32511c6992ecb5f1971e46a2943f2e6adceedafe/examples/before-after.md)

- **A，工具说明**：改写新增“读取已配置策略”这个实现步骤。原文说明行为取决于策略，并未明说读取发生的时间或机制。示例对 otherwise 的解释也选定了一个具体回退范围；在中文稿中，有实质歧义时应先确认。
- **B，错误消息**：原文的“处理期间可能发生错误”被改成“请求可能失败”；这两件事不是必然等价。改写还补出了服务器及“检查客户端版本”的动作。可以把检查建议另列，但不能当成原文内容。
- **C，代理指令**：示例明确承认新增了完整性检查；它还把 should 改成命令。中文稿保留原有规范强度，不把建议自动升格为必须执行的步骤。
- **D，README**：原文的无供应商锁定、低摩擦集成、语义相似度缓存主张，被改成关于普通缓存机制及数据不离开现有栈的具体陈述。尤其“无供应商锁定”不能推出“数据不外流”。这不是纯保真改写。

这不否定原项目的实用价值，而是说明：良好原则、示例正确性和检测能力必须分别核查。

## 5. 中文版完整执行方式

可直接使用的详细规则见 `SKILL.md`。执行时依次做四件事：

1. 识别文本是在命令读者、说明系统，还是报告状态。
2. 提取语义单元，保护数字、逻辑、限定、情态与机器标识。
3. 只修改确实导致歧义或阅读负担的表达。
4. 双向复核：原文每项信息都有去处，改写每项信息都有来源。

对缺失的信息，不做“合理补全”。对已有信息，不因为想让文字更干练而省略。正文与新增建议分开，未确定的解释明确标为待确认。

### 软句长怎么用

本稿不设中文字数指标，也不将英文 20/25 词换算成汉字数量。软目标是让每句优先承载一个主要动作或判断。真正需要检查的是一句里是否塞入多个难以区分的动作、分支或层级。条件完整的较长句优于丢失范围的几句短句。

## 6. 五个保真示例

以下示例是本稿编写的中文测试材料，说明允许的结构调整；不声称来自真实产品或官方标准。

### 示例 1：拆分共同条件，不新增顺序

原文：

> 当状态为 READY 且校验值匹配时，代理会提交结果并记录本次提交；否则代理会返回错误。

改写：

> 当状态为 READY 且校验值匹配时，代理会执行以下两项操作：
> - 提交结果。
> - 记录本次提交。
>
> 如果上述两个条件未同时满足，代理会返回错误。

核对：保留 READY、且、两项动作和原有错误分支；使用无序列表，不编造“先提交后记录”。不增加重试、回滚或用户处理步骤。

### 示例 2：错误、失败与可能原因分开

原文：

> 处理请求时可能发生了错误，原因可能是数据格式与预期不符，而这种不符可能由过旧的客户端版本引起。

改写：

> 处理请求时可能发生了错误。原因可能是数据格式与预期不符。这种格式不符可能由过旧的客户端版本引起。

核对：三个“可能”分别支配原有判断。没有把“发生错误”升级为“请求失败”，没有猜测谁定义预期格式，没有添加检查或升级客户端的命令。

### 示例 3：保留原有规范强度和未报告状态

原文：

> 在上游任务完成且未报告错误后，下游代理应读取输出产物，但在超时情况下，有时会生成不完整的产物。

改写：

> 在上游任务完成且未报告错误后，下游代理应读取输出产物。但在超时情况下，有时会生成不完整的产物。

核对：保留“应”，不擅自改成“必须”或“建议”；仍是“未报告错误”，不是“没有发生错误”；保留“但”和“有时”。没有增加“等待任务”“检查完整性”等原文没有的动作。

### 示例 4：减少动作外壳，保护参数与字符串

原文：

> 请对 `timeout_ms` 的值进行检查。它大于 5000 时，返回字符串 `"TIMEOUT_LIMIT"`；任何情况下都不要对参数 `retry_count` 进行修改。

改写：

> 请检查 `timeout_ms` 的值。当该值大于 5000 时，返回字符串 `"TIMEOUT_LIMIT"`。任何情况下都不要修改参数 `retry_count`。

核对：保留严格大于、数字 5000、两个参数名、精确字符串以及禁止修改。没有根据参数名把 5000 换算成秒；没有把最后的禁止事项错误地限定在超时分支内。

### 示例 5：原文有歧义时，不假装已经消除

原文：

> 更新代理和服务的配置后，重启它。

可交付的保留正文：

> 更新代理和服务的配置后，重启它。

必要说明：

> 待确认：要更新的是“代理的配置与服务的配置”，还是“代理本身与服务的配置”？“它”指代理还是服务？确认后再明确对象和指代。

核对：没有擅自改成“重启代理”或“重载配置”。这时保留歧义并提问，比输出一个流畅但可能错误的命令更可靠。

## 7. 验收方式与限制

读取 `references/acceptance-tests.zh-CN.md`，使用其中的原文、允许变化及禁止变化做独立测试。评判关键是语义不变量，不要求输出逐字等于某个示例。

最低验收标准：

- 无新增事实、动作、阈值、时限、责任方或处理策略。
- 无遗漏条件、量词、否定、例外或适用范围。
- 无变更必要/充分条件、且/或、确定程度、建议强度、时间或状态。
- 受保护字符串保持原样。
- 原文确有重要歧义时能够暂停相关改写，并给出具体待确认问题。
- 已经清晰的文本不强行改写。

这些规则不能证明原文真实、系统安全、业务逻辑正确或操作已获授权。它们也不能替代法律、医疗、航空等场景的专业审查。读者不应把“文字更清楚”当成“事实已经核实”。

本包不提供自动安装、后台常驻、代理间自动授权或默认写作风格切换。是否将技能加入某个工具环境，应由使用者另行决定。

## 8. 文件与许可

- `SKILL.md`：可直接复用的规则入口。
- `README.md`：项目用途、使用方式和边界。
- `RULES.zh-CN.md`：本说明，包括来源、映射、设计选择和保真示例。
- `references/acceptance-tests.zh-CN.md`：语义回归验收样例。
- `LICENSE`：原仓库 MIT 许可全文。

本稿适配了 Dustin Yuchen Teng 的 MIT 许可仓库内容，保留其版权与许可声明。中文适配的新增规则、示例和措辞是本次草稿，不应被归为上游作者或 ASD 的官方主张。分发衍生内容时保留原版权和许可。上游 MIT 许可不授予 ASD 官方标准全文或词典的复制许可；本包不包含该词典。[上游许可原文](https://github.com/danyuchn/asd-ste100-skill/blob/32511c6992ecb5f1971e46a2943f2e6adceedafe/LICENSE)

### MIT License

Copyright (c) 2026 Dustin Yuchen Teng

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
