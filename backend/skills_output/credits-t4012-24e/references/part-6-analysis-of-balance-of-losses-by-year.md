# Section 43

**Chapter 43**

---

## Part 6: Analysis of Loss Carryforwards by Year of Origin

This section provides a detailed breakdown of all available loss balances that can be carried forward to reduce taxable income in future years. It is essential for tracking the remaining amount of each loss incurred, as losses must be applied in a specific order and have different carryforward periods depending on their type.

### Key Concepts for Developers

When building a module to handle loss carryforwards, consider the following core principles:

*   **Loss Types:** The system must differentiate between loss types, as they have distinct rules.
    *   **Non-capital Losses:** Generally incurred from business, property, or employment. Can be carried forward **20 years** and carried back **3 years**. These are the most flexible and can be deducted against any source of income.
    *   **Capital Losses:** Incurred from the disposition of capital property (e.g., stocks, real estate). Can be carried forward **indefinitely**. Can only be applied against taxable capital gains.
    *   **Farm/Fishing Losses:** (Restricted vs. General) May have special rules, including an **indefinite** carryforward period for certain portions.
*   **Year of Origin:** Each loss pool is tracked by the taxation year it was incurred. This is the primary key for organizing the schedule.
*   **Balance Tracking:** The system must track the `remaining_balance` for each loss pool from each year of origin. As losses are claimed in subsequent years, this balance is reduced.

### Implementation Guidance

A tabular format is the most effective way to present this information to users and for processing.

**Recommended UI/UX Structure:**

| Year of Origin | Type of Loss | Amount Available at Start of Year | Amount Claimed in Current Year | Remaining Balance at End of Year |
| :--- | :--- | :--- | :--- | :--- |
| 2023 | Non-Capital | $15,000 | $0 | $15,000 |
| 2022 | Non-Capital | $8,500 | $8,500 | $0 |
| 2021 | Capital | $4,000 | $0 | $4,000 |
| ... | ... | ... | ... | ... |

**Calculation Logic:**
The core calculation for each row is straightforward:
`Remaining Balance = Amount Available at Start of Year - Amount Claimed in Current Year`

**Critical Business Rule:**
The Canada Revenue Agency (CRA) requires that losses from the **earliest years** be claimed before losses from more recent years. Your application must enforce this "first-in, first-out" (FIFO) logic when a user applies a loss against their current year's income.

### Practical Example

**Scenario:** For the 2023 tax year, a small business has a net income of $20,000 and wants to claim non-capital losses to reduce it to zero. The business has the following historical loss balances:

*   **2021:** $5,000 non-capital loss remaining
*   **2022:** $18,000 non-capital loss remaining

**Application in Part 6:**

The system would automatically apply the 2021 loss first, followed by the 2022 loss, as required by the FIFO rule.

| Year of Origin | Type of Loss | Amount Available at Start of Year | Amount Claimed in Current Year (2023) | Remaining Balance at End of Year |
| :--- | :--- | :--- | :--- | :--- |
| 2022 | Non-Capital | $18,000 | $15,000 | $3,000 |
| 2021 | Non-Capital | $5,000 | $5,000 | $0 |

**Explanation:**
1.  The system first applies the entire $5,000 loss from 2021 against the $20,000 income, reducing the taxable income to $15,000.
2.  It then applies $15,000 from the 2022 loss pool to bring the taxable income to zero.
3.  The remaining balance for the 2022 loss is $3,000 ($18,000 - $15,000), which can be carried forward to 2024. The 2021 loss pool is now fully exhausted.
