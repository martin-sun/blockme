# Section 67

**Chapter 67**

---

## Part 1 – Dividends Received in the Tax Year

### Purpose
Complete Part 1 to identify both taxable and non-taxable dividends received during the tax year and calculate Part IV tax before deductions.

### Exemptions
Public corporations (other than subject corporations) are exempt from calculating Part IV tax.

### Handling Multiple Dividend Sources

#### Multiple Payer Corporations
If more than one corporation paid dividends, perform a separate calculation for each payer corporation.

#### Different Tax Years
If your corporation's tax year-end differs from that of the payer corporation, dividends may have been received from multiple tax years of the payer corporation. In such cases:
- Use a separate line for each tax year of the payer corporation
- Provide information according to each respective tax year

### Taxable Dividends Deduction
On line 320 of the return, enter the amount of taxable dividends deductible from taxable income under:
- Section 112
- Subsections 113(2) and 138(6)
- Paragraphs 113(1)(a), (a.1), (b), or (d)

### Practical Examples

#### Example 1: Multiple Payer Corporations
Corporation A received dividends from three different corporations during the tax year:
- $10,000 from Corporation B
- $15,000 from Corporation C
- $5,000 from Corporation D

Each dividend amount requires a separate calculation in Part 1.

#### Example 2: Different Tax Years
Corporation X has a December 31 year-end and received dividends from Corporation Y, which has a March 31 year-end:
- $8,000 received in January 2023 (from Corporation Y's 2022 tax year)
- $12,000 received in July 2023 (from Corporation Y's 2023 tax year)

These dividends should be reported on separate lines according to Corporation Y's respective tax years.

### Implementation Notes for Developers
When building tax applications:
1. Create separate calculation modules for each dividend source
2. Implement functionality to handle different tax years for the same corporation
3. Include validation to ensure all applicable tax sections and subsections are considered for line 320 calculations
4. Design the interface to clearly distinguish between taxable and non-taxable dividends
5. Provide clear categorization for dividends received from different tax years of the same corporation
