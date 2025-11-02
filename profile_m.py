import os
import cProfile
import pstats
import datetime
import subprocess


def visualize_profile_file(file_path: str):
    print(f"\n🚀 正在使用 snakeviz 可视化文件：{file_path}")
    # 构造命令行命令：snakeviz [文件路径]
    command = ['snakeviz', file_path]

    try:
        # 使用 subprocess.run 执行命令
        # check=True 会在命令返回非零退出代码时抛出异常
        # shell=False (默认) 更安全
        subprocess.run(command, check=True)

    except FileNotFoundError:
        print("❌ 错误：未找到 'snakeviz' 命令。请确保您已安装 snakeviz 并将其添加到环境变量中。")
    except subprocess.CalledProcessError as e:
        print(f"❌ 错误：运行 snakeviz 时发生错误。详情：{e}")
    except Exception as e:
        print(f"❌ 发生意外错误：{e}")




def profile(result_dir: str, func, *args, print_stats: bool = True,visual_profile=True, **kwargs):
    """
    Run cProfile on func(*args, **kwargs), save a .prof file under result_dir,
    and optionally print sorted stats to stdout.
    """
    os.makedirs(result_dir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    result_file_path = os.path.join(result_dir, f"profile_{timestamp}.prof")

    profiler = cProfile.Profile()
    profiler.runcall(func, *args, **kwargs)
    profiler.dump_stats(result_file_path)

    if print_stats:
        p = pstats.Stats(result_file_path)
        p.strip_dirs().sort_stats('cumtime').print_stats()

    if visual_profile:
        visualize_profile_file(result_file_path)
