#!/usr/bin/env python3
"""
ユーザーストーリーに基づいた分割計算のテストスクリプト
"""
import sys
import os
import unittest

# プロジェクトのルートディレクトリをパスに追加
project_root = os.path.join(os.path.dirname(__file__), 'inheritance_tax_api')
sys.path.insert(0, project_root)

from src.models.inheritance import FamilyStructure, DivisionInput, Division
from src.services.tax_calculator import InheritanceTaxCalculator

# Gherkinユーザーストーリーから抽出したテストシナリオ
scenarios = [
    {
        "name": "Scenario 1: 課税対象総額3億3千万円、配偶者2億円相続",
        "taxable_amount": 330_000_000,
        "family_structure": { "spouse_exists": True, "children_count": 3 },
        "divisions": [
            {"id": "spouse", "name": "配偶者", "amount": 200_000_000},
            {"id": "child_1", "name": "子供1", "amount": 43_333_333},
            {"id": "child_2", "name": "子供2", "amount": 43_333_333},
            {"id": "child_3", "name": "子供3", "amount": 43_333_334},
        ],
        "expected_taxes": { "spouse": 6342424, "child_1": 7852525, "child_2": 7852525, "child_3": 7852525 },
        "expected_total_tax": 29899999
    },
    {
        "name": "Scenario 2: 課税対象総額2億円、配偶者1億6千万円相続",
        "taxable_amount": 200_000_000,
        "family_structure": { "spouse_exists": True, "children_count": 2 },
        "divisions": [
            {"id": "spouse", "name": "配偶者", "amount": 160_000_000},
            {"id": "child_1", "name": "子供1", "amount": 20_000_000},
            {"id": "child_2", "name": "子供2", "amount": 20_000_000},
        ],
        "expected_taxes": { "spouse": 0, "child_1": 2700000, "child_2": 2700000 },
        "expected_total_tax": 5400000
    },
    {
        "name": "Scenario 3: 課税対象総額4億円、配偶者3億円相続",
        "taxable_amount": 400_000_000,
        "family_structure": { "spouse_exists": True, "children_count": 2 },
        "divisions": [
            {"id": "spouse", "name": "配偶者", "amount": 300_000_000},
            {"id": "child_1", "name": "子供1", "amount": 50_000_000},
            {"id": "child_2", "name": "子供2", "amount": 50_000_000},
        ],
        "expected_taxes": { "spouse": 23050000, "child_1": 11525000, "child_2": 11525000 },
        "expected_total_tax": 46100000
    },
    {
        "name": "Scenario 4: 課税対象総額1億円、配偶者全額相続",
        "taxable_amount": 100_000_000,
        "family_structure": { "spouse_exists": True, "children_count": 1 },
        "divisions": [
            {"id": "spouse", "name": "配偶者", "amount": 100_000_000},
            {"id": "child_1", "name": "子供1", "amount": 0},
        ],
        "expected_taxes": { "spouse": 0, "child_1": 0 },
        "expected_total_tax": 0
    },
    {
        "name": "Scenario 5: 課税対象総額5億円、配偶者1億6千万円相続",
        "taxable_amount": 500_000_000,
        "family_structure": { "spouse_exists": True, "children_count": 3 },
        "divisions": [
            {"id": "spouse", "name": "配偶者", "amount": 160_000_000},
            {"id": "child_1", "name": "子供1", "amount": 113_333_333},
            {"id": "child_2", "name": "子供2", "amount": 113_333_333},
            {"id": "child_3", "name": "子供3", "amount": 113_333_334},
        ],
        "expected_taxes": { "spouse": 0, "child_1": 27029999, "child_2": 27029999, "child_3": 27029999 },
        "expected_total_tax": 81089997
    },
    {
        "name": "Scenario 7: 配偶者と親のみ",
        "taxable_amount": 250_000_000,
        "family_structure": { "spouse_exists": True, "parents_alive": 1 },
        "divisions": [
            {"id": "spouse", "name": "配偶者", "amount": 200_000_000},
            {"id": "parent_1", "name": "親1", "amount": 50_000_000},
        ],
        "expected_taxes": { "spouse": 6968889, "parent_1": 10453333 },
        "expected_total_tax": 17422222
    },
    {
        "name": "Scenario 8: 配偶者と兄弟姉妹",
        "taxable_amount": 180_000_000,
        "family_structure": { "spouse_exists": True, "siblings_count": 2 },
        "divisions": [
            {"id": "spouse", "name": "配偶者", "amount": 150_000_000},
            {"id": "sibling_1", "name": "兄弟姉妹1", "amount": 15_000_000},
            {"id": "sibling_2", "name": "兄弟姉妹2", "amount": 15_000_000},
        ],
        "expected_taxes": { "spouse": 0, "sibling_1": 2664999, "sibling_2": 2664999 },
        "expected_total_tax": 5329998
    },
]

class TestDivisionScenarios(unittest.TestCase):
    def setUp(self):
        self.calculator = InheritanceTaxCalculator()

    def run_scenario(self, scenario):
        with self.subTest(scenario["name"]):
            # 1. 家族構成を設定
            fs_data = {
                "spouse_exists": False, "children_count": 0, "adopted_children_count": 0,
                "grandchild_adopted_count": 0, "parents_alive": 0, "grandparents_alive": 0,
                "siblings_count": 0, "half_siblings_count": 0, "non_heirs_count": 0
            }
            fs_data.update(scenario["family_structure"])
            family_structure = FamilyStructure(**fs_data)
            
            # 2. 法定相続人を判定
            heirs = self.calculator.determine_legal_heirs(family_structure)
            
            # 3. 実際の分割内容を設定
            division_input = DivisionInput(
                divisions=[Division(
                    heir_id=d["id"], 
                    heir_name=d["name"], 
                    inheritance_amount=d["amount"]
                ) for d in scenario["divisions"]]
            )
            
            # 4. 分割計算を実行
            result = self.calculator.calculate_actual_division(
                scenario["taxable_amount"], heirs, division_input
            )
            
            # 5. 結果を検証
            # 各人の税額を検証
            for heir_id, expected_tax in scenario["expected_taxes"].items():
                actual_heir = next((d for d in result.heir_details if d.heir_id == heir_id), None)
                self.assertIsNotNone(actual_heir, f"{heir_id} が結果に見つかりません")
                # 1円未満の誤差は許容
                self.assertAlmostEqual(
                    expected_tax, actual_heir.final_tax_amount, delta=1,
                    msg=f"{scenario['name']} - {actual_heir.name} の税額が不正"
                )

            # 合計税額を検証
            self.assertAlmostEqual(
                scenario["expected_total_tax"], result.total_tax_amount, delta=1,
                msg=f"{scenario['name']} - 合計税額が不正"
            )

    def test_all_scenarios(self):
        # このメソッドは各シナリオを順次実行する
        for scenario in scenarios:
            self.run_scenario(scenario)

if __name__ == '__main__':
    unittest.main(verbosity=2) 