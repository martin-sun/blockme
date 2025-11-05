# Section 70

**Chapter 70**

---

## Part 4 of Schedule 43 – Calculation of Part IV.1 Tax Payable

### Overview of Part IV.1 Tax
Part 4 provides detailed instructions for calculating Part IV.1 tax, which applies to specific dividend income received by corporations. This tax mechanism prevents tax deferral advantages that might otherwise arise from certain corporate structures.

### Corporations Subject to Part IV.1 Tax

#### Public Corporations and Other Eligible Corporations
- Subject to 10% Part IV.1 tax on dividends received from taxable preferred shares
- Applies to dividends received from both Canadian and foreign corporations

#### Restricted Financial Institutions
- Subject to Part IV.1 tax on dividends received from taxable restricted financial institution shares
- Reference: Subsection 248(1) of the Income Tax Act for complete definitions

### Tax Election Mechanism

#### Issuer Election Option
The issuer of taxable preferred shares may elect to:
- Pay 40% tax under Part VI.1 (instead of the standard 25% rate)
- Complete this election in Part 3 of Schedule 43
- No additional forms required for this election

#### Impact on Shareholders
This election provides a significant benefit:
- Exempts the shareholder from the 10% Part IV.1 tax
- Eliminates the need for the shareholder to claim a refund for the Part IV.1 tax paid

**Example:** 
If Corporation A receives $10,000 in dividends from taxable preferred shares of Corporation B:
- Without election: Corporation A pays $1,000 (10%) Part IV.1 tax
- With election by Corporation B: Corporation A pays $0 Part IV.1 tax

### Excepted Dividends

#### Definition and Application
Excepted dividends, as defined in section 187.1 of the Income Tax Act, are exempt from Part IV.1 tax. These include:

1. **Substantial Interest Exception**
   - Dividends received on shares where the recipient corporation held a substantial interest at the time of dividend receipt
   - "Substantial interest" generally means 10% or more of the issued shares of any class

2. **Connected Corporation Exception**
   - Dividends from connected corporations where specific relationship criteria are met

**Practical Example:**
Corporation X owns 15% of Corporation Y's common shares. When Corporation Y declares and pays dividends to Corporation X, these dividends are considered "excepted dividends" and are not subject to Part IV.1 tax because Corporation X held a substantial interest (15%) at the time of dividend receipt.

### Implementation Notes for Tax Applications

#### Data Requirements
- Track share ownership percentages at dividend receipt dates
- Identify taxable preferred shares vs. regular shares
- Flag restricted financial institution shares
- Monitor issuer elections under Part VI.1

#### Calculation Logic
```pseudo
if (dividend.from_taxable_preferred_shares && !issuer_elected_part_VI1) {
    part_IV1_tax = dividend.amount * 0.10;
} else if (dividend.from_restricted_financial_institution_shares) {
    part_IV1_tax = dividend.amount * 0.10;
} else if (dividend.is_excepted) {
    part_IV1_tax = 0;
} else {
    part_IV1_tax = 0;
}
```

#### Reference Information
- Detailed guidance: Line 724 on page 97 of the T2 Corporation Income Tax Guide
- Legal definitions: Subsection 248(1) of the Income Tax Act
- Excepted dividends: Section 187.1 of the Income Tax Act
