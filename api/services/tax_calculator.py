"""
相続税計算のビジネスロジック
"""
import math
from typing import Dict, List, Tuple
from models.inheritance import (
    Heir, HeirType, RelationshipType, FamilyStructure, TaxCalculationInput,
    TaxCalculationResult, HeirTaxDetail, DivisionInput, DivisionResult,
    ValidationError, ValidationResult, TAX_TABLE, BASIC_DEDUCTION_BASE,
    BASIC_DEDUCTION_PER_HEIR, TWO_FOLD_ADDITION_EXEMPT
)


class InheritanceTaxCalculator:
    """相続税計算サービス"""
    
    def determine_legal_heirs(self, family_structure: FamilyStructure) -> List[Heir]:
        """法定相続人を判定する"""
        heirs = []
        
        has_children = family_structure.children_count > 0
        has_parents = family_structure.parents_alive > 0
        has_siblings = family_structure.siblings_count > 0 or family_structure.half_siblings_count > 0

        spouse_share = 0.0
        others_share = 1.0

        if family_structure.spouse_exists:
            if has_children:
                spouse_share = 1/2
            elif has_parents:
                spouse_share = 2/3
            elif has_siblings:
                spouse_share = 3/4
            else:
                spouse_share = 1.0
            
            others_share = 1.0 - spouse_share
            
            heirs.append(Heir(
                id="spouse",
                name="配偶者",
                heir_type=HeirType.SPOUSE,
                relationship=RelationshipType.SPOUSE,
                inheritance_share=spouse_share,
                two_fold_addition=False
            ))

        # 第1順位: 子供（直系卑属）
        if has_children:
            total_children = family_structure.children_count
            individual_share = others_share / total_children if total_children > 0 else 0
            
            adopted_indices = list(range(family_structure.adopted_children_count))
            grandchild_adopted_indices = list(range(family_structure.grandchild_adopted_count))

            for i in range(total_children):
                is_adopted = i < family_structure.adopted_children_count
                is_grandchild_adopted = is_adopted and (i < family_structure.grandchild_adopted_count)
                
                if is_grandchild_adopted:
                    name = f"孫養子{i + 1}"
                    relationship = RelationshipType.GRANDCHILD_ADOPTED
                elif is_adopted:
                    name = f"養子{i + 1}"
                    relationship = RelationshipType.ADOPTED_CHILD
                else:
                    name = f"子供{i + 1}"
                    relationship = RelationshipType.CHILD

                heirs.append(Heir(
                    id=f"child_{i+1}",
                    name=name,
                    heir_type=HeirType.CHILD,
                    relationship=relationship,
                    inheritance_share=individual_share,
                    two_fold_addition=is_grandchild_adopted,
                    is_adopted=is_adopted
                ))
        
        # 第2順位: 直系尊属（子供がいない場合）
        elif has_parents:
            individual_share = others_share / family_structure.parents_alive
            
            for i in range(family_structure.parents_alive):
                heirs.append(Heir(
                    id=f"parent_{i+1}",
                    name=f"親{i+1}",
                    heir_type=HeirType.PARENT,
                    relationship=RelationshipType.PARENT,
                    inheritance_share=individual_share,
                    two_fold_addition=False #親は２割加算の対象外
                ))
        
        # 第3順位: 兄弟姉妹（子供も直系尊属もいない場合）
        elif has_siblings:
            total_units = family_structure.siblings_count + family_structure.half_siblings_count / 2
            full_sibling_share = others_share / total_units if total_units > 0 else 0
            half_sibling_share = full_sibling_share / 2
            
            for i in range(family_structure.siblings_count):
                heirs.append(Heir(
                    id=f"sibling_{i+1}",
                    name=f"兄弟姉妹{i+1}",
                    heir_type=HeirType.SIBLING,
                    relationship=RelationshipType.SIBLING,
                    inheritance_share=full_sibling_share,
                    two_fold_addition=True
                ))
            
            for i in range(family_structure.half_siblings_count):
                heirs.append(Heir(
                    id=f"half_sibling_{i+1}",
                    name=f"半血兄弟姉妹{i+1}",
                    heir_type=HeirType.SIBLING,
                    relationship=RelationshipType.HALF_SIBLING,
                    inheritance_share=half_sibling_share,
                    two_fold_addition=True
                ))

        # 法定相続人以外の人を追加（実際の分割計算で使用するため）
        # ※ この段階では法定相続分には影響しない
        for i in range(family_structure.non_heirs_count):
            heirs.append(Heir(
                id=f"non_heir_{i+1}",
                name=f"法定相続人以外{i+1}",
                heir_type=HeirType.OTHER,
                relationship=RelationshipType.OTHER,
                inheritance_share=0.0,
                two_fold_addition=True
            ))
        
        return heirs
    
    def calculate_basic_deduction(self, heirs: List[Heir]) -> int:
        """基礎控除額を計算する"""
        # 養子の制限を適用した法定相続人数を計算
        legal_heirs_count = self._count_legal_heirs_for_deduction(heirs)
        return BASIC_DEDUCTION_BASE + (BASIC_DEDUCTION_PER_HEIR * legal_heirs_count)
    
    def _count_legal_heirs_for_deduction(self, heirs: List[Heir]) -> int:
        """基礎控除計算用の法定相続人数を計算（養子の制限を適用）"""
        count = 0
        adopted_count = 0
        has_biological_children = False
        
        for heir in heirs:
            if heir.heir_type == HeirType.SPOUSE:
                count += 1
            elif heir.heir_type == HeirType.CHILD:
                if heir.is_adopted:
                    adopted_count += 1
                else:
                    count += 1
                    has_biological_children = True
            elif heir.heir_type in [HeirType.PARENT, HeirType.SIBLING]:
                count += 1
        
        # 養子の制限を適用
        if has_biological_children:
            # 実子がいる場合、養子は1人まで
            count += min(adopted_count, 1)
        else:
            # 実子がいない場合、養子は2人まで
            count += min(adopted_count, 2)
        
        return count
    
    def calculate_tax_by_legal_share(self, taxable_amount: int, heirs: List[Heir]) -> TaxCalculationResult:
        """法定相続分による相続税計算"""
        # 基礎控除額の計算
        basic_deduction = self.calculate_basic_deduction(heirs)
        
        # 課税遺産総額の計算
        taxable_estate = max(0, taxable_amount - basic_deduction)
        
        if taxable_estate == 0:
            # 相続税がかからない場合
            heir_details = []
            for heir in heirs:
                heir_details.append(HeirTaxDetail(
                    heir_id=heir.id,
                    name=heir.name,
                    relationship=heir.relationship.value,
                    legal_share_amount=int(taxable_amount * heir.inheritance_share),
                    tax_before_addition=0,
                    two_fold_addition=0,
                    tax_after_addition=0
                ))
            
            return TaxCalculationResult(
                legal_heirs=heirs,
                total_heirs_count=len(heirs),
                basic_deduction=basic_deduction,
                taxable_inheritance=taxable_estate,
                total_tax_amount=0,
                heir_tax_details=heir_details
            )
        
        # 各相続人の相続税額を計算
        heir_details = []
        total_tax = 0
        
        for heir in heirs:
            # 法定相続分に応じた課税遺産額
            heir_taxable_amount = int(taxable_estate * heir.inheritance_share)
            
            # 相続税額の計算（2割加算前）
            tax_before_addition = self._calculate_tax_from_table(heir_taxable_amount)
            total_tax += tax_before_addition
            
            heir_details.append(HeirTaxDetail(
                heir_id=heir.id,
                name=heir.name,
                relationship=heir.relationship.value,
                legal_share_amount=int(taxable_amount * heir.inheritance_share),
                tax_before_addition=tax_before_addition,
                two_fold_addition=0, # この段階では計算しない
                tax_after_addition=tax_before_addition # 加算がないので同額
            ))
        
        return TaxCalculationResult(
            legal_heirs=heirs,
            total_heirs_count=len(heirs),
            basic_deduction=basic_deduction,
            taxable_inheritance=taxable_estate,
            total_tax_amount=total_tax,
            heir_tax_details=heir_details
        )
    
    def calculate_actual_division(self, division_input: DivisionInput) -> DivisionResult:
        """実際の分割による相続税計算"""
        heirs = division_input.heirs
        total_tax_by_legal_share = division_input.total_tax_amount
        total_taxable_amount = division_input.total_amount

        # 実際の取得金額を取得
        if division_input.mode == 'amount':
            actual_amounts = division_input.amounts
        else: # percentage
            actual_amounts = self._convert_percentage_to_amount(
                division_input.percentages, 
                total_taxable_amount,
                division_input.rounding_method
            )

        total_actual_amount = sum(actual_amounts.values())
        if total_actual_amount == 0: # ゼロ除算を回避
            total_actual_amount = 1

        heir_details = []
        calculated_final_tax_total = 0

        for heir in heirs:
            actual_amount = actual_amounts.get(heir.id, 0)
            actual_share = actual_amount / total_actual_amount if total_actual_amount > 0 else 0
            
            proportional_tax = int(total_tax_by_legal_share * actual_share)
            
            adjustment_amount = 0
            
            # 2割加算
            if heir.two_fold_addition:
                surcharge = int(proportional_tax * 0.2)
                adjustment_amount += surcharge

            # 配偶者税額軽減
            if heir.heir_type == HeirType.SPOUSE:
                spouse_statutory_share = self._calculate_spouse_legal_share(heirs)
                reduction_asset_limit = max(160_000_000, total_taxable_amount * spouse_statutory_share)
                reduction_base_amount = min(actual_amount, reduction_asset_limit)
                
                # total_taxable_amount is the base for the overall calculation, not total_actual_amount
                # It can be different if there are bequests to non-heirs that are not part of the taxable estate. 
                # For this app, we assume they are the same.
                base_for_reduction_calc = total_taxable_amount if total_taxable_amount > 0 else 1

                max_reduction = int(total_tax_by_legal_share * (reduction_base_amount / base_for_reduction_calc))
                
                deduction = min(proportional_tax, max_reduction)
                adjustment_amount -= deduction
            
            final_tax = max(0, proportional_tax + adjustment_amount)
            calculated_final_tax_total += final_tax

            heir_details.append(HeirTaxDetail(
                heir_id=heir.id,
                heir_name=heir.name,
                name=heir.name, # legacy
                relationship=heir.relationship.value,
                inheritance_amount=actual_amount,
                tax_amount=proportional_tax, # 配分税額
                surcharge_deduction_amount=adjustment_amount, # 加算減算
                final_tax_amount=final_tax # 最終納税額
            ))

        return DivisionResult(
            taxable_amount=total_taxable_amount,
            basic_deduction=self.calculate_basic_deduction(heirs),
            taxable_estate=max(0, total_taxable_amount - self.calculate_basic_deduction(heirs)),
            total_tax_amount=calculated_final_tax_total,
            heir_details=heir_details
        )
    
    def _convert_percentage_to_amount(self, percentages: Dict[str, float], total_amount: int, rounding_method: str) -> Dict[str, int]:
        """割合を金額に変換"""
        amounts = {}
        for heir_id, percentage in percentages.items():
            amount = total_amount * (percentage / 100)
            if rounding_method == 'round':
                amounts[heir_id] = int(round(amount))
            elif rounding_method == 'floor':
                amounts[heir_id] = int(math.floor(amount))
            else: # ceil
                amounts[heir_id] = int(math.ceil(amount))
        return amounts
        
    def _calculate_spouse_legal_share(self, heirs: List[Heir]) -> float:
        """配偶者の法定相続分を取得"""
        for heir in heirs:
            if heir.heir_type == HeirType.SPOUSE:
                return heir.inheritance_share
        return 0.0

    def _calculate_tax_from_table(self, amount: int) -> int:
        """税額速算表から税額を計算"""
        for row in TAX_TABLE:
            if amount <= row["max_amount"]:
                tax = (amount * row["tax_rate"]) - row["deduction"]
                return int(tax)
        return 0

    def validate_division_input(self, division_input: DivisionInput, heirs: List[Heir]) -> ValidationResult:
        """分割入力データのバリデーション"""
        errors: List[ValidationError] = []

        if division_input.mode == 'amount':
            if not division_input.amounts:
                errors.append(ValidationError(field="amounts", code="MISSING", message="各人の取得金額を入力してください。"))
            else:
                # Make sure all heirs are in the amounts dict
                for heir in heirs:
                    if heir.id not in division_input.amounts:
                         errors.append(ValidationError(field="amounts", code="MISSING_HEIR", message=f"{heir.name}の金額がありません。"))
                
                if sum(division_input.amounts.values()) != division_input.total_amount:
                    errors.append(ValidationError(field="amounts", code="INVALID_SUM", message=f"取得金額の合計({sum(division_input.amounts.values())})が課税価格の合計額({division_input.total_amount})と一致しません。"))
        
        elif division_input.mode == 'percentage':
            if not division_input.percentages:
                errors.append(ValidationError(field="percentages", code="MISSING", message="各人の取得割合を入力してください。"))
            else:
                for heir in heirs:
                    if heir.id not in division_input.percentages:
                         errors.append(ValidationError(field="percentages", code="MISSING_HEIR", message=f"{heir.name}の割合がありません。"))

                if round(sum(division_input.percentages.values()), 5) != 100.0:
                    errors.append(ValidationError(field="percentages", code="INVALID_SUM", message="取得割合の合計が100%になりません。"))

        return ValidationResult(is_valid=len(errors) == 0, errors=errors)

    def validate_family_structure(self, family_structure: FamilyStructure) -> ValidationResult:
        """家族構成入力のバリデーション"""
        errors: List[ValidationError] = []
        
        # 基本的な数値チェック
        if family_structure.children_count < 0:
            errors.append(ValidationError("children_count", "INVALID_VALUE", "子供の数は0以上である必要があります"))
        
        if family_structure.adopted_children_count < 0:
            errors.append(ValidationError("adopted_children_count", "INVALID_VALUE", "養子の数は0以上である必要があります"))
        
        if family_structure.grandchild_adopted_count < 0:
            errors.append(ValidationError("grandchild_adopted_count", "INVALID_VALUE", "孫養子の数は0以上である必要があります"))
        
        if family_structure.parents_alive < 0:
            errors.append(ValidationError("parents_alive", "INVALID_VALUE", "親の生存数は0以上である必要があります"))
        
        if family_structure.siblings_count < 0:
            errors.append(ValidationError("siblings_count", "INVALID_VALUE", "兄弟姉妹の数は0以上である必要があります"))
        
        if family_structure.half_siblings_count < 0:
            errors.append(ValidationError("half_siblings_count", "INVALID_VALUE", "半血兄弟姉妹の数は0以上である必要があります"))
        
        # 法定相続人の存在チェック
        total_heirs = (
            (1 if family_structure.spouse_exists else 0) +
            family_structure.children_count +
            family_structure.adopted_children_count +
            family_structure.grandchild_adopted_count +
            family_structure.parents_alive +
            family_structure.siblings_count +
            family_structure.half_siblings_count
        )
        
        if total_heirs == 0:
            errors.append(ValidationError("family_structure", "NO_HEIRS", "法定相続人が存在しません"))
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )

