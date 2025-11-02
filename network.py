import requests
import random
import time
from typing import List, Optional, Union

# 增加 MaxTestCount 常量来明确所需的最少测试次数
MIN_REQUIRED_SUCCESSFUL_CHECKS = 1  # 至少1个成功就可以判断为网络良好
MAX_TEST_COUNT = 5  # 至少尝试连接 5 个不同的网站才能判断为连接失败


def check_network(
        urls: Optional[List[str]] = None,
        timeout: int = 10,
        print_log=True
) -> bool:
    """
    通过尝试连接最多 N (MAX_TEST_COUNT) 个随机选择的目标URL来检查网络连通性。
    只要其中有 MIN_REQUIRED_SUCCESSFUL_CHECKS 个连接成功，即认为网络良好。

    Args:
        urls: 供检测使用的URL列表。如果未提供，将使用一个默认的知名URL列表。
              建议包含至少5个不同的、国内外稳定且响应快的网站。
        timeout: 每个请求的超时时间（秒）。

    Returns:
        bool: 如果在尝试次数内成功连接到任何一个 URL 并获取到状态码，则返回 True，否则返回 False。
    """
    # 默认的通用测试URL列表，包含不同国家/地区和服务的知名网站
    # 确保列表足够长，以支持至少选择 5 个不同的网站进行测试
    default_urls = [
        "https://www.baidu.com/",
        "https://www.sina.com.cn/",
        "https://www.taobao.com/",
        "https://www.jd.com/",
        "https://www.weibo.com/",
        "https://www.pinduoduo.com/",
        "https://www.aliyun.com/",
        "https://www.tencentcloud.com/",
        "https://cloud.baidu.com/",
    ]

    # 使用提供的URL列表或默认列表
    target_urls = urls if urls and isinstance(urls, list) and len(urls) > 0 else default_urls
    test_urls = random.sample(target_urls, min(MAX_TEST_COUNT, len(target_urls)))


    successful_count = 0

    for i, test_url in enumerate(test_urls):

        try:
            # 发送 HEAD 请求
            response = requests.head(test_url, timeout=timeout)

            # 检查响应状态码：2xx 和 3xx (重定向) 通常表示网络是连通的
            if 200 <= response.status_code < 400:
                successful_count += 1
                # ***核心逻辑***: 只要达到 MIN_REQUIRED_SUCCESSFUL_CHECKS 次成功，立即返回 True
                if successful_count >= MIN_REQUIRED_SUCCESSFUL_CHECKS:
                    return True
            else:
                if print_log:
                    print(f"⚠️ 状态码非预期,连接失败 ({response.status_code})")

        except requests.exceptions.RequestException as e:
            # 捕获所有requests相关的异常 (连接失败, 超时等)
            if print_log:
                print(f"❌ 连接失败/超时: {type(e).__name__}")
        except Exception as e:
            # 捕获其他非预期的异常
            if print_log:
                print(f"❌ 发生未知错误: {type(e).__name__}")

    # 如果循环结束，还没有返回 True (即成功计数不足)
    if print_log:
        print(f"\n--- 总结 ---")
    if successful_count < MIN_REQUIRED_SUCCESSFUL_CHECKS:
        if print_log:
            print(f"💔 所有 {len(test_urls)} 次尝试均未能满足 {MIN_REQUIRED_SUCCESSFUL_CHECKS} 次成功连接的要求。")
        return False

    # 理论上不会走到这里，因为满足成功计数时会提前返回 True
    return False
