import os
import Annuity_Factor_Calculator as AFC
import pandas as pd

maxPctError = .001 #setting 1% error. Will revise this to the max acceptable error when moving to a new actuarial system.

cwd = os.getcwd()

def ExecuteTest(Inputs, ExpectedResult, testMode = False):
    Calculator = AFC.Annuity_Factor_Calculator(Inputs)
    if testMode:
        ActualResult = Calculator.CalcPVF(testMode)
    else:
        ActualResult = Calculator.CalcPVF()
        
    pctError = abs((ExpectedResult - ActualResult)/ExpectedResult)
    if pctError<maxPctError: 
        if ExpectedResult == ActualResult:
            result = ['ExactPass', ExpectedResult, ActualResult, pctError]
        else:
            result = ['Pass', ExpectedResult, ActualResult, pctError]
    else:
        result = ['Fail', ExpectedResult, ActualResult, pctError]

    return result
        


annuity_categorical_variables = {
    'AnnuityType': ['SLA', 'J&S', 'C&L', 'JL'] 
    , 'PaymentFrequency':['ABOY', 'AEOY', 'ABOM', 'AEOM', 'MAPPX']
    , 'PrimaryAnnuitantGender':["M", 'F']
    , 'BeneficiaryGender':['M', 'F']
}

TestInputs_NoProj = {
    'DiscountRate':.04 #0-1
    , 'AnnualCOLA':0 #0-1
    , 'AnnuityType':None
    , 'SurvivorBenefitPrct':0.5 #0-1
    , 'PaymentFrequency':None
    , 'CertainPeriod': 10 #0-15
    , 'BenefitCommencementAge':62 #50-120
    , 'PrimaryAnnuitantAge':45 #20-120
    , 'PrimaryAnnuitantGender':"M" #M, F
    , 'BeneficiaryAge':45 #20-120
    , 'BeneficiaryGender':'M' #M, F
    , 'ValuationYear':2025 #1990-2030
    , 'MortalityBeforeBCA':"Pri2012_Total_Employee" #Pri2012_Total_Employee
    , 'MortalityAfterBCA':"Pri2012_Total_Retiree" #Pri2012_Total_Retiree
    , 'ProjectionMethod':"None" #None, Static, Generational
    , 'ProjectionScale':None #
    , 'StaticProjectionYears':0 #0-50
    , 'BlendMortalityRates':False #TRUE, FALSE
    , 'BlendingMalePercentage':None #0-1
    , 'SetbackYearsMale':0 #-10->10
    , 'SetbackYearsFemale':0 #-10->10
}
expected_results_NoProj = {
    'SLA_ABOY_M': 7.1227
    ,'SLA_ABOY_F': 7.6274 
    ,'SLA_AEOY_M': 6.6278
    ,'SLA_AEOY_F': 7.1258
    ,'SLA_MBOM_M': 6.8944
    ,'SLA_MBOM_F': 7.3961
    ,'SLA_MEOM_M': 6.8531
    ,'SLA_MEOM_F': 7.3543
    ,'SLA_MAPPX_M': 6.8958
    ,'SLA_MAPPX_F': 7.3975
    ,'J&S_ABOY_M_M': 7.8160
    ,'J&S_ABOY_M_F': 7.9253
    ,'J&S_ABOY_F_M': 8.1776
    ,'J&S_ABOY_F_F': 8.2715
    ,'J&S_AEOY_M_M': 7.3121
    ,'J&S_AEOY_M_F': 7.4214
    ,'J&S_AEOY_F_M': 7.6704
    ,'J&S_AEOY_F_F': 7.7642
    ,'J&S_MBOM_M_M': 7.5837
    ,'J&S_MBOM_M_F': 7.6930
    ,'J&S_MBOM_F_M': 7.9439
    ,'J&S_MBOM_F_F': 8.0378
    ,'J&S_MEOM_M_M': 7.5417
    ,'J&S_MEOM_M_F': 7.6510
    ,'J&S_MEOM_F_M': 7.9016
    ,'J&S_MEOM_F_F': 7.9955
    ,'J&S_MAPPX_M_M': 7.5891
    ,'J&S_MAPPX_M_F': 7.6985
    ,'J&S_MAPPX_F_M': 7.9477
    ,'J&S_MAPPX_F_F': 8.0416
    ,'C&L_ABOY_M': 7.3075
    ,'C&L_ABOY_F': 7.7702
    ,'C&L_AEOY_M': 6.8536
    ,'C&L_AEOY_F': 7.3007
    ,'C&L_MBOM_M': 7.0983
    ,'C&L_MBOM_F': 7.5539
    ,'C&L_MEOM_M': 7.0605
    ,'C&L_MEOM_F': 7.5148
    ,'C&L_MAPPX_M': 7.0806
    ,'C&L_MAPPX_F': 7.5403
    ,'JL_ABOY_M_M': 5.7361
    ,'JL_ABOY_M_F': 6.0222
    ,'JL_ABOY_F_M': 6.0222 
    ,'JL_ABOY_F_F': 6.3391
    ,'JL_AEOY_M_M': 5.2590
    ,'JL_AEOY_M_F': 5.5386
    ,'JL_AEOY_F_M': 5.5386
    ,'JL_AEOY_F_F': 5.8489
    ,'JL_MBOM_M_M': 5.5157
    ,'JL_MBOM_M_F': 5.7988
    ,'JL_MBOM_F_M': 5.7988
    ,'JL_MBOM_F_F': 6.1128
    ,'JL_MEOM_M_M': 5.4760
    ,'JL_MEOM_M_F': 5.7585
    ,'JL_MEOM_F_M': 5.7585
    ,'JL_MEOM_F_F': 6.0719
    ,'JL_MAPPX_M_M': 5.5093
    ,'JL_MAPPX_M_F': 5.7953
    ,'JL_MAPPX_F_M': 5.7922 #TODO investigate this
    ,'JL_MAPPX_F_F': 6.1092
}


TestInputs_StaticProj = {
    'DiscountRate':.04 #0-1
    , 'AnnualCOLA':0 #0-1
    , 'AnnuityType':None
    , 'SurvivorBenefitPrct':0.5 #0-1
    , 'PaymentFrequency':None
    , 'CertainPeriod': 10 #0-15
    , 'BenefitCommencementAge':62 #50-120
    , 'PrimaryAnnuitantAge':45 #20-120
    , 'PrimaryAnnuitantGender':"M" #M, F
    , 'BeneficiaryAge':45 #20-120
    , 'BeneficiaryGender':'M' #M, F
    , 'ValuationYear':2025 #1990-2030
    , 'MortalityBeforeBCA':"Pri2012_Total_Employee" #Pri2012_Total_Employee
    , 'MortalityAfterBCA':"Pri2012_Total_Retiree" #Pri2012_Total_Retiree
    , 'ProjectionMethod':"Static" #None, Static, Generational
    , 'ProjectionScale':'AA' #
    , 'StaticProjectionYears':13 #ADJUSTED TO ACCOUNT FOR SOA AUTOMATIC PROJECTION
    , 'BlendMortalityRates':False #TRUE, FALSE
    , 'BlendingMalePercentage':None #0-1
    , 'SetbackYearsMale':0 #-10->10
    , 'SetbackYearsFemale':0 #-10->10
}
expected_results_StaticProj = {
    'SLA_ABOY_M': 7.4122
    ,'SLA_ABOY_F': 7.7629
    ,'SLA_AEOY_M': 6.9137
    ,'SLA_AEOY_F': 7.2599
    ,'SLA_MBOM_M': 7.1823
    ,'SLA_MBOM_F': 7.5310
    ,'SLA_MEOM_M': 7.1808
    ,'SLA_MEOM_F': 7.4891
    ,'SLA_MAPPX_M': 7.1837
    ,'SLA_MAPPX_F': 7.5324
    ,'J&S_ABOY_M_M': 8.0659
    ,'J&S_ABOY_M_F': 8.1455
    ,'J&S_ABOY_F_M': 8.3208
    ,'J&S_ABOY_F_F': 8.3923
    ,'J&S_AEOY_M_M': 7.5601
    ,'J&S_AEOY_M_F': 7.6397
    ,'J&S_AEOY_F_M': 7.8128
    ,'J&S_AEOY_F_F': 7.8842
    ,'J&S_MBOM_M_M': 7.8328
    ,'J&S_MBOM_M_F': 7.9124
    ,'J&S_MBOM_F_M': 8.0867
    ,'J&S_MBOM_F_F': 8.1582
    ,'J&S_MEOM_M_M': 7.7906
    ,'J&S_MEOM_M_F': 7.8702
    ,'J&S_MEOM_F_M': 8.0444
    ,'J&S_MEOM_F_F': 8.1158
    ,'J&S_MAPPX_M_M': 7.8374
    ,'J&S_MAPPX_M_F': 7.9170
    ,'J&S_MAPPX_F_M': 8.0903
    ,'J&S_MAPPX_F_F': 8.1618
    ,'C&L_ABOY_M': 7.5680
    ,'C&L_ABOY_F': 7.8973
    ,'C&L_AEOY_M': 7.1042
    ,'C&L_AEOY_F': 7.4244
    ,'C&L_MBOM_M': 7.3543
    ,'C&L_MBOM_F': 7.6794
    ,'C&L_MEOM_M': 7.3156
    ,'C&L_MEOM_F': 7.6400
    ,'C&L_MAPPX_M': 7.3395
    ,'C&L_MAPPX_F': 7.6668
    ,'JL_ABOY_M_M': 6.1050
    ,'JL_ABOY_M_F': 7.2964
    ,'JL_ABOY_F_M': 6.2964
    ,'JL_ABOY_F_F': 6.5041
    ,'JL_AEOY_M_M': 5.6208
    ,'JL_AEOY_M_F': 5.8079
    ,'JL_AEOY_F_M': 5.8079
    ,'JL_AEOY_F_F': 6.0114
    ,'JL_MBOM_M_M': 5.8814
    ,'JL_MBOM_M_F': 6.0709
    ,'JL_MBOM_F_M': 6.0709
    ,'JL_MBOM_F_F': 6.2767
    ,'JL_MEOM_M_M': 5.8411
    ,'JL_MEOM_M_F': 6.0302
    ,'JL_MEOM_F_M': 6.0302
    ,'JL_MEOM_F_F': 6.2356
    ,'JL_MAPPX_M_M': 5.8765
    ,'JL_MAPPX_M_F': 6.0679
    ,'JL_MAPPX_F_M': 6.0658
    ,'JL_MAPPX_F_F': 6.2736
}


TestInputs_GenerationalProj = {
    'DiscountRate':.04 #0-1
    , 'AnnualCOLA':0 #0-1
    , 'AnnuityType':None
    , 'SurvivorBenefitPrct':0.5 #0-1
    , 'PaymentFrequency':None
    , 'CertainPeriod': 10 #0-15
    , 'BenefitCommencementAge':62 #50-120
    , 'PrimaryAnnuitantAge':45 #20-120
    , 'PrimaryAnnuitantGender':"M" #M, F
    , 'BeneficiaryAge':45 #20-120
    , 'BeneficiaryGender':'M' #M, F
    , 'ValuationYear':2025 #1990-2030
    , 'MortalityBeforeBCA':"Pri2012_Total_Employee" #Pri2012_Total_Employee
    , 'MortalityAfterBCA':"Pri2012_Total_Retiree" #Pri2012_Total_Retiree
    , 'ProjectionMethod':"Generational" #None, Static, Generational
    , 'ProjectionScale':'MP2021' #
    , 'StaticProjectionYears':0 #0-50
    , 'BlendMortalityRates':False #TRUE, FALSE
    , 'BlendingMalePercentage':None #0-1
    , 'SetbackYearsMale':0 #-10->10
    , 'SetbackYearsFemale':0 #-10->10
}
expected_results_GenerationalProj = {
    'SLA_ABOY_M': 7.7423
    ,'SLA_ABOY_F': 8.2342
    ,'SLA_AEOY_M': 7.2454
    ,'SLA_AEOY_F': 7.7310
    ,'SLA_MBOM_M': 7.5132
    ,'SLA_MBOM_F': 8.0023
    ,'SLA_MEOM_M': 7.4718
    ,'SLA_MEOM_F': 7.9604
    ,'SLA_MAPPX_M': 7.5145
    ,'SLA_MAPPX_F': 8.0035
    ,'J&S_ABOY_M_M': 8.4152
    ,'J&S_ABOY_M_F': 8.5105
    ,'J&S_ABOY_F_M': 8.7565
    ,'J&S_ABOY_F_F': 8.8373
    ,'J&S_AEOY_M_M': 7.9104
    ,'J&S_AEOY_M_F': 8.0055
    ,'J&S_AEOY_F_M': 8.2483
    ,'J&S_AEOY_F_F': 8.3291
    ,'J&S_MBOM_M_M': 8.1826
    ,'J&S_MBOM_M_F': 8.2779
    ,'J&S_MBOM_F_M': 8.5224
    ,'J&S_MBOM_F_F': 8.6033
    ,'J&S_MEOM_M_M': 8.1406
    ,'J&S_MEOM_M_F': 8.2358
    ,'J&S_MEOM_F_M': 8.4801
    ,'J&S_MEOM_F_F': 8.5609
    ,'J&S_MAPPX_M_M': 8.1875
    ,'J&S_MAPPX_M_F': 8.2828
    ,'J&S_MAPPX_F_M': 8.5258
    ,'J&S_MAPPX_F_F': 8.6067
    ,'C&L_ABOY_M': 7.8880
    ,'C&L_ABOY_F': 8.3423
    ,'C&L_AEOY_M': 7.4224
    ,'C&L_AEOY_F': 7.8623
    ,'C&L_MBOM_M': 7.6735
    ,'C&L_MBOM_F': 8.1213
    ,'C&L_MEOM_M': 7.6347
    ,'C&L_MEOM_F': 8.0812
    ,'C&L_MAPPX_M': 7.6603
    ,'C&L_MAPPX_F': 8.1117
    ,'JL_ABOY_M_M': 6.3963
    ,'JL_ABOY_M_F': 6.6977
    ,'JL_ABOY_F_M': 6.6977
    ,'JL_ABOY_F_F': 7.0279
    ,'JL_AEOY_M_M': 5.9154
    ,'JL_AEOY_M_F': 6.2107
    ,'JL_AEOY_F_M': 6.2107
    ,'JL_AEOY_F_F': 6.5346
    ,'JL_MBOM_M_M': 6.1744
    ,'JL_MBOM_M_F': 6.4730
    ,'JL_MBOM_F_M': 6.4730
    ,'JL_MBOM_F_F': 6.8003
    ,'JL_MEOM_M_M': 6.1343
    ,'JL_MEOM_M_F': 6.4324
    ,'JL_MEOM_F_M': 6.4324
    ,'JL_MEOM_F_F': 6.7592
    ,'JL_MAPPX_M_M': 6.1686
    ,'JL_MAPPX_M_F': 6.4700
    ,'JL_MAPPX_F_M': 6.4671 #TODO Investigate
    ,'JL_MAPPX_F_F': 6.7973
}

testResults_df = pd.DataFrame({'TestName':[], 'ProjectionType':[], 'TestResult':[], 'TestExpectedResult':[], 'TestActualResult':[], 'TestPctError':[]})

#Run NoProj Tests
for test in expected_results_NoProj.keys():
    inputs_for_test = test.split('_')

    AnnuityType = inputs_for_test[0]
    PaymentFrequency = inputs_for_test[1]
    PrimaryAnnuitantGender = inputs_for_test[2]
    if AnnuityType == 'SLA' or AnnuityType == 'C&L':
        BeneficiaryGender = None
    else:
        BeneficiaryGender = inputs_for_test[3]

    TestInputs_NoProj['AnnuityType'] = AnnuityType
    TestInputs_NoProj['PaymentFrequency'] = PaymentFrequency
    TestInputs_NoProj['PrimaryAnnuitantGender'] = PrimaryAnnuitantGender
    TestInputs_NoProj['BeneficiaryGender'] = BeneficiaryGender
  
    this_test_result = ExecuteTest(TestInputs_NoProj, expected_results_NoProj[test])

    result_df = pd.DataFrame({'TestName':[test], 'ProjectionType':['None'], 'TestResult':[this_test_result[0]], 'TestExpectedResult':[this_test_result[1]], 'TestActualResult':[this_test_result[2]], 'TestPctError':[this_test_result[3]]})
    testResults_df = pd.concat([testResults_df, result_df])

#Run Static Tests
for test in expected_results_StaticProj.keys():
    inputs_for_test = test.split('_')

    AnnuityType = inputs_for_test[0]
    PaymentFrequency = inputs_for_test[1]
    PrimaryAnnuitantGender = inputs_for_test[2]
    if AnnuityType == 'SLA' or AnnuityType == 'C&L':
        BeneficiaryGender = None
    else:
        BeneficiaryGender = inputs_for_test[3]

    TestInputs_StaticProj['AnnuityType'] = AnnuityType
    TestInputs_StaticProj['PaymentFrequency'] = PaymentFrequency
    TestInputs_StaticProj['PrimaryAnnuitantGender'] = PrimaryAnnuitantGender
    TestInputs_StaticProj['BeneficiaryGender'] = BeneficiaryGender
  
    this_test_result = ExecuteTest(TestInputs_StaticProj, expected_results_StaticProj[test])

    result_df = pd.DataFrame({'TestName':[test], 'ProjectionType':['Static'], 'TestResult':[this_test_result[0]], 'TestExpectedResult':[this_test_result[1]], 'TestActualResult':[this_test_result[2]], 'TestPctError':[this_test_result[3]]})
    testResults_df = pd.concat([testResults_df, result_df])

#Run Generational Tests
for test in expected_results_GenerationalProj.keys():
    inputs_for_test = test.split('_')

    AnnuityType = inputs_for_test[0]
    PaymentFrequency = inputs_for_test[1]
    PrimaryAnnuitantGender = inputs_for_test[2]
    if AnnuityType == 'SLA' or AnnuityType == 'C&L':
        BeneficiaryGender = None
    else:
        BeneficiaryGender = inputs_for_test[3]

    TestInputs_GenerationalProj['AnnuityType'] = AnnuityType
    TestInputs_GenerationalProj['PaymentFrequency'] = PaymentFrequency
    TestInputs_GenerationalProj['PrimaryAnnuitantGender'] = PrimaryAnnuitantGender
    TestInputs_GenerationalProj['BeneficiaryGender'] = BeneficiaryGender
  
    this_test_result = ExecuteTest(TestInputs_GenerationalProj, expected_results_GenerationalProj[test])

    result_df = pd.DataFrame({'TestName':[test], 'ProjectionType':['Generational'], 'TestResult':[this_test_result[0]], 'TestExpectedResult':[this_test_result[1]], 'TestActualResult':[this_test_result[2]], 'TestPctError':[this_test_result[3]]})
    testResults_df = pd.concat([testResults_df, result_df])

print(testResults_df)
print('Exact Passes: ' + str(testResults_df[testResults_df['TestResult']=='ExactPass']['TestName'].count()))
print('Non Exact Passes: ' + str(testResults_df[testResults_df['TestResult']=='Pass']['TestName'].count()))
print('Fails: ' + str(testResults_df[testResults_df['TestResult']=='Fail']['TestName'].count()))