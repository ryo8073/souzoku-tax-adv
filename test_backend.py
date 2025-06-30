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
        "grandparents_alive": 0,
        "siblings_count": 0,
        "half_siblings_count": 0,
        "non_heirs_count": 0
    }
}

# 法定相続人判定APIのテスト
print("=== 法定相続人判定APIのテスト ===")
try:
    response = requests.post(
        'http://localhost:5003/api/calculation/heirs',
        json={"family_structure": test_data["family_structure"]},
        headers={'Content-Type': 'application/json'}
    )
    print(f"ステータスコード: {response.status_code}")
    print(f"レスポンス: {response.text}")
    
    if response.status_code == 200:
        heirs_data = response.json()
        print("法定相続人判定API: 成功")
        
        # 相続税計算APIのテスト
        print("\n=== 相続税計算APIのテスト ===")
        tax_response = requests.post(
            'http://localhost:5003/api/calculation/tax-amount',
            json=test_data,
            headers={'Content-Type': 'application/json'}
        )
        print(f"ステータスコード: {tax_response.status_code}")
        print(f"レスポンス: {tax_response.text}")
        
        if tax_response.status_code == 200:
            print("相続税計算API: 成功")
        else:
            print("相続税計算API: エラー")
    else:
        print("法定相続人判定API: エラー")
        
except Exception as e:
    print(f"エラー: {e}")

