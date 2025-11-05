# Section 73

**Chapter 73**

---

## Part 2 of Schedule 43 – Dividend Allowance Allocation Among Associated Corporations

### Overview
Associated corporations must complete Part 2 of Schedule 43 to formally allocate the enhanced dividend refundable tax (DRD) allowance among group members. This allocation ensures proper distribution of tax benefits within the corporate group structure.

### Key Requirements

#### Associated Group Definition
Corporations are considered associated when they meet any of the following criteria:
- One corporation controls the other
- Both corporations are controlled by the same person or group of persons
- Each corporation is controlled by a related person

#### Allocation Process
1. **Determine Total Allowance**: Calculate the combined dividend allowance for the entire associated group
2. **Execute Allocation Agreement**: Complete Part 2 of Schedule 43 to distribute the allowance
3. **File with T2 Returns**: Each corporation must file their respective T2 return with the allocation agreement

### Implementation Examples

#### Example 1: Simple Two-Corporation Allocation
```
Corporation A: 60% ownership
Corporation B: 40% ownership
Total Dividend Allowance: $50,000

Allocation:
- Corporation A: $30,000 (60%)
- Corporation B: $20,000 (40%)
```

#### Example 2: Multi-Corporation Complex Structure
```
Parent Corp (100% control)
├── Subsidiary A (70% ownership)
├── Subsidiary B (20% ownership)
└── Subsidiary C (10% ownership)

Total Dividend Allowance: $100,000

Allocation:
- Parent Corp: $10,000 (10%)
- Subsidiary A: $70,000 (70%)
- Subsidiary B: $20,000 (20%)
- Subsidiary C: $0 (opted out via agreement)
```

### Technical Implementation for Developers

#### Data Structure Requirements
```json
{
  "schedule43_part2": {
    "corporation_id": "string",
    "associated_group_id": "string",
    "total_dividend_allowance": "decimal",
    "allocated_amount": "decimal",
    "allocation_percentage": "decimal",
    "agreement_date": "date",
    "signing_authority": {
      "name": "string",
      "title": "string",
      "signature": "string"
    }
  }
}
```

#### Validation Rules
1. Total allocations must equal 100% of the dividend allowance
2. All associated corporations must be included in the agreement
3. Allocation percentages must be consistent across all group members
4. Agreement must be signed by authorized representatives

#### Integration Points
- Link with T2 Corporation Income Tax Return filing system
- Connect to associated corporation relationship database
- Interface with CRA's digital submission protocols
- Implement audit trail for allocation changes

### Compliance Notes
- File Schedule 43 with the corporation that has the earliest tax year-end
- Maintain supporting documentation for allocation methodology
- Update agreements when corporate relationships change
- Retain records for minimum 7 years per CRA requirements
