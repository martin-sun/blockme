# Section 69

**Chapter 69**

---

## Part IV and IV.1 Tax Payable

### Part IV Tax on Dividends

Part IV tax applies to taxable dividends received by private corporations and subject corporations. This tax prevents the deferral of tax benefits within corporate groups.

#### Taxable Dividends from Connected Corporations

When a corporation receives taxable dividends from connected corporations, Part IV tax is calculated to prevent tax deferral within the corporate group.

**Example:**
- Parent Corp receives $50,000 in taxable dividends from Subsidiary Corp
- The Part IV tax rate is 33.33% (refunded when dividends are paid to shareholders)
- Part IV tax payable: $50,000 × 33.33% = $16,665

#### Eligible Dividends from Non-Connected Corporations

For eligible dividends received from non-connected corporations, Part IV tax may also apply, though the calculation differs.

**Implementation Note:**
```javascript
// Calculate Part IV tax on taxable dividends
function calculatePartIVTax(dividendAmount, isConnectedCorporation) {
  const taxRate = isConnectedCorporation ? 0.3333 : 0.3333; // Rates may vary
  return dividendAmount * taxRate;
}
```

### Reporting Part IV Tax

Enter the calculated Part IV tax payable on line 712 of the T2 Corporation Income Tax Return.

### Part IV.1 Tax Payable

Part IV.1 tax applies to certain dividends received by corporations that are subject to the general tax reduction.

#### Calculation Requirements

To determine Part IV.1 tax payable:

1. Complete Schedule 43, "Calculation of Parts IV.1 and VI.1 Taxes"
2. Apply the appropriate tax rate to eligible dividends
3. Consider any applicable deductions or credits

**Example:**
- Corporation receives $100,000 in eligible dividends from portfolio investments
- Part IV.1 tax rate: 10.67% (subject to change)
- Part IV.1 tax payable: $100,000 × 10.67% = $10,670

### Implementation Guidance for Developers

#### Data Points Required:
- Dividend amounts received
- Connection status between corporations
- Dividend eligibility status
- Applicable tax rates (may vary by tax year)

#### Validation Rules:
- Ensure dividend amounts are positive values
- Verify connection status for proper tax rate application
- Check that Schedule 43 is completed when Part IV.1 tax applies

#### References:
- IT-269, Part IV Tax on Taxable Dividends Received by a Private Corporation or a Subject Corporation
- Income Tax Act, Subsection 129(4)
- T2 Corporation Income Tax Guide, Schedule 43 Instructions
