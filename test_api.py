#!/usr/bin/env python3
import requests
import json

# テストデータ
test_data = {
    "taxable_amount": 100000000,
    "family_structure": {
        "spouse_exists": True,
        "children_count": 2,
        "adopted_children_count": 0,
        "grandchild_adopted_count": 0,
        "parents_alive": 0,
        "siblings_count": 0,
        "half_siblings_count": 0,
        "non_heirs_count": 1
    }
}

# APIエンドポイント
url = "http://localhost:5001/api/calculation/tax-amount"

try:
    print("APIテストを開始...")
    print(f"送信データ: {json.dumps(test_data, indent=2, ensure_ascii=False)}")
    
    response = requests.post(url, json=test_data)
    
    print(f"ステータスコード: {response.status_code}")
    print(f"レスポンス: {json.dumps(response.json(), indent=2, ensure_ascii=False)}")
    
except Exception as e:
    print(f"エラーが発生しました: {e}")

