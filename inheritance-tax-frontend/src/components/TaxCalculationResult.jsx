import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { CheckCircle, Users, Calculator, AlertTriangle } from 'lucide-react'

const TaxCalculationResult = ({ result }) => {
  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('ja-JP', {
      style: 'currency',
      currency: 'JPY',
      minimumFractionDigits: 0
    }).format(amount)
  }

  const formatPercentage = (decimal) => {
    return (decimal * 100).toFixed(1) + '%'
  }

  return (
    <div className="space-y-6">
      {/* 計算結果サマリー */}
      <Card className="border-green-200 bg-green-50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-green-800">
            <CheckCircle className="h-5 w-5" />
            相続税計算結果
          </CardTitle>
          <CardDescription className="text-green-700">
            法定相続分による相続税の総額が計算されました
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <div className="text-center">
              <div className="text-2xl font-bold text-green-800 mb-1">
                {formatCurrency(result.basic_deduction)}
              </div>
              <div className="text-sm text-green-600">基礎控除額</div>
            </div>
            <div className="text-center">
              <div className="text-2xl font-bold text-blue-800 mb-1">
                {formatCurrency(result.taxable_inheritance)}
              </div>
              <div className="text-sm text-blue-600">課税遺産総額</div>
            </div>
            <div className="text-center">
              <div className="text-3xl font-bold text-red-800 mb-1">
                {formatCurrency(result.total_tax_amount)}
              </div>
              <div className="text-sm text-red-600">相続税の総額</div>
            </div>
          </div>
        </CardContent>
      </Card>

      {/* 法定相続人一覧 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Users className="h-5 w-5" />
            法定相続人と相続分
          </CardTitle>
          <CardDescription>
            判定された法定相続人と各々の法定相続分です
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {result.legal_heirs.map((heir, index) => (
              <div key={heir.id} className="flex items-center justify-between p-4 border rounded-lg">
                <div className="flex items-center gap-3">
                  <div className="w-8 h-8 bg-blue-100 text-blue-800 rounded-full flex items-center justify-center text-sm font-semibold">
                    {index + 1}
                  </div>
                  <div>
                    <div className="font-medium">{heir.name}</div>
                    <div className="text-sm text-gray-500">{heir.relationship}</div>
                  </div>
                </div>
                <div className="text-right">
                  <div className="font-medium">{formatPercentage(heir.inheritance_share)}</div>
                  {heir.two_fold_addition && (
                    <Badge variant="destructive" className="text-xs">
                      2割加算対象
                    </Badge>
                  )}
                </div>
              </div>
            ))}
          </div>
        </CardContent>
      </Card>

      {/* 税額計算詳細 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            <Calculator className="h-5 w-5" />
            税額計算の詳細
          </CardTitle>
          <CardDescription>
            各相続人の法定相続分に基づく税額計算の内訳です
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr className="border-b">
                  <th className="text-left p-3">相続人</th>
                  <th className="text-right p-3">法定相続分</th>
                  <th className="text-right p-3">税額（法定相続分による）</th>
                </tr>
              </thead>
              <tbody>
                {result.heir_tax_details.map((detail) => (
                  <tr key={detail.heir_id} className="border-b hover:bg-gray-50">
                    <td className="p-3">
                      <div>
                        <div className="font-medium">{detail.name}</div>
                        <div className="text-sm text-gray-500">{detail.relationship}</div>
                      </div>
                    </td>
                    <td className="text-right p-3">
                      {formatCurrency(detail.legal_share_amount)}
                    </td>
                    <td className="text-right p-3">
                      {formatCurrency(detail.tax_before_addition)}
                    </td>
                  </tr>
                ))}
                <tr className="border-b-2 border-gray-300 bg-gray-50">
                  <td className="p-3 font-semibold">合計</td>
                  <td className="text-right p-3 font-semibold">
                    {formatCurrency(result.taxable_inheritance + result.basic_deduction)}
                  </td>
                  <td className="text-right p-3 font-semibold text-red-800">
                    {formatCurrency(result.total_tax_amount)}
                  </td>
                </tr>
              </tbody>
            </table>
          </div>
        </CardContent>
      </Card>

      {/* 注意事項 */}
      <Card className="border-yellow-200 bg-yellow-50">
        <CardHeader>
          <CardTitle className="flex items-center gap-2 text-yellow-800">
            <AlertTriangle className="h-5 w-5" />
            重要な注意事項
          </CardTitle>
        </CardHeader>
        <CardContent className="text-yellow-800">
          <ul className="space-y-2 text-sm">
            <li>• この計算結果は法定相続分による相続税の総額です。</li>
            <li>• 実際の遺産分割が法定相続分と異なる場合は、「実際の分割」タブで再計算してください。</li>
            <li>• 配偶者控除、未成年者控除、障害者控除等の各種控除は含まれていません。</li>
            <li>• 実際の税務申告においては、税理士等の専門家にご相談ください。</li>
          </ul>
        </CardContent>
      </Card>
    </div>
  )
}

export default TaxCalculationResult

