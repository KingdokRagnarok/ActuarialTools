import pandas as pd
import numpy as np
import datetime

pd.set_option('display.max_rows', 500)

class Annuity_Factor_Calculator:

    def CalcPVF(self, UserInputs_dict:{}, mortTablepath:str):
        pmt_timing = self.GetPaymentTiming(UserInputs_dict['PaymentFrequency'])
        mort_df = self.PrepMortality(mortTablepath
                            , UserInputs_dict['MortalityBeforeBCA']
                            , UserInputs_dict['MortalityAfterBCA']
                            , UserInputs_dict['ProjectionMethod']
                            , UserInputs_dict['PrimaryAnnuitantGender']
                            , UserInputs_dict['PrimaryAnnuitantAge']
                            , UserInputs_dict['BeneficiaryGender']
                            , UserInputs_dict['BeneficiaryAge']
                            , UserInputs_dict['BenefitCommencementAge']
                            )
        calc_df = self.InitializePVFCalc(UserInputs_dict['PrimaryAnnuitantAge'], UserInputs_dict['AnnuityType'], UserInputs_dict['BeneficiaryAge'])
        calc_df = self.calc_nPx(calc_df, mort_df, UserInputs_dict['PrimaryAnnuitantAge'], mort_type = 'PrimaryAnnuitant')
        if (UserInputs_dict['AnnuityType']=="J&S") or (UserInputs_dict['AnnuityType']=='JL'):
                calc_df = self.calc_nPx(calc_df, mort_df, UserInputs_dict['BeneficiaryAge'], mort_type = 'Beneficiary')

        calc_df = self.calc_discountFactor(calc_df, UserInputs_dict['DiscountRate'], pmt_timing)
        calc_df = self.calc_PaymentAmounts(calc_df, UserInputs_dict['BenefitCommencementAge'], UserInputs_dict['AnnualCOLA'], UserInputs_dict['AnnuityType'], UserInputs_dict['SurvivorBenefitPrct'], UserInputs_dict['CertainPeriod(years)'])
        pvf = self.calculateDiscountedPV(calc_df, UserInputs_dict['AnnuityType'], UserInputs_dict['BenefitCommencementAge'])
        return pvf

    @staticmethod
    def GetPaymentTiming(PaymentFrequency):
        match PaymentFrequency:
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

    @staticmethod
    def PrepMortality(BaseMortPath, PreCommencementMortality, PostCommencementMortality, ProjectionMethod, PrimaryAnnuitantGender, PrimaryAnnuitantAge, BeneficiaryGender, BeneficiaryAge, BenefitCommencementAge):
    
        #TODO this does not do any mort projection. I think I will rename this to "prepRawMortality" and add a function to apply mort projection down the road

        #Get Mortality Tables
        mort_df = pd.read_parquet(BaseMortPath
                            , columns=['MortalityTableName', 'BaseYear', 'Sex', 'Age', 'Qx']
                            , filters = [[('MortalityTableName', '==', PreCommencementMortality)], [('MortalityTableName', '==', PostCommencementMortality)]]) 

        #determine PA table 
        PrimaryAnnuitant_PreRetMort_df = mort_df[(mort_df['MortalityTableName'] == PreCommencementMortality)
                            &(mort_df['Sex']==PrimaryAnnuitantGender)
                            &(mort_df['Age']>=PrimaryAnnuitantAge)
                            &(mort_df['Age']<BenefitCommencementAge)]
        PrimaryAnnuitant_PostRetMort_df = mort_df[(mort_df['MortalityTableName'] == PostCommencementMortality)
                            &(mort_df['Sex']==PrimaryAnnuitantGender)
                            &(mort_df['Age']>=BenefitCommencementAge)
                            &(mort_df['Age']<=120)] #TODO reconsider hardcode of max age

        PrimaryAnnuitant_mort_df = pd.concat([PrimaryAnnuitant_PreRetMort_df, PrimaryAnnuitant_PostRetMort_df]).rename(columns={'Qx':'PriorQx'}) #renaming Qx in preparation for the offset on next line
        PrimaryAnnuitant_mort_df['Age'] = PrimaryAnnuitant_mort_df['Age'] + 1 #note 1 year offset so merge gets ages on the same row

        #determine whether Beneficiary table will be the same as PA table if age and gender is the same
        BeneficiaryTable_Is_PrimaryTable = False
        if (PrimaryAnnuitantGender == BeneficiaryGender) and (PrimaryAnnuitantAge == BeneficiaryAge):
            BeneficiaryTable_Is_PrimaryTable = True

        #BenefitCommencementBeneficiaryAge = BenefitCommencementAge - PrimaryAnnuitantAge + BeneficiaryAge 
        #TODO SOA calculator appears to be flipping beneficiary mortality tables at Primary Annuitant Commencement Age
        #That's a reasonable asusmption, but I don't necessarily agree with it. I may add my own input for Beneficiary BCA. 
        #For now, sticking with PA BCA to match SOA

        if BeneficiaryTable_Is_PrimaryTable:
            Beneficiary_mort_df = PrimaryAnnuitant_mort_df.copy()
        else:
            Beneficiary_PreRetMort_df = mort_df[(mort_df['MortalityTableName'] == PreCommencementMortality)
                                &(mort_df['Sex']==BeneficiaryGender)
                                &(mort_df['Age']>=BeneficiaryAge)
                                &(mort_df['Age']<BenefitCommencementAge)]

            Beneficiary_PostRetMort_df = mort_df[(mort_df['MortalityTableName'] == PostCommencementMortality)
                                &(mort_df['Sex']==BeneficiaryGender)
                                &(mort_df['Age']>=BenefitCommencementAge)
                                &(mort_df['Age']<=120)] #TODO reconsider hardcode of max age

            Beneficiary_mort_df = pd.concat([Beneficiary_PreRetMort_df, Beneficiary_PostRetMort_df]).rename(columns={'Qx':'PriorQx'}) #renaming Qx in preparation for the offset on next line
            Beneficiary_mort_df['Age'] = Beneficiary_mort_df['Age'] + 1 #note 1 year offset so merge gets ages on the same row
                

        PrimaryAnnuitant_mort_df['MortType'] = 'PrimaryAnnuitant'
        Beneficiary_mort_df['MortType'] = 'Beneficiary'
        mort_df = pd.concat([PrimaryAnnuitant_mort_df, Beneficiary_mort_df])

        return mort_df

    @staticmethod
    def InitializePVFCalc(PrimaryAnnuitantAge, AnnuityType, BeneficiaryAge):
        calc_df = pd.DataFrame({'Time':np.arange(121)}) #TODO can just pass in PA Age, Beneficiary Age, and BCA, and calc the # of year to initialize
        calc_df['PrimaryAnnuitant_Age'] = calc_df['Time'] + PrimaryAnnuitantAge
        calc_df['MinAge'] = calc_df['PrimaryAnnuitant_Age']

        if (AnnuityType == 'J&S') or (AnnuityType == 'JL'):
             calc_df['Beneficiary_Age'] = calc_df['Time'] + BeneficiaryAge
             calc_df['MinAge'] = np.minimum(calc_df['Beneficiary_Age'], calc_df['PrimaryAnnuitant_Age'])

        calc_df = calc_df[(calc_df['MinAge']<=120)]#TODO reconsider hardcode. 
        return calc_df

    @staticmethod
    def calc_nPx(calc_df, mort_df, Age, mort_type):

        filtered_mort_df = mort_df[mort_df['MortType']==mort_type][['PriorQx', 'Age']]
        filtered_mort_df = filtered_mort_df.rename(columns ={'PriorQx':mort_type+'_PriorQx', 'Age':mort_type+'_Age'})

        #print(calc_df[mort_type+'_Age'])
        #print(filtered_mort_df[mort_type+'_Age'])

        calc_df = calc_df.merge(filtered_mort_df, how = 'left', on = [mort_type+'_Age'])
        calc_df[mort_type+'_PriorPx'] = 1 - calc_df[mort_type+'_PriorQx']
        calc_df[mort_type+'_PriorPx'] = calc_df[mort_type+'_PriorPx'].where(calc_df[mort_type+'_Age']!=Age, 1) #necessarily, prior Px to current age is 1 because the ptcp has survived to their current age
        calc_df[mort_type+'_nPx'] = calc_df[mort_type+'_PriorPx'].cumprod()

        return calc_df

    @staticmethod
    def calc_discountFactor(calc_df, DiscountRate, PaymentTiming):
        calc_df['discount_rate'] = DiscountRate #TODO eventually this will merge with an entire dataframe of discount rates (ie a Full Yield Curve, or even just expanded single segments)
        calc_df['discount_factor'] = (1+calc_df['discount_rate'])**-(PaymentTiming + calc_df['Time'])

        return calc_df

    @staticmethod
    def calc_PaymentAmounts(calc_df, BenefitCommencementAge, COLA_pct, AnnuityType, SurvivorBenefitPct, CertainPeriod):
        
        #SLA payment - JL payment is the same
        calc_df['sla_payment'] = 0
        calc_df['sla_payment'] = calc_df['sla_payment'].where(calc_df['PrimaryAnnuitant_Age']<BenefitCommencementAge, 1)
        
        #J&S payment
        if AnnuityType == "J&S":
            calc_df['jointAndSurvivor_payment'] = calc_df['sla_payment']*SurvivorBenefitPct
        else:
            calc_df['jointAndSurvivor_payment'] = 0

        #C&L payment
        if AnnuityType == "C&L":
            calc_df['certain_payment'] = 0
            calc_df['certain_payment'] = calc_df['certain_payment'].where((calc_df['PrimaryAnnuitant_Age']<BenefitCommencementAge), 1)
            calc_df['certain_payment'] = calc_df['certain_payment'].where((calc_df['PrimaryAnnuitant_Age']<BenefitCommencementAge + CertainPeriod), 0)
            #adjust SLA payment
            calc_df['sla_payment'] = calc_df['sla_payment'].where(calc_df['PrimaryAnnuitant_Age']>=BenefitCommencementAge + CertainPeriod, 0)
        else:
            calc_df['certain_payment'] = 0
        
        #apply COLA
        calc_df['Time_From_BCA'] = np.maximum(0, calc_df['PrimaryAnnuitant_Age'] - BenefitCommencementAge)
        calc_df['COLA_Factor'] = (1+COLA_pct)**(calc_df['Time_From_BCA'])
        calc_df['sla_payment'] = calc_df['sla_payment'] * calc_df['COLA_Factor']
        calc_df['jointAndSurvivor_payment'] = calc_df['jointAndSurvivor_payment'] * calc_df['COLA_Factor']
        calc_df['certain_payment'] = calc_df['certain_payment'] * calc_df['COLA_Factor']
        
        return calc_df

    @staticmethod
    def calculateDiscountedPV(calc_df, AnnuityType, BenefitCommencementAge):
        match AnnuityType:
            case "SLA":
                 calc_df['discounted_payment'] = calc_df['sla_payment'] * calc_df['discount_factor'] * calc_df['PrimaryAnnuitant_nPx']
            case "J&S":
                calc_df['sla_discounted_payment'] = calc_df['sla_payment'] * calc_df['discount_factor'] * calc_df['PrimaryAnnuitant_nPx']
                calc_df['jointAndSurvivor_discounted_payment'] = calc_df['jointAndSurvivor_payment'] * calc_df['discount_factor'] * calc_df['Beneficiary_nPx']*(1-calc_df['PrimaryAnnuitant_nPx'])
                calc_df['discounted_payment'] = calc_df['sla_discounted_payment'] + calc_df['jointAndSurvivor_discounted_payment']
            case "C&L":
                SurvivalToStart = calc_df[calc_df['PrimaryAnnuitant_Age']==BenefitCommencementAge]['PrimaryAnnuitant_nPx'].values[0]
                calc_df['sla_discounted_payment'] = calc_df['sla_payment'] * calc_df['discount_factor'] * calc_df['PrimaryAnnuitant_nPx']                
                calc_df['certain_discounted_payment'] = calc_df['certain_payment'] * calc_df['discount_factor']*SurvivalToStart
                calc_df['discounted_payment'] = calc_df['sla_discounted_payment'] + calc_df['certain_discounted_payment']
            case "JL":
                calc_df['discounted_payment'] = calc_df['sla_payment']* calc_df['discount_factor'] * calc_df['PrimaryAnnuitant_nPx']* calc_df['Beneficiary_nPx']

        pvf = calc_df['discounted_payment'].sum().round(4) #TODO Parametrize rounding

        calc_df.to_csv('/home/jroth/Documents/Repos/ActuarialTools/Annuity_Factor_Calculator/testFiles/'+str(datetime.datetime.now())+".csv", index=False)

        return pvf

