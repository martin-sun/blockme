# Section 46

**Chapter 46**

---

## Intercorporate Dividend Deduction (Section 112 and Subsection 138(6))

### General Rule
Corporations receiving intercorporate dividends can claim a deduction equal to the amount of dividends received under Section 112 and subsection 138(6) of the Income Tax Act.

### Exception for Financial Institutions (Post-2023)
For dividends received or deemed received after 2023, the dividend received deduction under subsections 112(1), 112(2), and 138(6) will be denied for corporations that are financial institutions (as defined in subsection 142.2(1)). This applies to:
- Shares that are mark-to-market (MTM) property
- Tracking property of the corporation
- Shares that would be MTM property if held at any time during the year

**Exception:** This measure generally does not apply to dividends received on taxable preferred shares (as defined in the Income Tax Act).

### Key Definitions
#### Mark-to-Market (MTM) Property
Shares are considered MTM property when a financial institution holds less than 10% of the vote or value of the corporation that issued the shares.

#### Tracking Property
A property whose fair market value is determined by reference to certain attributes of another property that would be MTM property if held directly by the corporation.

### Deductible Dividends Under Section 112
When calculating taxable income, corporations can deduct the following types of taxable dividends received:
- Dividends from a taxable Canadian corporation
- Dividends from a corporation resident in Canada and controlled by the receiving corporation
- Dividends (or a portion of them) from a non-resident corporation (other than a foreign affiliate) that has carried on business in Canada continuously since June 18, 1971

### Non-Deductible Dividends Under Section 112
The following types of taxable dividends received are not deductible:
- Dividends from a corporation that is exempt from Part I tax
- Dividends on collateralized preferred shares (loss rental plans)
- Dividends that are part of a dividend rental arrangement, as defined in subsection 248(1)
- Dividends on term preferred shares received by certain financial institutions
- Dividends on shares guaranteed by a specified financial institution, as described in subsection 112(2.2)

### Practical Examples

#### Example 1: Standard Intercorporate Dividend Deduction
Corporation A receives $50,000 in dividends from Corporation B, a taxable Canadian corporation. Corporation A can deduct the full $50,000 when calculating its taxable income under section 112.

#### Example 2: Financial Institution with MTM Property
Bank X (a financial institution) holds 5% of the voting shares of Company Y, making these shares MTM property. In 2024, Bank X receives $20,000 in dividends from Company Y. Under the post-2023 rules, Bank X cannot claim the dividend received deduction for this amount.

#### Example 3: Preferred Share Exception
Financial Institution Z holds 8% of the preferred shares of Company W, which are classified as taxable preferred shares. Even though these shares would normally be considered MTM property (due to the ownership percentage being less than 10%), the dividends received on these shares remain deductible under the preferred share exception.

#### Example 4: Non-Resident Corporation Dividends
Canadian Corporation P receives $30,000 in dividends from US Corporation Q, which has been carrying on business in Canada continuously since 1970. Since Corporation Q is not a foreign affiliate and has been operating in Canada since before June 18, 1971, Corporation P can deduct these dividends under section 112.

### Implementation Considerations for Developers
1. **Financial Institution Identification**: Implement logic to identify if a corporation qualifies as a financial institution under subsection 142.2(1).

2. **MTM Property Classification**: Develop algorithms to determine if shares qualify as MTM property based on ownership percentage (less than 10% of vote or value).

3. **Tracking Property Detection**: Create mechanisms to identify tracking properties based on valuation methods.

4. **Preferred Share Exception**: Implement logic to identify taxable preferred shares as defined in the Income Tax Act.

5. **Dividend Type Classification**: Build functionality to classify dividends according to the deductible and non-deductible categories listed above.

6. **Date-Based Rules**: Ensure the system correctly applies the post-2023 rules for financial institutions.

### References
- Subsections 112(1), 112(2), and 112(2.1) to 112(2.9)
- Subsection 138(6)
- Subsection 142.2(1)
- Subsection 248(1)
