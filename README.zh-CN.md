# skills

[English](README.md) · [简体中文](README.zh-CN.md)

[@Loner1024](https://github.com/Loner1024) 的 agent skill 集合。每个 skill 都是一个自洽目录，遵循
[Agent Skills 规范](https://agentskills.io)：一个带 YAML frontmatter 的 `SKILL.md`，加上它自己需要的
references、assets 和 scripts。

一条命令即可装进 Claude Code、Codex、Cursor、Droid、OpenCode、Zed 或
[其他支持的 agent](https://github.com/vercel-labs/skills#supported-agents)。

[![skills.sh](https://skills.sh/b/Loner1024/skills)](https://skills.sh/Loner1024/skills)

## 安装

```bash
# 先看仓库里有什么
npx skills add Loner1024/skills --list

# 交互式：自己挑 skill、挑 agent、挑安装范围
npx skills add Loner1024/skills

# 非交互：装一个 skill，全局范围，指定 agent
npx skills add Loner1024/skills --skill tech-diagrams -g -a claude-code -a codex -a droid -y

# 全部 skill 装到你装过的所有 agent
npx skills add Loner1024/skills --all
```

不安装，只在单次会话里加载一个 skill：

```bash
npx skills use Loner1024/skills@tech-diagrams | claude
```

之后用 `npx skills update -g` 更新，用 `npx skills remove <skill>` 卸载。

## Skill 清单

| Skill | 做什么 | 依赖 |
| --- | --- | --- |
| [`tech-diagrams`](skills/tech-diagrams) | 产出可发布级技术图表：手写 SVG 加自包含 HTML 预览，交付前自动 lint。覆盖 14 类图，从架构拓扑到序列图、状态机、基准条形、终端窗口框架。同时决定**什么时候不该画图**。 | `python3`、`rsvg-convert`、Chrome/Chromium（渲染 HTML 预览用） |
| [`architecture-ablation`](skills/architecture-ablation) | 通过移除或替换某个组件、层次或机制，并和基线对照，检验它到底贡献了什么。把"这层抽象是不是多余的"变成一个可以复核的证据结论。 | 无 |

## tech-diagrams

agent 画的图大多是 Mermaid 方块堆：所有盒子一样大，箭头从空白处起笔，标签被盒子盖住。这个 skill
走的是相反的路——它的规则来自逐篇精读 Linear、Cursor、Vercel、Anthropic、OpenAI 技术写作里**实际怎么放图**。
逐家的原始证据在 [`research/`](research)，但 skill 本身不读它。

每张图交付两个产物：

| 产物 | 用途 |
| --- | --- |
| `<slug>.html` | 自包含预览：内联 SVG 加内联设计 token，无外部请求，离线可开 |
| `<slug>.svg` | 单文件交付件，嵌 README、文档、博客或幻灯片 |

另外附一行 caption（同时就是图片的 `alt`），以及一句话说明这张图**故意省掉了什么**。

![skill 画的分片查询架构图](skills/tech-diagrams/examples/sharded-lookup.png)

![带重试路径的序列图](skills/tech-diagrams/examples/sequence-retry.png)

### 它强制什么

- **一张图只讲一个结论**，结论写在 caption 里，caption 同时是 `alt`。
- **只有正文承载不了结构时才画**：超过三个对象的对比、多步因果、随时间变化的状态、需要看排名的测量。
  否则它会说"用表格"然后停下。
- **几何预算**：节点最多 9 个，焦点元素一个，4px 网格，圆角 ≤ 8px，线宽 1px，只允许正交连线，字号最小 11px。
- **连线卫生**：每个箭头两端都落在看得见的东西上（盒子边框、生命线、起点圆点），箭头不指向角落，
  线不穿过非端点的盒子，短箭头必须带标签。
- **一张图一个强调色。** 禁止渐变、发光、投影和装饰性 chrome。
- **对比度与中文字体栈由脚本校验**，避免栅格化时静默 tofu。

### 使用流程

```bash
cd skills/tech-diagrams

# 1. 从模板开始（默认 register 是 technical dark）
mkdir -p figures && cp assets/template-dark.html figures/my-figure.html

# 2. 先校验源文件，再看渲染结果
python3 scripts/self_check.py figures/my-figure.html --strict
./scripts/render.sh figures/my-figure.html --scale 2

# 3. 拿源文件和它自己的渲染结果对校（能查出空白图和密度过低）
./scripts/render.sh figures/my-figure.svg --scale 2
python3 scripts/self_check.py figures/my-figure.svg --png figures/my-figure.png

# 改过 reference 文档后，证明里面的代码片段仍然过同一套 lint
python3 scripts/lint_docs.py
```

渲染需要 `rsvg-convert`（macOS 上 `brew install librsvg`）处理 SVG，以及无头 Chrome/Chromium 处理
HTML 预览。linter 只用 Python 标准库。图表是在 macOS 上创作和渲染的；其他平台上 `rsvg-convert` 和
Chrome 的字体解析行为不同，所以中文字体栈是显式列出的。

### 老实说它的边界

linter 只查能查的部分。视觉手感、线宽、这张图到底有没有说服力，仍然需要人眼看一眼 PNG。如果 agent 在某次
会话里无法读图，它会直说，并把渲染结果交给你做最终确认。

## architecture-ablation

问 agent「这个队列有必要吗」，你通常得到的是一个观点。这个 skill 逼它给对照：先锁定必须守住的约束，再每次
只移除或替换一个机制，并把结论归因到带标签的证据上。

它强制了几件靠辩论通常会跳过的动作：

- **先有基线再谈删除。** 约束、关键调用路径、状态归属都要先写下来。如果基线在相关场景下本来就失败，那就
  记录为失败——「两个方案都失败」不算简化通过。
- **假设用统一格式写**，方便追踪：`[假设] <陈述> → 若不成立则影响 <哪个结论>`。
- **用证据标签代替自信的叙述。** 每条结论都标 `实测` / `设计推演` / `待验证`，不允许把预计结果写成已经通过。
- **四种结论，不是两种**：删除或替换、保留、延后引入、待验证。选「保留」必须写出没有它会失败的场景；选
  「延后引入」必须写出把它请回来的可观察条件。
- **单独删都过，推不出一起删也过。** 职责重叠的机制要再做组合复验。
- **复杂度转移了就不算减少。** 最后要确认它有没有跑到调用方、运维流程或另一份状态里去。

用户的目标是约束，不是变量：skill 可以指出某个既定技术栈或边界的代价，但不能靠改变用户的目标去换一个更简单
的方案。局部重构和 ML 模型消融明确不在范围内。

交付的是推荐方案加可复核的证据；单项决策建议直接融进现有设计文档或 ADR，不另生成重复报告。

## 仓库结构

```
research/                        出处材料，不属于任何 skill
  FINDINGS.md                    五家怎么做图，逐家记录，带原始链接
  TAXONOMY.md                    规则背后的决策分类与工具路线调研
skills/
  tech-diagrams/
    SKILL.md                     入口：流程、类型路由表、硬规则
    references/                  when-to-draw · registers · primitives · type-* · verification · export
    assets/                      tokens.css 加深色/浅色起始模板
    scripts/                     render.sh · self_check.py · lint_docs.py
    examples/                    七张成品图，覆盖四个内容族
  architecture-ablation/
    SKILL.md                     入口：基线、消融循环、决策表
    agents/openai.yaml           界面元数据：显示名、触发词、不触发词
```

`skills/<name>/` 就是安装单元：`npx skills` 复制的正是这一整个目录。这里的每个 skill 都自洽，不读自己文件夹
之外的任何文件，所以从仓库 clone 用和安装后用，行为完全一致。

`research/` 是有意留下的例外：它放在仓库里是为了让人判断某条规则值不值得信，`skills/` 下面没有任何文件读它。
删掉整个目录，所有 skill 照常工作。它用中文写；真正运行用的规则是 `skills/tech-diagrams/references/` 下的英文文件。

## 新增一个 skill

```
skills/<skill-name>/SKILL.md     # frontmatter 要有 name 和 description；名字用小写连字符
```

提交推送后立刻可安装：`npx skills add Loner1024/skills --list` 会自动发现 `skills/` 下的一切。每个 skill
保持自洽，只有运行时才需要的东西放进它自己的文件夹，能用脚本机械校验的规则就别只写成文字。

## 许可

[MIT](LICENSE)。第三方材料在出现处注明出处。
