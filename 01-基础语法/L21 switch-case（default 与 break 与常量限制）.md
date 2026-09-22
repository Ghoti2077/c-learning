---
title: "L21 switch-case（default 是什么、break 到底中断谁、类型与常量限制）"
type: lesson
lesson: L21
date: 2026-09-21
tags: [C语言, 基础语法, 分支, switch, break, default]
status: 已完成
---
# L21 switch-case：`default` 是什么、`break` 到底中断谁

- 日期：2026-09-21
- 来源：我学 switch 时自己总结的四句话 + 疑问（`default` 干嘛的）
- 素材：翁恺《C语言程序设计》"switch-case / break"那节课件 + 我的 switch 版问候语程序 + AI 实测
- 标签：`#C语言` `#基础语法` `#分支` `#switch` `#break` `#default`

> **一句话总结**：
> **`switch` = 电梯**：先算出"几楼"（控制表达式的值），然后**直接跳到那一层**。
> 跳过去之后**开始顺着往下走**——`break` 才是"到这儿停、出电梯"。没有 `break` 就会一路穿透下去。
> **`default` = "剩下的所有情况"**（等价于 if-else 链最后的 `else`）。

---

## 1. 先看结构 + 打比方

![[L21-课件 switch-case 结构.png]]

```c
switch (控制表达式) {
case 常量1:
    语句...
    break;
case 常量2:
    语句...
    break;
default:
    语句...
    break;
}
```

**打比方——电梯**：

| 代码 | 电梯里的对应物 |
|---|---|
| `switch (type)` | 按了电梯里的**目标楼层**（先算出 type 是几） |
| `case 1:` `case 2:` | **楼层号牌**（只是"位置路标"） |
| `default:` | **"其他楼层"**（没按到任何存在的楼层就走这儿） |
| `break;` | **到站停下、走出电梯** |
| 不写 `break` | **电梯不停，继续往下一层跑**（这就是"穿透"） |

课件原话我也抄下来了：**"switch 语句可以看作是一种基于计算的跳转……分支标号只是说明 switch 内部位置的路标。在执行完分支中的最后一条语句后，如果后面没有 break，就会顺序执行到下面的 case 里去，直到遇到一个 break，或者 switch 结束为止。"**

## 2. 我那四句话，逐条批改

| 我的说法 | 判定 | 正确的说法 |
|---|---|---|
| 「`break` 是用来**中断前面的 case** 的」 | ⚠️ **半对** | `break` 的作用是**跳出整个 `switch`**（结束这条 switch 语句），不是"中断某个 case"。它的实际效果：**阻止继续往下穿透**。没有它，程序会一路执行下面的 case（实测见第 3 节） |
| 「`default` 的功能我还不太明白」 | 🔧 **本课补上** | `default` = **"剩下的所有情况"**，等价于 if-else 链最后的 `else`：**所有 case 都不匹配时才执行它**。它可以**省略**（那就什么都不做）；位置也**不必须在最后**——它只是个"标签"，放中间照样是"没匹配到才去" |
| 「`switch` 语句必须是 `int` 类型」 | ⚠️ **不够准** | 控制表达式必须是**整型**：`char` / `short` / `int` / `long`（枚举也行）**统统可以**；**`float` / `double` 不行**，字符串也不行 |
| 「`case` 后面可以是表达式，但必须是常数」 | ⚠️ **半对** | 只能放**整型常量表达式**（编译期就能算出确定值的）：`1`、`'a'`、`2 + 3` 都行；**变量不行，连 `const int` 变量都不行**（这点最反直觉，见第 4 节） |

## 3. 实测：`break` 到底管什么（穿透现象）

![[L21-课件 break 说明（穿透）.png]]

我故意让 `case 1` **不写** `break`：

```c
switch (t)
{
case 1:
    printf("A（case 1，没有 break）\n");
case 2:
    printf("B（case 2，有 break）\n");
    break;
case 3:
    printf("C（case 3，有 break）\n");
    break;
default:
    printf("D（default）\n");
    break;
}
```

**实测输出**：

| t | 输出 | 说明 |
|---|---|---|
| **1** | `A` + **`B`** | 跳到 case 1 → 打印 A → **没 break，继续往下执行 case 2** → 打印 B → 遇到 break 才停 |
| **2** | `B` | 直接跳 case 2 → 打印 B → break 停 |
| **3** | `C` | 同上 |
| **9** | `D` | 没有匹配的 case → 走 default |

> **这就是 `break` 的真正作用**：**"到此为止、跳出 switch"**。
> 反过来说——**忘了写 `break`，代码不会报错，只会"多做一遍事"**，这种 bug 最阴。

## 4. ⚠️ 最关键的一条：`case` 后面连 `const int` 变量都不行

刚学完 `const` 的我，第一反应肯定是"`const` 是常量，那 `case ONE:` 总行了吧"。**C 语言里不行。** 实测：

```c
const int ONE = 1;
int type = 1;
switch (type)
{
case ONE:            /* ← 想用 const 变量当标签 */
    ...
}
```

| 编译器 | 报错原文 |
|---|---|
| **gcc** | `error: case label does not reduce to an integer constant` |
| **VS（我实测 cl.exe）** | `error C2051: case 表达式不是常量` |

**同理**（都实测过）：

| 写法 | 结果 |
|---|---|
| `case 2 + 3:` | ✅ 合法（常量表达式，编译期算出 5） |
| `case 'a':` | ✅ 合法（字符常量就是整型常量） |
| `case a:`（`a` 是变量） | ❌ `error: case label does not reduce to an integer constant` / VS `C2051` |
| `case ONE:`（`ONE` 是 `const int`） | ❌ **同上**（C 不是 C++！C++ 允许，C 不允许） |
| `switch (ch)`（`ch` 是 `char`） | ✅ 合法（测过：输入 `'b'` → 正确命中 `case 'b'`） |
| `switch (f)`（`f` 是 `float`） | ❌ gcc：`error: switch quantity not an integer`；VS：`error C2050: switch 表达式不是整型` |

**为什么？** 因为 `case` 标签要在**编译阶段**就确定下来（编译器要拿它们去建"跳转表"）；而 `const int` 在 C 里虽然不能改，**但它仍然是"变量"**，编译器不当它是编译期常量。**`case` 后面只能写"编译期就板上钉钉的整型常量"**（字面量、字符常量、常量表达式）。

> 顺带答一下弹幕里的疑问（我看到的）："试过了字符型常量不可以" —— **其实 `char` 是可以的**（`case 'a':` 合法，我实测过）。那位同学大概是别的地方写错了。

## 5. 顺便：故意"穿透"是一种正常用法

课件里那一小段就是**故意不写 break**的：

```c
switch (type)
{
case 1:
case 2:                       /* ← case 1 和 case 2 共用下面这段 */
    printf("你好\n");
    break;
case 3:
    printf("晚上好\n");
case 4:
    printf("再见\n");
    break;
default:
    printf("啊，什么啊？\n");
    break;
}
```

- `case 1:` 后面**故意空着**——`type == 1` 时穿透到 `case 2`，两个值**共用**同一段代码。这是**标准技巧**（比写两遍 `printf` 干净）。
- `case 3:` 后面也**没写 break** → `type == 3` 会打印"晚上好"**再加**"再见"。这多半是**漏写**（课件就是这么演示"没有 break 会怎样"的）。

**判断标准**：**空 case 叠在一起 = 故意共用；case 里有语句却没 break = 大概率是 bug。**

## 6. 我的程序核对（switch 版问候语）

![[L21-我的 switch 版问候语程序.png]]

```c
switch (type) {
case 1:
    printf("你好");
    break;
case 2:
    printf("早上好");
    break;
case 3:
    printf("晚上好");
    break;
case 4:
    printf("再见");
    break;
default:
    printf("啊神魔啊");
    break;
}
```

| 检查点 | 判定 |
|---|---|
| `switch (type)`，`type` 是 int | ✅ 合法 |
| 每个 `case` 后面都跟了 `break`（包括 default） | ✅ **一个都没漏**，很棒 |
| 最后有 `default` 兜底 | ✅ |
| `case` 标签用的都是字面量 `1/2/3/4` | ✅ 合法 |
| 错误列表 0 错误 0 警告 | ✅ 编译干净 |
| **5 个 `printf` 全都没写 `\n`** | ⚠️ **第 3 次犯**（上次是"请输入金额93"、再上次是"你好1"） |

**AI 实测**（补上 `\n` 之后编译运行）：

| 输入 | 输出 |
|---|---|
| 1 | `你好` |
| 4 | `再见` |
| 9 | `啊神魔啊` |

**逻辑全对** ✅。**唯一的问题还是 `\n`**——而且这次编译器给了 **0 错误 0 警告**，说明"漏 `\n`"这事**编译器根本不提醒**，只能靠自己扫。

> **从今天起的固定动作**：一段代码写完，**眼睛扫一遍所有 `printf` 结尾有没有 `\n`**，再点运行。

## 7. `switch` 和 `else if` 该怎么选

| 情况 | 用什么 |
|---|---|
| 判断**某个变量等于几个固定值**（1、2、3、'a'、'q'） | ✅ **`switch`** 更清楚、更整齐（课件弹幕里那句"做项目的时候多用这个少用 else-if"就是这个意思） |
| 判断**范围**（`score >= 90`、`x < 0`） | ❌ `switch` 干不了（`case` 只能是点值）→ 只能用 `if / else if` |
| 判断**多个变量的组合条件**（`a > 0 && b < 5`） | ❌ 也只能用 `if` |

**记忆**：`switch` 只会"**跳到某个值**"，不会"**算范围**"。

## 8. 复习题（先自己答）

1. `break` 的作用到底什么？不写会怎样？
2. `default` 是什么意思？可以省略吗？必须写在最后吗？
3. 下面哪个能当 `case` 的标签？为什么？
   ```c
   int a = 1;
   const int ONE = 1;
   case 1:        case a:        case ONE:        case 2 + 3:
   ```
4. `switch (f)` 里的 `f` 如果是 `double`，能编译吗？为什么？
5. `case 1:` 后面故意不写 `break`、直接接 `case 2:`，这是 bug 还是技巧？

> [!question]- 参考答案（先自己答完再点开）
>
> 1. `break` 的作用是**跳出整个 `switch`**（结束这条 switch 语句），效果就是"阻止继续往下穿透"。**不写 `break`**：跳到匹配的 case 后会**继续顺序执行下面的 case**，直到遇到 `break` 或 switch 结束（实测 `t=1` 时打印了 A 和 B）。
> 2. `default` = **"剩下的所有情况"**，等价于 if-else 链最后的 `else`：**所有 case 都不匹配才执行**。**可以省略**（那就什么都不做）。**不必写在最后**——它只是个标签，放中间照样是"没匹配到才去"（实测：default 放中间，`type=2` 仍进 `case 2`、`type=9` 才进 default）。
> 3. `case 1:` ✅（字面量）、`case 2 + 3:` ✅（常量表达式）；`case a:` ❌（变量）；`case ONE:` ❌（`const int` 在 C 里**仍是变量**，不是编译期常量）→ 报 `case label does not reduce to an integer constant` / VS `C2051`。
> 4. **不能编译。** `switch` 的控制表达式必须是**整型**（char/short/int/long/枚举）；`double` 报 `error: switch quantity not an integer` / VS `C2050: switch 表达式不是整型`。
> 5. **是技巧**（故意"穿透"）：`case 1:` 空着 = 让 1 和 2 **共用**下面那段代码。**判断标准**：空 case 叠在一起 = 故意共用；**case 里有语句却没有 `break`** = 大概率是漏写。

## 9. 嵌入式视角

- **`switch` 在单片机里天天用**：解析"命令字"（收到 `0x01` 点亮、`0x02` 熄灭）、按键映射、通信协议的帧类型分发（`switch (frame_type)`）。这类判断都是**"等值跳转"**，正是 `switch` 的主场。
- **编译器可能把 `case` 密集的 switch 编译成"跳转表"**（一张地址表 + 一次查表跳转）——比一串 `if-else` **更快、更省空间**。这也解释了为什么 `case` 必须是编译期常量：**要建表**。
- **漏 `break` 在嵌入式里最要命**：状态机写成 `switch (state)` 时漏一个 `break`，就会"从一个状态直接穿到下一个状态"，表现为"设备偶尔自己跳状态"——**而编译器不会报错**（最多在很高的警告等级下提示）。工程规范通常要求：**每个 case 结尾一律 `break`，要用穿透必须写注释说明**。
- **`default` 一定要写**：处理"收到意料之外的命令字"（可能来自干扰、通信错误）。默认分支里通常做**报错/复位/丢弃**，而不是啥都不干。

## 相关
- [[L20 else if 级联 与 单一出口]]（多个分支的选择：级联 vs switch）
- [[L19 const 常量 与 else 匹配规则]]（`const` 是"只读变量"，**不是**编译期常量 ← 本课第 4 节就是它挖的坑）
- [[L18 缩进与花括号（if 管一条语句）]]（`{}` 与语句块）
- [[L15 if语句与关系运算符]]（`==` 与 `=` 的区别）
- [[❌ 我的易错点清单]]
