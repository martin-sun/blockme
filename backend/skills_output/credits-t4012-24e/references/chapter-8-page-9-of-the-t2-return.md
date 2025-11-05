# Section 61

**Chapter 61**

---

## Chapter 8 – Tax and Credits Overview

### Summary of Tax and Credits (Page 94)
This section provides a comprehensive overview of all federal taxes payable and credits available to corporations. Developers should implement this as a summary view that aggregates all tax calculations and credits.

### Federal Tax Calculations (Page 94)

#### Line 700 – Part I Tax Payable
Represents the basic federal tax calculated on taxable income. This is the primary federal tax obligation before any special taxes or credits.

**Implementation Note:** Calculate as taxable income × federal tax rate (15% for general corporations, lower rates for small businesses).

#### Line 705 – Part II.2 Tax Payable
Applies to certain corporations with capital gains from taxable capital property. This is a specialized tax that affects specific corporate structures.

**Example:** A corporation with $100,000 in taxable capital gains may be subject to Part II.2 tax.

#### Line 710 – Part III.1 Tax Payable
Relates to tax on investment income of private corporations that have not distributed sufficient dividends to shareholders.

**Implementation Note:** Calculate based on refundable dividend tax on hand (RDTOH) and investment income.

### Dividend-Related Calculations (Page 94)

#### Eligible Dividend Designation
Corporations must designate dividends as eligible to allow shareholders to claim the enhanced dividend tax credit.

**Implementation Note:** Track eligible dividend designations throughout the year and ensure proper documentation.

#### General Rate Income Pool (GRIP)
Represents the portion of a corporation's income that can be paid as eligible dividends.

**Example:** If a corporation has $50,000 in GRIP, it can designate up to $50,000 of dividends as eligible.

#### Low Rate Income Pool (LRIP)
Represents the portion of income taxed at the small business rate that can be paid as eligible dividends.

**Implementation Note:** Calculate LRIP as small business deduction limit × (general tax rate - small business rate).

### Corporate Elections (Page 95)

#### Election to Not Be a Canadian-Controlled Private Corporation (CCPC)
Corporations can elect to lose CCPC status for tax purposes, which affects eligibility for certain credits and deductions.

**Implementation Note:** Include this as a binary flag in the corporate profile with effective date.

#### Election to Treat Excessive Eligible Dividend Designations as Ordinary Dividends
Allows corporations to reclassify dividends that exceed their GRIP balance.

**Example:** If a corporation designates $60,000 as eligible dividends but only has $50,000 in GRIP, it can elect to treat $10,000 as ordinary dividends.

### Specialized Tax Calculations (Page 95-96)

#### Line 712 – Part IV Tax Payable
Applies to dividends received from taxable Canadian corporations, designed to prevent tax deferral through corporate structures.

**Implementation Note:** Calculate as 33⅓% of taxable dividends received, with exceptions for connected corporations.

#### Dividends Subject to Part IV Tax
Not all dividends are subject to Part IV tax. This section details which dividends are included.

**Example:** Dividends from connected corporations and portfolio dividends may be treated differently.

#### Definitions
Provides specific definitions for terms used in Part IV tax calculations.

**Implementation Note:** Create a reference table for these definitions to ensure consistent application.

#### Parts 1 and 2 of Schedule 3
Details the specific calculations for Part IV tax, including portfolio dividends and connected corporation dividends.

#### Line 716 – Part IV.1 Tax Payable
Applies to certain inter-corporate dividends received by insurance corporations.

**Implementation Note:** Implement specific validation rules for insurance corporations to determine Part IV.1 tax applicability.
