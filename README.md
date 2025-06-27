# ActuarialTools
Actuarial tools developed by Joseph Roth (KingdokRagnarok).

Date: 2025-06-20

## Repository Purpose:

This repository is a place for me to write scripts and applications to broaden my knowledge of actuarial science, and to demonstrate my capabilities as an actuarial programmer.

At some point, I would like to develop these into tools for other actuaries to use. However, they are not at this time sufficiently developed for that purpose. If and when these tools are developed to a degree that they are useable for actuarial work, I will update this Readme to indicate such useability.

## Projects and Tools:

My objective is to replicate some of the tools on the SOA website (https://www.soa.org/resources/tables-calcs-tools/act-practice-tools-landing/). I have significant experience in developing pension-related models and applications, and I hope to learn about other actuarial areas of practice by replicating tools used in those areas. 

Currently Available Tools:
* Annuity Factor Calculator

Planned Tools:
tbd

### Annuity Factor Calculator:

Updated Date: 2025-06-20

#### Purpose: 
A python-based annuity factor calculator which can be installed via PIP. It should, in order of development priority, (a) calculate Annuity PVFs in a method similar to other PVF Calculators, (b) include calculation checking/audit trail capabilities, and (c) have a flexible interface/API which permits advanced users to integrate it into their own applications.

#### Installation: 
I have not tested installation, so it may not work. If you wanted to install this, I would recommend:
1. Install python (I have 3.12.3)
2. Install requirement packages (I think that is pandas, numpy, and json)
3. Download the Annuity_Factor_Calculator folder.
4. To use in a python program: "import Annuity_Factor_Calculator" (I haven't tested adding the python to my python environment or executing from a file outside the folder itself. May need to read up on the import function: https://docs.python.org/3/reference/import.html. This is another reason not to use this tool yet)
5. Create the calculator as an instance of the Annuity_Factor_Calculator.Annuity_Factor_Calculator(Inputs) class. Use the Annuity_Factor_Calculator.CalcPVF() method to return a single number which is the Annuity PVF corresponding to that input set.
6. You can refer to the AFC_class_tests.py file for an example of how inputs should be formatted. You can also use one of the blocks in UtilityCode.ipynb to create an input string.

#### Features:
The following features analogous to the SOA Annuity Factor Calculator Calculator are required features:  
* Discount Rate (operational)
* Post-Retirement COLA (operational)
* Annuity Type (SLA, J&S, C&L, JL) (Operational)
* Beneficiary benefit Percent (Operational)
* Payment Frequence (Annual BOY, Annual EOY, Monthly BOM, Monthly EOM, Monthly 11/24 Approximation) (Mostly Operational, but Approximation only works for SLA and some questions remain about the Monthly Exact methods)
* Certain period (Operational)
* Primary Annuity Benefit Commencement Age (Operational)
* Primary Annuity Current Age (Operational)
* Primary Annuitant Gender (Operational)
* Beneficiary Age (Operational)
* Beneficiary gender (Operational)
* Valuation Year (applicable to Mortality Projection) (NOT operational)
* Mortality Before and After Benefit Commencement Age (operational)
* Projection Method (Generational, Static, None) (NOT operational)
* Projection Scale (NOT operational)
* Static Projection # of years to project (NOT operational)
* Blend Mortality Rates + Percentage of Blend (NOT operational)
* Setback years (each gender separate) (NOT operational)

The following features are planned additions:
* Separate Beneficiary Benefit Commencent Age (for switching mortality tables)
* Full Yield Curve
* Parallelized calculation of multiple PVFs
* Additional functions (nPx, nQx, endowment factors)
* Calculation Validation Output
* User-Defined Mortality Tables
*   Mort table validator

#### Comments:
The initial version of this tool is intended to replicate most of the capabilities of the SOA Annuity Factor Calculator (https://afc.soa.org/).
It will likely include all the features that the SOA calculator has, and it is intended to include some additional features (flexible discount rate inputs, alternate Beneficiary Mortality, and any other features I feel like adding). For now, the only output is a PVF, but I may add add some alternate outputs (nPx, nQx, discount factors, validation tools, etc). The PVF calc is contained within the Annuity_Factor_Calculator file. 

The UtilityCode.ipynb has blocks of code for creating certain files needed for the PVF calculator: MortTables.parquet, and userInputs.txt
Long-term, I anticipate MortTables will continue to be held in a parquet file. Another one will be needed for Projection Scales, and another for interest rate arrays - thought I do need to figure out how the input for that will work. The currently used inputs string will probably be enhanced by a UI for passing inputs from the user, but until then it is convenient for me to directly modify a Python Dict and save it to a .txt file.

My initital intent was to use the SOA AFC Calculator to exactly match my calculations. However, because I am not intending to exactly match the calculator in the long term, my testing process now defines a maximimum error from the SOA AFC results. I intend to use the SOA Calculator to get directionally close to the correct calculation, but to use my own actuarial knowledge to confirm the correctness of the calculations.
As of the current date, my own actuarial knowledge indicates that not all intended features of the calculator have been built, and for some of those that have been built (specifically some Payment Frequency Options) I cannot confirm why they do not match the SOA calculator. Therefore, as of the current date, I would not recommend using this tool. 
