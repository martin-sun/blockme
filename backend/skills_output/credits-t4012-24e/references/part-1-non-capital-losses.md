# Section 37

**Chapter 37**

---

## Part 1 – Non-capital Losses

### Overview of Non-capital Losses as Tax Credits

Non-capital losses are an important tax credit mechanism that allows taxpayers to offset income in other years. When a taxpayer has more deductions than income in a tax year, they may incur a non-capital loss that can be carried back 3 years or carried forward up to 20 years to reduce taxable income in those years.

### Determination of Current Year Non-capital Loss

To determine the current-year non-capital loss, complete Part 1 as follows:

#### Step 1: Calculate Net Income (Loss) for Income Tax Purposes
- Income from all sources minus losses from business and property
- Plus or minus adjustments on Schedule 1

#### Step 2: Deduct the Following Amounts
- **Net capital losses deducted in the year**: Net capital losses from previous years used to reduce taxable capital gains included in income
- **Taxable dividends deductible**: Taxable dividends received, deductible under section 112 or 113 or subsection 138(6) (for details, see Line 320 on page 72)
- **Amount of Part VI.1 tax deductible**: Unused Part VI.1 tax deductible in the taxable income calculation
- **Amount deductible as prospector's and grubstaker's shares**: Paragraph 110(1)(d.2) – the amount deductible is the value of any shares received from a corporation on disposition of a right or a mining property, except if the amount is exempt from tax in Canada by virtue of one of Canada's tax treaties, multiplied by 1/2

#### Step 3: Calculate Subtotal
- If the result is positive, enter "0"
- If the result is negative, this amount represents your current-year non-capital loss

### Practical Examples

#### Example 1: Simple Non-capital Loss Calculation
- Net income for tax purposes: $10,000
- Net capital losses deducted: $3,000
- Taxable dividends deductible: $2,000
- Part VI.1 tax deductible: $500
- Prospector's shares deductible: $0

Calculation:
$10,000 - $3,000 - $2,000 - $500 = $4,500
Since the result is positive, the non-capital loss is $0.

#### Example 2: Non-capital Loss Result
- Net loss for tax purposes: -$5,000
- Net capital losses deducted: $0
- Taxable dividends deductible: $1,000
- Part VI.1 tax deductible: $0
- Prospector's shares deductible: $500

Calculation:
-$5,000 - $0 - $1,000 - $0 - $500 = -$6,500
Since the result is negative, the current-year non-capital loss is $6,500.

### Implementation Notes for Developers

When building tax applications:

1. **Data Structure**: Create a form that captures all required inputs for non-capital loss calculation
2. **Validation**: Ensure all monetary inputs are properly validated
3. **Calculation Logic**: Implement the step-by-step calculation process
4. **Result Handling**: Display "0" for positive results and the absolute value for negative results
5. **Carry-forward Tracking**: Implement functionality to track non-capital losses that can be carried forward to other years
6. **Reference Integration**: Include links to relevant CRA documentation (e.g., T1 Guide, Schedule 1)

### Related Forms and Schedules
- T1 General Income Tax and Benefit Return
- Schedule 1 - Federal Tax
- T1 Guide - Completing your Income Tax and Benefit Return
