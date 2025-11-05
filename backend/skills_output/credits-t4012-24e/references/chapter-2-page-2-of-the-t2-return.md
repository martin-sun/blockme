# Section 13

**Chapter 13**

---

## T2 Corporation Income Tax Return: Credit-Related Schedules and Forms

### Overview of Credit-Related Attachments

The T2 Corporation Income Tax Return requires various schedules and forms to calculate and claim tax credits. These attachments fall into two main categories:

- **Information schedules**: Provide details about corporate structure and relationships that affect credit eligibility
- **Calculation schedules**: Used to calculate specific tax credits and limitations

### Key Schedules for Tax Credits

#### Schedule 23: Agreement Among Associated CCPCs to Allocate the Business Limit

**Purpose**: Allocates the small business deduction (SBD) business limit among associated Canadian-Controlled Private Corporations (CCPCs).

**Requirements**:
- All associated CCPCs must file Schedule 23
- Only one corporation needs to file for a calendar year
- Total allocation cannot exceed 100% of the maximum business limit ($500,000)

**Proration Rules**:
- For tax years shorter than 51 weeks, prorate based on days in tax year ÷ 365
- For multiple tax years in same calendar year, use lesser of:
  - Amount allocated for first tax year
  - Amount allocated for later tax year

**Example**:
```
Corp A and Corp B are associated in 2024.
Corp A's tax year: Jan 1, 2024 to June 30, 2024 (181 days)
Business limit allocated: $100,000

Prorated limit = $100,000 × (181 ÷ 365) = $49,589
```

#### Schedule 49: Agreement Among Associated CCPCs to Allocate the Expenditure Limit

**Purpose**: Allocates the expenditure limit for the 35% Scientific Research and Experimental Development (SR&ED) Investment Tax Credit (ITC).

**Requirements**:
- Required for all associated CCPCs with SR&ED expenditures
- Only one corporation needs to file for a calendar year
- Identifies all associated corporations and allocates expenditure limit

**Proration Rules**:
- For multiple tax years in same calendar year, prorate based on days in tax year ÷ 365
- Ensure prorated amounts equal allocation for first tax year in calendar year

### Other Schedules Impacting Credits

#### Schedule 9: Related and Associated Corporations

**Purpose**: Identifies corporate relationships that affect credit eligibility.

**Association Rules** (Corporations are associated if any apply):
1. One controls the other
2. Both controlled by same person/group
3. Each controlled by related persons with ≥25% cross-ownership
4. One controlled by person related to group controlling other
5. Each controlled by related groups with full member relationships
6. Associated with same third corporation (subsection 256(2))

**Example**:
```
Corp X owns 100% of Corp Y voting shares
Corp Y owns 51% of Corp Z voting shares

Result: Corp X associated with both Corp Y (direct) and Corp Z (indirect)
```

#### Schedule 28: Election Not to be Associated Through a Third Corporation

**Purpose**: Allows CCPCs to elect that two corporations associated through a third corporation are not associated for SBD purposes.

**Impact**:
- Third corporation's business limit becomes zero
- Investment income from other corporations ineligible for SBD
- Must file annually for each applicable tax year

#### Schedule 130: Excessive Interest and Financing Expenses Limitation (EIFEL)

**Purpose**: Limits deductible interest and financing expenses to 30% of adjusted taxable income (40% for transitional period).

**Applicability**:
- Tax years starting on or after October 1, 2023
- Excludes entities with:
  - Taxable capital < $50M (CCPCs and associated corporations)
  - Net interest expenses ≤ $1M
  - Limited non-resident ties

**Implementation Notes for Developers**:
1. Track association relationships throughout tax year
2. Implement proration calculations for short tax years
3. Handle multiple tax years ending in same calendar year
4. Validate total allocations don't exceed limits
5. Account for election filings (Schedule 28)
6. Apply EIFEL rules where applicable

### Reference Materials

- **Forms and Schedules**: Available at canada.ca/cra-forms-publications
- **GIFI Requirements**: See Guide RC4088
- **Technical Guides**: IT-64 (Corporations: Association and Control)
- **EIFEL Information**: canada.ca/cra-eifel

### Filing Requirements

- Attach applicable schedules when responding "yes" to related questions on T2 return pages 2-3
- File electronically to avoid paper financial statement requirements
- Maintain documentation for all credit calculations and allocations
- Respect filing deadlines to avoid penalties

For complete schedule listings and detailed requirements, refer to the T2 Corporation Income Tax Guide.
