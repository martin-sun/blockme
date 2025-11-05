# Section 27

**Chapter 27**

---

## Part 4 – Other Properties

This section requires reporting of capital property dispositions during the tax year that were not previously reported in Parts 1, 2, and 3.

### Types of Other Properties

#### Capital Debts Established as Bad Debts

When an amount receivable on a capital account becomes a bad debt and you elect to have subsection 50(1) applied on your return, a deemed disposition occurs at year-end. You are considered to have reacquired the debt immediately afterwards at a cost of nil.

**Tax Implications:**
- This election allows the corporation to claim a bad debt as a capital loss in the current year
- Any subsequent recovery of that debt will result in a capital gain

**Example:**
ABC Corp. had a $50,000 loan to XYZ Inc. that became uncollectible in 2023. By electing under subsection 50(1), ABC Corp. can claim a $50,000 capital loss in 2023. If XYZ Inc. later pays $30,000 of this debt in 2024, ABC Corp. must report a $30,000 capital gain in 2024.

**References:**
- Subsection 50(1)
- IT-159, Capital Debts Established to be Bad Debts

#### Bad Debts Related to Personal-Use Property

Under subsection 50(2), you can deduct capital losses for bad debts relating to the disposition of personal-use property to an arm's length person.

**Limitations:**
- The loss amount cannot exceed the gain previously reported on the disposition of the personal-use property

**Example:**
You sold a personal-use vehicle for $15,000 (original cost $20,000) to an arm's length person on credit. The buyer later defaults on the payment. You can claim a capital loss of up to $15,000 (the amount of the original disposition), not $20,000 (the original cost).

**Reference:**
- Subsection 50(2)

#### Foreign Currency Transactions

Foreign exchange gains or losses from buying or selling capital properties are treated as capital gains or capital losses.

**Application:**
- Transactions in foreign currency or foreign currency futures that are not part of business operations can be considered capital dispositions

**Example:**
A corporation purchases US stocks for $10,000 USD when the exchange rate is 1.25 CAD/USD (cost = $12,500 CAD). It later sells the stocks for $10,000 USD when the exchange rate is 1.35 CAD/USD (proceeds = $13,500 CAD). The corporation realizes a $1,000 capital gain from the foreign exchange fluctuation.

**References:**
- Subsection 39(2)
- IT-95, Foreign Exchange Gains and Losses

#### Partnership and Trust Allocations

Capital gains or losses allocated from partnerships and trusts must be reported in this section.

#### Depreciable Property Special Rules

For dispositions of depreciable property:
- A capital gain results if proceeds exceed the capital cost
- Losses on depreciable property do not result in capital losses but rather terminal losses

**Note:** See "Column 10 – UCC" (undepreciated capital cost) for information on terminal losses.

### Reporting Requirements

Enter the total amount of gain or loss realized on disposition of other properties at amount D.

**Implementation Notes for Developers:**
- Create separate input fields for each type of other property disposition
- Implement validation to ensure bad debt losses on personal-use property don't exceed original disposition proceeds
- Track foreign exchange rates at time of acquisition and disposition for accurate capital gain/loss calculation
- For depreciable property, implement logic to distinguish between capital gains and terminal losses
- Ensure proper categorization of partnership and trust allocations
