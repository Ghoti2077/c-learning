---
title: "E01 点灯程序逐行解读（用的全是 CubeMX 生成的 HAL 库）"
type: lesson
lesson: E01
date: 2026-10-01
tags: [嵌入式, STM32, HAL, 点灯, CLion]
status: 已完成
---
# E01 点灯程序解读：全是用 HAL 库函数（CubeMX 生成）

- 日期：2026-10-01
- 来源：我的第一个 STM32 工程 `D:\work\STM32\projects\blink`（CubeMX 生成 + CLion 编译）
- 我的问题（原话）：「我的点灯程序，你是用 **CubeMX 里生成的 HAL 库函数**吗」
- 标签：`#嵌入式` `#STM32` `#HAL` `#点灯`

> **答案：是的，点灯用到的全部是 HAL 库里的函数（还有 1 个宏）**，
> 它们跟着 CubeMX 生成工程时一起被拷进了 `Drivers\STM32F1xx_HAL_Driver\`。

---

## 1. 源码（`Core\Src\main.c` 的关键部分，原样）

```c
int main(void)
{
  /* USER CODE BEGIN 1 */

  /* USER CODE END 1 */

  /* MCU Configuration--------------------------------------------------------*/

  /* Reset of all peripherals, Initializes the Flash interface and the Systick. */
  HAL_Init();                                  /* ← HAL 函数 ① */

  /* Configure the system clock */
  SystemClock_Config();

  /* USER CODE BEGIN 2 */
  /* 打开 GPIOC 的时钟：不打开，PC13 怎么点都不动 */
  __HAL_RCC_GPIOC_CLK_ENABLE();                /* ← 宏 ② */

  /* 把 PC13 配成"推挽输出" */
  GPIO_InitTypeDef led = {0};                  /* ← HAL 定义的结构体类型 */
  led.Pin   = GPIO_PIN_13;
  led.Mode  = GPIO_MODE_OUTPUT_PP;
  led.Pull  = GPIO_NOPULL;
  led.Speed = GPIO_SPEED_FREQ_LOW;
  HAL_GPIO_Init(GPIOC, &led);                  /* ← HAL 函数 ③ */

  /* Infinite loop */
  /* USER CODE BEGIN WHILE */
  while (1)
  {
    /* USER CODE END WHILE */

    /* USER CODE BEGIN 3 */
    HAL_GPIO_TogglePin(GPIOC, GPIO_PIN_13);    /* ← HAL 函数 ④ 翻转电平 */
    HAL_Delay(500);                            /* ← HAL 函数 ⑤ 等 500 毫秒 */
  }
  /* USER CODE END 3 */
}
```

## 2. 用的每个东西是什么（逐行）

| 行 | 名字 | 类别 | 干什么 |
|---|---|---|---|
| 73 | `HAL_Init()` | **HAL 函数** | HAL 自己的"开机自检"：复位所有外设、初始化 Flash 接口和 **SysTick**（后面 `HAL_Delay` 就靠它计时） |
| 89 | `__HAL_RCC_GPIOC_CLK_ENABLE()` | **宏**（不是函数） | **打开 GPIOC 的时钟**。STM32 的外设默认**断电（不供时钟）**，不先开时钟，PC13 怎么设置都不动 —— 这是新手最容易漏的一步 |
| 92–96 | `GPIO_InitTypeDef led` + 4 个成员 | HAL 定义的**结构体** | **先填一张"配置单"**：哪个引脚（13）、什么模式（推挽输出 PP）、上拉/下拉（都不要）、速度（低速） |
| 97 | `HAL_GPIO_Init(GPIOC, &led)` | **HAL 函数** | **把配置单交给 HAL 去执行**，真正写进寄存器 |
| 107 | `HAL_GPIO_TogglePin(GPIOC, GPIO_PIN_13)` | **HAL 函数** | **翻转** PC13 电平（本来低的变高、高的变低）—— 亮灭一次 |
| 108 | `HAL_Delay(500)` | **HAL 函数** | 等 500 毫秒（靠 SysTick 中断数数，单位是毫秒） |

**打比方**：STM32 的引脚像一个**没通电的开关柜**。
①`__HAL_RCC_..._CLK_ENABLE()` = **给这排柜子通电**；② 填 `GPIO_InitTypeDef` = **写一张配置单**；③ `HAL_GPIO_Init()` = **把配置单交给工人装好**；④ `HAL_GPIO_TogglePin()` = **抬手按一下开关**；⑤ `HAL_Delay()` = **数 500 个 1/1000 秒**。

**"HAL"是什么**：**Hardware Abstraction Layer（硬件抽象层）** —— ST 写好的一大堆驱动函数。
它把"往哪个寄存器写什么位"这种底层操作**包成了函数**，所以你**一行 `HAL_GPIO_Init` 就能配好引脚**，不用去背寄存器地址。
（生成的工程里 `Drivers\STM32F1xx_HAL_Driver\Src\` 下那几十个 `.c` 文件就是它的源码 —— 编译出来的 3.6KB Flash 里，大部分就是它们。）

## 3. ⚠️ 必须记住的一条规矩：只改 `USER CODE` 区域

`main.c` 里到处是这种成对的注释：

```c
/* USER CODE BEGIN 2 */
   ... 我自己写的代码 ...
/* USER CODE END 2 */
```

- **只有夹在 `USER CODE BEGIN / END` 之间的代码，CubeMX 重新生成时才会保留**；
- 写在别处（比如 `HAL_Init()` 那几行附近）的代码，**下次在 CubeMX 里点 GENERATE CODE 会被直接覆盖掉**。
- 我发现点灯的那段正好写在 `USER CODE BEGIN 2` 和 `BEGIN 3` 里面 ✅ 位置是对的。

## 4. 顺带看出的一件事：板子现在跑在 8MHz（不是 72MHz）

生成的 `SystemClock_Config()` 里是：

```c
RCC_OscInitStruct.OscillatorType = RCC_OSCILLATORTYPE_HSI;   /* 用内部 RC 振荡器 */
RCC_OscInitStruct.HSIState = RCC_HSI_ON;
RCC_OscInitStruct.PLL.PLLState = RCC_PLL_NONE;               /* PLL 没开 */
RCC_ClkInitStruct.SYSCLKSource = RCC_SYSCLKSOURCE_HSI;       /* 时钟源直接就是 HSI */
```

- **HSI** = 芯片内部的 8MHz RC 振荡器（不用外部晶振就能跑，但精度差一点）；**PLL 没开** → 主频就是 **8MHz**。
- 想让板子跑 **72MHz**：在 CubeMX 的 **Clock Configuration** 页把 **PLL 开起来**（蓝板上有 8MHz 外部晶振 HSE，×9 = 72MHz），重新生成即可。
- **现在要不要改？不用** —— 点灯这活儿 8MHz 足够，先跑通再说。（`HAL_Delay` 是按当前主频算的，所以 500ms 依然是 500ms。）

## 5. 以后会碰到："寄存器版"点灯

同一件事，以后你会看到另一种写法（不看 HAL，直接写寄存器）：

```c
RCC->APB2ENR |= 1 << 4;        /* 打时钟 */
GPIOC->CRH &= ~(0xF << 20);    /* 清配置位 */
GPIOC->CRH |= 0x1 << 20;       /* 配成推挽输出 */
GPIOC->ODR ^= 1 << 13;         /* 翻转 PC13 */
```

**两种写法的关系**：HAL = **别人替你写好的驱动**（好写、看得懂、稍慢）；寄存器 = **自己直接操作硬件**（难写、但快且省空间）。
**现在只用 HAL**，等学完 C 的**位运算**和**指针**再看寄存器版 —— 那时候你会觉得"原来 HAL 就是帮我做了这些事"。

## 相关
- [[STM32-CLion 环境交接（给新对话）]]（环境、路径、烧录步骤）
- [[L28 int的上限与溢出（为什么变负数）]]（嵌入式里 `int` 更小、溢出更危险）
- [[📌 待办与欠账]]（上板验证清单）
