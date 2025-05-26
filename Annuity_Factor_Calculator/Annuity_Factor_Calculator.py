import pandas as pd
import numpy as np
import json
import os

cwd = os.getcwd()

#get data - TODO these should be passed as function args
with open(cwd+'/Annuity_Factor_Calculator/userInputs.txt', 'r') as UserInputs:
    UserInputs_dict = json.loads(UserInputs.read())

def GetPaymentTiming(PaymentFrequency):
    match PaymentFrequency:
        case 'ABOY':
            return 0
        case 'AEOY':
            return 1
        case 'MEBOM':
            return "NOT BUILT YET" #TODO
        case 'MEEOM':
            return "NOT BUILT YET" #TODO
        case 'MAPPX':
            return "NOT BUILT YET" #TODO
        case _:
            return "INVALID INPUT"

#determine pmt timing
pmt_timing = GetPaymentTiming(UserInputs_dict['PaymentFrequency'])

def PrepMortality(BaseMortPath, PreCommencementMortality, PostCommencementMortality, PrimaryAnnuitantGender, PrimaryAnnuitantAge, BenefitCommencementAge):
    
    mort_df = pd.read_parquet(BaseMortPath
                          , columns=['MortalityTableName', 'BaseYear', 'Sex', 'Age', 'Qx']
                          , filters = [[('MortalityTableName', '==', PreCommencementMortality)], [('MortalityTableName', '==', PostCommencementMortality)]]) 

    Ptcp_PreRetMort_df = mort_df[(mort_df['MortalityTableName'] == PreCommencementMortality)
                          &(mort_df['Sex']==PrimaryAnnuitantGender)
                          &(mort_df['Age']>=PrimaryAnnuitantAge)
                          &(mort_df['Age']<BenefitCommencementAge)]
    Ptcp_PostRetMort_df = mort_df[(mort_df['MortalityTableName'] == PostCommencementMortality)
                          &(mort_df['Sex']==PrimaryAnnuitantGender)
                          &(mort_df['Age']>=BenefitCommencementAge)
                          &(mort_df['Age']<=120)] #TODO reconsider hardcode of max age

    ptcp_mort_df = pd.concat([Ptcp_PreRetMort_df, Ptcp_PostRetMort_df]).rename(columns={'Age':'ptcp_age', 'Qx':'PriorQx'}) #renaming Qx in preparation for the offset on next line
    ptcp_mort_df['ptcp_age'] = ptcp_mort_df['ptcp_age'] + 1 #note 1 year offset so merge gets ages on the same row

    return ptcp_mort_df

ptcp_mort_df = PrepMortality(cwd + '/Annuity_Factor_Calculator/MortTables/MortTables.parquet'
                        , UserInputs_dict['MortalityBeforeBCA']
                        , UserInputs_dict['MortalityAfterBCA']
                        , UserInputs_dict['PrimaryAnnuitantGender']
                        , UserInputs_dict['PrimaryAnnuitantAge']
                        , UserInputs_dict['BenefitCommencementAge']
                        )


def InitializePVFCalc(PrimaryAnnuitantAge):
    calc_df = pd.DataFrame({'Time':np.arange(121)}) #TODO can just pass in PA Age, Beneficiary Age, and BCA, and calc the # of year to initialize
    calc_df['ptcp_age'] = calc_df['Time'] + PrimaryAnnuitantAge
    calc_df = calc_df[calc_df['ptcp_age']<=120]#TODO reconsider hardcode. Also this will be different for J&S annuity
    return calc_df

#Initialize Calc df
calc_df = InitializePVFCalc(UserInputs_dict['PrimaryAnnuitantAge'])

def calc_nPx(calc_df, mort_df, PrimaryAnnuitantAge):
    calc_df = calc_df.merge(mort_df, how = 'left', on = ['ptcp_age'])
    calc_df['PriorPx'] = 1 - calc_df['PriorQx']
    calc_df['PriorPx'] = calc_df['PriorPx'].where(calc_df['ptcp_age']!=PrimaryAnnuitantAge, 1) #necessarily, prior Px to current age is 1 because the ptcp has survived to their current age
    calc_df['nPx'] = calc_df['PriorPx'].cumprod()

    return calc_df

#Add Mortality Factors and calculate nPx
calc_df = calc_nPx(calc_df, ptcp_mort_df[['ptcp_age', 'PriorQx']], UserInputs_dict['PrimaryAnnuitantAge'])

def calc_discountFactor(calc_df, DiscountRate, PaymentTiming):
    calc_df['discount_rate'] = DiscountRate #TODO eventually this will merge with an entire dataframe of discount rates (ie a Full Yield Curve, or even just expanded single segments)
    calc_df['discount_factor'] = (1+calc_df['discount_rate'])**-(PaymentTiming + calc_df['Time'])

    return calc_df

#Add discount rates and calculate discount factor
calc_df = calc_discountFactor(calc_df, UserInputs_dict['DiscountRate'], pmt_timing)

def calc_PaymentAmounts(calc_df, BenefitCommencementAge):
    calc_df['payment'] = 0
    calc_df['payment'] = calc_df['payment'].where(calc_df['ptcp_age']<BenefitCommencementAge, 1)
    
    return calc_df

#calculate payment amounts
calc_df = calc_PaymentAmounts(calc_df, UserInputs_dict['BenefitCommencementAge'])

def calculateDiscountedPV(calc_df):
    calc_df['discounted_payment'] = calc_df['payment'] * calc_df['discount_factor'] * calc_df['nPx']
    pvf = calc_df['discounted_payment'].sum()

    return pvf

#discount and sum
pvf = calculateDiscountedPV(calc_df)

print(calc_df)
print(pvf.round(4))