import json
import os

import Annuity_Factor_Calculator as AFC

cwd = os.getcwd()

#Mort Data path
mortTablePath = cwd + '/Annuity_Factor_Calculator/MortTables/MortTables.parquet'

def ExecuteTest(TestNumber, Inputs, ExpectedResult, mortTablePath):
    ActualResult = AFC.Annuity_Factor_Calculator.CalcPVF(AFC.Annuity_Factor_Calculator, Inputs, mortTablePath)
    if ExpectedResult == ActualResult:
        print("Test " + str(TestNumber) + " PASSED")
    else:
        print("Test " + str(TestNumber) + " FAILED - Expected: "+str(ExpectedResult)+", Returned: "+str(ActualResult))

#Test 1: Basic
Test1Inputs = {
    'DiscountRate':.05 #0-1
    , 'AnnualCOLA':0 #0-1
    , 'AnnuityType':'SLA' # SLA, J&S, C&L, JL 
    , 'SurvivorBenefitPrct':0 #0-1
    , 'PaymentFrequency':'ABOY'  #ABOY
    , 'CertainPeriod(years)': 0#0-15
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
ExecuteTest(1, Test1Inputs, Test1ExpectedResult, mortTablePath)

#Test 2: COLA
Test2Inputs = {
    'DiscountRate':.05 #0-1
    , 'AnnualCOLA':0.025 #0-1
    , 'AnnuityType':'SLA' # SLA, J&S, C&L, JL 
    , 'SurvivorBenefitPrct':0 #0-1
    , 'PaymentFrequency':'ABOY'  #ABOY
    , 'CertainPeriod(years)': 0#0-15
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
Test2ExpectedResult = 5.0246
ExecuteTest(2, Test2Inputs, Test2ExpectedResult, mortTablePath)

'''
#Test 1:
Test1Inputs = {
    'DiscountRate':.05 #0-1
    , 'AnnualCOLA':0 #0-1
    , 'AnnuityType':'SLA' # SLA, J&S, C&L, JL 
    , 'SurvivorBenefitPrct':0 #0-1
    , 'PaymentFrequency':'ABOY'  #ABOY
    , 'CertainPeriod(years)': 0#0-15
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
Test1ExpectedResult = 3.989
ExecuteTest(1, Test1Inputs, Test1ExpectedResult, mortTablePath)
'''

'''
Other tests needed:

all 4 annuity types
all 5 pmt frequencies
all 4 primary/beneficiary gender combinations + both genders with no beneficiary
current age = commencement age
beneficiary older than primary annuitant
3-5 mort tables
all 3 mort projection methods, 2x projection scales of each static and generational
Mort Blend
4 setback scenarios (+/-, m/f)

Note - I would very much like to be able to use an array of discount rates at some point.
Right now, my expected results are coming from the SOA calculator (https://afc.soa.org/#Calculator).
That does not currently work with an array of discount rates, so I will need to find a different way of verifying calcs when I move to a discount array.

'''