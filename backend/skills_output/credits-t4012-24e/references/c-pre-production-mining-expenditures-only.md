# Section 58

**Chapter 58**

---

## Investment Tax Credits (ITCs)

### Eligible Expenditures for ITC Claims

#### C. Pre-production Mining Expenditures
- **Note**: Only carry-forward amounts are allowed for claiming
- These expenditures must be related to mining activities before commercial production begins
- Typical expenses include exploration, development, and construction of mining infrastructure
- **Implementation Tip**: Track the original year of expenditure to calculate carry-forward periods correctly

#### D. Apprenticeship Expenditures
- Eligible expenses include wages paid to eligible apprentices
- Must be registered apprentices in a designated trade under the Apprenticeship and Certification Act
- Maximum credit of $2,000 per eligible apprentice per year
- **Implementation Tip**: Validate apprentice registration numbers and track annual wage payments per apprentice

#### E. Eligible Child Care Space Expenditures
- **Note**: Only carry-forward amounts are allowed for claiming
- Applies to businesses that create licensed child care spaces for employees
- Eligible expenses include construction, renovation, and equipment costs
- **Implementation Tip**: Track licensing information and categorize expenses by construction, renovation, and equipment

### Clean Economy ITCs
- For information on clean economy Investment Tax Credits, see Line 780 on page 135 of the T2 Corporation Income Tax Guide
- **Implementation Tip**: Create a separate module for clean economy ITCs as they have distinct eligibility criteria

### Definitions of Qualified Investments and Expenditures

#### A. Qualified Property
- **Definition**: As defined in subsection 127(9) of the Income Tax Act
- **Includes**: 
  - New prescribed buildings
  - Prescribed machinery and equipment
  - Prescribed energy and conservation property
- **Requirements**: Must be acquired during the tax year for use in specific activities in:
  - Newfoundland and Labrador
  - Nova Scotia
  - Prince Edward Island
  - New Brunswick
  - The Gaspé Peninsula
  - Prescribed offshore regions (collectively known as the Atlantic region)
- **Implementation Tip**: Implement regional validation to ensure property is located in eligible areas

#### A.1 Qualified Resource Property
- **Definition**: As defined in subsection 127(9) of the Income Tax Act
- **Status**: This credit expired on December 31, 2015
- **Transitional Measures**: Expired on December 31, 2016
- **Carry-forward Provision**: Unused credits can be carried forward for up to 20 tax years following the year of investment
- **Implementation Tip**: 
  - Block new claims for this credit
  - Implement date validation to ensure carry-forward claims are within the 20-year window
  - Example: If investment was made in 2015, carry-forward claims must be made by the end of 2035

#### B. Qualified Expenditure and SR&ED Qualified Expenditure Pool
- **Definition**: As defined in subsection 127(9) of the Income Tax Act
- **Related Definition**: Scientific Research and Experimental Development (SR&ED) is defined in subsection 248(1) of the Income Tax Act
- **Purpose**: These expenditures qualify for the Scientific Research and Experimental Development (SR&ED) Investment Tax Credit
- **Implementation Tip**: Create a separate pool tracking mechanism for SR&ED expenditures with proper categorization

### Implementation Notes for Developers
- When building tax applications, ensure proper tracking of carry-forward amounts for expired credits
- Implement validation checks for regional eligibility of qualified property
- Create separate tracking mechanisms for different types of expenditures with varying carry-forward rules
- Consider the 20-year carry-forward limitation for qualified resource property when implementing date calculations
- Implement proper error handling for claims made after credit expiration dates
- Consider creating a credit eligibility matrix to quickly determine which credits are available based on tax year and expenditure type
