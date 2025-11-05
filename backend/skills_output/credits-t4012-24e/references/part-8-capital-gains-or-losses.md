# Section 31

**Chapter 31**

---

## Part 8 – Capital Gains or Losses

### Line 875 – Capital Gains Dividends

**Definition and Tax Treatment:**
Capital gains dividends received from specific investment entities are treated as capital gains for tax purposes. These dividends are considered capital gains under the following sections of the Income Tax Act:
- Paragraphs 130.1(4)(a) and (b)
- Paragraphs 131(1)(a) and (b)

**Applicable Entities:**
These provisions specifically apply to:
- Mortgage Investment Corporations (MICs)
- Mutual Fund Corporations

**Reporting Requirements:**
If you received any capital gains dividends during the tax year, report the total amount on line 875.

**Practical Example:**
If you received $500 in capital gains dividends from a mutual fund corporation and $300 from a mortgage investment corporation, you would report a total of $800 on line 875.

**Implementation Notes for Developers:**
- Validate that the entity type is either a MIC or Mutual Fund Corporation before classifying dividends as capital gains dividends
- Ensure the system can track and sum capital gains dividends from multiple sources
- Provide clear labeling on tax forms to distinguish capital gains dividends from other types of dividends

### Line 880 – Capital Gains Reserve Balance

**Definition:**
This line represents the opening balance of the capital gains reserve as calculated on Schedule 13 of the tax return.

**Inclusion Requirements:**
The amount reported should include:
- The capital gains reserve balance at the beginning of the tax year
- Any amounts from the last tax year of predecessor corporations after amalgamation or wind-up

**Practical Example:**
If your corporation had a capital gains reserve of $10,000 at the end of the previous tax year, and it acquired another corporation through amalgamation that had a capital gains reserve of $5,000, you would report $15,000 on line 880.

**Implementation Notes for Developers:**
- Create a data field to track the opening balance of the capital gains reserve
- Implement logic to include reserves from predecessor corporations after corporate restructuring
- Ensure the system maintains historical data for accurate carry-forward calculations
- Provide validation to prevent negative values unless specifically allowed by tax regulations
