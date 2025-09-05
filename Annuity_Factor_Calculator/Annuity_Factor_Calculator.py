import pandas as pd
import numpy as np
import datetime
import os

pd.set_option('display.max_rows', 500)
pd.set_option('future.no_silent_downcasting', True)

print("Annuity_Factor_Calculator is loaded")
print(__file__)

class MortTableGenerator:
    mortTablePath = os.getcwd() + '/Annuity_Factor_Calculator/MortTables/MortTables.parquet'
    mortInfoPath = os.getcwd() + '/Annuity_Factor_Calculator/MortTables/MortTableInfo.parquet'
    ProjScalePath = os.getcwd() + '/Annuity_Factor_Calculator/ProjectionScales'

    def CreateRawMortTable(self, MortalityTableName, StartAge, EndAge, Sex, setbackYears):
        mort_df = self.AccessMortDatabase(MortalityTableName)
        mort_df = self.filterMort(mort_df, StartAge, EndAge, Sex, setbackYears)

        mort_df = mort_df.drop(columns = {'Sex'})

        return mort_df

    def AccessMortDatabase(self, MortalityTableName):
        mort_df = pd.read_parquet(self.mortTablePath
                            , columns=['Sex', 'Age', 'Qx']
                            , filters = [('MortalityTableName', '==', MortalityTableName)])
        
        return mort_df
        
    def filterMort(self, mort_df, startAge, endAge, Sex, setbackYears):

        mort_df['Age'] = mort_df['Age'] + setbackYears

        mort_df = mort_df[(mort_df['Sex']==Sex)
                            &(mort_df['Age']>=startAge)
                            &(mort_df['Age']<endAge)
                            ]
        
        return mort_df

    @staticmethod
    def BlendMortality(mort_df_m, blend_pct_m, mort_df_f):

        blend_pct_f = 1 -blend_pct_m
        
        mort_df_m['blend_rate_1'] = blend_pct_m
        mort_df_m = mort_df_m.rename(columns = {'Qx':'Qx_1'})

        mort_df_f['blend_rate_2'] = blend_pct_f
        mort_df_f = mort_df_f.rename(columns = {'Qx':'Qx_2'})
        
        mort_df = mort_df_m.merge(mort_df_f, how = 'left', on = 'Age')
        mort_df['Qx'] = (mort_df['Qx_1'] * mort_df['blend_rate_1']) + (mort_df['Qx_2'] * (mort_df['blend_rate_2']))

        mort_df = mort_df.drop(columns = {'Qx_1', 'blend_rate_1', 'Qx_2', 'blend_rate_2'})

        return mort_df

    def AccessOneDimProjectionScale(self, mortScaleName):
        mort_proj_rates_df = pd.read_parquet(self.ProjScalePath + '/MortProjectionScale_1d.parquet'
                                    , columns=['MortScaleName', 'Gender', 'Age', 'ImprovementRate']
                                    , filters = [[('MortScaleName', '==', mortScaleName)]])
        mort_proj_rates_df = mort_proj_rates_df.rename(columns ={'Gender':'Sex'})

        #TODO - theoretically I guess you could access a 2D table as if it were 1D. If so, logic for that could go here

        return mort_proj_rates_df

    def AccessTwoDimProjectionScale(self, mortScaleName):
        mort_proj_rates_df = pd.read_parquet(self.ProjScalePath + '/MortProjectionScale_2d.parquet'
                    , columns=['MortScaleName', 'Gender', 'Age', 'ValYear', 'ImprovementRate']
                    , filters = [[('MortScaleName', '==', mortScaleName)], [('MortScaleName', '==', mortScaleName)]])    
        mort_proj_rates_df = mort_proj_rates_df.rename(columns ={'Gender':'Sex'})

        return mort_proj_rates_df

    def filterOneDimProjectionScale(self, projectionScaleDF, StartAge, EndAge, Sex, setbackYears):
        projectionScaleDF['Age'] = projectionScaleDF['Age'] + setbackYears

        projectionScaleDF = projectionScaleDF[(projectionScaleDF['Sex']==Sex)
                            &(projectionScaleDF['Age']>=StartAge)
                            &(projectionScaleDF['Age']<EndAge)
                            ]
        
        return projectionScaleDF

    def filterTwoDimProjectionScale(self, projectionScaleDF, StartAge, EndAge, Sex, setbackYears, BaseYear, EndYear):
        projectionScaleDF['Age'] = projectionScaleDF['Age'] + setbackYears

        projectionScaleDF = projectionScaleDF[(projectionScaleDF['Sex']==Sex)
                            &(projectionScaleDF['Age']>=StartAge)
                            &(projectionScaleDF['Age']<EndAge)
                            &(projectionScaleDF['ValYear']>BaseYear)
                            &(projectionScaleDF['ValYear']<=EndYear)
                            ]
        
        return projectionScaleDF

    def createRawMortProjScale(self, ProjectionMethod, ProjectionScaleName, StartAge, EndAge, Sex, setbackYears, StartValYear, numberOfYearsToProject):
        match ProjectionMethod:
            case 'None':
                mort_proj_rates = None
            case 'Static':
                mort_proj_rates = self.AccessOneDimProjectionScale(ProjectionScaleName)
                mort_proj_rates = self.filterOneDimProjectionScale(mort_proj_rates, StartAge, EndAge, Sex, setbackYears)               
            case 'Generational':
                mort_proj_rates = self.AccessTwoDimProjectionScale(ProjectionScaleName)
                mort_proj_rates = self.filterTwoDimProjectionScale(mort_proj_rates, StartAge, EndAge, Sex, setbackYears, StartValYear, StartValYear + numberOfYearsToProject)
        
        return mort_proj_rates

    @staticmethod
    def BlendOneDimMortProj(proj_df_m, blend_pct_m, proj_df_f):
        blend_pct_f = 1 -blend_pct_m
        
        proj_df_m['blend_rate_1'] = blend_pct_m
        proj_df_m = proj_df_m.rename(columns = {'ImprovementRate':'ImprovementRate_1'})

        proj_df_f['blend_rate_2'] = blend_pct_f
        proj_df_f = proj_df_f.rename(columns = {'ImprovementRate':'ImprovementRate_2'})
        
        mort_proj_rates_df = proj_df_m.merge(proj_df_f, how = 'left', on = 'Age')
        mort_proj_rates_df['ImprovementRate'] = (mort_proj_rates_df['ImprovementRate_1'] * mort_proj_rates_df['blend_rate_1']) + (mort_proj_rates_df['ImprovementRate_2'] * (mort_proj_rates_df['blend_rate_2']))

        mort_proj_rates_df = mort_proj_rates_df.drop(columns = {'ImprovementRate_1', 'blend_rate_1', 'ImprovementRate_2', 'blend_rate_2'})
        
        return mort_proj_rates_df

    @staticmethod
    def BlendTwoDimMortProj(proj_df_m, blend_pct_m, proj_df_f):

        blend_pct_f = 1 -blend_pct_m
        
        proj_df_m['blend_rate_1'] = blend_pct_m
        proj_df_m = proj_df_m.rename(columns = {'ImprovementRate':'ImprovementRate_1'})

        proj_df_f['blend_rate_2'] = blend_pct_f
        proj_df_f = proj_df_f.rename(columns = {'ImprovementRate':'ImprovementRate_2'})
        
        mort_proj_rates_df = proj_df_m.merge(proj_df_f, how = 'left', on = ['Age', 'ValYear'])
        mort_proj_rates_df['ImprovementRate'] = (mort_proj_rates_df['ImprovementRate_1'] * mort_proj_rates_df['blend_rate_1']) + (mort_proj_rates_df['ImprovementRate_2'] * (mort_proj_rates_df['blend_rate_2']))

        mort_proj_rates_df = mort_proj_rates_df.drop(columns = {'ImprovementRate_1', 'blend_rate_1', 'ImprovementRate_2', 'blend_rate_2'})
        
        return mort_proj_rates_df

    def createMortProjScale(self, ProjectionMethod, ProjectionScaleName, StartAge, EndAge, Sex, setbackYears, blend_mortality, blend_pct_m, alt_setBackYears, StartValYear, numberOfYearsToProject):
        
        mort_proj_rates = self.createRawMortProjScale(ProjectionMethod, ProjectionScaleName, StartAge, EndAge, Sex, setbackYears, StartValYear, numberOfYearsToProject)

        if blend_mortality:
            if Sex == 'M':
                alt_sex_mort_proj_rates = self.createRawMortProjScale(ProjectionMethod, ProjectionScaleName, StartAge, EndAge, 'F', alt_setBackYears, StartValYear, numberOfYearsToProject)
                mort_proj_rates = self.BlendOneDimMortProj(mort_proj_rates, blend_pct_m, alt_sex_mort_proj_rates)
            elif Sex == 'F':
                alt_sex_mort_proj_rates = self.createRawMortProjScale(ProjectionMethod, ProjectionScaleName, StartAge, EndAge, 'M', alt_setBackYears, StartValYear, numberOfYearsToProject)
                mort_proj_rates = self.BlendTwoDimMortProj(alt_sex_mort_proj_rates, blend_pct_m, mort_proj_rates)
            else:
                print('invalid sex for mortality blend - returning unblended mortality')

        return mort_proj_rates      

    def CreateUnprojectedMortTable(self, MortalityTableName, StartAge, EndAge, Sex, setbackYears, blend_mortality, blend_pct_m, alt_setBackYears):

        mort_df = self.CreateRawMortTable(MortalityTableName, StartAge, EndAge, Sex, setbackYears)

        if blend_mortality:
            if Sex == 'M':
                alt_sex_mort_df = self.CreateRawMortTable(MortalityTableName, StartAge, EndAge, 'F', alt_setBackYears)
                mort_df = self.BlendMortality(mort_df, blend_pct_m, alt_sex_mort_df)
            elif Sex == 'F':
                alt_sex_mort_df = self.CreateRawMortTable(MortalityTableName, StartAge, EndAge, 'M', alt_setBackYears)
                mort_df = self.BlendMortality(alt_sex_mort_df, blend_pct_m, mort_df)
            else:
                print('invalid sex for mortality blend - returning unblended mortality')

        return mort_df

    def CalculateOneDimMortalityImprovementFactor(self, baseMortProj_df, numberOfYearsToProject):
        baseMortProj_df['AnnualMortalityImprovementFactor'] = 1 - baseMortProj_df['ImprovementRate']
        baseMortProj_df['TotalMortalityImprovementFactor'] = baseMortProj_df['AnnualMortalityImprovementFactor'] ** numberOfYearsToProject

        return baseMortProj_df

    def CalculateTwoDimMortalityImprovementFactor(self, baseMortProj_df, EndYear, CurrentAge, ValuationYear):

        baseMortProj_df['AnnualMortalityImprovementFactor'] = 1 - baseMortProj_df['ImprovementRate']

        mortProjMaxYear = np.max(baseMortProj_df['ValYear'])
        
        if mortProjMaxYear < EndYear:
            yearsToRepeat = range(mortProjMaxYear, EndYear+1)
            baseMortProj_df['Repeat'] = 0
            baseMortProj_df['Repeat'] = baseMortProj_df['Repeat'].where(baseMortProj_df['ValYear']<mortProjMaxYear, 1)
            MortProjRepeats_df = pd.DataFrame({'ValYear':yearsToRepeat})
            MortProjRepeats_df['Repeat'] = 1
            baseMortProj_df = baseMortProj_df.merge(MortProjRepeats_df, how = 'left', on = 'Repeat')
            baseMortProj_df['ValYear'] = baseMortProj_df['ValYear_x'].where(baseMortProj_df['ValYear_x']<mortProjMaxYear, baseMortProj_df['ValYear_y'])

            baseMortProj_df = baseMortProj_df.drop(columns = {'Repeat', 'ValYear_x', 'ValYear_y'})

            #The year to project to is different for each age. If age X today, project age [X] Qx to [Val Year], but project age [X + 1] Qx to [Val Year + 1]
            baseMortProj_df['MaxProjYear_thisAge'] = baseMortProj_df['Age'] - CurrentAge + ValuationYear
            baseMortProj_df = baseMortProj_df[baseMortProj_df['ValYear']<= baseMortProj_df['MaxProjYear_thisAge']]

            #groupby product - return Sex, Age, Annual improvement Factor, rename the aggregated column to 'TotalMortalityImprovementFactor'
            baseMortProj_df = baseMortProj_df[['Age', 'AnnualMortalityImprovementFactor']].groupby(['Age']).prod().reset_index().rename(columns = {'AnnualMortalityImprovementFactor':'TotalMortalityImprovementFactor'})

            return baseMortProj_df

    @staticmethod
    def MortProj(baseMort_df, mortProj_df):
        mort_df = baseMort_df.merge(mortProj_df, how = 'left', on = 'Age')
        mort_df['Qx'] = mort_df['Qx'] * mort_df['TotalMortalityImprovementFactor']
        
        return mort_df[['Age', 'Qx']]

    def CreateMortTable(self, MortalityTableName, StartAge, EndAge, Sex, setbackYears, blend_mortality, blend_pct_m, alt_setBackYears, ProjectionMethod, ProjectionScaleName, StartValYear, numberOfYearsToProject, CurrentAge, ValuationYear):
        baseMort_df = self.CreateUnprojectedMortTable(MortalityTableName, StartAge, EndAge, Sex, setbackYears, blend_mortality, blend_pct_m, alt_setBackYears)

        match ProjectionMethod:
            case 'None':
                mort_df = baseMort_df
            case 'Static':
                baseMortProj_df = self.createMortProjScale(ProjectionMethod, ProjectionScaleName, StartAge, EndAge, Sex, setbackYears, blend_mortality, blend_pct_m, alt_setBackYears, StartValYear, numberOfYearsToProject)
                mortProj_df = self.CalculateOneDimMortalityImprovementFactor(baseMortProj_df, numberOfYearsToProject)
                mort_df = self.MortProj(baseMort_df, mortProj_df)
            case 'Generational':
                baseMortProj_df = self.createMortProjScale(ProjectionMethod, ProjectionScaleName, StartAge, EndAge, Sex, setbackYears, blend_mortality, blend_pct_m, alt_setBackYears, StartValYear, numberOfYearsToProject)
                mortProj_df = self.CalculateTwoDimMortalityImprovementFactor(baseMortProj_df, StartValYear + numberOfYearsToProject, CurrentAge, ValuationYear)
                mort_df = self.MortProj(baseMort_df, mortProj_df)
                
        return mort_df

class Annuity_Factor_Calculator:
    mortInfoPath = os.getcwd() + '/Annuity_Factor_Calculator/MortTables/MortTableInfo.parquet'
    
    MaxProjectionAge = 120
    intermediateRoundingDigits = 6
    finalRoundingDigits = 4

    def __init__(self, UserInputs_dict:{}):
        self.__dict__.update(UserInputs_dict)
        self.SetPaymentFrequency()
        self.initializeCalcDF()
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
                self.pmt_timing_within_period = 0 #Not 11/24 since it is an after-the-fact adjustment
                self.periods_per_year  = 1
            case _:
                print("INVALID INPUT")

    def initializeCalcDF(self):
        self.includeBeneficiary = (self.AnnuityType == 'J&S' or self.AnnuityType == 'JL')

        if (self.includeBeneficiary):
            years_to_project = max(self.MaxProjectionAge - self.PrimaryAnnuitantAge, self.MaxProjectionAge - self.BeneficiaryAge)
        else:
            years_to_project = self.MaxProjectionAge - self.PrimaryAnnuitantAge
        periods_to_project = years_to_project * self.periods_per_year
        self.pvf_calc_df = pd.DataFrame({'Time_Period_Begin':np.arange(periods_to_project)})
        self.pvf_calc_df['Year'] = self.pvf_calc_df['Time_Period_Begin'] //self.periods_per_year
        self.pvf_calc_df['period_in_year'] = self.pvf_calc_df['Time_Period_Begin'].mod(self.periods_per_year)

    def initializeDiscountRatesDF(self):

        if self.includeBeneficiary:
            years_to_project = max(self.MaxProjectionAge - self.PrimaryAnnuitantAge, self.MaxProjectionAge - self.BeneficiaryAge)
        else:
            years_to_project = self.MaxProjectionAge - self.PrimaryAnnuitantAge

        self.discount_rates_df = pd.DataFrame({'Discount_Year':np.arange(years_to_project)}) 
        self.discount_rates_df['spot_rate'] = self.DiscountRate
          
        #TODO Replace this whole thing with reading an input file whenever we get around to adding inputs

    def calc_nPx_toBOY(self, Age, mort_type, mort_table):

        mort_table_copy = mort_table.copy()

        mort_table_copy = mort_table_copy.rename(columns ={'Qx':mort_type+'_Qx_Annual_Applicable', 'Age':mort_type+'_Age_Mortality'})
        mort_table_copy[mort_type+'_Px_Annual_to_pmt'] = 1 - mort_table_copy[mort_type+'_Qx_Annual_Applicable']
        mort_table_copy[mort_type+'_nPx_toBOY'] = mort_table_copy[mort_type+'_Px_Annual_to_pmt'].cumprod()
        mort_table_copy[mort_type+'_nPx_toBOY'] = mort_table_copy[mort_type+'_nPx_toBOY'].round(self.intermediateRoundingDigits) #ROUND

        mort_table_copy['Year'] = mort_table_copy[mort_type+'_Age_Mortality'] - Age + 1
        self.pvf_calc_df = self.pvf_calc_df.merge(mort_table_copy, how = 'left', on = ['Year'])

    def calc_nPX_withinYear(self, Age, mort_type, mort_table):
        
        #if BOY pmts and annual pmt timing, directly set _Qx_Period to 0. For every other scenario, a Qx within the period is needed (either monthly Qxs or pmt occurs after mortality decrement)
        if (self.pmt_timing_within_period == 0) and (self.periods_per_year ==1):
            self.pvf_calc_df[mort_type+'_Qx_Period'] = 0
        else:
            mort_table_copy = mort_table.copy()

            mort_table_copy = mort_table_copy.rename(columns ={'Qx':mort_type+'_Qx_Period_Applicable', 'Age':mort_type+'_Age'})
            mort_table_copy[mort_type+'_Qx_Period'] = mort_table_copy[mort_type+'_Qx_Period_Applicable']/self.periods_per_year
            mort_table_copy[mort_type+'_Qx_Period'] = mort_table_copy[mort_type+'_Qx_Period'].round(self.intermediateRoundingDigits) #ROUND
            mort_table_copy['Year'] = mort_table_copy[mort_type+'_Age'] - Age #TODO this feels duplicative with calc_nPx_toBOY
            self.pvf_calc_df = self.pvf_calc_df.merge(mort_table_copy[['Year', mort_type+'_Qx_Period']], how = 'left', on = ['Year'])

        self.pvf_calc_df[mort_type+'_nPX_withinYear'] = 1 - (self.pvf_calc_df[mort_type+'_Qx_Period'] * (self.pvf_calc_df['period_in_year']+self.pmt_timing_within_period))

    def calc_nPx(self, Age, mort_type, mort_table):
        self.calc_nPx_toBOY(Age, mort_type, mort_table)
        self.calc_nPX_withinYear(Age, mort_type, mort_table)
            
        #calc nPx
        #if self.pmt_timing_within_period == 0: # only if BO Period payments, 
        self.pvf_calc_df[mort_type+'_nPx_toBOY'] = self.pvf_calc_df[mort_type+'_nPx_toBOY'].where(self.pvf_calc_df['Time_Period_Begin']!=0, 1) #Prior Px to current age is 1 because the subject has survived to their current age
        
        self.pvf_calc_df[mort_type+'_nPx'] = self.pvf_calc_df[mort_type+'_nPx_toBOY'] * self.pvf_calc_df[mort_type+'_nPX_withinYear']

    def GetBaseYear(self, MortalityTableName):
        mortTableInfo = pd.read_parquet(self.mortInfoPath
                            , columns=['MortalityTableName', 'BaseYear']
                            , filters = [('MortalityTableName', '==', MortalityTableName)]) 
        
        BaseYear = mortTableInfo[mortTableInfo['MortalityTableName']==MortalityTableName]['BaseYear'].values[0] #TODO assuming in index row 0??? why        

        return BaseYear

    def getPA_PreCom_Mortality(self, mortTableGenerator):
        #PA Pre-Commencement inputs:
        if self.PrimaryAnnuitantGender == 'M':
            setbackYears = self.SetbackYearsMale
            alt_setBackYears = self.SetbackYearsFemale
        elif self.PrimaryAnnuitantGender == 'F':
            setbackYears = self.SetbackYearsFemale
            alt_setBackYears = self.SetbackYearsMale            
        else:
            print("invalid Primary AnnuitantGender for Setback")

        StartValYear = self.GetBaseYear(self.MortalityBeforeBCA)

        match self.ProjectionMethod:
            case 'None':
                numberOfYearsToProject = 0
            case 'Static':
                numberOfYearsToProject = self.ValuationYear - StartValYear + self.StaticProjectionYears #matched to SOA method
            case 'Generational':
                numberOfYearsToProject = self.ValuationYear - StartValYear + self.BenefitCommencementAge - self.PrimaryAnnuitantAge


        #NOTE IF THERE IS AN AGE SETBACK, THE MORT TABLE FLIP INCLUDES THE SETBACK AGE. THIS IS A METHOD CHOICE. SHOULDN'T MORT TABLE FLIP OCCUR AT ANNUITY COMMENCEMENT? 
                
        Ptcp_PreCom_Mort = mortTableGenerator.CreateMortTable(self.MortalityBeforeBCA, self.PrimaryAnnuitantAge, self.BenefitCommencementAge + setbackYears, 
                                                              self.PrimaryAnnuitantGender, setbackYears, self.BlendMortalityRates, self.BlendingMalePercentage, alt_setBackYears, 
                                                              self.ProjectionMethod, self.ProjectionScale, StartValYear, numberOfYearsToProject, self.PrimaryAnnuitantAge, 
                                                              self.ValuationYear)

        return Ptcp_PreCom_Mort
        
    def getPA_PostCom_Mortality(self, mortTableGenerator):
        #PA Pre-Commencement inputs:
        if self.PrimaryAnnuitantGender == 'M':
            setbackYears = self.SetbackYearsMale
            alt_setBackYears = self.SetbackYearsFemale
        elif self.PrimaryAnnuitantGender == 'F':
            setbackYears = self.SetbackYearsFemale
            alt_setBackYears = self.SetbackYearsMale            
        else:
            print("invalid Primary AnnuitantGender for Setback")

        StartValYear = self.GetBaseYear(self.MortalityAfterBCA)

        match self.ProjectionMethod:
            case 'None':
                numberOfYearsToProject = 0
            case 'Static':
                numberOfYearsToProject = self.ValuationYear - StartValYear + self.StaticProjectionYears #matched to SOA calculator method
            case 'Generational':
                numberOfYearsToProject = self.ValuationYear - StartValYear + self.MaxProjectionAge - self.PrimaryAnnuitantAge
        
        Ptcp_PostCom_Mort = mortTableGenerator.CreateMortTable(self.MortalityAfterBCA, self.BenefitCommencementAge + setbackYears, self.MaxProjectionAge, 
                                                               self.PrimaryAnnuitantGender, setbackYears, self.BlendMortalityRates, self.BlendingMalePercentage, alt_setBackYears, 
                                                               self.ProjectionMethod, self.ProjectionScale, StartValYear, numberOfYearsToProject, self.PrimaryAnnuitantAge, 
                                                               self.ValuationYear) #TODO Passing PA age into here is slightly confusing - I wonder if there's a better way to unwind this for generational mort proj

        return Ptcp_PostCom_Mort

    def getBene_PreCom_Mortality(self, mortTableGenerator):
        #Bene Pre-Commencement inputs:
        if self.BeneficiaryGender == 'M':
            setbackYears = self.SetbackYearsMale
            alt_setBackYears = self.SetbackYearsFemale
        elif self.BeneficiaryGender == 'F':
            setbackYears = self.SetbackYearsFemale
            alt_setBackYears = self.SetbackYearsMale            
        else:
            print("invalid Beneficiary AnnuitantGender for Setback")

        StartValYear = self.GetBaseYear(self.MortalityBeforeBCA)

        match self.ProjectionMethod:
            case 'None':
                numberOfYearsToProject = 0
            case 'Static':
                numberOfYearsToProject = self.ValuationYear - StartValYear + self.StaticProjectionYears #matched to SOA calculator method
            case 'Generational':
                numberOfYearsToProject = self.ValuationYear - StartValYear + self.BenefitCommencementAge - self.PrimaryAnnuitantAge #I don't like this       

        Ptcp_PreCom_Mort = mortTableGenerator.CreateMortTable(self.MortalityBeforeBCA, self.BeneficiaryAge, self.BenefitCommencementAge, self.BeneficiaryGender, 
                                                              setbackYears, self.BlendMortalityRates, self.BlendingMalePercentage, alt_setBackYears, self.ProjectionMethod, self.ProjectionScale, 
                                                              StartValYear, numberOfYearsToProject, self.BeneficiaryAge, self.ValuationYear)

        return Ptcp_PreCom_Mort
        
    def getBene_PostCom_Mortality(self, mortTableGenerator):
        #Bene Pre-Commencement inputs:
        if self.BeneficiaryGender == 'M':
            setbackYears = self.SetbackYearsMale
            alt_setBackYears = self.SetbackYearsFemale
        elif self.BeneficiaryGender == 'F':
            setbackYears = self.SetbackYearsFemale
            alt_setBackYears = self.SetbackYearsMale            
        else:
            print("invalid Primary AnnuitantGender for Setback")

        StartValYear = self.GetBaseYear(self.MortalityAfterBCA)

        match self.ProjectionMethod:
            case 'None':
                numberOfYearsToProject = 0
            case 'Static':
                numberOfYearsToProject = self.ValuationYear - StartValYear + self.StaticProjectionYears #matched to SOA calculator method
            case 'Generational':
                numberOfYearsToProject = self.ValuationYear - StartValYear + self.MaxProjectionAge - self.BeneficiaryAge

        Ptcp_PostCom_Mort = mortTableGenerator.CreateMortTable(self.MortalityAfterBCA, self.BenefitCommencementAge, self.MaxProjectionAge, self.BeneficiaryGender, setbackYears, 
                                        self.BlendMortalityRates, self.BlendingMalePercentage, alt_setBackYears, self.ProjectionMethod, self.ProjectionScale, StartValYear, 
                                        numberOfYearsToProject, self.BeneficiaryAge, self.ValuationYear) 

        return Ptcp_PostCom_Mort

    def CalcPVF(self, testMode = False):
        #Get PA Mort table, and if the right annuity type, beneficiary mort table

        mortTableGenerator = MortTableGenerator()
        PA_PreCom_Mort = self.getPA_PreCom_Mortality(mortTableGenerator)
        PA_PostCom_Mort = self.getPA_PostCom_Mortality(mortTableGenerator)

        PrimaryAnnuitantMortality = pd.concat([PA_PreCom_Mort, PA_PostCom_Mort])

        if (self.AnnuityType == 'J&S') or (self.AnnuityType == 'JL'):
            Bene_PreCom_Mort = self.getBene_PreCom_Mortality(mortTableGenerator)
            Bene_PostCom_Mort = self.getBene_PostCom_Mortality(mortTableGenerator)

            BeneficiaryMortality = pd.concat([Bene_PreCom_Mort, Bene_PostCom_Mort])

        #joins
        self.calc_nPx(self.PrimaryAnnuitantAge, 'PrimaryAnnuitant', PrimaryAnnuitantMortality)
        if (self.AnnuityType=="J&S") or (self.AnnuityType=='JL'):
                self.calc_nPx(self.BeneficiaryAge, 'Beneficiary', BeneficiaryMortality)

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

