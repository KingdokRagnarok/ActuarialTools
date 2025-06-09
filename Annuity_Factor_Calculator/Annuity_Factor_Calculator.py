import pandas as pd
import numpy as np
import datetime

pd.set_option('display.max_rows', 500)

class Annuity_Factor_Calculator:
    mortTablePath = '/home/jroth/Documents/Repos/ActuarialTools/Annuity_Factor_Calculator/MortTables/MortTables.parquet'
    MaxProjectionYears = 121

    def __init__(self, UserInputs_dict:{}):
        self.pvf_calc_df = pd.DataFrame({'Time':np.arange(self.MaxProjectionYears)}) #This probably should initialize differently depending on time scale (ie initialize to 121*12 if monthly basis)
        self.mort_df = pd.DataFrame()
        self.__dict__.update(UserInputs_dict)


    def CalcPVF(self, testMode = False):
        pmt_timing = self.GetPaymentTiming()
        self.PrepMortality()
        self.InitializePVFCalc()
        self.calc_nPx(self.PrimaryAnnuitantAge, mort_type = 'PrimaryAnnuitant')
        if (self.AnnuityType=="J&S") or (self.AnnuityType=='JL'):
                self.calc_nPx(self.BeneficiaryAge, mort_type = 'Beneficiary')

        self.calc_discountFactor(pmt_timing)
        self.calc_PaymentAmounts()
        pvf = self.calculateDiscountedPV()
        if testMode:
            self.pvf_calc_df.to_csv('/home/jroth/Documents/Repos/ActuarialTools/Annuity_Factor_Calculator/testFiles/'+str(datetime.datetime.now())+".csv", index=False)

        return pvf

    def GetPaymentTiming(self):
        match self.PaymentFrequency:
            case 'ABOY':
                return 0
            case 'AEOY':
                return 1
            case 'MBOM':
                print("NOT BUILT YET") #TODO
                return 0
            case 'MEOM':
                print("NOT BUILT YET") #TODO
                return 0
            case 'MAPPX':
                print("NOT BUILT YET") #TODO
                return 0
            case _:
                return "INVALID INPUT"

    def PrepMortality(self):
    
        #TODO this does not do any mort projection. I think I will rename this to "prepRawMortality" and add a function to apply mort projection down the road

        #Get Mortality Tables
        mort_df = pd.read_parquet(self.mortTablePath
                            , columns=['MortalityTableName', 'BaseYear', 'Sex', 'Age', 'Qx']
                            , filters = [[('MortalityTableName', '==', self.MortalityBeforeBCA)], [('MortalityTableName', '==', self.MortalityAfterBCA)]]) 

        #determine PA table 
        PrimaryAnnuitant_PreRetMort_df = mort_df[(mort_df['MortalityTableName'] == self.MortalityBeforeBCA)
                            &(mort_df['Sex']==self.PrimaryAnnuitantGender)
                            &(mort_df['Age']>=self.PrimaryAnnuitantAge)
                            &(mort_df['Age']<self.BenefitCommencementAge)]
        PrimaryAnnuitant_PostRetMort_df = mort_df[(mort_df['MortalityTableName'] == self.MortalityAfterBCA)
                            &(mort_df['Sex']==self.PrimaryAnnuitantGender)
                            &(mort_df['Age']>=self.BenefitCommencementAge)
                            &(mort_df['Age']<=120)] #TODO reconsider hardcode of max age

        PrimaryAnnuitant_mort_df = pd.concat([PrimaryAnnuitant_PreRetMort_df, PrimaryAnnuitant_PostRetMort_df]).rename(columns={'Qx':'PriorQx'}) #renaming Qx in preparation for the offset on next line
        if self.PaymentFrequency == 'ABOY': # Adjust offset for timing depending on payment Frequency
            PrimaryAnnuitant_mort_df['Age'] = PrimaryAnnuitant_mort_df['Age'] + 1 #note 1 year offset so merge gets ages on the same row

        #determine whether Beneficiary table will be the same as PA table if age and gender is the same
        BeneficiaryTable_Is_PrimaryTable = False
        if (self.PrimaryAnnuitantGender == self.BeneficiaryGender) and (self.PrimaryAnnuitantAge == self.BeneficiaryAge):
            BeneficiaryTable_Is_PrimaryTable = True

        #BenefitCommencementBeneficiaryAge = BenefitCommencementAge - PrimaryAnnuitantAge + BeneficiaryAge 
        #TODO SOA calculator appears to be flipping beneficiary mortality tables at Primary Annuitant Commencement Age
        #That's a reasonable asusmption, but I don't necessarily agree with it. I may add my own input for Beneficiary BCA. 
        #For now, sticking with PA BCA to match SOA

        if BeneficiaryTable_Is_PrimaryTable:
            Beneficiary_mort_df = PrimaryAnnuitant_mort_df.copy()
        else:
            Beneficiary_PreRetMort_df = mort_df[(mort_df['MortalityTableName'] == self.MortalityBeforeBCA)
                                &(mort_df['Sex']==self.BeneficiaryGender)
                                &(mort_df['Age']>=self.BeneficiaryAge)
                                &(mort_df['Age']<self.BenefitCommencementAge)]

            Beneficiary_PostRetMort_df = mort_df[(mort_df['MortalityTableName'] == self.MortalityAfterBCA)
                                &(mort_df['Sex']==self.BeneficiaryGender)
                                &(mort_df['Age']>=self.BenefitCommencementAge)
                                &(mort_df['Age']<=120)] #TODO reconsider hardcode of max age

            Beneficiary_mort_df = pd.concat([Beneficiary_PreRetMort_df, Beneficiary_PostRetMort_df]).rename(columns={'Qx':'PriorQx'}) #renaming Qx in preparation for the offset on next line
            if self.PaymentFrequency == 'ABOY': # Adjust offset for timing depending on payment Frequency
                Beneficiary_mort_df['Age'] = Beneficiary_mort_df['Age'] + 1 #note 1 year offset so merge gets ages on the same row
                

        PrimaryAnnuitant_mort_df['MortType'] = 'PrimaryAnnuitant'
        Beneficiary_mort_df['MortType'] = 'Beneficiary'
        self.mort_df = pd.concat([PrimaryAnnuitant_mort_df, Beneficiary_mort_df])

    def InitializePVFCalc(self):
        self.pvf_calc_df['PrimaryAnnuitant_Age'] = self.pvf_calc_df['Time'] + self.PrimaryAnnuitantAge
        self.pvf_calc_df['MinAge'] = self.pvf_calc_df['PrimaryAnnuitant_Age']

        if (self.AnnuityType == 'J&S') or (self.AnnuityType == 'JL'):
             self.pvf_calc_df['Beneficiary_Age'] = self.pvf_calc_df['Time'] + self.BeneficiaryAge
             self.pvf_calc_df['MinAge'] = np.minimum(self.pvf_calc_df['Beneficiary_Age'], self.pvf_calc_df['PrimaryAnnuitant_Age'])

        self.pvf_calc_df = self.pvf_calc_df[(self.pvf_calc_df['MinAge']<=120)]#TODO reconsider hardcode. 

    def calc_nPx(self, Age, mort_type):

        filtered_mort_df = self.mort_df[self.mort_df['MortType']==mort_type][['PriorQx', 'Age']]
        filtered_mort_df = filtered_mort_df.rename(columns ={'PriorQx':mort_type+'_PriorQx', 'Age':mort_type+'_Age'})

        self.pvf_calc_df = self.pvf_calc_df.merge(filtered_mort_df, how = 'left', on = [mort_type+'_Age'])
        self.pvf_calc_df[mort_type+'_PriorPx'] = 1 - self.pvf_calc_df[mort_type+'_PriorQx']
        
        if self.PaymentFrequency == 'ABOY': # only if BOY payments, Prior Px to current age is 1 because the ptcp has survived to their current age
            self.pvf_calc_df[mort_type+'_PriorPx'] = self.pvf_calc_df[mort_type+'_PriorPx'].where(self.pvf_calc_df[mort_type+'_Age']!=Age, 1)
        self.pvf_calc_df[mort_type+'_nPx'] = self.pvf_calc_df[mort_type+'_PriorPx'].cumprod()

    def calc_discountFactor(self, PaymentTiming):
        self.pvf_calc_df['discount_rate'] = self.DiscountRate #TODO eventually this will merge with an entire dataframe of discount rates (ie a Full Yield Curve, or even just expanded single segments)
        self.pvf_calc_df['discount_factor'] = (1+self.pvf_calc_df['discount_rate'])**-(PaymentTiming + self.pvf_calc_df['Time'])

    def calc_PaymentAmounts(self):
        
        #SLA payment - JL payment is the same
        self.pvf_calc_df['sla_payment'] = 0
        self.pvf_calc_df['sla_payment'] = self.pvf_calc_df['sla_payment'].where(self.pvf_calc_df['PrimaryAnnuitant_Age']<self.BenefitCommencementAge, 1)
        
        #J&S payment
        if self.AnnuityType == "J&S":
            self.pvf_calc_df['jointAndSurvivor_payment'] = self.pvf_calc_df['sla_payment']*self.SurvivorBenefitPrct
        else:
            self.pvf_calc_df['jointAndSurvivor_payment'] = 0

        #C&L payment
        if self.AnnuityType == "C&L":
            self.pvf_calc_df['certain_payment'] = 0
            self.pvf_calc_df['certain_payment'] = self.pvf_calc_df['certain_payment'].where((self.pvf_calc_df['PrimaryAnnuitant_Age']<self.BenefitCommencementAge), 1)
            self.pvf_calc_df['certain_payment'] = self.pvf_calc_df['certain_payment'].where((self.pvf_calc_df['PrimaryAnnuitant_Age']<self.BenefitCommencementAge + self.CertainPeriod), 0)
            #adjust SLA payment
            self.pvf_calc_df['sla_payment'] = self.pvf_calc_df['sla_payment'].where(self.pvf_calc_df['PrimaryAnnuitant_Age']>=self.BenefitCommencementAge + self.CertainPeriod, 0)
        else:
            self.pvf_calc_df['certain_payment'] = 0

        #apply COLA
        self.pvf_calc_df['Time_From_BCA'] = np.maximum(0, self.pvf_calc_df['PrimaryAnnuitant_Age'] - self.BenefitCommencementAge)
        self.pvf_calc_df['COLA_Factor'] = (1+self.AnnualCOLA)**(self.pvf_calc_df['Time_From_BCA'])
        self.pvf_calc_df['sla_payment'] = self.pvf_calc_df['sla_payment'] * self.pvf_calc_df['COLA_Factor']
        self.pvf_calc_df['jointAndSurvivor_payment'] = self.pvf_calc_df['jointAndSurvivor_payment'] * self.pvf_calc_df['COLA_Factor']
        self.pvf_calc_df['certain_payment'] = self.pvf_calc_df['certain_payment'] * self.pvf_calc_df['COLA_Factor']
        
    def calculateDiscountedPV(self):
        match self.AnnuityType:
            case "SLA":
                 self.pvf_calc_df['discounted_payment'] = self.pvf_calc_df['sla_payment'] * self.pvf_calc_df['discount_factor'] * self.pvf_calc_df['PrimaryAnnuitant_nPx']
            case "J&S":
                self.pvf_calc_df['sla_discounted_payment'] = self.pvf_calc_df['sla_payment'] * self.pvf_calc_df['discount_factor'] * self.pvf_calc_df['PrimaryAnnuitant_nPx']
                self.pvf_calc_df['jointAndSurvivor_discounted_payment'] = self.pvf_calc_df['jointAndSurvivor_payment'] * self.pvf_calc_df['discount_factor'] * self.pvf_calc_df['Beneficiary_nPx']*(1-self.pvf_calc_df['PrimaryAnnuitant_nPx'])
                self.pvf_calc_df['discounted_payment'] = self.pvf_calc_df['sla_discounted_payment'] + self.pvf_calc_df['jointAndSurvivor_discounted_payment']
            case "C&L":
                SurvivalToStart = self.pvf_calc_df[self.pvf_calc_df['PrimaryAnnuitant_Age']==self.BenefitCommencementAge]['PrimaryAnnuitant_nPx'].values[0]
                self.pvf_calc_df['sla_discounted_payment'] = self.pvf_calc_df['sla_payment'] * self.pvf_calc_df['discount_factor'] * self.pvf_calc_df['PrimaryAnnuitant_nPx']                
                self.pvf_calc_df['certain_discounted_payment'] = self.pvf_calc_df['certain_payment'] * self.pvf_calc_df['discount_factor']*SurvivalToStart
                self.pvf_calc_df['discounted_payment'] = self.pvf_calc_df['sla_discounted_payment'] + self.pvf_calc_df['certain_discounted_payment']
            case "JL":
                self.pvf_calc_df['discounted_payment'] = self.pvf_calc_df['sla_payment']* self.pvf_calc_df['discount_factor'] * self.pvf_calc_df['PrimaryAnnuitant_nPx']* self.pvf_calc_df['Beneficiary_nPx']

        pvf = self.pvf_calc_df['discounted_payment'].sum().round(4) #TODO Parametrize rounding

        return pvf

