
import pyautogui
import time

import pyperclip




def locate(img_path:str,confidence:float=0.98):
    """

    :author: name
    :date: 2025/11/2
    :desc: 返回图片在屏幕上的中心位置，如果找到返回坐标，如果没找到就返回None
    例如：(100,200)
    :param :
    :type :
    :return:
    :rtype:
    """
    try:
        location=pyautogui.locateOnScreen(img_path,confidence=confidence)
        if location:
            return location.left+location.width//2,location.top+location.height//2
        else:
            return None
    except Exception as e:
        # print(f"定位失败{e}")
        return None

def wait(
    img_path: str,
    timeout: int = 30,
    interval: float = 0.01,
    appear: bool = True,
):
    """
    等待图像出现或消失，并在条件满足时执行回调函数。

    参数：
    - img_path: 图像文件路径（PNG/JPG）。
    - timeout: 最长等待时间，单位秒。
    - interval: 检查间隔，单位秒。
    - appear: True 等待出现，False 等待消失。
    """

    start_time = time.time()
    while True:
        location = locate(img_path, confidence=0.9)  # confidence 可调，0-1

        if appear and location:
           return location
        elif not appear and not location:
            return location

        if time.time() - start_time > timeout:
            print(f"Timeout: {'waiting for appearance' if appear else 'waiting for disappearance'} of {img_path}")
            return None
        time.sleep(interval)

def click(x:int,y:int,button="left",duration: float=0.5,after_sleep: float=0.5,):
    """

    :author: name
    :date: 2025/11/2
    :desc: 点击
    :param :
    :type :
    :return:
    :rtype:
    """
    pyautogui.moveTo(x,y,duration=duration)
    pyautogui.click(button=button)
    time.sleep(after_sleep)
    pass

def double_click(x:int,y:int,button="left",duration: float=0.5,after_sleep: float=0.5):
    """

    :author: name
    :date: 2025/11/2
    :desc: 双击
    :param :
    :type :
    :return:
    :rtype:
    """
    pyautogui.moveTo(x,y,duration=duration)
    pyautogui.doubleClick(button=button)
    time.sleep(after_sleep)

def input(msg:str,after_sleep: float=0.5):
    """

    :author: name
    :date: 2025/11/2
    :desc: 输入，包括中文和英文，在输入之前要把光标放到输入框内
    :param :
    :type :
    :return:
    :rtype:
    """

    pyperclip.copy(msg)
    time.sleep(0.3) ##等待粘贴完成
    pyautogui.hotkey("ctrl","v")
    time.sleep(after_sleep)



def type_ascii_str(msg:str,after_sleep:float=0.5,pre_sleep:float=0.5):
    """

    :author: name
    :date: 2025/11/2
    :desc: 直接输入ascii字符，要把光标放在输入框里，这里模拟的是直接击键
    :param :
    :type :
    :return:
    :rtype:
    """
    time.sleep(after_sleep)
    pyautogui.typewrite(msg)
    time.sleep(after_sleep)

def hover(x:int,y:int,duration: float=0.5):
    """

    :author: name
    :date: 2025/11/2
    :desc: 悬停
    :param :
    :type :
    :return:
    :rtype:
    """
    pyautogui.moveTo(x,y,duration=duration)


def print_screenshot(save_path:str=None):
    """

    :author: name
    :date: 2025/11/2
    :desc: 截图，保存到指定位置
    :param :
    :type :
    :return:
    :rtype:
    """
    img = pyautogui.screenshot()
    if  save_path:
        img.save(save_path)
        return None
    
    return img



def mouse_scroll(step,after_sleep:float=0.5):
    """
    
    :author: name
    :date: 2025/11/2
    :desc: 滚轮滚动，负数往下，正数上滚，滚动step是像素数字，一般100左右 
    :param : 
    :type : 
    :return: 
    :rtype: 
    """
    pyautogui.scroll(step)
    time.sleep(after_sleep)

def enter(after_sleep:float=0.5):
    """
    
    :author: name
    :date: 2025/11/2
    :desc: 按下回车
    :param : 
    :type : 
    :return: 
    :rtype: 
    """
    pyautogui.press("enter")
    time.sleep(after_sleep)
