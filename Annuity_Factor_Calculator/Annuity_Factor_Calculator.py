import pandas as pd
import numpy as np
import datetime
import os

pd.set_option('display.max_rows', 500)

class Annuity_Factor_Calculator:
    #mortTablePath = '/home/jroth/Documents/Repos/ActuarialTools/Annuity_Factor_Calculator/MortTables/MortTables.parquet' #TODO parametrize with installation
    mortTablePath = os.getcwd() + '/Annuity_Factor_Calculator/MortTables/MortTables.parquet' #TODO parametrize with installation

    MaxProjectionAge = 120
    intermediateRoundingDigits = 6
    finalRoundingDigits = 4

    def __init__(self, UserInputs_dict:{}):
        self.__dict__.update(UserInputs_dict)
        self.SetPaymentFrequency()
        self.initializeCalcDF()
        self.initializeMortDF()
        self.initializeMortProjDF()
        self.initializeDiscountRatesDF()
        

    def SetPaymentFrequency(self):
        match self.PaymentFrequency:
            case 'ABOY':
                self.pmt_timing_within_period = 0
                self.periods_per_year  = 1
            case 'AEOY':
                self.pmt_timing_within_period = 1
                self.periods_per_year  = 1
            case 'MBOM':
                self.pmt_timing_within_period = 0
                self.periods_per_year  = 12
            case 'MEOM':
                self.pmt_timing_within_period = 1
                self.periods_per_year  = 12
            case 'MAPPX':
                self.pmt_timing_within_period = 0 #TODO - considering whether this should be 11/24???
                self.periods_per_year  = 1
            case _:
                print("INVALID INPUT")

    def initializeCalcDF(self):
        years_to_project = max(self.MaxProjectionAge - self.PrimaryAnnuitantAge, self.MaxProjectionAge - self.BeneficiaryAge)
        periods_to_project = years_to_project * self.periods_per_year
        self.pvf_calc_df = pd.DataFrame({'Time_Period_Begin':np.arange(periods_to_project)})
        self.pvf_calc_df['Year'] = self.pvf_calc_df['Time_Period_Begin'] //self.periods_per_year
        self.pvf_calc_df['period_in_year'] = self.pvf_calc_df['Time_Period_Begin'].mod(self.periods_per_year)


    @staticmethod
    def filterBaseMortality(base_mort_df, Age, BCA, Gender, MortalityBeforeBCA, MortalityAfterBCA, MaxProjectionAge):
            PreRetMort_df = base_mort_df[(base_mort_df['MortalityTableName'] == MortalityBeforeBCA)
                            &(base_mort_df['Sex']==Gender)
                            &(base_mort_df['Age']>=Age)
                            &(base_mort_df['Age']<BCA)]
            
            PostRetMort_df = base_mort_df[(base_mort_df['MortalityTableName'] == MortalityAfterBCA)
                            &(base_mort_df['Sex']==Gender)
                            &(base_mort_df['Age']>=BCA)
                            &(base_mort_df['Age']<=MaxProjectionAge)] #TODO reconsider hardcode of max age
            

            BaseMort_df = pd.concat([PreRetMort_df, PostRetMort_df])
            
            return BaseMort_df

    def initializeMortDF(self):
    
        #Get Mortality Tables
        base_mort_df = pd.read_parquet(self.mortTablePath
                            , columns=['MortalityTableName', 'BaseYear', 'Sex', 'Age', 'Qx']
                            , filters = [[('MortalityTableName', '==', self.MortalityBeforeBCA)], [('MortalityTableName', '==', self.MortalityAfterBCA)]]) 

        PrimaryAnnuitant_mort_df = self.filterBaseMortality(base_mort_df, self.PrimaryAnnuitantAge, self.BenefitCommencementAge, self.PrimaryAnnuitantGender, self.MortalityBeforeBCA, self.MortalityAfterBCA, self.MaxProjectionAge)
        PrimaryAnnuitant_mort_df['MortType'] = 'PrimaryAnnuitant'

        if (self.AnnuityType == 'J&S' ) or (self.AnnuityType == 'JL'):
                    #determine whether Beneficiary table will be the same as PA table - if age and gender is the same
            BeneficiaryTable_Is_PrimaryTable = False
            if (self.PrimaryAnnuitantGender == self.BeneficiaryGender) and (self.PrimaryAnnuitantAge == self.BeneficiaryAge):
                BeneficiaryTable_Is_PrimaryTable = True

            if BeneficiaryTable_Is_PrimaryTable:
                Beneficiary_mort_df = PrimaryAnnuitant_mort_df.copy()
            else:
                Beneficiary_mort_df = self.filterBaseMortality(base_mort_df, self.BeneficiaryAge, self.BenefitCommencementAge, self.BeneficiaryGender, self.MortalityBeforeBCA, self.MortalityAfterBCA, self.MaxProjectionAge)
            
            Beneficiary_mort_df['MortType'] = 'Beneficiary'
            self.base_mort_df = pd.concat([PrimaryAnnuitant_mort_df, Beneficiary_mort_df])
        else:
            self.base_mort_df = PrimaryAnnuitant_mort_df

    def initializeMortProjDF(self):
        #TODO
        pass

    def initializeDiscountRatesDF(self):
        years_to_project = max(self.MaxProjectionAge - self.PrimaryAnnuitantAge, self.MaxProjectionAge - self.BeneficiaryAge)
        self.discount_rates_df = pd.DataFrame({'Discount_Year':np.arange(years_to_project)}) 
        self.discount_rates_df['spot_rate'] = self.DiscountRate

        #TODO Replace this whole thing with reading an input file whenever we get around to adding inputs

    def projectMortality(self):
        #TODO
        self.projectedAnnualMort_df = self.base_mort_df.copy()
        #TODO Round at the end

    def adjustDiscountMethod(self):
        #TODO
        pass

    def calc_nPx_toBOY(self, Age, mort_type):
        filtered_Annualmort_df = self.projectedAnnualMort_df[self.projectedAnnualMort_df['MortType']==mort_type][['Qx', 'Age']]
        filtered_Annualmort_df = filtered_Annualmort_df.rename(columns ={'Qx':mort_type+'_Qx_Annual_Applicable', 'Age':mort_type+'_Age_Mortality'})
        filtered_Annualmort_df[mort_type+'_Px_Annual_to_pmt'] = 1 - filtered_Annualmort_df[mort_type+'_Qx_Annual_Applicable']
        filtered_Annualmort_df[mort_type+'_nPx_toBOY'] = filtered_Annualmort_df[mort_type+'_Px_Annual_to_pmt'].cumprod()
        filtered_Annualmort_df[mort_type+'_nPx_toBOY'] = filtered_Annualmort_df[mort_type+'_nPx_toBOY'].round(self.intermediateRoundingDigits) #ROUND

        filtered_Annualmort_df['Year'] = filtered_Annualmort_df[mort_type+'_Age_Mortality'] - Age + 1
        self.pvf_calc_df = self.pvf_calc_df.merge(filtered_Annualmort_df, how = 'left', on = ['Year'])

    def calc_nPX_withinYear(self, Age, mort_type):
        
        #if BOY pmts and annual pmt timing, directly set _Qx_Period to 0. For every other scenario, a Qx within the period is needed (either monthly Qxs or pmt occurs after mortality decrement)
        if (self.pmt_timing_within_period == 0) and (self.periods_per_year ==1):
            self.pvf_calc_df[mort_type+'_Qx_Period'] = 0
        else:
            filtered_Annualmort_df = self.projectedAnnualMort_df[self.projectedAnnualMort_df['MortType']==mort_type][['Qx', 'Age']]
            filtered_Annualmort_df = filtered_Annualmort_df.rename(columns ={'Qx':mort_type+'_Qx_Period_Applicable', 'Age':mort_type+'_Age'})
            filtered_Annualmort_df[mort_type+'_Qx_Period'] = filtered_Annualmort_df[mort_type+'_Qx_Period_Applicable']/self.periods_per_year
            filtered_Annualmort_df[mort_type+'_Qx_Period'] = filtered_Annualmort_df[mort_type+'_Qx_Period'].round(self.intermediateRoundingDigits) #ROUND
            filtered_Annualmort_df['Year'] = filtered_Annualmort_df[mort_type+'_Age'] - Age #TODO this feels duplicative with calc_nPx_toBOY
            self.pvf_calc_df = self.pvf_calc_df.merge(filtered_Annualmort_df[['Year', mort_type+'_Qx_Period']], how = 'left', on = ['Year'])

        self.pvf_calc_df[mort_type+'_nPX_withinYear'] = 1 - (self.pvf_calc_df[mort_type+'_Qx_Period'] * (self.pvf_calc_df['period_in_year']+self.pmt_timing_within_period))

    def calc_nPx(self, Age, mort_type):
        self.calc_nPx_toBOY(Age, mort_type)
        self.calc_nPX_withinYear(Age, mort_type)
            
        #calc nPx
        #if self.pmt_timing_within_period == 0: # only if BO Period payments, 
        self.pvf_calc_df[mort_type+'_nPx_toBOY'] = self.pvf_calc_df[mort_type+'_nPx_toBOY'].where(self.pvf_calc_df['Time_Period_Begin']!=0, 1) #Prior Px to current age is 1 because the subject has survived to their current age
        
        self.pvf_calc_df[mort_type+'_nPx'] = self.pvf_calc_df[mort_type+'_nPx_toBOY'] * self.pvf_calc_df[mort_type+'_nPX_withinYear']

    def CalcPVF(self, testMode = False):
        self.projectMortality()
        self.adjustDiscountMethod()

        #joins
        self.calc_nPx(self.PrimaryAnnuitantAge, mort_type = 'PrimaryAnnuitant')
        if (self.AnnuityType=="J&S") or (self.AnnuityType=='JL'):
                self.calc_nPx(self.BeneficiaryAge, mort_type = 'Beneficiary')

        self.calc_discountFactor()
        self.calc_PaymentAmounts()

        pvf = self.calculateDiscountedPV()
        if testMode:
            self.pvf_calc_df.to_csv('/home/jroth/Documents/Repos/ActuarialTools/Annuity_Factor_Calculator/testFiles/'+str(datetime.datetime.now())+".csv", index=False)

        return pvf

    def calc_discountFactor(self):
        #split based on # of periods
        periods_df = pd.DataFrame({'period_in_year':list(range(self.periods_per_year))})
        periods_df['merge_column'] = 1
        self.discount_rates_df['merge_column'] = 1
        self.discount_rates_df = self.discount_rates_df.merge(periods_df, how = 'outer')
        self.discount_rates_df['Time_Period_Begin'] = self.periods_per_year * self.discount_rates_df['Discount_Year']+self.discount_rates_df['period_in_year']
        self.discount_rates_df = self.discount_rates_df.drop(columns = {'merge_column', 'period_in_year'})

        self.pvf_calc_df = self.pvf_calc_df.merge(self.discount_rates_df, how = 'left', on = 'Time_Period_Begin') 
        self.pvf_calc_df['discount_factor'] = (1+self.pvf_calc_df['spot_rate'])**-((self.pvf_calc_df['Time_Period_Begin']+self.pmt_timing_within_period)/self.periods_per_year)
        self.pvf_calc_df['discount_factor'] = self.pvf_calc_df['discount_factor'].round(self.intermediateRoundingDigits) #ROUND
    
    def calc_PaymentAmounts(self):
        self.BenefitCommencementTime_Period_Begin = (self.BenefitCommencementAge - self.PrimaryAnnuitantAge)*self.periods_per_year
        
        #SLA payment - JL payment is the same
        self.pvf_calc_df['sla_payment'] = 0
        self.pvf_calc_df['sla_payment'] = self.pvf_calc_df['sla_payment'].where(self.pvf_calc_df['Time_Period_Begin']<self.BenefitCommencementTime_Period_Begin, 1)
        self.pvf_calc_df['sla_payment'] = self.pvf_calc_df['sla_payment']/self.periods_per_year
        self.pvf_calc_df['sla_payment'] = self.pvf_calc_df['sla_payment'].round(self.intermediateRoundingDigits) #ROUND

        #J&S payment
        if self.AnnuityType == "J&S":
            self.pvf_calc_df['jointAndSurvivor_payment'] = self.pvf_calc_df['sla_payment']*self.SurvivorBenefitPrct
        else:
            self.pvf_calc_df['jointAndSurvivor_payment'] = 0

        #C&L payment
        if self.AnnuityType == "C&L":
            certainPeriodEnd_Time_Begin = self.BenefitCommencementTime_Period_Begin + self.periods_per_year*self.CertainPeriod

            self.pvf_calc_df['certain_payment'] = 0
            self.pvf_calc_df['certain_payment'] = self.pvf_calc_df['certain_payment'].where((self.pvf_calc_df['Time_Period_Begin']<self.BenefitCommencementTime_Period_Begin), 1)
            self.pvf_calc_df['certain_payment'] = self.pvf_calc_df['certain_payment'].where(self.pvf_calc_df['Time_Period_Begin']<certainPeriodEnd_Time_Begin, 0)
            self.pvf_calc_df['certain_payment'] = self.pvf_calc_df['certain_payment']/self.periods_per_year
            self.pvf_calc_df['certain_payment'] = self.pvf_calc_df['certain_payment'].round(self.intermediateRoundingDigits) #ROUND

            #adjust SLA payment
            self.pvf_calc_df['sla_payment'] = self.pvf_calc_df['sla_payment'].where(self.pvf_calc_df['Time_Period_Begin']>=certainPeriodEnd_Time_Begin, 0)
        else:
            self.pvf_calc_df['certain_payment'] = 0

        #apply COLA
        self.pvf_calc_df['Years_From_BCA'] = np.maximum(0, (self.pvf_calc_df['Time_Period_Begin'] - self.BenefitCommencementTime_Period_Begin)//self.periods_per_year)
        self.pvf_calc_df['COLA_Factor'] = (1+self.AnnualCOLA)**(self.pvf_calc_df['Years_From_BCA'])
        self.pvf_calc_df['COLA_Factor'] = self.pvf_calc_df['COLA_Factor'].round(self.intermediateRoundingDigits) #ROUND
        self.pvf_calc_df['sla_payment'] = self.pvf_calc_df['sla_payment'] * self.pvf_calc_df['COLA_Factor']
        self.pvf_calc_df['jointAndSurvivor_payment'] = self.pvf_calc_df['jointAndSurvivor_payment'] * self.pvf_calc_df['COLA_Factor']
        self.pvf_calc_df['certain_payment'] = self.pvf_calc_df['certain_payment'] * self.pvf_calc_df['COLA_Factor']

    def calculateWoolhouseInterpolation(self):
        '''
        Notes on Woolhouse Interpolation:

        The two-term woolhouse adjusment is used to convert from an annual annuity to an (n)thly annuity using the following formula
        Annuity Factor (nthly) ~= Annuity Factor (annual) - (1-n)/(2*n). For a monthly annuity, this is: Annuity Factor (nthly) ~= Annuity Factor (annual) - 11/24

        This formula does  not work directly for a deferred annuity.
        In addition, when interest rates change between years, this formula no longer works. [TODO I cannot remember why it doesn't work - I need to look into this at some point]

        However, we can use basic Life Functions to relate our target annuity to some sort of immediate whole life annuity, and use algebra to calculate the alternate adjustment.

        For example:
        [n]AnnuityFactor[x](annual) is the Annual Annuity Factor for a Whole Life annuity of a person currently age x, deferred for n years.
        [n]AnnuityFactor[x](monthly) = AnnuityFactor[x+n](monthly) * [n]EndowmentFactor[x] (this formula does not depend on frequency of payment)
        AnnuityFactor[x+n](monthly) ~= AnnuityFactor[x+n](annual) - 11/24
        [n]AnnuityFactor[x](monthly) ~= (AnnuityFactor[x+n](annual) - 11/24)*[n]EndowmentFactor[x] = [n]AnnuityFactor[x](annual) - (11/24)*[n]EndowmentFactor[x].
        
        TODO expand with more math as we add:
        Certain & Life (just applicable to the deferred annuity, I think)
        J&S (complicated math to get that endowment factor - I think we have to use the following formula: a[x AND y] + a[x OR y] = a[x] + a[y])
        JL (On the flip side of J&S, actually quite easy since nPxy = nPx * nPy TODO double check my math here)
        Full Yield Curve: for some reason, I think this will use a series of 1-year terms as: a[x|1]  = a[x] - a[x+1]*[1]E[x]
        '''

        if self.AnnuityType == 'SLA':
            woolhouseAdjustment = self.calculateSLAWoolhouse()
        else:
            print('Non-SLA Woolhouse not currently supported - returning an annual, beginning of year factor')
            woolhouseAdjustment = 0

        return woolhouseAdjustment

    def calculateSLAWoolhouse(self):
        #TODO - can vectorize across entire calc df when I add support for full yield curve
        nPx = self.pvf_calc_df[self.pvf_calc_df['Time_Period_Begin']==self.BenefitCommencementTime_Period_Begin]['PrimaryAnnuitant_nPx'].values[0]
        discountFactor = self.pvf_calc_df[self.pvf_calc_df['Time_Period_Begin']==self.BenefitCommencementTime_Period_Begin]['discount_factor'].values[0]

        return nPx * discountFactor * 11/24


    def calculateDiscountedPV(self):
        match self.AnnuityType:
            case "SLA":
                 self.pvf_calc_df['discounted_payment'] = self.pvf_calc_df['sla_payment'] * self.pvf_calc_df['discount_factor'] * self.pvf_calc_df['PrimaryAnnuitant_nPx']
            case "J&S":
                self.pvf_calc_df['sla_discounted_payment'] = self.pvf_calc_df['sla_payment'] * self.pvf_calc_df['discount_factor'] * self.pvf_calc_df['PrimaryAnnuitant_nPx']
                self.pvf_calc_df['jointAndSurvivor_discounted_payment'] = self.pvf_calc_df['jointAndSurvivor_payment'] * self.pvf_calc_df['discount_factor'] * self.pvf_calc_df['Beneficiary_nPx']*(1-self.pvf_calc_df['PrimaryAnnuitant_nPx'])
                self.pvf_calc_df['discounted_payment'] = self.pvf_calc_df['sla_discounted_payment'] + self.pvf_calc_df['jointAndSurvivor_discounted_payment']
            case "C&L":
                SurvivalToStart = self.pvf_calc_df[self.pvf_calc_df['Time_Period_Begin']==self.BenefitCommencementTime_Period_Begin]['PrimaryAnnuitant_nPx'].values[0]
                self.pvf_calc_df['sla_discounted_payment'] = self.pvf_calc_df['sla_payment'] * self.pvf_calc_df['discount_factor'] * self.pvf_calc_df['PrimaryAnnuitant_nPx']                
                self.pvf_calc_df['certain_discounted_payment'] = self.pvf_calc_df['certain_payment'] * self.pvf_calc_df['discount_factor']*SurvivalToStart
                self.pvf_calc_df['discounted_payment'] = self.pvf_calc_df['sla_discounted_payment'] + self.pvf_calc_df['certain_discounted_payment']
            case "JL":
                self.pvf_calc_df['discounted_payment'] = self.pvf_calc_df['sla_payment']* self.pvf_calc_df['discount_factor'] * self.pvf_calc_df['PrimaryAnnuitant_nPx']* self.pvf_calc_df['Beneficiary_nPx']

        pvf = self.pvf_calc_df['discounted_payment'].sum().round(self.finalRoundingDigits) #ROUND

        if self.PaymentFrequency == 'MAPPX':
            pvf = pvf - self.calculateWoolhouseInterpolation()

        return pvf



test_inputs = {
    'DiscountRate':.05 #0-1
    , 'AnnualCOLA':0 #0-1
    , 'AnnuityType':'SLA' # SLA, J&S, C&L, JL 
    , 'SurvivorBenefitPrct':0 #0-1
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

if __name__ == '__main__':
    calc = Annuity_Factor_Calculator(test_inputs)
    pvf = calc.CalcPVF()

