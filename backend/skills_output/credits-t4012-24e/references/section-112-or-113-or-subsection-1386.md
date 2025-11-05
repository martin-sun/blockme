# Section 23

**Chapter 23**

---

## Tax Credits and Deductions for Corporations

### Key Tax Deduction Lines

#### Line 325 – Part VI.1 Tax Deduction
Corporations can claim a deduction for Part VI.1 tax paid on taxable capital gains. This prevents double taxation on investment income.

#### Lines 331-335 – Loss Carryforwards
Corporations may carry forward various types of losses to offset future taxable income:

- **Line 331**: Non-capital losses of previous tax years
- **Line 332**: Net capital losses of previous tax years
- **Line 333**: Restricted farm losses of previous tax years
- **Line 334**: Farm losses of previous tax years
- **Line 335**: Limited partnership losses of previous tax years

**Example**: A corporation with $50,000 in non-capital losses from 2020 can apply these losses against 2023 taxable income, subject to limitation rules.

#### Line 340 – Credit Union Allocations
Corporations that are members of central credit unions must report taxable capital gains or taxable dividends allocated from the credit union.

#### Line 350 – Prospector's and Grubstaker's Shares
Special deduction available for corporations holding prospector's or grubstaker's shares, subject to specific conditions under the Income Tax Act.

#### Line 352 – Employer Deduction for Non-Qualified Securities
Employers can claim a deduction for certain non-qualified securities provided to employees, subject to specific valuation rules.

#### Line 355 – Section 110.5 Additions
Corporations must include certain amounts under section 110.5 or subparagraph 115(1)(a)(vii) when calculating taxable income.

#### Line 360 – Taxable Income
This represents the final taxable income after all deductions and adjustments have been applied.

## Corporate Information Requirements

### Line 270 – IFRS Reporting
Corporations must indicate if they used International Financial Reporting Standards (IFRS) when preparing financial statements.

**Implementation Note**: For tax applications, include a checkbox field for IFRS compliance with validation logic that:
- Requires "Yes" for publicly accountable enterprises
- Provides documentation requirements for first-year IFRS adoption
- Links to canada.ca/international-financial-reporting-standards-ifrs

### Line 280 – Inactive Corporations
Even inactive corporations must file a T2 return. Inactive corporations without balance sheet or income statement information may not need to attach Schedules 100, 125, and 141.

### Lines 284-289 – Business Activities
Corporations must specify principal products/services and approximate revenue percentages.

**Technical Implementation**:
- Require NAICS code selection for electronic filing
- Validate that percentages sum to 100%
- Include validation for construction industry businesses (T5018 reporting)

### Line 290 – Substantive CCPC Status
Corporations must determine if they meet the definition of substantive Canadian-Controlled Private Corporation (CCPC).

**Key Rules**:
- A substantive CCPC is a private corporation controlled by Canadian residents
- Applies to tax planning strategies involving loss of CCPC status
- Special rules apply for corporations with non-resident or public corporation share acquisition rights

**Implementation Note**: Create a decision tree in your application to help users determine substantive CCPC status based on control tests.

## Net Income Calculation

### Schedule 1 – Net Income (Loss) for Tax Purposes
Schedule 1 reconciles financial statement net income to taxable income by making specific tax adjustments.

**Key Adjustments**:
- Add non-deductible expenses (lines 101-199)
- Deduct non-taxable income (lines 401-499)
- Special rules for entertainment expenses (50% deductible, 80% for long-haul truck drivers)
- Non-compliant short-term rental expenses (effective January 1, 2024)

**Example**: A corporation with $100,000 accounting net income might have:
- $5,000 non-deductible entertainment expenses (added back)
- $2,000 non-taxable dividends (deducted)
- Resulting in $103,000 net income for tax purposes

### Schedule 6 – Capital Dispositions
Corporations must complete Schedule 6 when disposing of capital property.

**Key Fields**:
- Date of acquisition
- Proceeds of disposition
- Adjusted cost base (ACB)
- Outlays and expenses
- Capital gain or loss calculation

**Special Rules**:
- Partnership interests have specific ACB calculation rules
- Negative ACB triggers immediate capital gain recognition
- Crypto-assets may generate capital gains if not held as inventory

**Implementation Note**: Include validation for:
- Proceeds of disposition cannot be negative
- ACB calculation must follow specific rules for different property types
- Automatic calculation of capital gains/losses based on input data

## Technical Implementation Guidelines

For developers building tax applications:

1. **Data Validation**:
   - Implement field-specific validation rules
   - Cross-reference between related schedules
   - Ensure mathematical accuracy of calculations

2. **User Experience**:
   - Provide contextual help for complex concepts
   - Include examples for non-standard situations
   - Create decision trees for status determinations (CCPC, substantive CCPC)

3. **Integration Points**:
   - Link to NAICS code database
   - Connect to CRA documentation for reference materials
   - Implement electronic filing compatibility

4. **Compliance Features**:
   - Track effective dates for rule changes
   - Maintain audit trail for calculations
   - Generate required documentation summaries
