# Section 35

**Chapter 35**

---

## Capital Gains Reserves

A capital gains reserve allows a taxpayer to defer a portion of a capital gain when the proceeds from the sale of a property are not due until after the end of the taxation year. This reserve is deducted in the year of sale and then brought back into income over a maximum of five years.

### Core Principles and Calculation Logic

#### 1. Continuity of Reserves per Property
A separate reserve calculation must be maintained for each distinct property disposed of. You cannot aggregate reserves from multiple properties into a single calculation. This continuity must be tracked year-over-year until the reserve is fully brought into income.

#### 2. Inclusion of Predecessor Corporation Reserves
Unlike other types of reserves, the calculation for the current year must include the total capital gains reserves deducted by both your corporation and its predecessor corporation in the preceding taxation year. This rule ensures continuity in situations involving corporate amalgamations or reorganizations.

#### 3. Calculation on Schedule 6
The net taxable capital gain for the year is calculated on `Schedule 6`. The fundamental logic is as follows:

1.  **Start** with the total capital gains realized in the current year.
2.  **Add back** the total reserve claimed in the previous year (by your corporation and its predecessor).
3.  **Subtract** the new reserve you are claiming for the current year.

The result is the capital gain to be included in income for the current year.

---

### Practical Example

**Scenario:** Your corporation sells a commercial building in 2023 for a $500,000 capital gain. The sale agreement stipulates that 20% of the proceeds ($100,000) are not payable until 2025. The maximum reserve claim is limited to the amount of proceeds not received.

**Year 1 (2023):**
*   **Total Capital Gain:** $500,000
*   **Maximum Reserve Allowed (20% of gain):** $100,000
*   **Calculation for Schedule 6:**
    *   Capital Gains: $500,000
    *   Add: Reserve from previous year (2022): $0
    *   Less: Reserve claimed for current year (2023): $100,000
*   **Taxable Capital Gain for 2023:** $400,000

**Year 2 (2024):**
*   No new capital gains are realized.
*   The reserve from 2023 must be added back into income. A new reserve can be claimed for the proceeds still not received (up to 2/5 of the original gain, which is $200,000, but limited to the outstanding proceeds).
*   **Calculation for Schedule 6:**
    *   Capital Gains: $0
    *   Add: Reserve from previous year (2023): $100,000
    *   Less: Reserve claimed for current year (2024): $100,000 (assuming proceeds are still not received)
*   **Taxable Capital Gain for 2024:** $0

**Year 3 (2025):**
*   The final payment is received. The remaining reserve must be brought into income.
*   **Calculation for Schedule 6:**
    *   Capital Gains: $0
    *   Add: Reserve from previous year (2024): $100,000
    *   Less: Reserve claimed for current year (2025): $0 (no proceeds outstanding)
*   **Taxable Capital Gain for 2025:** $100,000

---

### Implementation Guidance for Developers

#### Data Model Considerations
To accurately track and calculate capital gains reserves, your application should store the following data points for each disposition:
*   `propertyID`: A unique identifier for the disposed property.
*   `taxationYear`: The year of the sale.
*   `totalCapitalGain`: The full capital gain from the disposition.
*   `proceedsReceivedInYear`: The portion of proceeds received in the current year.
*   `outstandingProceeds`: The portion of proceeds not yet received.
*   `reserveClaimedCurrentYear`: The reserve amount calculated and claimed for the current year.
*   `reserveFromPreviousYear`: The reserve amount claimed in the preceding year (this must be fetched from the prior year's data for the same `propertyID`).

#### Calculation Algorithm
The core logic for calculating the taxable capital gain for a given property in a specific year can be represented as:

```javascript
// Pseudo-code for calculating taxable gain for a single property in a given year
function calculateTaxableCapitalGain(currentYearGain, previousYearReserve, currentYearReserve) {
  const taxableGain = (currentYearGain + previousYearReserve) - currentYearReserve;
  return Math.max(0, taxableGain); // Ensure the result is not negative
}

// The total taxable capital gain is the sum of this calculation across all properties.
```

#### Form Integration
The final calculated taxable capital gain for the corporation is the sum of the individual calculations for all properties. This aggregate value is reported on `Schedule 6` of the `T2 Corporation Income Tax Return`.

For detailed instructions and specific line references, consult the T2 Corporation Income Tax Guide.
