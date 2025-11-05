# Section 82

**Chapter 82**

---

## Service Issue Resolution Process

### Escalation Path for Service-Related Issues
If you have not been able to resolve your service-related issue with a CRA employee, you can request to discuss the matter with the employee's supervisor. This is the first step in the formal escalation process.

### Filing a Service-Related Complaint
If the problem remains unresolved after speaking with a supervisor, you can file a formal service-related complaint by:
1. Completing Form RC193, Service Feedback
2. Submitting it through the official channel at canada.ca/cra-service-feedback

### Escalating to the Taxpayers' Ombudsperson
If you are not satisfied with how the CRA has handled your service-related complaint, you have the option to submit a complaint to the Office of the Taxpayers' Ombudsperson. This is an independent body that reviews complaints about CRA service.

## Reprisal Complaints

### When to File a Reprisal Complaint
If you have received a response regarding a previously submitted service complaint or a formal review of a CRA decision and believe you were not treated impartially by a CRA employee, you may submit a reprisal complaint.

### How to File a Reprisal Complaint
1. Complete Form RC459, Reprisal Complaint
2. Submit it through the official channel at canada.ca/cra-reprisal-complaints

## Due Date Considerations

### Payment Timing Rules
When a due date falls on a Saturday, Sunday, or public holiday recognized by the CRA, your payment is considered on time if the CRA receives it on or before the next business day.

For developers building tax applications, this means:
- Implement a holiday calendar check for CRA-recognized holidays
- Adjust due dates that fall on weekends or holidays to the next business day
- Display both the original due date and the effective payment deadline

For more information on important dates, visit canada.ca/important-dates-corporations.

## Non-Resident Corporation Enquiries

### Online Resources
For questions about non-resident corporation accounts, visit canada.ca/taxes-international-business

### Contact Information

#### Within Canada and Continental United States
- Phone: 1-800-959-5525
- Hours: Monday to Friday (except holidays), 9 am to 6 pm (local time)

#### From Outside Canada and Continental United States
- Phone: 613-940-8497
- Hours: Monday to Friday (except holidays), 9 am to 6 pm (Eastern Standard Time)
- Note: The CRA only accepts collect calls made through telephone operators. After your call is accepted by an automated response, you may hear a beep and notice a normal connection delay.

### Mailing Address
For written correspondence:
```
Sudbury Tax Centre
PO Box 20000, STN A
Sudbury ON P3A 5C1
```

For developers implementing contact functionality:
- Include both phone numbers with appropriate country codes
- Implement time zone conversion for international callers
- Display the mailing address in a format that can be easily copied or exported
- Consider adding a feature to check if today is a CRA-recognized holiday before displaying contact hours
