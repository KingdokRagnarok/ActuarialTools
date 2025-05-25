import pandas as pd
import numpy as np
import json
import os

cwd = os.getcwd()

with open(cwd+'/Annuity_Factor_Calculator/userInputs.txt', 'r') as UserInputs:
    UserInputs_dict = json.loads(UserInputs.read())

if UserInputs_dict['PaymentFrequency'] == 'ABOY':
    pmt_timing = 0

mort_df = pd.read_parquet(cwd + '/Annuity_Factor_Calculator/MortTables/MortTables.parquet'
                          , columns=['MortalityTableName', 'BaseYear', 'Sex', 'Age', 'Qx']
                          , filters = [[('MortalityTableName', '==', UserInputs_dict['MortalityBeforeBCA'])], [('MortalityTableName', '==', UserInputs_dict['MortalityAfterBCA'])]]) #TODO - Filter on Read

Ptcp_PreRetMort_df = mort_df[(mort_df['MortalityTableName'] == UserInputs_dict['MortalityBeforeBCA'])
                          &(mort_df['Sex']==UserInputs_dict['PrimaryAnnuitantGender'])
                          &(mort_df['Age']>=UserInputs_dict['PrimaryAnnuitantAge'])
                          &(mort_df['Age']<UserInputs_dict['BenefitCommencementAge'])]
Ptcp_PostRetMort_df = mort_df[(mort_df['MortalityTableName'] == UserInputs_dict['MortalityAfterBCA'])
                          &(mort_df['Sex']==UserInputs_dict['PrimaryAnnuitantGender'])
                          &(mort_df['Age']>=UserInputs_dict['BenefitCommencementAge'])
                          &(mort_df['Age']<=120)] #TODO reconsider hardcode of max age

ptcp_mort_df = pd.concat([Ptcp_PreRetMort_df, Ptcp_PostRetMort_df]).rename(columns={'Age':'ptcp_age', 'Qx':'PriorQx'}) #note 1 year offset so merge gets ages on the same row
ptcp_mort_df['ptcp_age'] = ptcp_mort_df['ptcp_age'] + 1

calc_df = pd.DataFrame({'Time':np.arange(121)})
calc_df['ptcp_age'] = calc_df['Time'] + UserInputs_dict['PrimaryAnnuitantAge']
calc_df = calc_df.merge(ptcp_mort_df[['ptcp_age', 'PriorQx']], how = 'left', on = ['ptcp_age'])
calc_df = calc_df[calc_df['ptcp_age']<=120]#TODO reconsider hardcode. Also this will be different for J&S annuity


calc_df['PriorPx'] = 1 - calc_df['PriorQx']
calc_df['PriorPx'] = calc_df['PriorPx'].where(calc_df['ptcp_age']!=UserInputs_dict['PrimaryAnnuitantAge'], 1) #necessarily, prior Px to current age is 1 because the ptcp has survived...
calc_df['nPx'] = calc_df['PriorPx'].cumprod() 

calc_df['discount_rate'] = UserInputs_dict['DiscountRate']
calc_df['discount_factor'] = (1+calc_df['discount_rate'])**-(pmt_timing + calc_df['Time'])

calc_df['payment'] = 0
calc_df['payment'] = calc_df['payment'].where(calc_df['ptcp_age']<UserInputs_dict['BenefitCommencementAge'], 1)

calc_df['discounted_payment'] = calc_df['payment'] * calc_df['discount_factor'] * calc_df['nPx']

pvf = calc_df['discounted_payment'].sum()
print(calc_df)
print(pvf.round(4))


#print(calc_df)