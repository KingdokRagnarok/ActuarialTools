'''
DISCUSSION

This is a complete overhaul of the annuity factor calculator.
In the old version, there is a single calculation path determined by the .CalcPVF(Inputs) method.
In this version, the calculator object will contain the possibility for multiple different calculation paths, depending on the inputs (TODO Example here).
When a calculation type is requested from the calculator, the calculator will determine the correct path for generating that particular calculation, and save the path and the intermediate calculations.

Thus the core of this calculator is the calculation framework that directs the calculator how to generate each method based on each set of inputs.

'''

'''
CALCULATION FRAMEWORK

DataFrame Indexed on "Time"

    PVF_scalar = SUM_overTime(DiscountedPayment_TimeSeries)
    DiscountedPayment_TimeSeries = DiscountFactor_TimeSeries * ExpectedPayment_TimeSeries

    DiscountFactor_TimeSeries = (1+DiscountSpotRate_TimeSeries)^((-1)*(Time + PaymentTimingAdjustment))
    ExpectedPayment_TimeSeries = Sum_overScenarios(ScenarioPayment_TimeSeries*ScenarioProbability_TimeSeries)

    DiscountSpotRate_TimeSeries = InputData
    PaymentTimingAdjustment = Parameter

SIMPLE SCENARIO:
Under a simple scenario, such as an simple pension annuities, the scenarios can be defined as the probabilities of survival of the Primary Annuitant and the Beneficiary.
The time series of the probabilities of each scenario are determined using basic Mortality Table mathematics plus adjustments for certain periods, and the payments under each scenario are easily defined based on the annuity type:

Example: An SLA Annuity pays 1 when the participant is alive and past commencement age, and 0 when the participant is not alive or prior to commencement Age.

However, this framework can be extended to any set of scenarios defined by probabilities of future decrements and payments corresponding to the scenarios.
For example, a deferred life insurance policy could include negative payment amounts (premium payments) for several years, then some positive payment amount once the coverage begins.
There could be several decrements, including premium lapse, withdrawal, death, and commencement.

In the interest of maximum usability, this tool will be constructed using a highly generic calculation framework, combined with subtools that will generate the ScenarioPayment and ScenarioProbability Time Series.
I am hopeful that the tool will also permit passing in "Framework Definitions" which will be framework constraints that reduce the complexity of a particular instance of the tool.
For example, the "Pension" Framework Definition might force the tool to only consider 2 lives (Primary Annuitant, Beneficiary), define the scenarios related to those two (Both alive, PA alive only, B alive only, both deceased), and predefine certain payment patterns.

A Framework Definition would also be used to match other actuarial tools. For example, a "SOA AFC" Framework Definition could be used to reduce the calculators input set to only those permitted by the SOA Calculator, and ensure matching calculation methodology (??? If SOA is willing to share???).

The beginnings of the more complex framework might look like:

    ScenarioPayment_TimeSeries ~ [Derived from the scenario definition]
    ScenarioProbability_TimeSeries = SurvivalToBeginningOfPeriod_TimeSeries * ScenarioProbabilityWithinPeriod_TimeSeries * DecrementTimingAdjustment

    SurvivalToBeginningOfPeriod_TimeSeries ~ [Derived from the scenario definition]
    ScenarioProbabilityWithinPeriod_TimeSeries ~ [Derived from the scenario definition]
    DecrementTimingAdjustment = Parameter

Thus, subtools would be needed for defining Survival probabilities, event probabilities, and Payment time series. 
TODO - outline frameworks for those subtools
'''

'''
FINGERPRINTING

Present Value Factors are deterministic. A given set of inputs leads to precisely one output. 
Therefore, each set of inputs can be "hashed" into a single fingerprint that uniquely defines the Present Value Factor. Any calculator in the world should calculate exactly the same PVF given the same inputs.
This has obvious auditability uses, but can also be used to improve tool performance (at least in theory). 
When calculating many PVFs or complex PVFs, outputs and intermediate results (ie subtool results which have the same deterministic properties) can be stored with their fingerprints.
Then, when the same output or intermediate result is needed multiple times, a cached version can be accessed rather than recalculating.
I believe the fingerprinting is valuable to add due to the auditability, but I will conceed that I am not sure that it will actually improve performance.


I also recognize that there are minute calculation differences (such as rounding) in different tools. It may be necessary to define both a "Calculation Inputs" fingerprint and a "calculation methodologies" fingerprint.
The Calculation Inputs Fingerprint would be essential, while the calculation methodologies would be optional, since it would be assumed that the difference between two calculation methodologies would be de minimis.
Someone who is better at pure math than me might be able to figure out how large of a difference is possible based on differences in calculation methodology.

'''


'''
CHECKING

TODO - each output step can be converted to a tab in excel. 

'''


