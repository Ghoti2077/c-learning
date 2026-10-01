# STM32CubeMX + CLion 环境配置记录

> 依据腾讯文档《悍匠STM32CubeMX+Clion配置教程》在本机落地。
> 生成时间：2026-10-01　机器：Windows　板子：**STM32F103C8T6（蓝色药丸）**

---

## 状态总览（2026-10-01 04:25）

| 环节 | 状态 |
|---|---|
| OpenOCD / ARM GCC 安装 + PATH | ✅ 完成 |
| STM32CubeMX 6.18.1 安装 | ✅ 完成 |
| CLion 嵌入式开发设置（CubeMX / OpenOCD 路径） | ✅ 完成 |
| CubeMX 生成 CMake 工程 | ✅ 完成 |
| CLion 编译出 `blink.elf` | ✅ 完成（FLASH 3.5KB / 64KB） |
| 建「OpenOCD 下载并运行」配置 | ⏳ 待你建（见第六节） |
| 实体烧录 / 调试 | ⏳ 待插 ST-Link 验证 |

> **软件环境已全部配好**，剩下两步（建烧录配置、真机烧录）是动手操作，不涉环境安装。

### 本工程关键路径

```
工程目录      D:\work\STM32\projects\blink
固件 elf      D:\work\STM32\projects\blink\build\Debug\blink.elf
板级 cfg      D:\work\STM32\projects\blink\stm32f103c8_blue_pill.cfg
链接脚本      D:\work\STM32\projects\blink\STM32F103xx_FLASH.ld
```
> 注意：走 CMakePresets 时构建目录是 `build\Debug`，不是 `cmake-build-debug`。

### 本板特有的两点结论

- 板级 cfg 用 `stm32f103c8_blue_pill.cfg`；它引的 `stm32f1x.cfg` 里是 `reset_config srst_nogate`，
  **教程里"srst_only 改 none"这一步不用做**
- `STM32F103xx_FLASH.ld` 里 5 处 `READONLY`（106/113/122/131/141 行）**不用删**，
  那是 GCC10 及更早才报错，当前 GCC 14.3.1 支持

---

## 一、已完成（自动配置）

| 组件 | 版本 | 安装路径 | 状态 |
|---|---|---|---|
| OpenOCD | 0.12.0 (2026-03-02) | `D:\work\Toolchains\OpenOCD-20260302-0.12.0` | 已装并验证 |
| ARM GNU Toolchain | 14.3.Rel1 (gcc 14.3.1 / gdb 15.2) | `D:\work\Toolchains\arm-gnu-toolchain-14.3.rel1` | 已装并验证 |
| CLion | 2026.1 | `D:\APP\Clian\CLion 2026.1` | 已存在 |
| STM32CubeMX | **6.18.1** | `D:\work\STM32\STM32CubeMX\STM32CubeMX.exe` | 已装，验证通过 |

最终验收（全部通过）：

```
openocd -v              → Open On-Chip Debugger 0.12.0 (2026-03-02)
arm-none-eabi-gcc -v    → gcc version 14.3.1 (Arm GNU Toolchain 14.3.Rel1)
arm-none-eabi-gdb -v    → GNU gdb 15.2.90
STM32CubeMX.exe         → D:\work\STM32\STM32CubeMX\STM32CubeMX.exe (107 MB)
```

`D:\work` 最终只剩两个目录：`STM32\`（装好的 CubeMX）和 `Toolchains\`（OpenOCD + ARM GCC），
安装包、解压中间产物、压缩包共约 2.1 GB 已清进回收站。

已写入「用户级 PATH」的两条（重开终端即生效）：

```
D:\work\Toolchains\OpenOCD-20260302-0.12.0\bin
D:\work\Toolchains\arm-gnu-toolchain-14.3.rel1\bin
```

验证命令（新开一个 cmd / PowerShell）：

```bat
openocd -v
arm-none-eabi-gcc -v
arm-none-eabi-gdb -v
```

> 注意：`openocd -v` 会把版本信息输出到 stderr，PowerShell 里显示为红色报错是正常现象，看到
> `Open On-Chip Debugger 0.12.0 (2026-03-02)` 就说明装好了。

其它可用位置：

- ST-Link 驱动：`D:\work\Toolchains\OpenOCD-20260302-0.12.0\drivers\ST-Link\stlink_winusb_install.bat`
- 原始压缩包（可删）：`D:\work\Toolchains\arm-gnu-toolchain-14.3.rel1.zip`(276MB)、`openocd-20260302.7z`(7MB)

---

## 二、STM32CubeMX 6.18.1（已安装完成）

安装路径：**`D:\work\STM32\STM32CubeMX\STM32CubeMX.exe`**（107 MB，自带 jre，无需另装 JDK）

ST 的下载站 `downloads.st.com` 在当前所有网络出口都不可达，自动化下载没走通；
最终用你邮件里的带 token 链接确认到最新版 **6.18.1**（链接里能解出真实文件名
`SetupSTM32CubeMX-6.18.1-Win-x86_64.zip`），包由你下载后我做了后续处理：

- 安装包是**两层 7z 自解压**：zip → `SetupSTM32CubeMX-6.18.1.exe` → `jre\` + 真正的
  `SetupSTM32CubeMX-6.18.1.exe`（IzPack/Java 安装器），已剥到最内层
- 安装过程中踩到的坑：**安装路径输入框带尾随空格** → 报
  `Could not create directory: D:\work\STM32\STM32CubeMX \help`。清空重输即可
- 装完后所有中间产物已清理（回收站可还原）

> 顺带记一条：新版 CubeMX 内置 jre，**不要再单独装 JDK**。

---

## 三、待完成 2：CLion 设置（图形界面，约 2 分钟）

1. 打开 CLion 2026.1 → 随便新建一个 **普通 C 项目**（不要新建 STM32 工程）
2. 首次进入会提示配置 MinGW，默认自动检测到，点确定
3. `设置 (Settings)` → `构建、执行、部署` → `工具链`：确认 CMake 工具链正常
4. `设置` → `构建、执行、部署` → `嵌入式开发 (Embedded Development)`：
   - **STM32CubeMX**：点右侧 `...` 选择你刚装的 `STM32CubeMX.exe`
   - 点 **测试**，不报错即可
   - OpenOCD / gdb 会从 PATH 自动找到（已配好）

---

## 四、新建 STM32 工程流程（教程要点）

1. STM32CubeMX → **New Project** → 搜索芯片
   - 大疆 C 板 → `STM32F407IGH6`
2. `Project Manager` 页配置工程名与路径（**路径不要有中文**），Toolchain 选 **STM32CubeIDE** 或 CMake 均可
3. 改完路径按回车，点 **GENERATE CODE**，首次会提示登录 ST 账号并下载固件包，等它下完
4. 在生成的工程文件夹上右键 → **用 CLion 打开**
5. 提示选择面板配置文件时，C 板选 `st_nucleo_f4.cfg` 一类对应的 cfg（用不同芯片按需求选）→ **复制到项目并使用**

---

## 五、烧录前两个必踩的坑（教程里的排错项）

1. **改 cfg**：打开工程里的 `.cfg` 文件，把末尾 `reset_config srst_only` 改成
   `reset_config none`（否则 ST-Link 连接会报复位错误）
2. **改 ld**：如果报 `READONLY` 相关错误，点蓝色链接进入 `.ld` 文件，把里面全部
   `READONLY`（共 5 处）删掉，重新烧录

---

## 六、ST-Link 驱动（首次烧录前）

如果 CLion 报找不到 ST-Link / 设备管理器里是未知设备：

1. 打开 `D:\work\Toolchains\OpenOCD-20260302-0.12.0\drivers\ST-Link`
2. 右键 **以管理员身份运行** `stlink_winusb_install.bat`（或按系统位数跑 `dpinst_amd64.exe`）
3. 同时检查线序：C 板上插 SWD 线，**ST-Link 侧的 SWCLK 与 SWDIO 是反的**，GND 与 3.3V 相同，接错会连不上

---

## 七、OpenOCD 下载配置（烧录配置缺失时）

报错「OpenOCD 没有配置」时：

1. 右上角配置下拉 → **编辑配置** → `+` → **OpenOCD 下载并运行**
2. **可执行的二进制文件**：选工程的 `.elf` 文件
3. **面板配置文件**：选工程里的 `.cfg` 文件
4. 保存，即可烧录
