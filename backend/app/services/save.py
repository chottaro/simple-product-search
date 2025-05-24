# utils/save.py

import json
import os

from app.models.product_data import ProductItem


def save_to_json(data: list[ProductItem], filename: str = "output.json") -> None:
    """
    Save the file in JSON format.

    Args:
        data (list): Product data.
        filename (str): The file name in JSON format.
    """

    # パスを取得
    script_dir = os.path.dirname(os.path.abspath(__file__))
    # 出力先のディレクトリを指定
    output_dir = os.path.join(os.path.dirname(script_dir), "output")
    # 出力ファイル名のフルパスを作成
    filepath = os.path.join(output_dir, filename)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
