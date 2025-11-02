import os
from pathlib import Path


def convert_files_to_utf8(input_dir: str, src_encoding="gbk",output_dir: str = None) -> dict:
    """
    将指定目录下的文本文件转换为 UTF-8 编码，自动检测文件编码。

    :param input_dir: 输入目录路径。
    :param output_dir: 输出目录路径，可选。如果未指定，则原地覆盖。
    :return: 包含转换结果的字典，键为 'success_count' 和 'failed_files'。
    """
    success_count = 0
    failed_files = []

    input_dir = Path(input_dir)
    if output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
    else:
        output_dir = input_dir

    for root, _, files in os.walk(input_dir,topdown=True):
        for file_name in files:
            source_path = Path(root) / file_name
            relative_path = source_path.relative_to(input_dir)
            dest_path = output_dir / relative_path

            if not dest_path.parent.exists():
                dest_path.parent.mkdir(parents=True, exist_ok=True)
            try:
                # 读取文件内容并转换为 UTF-8
                with open(source_path, 'r', encoding=src_encoding) as f:
                    content = f.read()

                with open(dest_path, 'w', encoding='utf-8') as f:
                    f.write(content)

                success_count += 1
            except Exception as e:
                failed_files.append(f"{source_path} (错误: {e})")


    return {
        "success_count": success_count,
        "failed_files": failed_files
    }
