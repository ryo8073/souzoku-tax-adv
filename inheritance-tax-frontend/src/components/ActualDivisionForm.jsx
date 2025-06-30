import { useState, useEffect } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Label } from '@/components/ui/label.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Badge } from '@/components/ui/badge.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Calculator, AlertCircle, ToggleLeft, ToggleRight, RefreshCw, Plus, Minus } from 'lucide-react'

const ActualDivisionForm = ({ heirs, totalAmount, onSubmit, result }) => {
  const [divisionMode, setDivisionMode] = useState('amount') // 'amount' or 'percentage'
  const [amounts, setAmounts] = useState({})
  const [percentages, setPercentages] = useState({})
  const [roundingMethod, setRoundingMethod] = useState('round')
  const [errors, setErrors] = useState({})
  const [isSubmitting, setIsSubmitting] = useState(false)

  // 初期値の設定
  useEffect(() => {
    if (heirs.length > 0) {
      const initialAmounts = {}
      let distributedAmount = 0
      
      // 法定相続分に基づいて初期金額を割り当て
      heirs.forEach((heir, index) => {
        if (index < heirs.length - 1) {
          const amount = Math.round(totalAmount * (heir.inheritance_share || 0))
          initialAmounts[heir.id] = amount
          distributedAmount += amount
        } else {
          // 最後の相続人で端数調整
          initialAmounts[heir.id] = totalAmount - distributedAmount
        }
      })
      
      setAmounts(initialAmounts)
      setPercentages(convertAmountToPercentage(initialAmounts, totalAmount))
    }
  }, [heirs, totalAmount])

  // 割合が変更されたら金額を更新
  useEffect(() => {
    if (divisionMode === 'percentage') {
      const newAmounts = convertPercentageToAmount(percentages, totalAmount, roundingMethod);
      setAmounts(newAmounts);
    }
  }, [percentages, roundingMethod, divisionMode, totalAmount]);

  // 金額が変更されたら割合を更新
  useEffect(() => {
    if (divisionMode === 'amount') {
      const newPercentages = convertAmountToPercentage(amounts, totalAmount);
      setPercentages(newPercentages);
    }
  }, [amounts, divisionMode, totalAmount]);

  const formatCurrency = (amount) => {
    if (amount === null || typeof amount === 'undefined') return ''
    return new Intl.NumberFormat('ja-JP').format(amount) + '円'
  }

  const convertAmountToPercentage = (currentAmounts, total) => {
    const newPercentages = {}
    Object.keys(currentAmounts).forEach((heirId) => {
      const amount = currentAmounts[heirId] || 0
      newPercentages[heirId] = total > 0 ? parseFloat(((amount / total) * 100).toFixed(5)) : 0
    })
    return newPercentages
  }

  const convertPercentageToAmount = (currentPercentages, total, rounding) => {
    const newAmounts = {}
    const heirIds = Object.keys(currentPercentages)
    let remainingAmount = total
    
    heirIds.slice(0, -1).forEach(heirId => {
      const percentage = currentPercentages[heirId] || 0
      let amount = (total * percentage) / 100
      
      switch (rounding) {
        case 'round': amount = Math.round(amount); break
        case 'floor': amount = Math.floor(amount); break
        case 'ceil':  amount = Math.ceil(amount); break
        default:      amount = Math.round(amount)
      }
      
      newAmounts[heirId] = amount
      remainingAmount -= amount
    })
    
    if (heirIds.length > 0) {
      newAmounts[heirIds[heirIds.length - 1]] = remainingAmount
    }
    
    return newAmounts
  }

  const handleModeChange = (newMode) => {
    if (newMode === divisionMode) return
    setDivisionMode(newMode)
    setErrors({})
  }

  const handleAmountChange = (heirId, value) => {
    const parsedValue = parseInt(value.replace(/,/g, ''), 10)
    setAmounts(prev => ({
      ...prev,
      [heirId]: isNaN(parsedValue) ? 0 : parsedValue
    }))
  }

  const handlePercentageChange = (heirId, value) => {
    const parsedValue = parseFloat(value)
    setPercentages(prev => ({
      ...prev,
      [heirId]: isNaN(parsedValue) ? 0 : parsedValue
    }))
  }

  const handleRoundingMethodChange = (method) => {
    setRoundingMethod(method)
  }

  const validateForm = () => {
    const newErrors = {}
    
    if (divisionMode === 'amount') {
      const currentAmounts = divisionMode === 'amount' ? amounts : convertPercentageToAmount(percentages, totalAmount, roundingMethod)
      const totalInput = Object.values(currentAmounts).reduce((sum, amount) => sum + (amount || 0), 0)
      if (Math.abs(totalInput - totalAmount) !== 0) {
        newErrors.total = `金額の合計(${formatCurrency(totalInput)})が課税価格の合計額(${formatCurrency(totalAmount)})と一致しません`
      }
    } else {
      const totalPercentage = Object.values(percentages).reduce((sum, percentage) => sum + (percentage || 0), 0)
      if (Math.abs(totalPercentage - 100) > 0.001) {
        newErrors.total = `割合の合計(${totalPercentage.toFixed(2)}%)が100%になりません`
      }
    }
    
    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!validateForm()) return
    
    setIsSubmitting(true)
    
    const finalAmounts = divisionMode === 'amount' ? amounts : convertPercentageToAmount(percentages, totalAmount, roundingMethod)

    const divisionData = {
      mode: 'amount', // Backend now receives amounts
      total_amount: totalAmount,
      amounts: finalAmounts
    }
    
    try {
      await onSubmit(divisionData)
    } catch (error) {
      console.error('分割計算エラー:', error)
      setErrors({ submit: '計算の実行中にエラーが発生しました。' })
    } finally {
      setIsSubmitting(false)
    }
  }

  const resetToLegalShare = () => {
    const initialAmounts = {}
    let distributedAmount = 0
    heirs.forEach((heir, index) => {
      if (index < heirs.length - 1) {
        const amount = Math.round(totalAmount * (heir.inheritance_share || 0))
        initialAmounts[heir.id] = amount
        distributedAmount += amount
      } else {
        initialAmounts[heir.id] = totalAmount - distributedAmount
      }
    })
    setAmounts(initialAmounts)
    setPercentages(convertAmountToPercentage(initialAmounts, totalAmount))
    setErrors({})
  }
  
  const currentAmounts = divisionMode === 'amount' ? amounts : convertPercentageToAmount(percentages, totalAmount, roundingMethod)
  const totalDisplayAmount = Object.values(currentAmounts).reduce((sum, val) => sum + (val || 0), 0)
  const totalDisplayPercentage = Object.values(percentages).reduce((sum, val) => sum + (val || 0), 0)

  return (
    <div className="space-y-6">
      {/* 分割方式選択 */}
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center gap-2">
            {divisionMode === 'amount' ? <ToggleLeft className="h-5 w-5" /> : <ToggleRight className="h-5 w-5" />}
            分割方式の選択
          </CardTitle>
          <CardDescription>
            遺産分割の入力方法を選択してください。いつでも切り替えることができます。
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Tabs value={divisionMode} onValueChange={handleModeChange} className="w-full">
            <TabsList className="grid w-full grid-cols-2">
              <TabsTrigger value="amount">金額で指定</TabsTrigger>
              <TabsTrigger value="percentage">割合（％）で指定</TabsTrigger>
            </TabsList>
          </Tabs>
          
          {divisionMode === 'percentage' && (
            <div className="mt-4">
              <Label htmlFor="roundingMethod">端数処理方法</Label>
              <Select value={roundingMethod} onValueChange={handleRoundingMethodChange}>
                <SelectTrigger className="w-48">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="round">四捨五入</SelectItem>
                  <SelectItem value="floor">切り捨て</SelectItem>
                  <SelectItem value="ceil">切り上げ</SelectItem>
                </SelectContent>
              </Select>
              <p className="text-sm text-gray-500 mt-1">
                割合から金額への変換時の端数処理方法を選択してください
              </p>
            </div>
          )}
        </CardContent>
      </Card>

      {/* 分割入力フォーム */}
      <form onSubmit={handleSubmit}>
        <Card>
          <CardHeader>
            <CardTitle className="flex items-center justify-between">
              <span>遺産分割の入力</span>
              <div className="flex gap-2">
                <Button type="button" variant="outline" size="sm" onClick={resetToLegalShare}>
                  <RefreshCw className="h-4 w-4 mr-2" />
                  法定相続分に戻す
                </Button>
              </div>
            </CardTitle>
            <CardDescription>
              各相続人の実際の取得{divisionMode === 'amount' ? '金額' : '割合'}を入力してください。法定相続人以外の人（遺贈を受ける人など）も追加できます。
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full border-collapse">
                <thead>
                  <tr className="border-b">
                    <th className="text-left p-3">相続人</th>
                    <th className="text-right p-3">法定相続分</th>
                    <th className="text-right p-3">
                      実際の取得{divisionMode === 'amount' ? '金額' : '割合'}
                    </th>
                    {divisionMode === 'percentage' && (
                      <th className="text-right p-3">換算金額</th>
                    )}
                  </tr>
                </thead>
                <tbody>
                  {heirs.map((heir) => (
                    <tr key={heir.id} className="border-b">
                      <td className="p-3 align-top">
                        <div>
                          <div className="font-medium">{heir.name}</div>
                          <div className="text-sm text-gray-500 flex items-center gap-1 mt-1">
                            {heir.relationship}
                            {heir.two_fold_addition && (
                              <Badge variant="destructive" className="text-xs">
                                2割加算
                              </Badge>
                            )}
                          </div>
                        </div>
                      </td>
                      <td className="text-right p-3 align-top">
                        <div className="text-sm">
                          {(heir.inheritance_share * 100).toFixed(1)}%
                        </div>
                        <div className="text-xs text-gray-500">
                          {formatCurrency(Math.round(totalAmount * heir.inheritance_share))}
                        </div>
                      </td>
                      <td className="text-right p-3 align-top">
                        {divisionMode === 'amount' ? (
                          <div className="space-y-1">
                            <Input
                              type="number"
                              value={amounts[heir.id] || ''}
                              onChange={(e) => handleAmountChange(heir.id, e.target.value)}
                              className={`w-40 text-right ${errors[heir.id] ? 'border-red-500' : ''}`}
                              placeholder="0"
                            />
                            <div className="text-xs text-gray-500 text-right h-4">
                              {formatCurrency(amounts[heir.id] || 0)}
                            </div>
                            {errors[heir.id] && (
                              <p className="text-xs text-red-500">{errors[heir.id]}</p>
                            )}
                          </div>
                        ) : (
                          <div className="space-y-1">
                            <div className="relative">
                              <Input
                                type="number"
                                step="0.01"
                                value={percentages[heir.id] || ''}
                                onChange={(e) => handlePercentageChange(heir.id, e.target.value)}
                                className={`w-24 text-right ${errors[heir.id] ? 'border-red-500' : ''}`}
                                placeholder="0"
                              />
                              <span className="absolute right-3 top-1/2 transform -translate-y-1/2 text-sm text-gray-500">
                                %
                              </span>
                            </div>
                            {errors[heir.id] && (
                              <p className="text-xs text-red-500">{errors[heir.id]}</p>
                            )}
                          </div>
                        )}
                      </td>
                      {divisionMode === 'percentage' && (
                        <td className="text-right p-3 align-top text-sm text-gray-600">
                          {formatCurrency(amounts[heir.id] || 0)}
                        </td>
                      )}
                    </tr>
                  ))}
                </tbody>
                <tfoot>
                  <tr className="border-t-2 bg-gray-50 font-semibold">
                    <td className="p-3">合計</td>
                    <td className="text-right p-3">100%</td>
                    <td className="text-right p-3">
                      {divisionMode === 'amount' ? (
                        <div className={totalDisplayAmount !== totalAmount ? 'text-red-500' : ''}>
                          {formatCurrency(totalDisplayAmount)}
                        </div>
                      ) : (
                        <div className={Math.abs(totalDisplayPercentage - 100) > 0.01 ? 'text-red-500' : ''}>
                          {totalDisplayPercentage.toFixed(2)}%
                        </div>
                      )}
                    </td>
                    {divisionMode === 'percentage' && (
                      <td className="text-right p-3">
                         <div className={totalDisplayAmount !== totalAmount ? 'text-red-500' : ''}>
                          {formatCurrency(totalDisplayAmount)}
                        </div>
                      </td>
                    )}
                  </tr>
                </tfoot>
              </table>
            </div>
            
            {errors.total && (
              <div className="mt-4 text-red-500 text-sm font-semibold flex items-center gap-2">
                <AlertCircle className="h-4 w-4" />
                {errors.total}
              </div>
            )}
          </CardContent>
        </Card>

        {/* 計算ボタン */}
        <div className="flex justify-center mt-6">
          <Button 
            type="submit" 
            size="lg" 
            disabled={isSubmitting}
            className="min-w-48"
          >
            {isSubmitting ? (
              <>
                <div className="animate-spin rounded-full h-4 w-4 border-b-2 border-white mr-2"></div>
                計算中...
              </>
            ) : (
              <>
                <Calculator className="h-4 w-4 mr-2" />
                税額配分を計算する
              </>
            )}
          </Button>
        </div>
      </form>

      {/* 計算結果表示 */}
      {result && Array.isArray(result.heir_details) && (
        <Card className="border-blue-200 bg-blue-50">
          <CardHeader>
            <CardTitle className="text-blue-800">実際の分割による税額配分結果</CardTitle>
            <CardDescription className="text-blue-700">
              入力された分割割合に基づく各相続人の納税額です
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="overflow-x-auto">
              <table className="w-full border-collapse">
                <thead>
                  <tr className="border-b">
                    <th className="text-left p-3">相続人</th>
                    <th className="text-right p-3">取得金額</th>
                    <th className="text-right p-3">配分税額</th>
                    <th className="text-right p-3">加算減算</th>
                    <th className="text-right p-3">最終納税額</th>
                  </tr>
                </thead>
                <tbody>
                  {result.heir_details.map((detail) => (
                    <tr key={detail.heir_id} className="border-b">
                      <td className="p-3">
                        <div className="font-medium">{detail.heir_name}</div>
                        <div className="text-sm text-gray-500">{detail.relationship}</div>
                      </td>
                      <td className="text-right p-3">
                        {detail.inheritance_amount_formatted}
                      </td>
                      <td className="text-right p-3">
                        {detail.tax_amount_formatted}
                      </td>
                      <td className={`text-right p-3 font-semibold ${detail.surcharge_deduction_amount > 0 ? 'text-red-600' : (detail.surcharge_deduction_amount < 0 ? 'text-blue-600' : '')}`}>
                        {detail.surcharge_deduction_amount_formatted}
                      </td>
                      <td className="text-right p-3 font-semibold">
                        {detail.final_tax_amount_formatted}
                      </td>
                    </tr>
                  ))}
                  <tr className="border-b-2 border-gray-300 bg-gray-50">
                    <td className="p-3 font-semibold">合計</td>
                    <td className="text-right p-3 font-semibold">
                      {formatCurrency(result.heir_details.reduce((sum, d) => sum + d.inheritance_amount, 0))}
                    </td>
                    <td className="text-right p-3 font-semibold">
                      {formatCurrency(result.heir_details.reduce((sum, d) => sum + d.tax_amount, 0))}
                    </td>
                    <td className="text-right p-3 font-semibold">
                      {formatCurrency(result.heir_details.reduce((sum, d) => sum + d.surcharge_deduction_amount, 0))}
                    </td>
                    <td className="text-right p-3 font-semibold text-red-800">
                      {result.total_tax_amount_formatted}
                    </td>
                  </tr>
                </tbody>
              </table>
            </div>
          </CardContent>
        </Card>
      )}
    </div>
  )
}

export default ActualDivisionForm

