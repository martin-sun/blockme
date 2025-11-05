# Section 24

**Chapter 24**

---

## Part 1 – Shares Disposition

### Data Structure for Developers
```json
{
  "shares_disposed": [
    {
      "number_of_shares": "integer",
      "corporation_name": "string",
      "share_class": "string",
      "proceeds_of_disposition": "decimal",
      "adjusted_cost_base": "decimal",
      "disposition_date": "date",
      "acquisition_date": "date",
      "ownership_percentage": "decimal",
      "dividends_received": "decimal",
      "business_of_trading_shares": "boolean",
      "reorganization_type": "enum[none, merger, amalgamation]"
    }
  ]
}
```

### Reporting Requirements
In this section, report all shares disposed of during the tax year with the following details:
- Number of shares disposed of
- Name of the corporation
- Class of shares

### Tax Treatment of Share Dispositions

#### Capital Gains/Losses
Typically, disposing of shares of a corporation's capital stock results in:
- Taxable capital gain (50% inclusion rate)
- Allowable capital loss (50% deductibility rate)

**Example:** ABC Corp. sells 1,000 shares of XYZ Inc. for $15,000. The shares had an adjusted cost base of $10,000. The capital gain is $5,000, with $2,500 (50%) being taxable.

**Developer Implementation:**
```javascript
function calculateCapitalGain(proceeds, acb) {
  const gain = proceeds - acb;
  return {
    totalGain: gain,
    taxableGain: gain > 0 ? gain * 0.5 : 0,
    allowableLoss: gain < 0 ? Math.abs(gain) * 0.5 : 0
  };
}
```

#### Business Income/Losses Exception
If the disposing corporation is in the business of trading shares, the disposition results in:
- Business income (for gains)
- Business loss (for losses)

**Example:** Trading Corp., which buys and sells securities as its primary business, sells shares resulting in a $10,000 gain. The full $10,000 is reported as business income, not as a capital gain.

**Developer Implementation:**
```javascript
function determineShareDispositionType(isTraderBusiness) {
  return isTraderBusiness ? 'business' : 'capital';
}
```

### Special Situations

#### Corporate Reorganizations
When shares are converted due to:
- Merger
- Amalgamation

Subsection 248(1) deems a disposition to have occurred for tax purposes.

**Example:** Company A merges with Company B, and shareholders of Company A receive shares of the new merged entity. For tax purposes, shareholders are deemed to have disposed of their Company A shares and acquired the new shares, potentially triggering capital gains or losses.

**Developer Implementation:**
```javascript
function isDeemedDisposition(reorganizationType) {
  return reorganizationType === 'merger' || reorganizationType === 'amalgamation';
}
```

#### Stop-Loss Rules
Under paragraph 112(3)(b), corporations must reduce losses from share dispositions when:
- The shares were held as capital property
- Certain dividends were received on those shares

This reduction prevents taxpayers from claiming both:
1. A capital loss on share disposition
2. A dividend deduction on the same shares

**Example:** Corp. X owns shares of Corp. Y and receives $5,000 in dividends. Later, Corp. X sells the shares at a $10,000 capital loss. Under the stop-loss rules, Corp. X must reduce its capital loss claim by the amount of dividends received, resulting in an allowable capital loss of only $5,000.

**Developer Implementation:**
```javascript
function applyStopLossRules(capitalLoss, dividendsReceived, ownershipPercentage, holdingPeriod) {
  // Check if stop-loss rules apply
  if (ownershipPercentage >= 0.05 || holdingPeriod <= 365) {
    const reducedLoss = Math.max(0, capitalLoss - dividendsReceived);
    return {
      originalLoss: capitalLoss,
      reducedLoss: reducedLoss,
      reductionAmount: capitalLoss - reducedLoss
    };
  }
  return {
    originalLoss: capitalLoss,
    reducedLoss: capitalLoss,
    reductionAmount: 0
  };
}
```

#### Exception to Stop-Loss Rules
The stop-loss rule generally does not apply when:
- The shareholder owns less than 5% of the shares
- The shares have been held for more than one year

**Example:** Individual investor owns 2% of Corp. Z's shares (held for 3 years) and receives dividends. When selling the shares at a loss, the stop-loss rules do not apply, and the full capital loss can be claimed.

### Reporting Instructions
1. Enter the total adjustment for losses identified in Part 1 on line 160
2. Enter the total amount of gain or loss realized on disposition of shares at amount A

**Developer Implementation:**
```javascript
function calculateReportingValues(sharesDisposed) {
  let totalGainLoss = 0;
  let totalAdjustment = 0;
  
  sharesDisposed.forEach(share => {
    const gainLoss = calculateCapitalGain(share.proceeds_of_disposition, share.adjusted_cost_base);
    totalGainLoss += gainLoss.totalGain;
    
    if (gainLoss.totalGain < 0) {
      const stopLossResult = applyStopLossRules(
        Math.abs(gainLoss.totalGain),
        share.dividends_received || 0,
        share.ownership_percentage || 0,
        calculateHoldingPeriod(share.acquisition_date, share.disposition_date)
      );
      totalAdjustment += stopLossResult.reductionAmount;
    }
  });
  
  return {
    amountA: totalGainLoss,
    line160Adjustment: totalAdjustment
  };
}
```

### Reference
IT-328, Losses on Shares on Which Dividends Have Been Received
