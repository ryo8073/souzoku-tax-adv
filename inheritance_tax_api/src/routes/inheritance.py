"""
相続税計算API のルート定義
"""
from flask import Blueprint, request, jsonify
from flask_cors import CORS
from src.services.tax_calculator import InheritanceTaxCalculator
from src.models.inheritance import (
    FamilyStructure, TaxCalculationInput, DivisionInput,
    ValidationError, ValidationResult
)

# ブループリントの作成
inheritance_bp = Blueprint('inheritance', __name__)
CORS(inheritance_bp)  # CORS対応

# 計算サービスのインスタンス
calculator = InheritanceTaxCalculator()


def format_currency(amount):
    """金額をカンマ区切りでフォーマット"""
    if amount is None:
        return "0"
    return f"{amount:,}"


def format_percentage(rate):
    """割合をパーセント表示でフォーマット"""
    if rate is None:
        return "0.0%"
    return f"{rate * 100:.1f}%"


@inheritance_bp.route('/calculation/heirs', methods=['POST'])
def determine_heirs():
    """法定相続人判定API"""
    try:
        data = request.get_json()
        
        # 入力データの検証
        family_structure_data = data.get('family_structure', {})
        family_structure = FamilyStructure(
            spouse_exists=family_structure_data.get('spouse_exists', False),
            children_count=family_structure_data.get('children_count', 0),
            adopted_children_count=family_structure_data.get('adopted_children_count', 0),
            grandchild_adopted_count=family_structure_data.get('grandchild_adopted_count', 0),
            parents_alive=family_structure_data.get('parents_alive', 0),
            grandparents_alive=family_structure_data.get('grandparents_alive', 0),
            siblings_count=family_structure_data.get('siblings_count', 0),
            half_siblings_count=family_structure_data.get('half_siblings_count', 0),
            non_heirs_count=family_structure_data.get('non_heirs_count', 0)
        )
        
        # バリデーション
        validation_result = calculator.validate_family_structure(family_structure)
        if not validation_result.is_valid:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': '入力値に問題があります',
                    'details': [
                        {
                            'field': error.field,
                            'code': error.code,
                            'message': error.message
                        } for error in validation_result.errors
                    ]
                }
            }), 400
        
        # 法定相続人の判定
        legal_heirs = calculator.determine_legal_heirs(family_structure)
        basic_deduction = calculator.calculate_basic_deduction(legal_heirs)
        
        # レスポンスの作成
        result = {
            'legal_heirs': [
                {
                    'id': heir.id,
                    'name': heir.name,
                    'type': heir.heir_type.value,
                    'relationship': heir.relationship.value,
                    'inheritance_share': heir.inheritance_share,
                    'inheritance_share_formatted': format_percentage(heir.inheritance_share),
                    'two_fold_addition': heir.two_fold_addition,
                    'is_adopted': heir.is_adopted
                } for heir in legal_heirs
            ],
            'total_heirs_count': len(legal_heirs),
            'basic_deduction': basic_deduction,
            'basic_deduction_formatted': format_currency(basic_deduction)
        }
        
        return jsonify({
            'success': True,
            'result': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_SERVER_ERROR',
                'message': str(e)
            }
        }), 500


@inheritance_bp.route('/calculation/tax-amount', methods=['POST'])
def calculate_tax_amount():
    """相続税額計算API"""
    try:
        data = request.get_json()
        
        # 入力データの取得
        taxable_amount = data.get('taxable_amount', 0)
        family_structure_data = data.get('family_structure', {})
        
        if taxable_amount <= 0:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': '課税価格の合計額は正の値である必要があります'
                }
            }), 400
        
        # 家族構成の作成
        family_structure = FamilyStructure(
            spouse_exists=family_structure_data.get('spouse_exists', False),
            children_count=family_structure_data.get('children_count', 0),
            adopted_children_count=family_structure_data.get('adopted_children_count', 0),
            grandchild_adopted_count=family_structure_data.get('grandchild_adopted_count', 0),
            parents_alive=family_structure_data.get('parents_alive', 0),
            grandparents_alive=family_structure_data.get('grandparents_alive', 0),
            siblings_count=family_structure_data.get('siblings_count', 0),
            half_siblings_count=family_structure_data.get('half_siblings_count', 0),
            non_heirs_count=family_structure_data.get('non_heirs_count', 0)
        )
        
        # 法定相続人の判定
        legal_heirs = calculator.determine_legal_heirs(family_structure)
        
        # 相続税計算
        tax_result = calculator.calculate_tax_by_legal_share(taxable_amount, legal_heirs)
        
        # レスポンスの作成
        result = {
            'taxable_amount': taxable_amount,
            'taxable_amount_formatted': format_currency(taxable_amount),
            'legal_heirs': [
                {
                    'id': heir.id,
                    'name': heir.name,
                    'type': heir.heir_type.value,
                    'relationship': heir.relationship.value,
                    'inheritance_share': heir.inheritance_share,
                    'inheritance_share_formatted': format_percentage(heir.inheritance_share),
                    'legal_share_amount': int(taxable_amount * heir.inheritance_share),
                    'legal_share_amount_formatted': format_currency(int(taxable_amount * heir.inheritance_share)),
                    'two_fold_addition': heir.two_fold_addition
                } for heir in legal_heirs
            ],
            'basic_deduction': tax_result.basic_deduction,
            'basic_deduction_formatted': format_currency(tax_result.basic_deduction),
            'taxable_inheritance': tax_result.taxable_inheritance,
            'taxable_inheritance_formatted': format_currency(tax_result.taxable_inheritance),
            'total_tax_amount': tax_result.total_tax_amount,
            'total_tax_amount_formatted': format_currency(tax_result.total_tax_amount),
            'heir_tax_details': [
                {
                    'heir_id': detail.heir_id,
                    'heir_name': detail.name,
                    'relationship': detail.relationship,
                    'legal_share_amount': detail.legal_share_amount,
                    'legal_share_amount_formatted': format_currency(detail.legal_share_amount),
                    'tax_before_addition': detail.tax_before_addition,
                    'tax_before_addition_formatted': format_currency(detail.tax_before_addition),
                    'two_fold_addition': detail.two_fold_addition,
                    'two_fold_addition_formatted': format_currency(detail.two_fold_addition),
                    'tax_after_addition': detail.tax_after_addition,
                    'tax_after_addition_formatted': format_currency(detail.tax_after_addition)
                } for detail in tax_result.heir_tax_details
            ]
        }
        
        return jsonify({
            'success': True,
            'result': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_SERVER_ERROR',
                'message': str(e)
            }
        }), 500


@inheritance_bp.route('/calculation/actual-division', methods=['POST'])
def calculate_actual_division():
    """実際の分割による税額配分計算API"""
    try:
        data = request.get_json()
        
        # 入力データの取得
        taxable_amount = data.get('total_amount', 0)
        total_tax_amount = data.get('total_tax_amount', 0)
        heirs_data = data.get('heirs', [])
        
        # 相続人データの復元
        from src.models.inheritance import Heir, HeirType, RelationshipType
        heirs = []
        for heir_data in heirs_data:
            heirs.append(Heir(
                id=heir_data['id'],
                name=heir_data['name'],
                heir_type=HeirType(heir_data['type']),
                relationship=RelationshipType(heir_data['relationship']),
                inheritance_share=heir_data['inheritance_share'],
                two_fold_addition=heir_data.get('two_fold_addition', False),
                is_adopted=heir_data.get('is_adopted', False)
            ))
        
        # 分割入力データの作成
        division_input = DivisionInput(
            mode=data.get('mode', 'amount'),
            amounts=data.get('amounts'),
            percentages=data.get('percentages'),
            total_amount=taxable_amount,
            heirs=heirs,
            total_tax_amount=total_tax_amount,
            rounding_method=data.get('rounding_method', 'round')
        )
        
        # バリデーション
        validation_result = calculator.validate_division_input(division_input, heirs)
        if not validation_result.is_valid:
            return jsonify({
                'success': False,
                'error': {
                    'code': 'VALIDATION_ERROR',
                    'message': '分割入力データに問題があります',
                    'details': [
                        {
                            'field': error.field,
                            'code': error.code,
                            'message': error.message
                        } for error in validation_result.errors
                    ]
                }
            }), 400
        
        # 実際の分割割合で計算
        division_result = calculator.calculate_actual_division(division_input)

        # レスポンスの作成
        result = {
            'total_tax_amount': division_result.total_tax_amount,
            'total_tax_amount_formatted': format_currency(division_result.total_tax_amount),
            'heir_details': [
                {
                    'heir_id': detail.heir_id,
                    'heir_name': detail.heir_name,
                    'inheritance_amount': detail.inheritance_amount,
                    'inheritance_amount_formatted': format_currency(detail.inheritance_amount),
                    'tax_amount': detail.tax_amount,
                    'tax_amount_formatted': format_currency(detail.tax_amount),
                    'surcharge_deduction_amount': detail.surcharge_deduction_amount,
                    'surcharge_deduction_amount_formatted': format_currency(detail.surcharge_deduction_amount),
                    'final_tax_amount': detail.final_tax_amount,
                    'final_tax_amount_formatted': format_currency(detail.final_tax_amount),
                } for detail in division_result.heir_details
            ]
        }
        
        return jsonify({
            'success': True,
            'result': result
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_SERVER_ERROR',
                'message': str(e)
            }
        }), 500


@inheritance_bp.route('/utilities/tax-table', methods=['GET'])
def get_tax_table():
    """相続税速算表取得API"""
    try:
        from src.models.inheritance import TAX_TABLE
        
        return jsonify({
            'success': True,
            'data': {
                'tax_table': TAX_TABLE,
                'last_updated': '2025-06-30T00:00:00Z'
            }
        })
        
    except Exception as e:
        return jsonify({
            'success': False,
            'error': {
                'code': 'INTERNAL_SERVER_ERROR',
                'message': str(e)
            }
        }), 500


@inheritance_bp.route('/health', methods=['GET'])
def health_check():
    """ヘルスチェックAPI"""
    return jsonify({
        'status': 'healthy',
        'timestamp': '2025-06-30T10:30:00Z',
        'version': '1.0.0'
    })


# エラーハンドラー
@inheritance_bp.errorhandler(404)
def not_found(error):
    return jsonify({
        'success': False,
        'error': {
            'code': 'NOT_FOUND',
            'message': 'エンドポイントが見つかりません'
        }
    }), 404


@inheritance_bp.errorhandler(405)
def method_not_allowed(error):
    return jsonify({
        'success': False,
        'error': {
            'code': 'METHOD_NOT_ALLOWED',
            'message': '許可されていないHTTPメソッドです'
        }
    }), 405

