---
title: "🚨 VS 常见报错速查（都是我亲手踩过的）"
type: tool
---
# 🚨 VS 常见报错速查（都是我亲手踩过的）

> 专门记录**我在 VS 里真实撞到的报错** + 原因 + 怎么改。撞到新错就往这儿加。
> 遇到报错先在这里搜一眼，别慌。

---

## ⭐ C4996：`'scanf': This function or variable may be unsafe`

**我撞到的场景**（2026-09-17，写"时间差计算器"时）：代码用了 `scanf`，VS 直接报 2 个错误：

```
C4996 'scanf': This function or variable may be unsafe.
Consider using scanf_s instead.
To disable deprecation, use _CRT_SECURE_NO_WARNINGS.
```

### 这是什么意思？

**这不是我的代码写错了，是 VS 觉得 `scanf` 不安全。**

- `scanf("%d", &x)` 读字符串时**不知道自己能读多少**，如果用户输入很多，就可能**冲出数组、踩坏内存**（缓冲区溢出）。
- VS 的官方态度：**"这个函数有风险，我不想让你用"** → 所以直接当**错误**拦住你（在别的编译器比如 gcc 上，这事根本不算错）。

### 怎么改（三种办法，推荐第 1 种）

**① 在文件的最上面（所有 `#include` 之前）加一行：**

```c
#define _CRT_SECURE_NO_WARNINGS 1     // ← 必须是【第一行】
#include <stdio.h>
#include <string.h>
#include <stdbool.h>

int main()
{
    int hour1, minute1;
    scanf("%d %d", &hour1, &minute1);     // 现在不报错了
    ...
}
```

**⚠️ 唯一的坑：这行必须写在所有 `#include` 的【前面】。**

> 为什么？因为 `stdio.h` 里有一段"检查这个宏有没有定义"的代码：
> **如果宏在 `#include` 之前定义好了，头文件就认输、不报警告；如果写在后面，头文件执行检查时还看不到它，照样报错。**（第 2 节有实测证据）

**② 改项目属性**（不用每个文件加宏，一次设置整项目有效）：
`项目 → 属性 → C/C++ → 预处理器 → 预处理器定义 → 编辑 → 加一行 _CRT_SECURE_NO_WARNINGS`

**③ 换成 `scanf_s`** —— ❌ **不推荐**：`scanf_s` 是微软自己家的函数，**gcc、单片机的编译器都不认**。以后转嵌入式会白学，所以**别养成习惯**。

### 📌 顺手记住的道理（这条以后天天用）

> **gcc 编得过，不代表 VS 编得过；反过来也一样。**
> 同一份代码在不同编译器上的"宽容度"不同——**这不是你写错了，是工具的标准不同**。

---

## 📋 我踩过的报错总表

| 报错（大致长这样） | 我当时的场景 | 什么意思 / 怎么改 | 出处 |
|---|---|---|---|
| `C4996 'scanf' ... unsafe` | 用了 `scanf` | VS 的老规矩：文件第一行加 `#define _CRT_SECURE_NO_WARNINGS 1` | 本篇 |
| `C4067 预处理器指令后有意外标记-应输入换行符` | 三个 `#include` **挤在同一行** | **预处理指令必须一行一条**，挤一起则后面的失效 | [[L09 数据类型与布尔类型]] |
| `C2065 / E0020 未声明的标识符 "true"` | 上面那条导致的 | `true` 在 `<stdbool.h>` 里，include 失效就用不了 | [[L09 数据类型与布尔类型]] |
| `LNK2019 无法解析的外部符号 _main` | 没有（或漏了）`main` | **链接**阶段找不到入口。程序必须有且只有一个 `main` | [[L01 main函数与程序框架]] |
| `fatal error: stadio.h: No such file or directory` | 头文件名拼错/漏 `.h` | 文件名必须**一字不差**：`stdio.h` | [[L02 库函数与头文件（printf、stdio.h、命名）]] |
| `error: 'return0' undeclared` | 写成 `return0;` | `return` 和 `0` 之间要有**空格**，末尾要有**分号**：`return 0;` | [[L01 main函数与程序框架]] |
| `expected ';' before '}' token` | 语句末尾漏分号（或写成中文分号 `；`） | 补上**英文分号** `;` | [[L01 main函数与程序框架]] |
| `empty character constant` | 写了 `''`（单引号里什么都没有） | 单引号里要有**一个**字符；空格也算：`' '` | [[L03 字符与ASCII码]] |
| `multi-character character constant` | 写了 `'ab'` | 单引号只能放**一个**字符，多字符用双引号（字符串） | [[L03 字符与ASCII码]] |
| `missing terminating " character` | 字符串**写成两行**了 | `"` 到 `"` 必须在同一行，要换行就打 `\n` | [[L08 注释（不能嵌套的原因）]] |
| `unknown type name`（嵌套注释那题） | `/* */` 里又嵌了 `/* */` | 第一个 `*/` 就结束了注释，后面的变成代码 | [[L08 注释（不能嵌套的原因）]] |
| `expected expression before 'int'` | 写了 `sizeof int` | **操作数是类型名时必须加括号**：`sizeof(int)` | [[L10 sizeof（关键字、操作符、字节与比特）]] |
| `both 'unsigned' and 'float' in declaration specifiers` | 写了 `unsigned float` | `signed`/`unsigned` **只能修饰字符型和整型**，浮点型不行 | [[L11 signed和unsigned（float为什么不行）]] |
| `lvalue required as increment operand` | 写了 `(a + 1)++;` | `++`/`--` **只能作用在变量上**，算式不是变量 | [[L12 复合赋值、递增递减、前缀与后缀]] |
| `expected expression before '=' token` | 写了 `total + = 5;` | `+=` 是**一个**运算符，**中间不能有空格** | [[L12 复合赋值、递增递减、前缀与后缀]] |
| `warning: operation on 'a' may be undefined` | 一句里对同一变量自增两次 | **未定义行为**，改掉：一个表达式里同一变量只自增一次 | [[L12 复合赋值、递增递减、前缀与后缀]] |

---

## 猜错方向的成本：看懂"报错在哪个阶段"

| 阶段 | 报错特征 | 常见原因 |
|---|---|---|
| **预处理** | `fatal error: xxx.h`、`C4067` | 头文件名错、指令没独占一行 |
| **编译** | `error C....`、`expected ...`、`undeclared` | 拼写、符号、语法、类型问题 |
| **链接** | `LNK....`、`undefined reference` | 缺函数实现、缺 `main`、库没链 |

> **报错前缀先看一眼**：`C` 开头 = 编译期；`LNK` 开头 = 链接期。定位方向完全不同。

## 相关
- [[Visual Studio 快捷键与调试]]（F12 跳定义、断点调试）
- [[L13 时间差计算器（scanf 与 C4996）]]（C4996 的实战现场）
- [[❌ 我的易错点清单]]
