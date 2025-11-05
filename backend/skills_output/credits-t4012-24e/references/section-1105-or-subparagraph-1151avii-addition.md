# Section 38

**Chapter 38**

---

## Foreign Tax Deductions and Farm Loss Credits

### Section 110.5 or Subparagraph 115(1)(a)(vii) - Addition for Foreign Tax Deductions

Any amounts added to taxable income to utilize foreign tax deductions that could not otherwise be deducted from Part I tax.

**Implementation Note:** Developers should track these additions separately as they affect the calculation of taxable income but may have different carryforward rules than other deductions.

**Reference:** See Line 355 on page 74 of the T2 Corporation Income Tax Guide.

### Current-Year Farm Loss

#### Calculation Method

The current-year farm loss is the lesser of:
- The net loss from farming or fishing included in income
- The non-capital loss before deducting the farm loss

#### Detailed Calculation

The current-year farm loss is whichever of the following amounts is less:
- The loss from farming or fishing that exceeds the farming or fishing income for the year
- The amount of the current-year non-capital loss as calculated in Part 1 of Schedule 4 before deducting the farm loss for the year

**Implementation Steps:**
1. Calculate the farming or fishing loss (income minus expenses)
2. Calculate the non-capital loss before farm loss deduction
3. Apply the lesser of these two amounts as the farm loss

**Example:** 
A corporation has:
- Farming income: $50,000
- Farming expenses: $120,000
- Other business income: $30,000
- Other business expenses: $10,000

Calculation:
- Farming loss: $120,000 - $50,000 = $70,000
- Non-capital loss before farm loss: ($70,000 farming loss) + ($30,000 - $10,000) = $90,000
- Current-year farm loss: lesser of $70,000 and $90,000 = $70,000

Enter the farm loss calculated on line 310 of Schedule 4. The farm loss can also include an amount allocated from a partnership.

**Special Case:** If the result after the calculation shown under Part 1 is negative, enter this result (as positive) on line 110 of Schedule 4 as the current-year non-capital loss.

**Important Note:** You cannot use prior-year losses to create or increase a current-year non-capital loss, except with net capital losses of other years.

**References:**
- Subsection 111(8)
- IT-302, Losses of a Corporation – The Effect That Acquisitions of Control, Amalgamations and Windings-Up Have on Their Deductibility – After January 15, 1987

## Continuity of Non-Capital Losses and Carryback Provisions

### Overview

Use this section to establish the continuity of non-capital losses and to carry back a current-year non-capital loss to prior years.

### Carryback and Carryforward Rules

The current-year non-capital loss can:
- Reduce any kind of income or taxable dividends subject to Part IV tax
- Be carried back to the 3 previous tax years
- Be carried forward to the 20 following tax years
- Expire after the carry-forward period

**Implementation Note:** Developers should create a tracking system that monitors the expiry dates of non-capital losses to ensure they are utilized before expiration.

### Key Line Items and Their Meanings

#### Line 105 - Non-Capital Losses from Predecessor Corporation
Amount of non-capital losses transferred from:
- A predecessor corporation after amalgamation, or
- A subsidiary after wind-up where not less than 90% of the issued shares in each class were owned by the corporation immediately before the wind-up

This amount represents the unused non-capital losses available to be carried forward at the end of the tax year of the predecessor corporation or subsidiary ending immediately before the amalgamation or wind-up, minus any expired amount.

#### Line 140 - Debt Forgiveness Reduction
Amount of debt forgiveness under section 80 that reduces the non-capital losses balance. Losses must be reduced in the order established by section 80.

#### Line 150 - Other Adjustments
Amount received under subsection 111(10) as a fuel tax rebate that reduced non-capital loss for a previous year, and any other adjustments not previously mentioned.

These adjustments typically apply to corporations that have undergone an acquisition of control where losses accrued before the acquisition of control are not deductible after the acquisition of control.

### Final Calculation

The result of this section is the closing balance of non-capital losses carried forward to future years (line 180).

**Implementation Requirement:** Complete Part 6 to establish the balance of non-capital losses by year of origin to ensure proper tracking of expiry dates.
