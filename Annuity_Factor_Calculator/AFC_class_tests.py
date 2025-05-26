import json
import os

import Annuity_Factor_Calculator_class as AFC

cwd = os.getcwd()

#get data - TODO these should be passed as function args
with open(cwd+'/Annuity_Factor_Calculator/userInputs.txt', 'r') as UserInputs:
    UserInputs_dict = json.loads(UserInputs.read())

mortTablePath = cwd + '/Annuity_Factor_Calculator/MortTables/MortTables.parquet'

pvfCalc = AFC.Annuity_Factor_Calculator_class(UserInputs_dict, mortTablePath)

