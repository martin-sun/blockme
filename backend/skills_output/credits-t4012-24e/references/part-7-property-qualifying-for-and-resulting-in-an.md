# Section 30

**Chapter 30**

---

## Part 7 – Allowable Business Investment Loss (ABIL)

### Definition and Qualification

An Allowable Business Investment Loss (ABIL) arises from the arm's length disposition (or deemed disposition) of:

- Shares of a small business corporation
- Certain debts owed to the corporation by:
  - Small business corporations
  - Certain bankrupt corporations
  - Certain wound-up corporations

*Note: All corporations mentioned above must deal with the taxpayer at arm's length.*

A small business corporation is defined in subsection 248(1) of the Income Tax Act.

### Practical Example: ABIL Calculation

ABC Corp. invested $50,000 in shares of XYZ Inc., a small business corporation. XYZ Inc. went bankrupt, and ABC Corp. sold the shares for $2,000. The $48,000 loss ($50,000 - $2,000) qualifies as a business investment loss, which can be claimed as an ABIL.

### Implementation Considerations for Developers

When building tax applications:
1. Verify that the disposed property qualifies as ABIL-eligible
2. Check arm's length relationship requirements
3. Calculate ABIL as: Proceeds of disposition - Adjusted cost base
4. Apply any applicable limitations or special rules

### Calculation

Complete Part 7 to calculate the business investment losses at amount G.

## Capital Gains Reserve

### General Principle

When you don't receive the full proceeds of disposition (typically for real property) until after the end of the tax year, you can defer part of the capital gain to the year the corporation receives the proceeds by establishing a capital gains reserve. This allows spreading a capital gain over a maximum of five years.

### Practical Example: Real Property Disposition

A corporation sells a rental property for $500,000 with an adjusted cost base of $300,000, resulting in a $200,000 capital gain. The buyer pays $300,000 in the year of sale and will pay the remaining $200,000 in equal installments over the next four years. The corporation can claim a capital gains reserve for the portion of the gain attributable to the payments not yet received.

### Special Case: Gifts of Non-Qualifying Securities

A corporation that has made a gift of a non-qualifying security to a qualified donee may claim a reserve for any gain realized on this security. The reserve cannot exceed the eligible amount of the gift.

**Eligible Amount Calculation:**
The eligible amount of a gift is the amount by which the fair market value of the property exceeds the amount of any advantage received in respect of the gift.

### Practical Example: Gift of Non-Qualifying Securities

A corporation gifts shares with a fair market value of $100,000 and an adjusted cost base of $60,000 to a registered charity. The corporation receives no advantage for this gift. The eligible amount is $100,000, and the capital gain is $40,000. The corporation can claim a reserve for this gain, subject to the limitations described below.

### Conditions for Claiming Reserve

A reserve can only be claimed if:
- The donation is not deducted for tax purposes
- The donee does not dispose of the security
- The security does not cease to be a non-qualifying security

This reserve can only be claimed in tax years ending within 60 months of making the gift.

### Reserve Inclusion Requirements

The reserve must be included in income if:
- The corporation becomes a non-resident
- The corporation becomes tax-exempt

### Maximum Reserve Calculation

The reserve that can be claimed in a tax year cannot exceed the lesser of:

**A. Formula-based Calculation:**
```
Capital gain × (Amount not due until after the end of the year ÷ Proceeds of disposition)
```

**B. Percentage-based Calculation:**
- Year of disposition: 4/5 of the capital gain
- Second year: 3/5 of the capital gain
- Third year: 2/5 of the capital gain
- Fourth year: 1/5 of the capital gain

### Practical Example: Reserve Calculation

Using the real property example above:
- Capital gain: $200,000
- Amount not due until after year-end: $200,000
- Proceeds of disposition: $500,000

**Calculation A:**
$200,000 × ($200,000 ÷ $500,000) = $80,000

**Calculation B (Year of disposition):**
4/5 × $200,000 = $160,000

The maximum reserve that can be claimed is the lesser of $80,000 and $160,000, which is $80,000.

### Implementation Considerations for Developers

When building tax applications:
1. Track the timing of proceeds receipt
2. Calculate both reserve methods and apply the lesser amount
3. Implement a 5-year maximum reserve period
4. Handle special cases for gifts of non-qualifying securities
5. Include logic for reserve inclusion when corporation status changes
6. Maintain continuity of reserves across tax years

### Reporting Requirements

1. Add the reserve amount deducted in a tax year to income in the following tax year.
2. Report the reserve opening balance and subtract the reserve closing balance on lines 880 and 885 of Schedule 6.
3. Show the continuity of capital gain reserves on Schedule 13, Continuity of Reserves.

### References

- Subparagraphs 40(1)(a)(ii) and 40(1)(a)(iii) of the Income Tax Act
- Subsection 40(1.01) of the Income Tax Act
