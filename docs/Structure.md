# 相続税計算ウェブアプリ Structure文書（システム設計書）

**作成者**: Manus AI  
**作成日**: 2025年6月30日  
**バージョン**: 1.0  

## 1. システム概要

### 1.1 アーキテクチャ概要

相続税計算ウェブアプリケーションは、モダンなウェブアプリケーションアーキテクチャを採用し、フロントエンドとバックエンドを分離したSPA（Single Page Application）として設計されています。この設計により、ユーザー体験の向上、保守性の確保、拡張性の実現を図ります。

システム全体は以下の主要コンポーネントで構成されます：

**フロントエンド層**: React.jsベースのSPAとして実装され、ユーザーインターフェースとユーザー体験を担当します。TypeScriptを採用することで型安全性を確保し、開発効率と保守性を向上させます。Material-UIまたはAnt Designを使用してモダンで一貫性のあるUIコンポーネントを提供し、レスポンシブデザインによりデスクトップからモバイルまで幅広いデバイスに対応します。

**バックエンド層**: FlaskベースのRESTful APIサーバーとして実装され、相続税計算ロジックの実行とデータ処理を担当します。Pythonの豊富な数値計算ライブラリを活用し、複雑な相続税計算を正確に実行します。APIは明確に定義されたエンドポイントを提供し、フロントエンドとの疎結合を実現します。

**データ層**: 基本的にはステートレスな計算アプリケーションのため、永続化するデータは最小限に抑えます。必要に応じてRedisを使用してセッション管理やキャッシュ機能を提供します。ユーザーの入力データは主にブラウザのローカルストレージに保存し、プライバシーを保護します。

**インフラストラクチャ層**: クラウドベースのインフラストラクチャを採用し、スケーラビリティと可用性を確保します。Dockerコンテナ化により環境の一貫性を保ち、CI/CDパイプラインにより自動化されたデプロイメントを実現します。

### 1.2 設計原則

**単一責任の原則**: 各コンポーネントは明確に定義された単一の責任を持ちます。計算ロジック、UI表示、データ管理などの関心事を適切に分離し、保守性を向上させます。

**疎結合**: フロントエンドとバックエンドはRESTful APIを通じて通信し、互いに独立して開発・デプロイできる設計とします。これにより、技術スタックの変更や機能拡張が容易になります。

**再利用性**: 共通的な計算ロジックやUIコンポーネントは再利用可能な形で実装し、開発効率を向上させます。特に相続税計算の各種ルールは独立したモジュールとして実装し、テストと保守を容易にします。

**拡張性**: 将来的な機能追加や法改正への対応を考慮し、拡張しやすい設計とします。プラグイン的な機能追加や設定変更により、新しい計算ルールや控除制度に対応できる柔軟性を持たせます。

**セキュリティファースト**: セキュリティを設計の初期段階から考慮し、入力検証、データ暗号化、アクセス制御などを適切に実装します。個人の財産情報を扱うため、プライバシー保護を最優先に設計します。

## 2. システムアーキテクチャ

### 2.1 全体アーキテクチャ

```
┌─────────────────────────────────────────────────────────────┐
│                        ユーザー                              │
└─────────────────────┬───────────────────────────────────────┘
                      │ HTTPS
┌─────────────────────▼───────────────────────────────────────┐
│                   CDN / Load Balancer                       │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                 フロントエンド層                            │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   React SPA     │  │  Static Assets  │  │ Service      │ │
│  │                 │  │                 │  │ Worker       │ │
│  │ - Components    │  │ - CSS/Images    │  │              │ │
│  │ - State Mgmt    │  │ - Fonts         │  │ - Caching    │ │
│  │ - Routing       │  │ - Icons         │  │ - Offline    │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────┬───────────────────────────────────────┘
                      │ REST API (JSON)
┌─────────────────────▼───────────────────────────────────────┐
│                  バックエンド層                             │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │   Flask API     │  │  Calculation    │  │ Validation   │ │
│  │                 │  │  Engine         │  │ Layer        │ │
│  │ - Endpoints     │  │                 │  │              │ │
│  │ - Middleware    │  │ - Tax Rules     │  │ - Input      │ │
│  │ - Error Handle  │  │ - Heir Logic    │  │ - Business   │ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────┬───────────────────────────────────────┘
                      │
┌─────────────────────▼───────────────────────────────────────┐
│                   データ層                                  │
│  ┌─────────────────┐  ┌─────────────────┐  ┌──────────────┐ │
│  │     Redis       │  │   File System   │  │ Browser      │ │
│  │                 │  │                 │  │ Storage      │ │
│  │ - Session       │  │ - Tax Tables    │  │              │ │
│  │ - Cache         │  │ - Templates     │  │ - User Data  │ │
│  │ - Rate Limit    │  │ - Logs          │  │ - Preferences│ │
│  └─────────────────┘  └─────────────────┘  └──────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 コンポーネント詳細

#### 2.2.1 フロントエンド層

**React SPA コンポーネント**:

フロントエンドは React.js をベースとした Single Page Application として実装されます。コンポーネントベースの設計により、再利用性と保守性を確保します。

主要なコンポーネント構成：

```
src/
├── components/
│   ├── common/
│   │   ├── Header.tsx
│   │   ├── Footer.tsx
│   │   ├── Loading.tsx
│   │   └── ErrorBoundary.tsx
│   ├── forms/
│   │   ├── AssetInput.tsx
│   │   ├── FamilyStructure.tsx
│   │   ├── HeirSelection.tsx
│   │   └── ActualDivision.tsx
│   ├── results/
│   │   ├── TaxCalculation.tsx
│   │   ├── HeirList.tsx
│   │   ├── TaxBreakdown.tsx
│   │   └── FamilyTree.tsx
│   └── help/
│       ├── FAQ.tsx
│       ├── Glossary.tsx
│       └── Examples.tsx
├── hooks/
│   ├── useCalculation.ts
│   ├── useLocalStorage.ts
│   └── useValidation.ts
├── services/
│   ├── api.ts
│   ├── calculation.ts
│   └── validation.ts
├── types/
│   ├── family.ts
│   ├── tax.ts
│   └── api.ts
└── utils/
    ├── formatters.ts
    ├── validators.ts
    └── constants.ts
```

**状態管理**: React Context API または Redux Toolkit を使用して、アプリケーション全体の状態を管理します。相続税計算に必要な入力データ、計算結果、UI状態などを一元管理し、コンポーネント間でのデータ共有を効率化します。

**ルーティング**: React Router を使用してSPA内のナビゲーションを管理します。ユーザーの入力進捗に応じて適切なページを表示し、ブラウザの戻る・進むボタンにも対応します。

#### 2.2.2 バックエンド層

**Flask API サーバー**:

バックエンドは Flask を使用した RESTful API サーバーとして実装されます。軽量でありながら拡張性に優れた Flask の特性を活かし、効率的な API を提供します。

API エンドポイント設計：

```
/api/v1/
├── calculation/
│   ├── POST /heirs              # 法定相続人判定
│   ├── POST /basic-deduction    # 基礎控除計算
│   ├── POST /tax-amount         # 相続税額計算
│   ├── POST /two-fold-addition  # 2割加算計算
│   └── POST /actual-division    # 実際分割計算
├── validation/
│   ├── POST /family-structure   # 家族構成検証
│   ├── POST /asset-amount       # 資産額検証
│   └── POST /division-ratio     # 分割比率検証
└── utilities/
    ├── GET /tax-table           # 速算表取得
    ├── GET /legal-info          # 法的情報取得
    └── GET /health              # ヘルスチェック
```

**計算エンジン**: 相続税計算の核となる部分で、以下のモジュールで構成されます：

```python
calculation_engine/
├── __init__.py
├── heir_determination.py      # 法定相続人判定
├── basic_deduction.py         # 基礎控除計算
├── tax_calculation.py         # 相続税額計算
├── two_fold_addition.py       # 2割加算計算
├── actual_division.py         # 実際分割計算
├── validation.py              # 入力値検証
└── constants.py               # 定数定義
```

各モジュールは独立してテスト可能な設計とし、計算ロジックの正確性を保証します。

#### 2.2.3 データ層

**Redis キャッシュ**: セッション管理、計算結果のキャッシュ、レート制限の実装に使用します。メモリベースの高速アクセスにより、ユーザー体験を向上させます。

**ファイルシステム**: 相続税の速算表、法的情報、テンプレートファイルなどの静的データを保存します。これらのデータは読み取り専用で、アプリケーションの起動時に読み込まれます。

**ブラウザストレージ**: ユーザーの入力データは主にブラウザのローカルストレージに保存し、プライバシーを保護します。サーバーには計算に必要な最小限のデータのみを送信します。

### 2.3 セキュリティアーキテクチャ

**通信セキュリティ**: 全ての通信はHTTPS/TLSで暗号化されます。API通信においてもJWTトークンによる認証を実装し、不正アクセスを防止します。

**入力検証**: フロントエンドとバックエンドの両方で入力値の検証を実装します。SQLインジェクション、XSS攻撃などの一般的な脆弱性に対する対策を講じます。

**データ保護**: 個人情報は最小限の収集に留め、収集したデータは暗号化して保存します。GDPR等のプライバシー規制に準拠した設計とします。

**レート制限**: API呼び出しの頻度制限を実装し、DoS攻撃やスパム行為を防止します。Redis を使用してユーザー毎のリクエスト数を追跡します。



## 3. 詳細設計

### 3.1 フロントエンド詳細設計

#### 3.1.1 分割方式切り替え機能の設計

**概要**: ユーザーが遺産分割の入力方法を金額指定と割合指定で切り替えられる機能の詳細設計です。

**UI設計**:

分割方式選択インターフェース：
```tsx
interface DivisionModeSelector {
  mode: 'amount' | 'percentage';
  onModeChange: (mode: 'amount' | 'percentage') => void;
  hasExistingData: boolean;
}
```

分割入力コンポーネント：
```tsx
interface DivisionInput {
  heirs: Heir[];
  totalAmount: number;
  mode: 'amount' | 'percentage';
  values: DivisionValues;
  onValuesChange: (values: DivisionValues) => void;
  roundingMethod: 'round' | 'floor' | 'ceil';
  onRoundingMethodChange: (method: string) => void;
}

interface DivisionValues {
  amounts?: { [heirId: string]: number };
  percentages?: { [heirId: string]: number };
}
```

**状態管理設計**:

分割データの状態管理：
```typescript
interface DivisionState {
  mode: 'amount' | 'percentage';
  amounts: { [heirId: string]: number };
  percentages: { [heirId: string]: number };
  roundingMethod: 'round' | 'floor' | 'ceil';
  isValid: boolean;
  errors: ValidationError[];
}

// 状態更新アクション
type DivisionAction = 
  | { type: 'SET_MODE'; payload: 'amount' | 'percentage' }
  | { type: 'SET_AMOUNT'; payload: { heirId: string; amount: number } }
  | { type: 'SET_PERCENTAGE'; payload: { heirId: string; percentage: number } }
  | { type: 'SET_ROUNDING_METHOD'; payload: 'round' | 'floor' | 'ceil' }
  | { type: 'CONVERT_MODE'; payload: { fromMode: string; toMode: string } };
```

**変換ロジック設計**:

金額から割合への変換：
```typescript
function convertAmountToPercentage(
  amounts: { [heirId: string]: number },
  totalAmount: number
): { [heirId: string]: number } {
  const percentages: { [heirId: string]: number } = {};
  
  Object.entries(amounts).forEach(([heirId, amount]) => {
    percentages[heirId] = Math.round((amount / totalAmount) * 10000) / 100;
  });
  
  return percentages;
}
```

割合から金額への変換：
```typescript
function convertPercentageToAmount(
  percentages: { [heirId: string]: number },
  totalAmount: number,
  roundingMethod: 'round' | 'floor' | 'ceil'
): { [heirId: string]: number } {
  const amounts: { [heirId: string]: number } = {};
  let remainingAmount = totalAmount;
  const heirIds = Object.keys(percentages);
  
  // 最後の相続人以外を計算
  for (let i = 0; i < heirIds.length - 1; i++) {
    const heirId = heirIds[i];
    const percentage = percentages[heirId];
    let amount = (totalAmount * percentage) / 100;
    
    // 端数処理
    switch (roundingMethod) {
      case 'round':
        amount = Math.round(amount);
        break;
      case 'floor':
        amount = Math.floor(amount);
        break;
      case 'ceil':
        amount = Math.ceil(amount);
        break;
    }
    
    amounts[heirId] = amount;
    remainingAmount -= amount;
  }
  
  // 最後の相続人は残額を割り当て（端数調整）
  const lastHeirId = heirIds[heirIds.length - 1];
  amounts[lastHeirId] = remainingAmount;
  
  return amounts;
}
```

**バリデーション設計**:

入力値検証ルール：
```typescript
interface ValidationRule {
  field: string;
  validator: (value: any, context: any) => ValidationResult;
  message: string;
}

const divisionValidationRules: ValidationRule[] = [
  {
    field: 'amounts',
    validator: (amounts, context) => {
      const total = Object.values(amounts).reduce((sum, amount) => sum + amount, 0);
      return {
        isValid: Math.abs(total - context.totalAmount) < 1,
        error: total !== context.totalAmount ? 'AMOUNT_TOTAL_MISMATCH' : null
      };
    },
    message: '取得金額の合計が課税価格の合計額と一致しません'
  },
  {
    field: 'percentages',
    validator: (percentages) => {
      const total = Object.values(percentages).reduce((sum, pct) => sum + pct, 0);
      return {
        isValid: Math.abs(total - 100) < 0.01,
        error: Math.abs(total - 100) >= 0.01 ? 'PERCENTAGE_TOTAL_INVALID' : null
      };
    },
    message: '取得割合の合計が100%になりません'
  }
];
```

#### 3.1.2 UIコンポーネント設計

**分割方式選択コンポーネント**:
```tsx
const DivisionModeSelector: React.FC<DivisionModeSelectorProps> = ({
  mode,
  onModeChange,
  hasExistingData
}) => {
  const handleModeChange = (newMode: 'amount' | 'percentage') => {
    if (hasExistingData) {
      // 確認ダイアログを表示
      showConfirmDialog({
        title: '分割方式の変更',
        message: '入力済みのデータが変換されます。続行しますか？',
        onConfirm: () => onModeChange(newMode)
      });
    } else {
      onModeChange(newMode);
    }
  };

  return (
    <div className="division-mode-selector">
      <RadioGroup value={mode} onChange={handleModeChange}>
        <Radio value="amount">金額で指定</Radio>
        <Radio value="percentage">割合（％）で指定</Radio>
      </RadioGroup>
    </div>
  );
};
```

**分割入力テーブルコンポーネント**:
```tsx
const DivisionInputTable: React.FC<DivisionInputTableProps> = ({
  heirs,
  mode,
  values,
  onValuesChange,
  totalAmount,
  roundingMethod
}) => {
  const renderInputCell = (heir: Heir) => {
    if (mode === 'amount') {
      return (
        <NumberInput
          value={values.amounts?.[heir.id] || 0}
          onChange={(value) => onValuesChange({
            ...values,
            amounts: { ...values.amounts, [heir.id]: value }
          })}
          suffix="円"
          formatter={(value) => formatCurrency(value)}
        />
      );
    } else {
      return (
        <NumberInput
          value={values.percentages?.[heir.id] || 0}
          onChange={(value) => onValuesChange({
            ...values,
            percentages: { ...values.percentages, [heir.id]: value }
          })}
          suffix="%"
          precision={2}
          max={100}
          min={0}
        />
      );
    }
  };

  return (
    <Table>
      <TableHeader>
        <TableRow>
          <TableCell>相続人</TableCell>
          <TableCell>続柄</TableCell>
          <TableCell>
            {mode === 'amount' ? '取得金額' : '取得割合'}
          </TableCell>
          {mode === 'percentage' && <TableCell>換算金額</TableCell>}
        </TableRow>
      </TableHeader>
      <TableBody>
        {heirs.map(heir => (
          <TableRow key={heir.id}>
            <TableCell>{heir.name}</TableCell>
            <TableCell>{heir.relationship}</TableCell>
            <TableCell>{renderInputCell(heir)}</TableCell>
            {mode === 'percentage' && (
              <TableCell>
                {formatCurrency(calculateAmountFromPercentage(
                  values.percentages?.[heir.id] || 0,
                  totalAmount,
                  roundingMethod
                ))}
              </TableCell>
            )}
          </TableRow>
        ))}
      </TableBody>
    </Table>
  );
};
```

### 3.2 バックエンド詳細設計

#### 3.2.1 API エンドポイント拡張

分割計算APIの拡張：
```python
@app.route('/api/v1/calculation/actual-division', methods=['POST'])
def calculate_actual_division():
    data = request.get_json()
    
    # 入力データの検証
    validation_result = validate_division_input(data)
    if not validation_result.is_valid:
        return jsonify({
            'error': 'VALIDATION_ERROR',
            'details': validation_result.errors
        }), 400
    
    try:
        # 分割方式に応じた処理
        if data['mode'] == 'amount':
            division_amounts = data['amounts']
        else:  # percentage
            division_amounts = convert_percentage_to_amount(
                data['percentages'],
                data['total_amount'],
                data.get('rounding_method', 'round')
            )
        
        # 税額計算
        result = calculate_tax_by_actual_division(
            heirs=data['heirs'],
            division_amounts=division_amounts,
            total_tax_amount=data['total_tax_amount']
        )
        
        return jsonify({
            'success': True,
            'result': result,
            'division_amounts': division_amounts
        })
        
    except Exception as e:
        return jsonify({
            'error': 'CALCULATION_ERROR',
            'message': str(e)
        }), 500
```

#### 3.2.2 計算ロジック実装

分割計算エンジンの実装：
```python
class DivisionCalculator:
    def __init__(self):
        self.rounding_methods = {
            'round': round,
            'floor': math.floor,
            'ceil': math.ceil
        }
    
    def convert_percentage_to_amount(
        self,
        percentages: Dict[str, float],
        total_amount: int,
        rounding_method: str = 'round'
    ) -> Dict[str, int]:
        """割合から金額への変換"""
        amounts = {}
        remaining_amount = total_amount
        heir_ids = list(percentages.keys())
        
        # 最後の相続人以外を計算
        for heir_id in heir_ids[:-1]:
            percentage = percentages[heir_id]
            amount = (total_amount * percentage) / 100
            
            # 端数処理
            rounding_func = self.rounding_methods[rounding_method]
            amount = int(rounding_func(amount))
            
            amounts[heir_id] = amount
            remaining_amount -= amount
        
        # 最後の相続人は残額を割り当て
        amounts[heir_ids[-1]] = remaining_amount
        
        return amounts
    
    def convert_amount_to_percentage(
        self,
        amounts: Dict[str, int],
        total_amount: int
    ) -> Dict[str, float]:
        """金額から割合への変換"""
        percentages = {}
        
        for heir_id, amount in amounts.items():
            percentage = (amount / total_amount) * 100
            # 小数点以下2桁で四捨五入
            percentages[heir_id] = round(percentage, 2)
        
        return percentages
    
    def validate_division_input(self, data: Dict) -> ValidationResult:
        """分割入力データの検証"""
        errors = []
        
        if data['mode'] == 'amount':
            amounts = data.get('amounts', {})
            total_input = sum(amounts.values())
            expected_total = data.get('total_amount', 0)
            
            if abs(total_input - expected_total) > 0:
                errors.append({
                    'field': 'amounts',
                    'code': 'TOTAL_MISMATCH',
                    'message': f'金額の合計({total_input:,}円)が課税価格の合計額({expected_total:,}円)と一致しません'
                })
        
        elif data['mode'] == 'percentage':
            percentages = data.get('percentages', {})
            total_percentage = sum(percentages.values())
            
            if abs(total_percentage - 100) > 0.01:
                errors.append({
                    'field': 'percentages',
                    'code': 'PERCENTAGE_TOTAL_INVALID',
                    'message': f'割合の合計({total_percentage}%)が100%になりません'
                })
        
        return ValidationResult(
            is_valid=len(errors) == 0,
            errors=errors
        )
```

### 3.3 データモデル設計

#### 3.3.1 分割データモデル

```typescript
// フロントエンド型定義
interface DivisionData {
  mode: 'amount' | 'percentage';
  amounts: { [heirId: string]: number };
  percentages: { [heirId: string]: number };
  roundingMethod: 'round' | 'floor' | 'ceil';
  totalAmount: number;
  isValid: boolean;
  validationErrors: ValidationError[];
}

interface ValidationError {
  field: string;
  code: string;
  message: string;
}

interface DivisionResult {
  heirId: string;
  name: string;
  relationship: string;
  amount: number;
  percentage: number;
  taxAmount: number;
  taxAmountWithAddition: number;
  finalTaxAmount: number;
}
```

```python
# バックエンドデータクラス
from dataclasses import dataclass
from typing import Dict, List, Optional

@dataclass
class DivisionInput:
    mode: str  # 'amount' or 'percentage'
    amounts: Optional[Dict[str, int]] = None
    percentages: Optional[Dict[str, float]] = None
    total_amount: int = 0
    rounding_method: str = 'round'

@dataclass
class DivisionResult:
    heir_id: str
    name: str
    relationship: str
    amount: int
    percentage: float
    tax_amount: int
    tax_amount_with_addition: int
    final_tax_amount: int

@dataclass
class ValidationResult:
    is_valid: bool
    errors: List[Dict[str, str]]
```

この設計により、ユーザーは金額指定と割合指定を自由に切り替えながら、直感的に遺産分割の計算を行うことができます。端数処理の選択肢も提供することで、より実用的なツールとなります。


## 4. データベース設計

### 4.1 データベース構成

相続税計算アプリケーションは基本的にステートレスな計算ツールとして設計されているため、永続化が必要なデータは最小限に抑えられています。主要なデータストレージは以下の通りです：

**Redis（インメモリデータベース）**:
- セッション管理
- 計算結果の一時キャッシュ
- レート制限カウンター
- アプリケーション設定

**ファイルシステム**:
- 相続税速算表
- 法定相続人判定ルール
- アプリケーション設定ファイル
- ログファイル

**ブラウザローカルストレージ**:
- ユーザー入力データ
- 計算履歴
- ユーザー設定

### 4.2 Redisデータ構造

```redis
# セッション管理
session:{session_id} = {
  "user_id": "anonymous_user_123",
  "created_at": "2025-06-30T10:00:00Z",
  "last_accessed": "2025-06-30T10:30:00Z",
  "data": {
    "calculation_state": "in_progress",
    "current_step": "family_structure"
  }
}

# 計算結果キャッシュ
calculation:{hash} = {
  "input_data": {...},
  "result": {...},
  "calculated_at": "2025-06-30T10:30:00Z",
  "expires_at": "2025-06-30T11:30:00Z"
}

# レート制限
rate_limit:{ip_address}:{endpoint} = {
  "count": 10,
  "window_start": "2025-06-30T10:00:00Z",
  "expires_at": "2025-06-30T11:00:00Z"
}
```

### 4.3 ファイルベースデータ

**相続税速算表（tax_table.json）**:
```json
{
  "inheritance_tax_table": [
    {
      "min_amount": 0,
      "max_amount": 10000000,
      "tax_rate": 0.10,
      "deduction": 0
    },
    {
      "min_amount": 10000001,
      "max_amount": 30000000,
      "tax_rate": 0.15,
      "deduction": 500000
    }
  ]
}
```

**法定相続人判定ルール（heir_rules.json）**:
```json
{
  "inheritance_order": [
    {
      "order": 1,
      "type": "descendants",
      "description": "子供（直系卑属）",
      "inheritance_share": {
        "with_spouse": 0.5,
        "without_spouse": 1.0
      }
    },
    {
      "order": 2,
      "type": "ascendants",
      "description": "父母（直系尊属）",
      "inheritance_share": {
        "with_spouse": 0.33333,
        "without_spouse": 1.0
      }
    }
  ]
}
```

## 5. API設計

### 5.1 RESTful API エンドポイント

**ベースURL**: `https://api.inheritance-tax-calculator.com/api/v1`

#### 5.1.1 計算関連エンドポイント

```yaml
# 法定相続人判定
POST /calculation/heirs
Content-Type: application/json

Request:
{
  "spouse_exists": true,
  "children_count": 2,
  "adopted_children_count": 1,
  "parents_alive": 0,
  "siblings_count": 0
}

Response:
{
  "success": true,
  "result": {
    "legal_heirs": [
      {
        "id": "spouse_1",
        "type": "spouse",
        "name": "配偶者",
        "inheritance_share": 0.5,
        "two_fold_addition": false
      },
      {
        "id": "child_1",
        "type": "child",
        "name": "子供1",
        "inheritance_share": 0.25,
        "two_fold_addition": false
      }
    ],
    "total_heirs_count": 3,
    "basic_deduction": 48000000
  }
}
```

```yaml
# 相続税計算
POST /calculation/tax-amount
Content-Type: application/json

Request:
{
  "taxable_amount": 246000000,
  "legal_heirs": [...],
  "basic_deduction": 48000000
}

Response:
{
  "success": true,
  "result": {
    "taxable_inheritance": 198000000,
    "total_tax_amount": 39600000,
    "heir_tax_details": [
      {
        "heir_id": "spouse_1",
        "legal_share_amount": 99000000,
        "tax_before_addition": 19800000,
        "two_fold_addition": 0,
        "tax_after_addition": 19800000
      }
    ]
  }
}
```

```yaml
# 実際分割による税額配分
POST /calculation/actual-division
Content-Type: application/json

Request:
{
  "mode": "percentage",
  "total_amount": 246000000,
  "total_tax_amount": 39600000,
  "heirs": [...],
  "percentages": {
    "spouse_1": 60.0,
    "child_1": 25.0,
    "child_2": 15.0
  },
  "rounding_method": "round"
}

Response:
{
  "success": true,
  "result": {
    "division_amounts": {
      "spouse_1": 147600000,
      "child_1": 61500000,
      "child_2": 36900000
    },
    "tax_allocation": [
      {
        "heir_id": "spouse_1",
        "actual_amount": 147600000,
        "actual_percentage": 60.0,
        "allocated_tax": 23760000,
        "final_tax": 23760000
      }
    ]
  }
}
```

#### 5.1.2 検証関連エンドポイント

```yaml
# 入力値検証
POST /validation/input
Content-Type: application/json

Request:
{
  "type": "family_structure",
  "data": {
    "spouse_exists": true,
    "children_count": -1
  }
}

Response:
{
  "success": false,
  "errors": [
    {
      "field": "children_count",
      "code": "INVALID_RANGE",
      "message": "子供の数は0以上の整数である必要があります"
    }
  ]
}
```

#### 5.1.3 ユーティリティエンドポイント

```yaml
# 速算表取得
GET /utilities/tax-table

Response:
{
  "success": true,
  "data": {
    "tax_table": [...],
    "last_updated": "2025-06-30T00:00:00Z"
  }
}

# ヘルスチェック
GET /health

Response:
{
  "status": "healthy",
  "timestamp": "2025-06-30T10:30:00Z",
  "version": "1.0.0"
}
```

### 5.2 エラーハンドリング

```yaml
# 標準エラーレスポンス
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "入力値に問題があります",
    "details": [
      {
        "field": "taxable_amount",
        "code": "REQUIRED",
        "message": "課税価格の合計額は必須です"
      }
    ]
  },
  "timestamp": "2025-06-30T10:30:00Z",
  "request_id": "req_123456789"
}
```

**エラーコード一覧**:
- `VALIDATION_ERROR`: 入力値検証エラー
- `CALCULATION_ERROR`: 計算処理エラー
- `RATE_LIMIT_EXCEEDED`: レート制限超過
- `INTERNAL_SERVER_ERROR`: サーバー内部エラー

## 6. UI/UX設計

### 6.1 デザインシステム

#### 6.1.1 カラーパレット

```css
:root {
  /* プライマリカラー */
  --primary-50: #f0f9ff;
  --primary-100: #e0f2fe;
  --primary-500: #0ea5e9;
  --primary-600: #0284c7;
  --primary-700: #0369a1;

  /* セカンダリカラー */
  --secondary-50: #fafaf9;
  --secondary-100: #f5f5f4;
  --secondary-500: #78716c;
  --secondary-600: #57534e;

  /* ステータスカラー */
  --success-500: #10b981;
  --warning-500: #f59e0b;
  --error-500: #ef4444;
  --info-500: #3b82f6;

  /* ニュートラルカラー */
  --gray-50: #f9fafb;
  --gray-100: #f3f4f6;
  --gray-200: #e5e7eb;
  --gray-300: #d1d5db;
  --gray-400: #9ca3af;
  --gray-500: #6b7280;
  --gray-600: #4b5563;
  --gray-700: #374151;
  --gray-800: #1f2937;
  --gray-900: #111827;
}
```

#### 6.1.2 タイポグラフィ

```css
/* フォントファミリー */
--font-sans: 'Noto Sans JP', -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
--font-mono: 'JetBrains Mono', 'Fira Code', monospace;

/* フォントサイズ */
--text-xs: 0.75rem;    /* 12px */
--text-sm: 0.875rem;   /* 14px */
--text-base: 1rem;     /* 16px */
--text-lg: 1.125rem;   /* 18px */
--text-xl: 1.25rem;    /* 20px */
--text-2xl: 1.5rem;    /* 24px */
--text-3xl: 1.875rem;  /* 30px */
--text-4xl: 2.25rem;   /* 36px */

/* 行間 */
--leading-tight: 1.25;
--leading-normal: 1.5;
--leading-relaxed: 1.625;
```

#### 6.1.3 スペーシング

```css
/* スペーシングシステム */
--space-1: 0.25rem;   /* 4px */
--space-2: 0.5rem;    /* 8px */
--space-3: 0.75rem;   /* 12px */
--space-4: 1rem;      /* 16px */
--space-5: 1.25rem;   /* 20px */
--space-6: 1.5rem;    /* 24px */
--space-8: 2rem;      /* 32px */
--space-10: 2.5rem;   /* 40px */
--space-12: 3rem;     /* 48px */
--space-16: 4rem;     /* 64px */
```

### 6.2 レスポンシブデザイン

#### 6.2.1 ブレークポイント

```css
/* ブレークポイント定義 */
--breakpoint-sm: 640px;   /* スマートフォン */
--breakpoint-md: 768px;   /* タブレット */
--breakpoint-lg: 1024px;  /* デスクトップ */
--breakpoint-xl: 1280px;  /* 大画面デスクトップ */
```

#### 6.2.2 レイアウトグリッド

```css
.container {
  width: 100%;
  margin: 0 auto;
  padding: 0 var(--space-4);
}

@media (min-width: 640px) {
  .container { max-width: 640px; }
}

@media (min-width: 768px) {
  .container { max-width: 768px; }
}

@media (min-width: 1024px) {
  .container { max-width: 1024px; }
}

@media (min-width: 1280px) {
  .container { max-width: 1280px; }
}
```

### 6.3 コンポーネント設計

#### 6.3.1 フォームコンポーネント

```tsx
// 数値入力コンポーネント
interface NumberInputProps {
  label: string;
  value: number;
  onChange: (value: number) => void;
  min?: number;
  max?: number;
  step?: number;
  suffix?: string;
  prefix?: string;
  error?: string;
  required?: boolean;
  disabled?: boolean;
}

const NumberInput: React.FC<NumberInputProps> = ({
  label,
  value,
  onChange,
  min,
  max,
  step = 1,
  suffix,
  prefix,
  error,
  required,
  disabled
}) => {
  return (
    <div className="number-input">
      <label className="number-input__label">
        {label}
        {required && <span className="required">*</span>}
      </label>
      <div className="number-input__wrapper">
        {prefix && <span className="number-input__prefix">{prefix}</span>}
        <input
          type="number"
          value={value}
          onChange={(e) => onChange(Number(e.target.value))}
          min={min}
          max={max}
          step={step}
          disabled={disabled}
          className={`number-input__field ${error ? 'error' : ''}`}
        />
        {suffix && <span className="number-input__suffix">{suffix}</span>}
      </div>
      {error && <span className="number-input__error">{error}</span>}
    </div>
  );
};
```

#### 6.3.2 結果表示コンポーネント

```tsx
// 計算結果表示コンポーネント
interface TaxCalculationResultProps {
  result: TaxCalculationResult;
  showDetails?: boolean;
}

const TaxCalculationResult: React.FC<TaxCalculationResultProps> = ({
  result,
  showDetails = false
}) => {
  return (
    <div className="tax-result">
      <div className="tax-result__summary">
        <h3>相続税の総額</h3>
        <div className="tax-result__total">
          {formatCurrency(result.totalTaxAmount)}
        </div>
      </div>
      
      {showDetails && (
        <div className="tax-result__details">
          <h4>計算内訳</h4>
          <table className="tax-result__table">
            <thead>
              <tr>
                <th>相続人</th>
                <th>法定相続分</th>
                <th>相続税額</th>
                <th>2割加算</th>
                <th>最終税額</th>
              </tr>
            </thead>
            <tbody>
              {result.heirDetails.map(heir => (
                <tr key={heir.id}>
                  <td>{heir.name}</td>
                  <td>{formatCurrency(heir.legalShareAmount)}</td>
                  <td>{formatCurrency(heir.taxBeforeAddition)}</td>
                  <td>{formatCurrency(heir.twoFoldAddition)}</td>
                  <td>{formatCurrency(heir.finalTaxAmount)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
};
```

### 6.4 アクセシビリティ

#### 6.4.1 WCAG 2.1 AA準拠

- **キーボードナビゲーション**: 全ての機能がキーボードのみで操作可能
- **スクリーンリーダー対応**: 適切なARIAラベルとランドマークの設定
- **色覚対応**: 色だけに依存しない情報伝達
- **コントラスト比**: テキストと背景のコントラスト比4.5:1以上

#### 6.4.2 実装例

```tsx
// アクセシブルなフォーム実装
<form role="form" aria-labelledby="form-title">
  <h2 id="form-title">家族構成の入力</h2>
  
  <fieldset>
    <legend>配偶者の有無</legend>
    <div role="radiogroup" aria-labelledby="spouse-label">
      <input
        type="radio"
        id="spouse-yes"
        name="spouse"
        value="yes"
        aria-describedby="spouse-help"
      />
      <label htmlFor="spouse-yes">有</label>
      
      <input
        type="radio"
        id="spouse-no"
        name="spouse"
        value="no"
        aria-describedby="spouse-help"
      />
      <label htmlFor="spouse-no">無</label>
    </div>
    <div id="spouse-help" className="help-text">
      被相続人の配偶者が存命かどうかを選択してください
    </div>
  </fieldset>
</form>
```

この詳細設計により、ユーザビリティとアクセシビリティを両立した高品質なウェブアプリケーションの実装が可能になります。

