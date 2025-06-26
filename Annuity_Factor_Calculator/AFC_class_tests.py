import os

import Annuity_Factor_Calculator as AFC

maxPctError = .001 #setting 1% error. Will revise this to the max acceptable error when moving to a new actuarial system.

cwd = os.getcwd()

def ExecuteTest(TestNumber, Inputs, ExpectedResult, testMode = False):
    Calculator = AFC.Annuity_Factor_Calculator(Inputs)
    if testMode:
        ActualResult = Calculator.CalcPVF(testMode)
    else:
        ActualResult = Calculator.CalcPVF()
        
    pctError = abs((ExpectedResult - ActualResult)/ExpectedResult)
    if pctError<maxPctError: 
        if ExpectedResult == ActualResult:
            resultString = "Test" + str(TestNumber) + "PASSED: EXACT"
        else:
            resultString = "Test " + str(TestNumber) + " PASSED - Expected: "+str(ExpectedResult)+", Returned: "+str(ActualResult) +", Percent Error: " + str(pctError)
    else:
        resultString = "Test " + str(TestNumber) + " FAILED - Expected: "+str(ExpectedResult)+", Returned: "+str(ActualResult)

    print(resultString)

#Test 1: Basic
Test1Inputs = {
    'DiscountRate':.05 #0-1
    , 'AnnualCOLA':0 #0-1
    , 'AnnuityType':'SLA' # SLA, J&S, C&L, JL 
    , 'SurvivorBenefitPrct':0 #0-1
    , 'PaymentFrequency':'ABOY'  #ABOY
    , 'CertainPeriod': 0#0-15
    , 'BenefitCommencementAge':65 #50-120
    , 'PrimaryAnnuitantAge':45 #20-120
    , 'PrimaryAnnuitantGender':"M" #M, F
    , 'BeneficiaryAge':20 #20-120
    , 'BeneficiaryGender':'M' #M, F
    , 'ValuationYear':2025 #1990-2030
    , 'MortalityBeforeBCA':"Pri2012_Total_Employee" #Pri2012_Total_Employee
    , 'MortalityAfterBCA':"Pri2012_Total_Retiree" #Pri2012_Total_Retiree
    , 'ProjectionMethod':"None" #None, Static, Generational
    , 'ProjectionScale':"AA" #
    , 'StaticProjectionYears':0 #0-50
    , 'BlendMortalityRates':False #TRUE, FALSE
    , 'BlendingMalePercentage':.5 #0-1
    , 'SetbackYearsMale':0 #-10->10
    , 'SetbackYearsFemale':0 #-10->10
}
Test1ExpectedResult = 4.3989
ExecuteTest(1, Test1Inputs, Test1ExpectedResult)

#Test 2: COLA
Test2Inputs = {
    'DiscountRate':.05 #0-1
    , 'AnnualCOLA':0.025 #0-1
    , 'AnnuityType':'SLA' # SLA, J&S, C&L, JL 
    , 'SurvivorBenefitPrct':0 #0-1
    , 'PaymentFrequency':'ABOY'  #ABOY
    , 'CertainPeriod': 0#0-15
    , 'BenefitCommencementAge':65 #50-120
    , 'PrimaryAnnuitantAge':45 #20-120
    , 'PrimaryAnnuitantGender':"M" #M, F
    , 'BeneficiaryAge':20 #20-120
    , 'BeneficiaryGender':'M' #M, F
    , 'ValuationYear':2025 #1990-2030
    , 'MortalityBeforeBCA':"Pri2012_Total_Employee" #Pri2012_Total_Employee
    , 'MortalityAfterBCA':"Pri2012_Total_Retiree" #Pri2012_Total_Retiree
    , 'ProjectionMethod':"None" #None, Static, Generational
    , 'ProjectionScale':"AA" #
    , 'StaticProjectionYears':0 #0-50
    , 'BlendMortalityRates':False #TRUE, FALSE
    , 'BlendingMalePercentage':.5 #0-1
    , 'SetbackYearsMale':0 #-10->10
    , 'SetbackYearsFemale':0 #-10->10
}
Test2ExpectedResult = 5.5083
ExecuteTest(2, Test2Inputs, Test2ExpectedResult)

#Test 3: J&S
Test3Inputs = {
    'DiscountRate':.05 #0-1
    , 'AnnualCOLA':0.0 #0-1
    , 'AnnuityType':'J&S' # SLA, J&S, C&L, JL 
    , 'SurvivorBenefitPrct':0.5 #0-1
    , 'PaymentFrequency':'ABOY'  #ABOY
    , 'CertainPeriod': 0#0-15
    , 'BenefitCommencementAge':65 #50-120
    , 'PrimaryAnnuitantAge':45 #20-120
    , 'PrimaryAnnuitantGender':"M" #M, F
    , 'BeneficiaryAge':40 #20-120
    , 'BeneficiaryGender':'M' #M, F
    , 'ValuationYear':2025 #1990-2030
    , 'MortalityBeforeBCA':"Pri2012_Total_Employee" #Pri2012_Total_Employee
    , 'MortalityAfterBCA':"Pri2012_Total_Retiree" #Pri2012_Total_Retiree
    , 'ProjectionMethod':"None" #None, Static, Generational
    , 'ProjectionScale':"AA" #
    , 'StaticProjectionYears':0 #0-50
    , 'BlendMortalityRates':False #TRUE, FALSE
    , 'BlendingMalePercentage':.5 #0-1
    , 'SetbackYearsMale':0 #-10->10
    , 'SetbackYearsFemale':0 #-10->10
}
Test3ExpectedResult = 5.0195
ExecuteTest(3, Test3Inputs, Test3ExpectedResult)

#Test 4: C&L
Test4Inputs = {
    'DiscountRate':.05 #0-1
    , 'AnnualCOLA':0.0 #0-1
    , 'AnnuityType':'C&L' # SLA, J&S, C&L, JL 
    , 'SurvivorBenefitPrct':0.0 #0-1
    , 'PaymentFrequency':'ABOY'  #ABOY
    , 'CertainPeriod': 10 #0-15
    , 'BenefitCommencementAge':65 #50-120
    , 'PrimaryAnnuitantAge':45 #20-120
    , 'PrimaryAnnuitantGender':"M" #M, F
    , 'BeneficiaryAge':40 #20-120
    , 'BeneficiaryGender':'M' #M, F
    , 'ValuationYear':2025 #1990-2030
    , 'MortalityBeforeBCA':"Pri2012_Total_Employee" #Pri2012_Total_Employee
    , 'MortalityAfterBCA':"Pri2012_Total_Retiree" #Pri2012_Total_Retiree
    , 'ProjectionMethod':"None" #None, Static, Generational
    , 'ProjectionScale':"AA" #
    , 'StaticProjectionYears':0 #0-50
    , 'BlendMortalityRates':False #TRUE, FALSE
    , 'BlendingMalePercentage':.5 #0-1
    , 'SetbackYearsMale':0 #-10->10
    , 'SetbackYearsFemale':0 #-10->10
}
Test4ExpectedResult = 4.5586
ExecuteTest(4, Test4Inputs, Test4ExpectedResult)

#Test 5: JL
Test5Inputs = {
    'DiscountRate':.05 #0-1
    , 'AnnualCOLA':0.0 #0-1
    , 'AnnuityType':'JL' # SLA, J&S, C&L, JL 
    , 'SurvivorBenefitPrct':0.5 #0-1
    , 'PaymentFrequency':'ABOY'  #ABOY
    , 'CertainPeriod':0 #0-15
    , 'BenefitCommencementAge':65 #50-120
    , 'PrimaryAnnuitantAge':45 #20-120
    , 'PrimaryAnnuitantGender':"M" #M, F
    , 'BeneficiaryAge':40 #20-120
    , 'BeneficiaryGender':'M' #M, F
    , 'ValuationYear':2025 #1990-2030
    , 'MortalityBeforeBCA':"Pri2012_Total_Employee" #Pri2012_Total_Employee
    , 'MortalityAfterBCA':"Pri2012_Total_Retiree" #Pri2012_Total_Retiree
    , 'ProjectionMethod':"None" #None, Static, Generational
    , 'ProjectionScale':"AA" #
    , 'StaticProjectionYears':0 #0-50
    , 'BlendMortalityRates':False #TRUE, FALSE
    , 'BlendingMalePercentage':.5 #0-1
    , 'SetbackYearsMale':0 #-10->10
    , 'SetbackYearsFemale':0 #-10->10
}
Test5ExpectedResult = 3.8365
ExecuteTest(5, Test5Inputs, Test5ExpectedResult)

#Test 6: AEOY
Test6Inputs = {
    'DiscountRate':.05 #0-1
    , 'AnnualCOLA':0.0 #0-1
    , 'AnnuityType':'SLA' # SLA, J&S, C&L, JL 
    , 'SurvivorBenefitPrct':0.0 #0-1
    , 'PaymentFrequency':'AEOY'  #ABOY
    , 'CertainPeriod':0 #0-15
    , 'BenefitCommencementAge':65 #50-120
    , 'PrimaryAnnuitantAge':45 #20-120
    , 'PrimaryAnnuitantGender':"M" #M, F
    , 'BeneficiaryAge':40 #20-120
    , 'BeneficiaryGender':'M' #M, F
    , 'ValuationYear':2025 #1990-2030
    , 'MortalityBeforeBCA':"Pri2012_Total_Employee" #Pri2012_Total_Employee
    , 'MortalityAfterBCA':"Pri2012_Total_Retiree" #Pri2012_Total_Retiree
    , 'ProjectionMethod':"None" #None, Static, Generational
    , 'ProjectionScale':"AA" #
    , 'StaticProjectionYears':0 #0-50
    , 'BlendMortalityRates':False #TRUE, FALSE
    , 'BlendingMalePercentage':.5 #0-1
    , 'SetbackYearsMale':0 #-10->10
    , 'SetbackYearsFemale':0 #-10->10
}
Test6ExpectedResult = 4.0408
ExecuteTest(6, Test6Inputs, Test6ExpectedResult)

#Test 7: MBOM
Test7Inputs = {
    'DiscountRate':.05 #0-1
    , 'AnnualCOLA':0.0 #0-1
    , 'AnnuityType':'SLA' # SLA, J&S, C&L, JL 
    , 'SurvivorBenefitPrct':0.0 #0-1
    , 'PaymentFrequency':'MBOM'  #ABOY
    , 'CertainPeriod':0 #0-15
    , 'BenefitCommencementAge':65 #50-120
    , 'PrimaryAnnuitantAge':45 #20-120
    , 'PrimaryAnnuitantGender':"M" #M, F
    , 'BeneficiaryAge':40 #20-120
    , 'BeneficiaryGender':'M' #M, F
    , 'ValuationYear':2025 #1990-2030
    , 'MortalityBeforeBCA':"Pri2012_Total_Employee" #Pri2012_Total_Employee
    , 'MortalityAfterBCA':"Pri2012_Total_Retiree" #Pri2012_Total_Retiree
    , 'ProjectionMethod':"None" #None, Static, Generational
    , 'ProjectionScale':"AA" #
    , 'StaticProjectionYears':0 #0-50
    , 'BlendMortalityRates':False #TRUE, FALSE
    , 'BlendingMalePercentage':.5 #0-1
    , 'SetbackYearsMale':0 #-10->10
    , 'SetbackYearsFemale':0 #-10->10
}
Test7ExpectedResult = 4.2335
ExecuteTest(7, Test7Inputs, Test7ExpectedResult)

#Test 8: MEOM
Test8Inputs = {
    'DiscountRate':.05 #0-1
    , 'AnnualCOLA':0.0 #0-1
    , 'AnnuityType':'SLA' # SLA, J&S, C&L, JL 
    , 'SurvivorBenefitPrct':0.0 #0-1
    , 'PaymentFrequency':'MEOM'  #ABOY
    , 'CertainPeriod':0 #0-15
    , 'BenefitCommencementAge':65 #50-120
    , 'PrimaryAnnuitantAge':45 #20-120
    , 'PrimaryAnnuitantGender':"M" #M, F
    , 'BeneficiaryAge':40 #20-120
    , 'BeneficiaryGender':'M' #M, F
    , 'ValuationYear':2025 #1990-2030
    , 'MortalityBeforeBCA':"Pri2012_Total_Employee" #Pri2012_Total_Employee
    , 'MortalityAfterBCA':"Pri2012_Total_Retiree" #Pri2012_Total_Retiree
    , 'ProjectionMethod':"None" #None, Static, Generational
    , 'ProjectionScale':"AA" #
    , 'StaticProjectionYears':0 #0-50
    , 'BlendMortalityRates':False #TRUE, FALSE
    , 'BlendingMalePercentage':.5 #0-1
    , 'SetbackYearsMale':0 #-10->10
    , 'SetbackYearsFemale':0 #-10->10
}
Test8ExpectedResult = 4.2037
ExecuteTest(8, Test8Inputs, Test8ExpectedResult)

#Test 9: MAppx
Test9Inputs = {
    'DiscountRate':.05 #0-1
    , 'AnnualCOLA':0.0 #0-1
    , 'AnnuityType':'SLA' # SLA, J&S, C&L, JL 
    , 'SurvivorBenefitPrct':0.0 #0-1
    , 'PaymentFrequency':'MAPPX'  #ABOY
    , 'CertainPeriod':0 #0-15
    , 'BenefitCommencementAge':65 #50-120
    , 'PrimaryAnnuitantAge':45 #20-120
    , 'PrimaryAnnuitantGender':"M" #M, F
    , 'BeneficiaryAge':40 #20-120
    , 'BeneficiaryGender':'M' #M, F
    , 'ValuationYear':2025 #1990-2030
    , 'MortalityBeforeBCA':"Pri2012_Total_Employee" #Pri2012_Total_Employee
    , 'MortalityAfterBCA':"Pri2012_Total_Retiree" #Pri2012_Total_Retiree
    , 'ProjectionMethod':"None" #None, Static, Generational
    , 'ProjectionScale':"AA" #
    , 'StaticProjectionYears':0 #0-50
    , 'BlendMortalityRates':False #TRUE, FALSE
    , 'BlendingMalePercentage':.5 #0-1
    , 'SetbackYearsMale':0 #-10->10
    , 'SetbackYearsFemale':0 #-10->10
}
Test9ExpectedResult = 4.2347
ExecuteTest(9, Test9Inputs, Test9ExpectedResult)

#Test 10: M PA, F Ben
Test10Inputs = {
    'DiscountRate':.05 #0-1
    , 'AnnualCOLA':0.0 #0-1
    , 'AnnuityType':'J&S' # SLA, J&S, C&L, JL 
    , 'SurvivorBenefitPrct':0.5 #0-1
    , 'PaymentFrequency':'ABOY'  #ABOY
    , 'CertainPeriod':0 #0-15
    , 'BenefitCommencementAge':65 #50-120
    , 'PrimaryAnnuitantAge':45 #20-120
    , 'PrimaryAnnuitantGender':"M" #M, F
    , 'BeneficiaryAge':40 #20-120
    , 'BeneficiaryGender':'F' #M, F
    , 'ValuationYear':2025 #1990-2030
    , 'MortalityBeforeBCA':"Pri2012_Total_Employee" #Pri2012_Total_Employee
    , 'MortalityAfterBCA':"Pri2012_Total_Retiree" #Pri2012_Total_Retiree
    , 'ProjectionMethod':"None" #None, Static, Generational
    , 'ProjectionScale':"AA" #
    , 'StaticProjectionYears':0 #0-50
    , 'BlendMortalityRates':False #TRUE, FALSE
    , 'BlendingMalePercentage':.5 #0-1
    , 'SetbackYearsMale':0 #-10->10
    , 'SetbackYearsFemale':0 #-10->10
}
Test10ExpectedResult = 5.0967
ExecuteTest(10, Test10Inputs, Test10ExpectedResult)

#Test 11: F Ann, M Ben
Test11Inputs = {
    'DiscountRate':.05 #0-1
    , 'AnnualCOLA':0.0 #0-1
    , 'AnnuityType':'J&S' # SLA, J&S, C&L, JL 
    , 'SurvivorBenefitPrct':0.5 #0-1
    , 'PaymentFrequency':'ABOY'  #ABOY
    , 'CertainPeriod':0 #0-15
    , 'BenefitCommencementAge':65 #50-120
    , 'PrimaryAnnuitantAge':45 #20-120
    , 'PrimaryAnnuitantGender':"F" #M, F
    , 'BeneficiaryAge':40 #20-120
    , 'BeneficiaryGender':'M' #M, F
    , 'ValuationYear':2025 #1990-2030
    , 'MortalityBeforeBCA':"Pri2012_Total_Employee" #Pri2012_Total_Employee
    , 'MortalityAfterBCA':"Pri2012_Total_Retiree" #Pri2012_Total_Retiree
    , 'ProjectionMethod':"None" #None, Static, Generational
    , 'ProjectionScale':"AA" #
    , 'StaticProjectionYears':0 #0-50
    , 'BlendMortalityRates':False #TRUE, FALSE
    , 'BlendingMalePercentage':.5 #0-1
    , 'SetbackYearsMale':0 #-10->10
    , 'SetbackYearsFemale':0 #-10->10
}
Test11ExpectedResult = 5.2388
ExecuteTest(11, Test11Inputs, Test11ExpectedResult)

#Test 12: F Ann, F Ben
Test12Inputs = {
    'DiscountRate':.05 #0-1
    , 'AnnualCOLA':0.0 #0-1
    , 'AnnuityType':'JL' # SLA, J&S, C&L, JL 
    , 'SurvivorBenefitPrct':0.5 #0-1
    , 'PaymentFrequency':'ABOY'  #ABOY
    , 'CertainPeriod':0 #0-15
    , 'BenefitCommencementAge':65 #50-120
    , 'PrimaryAnnuitantAge':45 #20-120
    , 'PrimaryAnnuitantGender':"F" #M, F
    , 'BeneficiaryAge':40 #20-120
    , 'BeneficiaryGender':'F' #M, F
    , 'ValuationYear':2025 #1990-2030
    , 'MortalityBeforeBCA':"Pri2012_Total_Employee" #Pri2012_Total_Employee
    , 'MortalityAfterBCA':"Pri2012_Total_Retiree" #Pri2012_Total_Retiree
    , 'ProjectionMethod':"None" #None, Static, Generational
    , 'ProjectionScale':"AA" #
    , 'StaticProjectionYears':0 #0-50
    , 'BlendMortalityRates':False #TRUE, FALSE
    , 'BlendingMalePercentage':.5 #0-1
    , 'SetbackYearsMale':0 #-10->10
    , 'SetbackYearsFemale':0 #-10->10
}
Test12ExpectedResult = 4.2345 #Note JL AnnuityType
ExecuteTest(12, Test12Inputs, Test12ExpectedResult)

#Test 13: Age = CommAge
Test13Inputs = {
    'DiscountRate':.05 #0-1
    , 'AnnualCOLA':0.0 #0-1
    , 'AnnuityType':'SLA' # SLA, J&S, C&L, JL 
    , 'SurvivorBenefitPrct':0.0 #0-1
    , 'PaymentFrequency':'ABOY'  #ABOY
    , 'CertainPeriod':0 #0-15
    , 'BenefitCommencementAge':65 #50-120
    , 'PrimaryAnnuitantAge':65 #20-120
    , 'PrimaryAnnuitantGender':"M" #M, F
    , 'BeneficiaryAge':40 #20-120
    , 'BeneficiaryGender':'M' #M, F
    , 'ValuationYear':2025 #1990-2030
    , 'MortalityBeforeBCA':"Pri2012_Total_Employee" #Pri2012_Total_Employee
    , 'MortalityAfterBCA':"Pri2012_Total_Retiree" #Pri2012_Total_Retiree
    , 'ProjectionMethod':"None" #None, Static, Generational
    , 'ProjectionScale':"AA" #
    , 'StaticProjectionYears':0 #0-50
    , 'BlendMortalityRates':False #TRUE, FALSE
    , 'BlendingMalePercentage':.5 #0-1
    , 'SetbackYearsMale':0 #-10->10
    , 'SetbackYearsFemale':0 #-10->10
}
Test13ExpectedResult = 12.2833
ExecuteTest(13, Test13Inputs, Test13ExpectedResult)

#Test 14: B Age > PA Age
Test14Inputs = {
    'DiscountRate':.05 #0-1
    , 'AnnualCOLA':0.0 #0-1
    , 'AnnuityType':'J&S' # SLA, J&S, C&L, JL 
    , 'SurvivorBenefitPrct':0.5 #0-1
    , 'PaymentFrequency':'ABOY'  #ABOY
    , 'CertainPeriod':0 #0-15
    , 'BenefitCommencementAge':65 #50-120
    , 'PrimaryAnnuitantAge':45 #20-120
    , 'PrimaryAnnuitantGender':"M" #M, F
    , 'BeneficiaryAge':55 #20-120
    , 'BeneficiaryGender':'M' #M, F
    , 'ValuationYear':2025 #1990-2030
    , 'MortalityBeforeBCA':"Pri2012_Total_Employee" #Pri2012_Total_Employee
    , 'MortalityAfterBCA':"Pri2012_Total_Retiree" #Pri2012_Total_Retiree
    , 'ProjectionMethod':"None" #None, Static, Generational
    , 'ProjectionScale':"AA" #
    , 'StaticProjectionYears':0 #0-50
    , 'BlendMortalityRates':False #TRUE, FALSE
    , 'BlendingMalePercentage':.5 #0-1
    , 'SetbackYearsMale':0 #-10->10
    , 'SetbackYearsFemale':0 #-10->10
}
Test14ExpectedResult = 4.5955
ExecuteTest(14, Test14Inputs, Test14ExpectedResult)

#Test 15: 1983_GAM 
Test15Inputs = {
    'DiscountRate':.05 #0-1
    , 'AnnualCOLA':0.0 #0-1
    , 'AnnuityType':'SLA' # SLA, J&S, C&L, JL 
    , 'SurvivorBenefitPrct':0.0 #0-1
    , 'PaymentFrequency':'ABOY'  #ABOY
    , 'CertainPeriod':0 #0-15
    , 'BenefitCommencementAge':65 #50-120
    , 'PrimaryAnnuitantAge':45 #20-120
    , 'PrimaryAnnuitantGender':"M" #M, F
    , 'BeneficiaryAge':40 #20-120
    , 'BeneficiaryGender':'M' #M, F
    , 'ValuationYear':2025 #1990-2030
    , 'MortalityBeforeBCA':"1983_GAM" #Pri2012_Total_Employee
    , 'MortalityAfterBCA':"1983_GAM" #Pri2012_Total_Retiree
    , 'ProjectionMethod':"None" #None, Static, Generational
    , 'ProjectionScale':"AA" #
    , 'StaticProjectionYears':0 #0-50
    , 'BlendMortalityRates':False #TRUE, FALSE
    , 'BlendingMalePercentage':.5 #0-1
    , 'SetbackYearsMale':0 #-10->10
    , 'SetbackYearsFemale':0 #-10->10
}
Test15ExpectedResult = 3.6838
ExecuteTest(15, Test15Inputs, Test15ExpectedResult)

#Test 16: RP2000_BlueCol
Test16Inputs = {
    'DiscountRate':.05 #0-1
    , 'AnnualCOLA':0.0 #0-1
    , 'AnnuityType':'SLA' # SLA, J&S, C&L, JL 
    , 'SurvivorBenefitPrct':0.0 #0-1
    , 'PaymentFrequency':'ABOY'  #ABOY
    , 'CertainPeriod':0 #0-15
    , 'BenefitCommencementAge':65 #50-120
    , 'PrimaryAnnuitantAge':45 #20-120
    , 'PrimaryAnnuitantGender':"M" #M, F
    , 'BeneficiaryAge':40 #20-120
    , 'BeneficiaryGender':'M' #M, F
    , 'ValuationYear':2025 #1990-2030
    , 'MortalityBeforeBCA':"RP2000_BlueCol" #Pri2012_Total_Employee
    , 'MortalityAfterBCA':"RP2000_BlueCol" #Pri2012_Total_Retiree
    , 'ProjectionMethod':"None" #None, Static, Generational
    , 'ProjectionScale':"AA" #
    , 'StaticProjectionYears':0 #0-50
    , 'BlendMortalityRates':False #TRUE, FALSE
    , 'BlendingMalePercentage':.5 #0-1
    , 'SetbackYearsMale':0 #-10->10
    , 'SetbackYearsFemale':0 #-10->10
}
Test16ExpectedResult = 4.7883
ExecuteTest(16, Test16Inputs, Test16ExpectedResult)

#Test 17: RP2014
Test17Inputs = {
    'DiscountRate':.05 #0-1
    , 'AnnualCOLA':0.0 #0-1
    , 'AnnuityType':'SLA' # SLA, J&S, C&L, JL 
    , 'SurvivorBenefitPrct':0.0 #0-1
    , 'PaymentFrequency':'ABOY'  #ABOY
    , 'CertainPeriod':0 #0-15
    , 'BenefitCommencementAge':65 #50-120
    , 'PrimaryAnnuitantAge':45 #20-120
    , 'PrimaryAnnuitantGender':"M" #M, F
    , 'BeneficiaryAge':40 #20-120
    , 'BeneficiaryGender':'M' #M, F
    , 'ValuationYear':2025 #1990-2030
    , 'MortalityBeforeBCA':"RP2014_Employee" #Pri2012_Total_Employee
    , 'MortalityAfterBCA':"RP2014_HealthyAnnuit" #Pri2012_Total_Retiree
    , 'ProjectionMethod':"None" #None, Static, Generational
    , 'ProjectionScale':"AA" #
    , 'StaticProjectionYears':0 #0-50
    , 'BlendMortalityRates':False #TRUE, FALSE
    , 'BlendingMalePercentage':.5 #0-1
    , 'SetbackYearsMale':0 #-10->10
    , 'SetbackYearsFemale':0 #-10->10
}
Test17ExpectedResult = 4.4245
ExecuteTest(17, Test17Inputs, Test17ExpectedResult)

#Test 18: RP 2000, AA, Static
Test18Inputs = {
    'DiscountRate':.05 #0-1
    , 'AnnualCOLA':0.0 #0-1
    , 'AnnuityType':'SLA' # SLA, J&S, C&L, JL 
    , 'SurvivorBenefitPrct':0.0 #0-1
    , 'PaymentFrequency':'ABOY'  #ABOY
    , 'CertainPeriod':0 #0-15
    , 'BenefitCommencementAge':65 #50-120
    , 'PrimaryAnnuitantAge':45 #20-120
    , 'PrimaryAnnuitantGender':"M" #M, F
    , 'BeneficiaryAge':40 #20-120
    , 'BeneficiaryGender':'M' #M, F
    , 'ValuationYear':2025 #1990-2030
    , 'MortalityBeforeBCA':"RP2000_Employee" #Pri2012_Total_Employee
    , 'MortalityAfterBCA':"RP2000_HealthyAnnuit" #Pri2012_Total_Retiree
    , 'ProjectionMethod':"Static" #None, Static, Generational
    , 'ProjectionScale':"AA" #
    , 'StaticProjectionYears':2025-2000 #0-50
    , 'BlendMortalityRates':False #TRUE, FALSE
    , 'BlendingMalePercentage':.5 #0-1
    , 'SetbackYearsMale':0 #-10->10
    , 'SetbackYearsFemale':0 #-10->10
}
Test18ExpectedResult = 4.8553
ExecuteTest(18, Test18Inputs, Test18ExpectedResult)

#Test 19: RP 2014, MP2021, Generational
Test19Inputs = {
    'DiscountRate':.05 #0-1
    , 'AnnualCOLA':0.0 #0-1
    , 'AnnuityType':'SLA' # SLA, J&S, C&L, JL 
    , 'SurvivorBenefitPrct':0.0 #0-1
    , 'PaymentFrequency':'ABOY'  #ABOY
    , 'CertainPeriod':0 #0-15
    , 'BenefitCommencementAge':65 #50-120
    , 'PrimaryAnnuitantAge':45 #20-120
    , 'PrimaryAnnuitantGender':"M" #M, F
    , 'BeneficiaryAge':40 #20-120
    , 'BeneficiaryGender':'M' #M, F
    , 'ValuationYear':2025 #1990-2030
    , 'MortalityBeforeBCA':"RP2014_Employee" #Pri2012_Total_Employee
    , 'MortalityAfterBCA':"RP2014_HealthyAnnuit" #Pri2012_Total_Retiree
    , 'ProjectionMethod':"Generational" #None, Static, Generational
    , 'ProjectionScale':"MP2021" #
    , 'StaticProjectionYears':0 #0-50
    , 'BlendMortalityRates':False #TRUE, FALSE
    , 'BlendingMalePercentage':.5 #0-1
    , 'SetbackYearsMale':0 #-10->10
    , 'SetbackYearsFemale':0 #-10->10
}
Test19ExpectedResult = 4.8289
ExecuteTest(19, Test19Inputs, Test19ExpectedResult)

#Test 20: PRI 2012, MP 2021, Generational, J&S, different genders
Test20Inputs = {
    'DiscountRate':.05 #0-1
    , 'AnnualCOLA':0.0 #0-1
    , 'AnnuityType':'J&S' # SLA, J&S, C&L, JL 
    , 'SurvivorBenefitPrct':0.5 #0-1
    , 'PaymentFrequency':'ABOY'  #ABOY
    , 'CertainPeriod':0 #0-15
    , 'BenefitCommencementAge':65 #50-120
    , 'PrimaryAnnuitantAge':45 #20-120
    , 'PrimaryAnnuitantGender':"M" #M, F
    , 'BeneficiaryAge':40 #20-120
    , 'BeneficiaryGender':'F' #M, F
    , 'ValuationYear':2025 #1990-2030
    , 'MortalityBeforeBCA':"Pri2012_Total_Employee" #Pri2012_Total_Employee
    , 'MortalityAfterBCA':"Pri2012_Total_Retiree" #Pri2012_Total_Retiree
    , 'ProjectionMethod':"Generational" #None, Static, Generational
    , 'ProjectionScale':"MP2021" #
    , 'StaticProjectionYears':2025-2012 #0-50
    , 'BlendMortalityRates':False #TRUE, FALSE
    , 'BlendingMalePercentage':.5 #0-1
    , 'SetbackYearsMale':0 #-10->10
    , 'SetbackYearsFemale':0 #-10->10
}
Test20ExpectedResult = 5.4681
ExecuteTest(20, Test20Inputs, Test20ExpectedResult)

#Test 21: Mort Blend
Test21Inputs = {
    'DiscountRate':.05 #0-1
    , 'AnnualCOLA':0.0 #0-1
    , 'AnnuityType':'SLA' # SLA, J&S, C&L, JL 
    , 'SurvivorBenefitPrct':0.0 #0-1
    , 'PaymentFrequency':'ABOY'  #ABOY
    , 'CertainPeriod':0 #0-15
    , 'BenefitCommencementAge':65 #50-120
    , 'PrimaryAnnuitantAge':45 #20-120
    , 'PrimaryAnnuitantGender':"M" #M, F
    , 'BeneficiaryAge':40 #20-120
    , 'BeneficiaryGender':'M' #M, F
    , 'ValuationYear':2025 #1990-2030
    , 'MortalityBeforeBCA':"Pri2012_Total_Employee" #Pri2012_Total_Employee
    , 'MortalityAfterBCA':"Pri2012_Total_Retiree" #Pri2012_Total_Retiree
    , 'ProjectionMethod':"None" #None, Static, Generational
    , 'ProjectionScale':"AA" #
    , 'StaticProjectionYears':0 #0-50
    , 'BlendMortalityRates':True #TRUE, FALSE
    , 'BlendingMalePercentage':.5 #0-1
    , 'SetbackYearsMale':0 #-10->10
    , 'SetbackYearsFemale':0 #-10->10
}
Test21ExpectedResult = 4.5612
ExecuteTest(21, Test21Inputs, Test21ExpectedResult)

#Test 22: M Set back
Test22Inputs = {
    'DiscountRate':.05 #0-1
    , 'AnnualCOLA':0.0 #0-1
    , 'AnnuityType':'SLA' # SLA, J&S, C&L, JL 
    , 'SurvivorBenefitPrct':0.0 #0-1
    , 'PaymentFrequency':'ABOY'  #ABOY
    , 'CertainPeriod':0 #0-15
    , 'BenefitCommencementAge':65 #50-120
    , 'PrimaryAnnuitantAge':45 #20-120
    , 'PrimaryAnnuitantGender':"M" #M, F
    , 'BeneficiaryAge':40 #20-120
    , 'BeneficiaryGender':'M' #M, F
    , 'ValuationYear':2025 #1990-2030
    , 'MortalityBeforeBCA':"Pri2012_Total_Employee" #Pri2012_Total_Employee
    , 'MortalityAfterBCA':"Pri2012_Total_Retiree" #Pri2012_Total_Retiree
    , 'ProjectionMethod':"None" #None, Static, Generational
    , 'ProjectionScale':"AA" #
    , 'StaticProjectionYears':0 #0-50
    , 'BlendMortalityRates':False #TRUE, FALSE
    , 'BlendingMalePercentage':.5 #0-1
    , 'SetbackYearsMale':3 #-10->10
    , 'SetbackYearsFemale':0 #-10->10
}
Test22ExpectedResult = 4.8219
ExecuteTest(22, Test22Inputs, Test22ExpectedResult)

#Test 23: M Set Fwd
Test23Inputs = {
    'DiscountRate':.05 #0-1
    , 'AnnualCOLA':0.0 #0-1
    , 'AnnuityType':'SLA' # SLA, J&S, C&L, JL 
    , 'SurvivorBenefitPrct':0.0 #0-1
    , 'PaymentFrequency':'ABOY'  #ABOY
    , 'CertainPeriod':0 #0-15
    , 'BenefitCommencementAge':65 #50-120
    , 'PrimaryAnnuitantAge':45 #20-120
    , 'PrimaryAnnuitantGender':"M" #M, F
    , 'BeneficiaryAge':40 #20-120
    , 'BeneficiaryGender':'M' #M, F
    , 'ValuationYear':2025 #1990-2030
    , 'MortalityBeforeBCA':"Pri2012_Total_Employee" #Pri2012_Total_Employee
    , 'MortalityAfterBCA':"Pri2012_Total_Retiree" #Pri2012_Total_Retiree
    , 'ProjectionMethod':"None" #None, Static, Generational
    , 'ProjectionScale':"AA" #
    , 'StaticProjectionYears':0 #0-50
    , 'BlendMortalityRates':False #TRUE, FALSE
    , 'BlendingMalePercentage':.5 #0-1
    , 'SetbackYearsMale':-3 #-10->10
    , 'SetbackYearsFemale':0 #-10->10
}
Test23ExpectedResult = 3.9319
ExecuteTest(23, Test23Inputs, Test23ExpectedResult)

#Test 24: F Set Back
Test24Inputs = {
    'DiscountRate':.05 #0-1
    , 'AnnualCOLA':0.0 #0-1
    , 'AnnuityType':'SLA' # SLA, J&S, C&L, JL 
    , 'SurvivorBenefitPrct':0.0 #0-1
    , 'PaymentFrequency':'ABOY'  #ABOY
    , 'CertainPeriod':0 #0-15
    , 'BenefitCommencementAge':65 #50-120
    , 'PrimaryAnnuitantAge':45 #20-120
    , 'PrimaryAnnuitantGender':"F" #M, F
    , 'BeneficiaryAge':40 #20-120
    , 'BeneficiaryGender':'M' #M, F
    , 'ValuationYear':2025 #1990-2030
    , 'MortalityBeforeBCA':"Pri2012_Total_Employee" #Pri2012_Total_Employee
    , 'MortalityAfterBCA':"Pri2012_Total_Retiree" #Pri2012_Total_Retiree
    , 'ProjectionMethod':"None" #None, Static, Generational
    , 'ProjectionScale':"AA" #
    , 'StaticProjectionYears':0 #0-50
    , 'BlendMortalityRates':False #TRUE, FALSE
    , 'BlendingMalePercentage':.5 #0-1
    , 'SetbackYearsMale':0 #-10->10
    , 'SetbackYearsFemale':3 #-10->10
}
Test24ExpectedResult = 5.1344
ExecuteTest(24, Test24Inputs, Test24ExpectedResult)

#Test 25: F Set Fwd
Test25Inputs = {
    'DiscountRate':.05 #0-1
    , 'AnnualCOLA':0.0 #0-1
    , 'AnnuityType':'JL' # SLA, J&S, C&L, JL 
    , 'SurvivorBenefitPrct':0.5 #0-1
    , 'PaymentFrequency':'ABOY'  #ABOY
    , 'CertainPeriod':0 #0-15
    , 'BenefitCommencementAge':65 #50-120
    , 'PrimaryAnnuitantAge':45 #20-120
    , 'PrimaryAnnuitantGender':"F" #M, F
    , 'BeneficiaryAge':40 #20-120
    , 'BeneficiaryGender':'M' #M, F
    , 'ValuationYear':2025 #1990-2030
    , 'MortalityBeforeBCA':"Pri2012_Total_Employee" #Pri2012_Total_Employee
    , 'MortalityAfterBCA':"Pri2012_Total_Retiree" #Pri2012_Total_Retiree
    , 'ProjectionMethod':"None" #None, Static, Generational
    , 'ProjectionScale':"AA" #
    , 'StaticProjectionYears':0 #0-50
    , 'BlendMortalityRates':False #TRUE, FALSE
    , 'BlendingMalePercentage':.5 #0-1
    , 'SetbackYearsMale':0 #-10->10
    , 'SetbackYearsFemale':-3 #-10->10
}
Test25ExpectedResult = 4.2953
ExecuteTest(25, Test25Inputs, Test25ExpectedResult)


'''

Note - I would very much like to be able to use an array of discount rates at some point.
Right now, my expected results are coming from the SOA calculator (https://afc.soa.org/#Calculator).
That does not currently work with an array of discount rates, so I will need to find a different way of verifying calcs when I move to a discount array.

Note 2 - I don't like the way this workbook is set up
(1) I think I should return a value instead of printing a value. My feeling is that such a construction would be easier to include into a CICD framework
(2) I think numbering the tests is weird. I should put them in a named tuple with: Name, Input dict, expected output, maybe a blank field for result??

Additional Test cases:
COLA with mthly
COLA with Annual EOY
COLA with mthly EOM
J&S with EOY/EOM


'''