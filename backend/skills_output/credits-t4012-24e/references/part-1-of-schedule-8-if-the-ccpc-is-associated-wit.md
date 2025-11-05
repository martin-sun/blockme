# Section 34

**Chapter 34**

---

## Schedule 8: Capital Cost Allowance (CCA) Calculations

### Part 1: CCPC and EPOP Considerations

For Canadian-Controlled Private Corporations (CCPCs) associated with Eligible Persons or Partnerships (EPOPs):

#### Special Rules for CCPCs with EPOP Associations
- **Nil amount applies** when:
  - Total percentages assigned in the agreement exceed 100%, OR
  - CCPC has not filed the agreement in prescribed form under subsection 1104(3.3) of the Regulations

- **Special calculations required** for:
  - Second or subsequent tax years ending in a calendar year when CCPC has multiple tax years ending in that calendar year and is associated with another EPOP with a tax year ending in that calendar year
  - Amounts allocated by the minister under subsection 1104(3.4) of the Regulations

#### Immediate Expensing Limit Proration
The immediate expensing limit must be prorated if your tax year is less than 365 days.

**Reference:** Regulations 1100(0.1) and 1104(3.1) to (3.6)

---

### Schedule 8 Column Explanations

#### Column 13 – Cost of Acquisitions on Remainder of Class
Represents the cost of acquisitions not eligible for immediate expensing incentive, including:
- Properties that are not DIEP
- DIEPs that have exceeded the immediate expensing deduction for the tax year

**Calculation:**
```
Column 13 = Column 3 - Column 12
```

#### Column 14 – Cost of AIIP and Properties in Classes 54-56
Enter the total cost of Accelerated Investment Incentive Property (AIIP) or properties in classes 54-56 acquired during the year.

**AIIP Definition:**
Property (excluding classes 54-56) acquired after November 20, 2018, that becomes available for use before 2028.

**Reference:** Regulation 1104(4), Schedule II of the Regulations

#### Column 15 – Remaining UCC
Represents the remaining Undepreciated Capital Cost (UCC) after applying the immediate expensing deduction.

**Calculation:**
```
Column 15 = Column 10 - Column 12
```

**Reference:** Regulation 1100(0.2)

#### Column 16 – Proceeds of Disposition for AIIP
When you purchase both AIIP/non-AIIP properties and a disposition occurs, the disposition first offsets non-AIIP properties, then reduces the UCC of AIIP.

**Calculation:**
```
Column 16 = Column 8 + Column 6 - Column 13 + Column 14 - Column 7
```

**Reference:** Regulation 1100(2)

#### Column 17 – Net Capital Cost Additions of AIIP
**Calculation:**
```
Column 17 = Column 14 - Column 16
```

#### Column 18 – UCC Adjustment for AIIP
Adjust the remaining UCC to include an accelerated CCA component for AIIP and properties in classes 54-56.

**Calculation:**
```
Column 18 = Column 17 × 0.5 (unless different factor applies)
```

#### Column 19 – UCC Adjustment for Other Properties (50% Rule)
Generally, property acquired during the tax year is only eligible for 50% of normal maximum CCA.

**Exceptions to 50% rule:**
- AIIP and properties in classes 54-56
- Properties acquired through non-arm's length transfers
- Properties acquired through butterfly transfers

**Calculation:**
```
Column 19 = (Column 13 - Column 14 - Column 6 + Column 7 - Column 8) × 0.5
```

**References:** Regulations 1100(2) and 1100(2.2)

#### Column 20 – CCA Rate
Enter the prescribed rate for declining balance method. For straight-line method assets, enter N/A.

**Declining Balance Method Example:**
- Asset cost: $780,000
- Rate: 10% with half-year rule
- First year: $780,000 × 10% ÷ 2 = $39,000 CCA
- Second year: ($780,000 - $39,000) × 10% = $74,100 CCA

#### Column 21 – Recapture of CCA
Enter recapture amount from column 10. Include as income on line 107 of Schedule 1.

**Note:** Recapture rules don't apply to passenger vehicles in class 10.1, but do apply to passenger vehicles that were DIEP.

**References:** Subsections 13(1) and 13(2)

#### Column 22 – Terminal Loss
Enter terminal loss from column 10. Deduct from income on line 404 of Schedule 1.

**Terminal loss rules don't apply to:**
- Passenger vehicles in class 10.1
- Property in class 14.1 (unless business discontinued)
- Limited-period franchises in class 14 (with certain conditions)

**Reference:** Subsection 20(16.1)

#### Column 23 – CCA
**Maximum CCA Calculation (declining balance):**
```
CCA = (Column 15 + Column 18 - Column 19) × Column 20 + Column 12
```

**Short Tax Year Adjustment:**
For tax years less than 365 days, prorate CCA claim (except for excluded classes):
```
Prorated CCA = Maximum CCA × (Days in tax year ÷ 365)
```

**Excluded Classes:** 14, 15, timber limits, cutting rights, industrial mineral mines, certified productions, Canadian film/video productions, certain mining equipment

**Reference:** Regulation 1100(3)

#### Column 24 – UCC at End of Year
**Calculation:**
```
Column 24 = Column 10 - Column 23
```

When recapture or terminal loss occurs, UCC at year-end is always nil.

---

### Practical Examples

#### Example 1: Terminal Loss
A manufacturing business sells its warehouse for $60,000. At year-end, it has no more assets in class 3. Beginning UCC was $65,000.

**Result:** $5,000 terminal loss (deducted on line 404 of Schedule 1)

#### Example 2: Recapture of CCA
A clothing company sells a sewing machine for $18,000 (capital cost $15,000). Beginning UCC was $6,720.

**Result:** $8,280 recapture (included in income on line 107 of Schedule 1)

#### Example 3: 50% Rule
A bookstore buys a photocopier for $10,000 from a non-arm's length person. Beginning UCC was $14,000.

**Calculation:**
- Column 19 adjustment: ($10,000 - $0 - $0 + $0 - $0) × 0.5 = $5,000
- Maximum CCA: ($24,000 + $0 - $5,000) × 20% = $3,800

#### Example 4: Accelerated Investment Incentive Property
A grocery store buys refrigeration equipment for $20,000 (AIIP). Beginning UCC was $45,000.

**Calculation:**
- Column 18 adjustment: $20,000 × 0.5 = $10,000
- Maximum CCA: ($65,000 + $10,000 - $0) × 20% = $15,000

#### Example 5: AIIP and Non-AIIP
A potato producer buys tractors for $200,000, including $50,000 non-AIIP. Beginning UCC was $450,000.

**Calculation:**
- Column 18 adjustment: $150,000 × 0.5 = $75,000
- Column 19 adjustment: ($50,000 - $0 - $0 + $0 - $0) × 0.5 = $25,000
- Maximum CCA: ($650,000 + $75,000 - $25,000) × 30% = $210,000

#### Example 6: Designated Immediate Expensing Property (DIEP)
A new CCPC buys eligible machinery for $1.2 million. No EPOP associations.

**Calculation:**
- Immediate expensing: lesser of $1.5 million limit and $1.2 million UCC = $1.2 million
- CCA claim: $1.2 million (full expensing)

#### Example 7: DIEP and Non-DIEP
A corporation buys eligible machinery for $2.8 million, with $1.8 million qualifying as DIEP.

**Calculation:**
- Immediate expensing: $1.5 million (limit)
- Column 18 adjustment: $1.3 million × 0.5 = $650,000
- Maximum CCA: ($1.3 million + $650,000 - $0) × 30% = $585,000
- Total CCA: $585,000 + $1.5 million = $2,085,000

---

### Common CCA Classes and Rates

| Class | Description | Rate |
|-------|-------------|------|
| 1 | Buildings (brick, stone, cement) acquired after 1987 | 4% |
| 3 | Buildings acquired before 1988 | 5% |
| 6 | Frame buildings, fences, greenhouses | 10% |
| 8 | Furniture, equipment, tools ($500+), outdoor advertising | 20% |
| 9 | Aircraft and equipment | 25% |
| 10 | Vehicles, computers, electronic equipment | 30% |
| 10.1 | Passenger vehicles over cost limit | 30% |
| 12 | Small tools, software, certain rental property | 100% |
| 13 | Leasehold interests | n/a |
| 14 | Limited-period intangible property | n/a |
| 14.1 | Goodwill, trademarks, unlimited-period intangibles | 5% |
| 16 | Rental vehicles, taxis, heavy trucks | 40% |
| 17 | Roads, parking lots, communication equipment | 8% |
| 29 | Manufacturing equipment (2007-2016) | 50% |
| 43 | Manufacturing equipment (after 1992) | 30% |
| 43.1 | Clean energy equipment (10-90kW) | 30% |
| 43.2 | Clean energy equipment (2005-2025) | 50% |
| 44 | Patents and licences | 25% |
| 46 | Data network infrastructure | 30% |
| 50 | Computer equipment (after 2007) | 55% |
| 53 | Manufacturing equipment (2016-2026) | 50% |
| 54 | Zero-emission vehicles (not class 16/55) | 30% |
| 55 | Zero-emission vehicles (class 16 type) | 40% |
| 56 | Electric/hydrogen automotive equipment | 30% |
| 57 | CCUS capture/transport/storage equipment | 8% |
| 58 | CCUS utilization equipment | 20% |
| 59 | CCUS geological assessment intangibles | 100% |
| 60 | CCUS drilling intangibles | 30% |

---

### Related Schedules

#### Schedule 12: Resource-Related Deductions
Complete if claiming:
- Canadian exploration expenses (including CRCE)
- Canadian development expenses
- Canadian oil and gas property expenses
- Depletion
- Foreign exploration and development expenses
- Specified foreign exploration and development expenses
- Foreign resource expenses

**Accelerated Investment Incentive:**
Available for eligible CDE and COGPE incurred after November 20, 2018, and before 2028 (phased out after 2023).

#### Schedule 13: Continuity of Reserves
Complete to show continuity of deductible reserves, including:
- Prior-year reserves
- Current-year reserves
- Reserves transferred from amalgamation or wind-up

If a reserve was deducted last year, add it to current-year income and establish a new reserve amount.
