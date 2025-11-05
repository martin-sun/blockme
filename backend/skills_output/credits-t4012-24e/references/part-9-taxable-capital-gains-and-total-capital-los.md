# Section 32

**Chapter 32**

---

## Part 9 – Taxable Capital Gains and Total Capital Losses

### Zero Inclusion Rate for Qualified Donations
Generally, a zero inclusion rate applies for capital gains arising as a result of a gift to qualified donees of:
- Securities listed on a designated stock exchange
- Shares or units of mutual funds
- Interests in segregated funds
- Prescribed debt obligations
- Environmentally sensitive land

**Important Note:** The zero inclusion rate is restricted to only part of the capital gain if the taxpayer is entitled to an advantage or benefit in respect of a gift.

**Implementation Note:** For tax calculation purposes, apply a 0% inclusion rate to eligible donation-related capital gains, unless an advantage or benefit is present, in which case calculate the appropriate reduced inclusion rate based on the benefit's value relative to the total gain.

### Reporting Capital Gains on Donated Securities
When completing this part:
- Line 895 requires the full amount of capital gains realized on donations of eligible securities to qualified donees
- This includes securities listed on designated stock exchanges, mutual fund shares/units, segregated fund interests, or prescribed debt obligations

**Example:** If a taxpayer donates publicly traded shares with an adjusted cost base of $5,000 and a fair market value of $15,000 to a registered charity, they would report the $10,000 capital gain on line 895, but with a zero inclusion rate, resulting in no taxable capital gain.

**Implementation Note:** When processing donation-related capital gains, first calculate the full capital gain (FMV - ACB), then apply the appropriate inclusion rate (0% for qualified donations without benefits).

### Flow-Through Share Class Property Donations
If you donate property to a qualified donee that is included in a flow-through share class of property, and you have an exemption threshold for the flow-through share class of property, you may be deemed to have an additional capital gain from the disposition of another capital property subject to the standard 50% inclusion rate.

**Implementation Note:** For flow-through share class property donations, check for exemption thresholds and apply the standard 50% inclusion rate to any deemed additional capital gains. The calculation should identify when a donation triggers a deemed disposition of other capital property.

### Adjusted Stub Period Accrual Amounts
Amounts under section 34.2 (the adjusted stub period accrual regime) that have the character of capital must be:
- Entered in this part of Schedule 6
- NOT reported on line 130 of Schedule 1

Since these amounts are deemed to be taxable capital gains/allowable capital losses under the rules in section 34.2, they require special handling in the calculation system.

**Implementation Note:** Ensure section 34.2 amounts with capital character are routed to Schedule 6, Part 9, not to Schedule 1, line 130. These amounts should be flagged during data processing to ensure proper routing.

### Developer Implementation Guidelines
For tax application developers implementing this section:

1. **Donation Detection**: Implement logic to identify when a capital property disposition qualifies as a donation to a qualified donee.

2. **Inclusion Rate Application**: Create a function to apply the appropriate inclusion rate:
   - 0% for qualified donations without benefits
   - Reduced rate for donations with benefits (calculate proportionally)
   - 50% for flow-through share class deemed dispositions

3. **Line 895 Calculation**: Ensure the full capital gain amount is calculated and reported, with the inclusion rate applied separately in the taxable capital gain calculation.

4. **Section 34.2 Routing**: Implement a flagging system to identify section 34.2 amounts with capital character and route them to Schedule 6, Part 9.

5. **Validation Rules**: Include validation to ensure:
   - Qualified donee verification
   - Proper classification of donated property
   - Correct application of exemption thresholds for flow-through shares
