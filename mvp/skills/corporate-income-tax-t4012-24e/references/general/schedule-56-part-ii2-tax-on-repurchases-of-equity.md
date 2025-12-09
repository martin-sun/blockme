# Schedule 56, Part II.2 Tax on repurchases of equity

**Chapter 19**

---

## Schedule 56, Part II.2 Tax on Repurchases of Equity

### Overview
Use Schedule 56, Part II.2 to calculate any Part II.2 tax payable and file it with your T2 return. A penalty applies for late filing of Schedule 56 in addition to the penalty applicable to late filing of the T2 Return.

### Filing Requirements
- Complete Schedule 56, Part II.2 if your corporation has repurchased equity
- File Schedule 56 with your T2 Corporation Income Tax Return
- Late filing penalties apply separately from T2 return penalties

### Line 705 - Part II.2 Tax Payable
Enter the amount of Part II.2 tax payable that you determined at amount G of Schedule 56.

**Example:** If your corporation repurchased shares during the tax year and calculated $5,000 of Part II.2 tax at amount G of Schedule 56, enter $5,000 on line 705 of the T2 return.

## Line 710 - Part III.1 Tax Payable

### Eligible Dividend Designation Rules
A corporation that designates dividends as eligible dividends that exceed its capacity to pay such dividends is subject to Part III.1 tax.

### Tax Calculation
The tax is equal to 20% of the excessive eligible dividend designation.

**Example:** If your corporation designates $100,000 as eligible dividends but only has $80,000 of eligible dividend capacity, the excessive amount is $20,000. The Part III.1 tax would be 20% × $20,000 = $4,000, which would be entered on line 710.

### Implementation Notes for Developers
- Validate that Schedule 56 calculations match amount G to line 705
- Implement logic to track eligible dividend capacity vs. actual designations
- Calculate Part III.1 tax as 20% of excess eligible dividend designations
- Ensure both Part II.2 and Part III.1 taxes are included in total tax payable calculations
