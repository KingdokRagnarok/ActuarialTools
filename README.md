# ActuarialTools
Actuarial tools developed by Joseph Roth (KingdokRagnarok).

This repository is a place for me to write scripts and applications to broaden my knowledge of actuarial science, and to demonstrate my capabilities as an actuarial programmer.

At some point, I would like to develop these into tools for other actuaries to use. However, they are not at this time sufficiently developed for that purpose. If and when these tools are developed to a degree that they are useable for actuarial work, I will update this Readme to indicate such useability.

As of the current date, my objective is to replicate some of the tools on the SOA website (https://www.soa.org/resources/tables-calcs-tools/act-practice-tools-landing/). I have significant experience in developing pension-related models and applications, and I hope to learn about other actuarial areas of practice by replicating tools used in those areas. 

2025-05-25:
An initial iteration of the Annuity PVF Calculator has been added. It is in the "Annuity_Factor_Calculator" folder. The primary piece is the "Annuity_Factor_Calculator.py" file, which prints a dataframe used for calculating the Annuity PVF, and a calculated PVF.
The UtilityCode.ipynb has blocks of code for creating certain files needed for the PVF calculator: MortTables.parquet, and userInputs.txt
Long-term, I anticipate MortTables will continue to be held in a parquet file. Another one will be needed for Projection Scales, and possibly yet another for interest rate arrays if I ever get there. UserInputs.txt will probably be supplanted by directly passing inouts from a User Interface, but until then it is convenient for me to directly modify a Python Dict and save it to a .txt file.
This version can only calculate SLAs, Annual BOY payment timing, PRI 2012 EE and Retiree tables, etc. 