# Section 52

**Chapter 52**

---

## Aggregate Investment Income Calculation

### Overview
Aggregate investment income is a critical calculation for determining various tax credits and deductions for corporations. This represents the aggregate world source income calculated through specific additions and deductions.

### Calculation Formula
```
Aggregate Investment Income = (Eligible Capital Gains + Property Income) - Property Losses
```

### Calculation Steps

#### Step 1: Calculate Eligible Portion of Taxable Capital Gains
Add the eligible portion of taxable capital gains for the year that exceeds:
- The eligible portion of allowable capital losses for the year
- Net capital losses from previous years applied in the current year

**Implementation Note**: For developers, ensure your application tracks capital gains and losses separately, with the ability to apply previous year losses to current year gains.

**Example**: If a corporation has $10,000 in taxable capital gains, $3,000 in allowable capital losses for the year, and $2,000 in net capital losses from previous years, the amount to add would be $10,000 - ($3,000 + $2,000) = $5,000.

#### Step 2: Calculate Total Income from Property
Add total income from property, including income from a specified investment business carried on in Canada (excluding income from sources outside Canada), after deducting:
- Exempt income
- AgriInvest receipts (including Quebec amounts)
- Taxable dividends deductible after deducting related expenses
- Business income from an interest in a trust that is considered property income under paragraph 108(5)(a)

**Implementation Note**: Your application should categorize different types of property income and track deductible amounts separately for accurate calculation.

**Example**: If a corporation has $20,000 in property income, $2,000 in exempt income, $1,000 in AgriInvest receipts, and $3,000 in deductible taxable dividends, the amount to add would be $20,000 - ($2,000 + $1,000 + $3,000) = $14,000.

#### Step 3: Calculate Total Losses from Property
Deduct total losses for the year from property, including losses from a specified investment business carried on in Canada (excluding losses from sources outside Canada).

**Implementation Note**: Ensure your application can distinguish between property losses and other types of losses for accurate deduction.

**Example**: If a corporation has $5,000 in property losses for the year, this amount would be deducted from the total calculated in steps 1 and 2.

### Complete Calculation Example
Using the examples above:
```
Step 1 (Capital Gains): $5,000
Step 2 (Property Income): $14,000
Step 3 (Property Losses): $5,000

Aggregate Investment Income = ($5,000 + $14,000) - $5,000 = $14,000
```

### Reporting
Enter the calculated aggregate investment income on line 440 of the return, which should match the amount determined on line 092 of Schedule 7.

### Attribution Requirements for CCPCs
For Canadian Controlled Private Corporations (CCPCs), taxable capital gains and allowable capital losses can only be included in net investment income if they can be attributed to a period when one of the following entities held the disposed property:
- CCPC
- Investment corporation
- Mortgage investment corporation
- Mutual fund corporation

**Implementation Note**: Your application should track ownership periods for investment properties to determine eligibility for including gains/losses in aggregate investment income.

### Impact on Tax Credits
The aggregate investment income calculation directly affects:
- Small business deduction eligibility
- General rate reduction
- Various other tax credits and deductions

### Related Calculations
Part 2 of Schedule 7, Adjusted Aggregate Investment Income, is used to calculate the small business deduction for tax years starting after 2018. This calculation is detailed on page 4 of the return.
