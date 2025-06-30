import { useState } from 'react'
import { Button } from '@/components/ui/button.jsx'
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card.jsx'
import { Tabs, TabsContent, TabsList, TabsTrigger } from '@/components/ui/tabs.jsx'
import { Calculator, Users, PieChart, FileText, RotateCcw } from 'lucide-react'
import FamilyStructureForm from './components/FamilyStructureForm.jsx'
import TaxCalculationResult from './components/TaxCalculationResult.jsx'
import ActualDivisionForm from './components/ActualDivisionForm.jsx'
import './App.css'

function App() {
  const [familyStructure, setFamilyStructure] = useState({
    spouse_exists: false,
    children_count: 0,
    adopted_children_count: 0,
    parents_alive: 0,
    siblings_count: 0,
    half_siblings_count: 0,
    non_heirs_count: 0  // 法定相続人以外の人数を追加
  })

  const [taxableAmount, setTaxableAmount] = useState(0)
  const [legalHeirs, setLegalHeirs] = useState([])
  const [taxCalculationResult, setTaxCalculationResult] = useState(null)
  const [actualDivisionResult, setActualDivisionResult] = useState(null)
  const [currentStep, setCurrentStep] = useState('family')
  const [formInputData, setFormInputData] = useState(null) // 入力データを保持

  const API_BASE_URL = 'http://127.0.0.1:5001';

  const handleFamilyStructureSubmit = async (data) => {
    try {
      // 入力データを保持
      setFormInputData(data)
      setFamilyStructure(data.familyStructure)
      setTaxableAmount(data.taxableAmount)
      
      // 法定相続人判定API呼び出し
      const heirsResponse = await fetch(`${API_BASE_URL}/api/calculation/heirs`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          family_structure: data.familyStructure
        }),
      })
      
      const heirsData = await heirsResponse.json()
      
      if (heirsData.success) {
        setLegalHeirs(heirsData.result.legal_heirs)
        
        // 相続税計算API呼び出し
        const taxResponse = await fetch(`${API_BASE_URL}/api/calculation/tax-amount`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            taxable_amount: data.taxableAmount,
            family_structure: data.familyStructure
          }),
        })
        
        const taxData = await taxResponse.json()
        
        if (taxData.success) {
          setTaxCalculationResult(taxData.result)
          setCurrentStep('result')
        }
      }
    } catch (error) {
      console.error('計算エラー:', error)
    }
  }

  const handleActualDivisionSubmit = async (divisionData) => {
    try {
      const response = await fetch(`${API_BASE_URL}/api/calculation/actual-division`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          ...divisionData,
          heirs: legalHeirs,
          total_tax_amount: taxCalculationResult.total_tax_amount
        }),
      })
      
      const data = await response.json()
      
      if (data.success) {
        setActualDivisionResult(data.result)
      }
    } catch (error) {
      console.error('分割計算エラー:', error)
    }
  }

  const resetCalculation = () => {
    setFamilyStructure({
      spouse_exists: false,
      children_count: 0,
      adopted_children_count: 0,
      parents_alive: 0,
      siblings_count: 0,
      half_siblings_count: 0,
      non_heirs_count: 0
    })
    setTaxableAmount(0)
    setLegalHeirs([])
    setTaxCalculationResult(null)
    setActualDivisionResult(null)
    setCurrentStep('family')
    setFormInputData(null)
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-blue-50 to-indigo-100">
      <div className="container mx-auto px-4 py-8">
        {/* ヘッダー */}
        <div className="text-center mb-8">
          <div className="flex items-center justify-center mb-4">
            <Calculator className="h-12 w-12 text-blue-600 mr-3" />
            <h1 className="text-4xl font-bold text-gray-900">相続税計算アプリ</h1>
          </div>
          <p className="text-lg text-gray-600 max-w-2xl mx-auto">
            法定相続人の判定から相続税の計算、2割加算の適用まで、
            正確で簡単な相続税計算をサポートします。
          </p>
        </div>

        {/* メインコンテンツ */}
        <div className="max-w-6xl mx-auto">
          <Tabs value={currentStep} onValueChange={setCurrentStep} className="w-full">
            <TabsList className="grid w-full grid-cols-3 mb-8">
              <TabsTrigger value="family" className="flex items-center gap-2">
                <Users className="h-4 w-4" />
                家族構成入力
              </TabsTrigger>
              <TabsTrigger value="result" className="flex items-center gap-2" disabled={!taxCalculationResult}>
                <FileText className="h-4 w-4" />
                計算結果
              </TabsTrigger>
              <TabsTrigger value="division" className="flex items-center gap-2" disabled={!taxCalculationResult}>
                <PieChart className="h-4 w-4" />
                実際の分割
              </TabsTrigger>
            </TabsList>

            <TabsContent value="family" className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <Users className="h-5 w-5" />
                    家族構成と課税価格の入力
                  </CardTitle>
                  <CardDescription>
                    被相続人の家族構成と課税価格の合計額を入力してください。
                    法定相続人の判定と基礎控除の計算を行います。
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <FamilyStructureForm 
                    onSubmit={handleFamilyStructureSubmit} 
                    initialData={formInputData}
                  />
                  {formInputData && (
                    <div className="flex justify-center mt-6">
                      <Button onClick={resetCalculation} variant="outline" className="flex items-center gap-2">
                        <RotateCcw className="h-4 w-4" />
                        新しい計算を開始
                      </Button>
                    </div>
                  )}
                </CardContent>
              </Card>
            </TabsContent>

            <TabsContent value="result" className="space-y-6">
              {taxCalculationResult && (
                <>
                  <TaxCalculationResult result={{
                    ...taxCalculationResult,
                    legal_heirs: taxCalculationResult.legal_heirs.filter(h => h.type !== 'other'),
                    heir_tax_details: taxCalculationResult.heir_tax_details.filter(d => {
                      const heir = taxCalculationResult.legal_heirs.find(h => h.id === d.heir_id);
                      return heir && heir.type !== 'other';
                    })
                  }} />
                  <div className="flex justify-center gap-4">
                    <Button onClick={resetCalculation} variant="outline">
                      新しい計算を開始
                    </Button>
                    <Button onClick={() => setCurrentStep('division')}>
                      実際の分割を計算
                    </Button>
                  </div>
                </>
              )}
            </TabsContent>

            <TabsContent value="division" className="space-y-6">
              {taxCalculationResult && (
                <>
                  <Card>
                    <CardHeader>
                      <CardTitle className="flex items-center gap-2">
                        <PieChart className="h-5 w-5" />
                        実際の遺産分割
                      </CardTitle>
                      <CardDescription>
                        法定相続分とは異なる実際の遺産分割がある場合の税額配分を計算します。
                        金額指定または割合指定を選択できます。
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <ActualDivisionForm 
                        heirs={legalHeirs}
                        totalAmount={taxableAmount}
                        totalTaxAmount={taxCalculationResult.total_tax_amount}
                        familyStructure={familyStructure}
                        onSubmit={handleActualDivisionSubmit}
                        result={actualDivisionResult}
                      />
                    </CardContent>
                  </Card>
                  <div className="flex justify-center">
                    <Button onClick={resetCalculation} variant="outline">
                      新しい計算を開始
                    </Button>
                  </div>
                </>
              )}
            </TabsContent>
          </Tabs>
        </div>

        {/* フッター */}
        <footer className="mt-16 text-center text-gray-500">
          <p className="mb-2">
            ※ この計算結果は参考値です。実際の税務申告においては税理士等の専門家にご相談ください。
          </p>
          <p className="text-sm">
            相続税計算アプリ v1.0.0 | 2025年6月30日版
          </p>
        </footer>
      </div>
    </div>
  )
}

export default App

