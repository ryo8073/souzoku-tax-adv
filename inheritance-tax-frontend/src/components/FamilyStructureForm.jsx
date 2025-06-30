import { useState } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Input } from '@/components/ui/input.jsx'
import { Label } from '@/components/ui/label.jsx'
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '@/components/ui/select.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Calculator, AlertCircle } from 'lucide-react'

const FamilyStructureForm = ({ onSubmit, initialData }) => {
  const [formData, setFormData] = useState(() => {
    if (initialData) {
      return {
        taxableAmount: initialData.taxableAmount?.toString() || '',
        spouseExists: initialData.familyStructure?.spouse_exists ? 'true' : 'false',
        childrenCount: initialData.familyStructure?.children_count?.toString() || '',
        adoptedChildrenCount: initialData.familyStructure?.adopted_children_count?.toString() || '0',
        grandchildAdoptedCount: initialData.familyStructure?.grandchild_adopted_count?.toString() || '0',
        parentsAlive: initialData.familyStructure?.parents_alive?.toString() || '',
        siblingsCount: initialData.familyStructure?.siblings_count?.toString() || '0',
        halfSiblingsCount: initialData.familyStructure?.half_siblings_count?.toString() || '0',
        nonHeirsCount: initialData.familyStructure?.non_heirs_count?.toString() || '0'
      }
    }
    return {
      taxableAmount: '',
      spouseExists: '',
      childrenCount: '',
      adoptedChildrenCount: '0',      // デフォルト値を0に設定
      grandchildAdoptedCount: '0',    // 孫養子の数を追加
      parentsAlive: '',
      siblingsCount: '0',             // デフォルト値を0に設定
      halfSiblingsCount: '0',         // 半血兄弟姉妹の数を追加
      nonHeirsCount: '0'              // 法定相続人以外の人数を追加
    }
  })

  const [errors, setErrors] = useState({})
  const [isSubmitting, setIsSubmitting] = useState(false)

  const validateForm = () => {
    const newErrors = {}

    // 課税価格の検証
    if (!formData.taxableAmount || formData.taxableAmount <= 0) {
      newErrors.taxableAmount = '課税価格の合計額を入力してください'
    }

    // 配偶者の有無の検証
    if (formData.spouseExists === '') {
      newErrors.spouseExists = '配偶者の有無を選択してください'
    }

    // 子供の数の検証
    if (formData.childrenCount === '' || formData.childrenCount < 0) {
      newErrors.childrenCount = '子供の数を入力してください（0以上）'
    }

    // 養子の数の検証
    if (formData.adoptedChildrenCount === '' || formData.adoptedChildrenCount < 0) {
      newErrors.adoptedChildrenCount = '養子の数を入力してください（0以上）'
    }

    // 養子の数が子供の総数を超えていないかチェック
    if (parseInt(formData.adoptedChildrenCount) > parseInt(formData.childrenCount)) {
      newErrors.adoptedChildrenCount = '養子の数は子供の総数を超えることはできません'
    }

    // 孫養子の数の検証
    if (formData.grandchildAdoptedCount === '' || formData.grandchildAdoptedCount < 0) {
      newErrors.grandchildAdoptedCount = '孫養子の数を入力してください（0以上）'
    }

    // 孫養子の数が養子の数を超えていないかチェック
    if (parseInt(formData.grandchildAdoptedCount) > parseInt(formData.adoptedChildrenCount)) {
      newErrors.grandchildAdoptedCount = '孫養子の数は養子の数を超えることはできません'
    }

    // 親の生存状況の検証
    if (formData.parentsAlive === '') {
      newErrors.parentsAlive = '親の生存状況を選択してください'
    }

    // 兄弟姉妹の数の検証
    if (formData.siblingsCount === '' || formData.siblingsCount < 0) {
      newErrors.siblingsCount = '全血兄弟姉妹の数を入力してください（0以上）'
    }

    // 半血兄弟姉妹の数の検証
    if (formData.halfSiblingsCount === '' || formData.halfSiblingsCount < 0) {
      newErrors.halfSiblingsCount = '半血兄弟姉妹の数を入力してください（0以上）'
    }

    // 法定相続人以外の人数の検証
    if (formData.nonHeirsCount === '' || formData.nonHeirsCount < 0) {
      newErrors.nonHeirsCount = '法定相続人以外の人数を入力してください（0以上）'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleSubmit = async (e) => {
    e.preventDefault()
    
    if (!validateForm()) {
      return
    }

    setIsSubmitting(true)

    const familyStructure = {
      spouse_exists: formData.spouseExists === 'true',
      children_count: parseInt(formData.childrenCount),
      adopted_children_count: parseInt(formData.adoptedChildrenCount),
      grandchild_adopted_count: parseInt(formData.grandchildAdoptedCount),
      parents_alive: parseInt(formData.parentsAlive),
      siblings_count: parseInt(formData.siblingsCount),
      half_siblings_count: parseInt(formData.halfSiblingsCount),
      non_heirs_count: parseInt(formData.nonHeirsCount)
    }

    try {
      await onSubmit({
        familyStructure,
        taxableAmount: parseInt(formData.taxableAmount)
      })
    } catch (error) {
      console.error('送信エラー:', error)
    } finally {
      setIsSubmitting(false)
    }
  }

  const handleInputChange = (field, value) => {
    setFormData(prev => ({
      ...prev,
      [field]: value
    }))
    
    // エラーをクリア
    if (errors[field]) {
      setErrors(prev => ({
        ...prev,
        [field]: undefined
      }))
    }
  }

  const formatCurrency = (value) => {
    if (!value) return ''
    return parseInt(value).toLocaleString() + '円'
  }

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* 課税価格入力 */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">課税価格の合計額</CardTitle>
          <CardDescription>
            相続財産の総額から債務・葬式費用を差し引いた金額を入力してください
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-2">
            <Label htmlFor="taxableAmount">課税価格の合計額 *</Label>
            <div className="relative">
              <Input
                id="taxableAmount"
                type="number"
                placeholder="例: 246000000"
                value={formData.taxableAmount}
                onChange={(e) => handleInputChange('taxableAmount', e.target.value)}
                className={errors.taxableAmount ? 'border-red-500' : ''}
              />
              <div className="absolute right-3 top-1/2 transform -translate-y-1/2 text-sm text-gray-500">
                円
              </div>
            </div>
            {formData.taxableAmount && (
              <p className="text-sm text-blue-600">
                {formatCurrency(formData.taxableAmount)}
              </p>
            )}
            {errors.taxableAmount && (
              <p className="text-sm text-red-500 flex items-center gap-1">
                <AlertCircle className="h-4 w-4" />
                {errors.taxableAmount}
              </p>
            )}
          </div>
        </CardContent>
      </Card>

      {/* 家族構成入力 */}
      <Card>
        <CardHeader>
          <CardTitle className="text-lg">家族構成</CardTitle>
          <CardDescription>
            被相続人の家族構成を入力してください。法定相続人の判定に使用されます。
          </CardDescription>
        </CardHeader>
        <CardContent className="space-y-4">
          {/* 配偶者の有無 */}
          <div className="space-y-2">
            <Label htmlFor="spouseExists">配偶者の有無 *</Label>
            <Select value={formData.spouseExists} onValueChange={(value) => handleInputChange('spouseExists', value)}>
              <SelectTrigger className={errors.spouseExists ? 'border-red-500' : ''}>
                <SelectValue placeholder="選択してください" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="true">有（存命）</SelectItem>
                <SelectItem value="false">無（死亡・離婚）</SelectItem>
              </SelectContent>
            </Select>
            {errors.spouseExists && (
              <p className="text-sm text-red-500 flex items-center gap-1">
                <AlertCircle className="h-4 w-4" />
                {errors.spouseExists}
              </p>
            )}
          </div>

          {/* 子供の数 */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div className="space-y-2">
              <Label htmlFor="childrenCount">子供の総数 *</Label>
              <Input
                id="childrenCount"
                type="number"
                min="0"
                placeholder="0"
                value={formData.childrenCount}
                onChange={(e) => handleInputChange('childrenCount', e.target.value)}
                className={errors.childrenCount ? 'border-red-500' : ''}
              />
              {errors.childrenCount && (
                <p className="text-sm text-red-500 flex items-center gap-1">
                  <AlertCircle className="h-4 w-4" />
                  {errors.childrenCount}
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="adoptedChildrenCount">うち養子の数 *</Label>
              <Input
                id="adoptedChildrenCount"
                type="number"
                min="0"
                placeholder="0"
                value={formData.adoptedChildrenCount}
                onChange={(e) => handleInputChange('adoptedChildrenCount', e.target.value)}
                className={errors.adoptedChildrenCount ? 'border-red-500' : ''}
              />
              {errors.adoptedChildrenCount && (
                <p className="text-sm text-red-500 flex items-center gap-1">
                  <AlertCircle className="h-4 w-4" />
                  {errors.adoptedChildrenCount}
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="grandchildAdoptedCount">うち孫養子の数 *</Label>
              <Input
                id="grandchildAdoptedCount"
                type="number"
                min="0"
                placeholder="0"
                value={formData.grandchildAdoptedCount}
                onChange={(e) => handleInputChange('grandchildAdoptedCount', e.target.value)}
                className={errors.grandchildAdoptedCount ? 'border-red-500' : ''}
              />
              <p className="text-xs text-gray-500">
                養子の内、孫を養子にした数
              </p>
              {errors.grandchildAdoptedCount && (
                <p className="text-sm text-red-500 flex items-center gap-1">
                  <AlertCircle className="h-4 w-4" />
                  {errors.grandchildAdoptedCount}
                </p>
              )}
            </div>
          </div>

          {/* 親の生存状況 */}
          <div className="space-y-2">
            <Label htmlFor="parentsAlive">親の生存状況 *</Label>
            <Select value={formData.parentsAlive} onValueChange={(value) => handleInputChange('parentsAlive', value)}>
              <SelectTrigger className={errors.parentsAlive ? 'border-red-500' : ''}>
                <SelectValue placeholder="選択してください" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="0">両方死亡</SelectItem>
                <SelectItem value="1">片方存命</SelectItem>
                <SelectItem value="2">両方存命</SelectItem>
              </SelectContent>
            </Select>
            {errors.parentsAlive && (
              <p className="text-sm text-red-500 flex items-center gap-1">
                <AlertCircle className="h-4 w-4" />
                {errors.parentsAlive}
              </p>
            )}
          </div>

          {/* 兄弟姉妹の数 */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div className="space-y-2">
              <Label htmlFor="siblingsCount">全血兄弟姉妹の数 *</Label>
              <Input
                id="siblingsCount"
                type="number"
                min="0"
                placeholder="0"
                value={formData.siblingsCount}
                onChange={(e) => handleInputChange('siblingsCount', e.target.value)}
                className={errors.siblingsCount ? 'border-red-500' : ''}
              />
              <p className="text-xs text-gray-500">
                父母の両方が同じ兄弟姉妹
              </p>
              {errors.siblingsCount && (
                <p className="text-sm text-red-500 flex items-center gap-1">
                  <AlertCircle className="h-4 w-4" />
                  {errors.siblingsCount}
                </p>
              )}
            </div>

            <div className="space-y-2">
              <Label htmlFor="halfSiblingsCount">半血兄弟姉妹の数 *</Label>
              <Input
                id="halfSiblingsCount"
                type="number"
                min="0"
                placeholder="0"
                value={formData.halfSiblingsCount}
                onChange={(e) => handleInputChange('halfSiblingsCount', e.target.value)}
                className={errors.halfSiblingsCount ? 'border-red-500' : ''}
              />
              <p className="text-xs text-gray-500">
                父母の一方のみが同じ兄弟姉妹（相続分は全血の1/2）
              </p>
              {errors.halfSiblingsCount && (
                <p className="text-sm text-red-500 flex items-center gap-1">
                  <AlertCircle className="h-4 w-4" />
                  {errors.halfSiblingsCount}
                </p>
              )}
            </div>
          </div>

          {/* 法定相続人以外の人数 */}
          <div className="space-y-2">
            <Label htmlFor="nonHeirsCount">法定相続人以外の人数 *</Label>
            <Input
              id="nonHeirsCount"
              type="number"
              min="0"
              placeholder="0"
              value={formData.nonHeirsCount}
              onChange={(e) => handleInputChange('nonHeirsCount', e.target.value)}
              className={errors.nonHeirsCount ? 'border-red-500' : ''}
            />
            <p className="text-xs text-gray-500">
              遺贈を受ける人など、法定相続人以外で相続財産を取得する人の数
            </p>
            {errors.nonHeirsCount && (
              <p className="text-sm text-red-500 flex items-center gap-1">
                <AlertCircle className="h-4 w-4" />
                {errors.nonHeirsCount}
              </p>
            )}
          </div>
        </CardContent>
      </Card>

      {/* 送信ボタン */}
      <div className="flex justify-center">
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
              相続税を計算する
            </>
          )}
        </Button>
      </div>
    </form>
  )
}

export default FamilyStructureForm

