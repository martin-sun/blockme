# Section 28

**Chapter 28**

---

## Part 5 – Personal-use Property Dispositions

### Overview
Report all personal-use property disposed of during the tax year in this section.

### Definition
Personal-use property of a corporation refers to property owned primarily for the personal use or enjoyment of an individual related to the corporation.

### The $1,000 Rule for Determining Gains and Losses

#### Application of the Rule
When calculating gains or losses on personal-use property dispositions, apply the $1,000 rule as follows:
- If the adjusted cost base (ACB) is less than $1,000, it is deemed to be $1,000
- If the proceeds of disposition are less than $1,000, they are deemed to be $1,000

#### Practical Examples
1. **Example 1**: A corporation disposes of personal-use property with an ACB of $300 and proceeds of $800.
   - Deemed ACB: $1,000 (actual $300 < $1,000)
   - Deemed proceeds: $1,000 (actual $800 < $1,000)
   - Result: No capital gain or loss

2. **Example 2**: A corporation disposes of personal-use property with an ACB of $2,000 and proceeds of $1,200.
   - Deemed ACB: $2,000 (actual > $1,000)
   - Deemed proceeds: $1,200 (actual > $1,000)
   - Result: Capital loss of $800

#### Exception to the Rule
The $1,000 rule does not apply when:
- Donors acquire personal-use property as part of an arrangement
- The property is subsequently gifted to a qualified donee (e.g., registered charity)

### Treatment of Losses
Losses on dispositions of personal-use property are generally not deductible from income, except for:
- Listed personal property
- Debts that qualify as personal-use property

### Reporting Requirements
Enter the total amount of gain realized on disposition of personal-use property at amount E.

### Implementation Notes for Developers
- Implement validation to ensure all personal-use property dispositions are captured
- Apply the $1,000 rule logic when calculating gains/losses
- Include exception handling for charitable donation scenarios
- Ensure non-deductibility of losses is enforced in calculations
- Sum all gains for entry at amount E

### Reference
Subsection 46(1) of the Income Tax Act
