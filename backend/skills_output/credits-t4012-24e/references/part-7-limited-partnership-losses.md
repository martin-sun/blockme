# Section 44

**Chapter 44**

---

## Limited Partnership Losses

### Current-Year Limited Partnership Losses

This section calculates current-year limited partnership losses that cannot be deducted in the current year but may be carried forward to other taxation years.

#### Documentation Requirements

- **T5013 Slip**: The amount of partnership loss allocated to a limited partner is reported on the T5013, Statement of Partnership Income.
- **Exempt Partnerships**: If the partnership is exempt from filing T5013 slips, you must file the partnership's financial statements with the corporation's return to substantiate the corporation's share of the partnership loss.

#### Reporting Timing

Report the loss amount in the corporation's tax year that corresponds to the partnership's fiscal period ending date.

#### At-Risk Rules

For tax years ending after February 26, 2018, the at-risk rules apply to:
- Partnerships that are themselves limited partners of other partnerships
- Situations requiring adjustment of a corporation's available non-capital loss and limited partnership loss carryforward balances as if these rules applied in preceding years

#### Calculating At-Risk Amount

Enter the corporation's at-risk amount at the partnership's fiscal period ending in column 606. The amount in column 604 must be from a business (other than farming or fishing) or from property.

**Formula for At-Risk Amount Calculation:**
```
At-Risk Amount = Adjusted cost base of partnership interest
               + Share of current-year income from partnership
               - Amounts owed to the partnership
               - Any amount or benefit intended to protect against loss of investment
```

#### Exemptions to At-Risk Rules

Partnership interests operating continuously since February 25, 1986, are generally exempt from at-risk rules. However, this exempt status may be lost if either of the following occurred after February 25, 1986:
- A substantial contribution of capital to the partnership
- Substantial partnership borrowings

#### Calculating Limited Partnership Loss

The limited partnership loss equals the difference between:
1. The corporation's share of the actual partnership loss
2. The corporation's at-risk amount (reduced by any investment tax credit, clean economy tax credit, farming losses, and resource expenses allocated to the corporation for that fiscal period)

Enter this amount in column 620.

#### Reporting Requirements

- Add the total of column 620 to line 222 of Schedule 1
- Enter all losses in column 670 to establish continuity of losses

**Example:**
A corporation has a $50,000 share of partnership loss but an at-risk amount of only $30,000. The limited partnership loss that can be carried forward is $20,000 ($50,000 - $30,000).

### Limited Partnership Losses from Previous Tax Years

Complete this section to apply limited partnership losses from previous years to reduce any type of income in the current year.

**Limitation:** The deductible amount for each partnership is limited to the difference between:
- The balance of losses for that partnership
- The corporation's at-risk amount for that partnership (after deducting amounts specified under subparagraph 111(1)(e)(ii))

### Continuity of Limited Partnership Losses

Limited partnership losses can be carried forward indefinitely to future taxation years.

#### Corporate Reorganizations

Column 664 represents limited partnership losses transferred from:
- A predecessor corporation after amalgamation
- A subsidiary after wind-up (where not less than 90% of issued shares in each class were owned by the corporation immediately before wind-up)

This amount represents the unused limited partnership losses available to carry forward at the end of the predecessor corporation's or subsidiary's tax year ending immediately before the amalgamation or wind-up.

#### Final Carryforward Calculation

The result of this section is the amount of limited partnership losses to carry forward to later years (column 680).

### References

- Subsection 96(2.1) of the Income Tax Act
- Interpretation Bulletin IT-232, "Losses – Their Deductibility in the Loss Year or in Other Years"

### Implementation Notes for Developers

1. **Data Collection**: Capture T5013 slip information or partnership financial statements
2. **At-Risk Calculation**: Implement the at-risk amount formula with all required components
3. **Exemption Logic**: Track partnership history to determine exemption status
4. **Carryforward Tracking**: Maintain detailed records of loss carryforwards by partnership
5. **Corporate Structure Changes**: Handle loss transfers during amalgamations and wind-ups
6. **Integration Points**: Connect with Schedule 1 (line 222) and other relevant tax forms
