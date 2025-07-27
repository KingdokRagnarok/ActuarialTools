import pandas as pd
import numpy as np
import datetime
import os

pd.set_option('display.max_rows', 500)

class Annuity_Factor_Calculator:
    mortTablePath = os.getcwd() + '/Annuity_Factor_Calculator/MortTables/MortTables.parquet'
    mortInfoPath = os.getcwd() + '/Annuity_Factor_Calculator/MortTables/MortTableInfo.parquet'
    ProjScalePath = os.getcwd() + '/Annuity_Factor_Calculator/ProjectionScales'

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
    def filterBaseMortality(base_mort_df, Age, BCA, Gender, MortalityBeforeBCA, MortalityAfterBCA, MaxProjectionAge, setbackYears):

            PreRetMort_df = base_mort_df[(base_mort_df['MortalityTableName'] == MortalityBeforeBCA)
                            &(base_mort_df['Sex']==Gender)
                            &(base_mort_df['Age']>=Age)
                            &(base_mort_df['Age']<BCA + setbackYears)
                            ]
            
            PostRetMort_df = base_mort_df[(base_mort_df['MortalityTableName'] == MortalityAfterBCA)
                            &(base_mort_df['Sex']==Gender)
                            &(base_mort_df['Age']>=BCA + setbackYears)
                            &(base_mort_df['Age']<=MaxProjectionAge)] 
            

            BaseMort_df = pd.concat([PreRetMort_df, PostRetMort_df])
            
            return BaseMort_df

    def initializeMortDF(self):
    
        #Get Mortality Tables
        base_mort_df = pd.read_parquet(self.mortTablePath
                            , columns=['MortalityTableName', 'Sex', 'Age', 'Qx']
                            , filters = [[('MortalityTableName', '==', self.MortalityBeforeBCA)], [('MortalityTableName', '==', self.MortalityAfterBCA)]]) 
        #setback/forward
        base_mort_df['Age'] = base_mort_df['Age'].where(base_mort_df['Sex']=='F', base_mort_df['Age'] + self.SetbackYearsMale )
        base_mort_df['Age'] = base_mort_df['Age'].where(base_mort_df['Sex']=='M', base_mort_df['Age'] + self.SetbackYearsFemale )

        #blend rates
        if self.BlendMortalityRates == True:
            base_mort_df = self.BlendMortality(base_mort_df)
        
        if self.PrimaryAnnuitantGender == 'M':
            SetbackYears = self.SetbackYearsMale
        elif self.PrimaryAnnuitantGender == 'F':
            SetbackYears = self.SetbackYearsFemale
        else:
            print("invalid gender for filterBaseMortality") 

        PrimaryAnnuitant_mort_df = self.filterBaseMortality(base_mort_df, self.PrimaryAnnuitantAge, self.BenefitCommencementAge, self.PrimaryAnnuitantGender, self.MortalityBeforeBCA, self.MortalityAfterBCA, self.MaxProjectionAge, SetbackYears)
        PrimaryAnnuitant_mort_df['MortType'] = 'PrimaryAnnuitant'

        if (self.AnnuityType == 'J&S' ) or (self.AnnuityType == 'JL'):
                    #determine whether Beneficiary table will be the same as PA table - if age and gender is the same
            BeneficiaryTable_Is_PrimaryTable = False
            if (self.PrimaryAnnuitantGender == self.BeneficiaryGender) and (self.PrimaryAnnuitantAge == self.BeneficiaryAge):
                BeneficiaryTable_Is_PrimaryTable = True

            if BeneficiaryTable_Is_PrimaryTable:
                Beneficiary_mort_df = PrimaryAnnuitant_mort_df.copy()
            else:
                if self.BeneficiaryGender == 'M':
                    SetbackYears = self.SetbackYearsMale
                elif self.BeneficiaryGender == 'F':
                    SetbackYears = self.SetbackYearsFemale
                else:
                    print("invalid gender for filterBaseMortality") 
                Beneficiary_mort_df = self.filterBaseMortality(base_mort_df, self.BeneficiaryAge, self.BenefitCommencementAge, self.BeneficiaryGender, self.MortalityBeforeBCA, self.MortalityAfterBCA, self.MaxProjectionAge, SetbackYears)
            
            Beneficiary_mort_df['MortType'] = 'Beneficiary'
            self.base_mort_df = pd.concat([PrimaryAnnuitant_mort_df, Beneficiary_mort_df])
        else:
            self.base_mort_df = PrimaryAnnuitant_mort_df


        

    def setMortBaseYears(self):
        mortTableInfo = pd.read_parquet(self.mortInfoPath
                            , columns=['MortalityTableName', 'BaseYear']
                            , filters = [[('MortalityTableName', '==', self.MortalityBeforeBCA)], [('MortalityTableName', '==', self.MortalityAfterBCA)]]) 
        
        self.PreBCABaseYear = mortTableInfo[mortTableInfo['MortalityTableName']==self.MortalityBeforeBCA]['BaseYear'].values[0]
        self.PostBCABaseYear = mortTableInfo[mortTableInfo['MortalityTableName']==self.MortalityAfterBCA]['BaseYear'].values[0]

    def initializeMortProjDF(self):
        
        match self.ProjectionMethod:
            case 'None':
                pass
            case 'Static':
                self.mort_proj_rates_df = pd.read_parquet(self.ProjScalePath + '/MortProjectionScale_1d.parquet'
                                    , columns=['MortScaleName', 'Gender', 'Age', 'ImprovementRate']
                                    , filters = [[('MortScaleName', '==', self.ProjectionScale)], [('MortScaleName', '==', self.ProjectionScale)]])
                self.mort_proj_rates_df = self.mort_proj_rates_df.rename(columns ={'Gender':'Sex'})
                #setback/forward
                self.mort_proj_rates_df['Age'] = self.mort_proj_rates_df['Age'].where(self.mort_proj_rates_df['Sex']=='F', self.mort_proj_rates_df['Age'] + self.SetbackYearsMale )
                self.mort_proj_rates_df['Age'] = self.mort_proj_rates_df['Age'].where(self.mort_proj_rates_df['Sex']=='M', self.mort_proj_rates_df['Age'] + self.SetbackYearsFemale )                           
            case 'Generational':
                self.mort_proj_rates_df = pd.read_parquet(self.ProjScalePath + '/MortProjectionScale_2d.parquet'
                    , columns=['MortScaleName', 'Gender', 'Age', 'ValYear', 'ImprovementRate']
                    , filters = [[('MortScaleName', '==', self.ProjectionScale)], [('MortScaleName', '==', self.ProjectionScale)]])    
                self.mort_proj_rates_df = self.mort_proj_rates_df.rename(columns ={'Gender':'Sex'})
                
                #setback/forward
                self.mort_proj_rates_df['Age'] = self.mort_proj_rates_df['Age'].where(self.mort_proj_rates_df['Sex']=='F', self.mort_proj_rates_df['Age'] + self.SetbackYearsMale )
                self.mort_proj_rates_df['Age'] = self.mort_proj_rates_df['Age'].where(self.mort_proj_rates_df['Sex']=='M', self.mort_proj_rates_df['Age'] + self.SetbackYearsFemale ) 

                #TODO for now only setting base years for generational. But really to fully match SOA calculator functionality, Static projection needs to be revised to use this as well. 
                self.setMortBaseYears()

    def initializeDiscountRatesDF(self):
        years_to_project = max(self.MaxProjectionAge - self.PrimaryAnnuitantAge, self.MaxProjectionAge - self.BeneficiaryAge)
        self.discount_rates_df = pd.DataFrame({'Discount_Year':np.arange(years_to_project)}) 
        self.discount_rates_df['spot_rate'] = self.DiscountRate

        #TODO Replace this whole thing with reading an input file whenever we get around to adding inputs

    def projectMortalityGenerational(self, Age):
        #TODO - this is projecting both genders - probably should filter to only one based on what is passed.
        #remove rows before Val Year/ Before min age
        mortProjMinYear = min(self.PreBCABaseYear, self.PostBCABaseYear) #this could get set outside this function, but later on we might have different mort for the ptcp vs beneficiary, in which case, we would want to set mort proj min year on a per-ptcp basis
        mortProjMinAge = Age
        individual_mort_proj_rates_df = self.mort_proj_rates_df[(self.mort_proj_rates_df['ValYear']>mortProjMinYear) & (self.mort_proj_rates_df['Age']>= mortProjMinAge)]

        #if more mort proj years than needed, remove those excess years. If fewer mort proj years than needed, duplicate the final row
        mortProjMaxYear = np.max(individual_mort_proj_rates_df['ValYear'])
        mortRatesMaxYear = self.MaxProjectionAge - Age + self.ValuationYear
        if mortProjMaxYear > mortRatesMaxYear:
            individual_mort_proj_rates_df = individual_mort_proj_rates_df[individual_mort_proj_rates_df['ValYear']<=mortRatesMaxYear]
        elif mortProjMaxYear < mortRatesMaxYear:
            yearsToRepeat = range(mortProjMaxYear, mortRatesMaxYear+1)
            individual_mort_proj_rates_df['Repeat'] = 0
            individual_mort_proj_rates_df['Repeat'] = individual_mort_proj_rates_df['Repeat'].where(individual_mort_proj_rates_df['ValYear']<mortProjMaxYear, 1)
            MortProjRepeats_df = pd.DataFrame({'ValYear':yearsToRepeat})
            MortProjRepeats_df['Repeat'] = 1
            individual_mort_proj_rates_df = individual_mort_proj_rates_df.merge(MortProjRepeats_df, how = 'left', on = 'Repeat')
            individual_mort_proj_rates_df['ValYear'] = individual_mort_proj_rates_df['ValYear_x'].where(individual_mort_proj_rates_df['ValYear_x']<mortProjMaxYear, individual_mort_proj_rates_df['ValYear_y'])

            individual_mort_proj_rates_df = individual_mort_proj_rates_df.drop(columns = {'Repeat', 'ValYear_x', 'ValYear_y'})

            #The year to project to is different for each age. If age X today, project age [X] Qx to [Val Year], but project age [X + 1] Qx to [Val Year + 1]
            individual_mort_proj_rates_df['MaxProjYear_thisAge'] = individual_mort_proj_rates_df['Age'] - Age + self.ValuationYear
            individual_mort_proj_rates_df = individual_mort_proj_rates_df[individual_mort_proj_rates_df['ValYear']<= individual_mort_proj_rates_df['MaxProjYear_thisAge']]

            #groupby product - return Sex, Age, Annual improvement Factor, rename the aggregated column to 'TotalMortalityImprovementFactor'
            individual_mort_proj_rates_df = individual_mort_proj_rates_df[['Sex', 'Age', 'AnnualMortalityImprovementFactor']].groupby(['Sex', 'Age']).prod().reset_index().rename(columns = {'AnnualMortalityImprovementFactor':'TotalMortalityImprovementFactor'})

            return individual_mort_proj_rates_df

    def projectMortality(self):
        match self.ProjectionMethod:
            case 'None':
                self.projectedAnnualMort_df = self.base_mort_df.copy()
            case 'Static':
                self.mort_proj_rates_df['AnnualMortalityImprovementFactor'] = 1 - self.mort_proj_rates_df['ImprovementRate']
                self.mort_proj_rates_df['TotalMortalityImprovementFactor'] = self.mort_proj_rates_df['AnnualMortalityImprovementFactor'] ** self.StaticProjectionYears
                self.projectedAnnualMort_df = self.base_mort_df.merge(self.mort_proj_rates_df[['Sex', 'Age', 'TotalMortalityImprovementFactor']], how = 'left', on = ['Sex', 'Age'])
                self.projectedAnnualMort_df['Qx'] = self.projectedAnnualMort_df['Qx'] * self.projectedAnnualMort_df['TotalMortalityImprovementFactor']
                self.projectedAnnualMort_df = self.projectedAnnualMort_df.drop(columns = {'TotalMortalityImprovementFactor'})
            case 'Generational':
                #Only if Generation Mort Proj and joint annuity - need separatate Beneficiary mort Tables
                if self.AnnuityType == 'J&S' or self.AnnuityType == 'JL':
                    self.projectedBeneficiaryAnnualMort_df = self.base_mort_df.copy()

                self.mort_proj_rates_df['AnnualMortalityImprovementFactor'] = 1 - self.mort_proj_rates_df['ImprovementRate']
                PrimaryAnnuitant_mort_proj =  self.projectMortalityGenerational(self.PrimaryAnnuitantAge)

                #join and perform mort improvement
                self.projectedAnnualMort_df = self.base_mort_df.merge(PrimaryAnnuitant_mort_proj[['Sex', 'Age', 'TotalMortalityImprovementFactor']], how = 'left', on = ['Sex', 'Age'])
                self.projectedAnnualMort_df['Qx'] = self.projectedAnnualMort_df['Qx'] * self.projectedAnnualMort_df['TotalMortalityImprovementFactor']
                self.projectedAnnualMort_df = self.projectedAnnualMort_df.drop(columns = {'TotalMortalityImprovementFactor'})                   

                if self.AnnuityType == 'J&S' or self.AnnuityType == 'JL':
                    Beneficiary_mort_proj = self.projectMortalityGenerational(self.BeneficiaryAge)
                    self.projectedBeneficiaryAnnualMort_df = self.base_mort_df.merge(Beneficiary_mort_proj[['Sex', 'Age', 'TotalMortalityImprovementFactor']], how = 'left', on = ['Sex', 'Age'])
                    self.projectedBeneficiaryAnnualMort_df['Qx'] = self.projectedBeneficiaryAnnualMort_df['Qx'] * self.projectedBeneficiaryAnnualMort_df['TotalMortalityImprovementFactor']
                    self.projectedBeneficiaryAnnualMort_df = self.projectedBeneficiaryAnnualMort_df.drop(columns = {'TotalMortalityImprovementFactor'})     


                #TODO DOWNSTREAM DIFFERENT MORT TABLES IF GENERATIONAL MORTALITY
                #if self.AnnuityType == 'J&S' or self.AnnuityType == 'JL'...repeat mort proj procedure

    def BlendMortality(self, mort_df):

        mort_df['blend_rate'] = self.BlendingMalePercentage
        mort_df['blend_rate'] = mort_df['blend_rate'].where(mort_df['Sex'] == 'M', 1-self.BlendingMalePercentage)
        mort_df['join_sex'] = mort_df['Sex'].map({'M':'F', 'F':'M'})
        other_gender_mortalities_df = mort_df[['Age', 'Sex', 'MortalityTableName', 'Qx']]
        other_gender_mortalities_df = other_gender_mortalities_df.rename(columns = {'Sex':'join_sex', 'Qx':'second_gender_Qx'})
        mort_df = mort_df.rename(columns = {'Qx':'first_gender_Qx'})
        mort_df = mort_df.merge(other_gender_mortalities_df, how = 'left', on = ['Age', 'MortalityTableName', 'join_sex'])
        mort_df['Qx'] = (mort_df['first_gender_Qx'] * mort_df['blend_rate']) + (mort_df['second_gender_Qx'] * (1 - mort_df['blend_rate']))
        mort_df = mort_df.drop(columns = {'blend_rate', 'first_gender_Qx', 'second_gender_Qx', 'join_sex'})

        return mort_df
        
    def adjustDiscountMethod(self):
        #TODO
        pass

    def calc_nPx_toBOY(self, Age, mort_type):
        #Only if Generation Mort Proj and Beneficiary mortality - need to use alternative mort table
        if (self.ProjectionMethod == 'Generational') and (mort_type == 'Beneficiary'):
            filtered_Annualmort_df = self.projectedBeneficiaryAnnualMort_df[self.projectedBeneficiaryAnnualMort_df['MortType']==mort_type][['Qx', 'Age']]
        else:
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
            if (self.ProjectionMethod == 'Generational') and (mort_type == 'Beneficiary'):
                filtered_Annualmort_df = self.projectedBeneficiaryAnnualMort_df[self.projectedBeneficiaryAnnualMort_df['MortType']==mort_type][['Qx', 'Age']]            
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

