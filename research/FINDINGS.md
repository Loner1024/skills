> 调研记录（中文）。这份笔记不做规范，只作出处：它记录的是这五家**实际怎么画**，以及每条结论的来源与实测数据。
> `tech-diagrams` skill 的运行规则在 `skills/tech-diagrams/references/`，skill 本身**不依赖本目录**——本目录删掉不影响 skill 任何行为。

# 优质技术图表调研：Linear / Cursor / Vercel / Anthropic / OpenAI

调研日期：2026-09-15。目标是提炼"技术博客级"图表的**房屋规则（house rules）**，作为 `tech-diagrams` skill 的设计依据。

## 0. 方法与证据

- 对五家官方博客/文档逐篇抓取 HTML 与素材，记录：图的类型与顺序、alt/caption 原文、素材 URL 与尺寸、字体与 CSS 变量、明暗变体、动效。
- 通过子代理并行完成五家深挖，关键结论由我在主流程复核（例：Vercel CDN 一文的图序、caption==alt、真表格均已逐条核对）。
- **未验证项**已单独标注（见 §6）。特别是：**本次执行环境不支持图像输入**，因此所有风格描述均来自实测的像素/调色板/标签文本/HTML/CSS，而非"看图说话"。图表的最终审美判断必须由人眼复核。

## 1. 五家的图表人格

| | 画布与主题 | 强调色 | 字体 | 图与文的关系 | 标志性做法 |
|---|---|---|---|---|---|
| **Linear** | 深色优先（`<html data-theme="dark">`，亮/暗两张 hero 都 `fetchPriority="high"` preload） | 低饱和单一蓝（品牌页："a subtle desaturated blue"） | Inter / Inter Display / mono（`InterVariable.woff2`，static.linear.app） | 正文先陈述主张，再"如下所示"引出图；图与 alt 冗余 | 2:1–2.2:1 超宽横幅（3904×1920/1760）；`<figure data-wide>` 内 `hide-mobile`/`show-mobile` 双图；**无 figcaption**；数据图必配完整数据表 + `N =` 脚注（linear.app/data）；资产为内容寻址（`webassets.linear.app/images/.../<40-hex>.png?q=95&auto=format&dpr=2`）；视频是 `<video poster src=*.mp4>` |
| **Cursor** | 纯黑/纯白双主题，资产成对 `-light.png`/`-dark.png` | 单一橙 `#f54e00`（明暗两主题同值） | Cursor Gothic / Cursor Display + Berkeley Mono | **图标题即结论**（"Mixture-of-Kittens achieves up to 2.37x higher…"）+ 星号脚注 | 手写 inline SVG 协议图：`role="img"` + 完整 aria-label（"Animated diagram of a Git history walk…"）、命名类（`viz-label`、`viz-kv-key`）；**步进式模拟器**替代静态序列图（3PC、WAL race，带 Playback speed / Back / Next）；图表块用 `--bc-*` CSS 变量 + `[data-theme=dark]` / `prefers-color-scheme` 双主题；阶段图 1080×500 / 920×430；hero 循环动画 1200×630 |
| **Vercel** | 浅色 + 必配 dark 变体（并常配 mobile 变体） | 单色为主（Geist 十个色阶，用色极少） | Geist Sans / Geist Mono | 生命周期/管线图先于文字；精确数字用真 HTML 表格 | 素材编号命名（`01-request-path-before-after.png`、`02-…`、`03-…`）；**caption 与 alt 逐字相同**且含 takeaway；宽幅 hero 用 `w=3840`；明令拒绝渐变/发光/条纹/纹理/玻璃/装饰阴影/卡中卡（vercel.com/design.md）；"Prefer direct labels to legends" |
| **Anthropic** | 暖纸底 `#faf9f5`（正文）/#F3F2EC/#F1EEE7（图内实测） | 单一 clay/rose（`#d97757` / `#DD726F`） | Anthropic Serif / Sans / Mono（专有，无公开 webfont） | **每个命名模式恰好一张图**（BEA：8 模式 8 图）；prose 负责"何时用"，bullets 负责例子 | 框内只放名词短语（"Action"、"Feedback"、"Query"、"Call"）；循环条件写在弧线上（"Until tasks clear"、"Until tests pass"）；决策节点带显式出口（"(x) Exit loop"）；权衡一律交给表格与曲线；扁平填充、无渐变、无网格纹理（像素扫描实测） |
| **OpenAI** | 浅色；图表是 DOM/SVG 而非位图 | 近乎单色（克制） | OpenAI Sans + mono（小写连字符标识符：`habitat-service`、`gpt-5-main`） | `Figure NN · Title` + 一两句说明 + 斜体 caveat | 工程博客用**可交互动画**（Pause / Replay / 步骤 01-02-03，如 Habitat 篇）；文档用 `<picture>` 响应式（1400 桌面 / 680 移动）；大数字三连（"70M+ requests/second · 1B+ people each week · 500 PB+ data"）；虚线箭头语义在正文说明（"The dashed arrow applies only when…"） |

## 2. 跨家共性：优质技术图表的 12 条房屋规则

1. **图不承担论证，只承担证据**。五家都让标题/说明句给出结论，图负责"看得见"；caption 常直接给出 takeaway。
2. **一个强调色，焦点 ≤2 个元素**。其余一律中性（发丝线 + 灰阶文本）。
3. **禁止装饰**：渐变、发光、blob、玻璃、装饰阴影、装饰性网格、卡中卡——Vercel 把这条写成了硬性 reject 清单。
4. **几何纪律**：圆角小（4–8px 为主，Linear 8px、Vercel 4px）、1px 发丝线、正交连线；**优先直接标注而非图例**。
5. **字体三层**：无衬线（标签/正文）+ 等宽（标识符、命令、键、端口、数值）+ 可选衬线或 display（标题）。等宽只服务技术内容，不做"开发感"装饰。
6. **标识符写实**：节点写真实名字（`Postgres`、`Turbopuffer`、`420 → 421–500`、`p99`），不写抽象名词。
7. **短词标签 + 边上有条件**：方框内只有名词短语；分支/循环条件写在箭头上。
8. **密度预算**：Anthropic 2401×1000 只放 3 个框；Vercel/Linear 用 2:1 宽幅；超预算就拆"总览 + 细节"。
9. **表格与图表分工明确**：精确多属性 → 真表格；数量对比 → 条形；趋势 → 折线/分位；权衡 → 曲线或象限散点。
10. **明暗成对 + 响应式成对**是共同要求（Anthropic 是唯一例外，而它自己的 `alt=""` 也是唯一明显的无障碍反例）。
11. **动效是可选上层**：Linear 用 mp4 loop、Cursor 用 hero 视频 + 步进 SVG、OpenAI 用交互动画、Anthropic 完全不用。
12. **一致性来自模板而非自由发挥**：caption 位置、字号阶梯、图序编号、页面留白都成体系。

## 3. 生产事实（决定我们怎么做）

- **素材形态**：Linear/Vercel/Anthropic 博客正文图基本是**位图 PNG**（Linear 内容寻址 + `dpr=2`；Vercel 走 Contentful + `/_next/image?w=1920|3840&q=75|95`；Anthropic 走 `www-cdn.anthropic.com/...-<W>x<H>.png` + `/_next/image?w=3840&q=75`）。Cursor/OpenAI 的**图表**已是 DOM/SVG（Cursor 图表由客户端 JS 绘制，SSR 里挂载点为空；OpenAI 的 GPT-5 图表文本可被文本抓取提取到坐标轴与数据标签）。
- **代码渲染图**：五家博客正文**均无 Mermaid 渲染**。Anthropic cookbook 内有 3 个 ` ```mermaid ` 文件；Claude Code 文档带品牌化 Mermaid 主题（`.mermaid` 网格纸底、`.dark .mermaid` 深色）。OpenAI 取样页未见 Mermaid。
- **明暗与响应式**：Cursor（`-light/-dark` 成对 + 主题变量）、Vercel（`-dark` 变体 + mobile 变体）、Linear（亮暗 hero 双份 + `hide-mobile/show-mobile` 双图）、OpenAI（docs 用 `<picture>` 双尺寸）。Anthropic 无明暗变体。
- **无障碍**：Vercel 的 caption 与 alt 逐字相同；Cursor 用 `role="region" aria-label="<标题> …"` + SVG `role="img" aria-label`；Linear 用描述句 alt。**Anthropic 的旗舰图 `alt=""`**——这说明"大厂做法"不能照抄。
- **动效**：Linear/Vercel 用 `<video>`（mp4，poster 为 PNG），Cursor 另有 webm + GIF 兜底；OpenAI 是自定义交互组件。

## 4. 生态对照：怎么"画"（工具路线）

- **实测（DevelopersIO）**：SVG+cairosvg 视觉上限最高、需处理字体（日文曾 tofu）；Mermaid 布局最稳但观感"扁平/工具感"；Excalidraw 手绘风不适合技术博客、文本易溢出。结论：**人类描述成本三者相同，决定因素是成图质量**；有效做法是"语义化配色 + `<defs>` 模板 + 命名设计模式 + 复杂度上限 + 转换后回看图片"。
- **现有技能生态**：`diagram-design`（40 类、自包含 HTML+SVG、反 AI-slop 清单、连接线六条硬规则、复杂度预算、明暗变体）、`drawio-skill`/`excalidraw-diagram-skill`（可继续手改的源文件形态）、`mermaid-tools`（Markdown 内源码 → 高分辨率 PNG）。
- **本机可用**：Chrome 153 headless、`rsvg-convert` 2.63（cairo/pango/harfbuzz/fontconfig）、ImageMagick；字体 **Inter 已安装**，等宽有 SF Mono / Menlo，中文字体 fontconfig 可见 Hiragino Sans / Heiti SC（**PingFang 不在 fontconfig 注册**，rsvg 与 Chrome 行为会不同）。
- **本机网络注意**：`curl` 在本环境 TLS 失败，`python3 urllib` 可用——脚本一律用 python3 取网络资源。

## 5. 对我们 skill 的直接含义

1. 默认走 **SVG 作者路线**（视觉上限最高、可版本管理、可 diff），渲染校验用 `rsvg-convert` / Chrome headless。
2. **明暗成对**与 **caption=alt** 作为默认交付要求，而不是可选项。
3. 交付"**自包含 HTML 预览 + 单文件 SVG**"（用户已确认），HTML 承担排版与字体回退，SVG 承担嵌入与分发。
4. 必须有**密度预算、连接线规则、反 slop 清单**，否则模型输出会漂移成"通用 SaaS 风"。
5. 中文标签需要显式字体栈与独立的渲染验证（tofu 是真实风险）。
6. 校验环节不能只靠"看一眼"：要把可自动化的部分（几何、aria、预算、渲染冒烟）交给脚本，人眼只做最终审美确认。

## 6. 局限与未验证项

- 执行环境不支持图像输入：**主观质量（线宽手感、光学对齐）未经人眼确认**；调色板、尺寸、标签文本、结构均为实测。
- Anthropic 图表的绘制工具、Cursor 图表运行时库（`builder-export-chart` 之外无第三方库痕迹）、Vercel 图表是否曾有明暗差异、OpenAI 基准图是否绘制置信区间，均**无公开证据**。
- 五家均未公开其图表设计规范；Linear/Anthropic 的品牌页只覆盖 logo 与商标，不含图表规范。

## 7. 主要参考

- https://linear.app/now/rebuilding-delta-sync-read-path · https://linear.app/now/behind-the-latest-design-refresh · https://linear.app/brand · https://linear.app/data
- https://cursor.com/blog/kernels · https://cursor.com/blog/mixture-of-kittens · https://cursor.com/blog/git-at-any-scale · https://cursor.com/blog/how-cursor-router-works
- https://vercel.com/blog/how-we-cut-cdn-metadata-lookup-latency-by-91-percent · https://vercel.com/blog/life-of-a-vercel-request-what-happens-when-a-user-presses-enter · https://vercel.com/design.md · https://vercel.com/geist/introduction
- https://www.anthropic.com/engineering/building-effective-agents · https://www.anthropic.com/engineering/multi-agent-research-system · https://www.anthropic.com/engineering/how-we-contain-claude · https://code.claude.com/docs/en/how-claude-code-works
- https://openai.com/index/unrolling-the-codex-agent-loop/ · https://openai.com/index/scaling-storage-one-billion-users-part-one/ · https://openai.com/index/introducing-gpt-5/ · https://developers.openai.com/api/docs/guides/agents-api/architecture
- https://dev.classmethod.jp/en/articles/build-svg-diagram-skill-for-claude-code/ · https://github.com/cathrynlavery/diagram-design · https://www.mintlify.com/library/when-and-how-to-use-diagrams
