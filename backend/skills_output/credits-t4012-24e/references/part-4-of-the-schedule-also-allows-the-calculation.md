# Section 71

**Chapter 71**

---

## Part IV Tax Reduction

When Part IV.1 tax is payable on the same dividend, a Part IV tax reduction may be claimed. The reduction amount depends on the relationship between the corporations:

### Calculation Methods:
- **Non-connected corporation**: 10% of the dividend amount
- **Connected corporation**: 30% of the Part IV tax payable

### Practical Example:
If Corporation A receives a $100,000 dividend from a non-connected corporation, the Part IV tax reduction would be $10,000 (10% of $100,000).

If Corporation A receives the same dividend from a connected corporation and the Part IV tax payable is $15,000, the Part IV tax reduction would be $4,500 (30% of $15,000).

## Part IV.1 Tax Payable

On line 716 of the T2 Corporation Income Tax Return, enter the amount of Part IV.1 tax payable calculated on line 340 of Schedule 43.

## Part VI Tax Payable

Financial institutions must complete Schedule 38, Part VI Tax on Capital of Financial Institutions, to calculate Part VI tax.

### Tax Calculation:
Part VI tax is 1.25% of the taxable capital employed in Canada that exceeds the $1 billion capital deduction for the year.

### For Related Groups:
If the corporation is a member of a related group, the capital deduction must be allocated among members using Schedule 39, Agreement Among Related Financial Institutions – Part VI Tax.

### Filing Requirements:
- File Schedule 39 with your return
- Only one associated or related corporation needs to file Schedule 39 for a calendar year
- If Schedule 39 is not on file when the CRA assesses returns, it may request one

### Financial Institutions Definition:
Financial institutions include:
- Banks
- Trust companies
- Life insurance corporations
- Certain holding corporations
- Corporations that accept deposits and lend money on real property security
- Corporations investing in mortgage or hypothec indebtedness

On line 720, enter the amount of Part VI tax payable calculated on line 890 of Schedule 38.

## Part I Tax Credit for Part VI Tax

Under subsection 190.1(3), corporations can deduct Part I tax payable for the year from Part VI tax payable. This is known as the Part I tax credit.

### Credit Carryback and Carryforward:
- Unused Part I tax credits can be carried back 3 years
- Unused Part I tax credits can be carried forward 7 years
- Use Schedule 42, Calculation of Unused Part I Tax Credit, to calculate and carry back this credit

### Practical Example:
If a financial institution has $50,000 of Part VI tax payable and $30,000 of Part I tax payable, it can claim a $30,000 Part I tax credit, reducing its Part VI tax to $20,000. If the institution only uses $20,000 of this credit, the remaining $10,000 can be carried back or forward as specified.

## Part VI.1 Tax Payable

Complete the following schedules if required:
- Schedule 43, Calculation of Parts IV.1 and VI.1 Taxes
- Schedule 45, Agreement Respecting Liability for Part VI.1 Tax

## Implementation Notes for Developers

When building tax applications for these credits:

1. **Part IV Tax Reduction Logic**:
   ```javascript
   function calculatePartIVTaxReduction(dividendAmount, isFromConnectedCorp, partIVTaxPayable) {
     if (isFromConnectedCorp) {
       return partIVTaxPayable * 0.30;
     } else {
       return dividendAmount * 0.10;
     }
   }
   ```

2. **Part VI Tax Calculation**:
   ```javascript
   function calculatePartVITax(taxableCapitalInCanada, capitalDeduction = 1000000000) {
     const excessCapital = Math.max(0, taxableCapitalInCanada - capitalDeduction);
     return excessCapital * 0.0125; // 1.25%
   }
   ```

3. **Part I Tax Credit Carryforward/Carryback**:
   ```javascript
   function calculatePartICreditCarryforward(unusedCredits, currentYear, carrybackYears = 3, carryforwardYears = 7) {
     return {
       carrybackPeriod: {
         startYear: currentYear - carrybackYears,
         endYear: currentYear - 1
       },
       carryforwardPeriod: {
         startYear: currentYear + 1,
         endYear: currentYear + carryforwardYears
       },
       availableCredits: unusedCredits
     };
   }
   ```

4. **Required Schedules Mapping**:
   - Part IV.1 Tax: Schedule 43 (line 340)
   - Part VI Tax: Schedule 38 (line 890)
   - Part I Tax Credit: Schedule 42
   - Related Group Allocation: Schedule 39
   - Part VI.1 Tax: Schedule 43 and Schedule 45

5. **Validation Rules**:
   - Verify corporation type before applying Part VI tax
   - Check for related group membership to determine if Schedule 39 is required
   - Ensure Part IV tax reduction only applies when Part IV.1 tax is payable on the same dividend

## References
- Sections 187.1 to 187.6
- Subsections 186(1.1) and 191.2(1)
- Sections 190, 190.1, and 190.11 to 190.15
