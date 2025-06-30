"""
相続税計算のためのデータモデル
"""
from dataclasses import dataclass
from typing import Dict, List, Optional
from enum import Enum


class HeirType(Enum):
    SPOUSE = "spouse"
    CHILD = "child"
    PARENT = "parent"
    SIBLING = "sibling"
    OTHER = "other"


class RelationshipType(Enum):
    SPOUSE = "配偶者"
    CHILD = "子供"
    ADOPTED_CHILD = "養子"
    GRANDCHILD_ADOPTED = "孫養子"
    PARENT = "親"
    GRANDPARENT = "祖父母"
    SIBLING = "兄弟姉妹"
    HALF_SIBLING = "半血兄弟姉妹"
    OTHER = "その他"


@dataclass
class Heir:
    """法定相続人を表すクラス"""
    id: str
    name: str
    heir_type: HeirType
    relationship: RelationshipType
    inheritance_share: float  # 法定相続分（割合）
    two_fold_addition: bool = False  # 2割加算の対象かどうか
    is_adopted: bool = False  # 養子かどうか


@dataclass
class FamilyStructure:
    spouse_exists: bool
    children_count: int
    adopted_children_count: int
    grandchild_adopted_count: int
    parents_alive: int  # 0: 両方死亡, 1: 片方存命, 2: 両方存命
    grandparents_alive: int
    siblings_count: int
    half_siblings_count: int
    non_heirs_count: int = 0  # 法定相続人以外の人数


@dataclass
class TaxCalculationInput:
    """相続税計算の入力データ"""
    taxable_amount: int  # 課税価格の合計額
    family_structure: FamilyStructure
    heirs: Optional[List[Heir]] = None


@dataclass
class HeirTaxDetail:
    """各相続人の税額詳細"""
    heir_id: str
    name: str # 法定相続人名または入力された名前
    relationship: str
    legal_share_amount: Optional[int] = None # 法定相続分に応じる取得金額
    tax_before_addition: Optional[int] = None # 2割加算前の税額
    two_fold_addition: Optional[int] = None # 2割加算額
    tax_after_addition: Optional[int] = None # 2割加算後の税額
    
    # 実際分割でのみ使用
    heir_name: Optional[str] = None
    inheritance_amount: Optional[int] = None
    tax_amount: Optional[int] = None
    surcharge_deduction_amount: Optional[int] = None # 加算減算額
    final_tax_amount: Optional[int] = None


@dataclass
class TaxCalculationResult:
    """相続税計算の結果"""
    legal_heirs: List[Heir]
    total_heirs_count: int
    basic_deduction: int  # 基礎控除額
    taxable_inheritance: int  # 課税遺産総額
    total_tax_amount: int  # 相続税の総額
    heir_tax_details: List[HeirTaxDetail]


@dataclass
class Division:
    """個々の相続人の分割情報"""
    heir_id: str
    heir_name: str
    inheritance_amount: int


@dataclass
class DivisionInput:
    """実際の分割入力データ"""
    mode: str  # 'amount' or 'percentage'
    total_amount: int
    heirs: List[Heir]
    total_tax_amount: int
    amounts: Optional[Dict[str, int]] = None
    percentages: Optional[Dict[str, float]] = None
    rounding_method: str = 'round'


@dataclass
class DivisionResult:
    """実際の分割計算結果"""
    taxable_amount: int
    basic_deduction: int
    taxable_estate: int
    total_tax_amount: int
    heir_details: List[HeirTaxDetail]


@dataclass
class ValidationError:
    """バリデーションエラー"""
    field: str
    code: str
    message: str


@dataclass
class ValidationResult:
    """バリデーション結果"""
    is_valid: bool
    errors: List[ValidationError]


# 相続税速算表
TAX_TABLE = [
    {"min_amount": 0, "max_amount": 10000000, "tax_rate": 0.10, "deduction": 0},
    {"min_amount": 10000001, "max_amount": 30000000, "tax_rate": 0.15, "deduction": 500000},
    {"min_amount": 30000001, "max_amount": 50000000, "tax_rate": 0.20, "deduction": 2000000},
    {"min_amount": 50000001, "max_amount": 100000000, "tax_rate": 0.30, "deduction": 7000000},
    {"min_amount": 100000001, "max_amount": 200000000, "tax_rate": 0.40, "deduction": 17000000},
    {"min_amount": 200000001, "max_amount": 300000000, "tax_rate": 0.45, "deduction": 27000000},
    {"min_amount": 300000001, "max_amount": 600000000, "tax_rate": 0.50, "deduction": 42000000},
    {"min_amount": 600000001, "max_amount": float('inf'), "tax_rate": 0.55, "deduction": 72000000},
]

# 基礎控除の定数
BASIC_DEDUCTION_BASE = 30000000  # 3,000万円
BASIC_DEDUCTION_PER_HEIR = 6000000  # 600万円

# 2割加算の対象外となる関係
TWO_FOLD_ADDITION_EXEMPT = [
    HeirType.SPOUSE,
    HeirType.CHILD,
    HeirType.PARENT
]

