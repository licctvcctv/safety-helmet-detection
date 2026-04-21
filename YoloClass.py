from pathlib import Path
import cv2
import numpy as np
import torch
from PySide6.QtCore import QThread, Signal
from numpy import random
from lib.app_paths import append_exception, get_log_file, get_results_root
from models.experimental import attempt_load
from utils.datasets import LoadImages
from utils.general import check_img_size, increment_path, non_max_suppression, scale_coords
from utils.plots import plot_one_box
from utils.torch_utils import select_device, time_synchronized
from lib import glo


class YoloThread(QThread):
    send_input = Signal(np.ndarray)
    send_output = Signal(np.ndarray)
    send_result = Signal(dict)
    # emit：detecting/pause/stop/finished/error msg
    send_msg = Signal(str)
    send_percent = Signal(int)
    send_fps = Signal(str)

    def __init__(self):
        super(YoloThread, self).__init__()
        self.weights = ''
        self.current_weight = ''
        self.conf = 0.25
        self.iou = 0.40
        self.is_continue = True  # continue/pause
        self.jump_out = False  # jump out of the loop
        self.percent_length = 1000  # progress bar
        self.vid_cap = None
        self.vid_writer = None
        self.save_path = ''

    def _release_video_resources(self):
        if self.vid_cap is not None:
            self.vid_cap.release()
            self.vid_cap = None
        if isinstance(self.vid_writer, cv2.VideoWriter):
            self.vid_writer.release()
        self.vid_writer = None

    def _load_model(self, device, imgsz, half):
        weight_path = Path(self.weights)
        if not weight_path.exists():
            raise FileNotFoundError(f'模型文件不存在: {weight_path}')

        model = attempt_load(str(weight_path), map_location=device)
        stride = int(model.stride.max())
        imgsz = check_img_size(imgsz, s=stride)
        if half:
            model.half()

        names = model.module.names if hasattr(model, 'module') else model.names
        colors = [[random.randint(0, 255) for _ in range(3)] for _ in names]
        self.current_weight = str(weight_path)
        return model, names, colors, imgsz

    def _finish(self, message):
        self.send_percent.emit(0)
        self.send_msg.emit(message)
        self._release_video_resources()

    @torch.no_grad()
    def run(self,
            imgsz=640,
            device='',
            view_img=False,
            save_conf=False,
            nosave=False,
            classes=None,
            agnostic_nms=False,
            augment=False,
            update=False,
            project='result',
            name='exp',
            exist_ok=False,
            no_trace=False
            ):

        # Initialize
        try:
            source = glo.get_value('inputPath', '')
            if not source:
                raise ValueError('请先选择待检测的图片或视频')
            if not Path(source).exists():
                raise FileNotFoundError(f'待检测文件不存在: {source}')
            if not self.weights:
                raise ValueError('未检测到可用模型，请先导入 .pt 模型')

            device = select_device(device)
            half = device.type != 'cpu'
            save_img = not nosave and not str(source).endswith('.txt')  # save inference images
            # Directories
            save_dir = Path(increment_path(get_results_root() / name, exist_ok=exist_ok))  # increment run
            save_dir.mkdir(parents=True, exist_ok=True)  # make dir
            # Load model
            model, names, colors, imgsz = self._load_model(device, imgsz, half)
            stride = int(model.stride.max())
            # Set Dataloader
            vid_path, self.vid_writer = None, None
            dataset = iter(LoadImages(source, img_size=imgsz, stride=stride))

            # Run inference
            if device.type != 'cpu':
                model(torch.zeros(1, 3, imgsz, imgsz).to(device).type_as(next(model.parameters())))  # run once
            old_img_w = old_img_h = imgsz
            old_img_b = 1

            # 参数设置
            count = 0
            # 开始处理每一张图片
            while True:

                # 停止检测
                if self.jump_out:
                    self._finish('Stop')
                    break

                # change model
                if self.current_weight != str(Path(self.weights)):
                    # Load model
                    model, names, colors, imgsz = self._load_model(device, imgsz, half)
                    stride = int(model.stride.max())
                    # Run inference
                    if device.type != 'cpu':
                        model(torch.zeros(1, 3, imgsz, imgsz).to(device).type_as(next(model.parameters())))  # run once
                    old_img_w = old_img_h = imgsz
                    old_img_b = 1

                if self.is_continue:
                    try:
                        path, img, im0s, self.vid_cap = next(dataset)
                    except StopIteration:
                        self._finish('Finished')
                        break

                    im0 = im0s.copy() if isinstance(im0s, np.ndarray) else im0s[0].copy()
                    # 原始图片送入 input框
                    self.send_input.emit(im0)
                    # 处理processBar
                    count += 1

                    if self.vid_cap:
                        total_frames = int(self.vid_cap.get(cv2.CAP_PROP_FRAME_COUNT))
                        if total_frames > 0:
                            percent = min(
                                self.percent_length,
                                int(count / total_frames * self.percent_length),
                            )
                        else:
                            percent = 0
                        self.send_percent.emit(percent)
                    else:
                        percent = self.percent_length
                        self.send_percent.emit(percent)

                    # 处理图片
                    statistic_dic = {name: 0 for name in names}
                    img = torch.from_numpy(img).to(device)
                    img = img.half() if half else img.float()  # uint8 to fp16/32
                    img /= 255.0  # 0 - 255 to 0.0 - 1.0
                    if img.ndimension() == 3:
                        img = img.unsqueeze(0)
                    # Warmup
                    if device.type != 'cpu' and (
                            old_img_b != img.shape[0] or old_img_h != img.shape[2] or old_img_w != img.shape[3]):
                        old_img_b = img.shape[0]
                        old_img_h = img.shape[2]
                        old_img_w = img.shape[3]
                        for i in range(3):
                            model(img, augment=augment)[0]

                    # Inference
                    t1 = time_synchronized()
                    with torch.no_grad():  # Calculating gradients would cause a GPU memory leak
                        pred = model(img, augment=augment)[0]
                    t2 = time_synchronized()

                    # Apply NMS
                    pred = non_max_suppression(pred, self.conf, self.iou, classes=classes,
                                               agnostic=agnostic_nms)
                    t3 = time_synchronized()
                    # Process detections
                    for i, det in enumerate(pred):  # detections per image
                        p, s, frame = path, '', getattr(dataset, 'frame', 0)
                        p = Path(p)  # to Path
                        self.save_path = str(save_dir / p.name)  # img.jpg
                        if len(det):
                            # Rescale boxes from img_size to im0 size
                            det[:, :4] = scale_coords(img.shape[2:], det[:, :4], im0.shape).round()
                            # Write results
                            for *xyxy, conf, cls in reversed(det):
                                # Add bbox to image
                                c = int(cls)  # integer class
                                statistic_dic[names[c]] += 1
                                label = f'{names[int(cls)]} {conf:.2f}'
                                plot_one_box(xyxy, im0, label=label, color=colors[int(cls)], line_thickness=5)
                    # Stream results
                    self.send_output.emit(im0)
                    self.send_result.emit(statistic_dic)

                    # Save results (image with detections)
                    if save_img:
                        if dataset.mode == 'image':
                            if not cv2.imwrite(self.save_path, im0):
                                raise RuntimeError(f"结果图片保存失败: {self.save_path}")
                            print(f" The image with the result is saved in: {self.save_path}")
                        else:  # 'video' or 'stream'
                            if vid_path != self.save_path:  # new video
                                vid_path = self.save_path
                                if isinstance(self.vid_writer, cv2.VideoWriter):
                                    self.vid_writer.release()  # release previous video writer
                                fps = self.vid_cap.get(cv2.CAP_PROP_FPS) if self.vid_cap else 0
                                if fps <= 0:
                                    fps = 25
                                w = int(self.vid_cap.get(cv2.CAP_PROP_FRAME_WIDTH)) if self.vid_cap else im0.shape[1]
                                h = int(self.vid_cap.get(cv2.CAP_PROP_FRAME_HEIGHT)) if self.vid_cap else im0.shape[0]
                                self.vid_writer = cv2.VideoWriter(self.save_path,
                                                                  cv2.VideoWriter_fourcc(*'mp4v'),
                                                                  fps,
                                                                  (w, h))
                                if not self.vid_writer.isOpened():
                                    raise RuntimeError(f"结果视频保存失败: {self.save_path}")
                            self.vid_writer.write(im0)
                else:
                    self.msleep(30)

        except Exception as e:
            self._release_video_resources()
            append_exception(
                f"推理异常 | input={glo.get_value('inputPath', '')} | weights={self.weights} | log={get_log_file()}",
                e,
            )
            self.send_msg.emit("程序出错啦!!!   " + str(e))
