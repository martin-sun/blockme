# Section 54

**Chapter 54**

---

## Dividend Refund Eligibility and Calculation

### Identifying Qualifying Taxable Dividends
To determine which dividends qualify for the dividend refund, you must complete Part 3 of Schedule 3. This calculation only includes taxable dividends that meet specific criteria under the Income Tax Act.

### Non-Qualifying Dividends
If your corporation paid dividends that don't qualify for the dividend refund, you must exclude these amounts before completing the calculation in Part 3. In such cases, complete Part 4 of Schedule 3 to identify these non-qualifying dividends.

Non-qualifying dividends include:
- Dividends paid out of the capital dividend account
- Capital gains dividends
- Dividends paid for shares that don't qualify as taxable dividends because the main purpose of acquiring the shares was to receive a dividend refund [subsection 129(1.2)]
- Taxable dividends paid to a controlling corporation that was bankrupt at any time in the year

### Connected Corporation Considerations
Complete Part 3 of Schedule 3 to identify any connected corporation that received taxable dividends qualifying for the dividend refund.

### Handling Excess Refunds
If the dividend refund exceeds the amount of Part I tax payable for the year:
1. The CRA first deducts the excess from any other taxes owed under the Income Tax Act
2. Any remaining balance is available as a refund

### Reconciliation Requirements
If the total dividends paid during the year differs from the total of taxable dividends paid for dividend refund purposes, you must complete Part 4 of Schedule 3 to reconcile these amounts.

### Practical Examples

#### Example 1: Identifying Non-Qualifying Dividends
ABC Corporation paid $50,000 in dividends during the tax year:
- $30,000 in regular taxable dividends
- $15,000 from the capital dividend account
- $5,000 as capital gains dividends

For the dividend refund calculation, only the $30,000 in regular taxable dividends would be included in Part 3. The $20,000 in non-qualifying dividends would be reported in Part 4.

#### Example 2: Excess Refund Scenario
XYZ Corporation has:
- Part I tax payable: $8,000
- Other taxes under the Income Tax Act: $2,000
- Calculated dividend refund: $12,000

The $4,000 excess ($12,000 - $8,000) would first be applied against the $2,000 in other taxes, with the remaining $2,000 available as a refund.

### Implementation Notes for Developers
When building tax applications:
1. Create separate fields for qualifying and non-qualifying dividends
2. Implement validation to ensure all dividend types are properly categorized
3. Calculate the dividend refund only on qualifying dividends
4. Apply excess refunds to other tax obligations before determining the final refund amount
5. Include reconciliation functionality when total dividends differ from qualifying dividends

### References
- Section 129
- Subsection 186(5)
- Paragraph 129(1)(a)
