---
title: "STM32-CLion 环境交接（给新对话）"
type: tool
lesson: L32
date: 2026-10-02
tags: [嵌入式, STM32, CLion, OpenOCD, 交接]
status: 已完成
---
# STM32-CLion 环境交接（给新对话用）

> **新会话请先读这一份。** 环境 2026-10-01 用另一个助手（WorkBuddy）配好，Hermes 2026-10-01 / **2026-10-02 两次逐条复核**（每条附真实输出）。
>
> **一句话状态（2026-10-02 晚）**：**软件环境全通**（工具链齐、编译通过、ST-Link 驱动已装）；
> **曾成功烧录过一次并校验 OK**，但之后 **SWD 连接再也不稳定**（`init mode failed` / `open failed` 反复）—— **详见第 8 节**。
> 编译/工具链一侧已经排除，卡点**纯在物理连接**。

---

## 0. 板子与工程（一眼版）

| | |
|---|---|
| 板子 | **STM32F103C8T6**（蓝板/Blue Pill，最小系统板），LQFP48 |
| 芯片实测 | `device id = 0x20036410`、**`flash size = 64 KiB`**（OpenOCD 实测，真 64KB） |
| 工程目录 | `D:\work\STM32\projects\blink` |
| 芯片配置 | `Mcu.UserName = STM32F103C8Tx`，固件包 **STM32Cube FW_F1 V1.8.7** |
| 固件包本地位置 | `C:\Users\Ghoti\STM32Cube\Repository\STM32Cube_FW_F1_V1.8.7`（**不用再联网下**） |
| 编译产物 | `D:\work\STM32\projects\blink\build\Debug\blink.elf` |
| 板级 cfg | `D:\work\STM32\projects\blink\stm32f103c8_blue_pill.cfg` |
| 链接脚本 | `D:\work\STM32\projects\blink\STM32F103xx_FLASH.ld` |

**工程文件清单**（实测 `ls`）：`blink.ioc`、`Core/`、`Drivers/`、`cmake/`、`CMakeLists.txt`、`CMakePresets.json`（preset：`default` / `Debug` / `Release`）、`startup_stm32f103xb.s`、`stm32f103c8_blue_pill.cfg`、`STM32F103xx_FLASH.ld`

---

## 1. 已装好的工具（2026-10-02 复核 ✅）

| 组件 | 版本（实测输出） | 路径 |
|---|---|---|
| **STM32CubeMX** | **6.18.1**（exe 112,297,960 字节 ≈107MB，**自带 jre，不用装 JDK**） | `D:\work\STM32\STM32CubeMX\STM32CubeMX.exe` |
| **OpenOCD** | `Open On-Chip Debugger 0.12.0 (2026-03-02)`（sysprogs 版） | `D:\work\Toolchains\OpenOCD-20260302-0.12.0\` |
| **ARM GNU Toolchain** | `arm-none-eabi-gcc.exe (Arm GNU Toolchain 14.3.Rel1 (Build arm-14.174)) 14.3.1 20250623`；gdb 15.2 | `D:\work\Toolchains\arm-gnu-toolchain-14.3.rel1\` |
| **ST-Link 驱动** | ✅ **2026-10-02 装好**（管理员跑 `drivers\ST-Link\dpinst_amd64.exe`） | 见第 5 节坑 9 |
| CLion | 2026.1（中文界面） | `D:\APP\Clian\CLion 2026.1` |

**用户级 PATH 已写入这两条**（实测 `reg query HKCU\Environment` 能看到）：

```
D:\work\Toolchains\OpenOCD-20260302-0.12.0\bin
D:\work\Toolchains\arm-gnu-toolchain-14.3.rel1\bin
```

**CLion 里已配**：`.idea\debugServers\ST_LINK.xml`（ST-LINK 调试目标、SWD、GDB 端口 61234）。

**运行时配置在 `.idea\workspace.xml` 的 `<component name="RunManager">` 里**（不在 `.idea\runConfigurations\`，那目录不存在属正常）：

```
configuration name="blink 烧录"
  type      = com.jetbrains.cidr.embedded.openocd.conf.type
  RUN_PATH  = $PROJECT_DIR$/build/Debug/blink.elf
  board-config = D:\work\STM32\projects\blink\stm32f103c8_blue_pill.cfg
  gdb-port  = 3333   telnet-port = 4444   reset-type = INIT
```

---

## 2. 编译产物实测（Flash/RAM 占用）

```
arm-none-eabi-size build/Debug/blink.elf
   text      data       bss       dec       hex
   3616        12      1572      5200      1450
```

→ **Flash ≈ 3.6 KB / 64 KB**，**RAM ≈ 1.6 KB / 20 KB**。
（`blink.elf` 本体 639,592 字节，2026-10-01 04:17 生成。）

---

## 3. 真机烧录 —— ✅ **2026-10-02 成功**

**不需要 CLion，一条命令就能烧**（推荐先用它排除问题）：

```bash
cd /d/work/STM32/projects/blink
openocd -f interface/stlink.cfg -c "transport select swd" -f target/stm32f1x.cfg \
        -c "program build/Debug/blink.elf verify reset exit"
```

**成功输出（实测原样）：**

```
Info : STLINK V2J37S7 (API v2) VID:PID 0483:3748
Info : Target voltage: 3.237097
Info : SWD DPIDR 0x1ba01477
Info : [stm32f1x.cpu] Cortex-M3 r1p1 processor detected
Info : [stm32f1x.cpu] target has 6 breakpoints, 4 watchpoints
Info : [stm32f1x.cpu] Examination succeed
Info : device id = 0x20036410
Info : flash size = 64 KiB
** Programming Finished **
** Verify Started **
** Verified OK **
** Resetting Target **
Error: Fail reading CTRL/STAT register. Force reconnect      ← 见第 5 节坑 8，无害
```

**只连不烧**（想确认调试器通不通时用）：

```bash
openocd -f interface/stlink.cfg -c "transport select swd" -f target/stm32f1x.cfg -c "init; targets; shutdown"
```

**CLion 里**：右上角配置选 **`blink 烧录`** → 点烧录/调试。

**成功标志**：蓝板的 LED（**PC13**）开始闪 —— 蓝板 LED 是**低电平点亮**。

### 接线规则（这次卡了半天，记住）

**蓝板 4 针 SWD 头**（在 **USB 口的另一端**，丝印从上到下）：

| 板上丝印 | 信号 | 芯片引脚 |
|---|---|---|
| `3V3` | 电源 | +3.3V |
| `DIO` | **SWDIO** | PA13 |
| `CLK` | **SWCLK** | PA14 |
| `GND` | 地 | GND |

ST-Link 那头的 10 孔：`RST / SWCLK / SWIM / SWDIO / GND / 3.3V / 5V`

> ⚠️ **按丝印名字接，绝不按位置一排对一排插！**
> 克隆版 ST-Link 的 4 线排线顺序常是 `RST-SWCLK-SWDIO-GND`，板子是 `3V3-DIO-CLK-GND` ——
> 位置对位置插过去 = **SWDIO 和 SWCLK 接反** = `Error: init mode failed (unable to connect to the target)`。（本次真实踩坑，改对后立刻通）

可选：`RST` 接到板子 `NRST`（提高连不上的成功率）；**板子已用 USB 供电时，ST-Link 的 3.3V 可以不接**，避免两个电源打架。

---

## 4. 教程里的两步"坑"，**本机不用做**（2026-10-02 复核过，有证据）

| 教程说要改 | 本机实际情况 | 结论 |
|---|---|---|
| 把 `.cfg` 里 `reset_config srst_only` 改成 `reset_config none` | `share/openocd/scripts/target/stm32f1x.cfg:72` 已经是 **`reset_config srst_nogate`** | ✅ 不用改 |
| 删掉 `.ld` 里的 `READONLY`（5 处） | 实测在 **106 / 113 / 122 / 131 / 141 行**，注释写着"GCC11 及以后支持"；本机 **GCC 14.3.1** | ✅ 不用删 |

---

## 5. 已知坑（都实测踩过，按序号查）

1. **在 git-bash/MSYS 里调 `arm-none-eabi-size.exe`，路径必须写 `D:/work/...`（Windows 风格）** —— 写 `/d/work/...` 报 `No such file`。
2. `openocd -v` 把版本打到 **stderr**，PowerShell 里显示红色不一定是错。
3. CubeMX 安装时**路径输入框自带尾随空格** → 报 `Could not create directory: ...\STM32CubeMX \help`；清空重输。
4. 板级 cfg 里有 `set FLASH_SIZE 0x20000`（强制按 128KB 处理）；实测芯片是 64KB，用不满就不用管。
5. 走 CMakePresets 时构建目录是 **`build\Debug`**，不是 `cmake-build-debug`。
6. 固件包仓库里还留着一个 `stm32cube_fw_f1_v180.zip`（**可删**）。
7. **transport 的名字**：`openocd -c "init"` 直接跑会报 `Error: Unsupported transport` —— st-link 的 cfg **没默认 transport**，必须自己加 `-c "transport select swd"`。
   （新版 OpenOCD 里 `dapdirect_swd` **已废弃**，会警告 `DEPRECATED! use 'transport select swd'`。）
   （另：`hla_swd` 会报 `Debug adapter doesn't support 'hla_swd' transport`。）
8. **烧完那句 `Error: Fail reading CTRL/STAT register. Force reconnect` / `DP initialisation failed`** —— 出现在 `** Resetting Target **` **之后**，是复位瞬间 SWD 掉线的毛刺，**烧写和校验早已成功**，无害。
9. **ST-Link 驱动**：刚插上时设备管理器里 `STM32 STLink` 是**黄色感叹号**、`Problem = CM_PROB_FAILED_INSTALL`，OpenOCD 报 `Error: open failed`（此时连 `Target voltage` 都读不到，只能看到 STLINK 那行都读不到）。
   装法：**管理员身份**运行 `D:\work\Toolchains\OpenOCD-20260302-0.12.0\drivers\ST-Link\dpinst_amd64.exe`（或 `pnputil /add-driver ...\stlink_dbg_winusb.inf /install`）。
   装好后：`Status: OK`、`Problem: CM_PROB_NONE`、`Class: USBDevice`。
   > 本机 `Ghoti` 属管理员组但**会话是标准令牌**（UAC 过滤），后台提权会静默失败 —— **必须用户自己开管理员 PowerShell** 粘贴命令。
10. **`0x1ba01477` 是 Cortex-M3 的 DP ID** —— 看到它 + `Cortex-M3 r1p1 processor detected` 就说明 SWD 通了。
    **注意：`Target voltage` 读到 ~3.24V ≠ SWD 通**（那只说明 3.3V/GND 接上了），`Error: init mode failed` 通常是 SWDIO/SWCLK 接反。
11. 诊断阶梯（按顺序试，别乱猜）：① 设备管理器看驱动 `Problem` ② `openocd … -c "init; targets; shutdown"` 看有没有 `DPIDR` ③ 有 `Target voltage` 但 `init mode failed` → **先查接线** ④ 仍不行再降速 `adapter speed 100` / 加 `connect_assert_srst`。

---

## 6. SWD 连接不稳定 —— 完整排查记录（2026-10-02 晚，**未解决**）

### 现象

- **成功过一次**：`DPIDR 0x1ba01477` → `Cortex-M3 r1p1 processor detected` → `flash size = 64 KiB` → `Programming Finished` → `Verified OK`。
- **之后再也连不上**：连续 **1000+ 次尝试**，绝大多数 `Error: init mode failed (unable to connect to the target)`，偶尔 `Error: open failed`。

### 已排除（都有实测证据）

| 排查项 | 结论 |
|---|---|
| ST-Link 驱动 | ✅ 正常（`Present: True`、`Status: OK`、`Problem: CM_PROB_NONE`、`Class: USBDevice`） |
| 板子供电 | ✅ 有电（板上 PWR 灯亮；`Target voltage` 稳定读到 3.24V，数值会小幅波动说明是实时测量） |
| 排针焊点 | ✅ 正面背面照片都看过，4 个焊点有锡 |
| **接线位置** | ✅ **两端的丝印都核对过，接法正确**（见下表） |
| 换一组新杜邦线 | ❌ 换了还是失败 → 线本身没问题 |
| 降速 | ❌ 默认 / 1000 / 500 / 100 / 50 / 10 kHz **全部失败** |
| 换驱动后端 | ❌ `stlink.cfg` / `stlink-v2.cfg` / `stlink-v2-1.cfg` / `stlink-dap.cfg` / `stlink-hla.cfg` 全失败 |
| `reset_config` 各种组合 | ❌ `none` / `srst_only srst_nogate` / `connect_assert_srst` 全失败 |
| 板子侧 SWCLK/SWDIO 对调 | ❌ 试过，仍失败 |

**关键推断**：**降到 10 kHz 还失败** → 不可能是信号质量/线长/干扰问题（那个频率下烂线也能通）→ **是"某根信号线根本没接通"**（硬性开路或映射错位）。

### 两端接线核对结果（照片逐字确认）

| 蓝板 4 针丝印（背面视角从上到下） | 信号 | ST-Link 外壳引脚图 |
|---|---|---|
| `3V3` | 电源 | `⑦/⑧ 3.3V` |
| `SWIO` | SWDIO → **PA13** | `④ SWDIO` |
| `SWCLK` | SWCLK → **PA14** | `② SWCLK` |
| `GND` | 地 | `⑤/⑥ GND` |

ST-Link V2 克隆件外壳印的完整引脚图（**②④⑥⑧ 就是偶数那一列，从上往下正好是四线 SWD 需要的顺序**）：

```
RST   ① ②   SWCLK
SWIM  ③ ④   SWDIO
GND   ⑤ ⑥   GND
3.3V  ⑦ ⑧   3.3V
5.0V  ⑨ ⑩   5.0V
```

> ⚠️ 这根随机附带的 4 线排线，**两端线序对不上**（板子端左→右 = 红/棕/灰/紫，下载器端上→下 = 棕/灰/红/紫，正着反着都不一致）→ **怀疑排线内部是"拧线"的**，这也是最大的未排除项。

### 剩下的怀疑对象（按可能性）

1. **那根 4 线排线的内部映射不对**（克隆件常配拧线排线）→ 解法：**别用排线**，用 4 根杜邦线**一根一根从下载器的 `②④⑥⑧` 直接接到板子的 `SWCLK/SWIO/GND/3V3`**。
2. **蓝板 SWD 排针的焊点虚焊**（照片看着有锡，但看不出一致性）→ 解法：**重新烫一遍 4 个焊点**，或**把线直接焊死在板子上**。
3. **克隆下载器的 SWD 输出已损坏**（便宜件很容易被静电打坏）→ 解法：**换一个正经的 ST-Link V2**（20~30 元）。

### 建议的下一步（给新会话）

- **首选**：买一个正版/良品 ST-Link V2，或 ST-Link V2-1（NUCLEO 板载那种）。这已经耗掉 2 小时以上，20 块钱换 2 小时是划算的。
- **零成本**：有电烙铁就把 4 根线**直接焊到板子上**（排除所有连接器/排线）。
- **绕开 SWD 的另一条路**：拓展板上有 **`串口接口/蓝牙接口`：`VCC GND RXD TXD`**，配合 **BOOT0=1** 可以走 STM32 内置串口 bootloader 下载（需要 **USB-TTL 串口板 CH340/CP2102**，用户目前没有；`stm32flash` 或 CubeProgrammer 都能用）。

**注意**：诊断期间**不要同时跑两个 openocd / CLion 烧录**，抢同一个 USB 设备会额外产生 `open failed`，把真实故障掩盖掉（本次就吃过这个亏）。

---

## 7. 网络注意

- 本机 `www.st.com` 被拦（curl 返回 **HTTP 567**，`microsoft.com` 正常）—— CubeMX 已装好；**以后要在 CubeMX 里在线更新固件包/登录 myST 账号可能要开加速器**。
- F1 固件包**已下好**，短期不需要再联网。

---

## 8. 教这个用户时的规矩（给新会话，别偷懒）

- 他是 **C 语言初学者**（学到 分支/循环/switch/break-continue/浮点/拆位；**指针、数组、函数还没学**），STM32 是 **"并轨提前动手"** —— **别默认他懂指针、结构体、寄存器**。
- **讲解必须大白话 + 打比方 + 逐行解释**；超纲内容他说"先不用解释了"就**立刻收手**，记进待办。
- **凡是我说"实测/跑过"，必须把源码贴出来**（他明确要求过）。
- C 语言完整交接在 **`D:\APP\hermes\c-learning\_交接.md`**（进度/欠账以它为准）；教学流程/坑点在 **`c-learning-plan` 技能**。
- 他欠的复习题（L16/L17/L30/L31）**不催**，记在 `📌 待办与欠账.md`。

## 相关
- [[STM32 环境准备（我买了 F103C8T6）]]（板子参数、CubeMX 一代 vs MX2）
- [[STM32-CLion 环境配置记录（WorkBuddy 原始）]]（原始记录，存档）
- [[L10 sizeof（关键字、操作符、字节与比特）]]（**下一个上板验证项**：板上 `int`/`char` 实际字节数）
- [[📌 待办与欠账]]（上板验证清单）
