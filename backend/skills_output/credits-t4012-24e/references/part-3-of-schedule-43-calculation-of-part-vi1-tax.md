# Section 65

**Chapter 65**

---

## Corporate Tax Credits and Calculations

### Part VI.1 Tax Payable

#### Part 3 of Schedule 43 – Calculation of Part VI.1 Tax Payable

This section calculates the Part VI.1 tax payable, which applies to certain investment income of private corporations and specified public corporations. Part VI.1 tax is an additional tax that prevents the deferral of tax on investment income.

**For developers:**
- Implement calculation logic for Part VI.1 tax based on investment income
- Include fields for eligible dividends, taxable capital gains, and other investment income
- Apply appropriate tax rates as specified in the Income Tax Act

#### Schedule 45 – Agreement Respecting Liability for Part VI.1 Tax

Schedule 45 is used when multiple related corporations need to allocate Part VI.1 tax liability among themselves. This is common in corporate groups where investment income may be attributed to different entities.

**Example:**
A corporate group with three related corporations (A, B, and C) has total Part VI.1 tax of $15,000. They can use Schedule 45 to allocate this tax as follows:
- Corporation A: $7,500
- Corporation B: $5,000
- Corporation C: $2,500

**For developers:**
- Create forms for allocating Part VI.1 tax among related corporations
- Include validation to ensure total allocation equals the total Part VI.1 tax
- Implement logic for tracking related corporation information

### Other Tax Payable Categories

#### Line 725 – Part VI.2 Tax Payable

Part VI.2 tax applies to certain financial institutions and relates to their capital tax obligations. This tax was largely eliminated but may still apply in specific circumstances.

**For developers:**
- Include conditional logic to determine if Part VI.2 tax applies based on corporation type
- Implement calculation fields for applicable financial institutions

#### Line 727 – Part XIII.1 Tax Payable

Part XIII.1 tax is a withholding tax that applies to certain types of passive income paid to non-residents, including:
- Royalties
- Rent payments
- Management fees
- Interest payments (with exceptions)

**Example:**
A Canadian corporation pays $10,000 in royalties to a non-resident. The Part XIII.1 tax rate is 25%, resulting in $2,500 tax payable.

**For developers:**
- Implement calculation logic for various types of passive income paid to non-residents
- Include different tax rates based on tax treaty provisions
- Create fields for treaty-based reductions

#### Line 728 – Part XIV Tax Payable

Part XIV tax relates to the tax on large corporations. It applies to corporations with taxable capital employed in Canada exceeding $50 million.

**For developers:**
- Implement threshold checks for taxable capital
- Include progressive tax rate calculations based on capital amounts
- Create fields for capital employed in Canada calculations

### Provincial and Territorial Tax

#### Permanent Establishment

A permanent establishment is a fixed place of business in a province or territory, which determines where provincial/territorial tax is payable. This includes:
- Offices
- Factories
- Warehouses
- Construction sites lasting more than 12 months

**For developers:**
- Create logic to identify permanent establishments in each jurisdiction
- Implement allocation formulas for income attributable to each permanent establishment
- Include fields for physical presence details

#### Line 750 – Provincial or Territorial Jurisdiction

This line identifies which provincial or territorial tax forms need to be completed based on where the corporation has permanent establishments.

**Example:**
A corporation with permanent establishments in Ontario and Alberta would need to complete:
- T2 Corporation Income Tax Return (Federal)
- ON428 Corporation Tax Schedule (Ontario)
- AT1 Return of Income (Alberta)

**For developers:**
- Implement jurisdiction selection based on permanent establishment locations
- Create conditional form requirements based on selected jurisdictions
- Include mapping to appropriate provincial/territorial forms

#### Line 760 – Net Provincial and Territorial Tax Payable

This line calculates the total provincial and territorial tax payable after accounting for:
- Provincial/territorial tax credits
- Abatements
- Other reductions

**For developers:**
- Implement calculation logic for each provincial/territorial tax system
- Include fields for various provincial credits and deductions
- Create summation logic for multiple jurisdictions

### Schedule 5 – Tax Calculation Supplementary – Corporations

Schedule 5 provides additional calculations for corporate tax, including:
- Tax reductions for small businesses
- Manufacturing and processing profits deductions
- General tax reductions
- Investment tax credits

**For developers:**
- Implement comprehensive calculation fields for various tax reductions
- Include logic for small business deduction eligibility
- Create fields for investment tax credit calculations
- Implement validation for reduction limits and interactions
