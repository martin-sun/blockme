# Section 25

**Chapter 25**

---

## Part 2 – Real Estate Dispositions

This section requires the reporting of all real estate properties disposed of during the tax year. The calculation of the resulting gain or loss depends on whether the property is depreciable or non-depreciable.

### Data Requirements for Each Disposition

For each property disposed of, the following data points are required for calculation:

*   **Municipal Address**: The full address of the property.
*   **Property Type**: Classification as either depreciable (e.g., rental building) or non-depreciable (e.g., land).
*   **Date of Disposition**: The date the property was sold.
*   **Proceeds of Disposition**: The gross amount received or to be received for the property.
*   **Adjusted Cost Base (ACB)**: The original cost of the property plus capital expenditures, minus capital returns and CCA claimed (for non-depreciable property, CCA is not claimed).
*   **Undepreciated Capital Cost (UCC)**: The tax value of the depreciable property at the beginning of the tax year. This is critical for depreciable property calculations.

---

### Calculation Logic and Scenarios

The tax treatment of the disposition is determined by the property type.

#### ### Scenario 1: Non-Depreciable Real Property

Dispositions of non-depreciable property (such as vacant land or a personal-use cottage) result in a capital gain or capital loss. This rule does not apply if the property is held as inventory (e.g., by a property developer).

*   **Calculation**:
    *   **Capital Gain**: `Proceeds of Disposition - Adjusted Cost Base (ACB)`
    *   **Capital Loss**: `Adjusted Cost Base (ACB) - Proceeds of Disposition`

*   **Example**:
    A taxpayer sells a parcel of land (non-depreciable property).
    *   Proceeds of Disposition: $200,000
    *   Adjusted Cost Base (ACB): $150,000
    *   **Result**: A capital gain of $50,000 ($200,000 - $150,000).

---

#### ### Scenario 2: Depreciable Real Property

Dispositions of depreciable property (such as a rental building) can result in three different outcomes: a capital gain, a recapture of Capital Cost Allowance (CCA), or a terminal loss. The outcome depends on the relationship between the proceeds of disposition, the original cost, and the UCC.

*   **Case A: Capital Gain**
    Occurs when the **Proceeds of Disposition** are greater than the **Original Cost** of the property.
    *   **Calculation**: The capital gain is `Proceeds of Disposition - Original Cost`. In addition, all CCA claimed over the years (`Original Cost - UCC`) is considered recaptured and must be included as income.

*   **Case B: Recapture of CCA**
    Occurs when the **Proceeds of Disposition** are less than the **Original Cost** but greater than the **UCC**.
    *   **Calculation**: The recapture amount is `Proceeds of Disposition - UCC`. This amount is added to business or property income for the year.

*   **Case C: Terminal Loss**
    Occurs when the **Proceeds of Disposition** are less than the **UCC**.
    *   **Calculation**: The terminal loss is `UCC - Proceeds of Disposition`. This amount is deductible from business or property income for the year.

*   **Example (Recapture)**:
    A taxpayer sells a rental building (depreciable property).
    *   Original Cost: $500,000
    *   UCC at beginning of year: $400,000
    *   Proceeds of Disposition: $450,000
    *   **Analysis**: The proceeds ($450,000) are less than the original cost ($500,000) but greater than the UCC ($400,000).
    *   **Result**: A recapture of CCA of $50,000 ($450,000 - $400,000). This amount is included as income.

---

### Final Reporting

After calculating the gain, recapture, or terminal loss for each disposed property, sum the results.

*   Enter the total net amount from all real estate dispositions at **Amount B** on the form.

### Reference
*   **IT-218, Profit, Capital Gains and Losses From the Sale of Real Estate, Including Farmland and Inherited Land and Conversion of Real Estate From Capital Property to Inventory and Vice Versa**
