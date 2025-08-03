import os
import random
import Annuity_Factor_Calculator as AFC

maxPctError = .001 #setting 1% error. Will revise this to the max acceptable error when moving to a new actuarial system.

cwd = os.getcwd()

def ExecuteTest(testMode = True):
    Inputs = GenerateInputs()

    print(Inputs)

    ExpectedResult = float(input("Enter Expected Result Here:"))

    Calculator = AFC.Annuity_Factor_Calculator(Inputs)
    if testMode:
        ActualResult = Calculator.CalcPVF(testMode)
    else:
        ActualResult = Calculator.CalcPVF()
        
    pctError = abs((ExpectedResult - ActualResult)/ExpectedResult)
    if pctError<maxPctError: 
        if ExpectedResult == ActualResult:
            resultString = "Test PASSED: EXACT"
        else:
            resultString = "Test PASSED - Expected: "+str(ExpectedResult)+", Returned: "+str(ActualResult) +", Percent Error: " + str(pctError)
    else:
        resultString = "Test FAILED - Expected: "+str(ExpectedResult)+", Returned: "+str(ActualResult)

    print(resultString)

def GenerateInputs():
    InputCategories = ['DiscountRate'
    , 'AnnualCOLA'
    , 'AnnuityType'
    , 'SurvivorBenefitPrct'
    , 'PaymentFrequency'
    , 'CertainPeriod'
    , 'BenefitCommencementAge'
    , 'PrimaryAnnuitantAge'
    , 'PrimaryAnnuitantGender'  
    , 'BeneficiaryAge'
    , 'BeneficiaryGender'
    , 'ValuationYear'
    , 'MortalityBeforeBCA'
    , 'MortalityAfterBCA'
    , 'ProjectionMethod'
    , 'ProjectionScale'
    , 'StaticProjectionYears'
    , 'BlendMortalityRates'
    , 'BlendingMalePercentage'
    , 'SetbackYearsMale'
    , 'SetbackYearsFemale']

    #Randomization Types - 1 == Category, 2 == Float Range, 3 == Int Range
    RandomizationType = {'DiscountRate':2
    , 'AnnualCOLA':2
    , 'AnnuityType':1
    , 'SurvivorBenefitPrct':2
    , 'PaymentFrequency':1
    , 'CertainPeriod':3
    , 'BenefitCommencementAge':3
    , 'PrimaryAnnuitantAge':3
    , 'PrimaryAnnuitantGender': 1
    , 'BeneficiaryAge': 3
    , 'BeneficiaryGender': 1
    , 'ValuationYear': 3
    , 'MortalityBeforeBCA': 1
    , 'MortalityAfterBCA': 1
    , 'ProjectionMethod': 1
    , 'ProjectionScale': 1
    , 'StaticProjectionYears': 3
    , 'BlendMortalityRates': 1
    , 'BlendingMalePercentage': 2
    , 'SetbackYearsMale': 3
    , 'SetbackYearsFemale': 3}

    RandomizationOptions  = {'DiscountRate':[0, .1, 4]
    , 'AnnualCOLA':[0, .1, 2]
    , 'AnnuityType':['SLA', 'J&S', 'C&L', 'JL']
    , 'SurvivorBenefitPrct':[0, 1, 1]
    , 'PaymentFrequency':['ABOY', 'AEOY', 'MBOM', 'MEOM', 'MAPPX']
    , 'CertainPeriod':[0, 15]
    , 'BenefitCommencementAge':[50, 90] #SOA calc goes down to 20 but I might need some table extension capabilities
    , 'PrimaryAnnuitantAge':[20, 120]
    , 'PrimaryAnnuitantGender': ['M', 'F']
    , 'BeneficiaryAge': [20, 120]
    , 'BeneficiaryGender': ['M', 'F']
    , 'ValuationYear': [1990, 2030]
    , 'MortalityBeforeBCA': MortalityBeforeBCAList
    , 'MortalityAfterBCA': MortalityAfterBCAList
    , 'ProjectionMethod': ['None', 'Static', 'Generational']
    , 'ProjectionScale': ProjectionScaleList
    , 'StaticProjectionYears': [0, 50]
    , 'BlendMortalityRates': [True, False]
    , 'BlendingMalePercentage': [0, 1, 2]
    , 'SetbackYearsMale': [-10, 10]
    , 'SetbackYearsFemale': [-10, 10]}

    Inputs = {}

    for Input in InputCategories:
        match RandomizationType[Input]:
            case 1:
                Inputs[Input] = random.choice(RandomizationOptions[Input])
            case 2:
                Inputs[Input] = round(random.uniform(RandomizationOptions[Input][0], RandomizationOptions[Input][1]), RandomizationOptions[Input][2])
            case 3:
                Inputs[Input] = random.randint(RandomizationOptions[Input][0], RandomizationOptions[Input][1])
    
    return Inputs

            

MortalityBeforeBCAList = ['RPH2014_Top25%_Employee', 'Pri2012_Bot25_Employee', 'PubTH_2010A_Employee', '1983_GAM_Basic', 'RP2000_Disabled', '1983_IAM', 'RPH2014_Employee', 'Pri2012_Top25_Employee', 'PubGH_2010_Employee', 'RPH2014_Bot25%_Employee', 'Pri2012_Total_Employee', 'RP1992_Disabled', 'RP2014_Top25%_Employee', 'PubS_2010A_Employee', 'PubNSH_2010_Disabled', 'Pri2012_Total_Disabled', 'PubG_2010_Employee', '1971_GAM', 'RP2014_BlueCol_Employee', '1951_GAM', 'PubTH_2010_Employee', 'RP2000_WhiteCol', 'PubG_2010B_Employee', 'RPH2014_WhiteCol_Employee', 'RP2014_Bot25%_Employee', 'CPM2014', 'PriH2012_Total_Employee', 'PubG_2010A_Employee', '2012_IAM_Period', 'PriH2012_Total_Disabled', 'RP1992_CombinedHealthy', 'PubSH_2010_Disabled', 'RP2000_Employee', 'PubS_2010_Employee', 'PubS_2010_Disabled', 'RP2014_Employee', 'PubGH_2010A_Employee', 'PubTH_2010B_Employee', 'CPM2014_Public', 'PubT_2010_Employee', 'PriH2012_WhiteCol_Employee', 'CPM2014_Private', '1994_GAM_Static', 'RP2000_BlueCol', 'PubNS_2010_Disabled', 'UP_94', 'PriH2012_BlueCol_Employee', 'PubGH_2010B_Employee', 'PubT_2010A_Employee', 'PubS_2010B_Employee', '1983_GAM', 'RP2014_WhiteCol_Employee', 'UP84_unisex', 'RPH2014_BlueCol_Employee', '2012_IAM_Basic', 'Pri2012_WhiteCol_Employee', 'Pri2012_BlueCol_Employee', 'PubSH_2010B_Employee', 'RP1992_Employee', 'PriH2012_Bot25_Employee', 'PriH2012_Top25_Employee', 'PubSH_2010_Employee', 'PubT_2010B_Employee', 'PubSH_2010A_Employee']
MortalityAfterBCAList =  ['Pri2012_Total_ContAnn', 'Pub_2010A_ContSurvivor', 'PriH2012_Top25_Retiree', '1983_GAM_Basic', 'Pri2012_WhiteCol_NondisAnn', 'PriH2012_BlueCol_NondisAnn', '1983_IAM', 'RP2000_Disabled', 'PubS_2010_Retiree', 'RP1992_HealthyAnnuit', 'PubTH_2010B_Retiree', 'RP1992_Disabled', 'RP2000_HealthyAnnuit', 'Pub_2010_ContSurvivor', 'PriH2012_WhiteCol_ContAnn', 'PubGH_2010A_Retiree', 'PriH2012_Total_ContAnn', 'PubSH_2010_Retiree', 'PubNSH_2010_Disabled', 'PubT_2010B_Retiree', 'PubH_2010B_ContSurvivor', 'PubH_2010A_ContSurvivor', 'RP2014_HealthyAnnuit', 'Pri2012_WhiteCol_ContAnn', 'Pri2012_Total_Disabled', '1971_GAM', 'PubTH_2010_Retiree', '1951_GAM', 'PriH2012_Bot25_Retiree', 'RP2000_WhiteCol', 'PubG_2010_Retiree', 'PubGH_2010_Retiree', 'PriH2012_WhiteCol_Retiree', 'CPM2014', 'PubH_2010_ContSurvivor', 'PriH2012_WhiteCol_NondisAnn', 'Pri2012_WhiteCol_Retiree', 'PubSH_2010B_Retiree', 'PriH2012_Total_Disabled', 'RP1992_CombinedHealthy', 'PubSH_2010_Disabled', 'Pri2012_BlueCol_ContAnn', 'PriH2012_Total_NondisAnn', 'PriH2012_BlueCol_ContAnn', 'PubS_2010_Disabled', '2012_IAM_Period', 'CPM2014_Public', 'CPM2014_Private', '1994_GAM_Static', 'RP2000_BlueCol', 'Pri2012_Total_NondisAnn', 'PubNS_2010_Disabled', 'UP_94', 'PubT_2010A_Retiree', 'PriH2012_BlueCol_Retiree', 'PubTH_2010A_Retiree', '1983_GAM', 'PubSH_2010A_Retiree', 'Pri2012_BlueCol_Retiree', 'PriH2012_Total_Retiree', 'PubS_2010A_Retiree', 'PubS_2010B_Retiree', 'Pri2012_BlueCol_NondisAnn', 'UP84_unisex', 'Pri2012_Bot25_Retiree', 'Pub_2010B_ContSurvivor', 'PubG_2010A_Retiree', 'Pri2012_Top25_Retiree', '2012_IAM_Basic', 'PubG_2010B_Retiree', 'Pri2012_Total_Retiree', 'PubT_2010_Retiree']
ProjectionScaleList = ['AA', 'BB_1D', 'G2', 'G3', 'CPM2014_B1', 'AA', 'BB_1D', 'G2', 'G3', 'CPM2014_B1']

#Test 0: Basic
Test0Inputs = {
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
ExecuteTest()