# Section 29

**Chapter 29**

---

## Part 6 – Listed Personal Property (LPP) Dispositions

This section requires the reporting of all dispositions of Listed Personal Property (LPP) during the corporation's tax year.

### Definition of Listed Personal Property

LPP is a specific category of personal-use property that typically appreciates in value. Gains and losses from its disposition are subject to special rules.

The following items are classified as LPP:
-   Prints, etchings, drawings, paintings, sculptures, or other similar works of art
-   Jewellery
-   Rare folios, rare manuscripts, or rare books
-   Stamps
-   Coins

> **Developer Note:** For form UI, consider implementing a dropdown or selection list with these predefined categories to ensure data integrity and accurate classification.

### Special Treatment of LPP Losses

Losses incurred from the disposition of LPP are restricted. Unlike other capital losses, they can **only** be deducted against capital gains realized from the disposition of *other* LPP. They cannot be used to reduce gains from other types of capital property, such as real estate or stocks.

**Practical Example:**
A corporation disposes of two assets in the current year:
1.  Sells a sculpture (LPP) for a **$10,000 capital loss**.
2.  Sells a rare book collection (LPP) for a **$15,000 capital gain**.

**Calculation:**
The $10,000 LPP loss can be fully applied against the $15,000 LPP gain.
-   Net LPP Gain for the year = $15,000 (Gain) - $10,000 (Loss) = **$5,000**.

The $10,000 loss could not be used to offset a gain from, for example, selling a commercial building.

### Carryback and Carryforward of Unabsorbed LPP Losses

If LPP losses exceed LPP gains in the current year, the unabsorbed portion can be applied to other taxation years.
-   **Carryback:** Apply to reduce net LPP gains in any of the three preceding years.
-   **Carryforward:** Apply to reduce net LPP gains in any of the seven subsequent years.

Detailed tracking and application of these losses are managed in **Part 5 – Listed personal property losses**.

### Calculation and Form Integration

Follow these steps for accurate reporting and system logic:

1.  **Calculate Current-Year Net Gain/Loss:**
    Sum all individual gains and losses from LPP dispositions for the tax year.
    -   `Formula: Σ (Proceeds of Disposition - Adjusted Cost Base)`

2.  **Apply Prior-Year LPP Losses:**
    Enter the amount of available LPP losses from previous years that you wish to claim in the current year.
    -   Enter this amount on **line 655** of this schedule.
    -   Also, enter this amount on **line 530 of Schedule 4, Corporation Loss Continuity and Application**.

3.  **Determine Final Net Amount (Amount F):**
    Calculate the final amount to be reported.
    -   `Formula: Amount F = (Current Year Net LPP Gain) - (Amount from line 655)`

4.  **Manage Unabsorbed Losses:**
    If a net LPP loss remains after applying all available prior-year losses, your application must track this balance. This unabsorbed loss is available for carryback or carryforward according to the rules above.
