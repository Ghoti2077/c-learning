---
title: "E02 自己用 CLion 写 C8T6 程序的完整流程（两种方式）"
type: lesson
lesson: E02
date: 2026-10-05
tags: [嵌入式, STM32, CLion, CubeMX, 工作流]
status: 已完成
---
# E02 自己用 CLion 写 C8T6 程序的完整流程

- 日期：2026-10-05
- 来源：我的问题「以后我想自己用 CLion 写 C8T6 的程序该怎么做」
- 依据：本机已验证的工程 `D:\work\STM32\projects\blink`（`.ioc` 里 `TargetToolchain=CMake`、`CompilerLinker=GCC`、固件包 `STM32Cube FW_F1 V1.8.7`；`CMakePresets.json` 用 **Ninja** + `cmake/gcc-arm-none-eabi.cmake`）
- 标签：`#嵌入式` `#STM32` `#CLion` `#工作流`

> **一句话**：**两种方式** ——
> **① 复制 `blink` 当模板改**（最快，环境已配好）；**② 用 CubeMX 新建工程**（正式，能选引脚/时钟）。
> 两种最后都是同一套动作：**CLion 打开 → 构建 → OpenOCD 下载并运行**。

---

## 方式 ① 拿 blink 当模板（推荐，省事）

1. 复制整个工程文件夹：
   `D:\work\STM32\projects\blink` → 改个名，比如 `D:\work\STM32\projects\led2`
2. **删掉两个目录**：`build\`（构建产物）和 `.idea\`（CLion 的工程设置）
   → 让 CLion 重新生成，避免还指着旧工程
3. CLion → **打开** → 选新文件夹 → 它会读到 `CMakePresets.json` 自动配置（选 **Debug**）
4. 改代码（见下面第 4 节"能改哪儿"）
5. 右上角点 **构建**（锤子）→ 再点 **烧录/调试**
6. ⚠️ **新工程的烧录配置要再建一次**：编辑配置 → `+` → **OpenOCD 下载并运行** →
   可执行文件选新工程的 `build\Debug\<工程名>.elf`，面板配置文件选工程里的 `stm32f103c8_blue_pill.cfg`

## 方式 ② 用 CubeMX 从零新建工程

1. 打开 **STM32CubeMX** → `File` → **New Project**（新建工程）
2. 搜索框输入 **STM32F103C8** → 在列表里双击选中
3. **配引脚**：点芯片图上的 **PC13** → 选 `GPIO_Output`（蓝板的 LED 就在 PC13）
4. **（可选）配时钟**：`Clock Configuration` 页——想让板子跑 72MHz 就把 **PLL 打开**（HSE 8MHz ×9 = 72MHz）；不想折腾就保持默认 8MHz（HSI）
5. `Project Manager` 页（**最关键的一页**）：
   - **Project Name**：英文名，比如 `led2`
   - **Project Location**：**路径不要有中文、不要有空格**
   - **Toolchain / IDE**：选 **CMake**（本机就是这条路，CLion 直接能开）
   - **Firmware Package**：`STM32Cube FW_F1 V1.8.7`（**本机已有，不用联网下载**）
6. 点 **GENERATE CODE**（生成代码）
7. 回到 CLion → **打开**刚生成的文件夹
   - 提示选择面板配置文件时：选 **`stm32f103c8_blue_pill.cfg`** → 点 **复制到项目并使用**
8. 写代码 → 构建 → 建一次"OpenOCD 下载并运行"配置（同方式 ① 第 6 步）

> **注意**：CubeMX 里 `Toolchain` 选了 **CMake** 才会生成 `CMakeLists.txt` + `CMakePresets.json`（CLion 就靠这两个文件干活）。

---

## 1. 生成出来的工程里，每个文件夹是干嘛的

| 路径 | 是什么 | 能不能改 |
|---|---|---|
| `Core\Src\main.c` | **我的主程序**（`main()` 在这） | ✅ 改，但只在 `USER CODE` 区域里 |
| `Core\Src\stm32f1xx_it.c` | **中断处理**（SysTick 等） | ✅ 只在 USER CODE 区 |
| `Core\Inc\main.h` | 头文件 | ✅ USER CODE 区 |
| `Drivers\STM32F1xx_HAL_Driver\` | **HAL 库源码** | ❌ 别动 |
| `Drivers\CMSIS\` | ARM 内核相关的标准定义 | ❌ 别动 |
| `startup_stm32f103xb.s` | **启动文件**（汇编，芯片上电后第一步） | ❌ 别动 |
| `STM32F103xx_FLASH.ld` | **链接脚本**（告诉链接器：代码放 Flash 哪、变量放 RAM 哪） | ❌ 一般别动 |
| `CMakeLists.txt` / `CMakePresets.json` | **构建脚本**（编译器、优化等级、Debug/Release） | ⚠️ 加源文件时才动，且照注释提示的位置加 |
| `cmake\gcc-arm-none-eabi.cmake` | 指向 ARM 工具链的配置文件 | ❌ 别动 |
| `blink.ioc` | **CubeMX 的工程文件**（双击它就回到图形配置界面） | 用 CubeMX 改，别手改 |
| `build\` | 编译产物（`.elf`/`.hex`/`.map`） | 可删（删了重新构建就有） |

## 2. 平时最常用的四个"改代码的地方"

| 想干什么 | 去哪儿写 |
|---|---|
| **初始化外设**（配引脚、开时钟、初始化串口…） | `main()` 里 `/* USER CODE BEGIN 2 */` |
| **主循环逻辑**（灯怎么闪、状态机） | `while (1)` 里 `/* USER CODE BEGIN 3 */` |
| **自己写的函数** | `/* USER CODE BEGIN 4 */`（写在文件末尾那块） |
| **中断里要干的事** | `Core\Src\stm32f1xx_it.c` 对应函数的 USER CODE 区 |

## 3. 三条铁律（第 1 条最要命）

1. **只改 `USER CODE BEGIN/END` 之间的代码** —— 写在外面，下次在 CubeMX 点 **GENERATE CODE 会被直接覆盖**（我的点灯代码正好写在里面 ✅）。
2. **工程路径不要有中文/空格** —— CubeMX + CMake + ARM 工具链都容易在这里翻车。
3. **`Drivers\`、启动文件、链接脚本别手改** —— 要加自己的 `.c` 文件，优先用 CubeMX 加（或照 `CMakeLists.txt` 里的注释提示追加）。

## 4. 构建与烧录（每次开发就这三步）

1. **构建**：CLion 右上角选 **Debug** → 点锤子 → 看下方 Build 窗口出现 `blink.elf`
2. **烧录**：选 **OpenOCD 下载并运行** → 点绿色箭头（板子要插着 ST-Link）
3. **看效果**：LED 闪不闪

> 小坑（我实测）：**在 git-bash 里直接敲 `cmake` 是找不到命令的**（CMake 没进系统 PATH，CLion 用的是自己带的 CMake）。所以**构建就在 CLion 里点**，别想着命令行。

## 5. 常见报错往哪查

| 现象 | 大概率原因 |
|---|---|
| 报「OpenOCD 没有配置」 | 没建"OpenOCD 下载并运行"配置（见方式 ① 第 6 步） |
| ST-Link 连接失败 | ① 驱动没装（`drivers\ST-Link\stlink_winusb_install.bat` 管理员运行）② **SWCLK/SWDIO 接反了**（ST-Link 侧与板上标注相反） |
| 报 `reset_config` 相关错误 | 本机当前**不用改**（`stm32f1x.cfg` 已经是 `srst_nogate`）；真遇到再把 cfg 末尾改成 `reset_config none` |
| 报 `.ld` 里 `READONLY` 错误 | 本机 GCC 14.3.1 **不用删**（那是 GCC10 及更早的问题） |
| 编译找不到 `arm-none-eabi-gcc` | PATH 里少了工具链目录（本机已加好：`D:\work\Toolchains\arm-gnu-toolchain-14.3.rel1\bin`） |

## 6. 以后再进阶

- **想让板子跑 72MHz**：CubeMX → `Clock Configuration` → 开 PLL（HSE 8MHz ×9）
- **想加外设**（串口、定时器、ADC）：都在 CubeMX 里点，生成后代码会自动出现在 USER CODE 区旁边
- **想看底层**：等学完 C 的**位运算**和**指针**，再看"寄存器版点灯"（`GPIOC->ODR ^= 1 << 13;`），会明白 HAL 帮你做了什么

## 相关
- [[E01 点灯程序解读（HAL 库）]]（点灯代码逐行 + HAL 是什么）
- [[STM32-CLion 环境交接（给新对话）]]（工具链路径、版本、烧录细节）
- [[STM32 环境准备（我买了 F103C8T6）]]（板子参数）
