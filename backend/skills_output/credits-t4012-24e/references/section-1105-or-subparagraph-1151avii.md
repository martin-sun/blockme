# Section 48

**Chapter 48**

---

## Taxable Income Calculation (Line 360)

### Overview
Taxable income represents the portion of your income subject to Canadian income tax after applying all allowable deductions and specific additions.

### Calculation Method

To determine taxable income:

1. Start with net income for income tax purposes (line 300)
2. Subtract all deductions entered on lines 311 to 352
3. Add any applicable amounts from:
   - Section 110.5 (certain stock option benefits)
   - Subparagraph 115(1)(a)(vii) (non-resident trust income)
4. Enter the final amount on line 360

### Special Cases

#### Loss Situations
If the calculation results in a negative amount, enter "0" on line 360.

#### Loss Carrybacks
To carry back a current-year loss to a previous tax year, refer to "How to complete Schedule 4" on page 67 for detailed procedures.

### Implementation Notes for Developers

When building tax calculation functionality:

1. Ensure proper calculation sequence:
   ```javascript
   taxableIncome = netIncome - totalDeductions + section1105Additions + subparagraph115Additions;
   taxableIncome = Math.max(0, taxableIncome); // Handle losses
   ```

2. Validate input ranges for all line items (300, 311-352, 355)

3. Implement error handling for:
   - Missing required fields
   - Invalid numeric values
   - Calculation overflow scenarios

4. Store intermediate values for audit trail purposes

### Examples

#### Example 1: Standard Calculation
- Net income (line 300): $65,000
- Total deductions (lines 311-352): $8,500
- Section 110.5 additions (line 355): $0
- Taxable income (line 360): $65,000 - $8,500 + $0 = $56,500

#### Example 2: With Section 110.5 Additions
- Net income (line 300): $72,000
- Total deductions (lines 311-352): $10,000
- Section 110.5 additions (line 355): $2,000
- Taxable income (line 360): $72,000 - $10,000 + $2,000 = $64,000

#### Example 3: Loss Situation
- Net income (line 300): $45,000
- Total deductions (lines 311-352): $52,000
- Section 110.5 additions (line 355): $0
- Result: $45,000 - $52,000 + $0 = -$7,000 (loss)
- Taxable income (line 360): $0

### Additional Resources
For complete tax information, visit canada.ca/taxes
