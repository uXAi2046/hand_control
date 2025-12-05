# Touch-Free Recipe Scroller

一个基于 MediaPipe + OpenCV + PyAutoGUI 的免触滚屏与截图小工具：通过摄像头识别手势，
- 食指靠近窗口顶部绿色线时按节奏向上滚动；
- 食指靠近底部红色线时按节奏向下滚动；
- 五指捏合（拇指与四指尖同时聚拢）时自动截图并弹出预览窗口；
- 按 `q` 退出。

## 功能特性
- 手势滚动：顶部/底部“滚动分区”可视化，进入区并停留后按冷却节奏滚动，避免抖动与过快。
- 五指捏合截图：要求食指更紧、中/无名/小指至少三个与拇指接近，停留后截图并预览。
- 界面提示：左上角显示当前状态（`SCROLL UP`/`SCROLL DOWN`/`SHOT`/`IDLE`）与捏合调试读数。

## 环境要求
- macOS（ARM/Apple Silicon 已验证），摄像头可用。
- Python 3.11（推荐）。`mediapipe` 在 3.13 上无预编译轮子，建议使用 3.11。

## 安装步骤
在项目根目录执行：

```bash
# 安装 Python 3.11（如已安装可跳过）
brew install python@3.11

# 创建并启用虚拟环境
python3.11 -m venv .venv311
source .venv311/bin/activate

# 升级 pip 并安装依赖
python -m pip install --upgrade pip
pip install opencv-python mediapipe pyautogui
```

## 运行
```bash
source .venv311/bin/activate
python touch_free_recipe_scroller.py
```
或：
```bash
.venv311/bin/python touch_free_recipe_scroller.py
```

## 权限设置（macOS）
- 摄像头：系统设置 → 隐私与安全性 → 摄像头 → 允许终端或 Homebrew Python。
- 辅助功能（滚动）：系统设置 → 隐私与安全性 → 辅助功能 → 允许终端或 Python 控制电脑。
- 屏幕录制（截图预览）：系统设置 → 隐私与安全性 → 屏幕录制 → 允许终端或 Homebrew Python。

## 使用说明
- 置前目标窗口（浏览器/文档）并确保页面可滚动。
- 打开程序后，摄像头窗口会显示：顶部绿色线为“上滚区”，底部红色线为“下滚区”。
- 食指移动到对应分区并停留，即按冷却节奏进行滚动。
- 五指捏合并保持片刻后，将自动截图，弹出 `Screenshot Preview` 预览窗口。
- 按 `q` 退出程序。

## 手势与参数
主要参数位于 `touch_free_recipe_scroller.py`：
- `TOP_ZONE_RATIO` `touch_free_recipe_scroller.py:7`：顶部滚动分界线位置（0~1，高度比例）。
- `BOTTOM_ZONE_RATIO` `touch_free_recipe_scroller.py:8`：底部滚动分界线位置。
- `DWELL_MS` `touch_free_recipe_scroller.py:9`：进入滚动区的停留时间，增大更稳。
- `COOLDOWN_MS` `touch_free_recipe_scroller.py:10`：滚动冷却间隔，增大更平滑更慢。
- `SCROLL_AMOUNT` `touch_free_recipe_scroller.py:11`：每次滚动像素量。

五指捏合参数：
- `PINCH_DWELL_MS` `touch_free_recipe_scroller.py:15`：捏合触发的停留时间。
- `PINCH_COOLDOWN_MS` `touch_free_recipe_scroller.py:16`：截图冷却间隔。
- `FIVE_PINCH_INDEX_RATIO` `touch_free_recipe_scroller.py:18`：食指相对拇指的严格距离阈值。
- `FIVE_PINCH_DIST_RATIO` `touch_free_recipe_scroller.py:17`：中/无名/小指相对拇指的距离阈值。
- `FIVE_PINCH_MIN_NEAR_COUNT` `touch_free_recipe_scroller.py:19`：须满足阈值的非食指数量（默认≥3）。

开启了左上角调试读数：`near`（满足阈值的指数量）、`di/dm/dr/dp`（四指尖到拇指的归一化距离）。
根据读数进行快速校准：
- 触发困难：增大 `FIVE_PINCH_INDEX_RATIO` 至 `0.07~0.08`、`FIVE_PINCH_DIST_RATIO` 至 `0.11~0.12`，或降低 `PINCH_DWELL_MS`。
- 误触频繁：减小上述阈值，或增大 `PINCH_COOLDOWN_MS`。

## 常见问题
- `mediapipe` 安装失败（Python 3.13）：请改用 Python 3.11（`brew install python@3.11`）。
- 无法滚动：开启“辅助功能”权限并确保目标窗口处于可滚动区域且在最前。
- 预览黑屏或无截图：开启“屏幕录制”权限。
- 摄像头黑屏：关闭其他占用摄像头的应用，检查摄像头权限。

## 代码结构
- 主脚本：`touch_free_recipe_scroller.py`
  - 摄像头采集与分界线绘制：`touch_free_recipe_scroller.py:42`–`56`
  - 手部关键点提取：`touch_free_recipe_scroller.py:58`–`91`
  - 滚动判定与节奏：`touch_free_recipe_scroller.py:96`–`117`
  - 五指捏合判定与截图：`touch_free_recipe_scroller.py:119`–`145`
  - HUD 与退出：`touch_free_recipe_scroller.py:147`–`156`

## 开发与推送（可选）
- 建议使用分支开发并通过 PR 合并：
```bash
git checkout -b feature/your-change
git push -u origin feature/your-change
```
- GitHub CLI：
```bash
brew install gh
gh auth login
gh auth status
```
如出现 403 推送被拒，确认你对仓库有写权限或改走 PR 流程。

## 许可证
本项目仅用于学习与演示目的。
