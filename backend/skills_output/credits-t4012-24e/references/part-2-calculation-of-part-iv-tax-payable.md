# Section 68

**Chapter 68**

---

## Part IV Tax Calculation

### Reduction by Part IV.1 Tax

Part IV tax payable on a dividend is reduced by any amount of Part IV.1 tax payable on the same dividend. This reduction ensures that dividends are not subject to both taxes simultaneously.

**Example**: If a corporation receives a $10,000 dividend that would normally incur $1,333 in Part IV tax (at 13.33%), and the same dividend is subject to $800 in Part IV.1 tax, the net Part IV tax payable would be $533 ($1,333 - $800).

### Reduction Using Losses

Corporations can reduce the amount of dividends subject to Part IV tax by applying:

1. **Non-capital losses** incurred in the current tax year
2. **Non-capital losses** carried forward from previous years
3. **Farm losses** incurred in the current tax year
4. **Farm losses** carried forward from previous years

**Implementation Note**: When calculating Part IV tax, first determine the gross amount of dividends subject to tax, then apply available losses in the following order:
   1. Current year non-capital losses
   2. Current year farm losses
   3. Carried forward non-capital losses
   4. Carried forward farm losses

**Example**: A corporation receives $50,000 in taxable dividends and has $15,000 in non-capital losses from the current year and $10,000 in carried forward farm losses. The corporation can reduce its dividends subject to Part IV tax by $25,000 ($15,000 + $10,000), leaving only $25,000 subject to Part IV tax.

### Calculation Steps for Developers

1. Identify all dividends received during the tax year
2. Calculate gross Part IV tax payable (typically 33 1/3% of eligible dividends and 40% of non-eligible dividends)
3. Calculate Part IV.1 tax payable on the same dividends
4. Apply Part IV.1 tax reduction to Part IV tax
5. Apply available losses to reduce the dividend amount subject to Part IV tax
6. Calculate final Part IV tax payable
