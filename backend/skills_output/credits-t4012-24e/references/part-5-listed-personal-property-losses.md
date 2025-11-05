# Section 42

**Chapter 42**

---

## Listed Personal Property (LPP) Losses

This section outlines the specific rules governing losses from the disposition of listed personal property (LPP). LPP typically includes art, jewellery, stamps, and rare coins. These losses are a distinct category of capital losses with unique application rules.

### Core Principles

*   **Specific Application:** An LPP loss can only be deducted against **net capital gains** from the disposition of the **same type of LPP**. It cannot be applied against other types of capital gains (e.g., from stocks or real estate).
*   **Non-Transferable:** LPP losses cannot be transferred to a spouse or another individual.
*   **Separate Tracking:** LPP losses must be tracked separately from other capital losses due to their restricted application and limited carryforward period.

### Loss Carryback and Carryforward Periods

LPP losses are subject to specific time limitations for application against gains.

*   **Carryback:** A current-year LPP loss can be carried back to reduce net capital gains from the same type of LPP incurred in any of the **three preceding tax years**. This may result in a refund for those prior years.
*   **Carryforward:** Any unused portion of an LPP loss can be carried forward to reduce net capital gains from the same type of LPP in any of the **seven subsequent tax years**.

### Implementation for Tax Applications (T2 Schedule 6, Part 5)

For corporations, the calculation and tracking of LPP losses are formalized in Part 5 of Schedule 6 (Capital Gains). The following lines are critical for system logic:

*   **Line 530 - Prior-Year Losses Applied:** This field captures the total amount of LPP losses from prior years that are being applied to reduce the current year's net LPP capital gain. This value must also be populated on **Line 655 of Schedule 6**.
*   **Line 550 - Adjustments:** This line is used for specific adjustments, most notably for corporations that have undergone an **acquisition of control**. Losses accrued before the acquisition are generally not deductible after the event, requiring a reduction to the available loss balance.
*   **Line 580 - Closing Balance (Carryforward):** This is the resulting balance of LPP losses after all current-year applications and adjustments. It represents the amount available to be carried forward to future tax years and must be tracked by year of origin in Part 6.

### Special Considerations: Acquisition of Control

When a corporation is acquired, the tax attributes of the predecessor corporation, including LPP losses, are generally frozen. Any LPP losses that accrued before the acquisition of control cannot be used to offset capital gains realized after the acquisition. Line 550 is the mechanism for adjusting the loss pool to reflect this restriction.

### Practical Example

**Scenario:**
A corporation sells a rare painting (LPP) in the 2023 tax year, realizing a **$20,000 LPP loss**. In the 2021 tax year, the corporation sold a different painting and realized a **$15,000 LPP capital gain**.

**Action:**
The corporation can file a T2 Adjustment Request to carry back a portion of the 2023 loss.

**Result:**
1.  **Carryback:** $15,000 of the 2023 loss is carried back to 2021, reducing the 2021 net LPP capital gain to $0. This generates a tax refund for the 2021 year.
2.  **Carryforward:** The remaining **$5,000 loss** ($20,000 - $15,000) from 2023 is available to be carried forward. It can be applied against any LPP gains incurred up to and including the 2030 tax year (7-year limit).
