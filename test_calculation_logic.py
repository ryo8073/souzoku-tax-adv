#!/usr/bin/env python3
"""
相続税計算ロジックのテストスクリプト
半血兄弟姉妹の相続分計算と配偶者税額軽減の検証
"""

import sys
import os

# プロジェクトのルートディレクトリをパスに追加
project_root = os.path.join(os.path.dirname(__file__), 'inheritance_tax_api')
sys.path.insert(0, project_root)

from src.models.inheritance import FamilyStructure, HeirType
from src.services.tax_calculator import InheritanceTaxCalculator
from src.models.inheritance import DivisionInput, Division, HeirTaxDetail

def test_half_sibling_inheritance_share():
    """半血兄弟姉妹の相続分計算テスト"""
    print("=== 半血兄弟姉妹の相続分計算テスト ===")
    
    calculator = InheritanceTaxCalculator()
    
    # テストケース1: 配偶者なし、全血兄弟姉妹2人、半血兄弟姉妹1人
    family_structure = FamilyStructure(
        spouse_exists=False,
        children_count=0,
        adopted_children_count=0,
        grandchild_adopted_count=0,
        parents_alive=0,
        grandparents_alive=0,
        siblings_count=2,
        half_siblings_count=1,
        non_heirs_count=0
    )
    
    heirs = calculator.determine_legal_heirs(family_structure)
    
    print(f"法定相続人数: {len(heirs)}")
    for heir in heirs:
        print(f"  {heir.name}: {heir.inheritance_share:.4f} ({heir.inheritance_share * 100:.2f}%)")
    
    # 期待値の検証
    # 全血兄弟姉妹の相続分をA、半血兄弟姉妹の相続分をA/2とする
    # 2A + 1*(A/2) = 1.0
    # 2.5A = 1.0
    # A = 0.4, A/2 = 0.2
    expected_full_share = 0.4
    expected_half_share = 0.2
    
    full_siblings = [h for h in heirs if h.relationship.value == "兄弟姉妹"]
    half_siblings = [h for h in heirs if h.relationship.value == "半血兄弟姉妹"]
    
    assert len(full_siblings) == 2, f"全血兄弟姉妹の数が不正: {len(full_siblings)}"
    assert len(half_siblings) == 1, f"半血兄弟姉妹の数が不正: {len(half_siblings)}"
    
    for heir in full_siblings:
        assert abs(heir.inheritance_share - expected_full_share) < 0.001, \
            f"全血兄弟姉妹の相続分が不正: {heir.inheritance_share} (期待値: {expected_full_share})"
    
    for heir in half_siblings:
        assert abs(heir.inheritance_share - expected_half_share) < 0.001, \
            f"半血兄弟姉妹の相続分が不正: {heir.inheritance_share} (期待値: {expected_half_share})"
    
    print("✅ テストケース1: 配偶者なし、全血兄弟姉妹2人、半血兄弟姉妹1人 - 合格")
    
    # テストケース2: 配偶者あり、全血兄弟姉妹1人、半血兄弟姉妹2人
    family_structure2 = FamilyStructure(
        spouse_exists=True,
        children_count=0,
        adopted_children_count=0,
        grandchild_adopted_count=0,
        parents_alive=0,
        grandparents_alive=0,
        siblings_count=1,
        half_siblings_count=2,
        non_heirs_count=0
    )
    
    heirs2 = calculator.determine_legal_heirs(family_structure2)
    
    print(f"\n法定相続人数: {len(heirs2)}")
    for heir in heirs2:
        print(f"  {heir.name}: {heir.inheritance_share:.4f} ({heir.inheritance_share * 100:.2f}%)")
    
    # 期待値の検証
    # 配偶者: 3/4 = 0.75
    # 兄弟姉妹全体: 1/4 = 0.25
    # 全血兄弟姉妹の相続分をA、半血兄弟姉妹の相続分をA/2とする
    # 1A + 2*(A/2) = 0.25
    # 2A = 0.25
    # A = 0.125, A/2 = 0.0625
    
    spouse = next((h for h in heirs2 if h.heir_type == HeirType.SPOUSE), None)
    full_siblings2 = [h for h in heirs2 if h.relationship.value == "兄弟姉妹"]
    half_siblings2 = [h for h in heirs2 if h.relationship.value == "半血兄弟姉妹"]
    
    assert spouse is not None, "配偶者が見つからない"
    assert abs(spouse.inheritance_share - 0.75) < 0.001, \
        f"配偶者の相続分が不正: {spouse.inheritance_share} (期待値: 0.75)"
    
    expected_full_share2 = 0.125
    expected_half_share2 = 0.0625
    
    for heir in full_siblings2:
        assert abs(heir.inheritance_share - expected_full_share2) < 0.001, \
            f"全血兄弟姉妹の相続分が不正: {heir.inheritance_share} (期待値: {expected_full_share2})"
    
    for heir in half_siblings2:
        assert abs(heir.inheritance_share - expected_half_share2) < 0.001, \
            f"半血兄弟姉妹の相続分が不正: {heir.inheritance_share} (期待値: {expected_half_share2})"
    
    print("✅ テストケース2: 配偶者あり、全血兄弟姉妹1人、半血兄弟姉妹2人 - 合格")

def test_spouse_tax_deduction():
    """配偶者税額軽減のテスト"""
    print("\n=== 配偶者税額軽減のテスト ===")
    
    calculator = InheritanceTaxCalculator()
    
    # テストケース1: 配偶者と子供がいる場合（配偶者の法定相続分: 1/2）
    family_structure = FamilyStructure(
        spouse_exists=True,
        children_count=1,
        adopted_children_count=0,
        grandchild_adopted_count=0,
        parents_alive=0,
        grandparents_alive=0,
        siblings_count=0,
        half_siblings_count=0,
        non_heirs_count=0
    )
    
    heirs = calculator.determine_legal_heirs(family_structure)
    spouse = next((h for h in heirs if h.heir_type == HeirType.SPOUSE), None)
    
    assert spouse is not None, "配偶者(子供ありケース)が見つかりません"
    spouse_legal_share = spouse.inheritance_share
    
    print(f"配偶者の法定相続分: {spouse_legal_share} ({spouse_legal_share * 100}%)")
    assert abs(spouse_legal_share - 0.5) < 0.001, \
        f"配偶者の法定相続分が不正: {spouse_legal_share} (期待値: 0.5)"
    
    print("✅ テストケース1: 配偶者と子供 - 法定相続分1/2 - 合格")
    
    # テストケース2: 配偶者と親がいる場合（配偶者の法定相続分: 2/3）
    family_structure2 = FamilyStructure(
        spouse_exists=True,
        children_count=0,
        adopted_children_count=0,
        grandchild_adopted_count=0,
        parents_alive=1,
        grandparents_alive=0,
        siblings_count=0,
        half_siblings_count=0,
        non_heirs_count=0
    )
    
    heirs2 = calculator.determine_legal_heirs(family_structure2)
    spouse2 = next((h for h in heirs2 if h.heir_type == HeirType.SPOUSE), None)
    assert spouse2 is not None, "配偶者(親ありケース)が見つかりません"
    spouse_legal_share2 = spouse2.inheritance_share
    
    print(f"配偶者の法定相続分: {spouse_legal_share2:.4f} ({spouse_legal_share2 * 100:.2f}%)")
    assert abs(spouse_legal_share2 - 2.0/3.0) < 0.001, \
        f"配偶者の法定相続分が不正: {spouse_legal_share2} (期待値: {2.0/3.0})"
    
    print("✅ テストケース2: 配偶者と親 - 法定相続分2/3 - 合格")
    
    # テストケース3: 配偶者と兄弟姉妹がいる場合（配偶者の法定相続分: 3/4）
    family_structure3 = FamilyStructure(
        spouse_exists=True,
        children_count=0,
        adopted_children_count=0,
        grandchild_adopted_count=0,
        parents_alive=0,
        grandparents_alive=0,
        siblings_count=1,
        half_siblings_count=0,
        non_heirs_count=0
    )
    
    heirs3 = calculator.determine_legal_heirs(family_structure3)
    spouse3 = next((h for h in heirs3 if h.heir_type == HeirType.SPOUSE), None)
    assert spouse3 is not None, "配偶者(兄弟姉妹ありケース)が見つかりません"
    spouse_legal_share3 = spouse3.inheritance_share
    
    print(f"配偶者の法定相続分: {spouse_legal_share3:.4f} ({spouse_legal_share3 * 100:.2f}%)")
    assert abs(spouse_legal_share3 - 3.0/4.0) < 0.001, \
        f"配偶者の法定相続分が不正: {spouse_legal_share3} (期待値: {3.0/4.0})"
    
    print("✅ テストケース3: 配偶者と兄弟姉妹 - 法定相続分3/4 - 合格")

def test_spouse_tax_reduction_calculation():
    """配偶者の税額軽減の計算ロジックをテスト"""
    print("\n=== 配偶者税額軽減の計算テスト ===")
    calculator = InheritanceTaxCalculator()

    # 共通の家族構成: 配偶者＋子供1人
    family_structure = FamilyStructure(
        spouse_exists=True, children_count=1, adopted_children_count=0, grandchild_adopted_count=0,
        parents_alive=0, grandparents_alive=0, siblings_count=0, half_siblings_count=0, non_heirs_count=0
    )
    heirs = calculator.determine_legal_heirs(family_structure)
    
    # --- テストケース1: 配偶者の取得額が1億6千万円以下 ---
    print("\n--- ケース1: 取得額が1億6千万円以下 ---")
    taxable_amount = 200_000_000  # 課税価格2億円
    
    # 実際の分割
    division_input = DivisionInput(divisions=[
        Division(heir_id="spouse", heir_name="配偶者", inheritance_amount=150_000_000),
        Division(heir_id="child_1", heir_name="子供1", inheritance_amount=50_000_000)
    ])
    
    result = calculator.calculate_actual_division(taxable_amount, heirs, division_input)
    spouse_result = next(d for d in result.heir_details if d.heir_id == "spouse")
    
    print(f"配偶者の最終税額: {spouse_result.final_tax_amount:,}円")
    assert spouse_result.final_tax_amount == 0, "ケース1: 配偶者の税額が0ではありません"
    print("✅ ケース1: 合格")
    
    # --- テストケース2: 配偶者の取得額が法定相続分以下 ---
    print("\n--- ケース2: 取得額が法定相続分以下 ---")
    taxable_amount_2 = 400_000_000 # 課税価格4億円
    spouse_share_amount = taxable_amount_2 * 0.5 # 2億円
    
    division_input_2 = DivisionInput(divisions=[
        Division(heir_id="spouse", heir_name="配偶者", inheritance_amount=180_000_000), # 1.8億円 < 2億円
        Division(heir_id="child_1", heir_name="子供1", inheritance_amount=220_000_000)
    ])
    
    result_2 = calculator.calculate_actual_division(taxable_amount_2, heirs, division_input_2)
    spouse_result_2 = next(d for d in result_2.heir_details if d.heir_id == "spouse")
    
    print(f"配偶者の控除上限額: {max(160_000_000, spouse_share_amount):,}円")
    print(f"配偶者の最終税額: {spouse_result_2.final_tax_amount:,}円")
    assert spouse_result_2.final_tax_amount == 0, "ケース2: 配偶者の税額が0ではありません"
    print("✅ ケース2: 合格")
    
    # --- テストケース3: 配偶者の取得額が控除上限を超える ---
    print("\n--- ケース3: 取得額が控除上限を超える ---")
    taxable_amount_3 = 400_000_000 # 課税価格4億円
    spouse_share_amount_3 = taxable_amount_3 * 0.5 # 2億円
    spouse_deduction_limit = max(160_000_000, spouse_share_amount_3) # 2億円

    division_input_3 = DivisionInput(divisions=[
        Division(heir_id="spouse", heir_name="配偶者", inheritance_amount=300_000_000), # 3億円 > 2億円
        Division(heir_id="child_1", heir_name="子供1", inheritance_amount=100_000_000)
    ])
    
    result_3 = calculator.calculate_actual_division(taxable_amount_3, heirs, division_input_3)
    spouse_result_3 = next(d for d in result_3.heir_details if d.heir_id == "spouse")
    
    # 手計算での期待値
    # 課税遺産総額: 4億 - 4200万 = 3億5800万
    # 法定相続分での税額:
    #   配偶者(1億7900万): 40% - 1700万 = 5460万
    #   子供(1億7900万): 40% - 1700万 = 5460万
    #   相続税総額: 1億920万
    # 配偶者の按分税額: 1億920万 * (3億 / 4億) = 8190万
    # 軽減額: 8190万 * (2億 / 3億) = 5460万
    # 最終税額: 8190万 - 5460万 = 2730万
    expected_tax = 27300000
    
    print(f"配偶者の最終税額: {spouse_result_3.final_tax_amount:,}円 (期待値: {expected_tax:,}円)")
    assert abs(spouse_result_3.final_tax_amount - expected_tax) < 1, "ケース3: 配偶者の税額が期待値と異なります"
    print("✅ ケース3: 合格")

def main():
    """メイン関数"""
    print("相続税計算ロジックのテスト開始")
    print("=" * 50)
    
    try:
        test_half_sibling_inheritance_share()
        test_spouse_tax_deduction()
        test_spouse_tax_reduction_calculation()
        
        print("\n" + "=" * 50)
        print("🎉 全てのテストが合格しました！")
        
    except Exception as e:
        print(f"\n❌ テストが失敗しました: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0

if __name__ == "__main__":
    exit(main())

