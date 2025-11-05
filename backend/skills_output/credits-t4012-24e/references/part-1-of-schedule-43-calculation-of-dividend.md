# Section 72

**Chapter 72**

---

## Part 1 of Schedule 43 – Calculation of Dividend Allowance

### Overview
The dividend allowance is calculated on Part 1 of Schedule 43. This provision allows corporations to exempt a portion of dividends paid on taxable preferred shares from Part VI.1 tax liability.

### Basic Dividend Allowance
- The standard annual exemption is $500,000 of dividends paid on taxable preferred shares
- This exemption applies to dividends paid during the taxation year
- The allowance is automatically available unless reduced by previous year's dividend payments

### Reduction of Dividend Allowance
The $500,000 dividend allowance is reduced when:
- The corporation paid more than $1 million in dividends on taxable preferred shares in the previous taxation year
- The reduction is calculated proportionally based on the excess amount over $1 million

### Calculation Method
1. Determine if dividends paid on taxable preferred shares in the previous year exceeded $1 million
2. If yes, calculate the reduction amount
3. Subtract the reduction from the $500,000 basic allowance
4. The result is the allowable dividend exemption for the current year

### Practical Examples

#### Example 1: Full Dividend Allowance
ABC Corporation paid $750,000 in dividends on taxable preferred shares in the current year. In the previous year, they paid $800,000 in such dividends.

Calculation:
- Previous year dividends ($800,000) < $1 million threshold
- No reduction applies
- Full $500,000 dividend allowance available
- $750,000 - $500,000 = $250,000 subject to Part VI.1 tax

#### Example 2: Reduced Dividend Allowance
XYZ Corporation paid $600,000 in dividends on taxable preferred shares in the current year. In the previous year, they paid $1.5 million in such dividends.

Calculation:
- Previous year dividends ($1.5 million) > $1 million threshold
- Excess amount: $1.5 million - $1 million = $500,000
- Reduction amount: $500,000 × ($500,000 ÷ $1 million) = $250,000
- Reduced dividend allowance: $500,000 - $250,000 = $250,000
- $600,000 - $250,000 = $350,000 subject to Part VI.1 tax

### Implementation Considerations for Developers
When building tax applications to calculate the dividend allowance:

1. **Data Requirements**:
   - Total dividends paid on taxable preferred shares in the current year
   - Total dividends paid on taxable preferred shares in the previous year

2. **Calculation Logic**:
   ```python
   def calculate_dividend_allowance(current_year_dividends, previous_year_dividends):
       basic_allowance = 500000
       threshold = 1000000
       
       if previous_year_dividends <= threshold:
           return basic_allowance
       
       excess = previous_year_dividends - threshold
       reduction = excess * (basic_allowance / threshold)
       return max(0, basic_allowance - reduction)
   ```

3. **Validation Rules**:
   - Ensure dividend amounts are non-negative
   - Verify that only dividends on taxable preferred shares are included
   - Confirm the previous year data corresponds to the immediately preceding taxation year

4. **Output Requirements**:
   - Calculated dividend allowance amount
   - Amount of dividends subject to Part VI.1 tax
   - Reduction amount (if applicable)

### Related Forms and Schedules
- Schedule 43: Designation of Dividends Paid on Taxable Preferred Shares
- T2 Corporation Income Tax Return: Schedule 43 is filed with the T2 return
