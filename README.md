# 相続税計算アプリ

日本の相続税計算に対応したWebアプリケーションです。法定相続人の判定から相続税の計算、実際の分割による税額配分まで、正確で簡単な相続税計算をサポートします。

## 機能概要

- **法定相続人の自動判定**: 家族構成に基づいて法定相続人を自動判定
- **相続税の正確な計算**: 国税庁の規定に基づいた相続税計算
- **2割加算の適用**: 孫養子や法定相続人以外への適切な2割加算
- **配偶者税額軽減**: 配偶者の法定相続分に応じた控除の適用
- **実際の分割計算**: 金額または割合での分割指定が可能
- **半血兄弟姉妹対応**: 半血兄弟姉妹の相続分を全血の1/2として計算

## プロジェクト構成

```
inheritance-tax-calculator/
├── docs/                           # ドキュメント
│   ├── PRD.md                     # プロダクト要求仕様書
│   ├── Structure.md               # システム構成書
│   ├── TestCases.md              # テストケース
│   ├── UserManual.md             # ユーザーマニュアル
│   ├── ProjectCompletionReport.md # プロジェクト完了報告書
│   ├── inheritance_requirements.md # 要件定義
│   └── todo.md                   # タスク管理
├── inheritance-tax-frontend/       # フロントエンド (React)
├── inheritance_tax_api/           # バックエンド (Flask)
├── test_api.py                   # APIテスト
├── test_backend.py               # バックエンドテスト
├── test_calculation_logic.py     # 計算ロジックテスト
└── README.md                     # このファイル
```

## セットアップ

### バックエンド (Flask API)

```bash
cd inheritance_tax_api
pip install flask flask-cors flask-sqlalchemy
python src/main.py
```

バックエンドは `http://localhost:5001` で起動します。

### フロントエンド (React)

```bash
cd inheritance-tax-frontend
npm install
npm run dev
```

フロントエンドは `http://localhost:5173` で起動します。

## API エンドポイント

- `POST /api/calculation/heirs` - 法定相続人判定
- `POST /api/calculation/tax-amount` - 相続税額計算
- `POST /api/calculation/division` - 実際の分割による税額配分

## テスト

```bash
# APIテスト
python test_api.py

# バックエンドテスト
python test_backend.py

# 計算ロジックテスト
python test_calculation_logic.py
```

## 技術スタック

### フロントエンド
- React 18
- Vite
- Tailwind CSS
- shadcn/ui
- Lucide React

### バックエンド
- Flask
- Flask-CORS
- Flask-SQLAlchemy
- Python 3.11

## 主要機能

### 1. 家族構成入力
- 配偶者の有無
- 子供の数（養子、孫養子を含む）
- 親の生存状況
- 兄弟姉妹の数（全血・半血の区別）
- 法定相続人以外の人数

### 2. 相続税計算
- 基礎控除額の自動計算
- 法定相続分による税額計算
- 配偶者税額軽減の適用
- 2割加算の適用

### 3. 実際の分割
- 金額または割合での分割指定
- 端数処理方法の選択
- 法定相続人以外の人の動的追加
- 税額配分の自動計算

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。

## 注意事項

この計算結果は参考値です。実際の税務申告においては税理士等の専門家にご相談ください。

