# Section 59

**Chapter 59**

---

## Pre-production Mining Expenditure Credit

### Overview
The Pre-production Mining Expenditure Credit was a tax incentive designed to encourage investment in mining exploration and development activities. This credit is defined under **subsection 127(9)** of the Income Tax Act.

### Current Status
**IMPORTANT:** This credit has been fully discontinued.

- **Expiry Date:** December 31, 2015
- **Transitional Measures:** Expired on the same date
- **New Claims:** No longer accepted

### Carry Forward Provisions
For taxpayers with existing unused credits:

- **Carry Forward Period:** Up to 20 tax years following the year of investment
- **Eligibility:** Only unused credits that had not expired before the discontinuation date
- **Application:** Must be claimed against future tax liabilities within the carry-forward window

### Implementation Notes for Developers

```javascript
// Example validation logic for pre-production mining credit
function validatePreProductionMiningCredit(claimYear, investmentYear, hasUnusedCredits) {
  const expiryYear = 2015;
  const maxCarryForwardYears = 20;
  
  // Cannot claim new credits after expiry
  if (claimYear > expiryYear) {
    return { valid: false, reason: "Credit expired December 31, 2015" };
  }
  
  // Check carry-forward eligibility
  const yearsSinceInvestment = claimYear - investmentYear;
  if (yearsSinceInvestment > maxCarryForwardYears) {
    return { valid: false, reason: "Carry-forward period exceeded (20 years maximum)" };
  }
  
  return { valid: true };
}
```

### Example Scenario
A mining company incurred eligible pre-production expenditures in 2010 and claimed the credit annually until 2015. In 2016, they had $50,000 of unused credits remaining.

- **Action:** The company can continue to claim these unused credits until 2030 (2010 + 20 years)
- **Restriction:** No new credits can be generated for expenditures after December 31, 2015
- **Documentation:** Maintain detailed records of original expenditures and previous claims

### Related Forms and References
- **T2 Corporation Income Tax Return:** Schedule 31 (Investment Tax Credits)
- **T4012 Guide:** T2 Corporation Income Tax Guide
- **Legislative Reference:** Income Tax Act, subsection 127(9)
