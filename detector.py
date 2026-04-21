"""安全帽检测系统 —— 检测逻辑与界面交互。"""
import shutil
from pathlib import Path
import cv2
import numpy as np
from PySide6.QtGui import QPixmap, QImage, QMouseEvent, QGuiApplication, QCloseEvent
from PySide6.QtWidgets import QMessageBox, QFileDialog, QWidget
from PySide6.QtCore import QTimer, Qt

from lib.app_paths import get_dialog_root, get_results_root, get_user_model_dir, iter_model_dirs
from lib import glo
from ui import setup_ui, DARK_STYLE
from YoloClass import YoloThread


PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_DIALOG_DIR = get_dialog_root()
PTMODEL_DIR = get_user_model_dir()
MEDIA_FILTER = "图片/视频 (*.jpg *.jpeg *.png *.bmp *.mp4 *.avi *.mov *.mkv)"


class DetectorWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("安全帽佩戴行为检测系统")
        self.resize(1200, 800)
        setup_ui(self)
        self.setStyleSheet(DARK_STYLE)

        self.inputPath = ""
        self.pt_path = PTMODEL_DIR
        self.model_paths = {}
        self.drag = False

        self._init_sliders()
        self._init_buttons()
        self._init_models()
        self._init_yolo_thread()

    # ── 初始化：滑块 ──
    def _init_sliders(self):
        self.con_slider.valueChanged.connect(self._on_conf_slider_change)
        self.iou_slider.valueChanged.connect(self._on_iou_slider_change)
        self.con_num.valueChanged.connect(self._on_conf_spin_change)
        self.iou_num.valueChanged.connect(self._on_iou_spin_change)
        self._on_conf_slider_change(self.con_slider.value())
        self._on_iou_slider_change(self.iou_slider.value())

    # ── 初始化：按钮 ──
    def _init_buttons(self):
        self.folder.clicked.connect(self._select_file)
        self.importbtn.clicked.connect(self._import_model)
        self.exporter.clicked.connect(self._export_result)
        self.playbtn.clicked.connect(self._run_or_continue)
        self.stopbtn.clicked.connect(self._stop)
        self.input.clicked.connect(self._select_file)
        self.output.clicked.connect(self._select_file)

    # ── 初始化：模型列表 ──
    def _init_models(self):
        self.pt_path.mkdir(parents=True, exist_ok=True)
        self._refresh_model_list()
        self.qtimer_search = QTimer(self)
        self.qtimer_search.timeout.connect(self._refresh_model_list)
        self.qtimer_search.start(2000)
        self.comboBox.currentTextChanged.connect(self._on_model_change)

    # ── 初始化：YOLO 线程 ──
    def _init_yolo_thread(self):
        self.yolo_thread = YoloThread()
        self.model_type = self.comboBox.currentText()
        self.yolo_thread.weights = self._model_path(self.model_type)
        self.yolo_thread.percent_length = self.progressBar.maximum()
        self.yolo_thread.send_input.connect(
            lambda x: self._show_img(x, self.input))
        self.yolo_thread.send_output.connect(
            lambda x: self._show_img(x, self.output))
        self.yolo_thread.send_result.connect(self._show_result)
        self.yolo_thread.send_msg.connect(self._status_msg)
        self.yolo_thread.send_percent.connect(self._update_progress)

    def _model_path(self, model_name):
        if not model_name:
            return ""
        return str(self.model_paths.get(model_name, ""))

    def _update_model_state(self, has_models):
        self.playbtn.setEnabled(has_models)
        self.comboBox.setEnabled(has_models)
        if not has_models:
            self.playbtn.setChecked(False)
            self.playbtn.setText("开始检测")

    # ── 模型列表刷新 ──
    def _refresh_model_list(self):
        selected = self.comboBox.currentText()
        model_paths = {}
        for model_dir in iter_model_dirs():
            if not model_dir.exists():
                continue
            for model_path in model_dir.glob("*.pt"):
                model_paths[model_path.name] = model_path

        pt_list = sorted(
            model_paths,
            key=lambda name: (model_paths[name].stat().st_size, name.lower()),
        )
        if not hasattr(self, '_pt_list') or pt_list != self._pt_list:
            self.model_paths = model_paths
            self._pt_list = pt_list
            self.comboBox.blockSignals(True)
            self.comboBox.clear()
            self.comboBox.addItems(pt_list)
            if selected in pt_list:
                self.comboBox.setCurrentText(selected)
            self.comboBox.blockSignals(False)
        else:
            self.model_paths = model_paths

        has_models = bool(pt_list)
        self._update_model_state(has_models)
        if has_models:
            active_model = self.comboBox.currentText() or pt_list[0]
            if self.comboBox.currentText() != active_model:
                self.comboBox.setCurrentText(active_model)
            self._on_model_change(active_model)
        else:
            self.model_type = ""
            if hasattr(self, 'yolo_thread'):
                self.yolo_thread.weights = ""
            self._status_msg("未检测到模型文件，请先导入 .pt 模型")

    # ── 参数变化 ──
    def _on_conf_slider_change(self, value):
        self.numcon = value / 100.0
        self.con_num.blockSignals(True)
        self.con_num.setValue(self.numcon)
        self.con_num.blockSignals(False)
        if hasattr(self, 'yolo_thread'):
            self.yolo_thread.conf = self.numcon

    def _on_iou_slider_change(self, value):
        self.numiou = value / 100.0
        self.iou_num.blockSignals(True)
        self.iou_num.setValue(self.numiou)
        self.iou_num.blockSignals(False)
        if hasattr(self, 'yolo_thread'):
            self.yolo_thread.iou = self.numiou

    def _on_conf_spin_change(self, value):
        self.numcon = value
        slider_value = int(round(value * 100))
        self.con_slider.blockSignals(True)
        self.con_slider.setValue(slider_value)
        self.con_slider.blockSignals(False)
        if hasattr(self, 'yolo_thread'):
            self.yolo_thread.conf = self.numcon

    def _on_iou_spin_change(self, value):
        self.numiou = value
        slider_value = int(round(value * 100))
        self.iou_slider.blockSignals(True)
        self.iou_slider.setValue(slider_value)
        self.iou_slider.blockSignals(False)
        if hasattr(self, 'yolo_thread'):
            self.yolo_thread.iou = self.numiou

    def _on_model_change(self, _text):
        self.model_type = self.comboBox.currentText()
        if hasattr(self, 'yolo_thread'):
            self.yolo_thread.weights = self._model_path(self.model_type)

    # ── 图像显示 ──
    @staticmethod
    def _show_img(img, label):
        try:
            if isinstance(img, str):
                img = cv2.imdecode(np.fromfile(img, dtype=np.uint8), -1)
            if img is None:
                return
            ih, iw = img.shape[:2]
            w, h = label.width(), label.height()
            scale = min(w / iw, h / ih)
            new_w, new_h = int(iw * scale), int(ih * scale)
            resized = cv2.resize(img, (new_w, new_h))
            if resized.ndim == 2:
                rgb = cv2.cvtColor(resized, cv2.COLOR_GRAY2RGB)
            elif resized.shape[2] == 4:
                rgb = cv2.cvtColor(resized, cv2.COLOR_BGRA2RGB)
            else:
                rgb = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
            qimg = QImage(rgb.data, new_w, new_h, 3 * new_w,
                          QImage.Format_RGB888)
            label.setPixmap(QPixmap.fromImage(qimg))
        except Exception as e:
            print(repr(e))

    def _update_progress(self, value):
        self.progressBar.setValue(value)
        percent = int(round(value / self.progressBar.maximum() * 100)) if self.progressBar.maximum() else 0
        self.progressValue.setText(f"{percent}%")

    # ── 文件选择 ──
    def _select_file(self):
        dialog_root = Path(self.inputPath).parent if self.inputPath else DEFAULT_DIALOG_DIR
        path, _ = QFileDialog.getOpenFileName(
            self, "选择图片/视频", str(dialog_root),
            MEDIA_FILTER)
        if not path:
            return
        self.inputPath = path
        glo.set_value('inputPath', path)
        if path.lower().endswith(('.mp4', '.avi', '.mov', '.mkv')):
            cap = cv2.VideoCapture(path)
            ret, frame = cap.read()
            cap.release()
            if ret:
                self._show_img(frame, self.input)
        else:
            self._show_img(path, self.input)
        self.output.setText("开始检测后\n识别结果会显示在这里")
        self.output.setPixmap(QPixmap())
        self.resultlist.clear()
        self._update_progress(0)
        self._status_msg(f"已载入文件 >>> {Path(path).name}")

    def _import_model(self):
        dialog_root = Path(self.inputPath).parent if self.inputPath else DEFAULT_DIALOG_DIR
        path, _ = QFileDialog.getOpenFileName(
            self, "导入模型", str(dialog_root), "模型文件 (*.pt)")
        if path:
            src = Path(path)
            dst = self.pt_path / src.name
            if src.resolve() == dst.resolve():
                QMessageBox.information(self, "提示", "该模型已经在 ptmodel 目录中")
                return
            shutil.copy2(src, dst)
            self._refresh_model_list()
            self.comboBox.setCurrentText(dst.name)
            QMessageBox.information(self, "提示", "模型导入成功!")

    def _export_result(self):
        default_dir = Path(self.inputPath).parent if self.inputPath else get_results_root()
        save_path, _ = QFileDialog.getSaveFileName(
            self, "导出结果", str(default_dir),
            "图片/视频 (*.jpg *.png *.mp4)")
        if not save_path:
            return
        try:
            if not self.yolo_thread.save_path or not Path(self.yolo_thread.save_path).exists():
                raise FileNotFoundError
            shutil.copy(self.yolo_thread.save_path, save_path)
            QMessageBox.information(self, "提示", "导出成功!")
        except Exception:
            QMessageBox.warning(self, "提示", "请先完成检测")

    # ── 检测控制 ──
    def _run_or_continue(self):
        if not self.model_type:
            QMessageBox.warning(self, "提示", "未检测到可用模型，请先导入 .pt 模型!")
            self.playbtn.setChecked(False)
            return
        if not self.inputPath:
            QMessageBox.warning(self, "提示", "请先选择图片/视频!")
            self.playbtn.setChecked(False)
            return
        model_path = Path(self._model_path(self.model_type))
        if not model_path.exists():
            QMessageBox.warning(self, "提示", f"模型文件不存在: {model_path.name}")
            self.playbtn.setChecked(False)
            return
        self.yolo_thread.jump_out = False
        self.yolo_thread.weights = str(model_path)
        if self.playbtn.isChecked():
            self.yolo_thread.is_continue = True
            if not self.yolo_thread.isRunning():
                self.yolo_thread.start()
                self._status_msg("开始检测 >>> " + self.inputPath)
        else:
            self.yolo_thread.is_continue = False
            self._status_msg("已暂停")

    def _stop(self):
        self.yolo_thread.is_continue = False
        self.yolo_thread.jump_out = True
        self._status_msg("已停止")

    # ── 结果展示 ──
    def _show_result(self, stat_dict):
        self.resultlist.clear()
        items = sorted(stat_dict.items(), key=lambda x: x[1], reverse=True)
        items = [f"  {k}: {v}" for k, v in items if v > 0]
        self.resultlist.addItems(items)

    def _status_msg(self, msg):
        if msg in ('Stop', 'Finished'):
            self.playbtn.setChecked(False)
            self.playbtn.setText("开始检测")
            self._status_dot.setStyleSheet("color: #2aad5c;")
            self._status_label.setText("就绪")
        elif msg.startswith("程序出错啦"):
            self.playbtn.setChecked(False)
            self.playbtn.setText("开始检测")
            self._status_dot.setStyleSheet("color: #ad2a4c;")
            self._status_label.setText("异常")
        elif "未检测到模型" in msg:
            self.playbtn.setText("开始检测")
            self._status_dot.setStyleSheet("color: #ad2a4c;")
            self._status_label.setText("缺少模型")
        elif "开始检测" in msg or "检测中" in msg:
            self.playbtn.setText("暂停检测")
            self._status_dot.setStyleSheet("color: #f7c948;")
            self._status_label.setText("检测中...")
        elif msg == "已暂停":
            self.playbtn.setText("继续检测")
            self._status_dot.setStyleSheet("color: #f7c948;")
            self._status_label.setText("已暂停")
        elif msg == "已停止":
            self.playbtn.setText("开始检测")
            self._status_dot.setStyleSheet("color: #ad2a4c;")
            self._status_label.setText("已停止")
        self.outputbox.setText(msg)

    # ── 窗口拖拽 ──
    def mousePressEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self._drag_start = event.globalPosition().toPoint()
            self._win_pos = self.frameGeometry().topLeft()
            self.drag = True

    def mouseMoveEvent(self, event: QMouseEvent):
        if self.drag:
            delta = event.globalPosition().toPoint() - self._drag_start
            self.move(self._win_pos + delta)

    def mouseReleaseEvent(self, event: QMouseEvent):
        if event.button() == Qt.LeftButton:
            self.drag = False

    def center(self):
        scr = QGuiApplication.primaryScreen().size()
        geo = self.geometry()
        self.move((scr.width() - geo.width()) // 2,
                  (scr.height() - geo.height()) // 2)

    def closeEvent(self, event: QCloseEvent):
        if hasattr(self, 'yolo_thread') and self.yolo_thread.isRunning():
            self.yolo_thread.is_continue = False
            self.yolo_thread.jump_out = True
            self.yolo_thread.wait(3000)
        event.accept()
