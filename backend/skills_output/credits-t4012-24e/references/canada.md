# Section 83

**Chapter 83**

---

## Tax Credits Overview

This section outlines the various tax credits available to corporations under the Canadian tax system. Tax credits directly reduce the amount of tax payable, making them valuable tools for tax planning.

### Federal Tax Credits

#### Canadian Film or Video Production Tax Credit
- **Form**: T1131
- **Purpose**: Encourages Canadian film and video production
- **Implementation**: Developers should create form validation for T1131 submission
- **Example**: A corporation producing a certified Canadian film may claim 25% of qualified labour expenditures

#### Federal Qualifying Environmental Trust Tax Credit
- **Reference**: Schedule 139
- **Refund Process**: Available through Schedule 139
- **Implementation**: Track environmental trust investments separately for credit calculation
- **Example**: Corporations investing in qualifying environmental trusts can claim credits against Part I tax

#### Foreign Tax Credits
- **Business Income Tax Credit**: Schedule 21
- **Non-Business Income Tax Credit**: Schedule 21
- **Implementation**: 
  - Create separate tracking for foreign business vs. non-business income
  - Implement foreign tax credit limitation calculations
- **Example**: A corporation paying $10,000 in foreign business taxes on $50,000 of foreign business income can claim a credit up to the Canadian tax payable on that income

#### Investment Tax Credit
- **Form**: Schedule 31
- **Recapture**: Occurs when property is disposed of (Schedule 83)
- **Refund**: Available through Schedule 91 or 135
- **Implementation**: 
  - Track eligible investment expenditures by category
  - Implement recapture calculations on disposition
- **Example**: Scientific research and experimental development (SR&ED) expenditures may qualify for a 35% investment tax credit

#### Journalism Labour Tax Credit
- **Reference**: Schedule 140
- **Purpose**: Supports Canadian journalism organizations
- **Implementation**: Verify eligibility criteria and calculate qualified labour expenditures

#### Logging Tax Credit
- **Form**: Schedule 21
- **Implementation**: Track logging activities and related expenditures
- **Example**: Corporations engaged in logging operations may claim credits for qualified resource activities

#### Return of Fuel Charge Proceeds to Farmers Tax Credit
- **Form**: Schedule 63
- **Implementation**: Track eligible farming operations and fuel charge amounts
- **Example**: Farming corporations can claim a credit for fuel charges paid on farming activities

### Provincial and Territorial Tax Credits

#### General Implementation Notes
- Each province and territory maintains its own tax credit system
- Credits vary significantly by jurisdiction
- **Implementation**: Create jurisdiction-specific credit calculation modules

#### Provincial/Territorial Foreign Tax Credits
- **Reference**: Varies by province (starting at page 101)
- **Implementation**: Implement separate calculation for provincial foreign tax credit limitations
- **Example**: Ontario allows foreign tax credits calculated separately from federal credits

### Tax Reduction

#### General Tax Reduction
- **Reference**: Pages 79 and 87
- **Purpose**: Reduces overall tax liability after applying credits
- **Implementation**: 
  - Calculate tax reduction after all credits have been applied
  - Implement reduction limitation rules
- **Example**: Small businesses may qualify for additional tax reductions beyond the small business deduction

### Implementation Guidelines for Developers

#### Data Structure Requirements
```json
{
  "taxCredits": {
    "federal": {
      "filmProduction": {
        "form": "T1131",
        "rate": "percentage",
        "base": "qualifiedLabourExpenditures"
      },
      "environmentalTrust": {
        "schedule": "139",
        "type": "refundable"
      },
      "foreignTax": {
        "schedule": "21",
        "categories": ["business", "nonBusiness"]
      },
      "investment": {
        "schedule": "31",
        "recaptureSchedule": "83",
        "refundSchedule": ["91", "135"]
      }
    },
    "provincial": {
      "jurisdictionSpecific": true,
      "foreignTaxCredits": true
    }
  }
}
```

#### Calculation Sequence
1. Calculate net income for tax purposes
2. Apply deductions to determine taxable income
3. Calculate Part I tax before credits
4. Apply federal tax credits
5. Apply provincial/territorial tax credits
6. Apply tax reduction
7. Calculate final tax payable

#### Validation Requirements
- Verify eligibility criteria for each credit
- Validate supporting documentation
- Ensure credit limitations are properly applied
- Check for interactions between different credits

#### Common Integration Points
- T2 Corporation Income Tax Return
- Provincial/territorial tax schedules
- Information slips (T5013, etc.)
- Foreign tax documentation
- Investment expenditure records
