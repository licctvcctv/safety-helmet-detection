# 安全帽佩戴行为检测系统

用于图片和视频中的安全帽佩戴检测，支持本地模型加载、结果预览与导出。

## 功能特性

- 支持图片、视频文件检测
- 实时检测结果展示（检测前/检测后对比）
- 可切换检测模型（自动扫描 ptmodel 目录）
- 可调节置信度（Confidence）和交并比（IoU）阈值
- 检测结果统计与导出
- 异常预警提示

## 项目结构

```
├── main.py              # 程序入口
├── detector.py          # 检测逻辑与界面交互
├── YoloClass.py         # YOLOv7 推理线程
├── ui/
│   ├── layout.py        # 界面布局
│   ├── style.py         # 深色主题样式
│   └── widgets.py       # 自定义控件
├── models/              # YOLOv7 模型定义
├── utils/               # 工具函数
├── ptmodel/             # 模型权重文件 (.pt)
├── datasets/            # 测试数据
└── requirements.txt     # 依赖列表
```

## 启动方式

推荐直接双击项目根目录下的 `run_gui.bat`。

这个脚本会自动完成以下动作：

- 优先复用现有 `.venv`
- 自动跳过 `Microsoft\WindowsApps` 里的假 `python.exe`
- 自动过滤不兼容的 `Python 3.12+`
- 如果机器上没有可用 Python，会优先从清华 TUNA 的 Python 镜像下载安装 `Python 3.11.11` 到项目本地 `.python311/`
- 使用国内 PyPI 镜像安装依赖（优先 TUNA，失败回退到 USTC）
- 最后启动 `main.py`

只检查环境、不启动 GUI：

```bat
run_gui.bat --no-launch
```

## 手动启动

```bash
# Windows PowerShell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python main.py
```

## 运行说明

1. 将训练好的 `.pt` 模型文件放入 `ptmodel/` 目录
2. 运行 `run_gui.bat` 或 `python main.py` 启动检测界面
3. 点击「选择文件」导入待检测的图片或视频
4. 调节参数后点击「开始检测」

## 模型验证

仓库自带了一个可直接运行的推理验证脚本，会自动扫描 `ptmodel/` 和 `datasets/test_images/`：

```bash
python test_detect.py
```

验证结果会保存到 `test_results/<模型名>/`，可用于快速确认模型权重是否可用、推理链路是否正常。

## 交付说明

对外发送时，建议直接发送完整源码压缩包。压缩包中已包含：

- 项目源码
- 模型文件
- 界面资源
- 测试素材
- 一键启动脚本 `run_gui.bat`
