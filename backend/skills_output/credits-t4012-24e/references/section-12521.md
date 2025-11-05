# Section 56

**Chapter 56**

---

## Investment Tax Credits (ITC)

### Federal Qualifying Environmental Trust Tax Credit (Line 648)

Environmental trusts that meet specific criteria can claim this credit. The credit is calculated based on the trust's taxable income and is designed to encourage investment in environmental initiatives.

### Investment Tax Credit (Line 652)

#### Available-for-Use Rule
Property must be available for use before claiming ITC. The property is considered available for use when it is first used by the claimant for the purpose for which it was acquired.

**Example:** A corporation purchases manufacturing equipment in December 2023 but only begins using it in February 2024. The ITC can only be claimed in the 2024 tax year when the equipment becomes available for use.

#### Qualified Investments and Expenditures
ITC may be claimed for:
- Scientific research and experimental development (SR&ED)
- Apprenticeship job creation
- Child care spaces (eliminated for expenditures after March 21, 2017)
- Clean economy initiatives
- Conservation and energy efficiency measures

#### Qualified Activities for ITC
Activities must be directly related to the specific credit being claimed. For SR&ED, this includes experimental development, basic research, and applied research.

### Scientific Research and Experimental Development (SR&ED)

#### SR&ED Qualified Expenditure Pool
The pool includes:
- Current expenditures (salaries, materials, overhead)
- Capital expenditures (equipment used in SR&ED)
- Contract payments for SR&ED performed by others

#### SR&ED Investment Tax Credit and Refund
The refundable portion varies by business type:
- CCPCs: Up to 35% refundable on first $3 million of expenditures
- Other corporations: Generally 15% non-refundable
- Partnership expenditures: Flow-through to partners

**Implementation Note:** Developers should track the 20-year recapture period for SR&ED ITCs and implement validation for expenditure eligibility.

### Apprenticeship Job Creation Tax Credit
Corporations can claim a credit of up to 10% of eligible salaries paid to eligible apprentices, with a maximum credit of $2,000 per apprentice per year.

### Investment Tax Credit (ITC) for Child Care Spaces
**Note:** This credit is eliminated for expenditures incurred after March 21, 2017.

### Claiming Investment Tax Credits
Complete Schedule 31 (Investment Tax Credit – Corporations) to claim ITCs. The schedule must be filed with your T2 Corporation Income Tax Return.

### Investment Tax Credit Refund
Refundable portions of ITCs can be claimed as refunds even if the corporation has no tax payable. Non-refundable portions can only reduce tax payable to zero.

## Part I Tax Calculations

### Base Amount of Part I Tax (Line 550)

The basic rate of Part I tax is 38% of taxable income. Calculate this by multiplying the taxable income from line 360 by 0.38.

**Formula:** Base Part I Tax = Taxable Income (line 360) × 38%

### Additional Tax on Personal Services Business Income (Line 560)

A corporation must add 5% of its taxable income from a personal services business to its Part I tax payable.

**Formula:** Additional Tax = Personal Services Business Income × 5%

### Additional Tax on Banks and Life Insurers (Line 565)

For tax years ending after April 7, 2022, an additional 1.5% tax applies to taxable income for members of bank and life insurer groups.

**Key Points:**
- $100 million taxable income exemption can be allocated among group members
- For tax years including April 7, 2022, the tax is prorated based on days after that date
- Complete Schedule 68 to calculate this additional tax

### Labour Requirements Addition to Tax (Line 580)

For clean economy ITCs (excluding clean technology manufacturing ITC), non-compliance with labour requirements triggers additional tax.

#### Prevailing Wage Requirements
- Penalty: $20 per day per covered worker not paid prevailing wage (2023 rate, inflation-adjusted annually)
- Top-up requirement: Difference between required and actual wages plus interest
- Failure to pay top-up: 120% penalty on the top-up amount

#### Apprenticeship Requirements
- Penalty: $50 multiplied by the shortfall in required apprentice hours (2023 rate, inflation-adjusted annually)
- Applies to Red Seal trade apprenticeship requirements

**Implementation Note:** Developers should create tracking mechanisms for prevailing wage compliance and apprentice hour requirements for clean economy ITC claims.

## Tax Credit Recapture

### Recapture of Investment Tax Credit (Line 602)

#### SR&ED ITC Recapture
When SR&ED property is disposed of or converted to commercial use, recapture may be required.

**Recapture Calculation:** Lesser of:
1. Original ITC earned for the property
2. Original ITC percentage × Proceeds of disposition (arm's length) or Fair market value (non-arm's length)

**Recapture Period:** 20 years from the date the ITC was claimed

#### Child Care Spaces ITC Recapture
Recapture occurs if within 60 months of acquisition:
- The child care space is no longer available
- The property is sold, leased, or converted to another use

**Recapture Amount:** Lesser of:
1. Amount reasonably considered part of original ITC
2. 25% of proceeds of disposition or fair market value (non-arm's length)

#### Clean Economy ITC Recapture
Enter recapture amounts for each clean economy ITC (except CCUS ITC) in Part 25 of Schedule 31.

## Additional Taxes and Deductions

### Refundable Tax on CCPC's Investment Income (Line 604)

An additional refundable tax of 10 2/3% applies to investment income (excluding deductible dividends) of:
- CCPCs throughout the tax year
- Substantive CCPCs at any time during the tax year (for tax years starting after April 6, 2022)

**Implementation Note:** This tax is added to the NERDTOH pool and refunded when non-eligible dividends are paid to shareholders.

### Federal Tax Abatement (Line 608)

The federal tax abatement reduces Part I tax payable by 10% of taxable income earned in Canada.

**Formula:** Federal Tax Abatement = Canadian Taxable Income × 10%

**Note:** Income earned outside Canada is not eligible for this abatement.

### Manufacturing and Processing Profits Deduction (Line 616)

#### Basic MPPD
Corporations with at least 10% of gross revenue from Canadian manufacturing or processing can claim a 13% deduction on income not eligible for the small business deduction.

#### Zero-Emission Technology Manufacturing Deduction

**Reduced Tax Rates:**
| Tax Year Start | Small Business Rate | General Rate |
|---------------|-------------------|--------------|
| 2022-2031     | 4.5%              | 7.5%         |
| 2032          | 5.625%            | 9.375%       |
| 2033          | 6.75%             | 11.25%       |
| 2034          | 7.875%            | 13.125%      |
| 2035+         | 9%                | 15%          |

**Eligible Activities Include:**
- Manufacturing of energy conversion equipment (solar, wind, water, geothermal)
- Manufacturing of air-source heat pumps
- Zero-emission vehicle manufacturing and components
- Nuclear energy equipment manufacturing (for tax years starting after 2023)
- Nuclear fuel processing and recycling

**Implementation Note:** Use Schedule 27 to calculate these deductions. Small manufacturing corporations can use a simplified method, while others must use the basic labour and capital formula.
