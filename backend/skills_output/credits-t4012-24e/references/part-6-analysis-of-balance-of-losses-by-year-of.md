# Section 20

**Chapter 20**

---

## Managing Tax Losses: Carrybacks, Carryforwards, and Balance Tracking

This section details the rules for applying tax losses, which function as deductions against taxable income. While distinct from tax credits (which reduce tax payable directly), the tracking and application of losses require similar data management principles, particularly for maintaining balances by year of origin.

### Key Distinction: Loss vs. Credit

*   **Tax Loss:** A **deduction** that reduces a taxpayer's *taxable income*. The value of a loss is dependent on the tax rate applied to the income it offsets.
*   **Tax Credit:** A **reduction** that directly decreases the *tax payable* calculated on taxable income. The value of a credit is generally fixed (e.g., a $1,000 non-refundable credit reduces tax by $1,000).

### Types of Losses and Their Application Rules

Different loss types have specific rules for how far they can be carried back or carried forward. Your application must differentiate between these types.

| Loss Type | Description | Carryback Period | Carryforward Period |
| :--- | :--- | :--- | :--- |
| **Non-Capital Losses** | The most common type, arising from business or property expenses exceeding income. | 3 years | 20 years* |
| **Net Capital Losses** | Incurred when capital losses exceed capital gains. Can only be applied against taxable capital gains. | 3 years | Indefinitely |
| **Farm or Fishing Losses** | Specific to primary farming or fishing activities. | 3 years | 20 years* |
| **Restricted Farm Losses** | A portion of a farm loss that is treated as a non-capital loss if the taxpayer's farming income is not the primary source of income. | 3 years | 20 years* |

*\*Note: For losses incurred after March 20, 2023, the carryforward period is indefinite. For losses incurred in prior years, the 20-year limit still applies. Your system must track the origin year to apply the correct rule.*

### The Importance of Tracking Losses by Year of Origin

The "Analysis of balance of losses by year of origin" is a critical concept for developers. It is not sufficient to maintain a single, aggregated loss balance. Instead, you must track each loss pool separately based on the year it was incurred.

**Why is this essential?**
1.  **Expiry Dates:** Losses may expire (e.g., the 20-year rule for older non-capital losses). The system must know when each portion of the loss balance becomes unusable.
2.  **Rule Changes:** Tax laws evolve. A loss from 2010 might have different application rules than a loss from 2024.
3.  **Optimal Application:** To minimize tax, a system might need to strategically apply older losses before newer ones to prevent expiry.

### Practical Example: Applying a Non-Capital Loss

**Scenario:** A corporation has a $100,000 non-capital loss in 2023. It has taxable income of $30,000 in 2020, $0 in 2021, and $50,000 in 2024. The tax rate is 15%.

**Step 1: Carryback to 2020**
*   The corporation can carry back the loss to the 3 preceding years (2020, 2021, 2022).
*   It applies $30,000 of the 2023 loss against the 2020 taxable income.
*   **Result:** 2020 taxable income is reduced to $0. The corporation can file a T1 Adjustment Request to get a refund of the tax paid: $30,000 * 15% = $4,500.
*   **Remaining Loss Balance:** $100,000 - $30,000 = $70,000.

**Step 2: Carryforward to 2024**
*   The remaining $70,000 loss is carried forward to future years.
*   In 2024, the corporation has $50,000 of taxable income.
*   It applies $50,000 of the remaining loss against the 2024 income.
*   **Result:** 2024 taxable income is reduced to $0.
*   **Remaining Loss Balance:** $70,000 - $50,000 = $20,000. This $20,000 can be carried forward to 2025 and subsequent years until it expires.

### Implementation Notes for Tax Applications

When building a module to handle losses, consider the following:

#### 1. Data Structure
Your data model should track losses as a collection of objects, not a single value.

```json
"lossPools": [
  {
    "originYear": 2023,
    "type": "NON_CAPITAL",
    "initialAmount": 100000.00,
    "remainingAmount": 20000.00,
    "expiryYear": 2043 // Based on rules in effect for 2023
  },
  {
    "originYear": 2024,
    "type": "NET_CAPITAL",
    "initialAmount": 5000.00,
    "remainingAmount": 5000.00,
    "expiryYear": null // Indefinite carryforward
  }
]
```

#### 2. Calculation Logic
The calculation engine should follow a specific order of operations:
1.  **Identify Current Year Loss:** Determine if the current year's calculation results in a new loss. If so, create a new loss pool entry.
2.  **Apply Carrybacks:** For a new loss, first check the 3 preceding years for taxable income against which the loss can be applied. Generate the necessary data for refund claims.
3.  **Apply Carryforwards:** For the current year's taxable income, apply available carryforward losses. A common strategy is FIFO (First-In, First-Out) to use the oldest losses first and avoid expiry.
4.  **Update Balances:** After each application (carryback or carryforward), decrement the `remainingAmount` for the specific loss pool that was used.

#### 3. Edge Cases and Validation
*   **Amalgamations:** Handle the transfer and combination of loss pools between predecessor and successor corporations.
*   **Business Acquisitions:** Account for rules that may restrict the use of acquired losses.
*   **Change of Use:** Monitor changes in a corporation's primary business that could affect the classification of losses (e.g., a restricted farm loss).
*   **Annual Expiry Check:** Implement a process to flag or remove loss pools that have expired in the current tax year.
