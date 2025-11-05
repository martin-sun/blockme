# Section 55

**Chapter 55**

---

## T2 Corporate Tax Credits Overview

### Part I Tax Calculations

#### Base Amount of Part I Tax (Line 550)
The fundamental tax calculation for all corporations before applying specific credits or deductions.

**Example**: A corporation with $500,000 taxable income would calculate its base Part I tax at the federal rate (15% for general corporations) before applying any credits.

#### Additional Tax on Personal Services Business Income (Line 560)
Personal services businesses face an additional 5% tax on top of the regular corporate tax rate.

**Implementation Note**: Developers should flag corporations with PSB status for this additional calculation.

#### Additional Tax on Banks and Life Insurers (Line 565)
Financial institutions subject to special tax rules must calculate this additional tax component.

#### Total Labour Requirements Addition to Tax (Line 580)
Specific industries may face additional tax based on labour requirements.

### Investment Tax Credits (ITC)

#### Recapture of Investment Tax Credit (Line 602)
When previously claimed ITCs need to be returned due to changes in circumstances.

**Example**: If a corporation claimed $50,000 in SR&ED credits but later determines that only $35,000 was eligible, $15,000 would be recaptured on line 602.

#### Scientific Research and Experimental Development (SR&ED)
One of the most valuable ITCs, encouraging innovation and development activities.

**Implementation Note**: Track eligible expenditures separately for proper credit calculation.

#### Child Care Spaces ITC
Credits for creating licensed child care spaces for employees.

#### Clean Economy ITC
Recent credits supporting investments in clean technology and renewable energy.

### Specialized Corporate Tax Measures

#### Refundable Tax on CCPC's Investment Income (Line 604)
Canadian-Controlled Private Corporations (CCPCs) pay refundable tax on investment income, which creates a refundable dividend tax credit pool.

**Example**: A CCPC earning $100,000 in passive investment income would pay refundable tax at 30.67% (rate may vary by year).

#### Federal Tax Abatement (Line 608)
A general rate reduction for corporations earning income in provinces or territories, equivalent to 10% of taxable income.

#### Manufacturing and Processing Profits Deduction and Zero-Emission Technology Manufacturing Deduction (Lines 616)
Enhanced deductions for corporations engaged in eligible manufacturing activities or zero-emission technology production.

**Implementation Note**: Verify eligibility criteria and maintain separate calculations for M&P and zero-emission components.

#### Investment Corporation Deduction (Lines 620 and 624)
Special deduction for corporations primarily earning investment income.

### Foreign Tax Credits

#### Federal Foreign Non-Business Income Tax Credit (Line 632)
Credit for taxes paid on foreign non-business income (e.g., dividends, interest, royalties).

#### Federal Foreign Business Income Tax Credit (Line 636)
Credit for taxes paid on foreign business income.

#### Continuity of Unused Federal Foreign Business Income Tax Credits
Rules for carrying forward unused foreign business tax credits.

#### Carryback or Carryforward of Unused Credits
General provisions for utilizing tax credits in different taxation years.

**Implementation Note**: Track credit utilization by year to optimize carryback/carryforward decisions.

### Other Tax Reductions

#### General Tax Reduction (Lines 638 and 639)
Additional tax reduction for small businesses and other qualifying corporations.

#### Federal Logging Tax Credit (Line 640)
Specific credit for corporations in the logging industry.

#### Eligible Canadian Bank Deduction (Line 641)
Special deduction for eligible Canadian banks under specific provisions.
