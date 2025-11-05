# Section 39

**Chapter 39**

---

## Part 2 – Capital Losses

### Continuity of Capital Losses and Carryback Requests

The current-year capital loss is calculated on Schedule 6. This section establishes the continuity and application of capital losses as tax credits.

#### Establishing Continuity

To establish continuity of capital losses:
- Enter the total amount of capital losses (not net capital losses available)
- The inclusion rate is applied only when the loss is actually used as a credit
- Indicate the balance of any previous-year capital losses carried forward

**Example**: If your corporation has $100,000 in capital losses from the current year and $50,000 in carried forward losses from previous years, you would enter $100,000 for current losses and $50,000 for carried forward losses.

#### Application of Capital Losses as Tax Credits

Net capital losses can be applied as tax credits in the following ways:
- Reduce taxable capital gains included as income for the three previous tax years
- Be carried forward indefinitely for future years

**Example**: If your corporation has $20,000 in net capital losses for 2023, it can:
- Carry back up to $20,000 to offset capital gains in 2020, 2021, or 2022
- Carry forward any remaining balance to offset future capital gains

#### Specific Line Items

**Line 205 - Transferred Capital Losses**
Capital losses transferred from:
- A predecessor corporation after amalgamation, or
- A subsidiary after wind-up (where ≥90% of issued shares were owned immediately before wind-up)

This amount represents unused capital losses available to carry forward at the end of the tax year of the predecessor corporation or subsidiary, including:
- Any expired ABIL (Allowable Business Investment Loss) as non-capital loss
- Divided by the inclusion rate for the tax year in which the ABIL was incurred

**Example**: If a subsidiary with a $50,000 capital loss is wound up by a parent corporation owning 95% of its shares, the parent corporation can claim this $50,000 loss as a credit on line 205.

**Line 250 - Other Adjustments**
These adjustments typically apply to corporations that:
- Have undergone an acquisition of control
- Have losses accrued before acquisition of control that are not deductible as credits after
- Have losses occurred after acquisition of control that are not deductible as credits before

**Example**: If Corporation A acquires control of Corporation B on June 1, 2023, Corporation B's capital losses from before June 1 may not be deductible as credits after the acquisition, requiring an adjustment on line 250.

**Line 240 - Debt Forgiveness**
Debt forgiveness under section 80 that reduces the capital losses balance
- Losses must be reduced in the order established by section 80

**Example**: If a corporation has $30,000 in capital losses and receives $10,000 in debt forgiveness, the capital losses balance must be reduced by $10,000 on line 240.

**Line 220 - Expired ABIL**
ABIL earned as non-capital losses in the 11th previous year
- Must not have been used against taxable income in the previous 10 years
- Amount is multiplied by 2

**Example**: If a corporation has $5,000 of ABIL from 2013 that was not used in the past 10 years, it would enter $10,000 ($5,000 × 2) on line 220 for the 2023 tax year.

#### Carryback Process

On lines 951 to 953, enter the amount of capital loss you carry back to prior years:
- Line 951: Carryback to first prior year
- Line 952: Carryback to second prior year
- Line 953: Carryback to third prior year

**Example**: To carry back $15,000 of capital losses from 2023, with $5,000 to each of 2020, 2021, and 2022:
- Enter $5,000 on line 951 (for 2022)
- Enter $5,000 on line 952 (for 2021)
- Enter $5,000 on line 953 (for 2020)

#### Closing Balance

The result of this section is the closing balance of available capital losses carried forward to future years (line 280).

#### Inclusion Rate

The net capital loss amount will be calculated at the 50% inclusion rate.

**Example**: If a corporation has $20,000 in capital losses, the deductible amount for tax purposes is $10,000 ($20,000 × 50%).

### Implementation Notes for Developers

When implementing capital loss calculations as tax credits in tax software:

1. **Track Loss Origins**: Maintain records of when capital losses were incurred to properly apply carryback and carryforward rules.

2. **Inclusion Rate Application**: Apply the 50% inclusion rate only when calculating the deductible amount of capital losses as credits, not when tracking the total loss balance.

3. **Special Cases Handling**:
   - For amalgamations and wind-ups (line 205), verify the 90% ownership threshold
   - For acquisitions of control (line 250), track the acquisition date to separate pre- and post-acquisition losses
   - For debt forgiveness (line 240), apply section 80 ordering rules
   - For ABIL calculations (line 220), implement the 10-year expiry tracking and 2× multiplier

4. **Carryback Logic**:
   - Implement a three-year lookback window for capital loss carrybacks
   - Allow users to specify allocation across the three years
   - Ensure carryback amounts don't exceed available capital gains in those years

5. **Closing Balance Calculation**:
   - Opening balance + Current year losses - Applied losses - Adjustments = Closing balance
   - Ensure the closing balance is always non-negative

6. **Credit Application**:
   - Apply capital losses against capital gains first
   - Track remaining capital loss balance for future use
   - Generate appropriate T2 Corporation Income Tax Guide references for audit purposes
