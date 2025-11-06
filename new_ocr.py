import time

import pyautogui

import cv2
import re

#灰度化
def preprocess_gray_contrast(img_path, save_path="gray_temp.png"):
    """
    将图片转换为灰度图，并增强对比度（CLAHE）。

    :param img_path: 原始图片路径
    :param save_path: 可选，保存处理后的图片路径
    :return: 处理后的灰度图或三通道图（可直接给 PaddleOCR）
    """
    # 读取彩色图
    img = cv2.imread(img_path)
    if img is None:
        raise FileNotFoundError(f"{img_path} 未找到")

    # 转灰度
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    # 增强对比度（CLAHE）
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)

    # 可选：保存处理后的图像
    if save_path:
        cv2.imwrite(save_path, enhanced)

    return enhanced

#遮掩除矩形外
def mask_outside_roi(img_path, roi = (1633, 722, 1925,1030) , save_path="mask_temp.png"):
    """
    将图片中指定矩形外的区域置为白色（便于OCR），ROI内保留原图。

    :param img_path: 原始图片路径
    :param roi: (x1, y1, x2, y2)
    :param save_path: 可选，保存处理后图片路径
    :return: 处理后的图像（H, W, 3）
    """
    img = cv2.imread(img_path)
    if img is None:
        raise FileNotFoundError(f"{img_path} 未找到")

    # 创建纯白背景
    h, w = img.shape[:2]
    result = np.ones_like(img) * 255  # 白底

    # 裁剪 ROI
    x1, y1, x2, y2 = roi
    roi_img = img[y1:y2, x1:x2]

    # 可选：灰度化 + CLAHE 提升文字对比度
    gray = cv2.cvtColor(roi_img, cv2.COLOR_BGR2GRAY)
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(gray)
    roi_processed = cv2.cvtColor(enhanced, cv2.COLOR_GRAY2BGR)

    # 将处理后的 ROI 放回原图对应位置
    result[y1:y2, x1:x2] = roi_processed

    # 保存处理后的图片
    if save_path:
        cv2.imwrite(save_path, result)

    return result

from paddleocr import PaddleOCR
def ocr(file_path):
    p_ocr = PaddleOCR(
        lang="ch",
        ocr_version="PP-OCRv3",
        use_doc_orientation_classify=False,
        use_doc_unwarping=False,
        use_textline_orientation=False)
    print("开始识别")
    start = time.time()
    result = p_ocr.ocr(file_path)
    end = time.time()
    for res in result:
        print("保存")
        res.save_to_img("ocr_result.png")
        res.save_to_json("ocr_result.json")
    print(end - start, "秒")

import numpy as np

from typing import List, Dict, Tuple

def group_ocr_results_by_line(
        rec_texts: List[str],
        rec_boxes: List[List[int]],
        y_threshold: int = 8  # 垂直方向上判断是否为同一行的最大容忍距离（像素）
) -> List[str]:
    """
    根据OCR识别的文本块及其边界框，将其组织成按行排列的文本列表。

    Args:
        rec_texts: OCR识别的文本列表。
        rec_boxes: 文本块的边界框列表，格式为 [x_min, y_min, x_max, y_max]。
        y_threshold: 判断两个文本块是否在同一行的垂直距离阈值。

    Returns:
        按行排列的文本字符串列表。
    """
    if not rec_texts or not rec_boxes:
        return []

    # 1. 计算每个文本块的中心Y坐标和左侧X坐标
    text_data = []
    for text, box in zip(rec_texts, rec_boxes):
        if not text.strip():  # 跳过空字符串或仅包含空格的字符串
            continue

        x_min, y_min, x_max, y_max = box

        # 计算中心Y坐标：作为行的主要分组依据
        center_y = (y_min + y_max) / 2

        # 使用左侧X坐标：作为行内排序的依据
        left_x = x_min

        text_data.append({
            'text': text,
            'center_y': center_y,
            'left_x': left_x,
            'box': box
        })

    # 2. 按中心Y坐标升序排序
    # 确保我们从文档顶部开始处理行
    text_data.sort(key=lambda x: x['center_y'])

    # 3. 按行分组
    lines = []
    current_line = []

    for item in text_data:
        if not current_line:
            # 开启新行
            current_line.append(item)
            continue

        # 检查当前文本块的中心Y坐标与当前行（取第一个文本块）的中心Y坐标的差异
        # 注意：这里可以使用行内所有文本块的平均Y坐标，但为了简化，我们使用行内第一个作为参考
        reference_y = current_line[0]['center_y']

        if abs(item['center_y'] - reference_y) <= y_threshold:
            # 差异在阈值内，属于当前行
            current_line.append(item)
        else:
            # 差异过大，新行开始：

            # a. 整理并保存上一行
            # 在保存前，按X坐标排序以确保文本顺序正确
            current_line.sort(key=lambda x: x['left_x'])

            # 将文本块连接成一行文本，用空格分隔
            line_text = ' '.join([data['text'] for data in current_line])
            lines.append(line_text)

            # b. 开启新行
            current_line = [item]

    # 4. 处理最后一行
    if current_line:
        current_line.sort(key=lambda x: x['left_x'])
        line_text = ' '.join([data['text'] for data in current_line])
        lines.append(line_text)

    return lines

def lines():
    import json
    with open("ocr_result.json", "r", encoding="utf-8") as f:
        data = json.load(f)
    result_lines = group_ocr_results_by_line(data["rec_texts"], data["rec_boxes"])
    return result_lines

def code(ls:List[str],plate_name:str):

    for item in ls:

        value=item
        value=value.replace(" ", "")
        value=value.replace(plate_name, "")
        value=value.replace("板块","")

        def is_alnum(s):
            # ^[a-zA-Z0-9]+$ 匹配从头到尾只包含字母和数字的字符串
            return bool(re.fullmatch(r'[a-zA-Z0-9]+', s))

        if is_alnum(value):
            return value
    return ""

def ocr_code(plate_name):
    pyautogui.screenshot("img_temp.png")
    preprocess_gray_contrast("img_temp.png")
    mask_outside_roi("gray_temp.png")
    ocr("mask_temp.png")
    ls = lines()
    plate_code=code(ls,plate_name)
    return plate_code


from common import gui

if __name__ == '__main__':
    gui.click(*gui.locate("./imgs/tonghuashun.png"))
    gui.click(*gui.locate("./imgs/search.png"))
    gui.input("银行")
    c=ocr_code("银行")
    print(c)

