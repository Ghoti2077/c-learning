---
title: "STM32-CLion 环境交接（给新对话）"
type: tool
lesson: L32
date: 2026-10-01
tags: [嵌入式, STM32, CLion, OpenOCD, 交接]
status: 已完成
---
# STM32-CLion 环境交接（给新对话用）

> **新会话请先读这一份。** 环境是 2026-10-01 用另一个助手（WorkBuddy）配好的，
> 本文档由 Hermes 在 **2026-10-01 逐条复核过**，**2026-10-02 又复核了一遍**（下面每一条都附了真实输出）。
>
> **一句话状态**：**软件环境全部就绪、`blink.elf` 已编译、CLion 烧录配置已建好**；
> **只剩一件事：插上 ST-Link 真机烧录**（2026-10-02 实测：USB 设备列表里没有 ST-Link、`openocd init` 报 `Error: open failed` → **线还没插**）。

---

## 0. 板子与工程（一眼版）

| | |
|---|---|
| 板子 | **STM32F103C8T6**（蓝板/Blue Pill），LQFP48，标称 64KB Flash / 20KB RAM |
| 工程目录 | `D:\work\STM32\projects\blink` |
| 芯片配置 | `Mcu.UserName = STM32F103C8Tx`，固件包 **STM32Cube FW_F1 V1.8.7** |
| 固件包本地位置 | `C:\Users\Ghoti\STM32Cube\Repository\STM32Cube_FW_F1_V1.8.7` |
| 编译产物 | `D:\work\STM32\projects\blink\build\Debug\blink.elf` |
| 板级 cfg | `D:\work\STM32\projects\blink\stm32f103c8_blue_pill.cfg` |
| 链接脚本 | `D:\work\STM32\projects\blink\STM32F103xx_FLASH.ld` |

**工程文件清单**（实测 `ls`）：`blink.ioc`、`Core/`、`Drivers/`、`cmake/`、`CMakeLists.txt`、`CMakePresets.json`（preset 名：`default` / `Debug` / `Release`）、`startup_stm32f103xb.s`、`stm32f103c8_blue_pill.cfg`、`STM32F103xx_FLASH.ld`

---

## 1. 已装好的工具（2026-10-02 复核 ✅）

| 组件 | 版本（实测输出） | 路径 |
|---|---|---|
| **STM32CubeMX** | **6.18.1**（exe 112,297,960 字节 ≈107MB，**自带 jre，不用装 JDK**） | `D:\work\STM32\STM32CubeMX\STM32CubeMX.exe` |
| **OpenOCD** | `Open On-Chip Debugger 0.12.0 (2026-03-02)`（sysprogs 版） | `D:\work\Toolchains\OpenOCD-20260302-0.12.0\` |
| **ARM GNU Toolchain** | `arm-none-eabi-gcc.exe (Arm GNU Toolchain 14.3.Rel1 (Build arm-14.174)) 14.3.1 20250623`；gdb 15.2 | `D:\work\Toolchains\arm-gnu-toolchain-14.3.rel1\` |
| CLion | 2026.1（中文界面） | `D:\APP\Clian\CLion 2026.1` |

**用户级 PATH 已写入这两条**（实测 `reg query HKCU\Environment` 能看到）：

```
D:\work\Toolchains\OpenOCD-20260302-0.12.0\bin
D:\work\Toolchains\arm-gnu-toolchain-14.3.rel1\bin
```

**CLion 里已配**：`.idea\debugServers\ST_LINK.xml` 存在（ST-LINK 调试目标、SWD、GDB 端口 61234）。

**运行时配置 —— 已建好 ✅**（2026-10-02 复核；交接单原先写"还没建"**已过时**）：
存在 **`.idea\workspace.xml`** 的 `<component name="RunManager">` 里（不在 `.idea\runConfigurations\`，那个目录仍然不存在，属正常）：

```
configuration name="blink 烧录"
  type      = com.jetbrains.cidr.embedded.openocd.conf.type
  RUN_PATH  = $PROJECT_DIR$/build/Debug/blink.elf
  board-config = D:\work\STM32\projects\blink\stm32f103c8_blue_pill.cfg
  gdb-port  = 3333   telnet-port = 4444   reset-type = INIT
```

→ **第 3 节第一步「建配置」已经完成，直接跳到第二步（插线烧录）。**

---

## 2. 编译产物实测（Flash/RAM 占用）

```
arm-none-eabi-size build/Debug/blink.elf
   text      data       bss       dec       hex
   3616        12      1572      5200      1450
```

→ **Flash ≈ 3.6 KB（3616+12）/ 64 KB**，**RAM ≈ 1.6 KB（bss）/ 20 KB** —— 板子绰绰有余。
（`blink.elf` 本体 639,592 字节，2026-10-01 04:17 生成。）

---

## 3. 接下来要做的（新会话照这个走）

### ~~第一步：CLion 里建"OpenOCD 下载并运行"配置~~ ✅ **已完成**（见第 1 节）

原步骤留存备查：

1. CLion 右上角配置下拉 → **编辑配置（Edit Configurations）**
2. 左上 `+` → 选 **OpenOCD 下载并运行（OpenOCD Download & Run）**
3. **可执行的二进制文件**：选 `D:\work\STM32\projects\blink\build\Debug\blink.elf`
4. **面板配置文件（Board config file）**：选工程里的 `stm32f103c8_blue_pill.cfg`
5. 保存

### 第二步：插 ST-Link 真机烧录 ← **现在就差这一步**

**2026-10-02 实测：ST-Link 还没插**（证据：① `Get-PnpDevice` 的 USB 设备列表里没有 ST-Link 相关设备，只有蓝牙串口 COM3/COM4；② `openocd -f interface/stlink.cfg -c "transport select dapdirect_swd" -c "init"` → **`Error: open failed`**）。

1. **插线**：ST-Link 的 **SWCLK / SWDIO 与板上标注是反的**（交叉接），GND 对 GND、3.3V 对 3.3V（接错连不上）
2. 先只插 **ST-Link 的 USB 到电脑**，在设备管理器确认它被认出来（若显示"未知设备"：管理员运行
   `D:\work\Toolchains\OpenOCD-20260302-0.12.0\drivers\ST-Link\stlink_winusb_install.bat`）
3. 可以用一条命令先自检调试器能不能连上（不需要 CLion）：
   ```
   openocd -f interface/stlink.cfg -c "transport select dapdirect_swd" -c "init" -c "shutdown"
   ```
   出现 `STLINK` / target 信息 = 通了；`Error: open failed` = 调试器没插好或驱动没装
4. CLion 里选 **`blink 烧录`** 这个配置 → 点烧录/调试
5. **成功标志**：蓝板的 LED（PC13）开始闪（蓝板 LED 是**低电平点亮**）

---

## 4. 教程里的两步"坑"，**本机不用做**（2026-10-02 复核过，有证据）

| 教程说要改 | 本机实际情况 | 结论 |
|---|---|---|
| 把 `.cfg` 里 `reset_config srst_only` 改成 `reset_config none` | 本机 `share/openocd/scripts/target/stm32f1x.cfg:72` 已经是 **`reset_config srst_nogate`** | ✅ **不用改**（如果哪天真连不上，再回来加 `reset_config none` 也不迟） |
| 删掉 `.ld` 里的 `READONLY`（5 处） | 实测 5 处分别在 **106 / 113 / 122 / 131 / 141 行**，注释写着"GCC11 及以后支持"；本机是 **GCC 14.3.1** | ✅ **不用删** |

---

## 5. 已知坑（都是踩过的，别再踩）

1. **在 git-bash/MSYS 里调 `arm-none-eabi-size.exe` 时，路径必须写 `D:/work/...` 这种 Windows 风格**——写 `/d/work/...` 会报 `No such file`（我复核时就踩了这个）。
2. `openocd -v` 把版本打到 **stderr**，PowerShell 里显示红色不一定是错。
3. CubeMX 安装时**路径输入框会自带一个尾随空格** → 报 `Could not create directory: ...\STM32CubeMX \help`；清空重输即可。
4. 板级 cfg 里有 `set FLASH_SIZE 0x20000`（**强制按 128KB 处理**）。C8 标称 64KB，但很多人实测能写满 128KB —— 用不满就不用管。
5. 走 CMakePresets 时构建目录是 **`build\Debug`**，不是 `cmake-build-debug`（找 elf 别找错地方）。
6. 固件包仓库里还留着一个 `stm32cube_fw_f1_v180.zip`（**可删**）。
7. **`openocd -c "init"` 直接跑会报 `Error: Unsupported transport`** —— st-link 的 cfg 里没有默认 transport，**必须自己加 `-c "transport select dapdirect_swd"`**（新版驱动用 `dapdirect_swd`；`hla_swd` 会报 `Debug adapter doesn't support 'hla_swd' transport`）。（2026-10-02 实测）

---

## 6. 网络注意

- 本机 `www.st.com` 被拦（curl 返回 **HTTP 567**，`microsoft.com` 正常）—— CubeMX 已经装好了，**但如果以后要在 CubeMX 里在线更新固件包、或重新登录 myST 账号，可能还需要开加速器**。
- F1 的固件包**已经下好了**（见第 0 节路径），短期不需要再下东西。

---

## 7. 教这个用户时的规矩（给新会话，别偷懒）

- 他是 **C 语言初学者**（学到循环 + 分支 + 函数一点），STM32 属于 **"并轨提前动手"**——**别默认他懂指针、结构体、寄存器**。
- **讲解必须大白话 + 打比方 + 逐行解释**；超纲内容他说"先不用解释了"就**立刻收手**，记进待办。
- **凡是我说"实测/跑过"，必须把源码贴出来**（他明确要求过）。
- C 语言那边的完整交接在 **`D:\APP\hermes\c-learning\_交接.md`**（进度/欠账以它为准），教学流程/坑点在 **`c-learning-plan` 技能**里。
- 他欠着的复习题（L16/L17/L30/L31）**不催**，都记在 `📌 待办与欠账.md`。

## 相关
- [[STM32 环境准备（我买了 F103C8T6）]]（板子参数、CubeMX 一代 vs MX2 的区别）
- [[📌 待办与欠账]]（上板验证清单）
- [[L10 sizeof（关键字、操作符、字节与比特）]]（上板后要验证 `int`/`char` 的实际字节数）
