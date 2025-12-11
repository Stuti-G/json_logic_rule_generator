POLICY_DOCUMENTS = [
    """
    ## Credit Score Requirements
    
    Bureau score (credit score) is a critical factor in loan approval decisions.
    
    - **Minimum acceptable bureau score**: 600
    - **Good credit score**: Above 700
    - **Excellent credit score**: Above 750
    - **NTC (New to Credit)**: Applicants with no credit history require special consideration
    
    Applications with bureau scores below 550 should generally be flagged as high risk.
    For applicants between 550-600, additional documentation may be required.
    """,
    
    """
    ## Applicant Eligibility Criteria
    
    Primary applicant requirements:
    
    - **Minimum age**: 21 years
    - **Maximum age**: 65 years
    - **Preferred age range**: 25 to 55 years
    
    Monthly income thresholds:
    - Minimum monthly income for standard loans: ₹25,000
    - Minimum monthly income for premium loans: ₹1,00,000
    
    Veterans and government employees may receive preferential treatment.
    The 'veteran' tag in primary_applicant.tags indicates military service.
    """,
    
    """
    ## Business Vintage Requirements
    
    Business vintage (age of business) is an important stability indicator.
    
    - **Minimum vintage for standard loans**: 2 years
    - **Preferred vintage**: 3+ years
    - **New business**: Less than 1 year (higher risk)
    
    Businesses with vintage less than 1 year should be flagged for additional review.
    Commercial CIBIL score becomes more important for newer businesses.
    
    GST registration age (gst.registration_age_months) can serve as a proxy 
    for business vintage when formal business vintage data is unavailable.
    """,
    
    """
    ## High Risk Indicators
    
    The following conditions should trigger high-risk flagging:
    
    **Automatic rejection triggers:**
    - Wilful default (bureau.wilful_default = true)
    - Suit filed against borrower (bureau.suit_filed = true)
    
    **High risk flags:**
    - DPD (Days Past Due) >= 90 days
    - Overdue amount > ₹50,000
    - More than 5 recent credit enquiries
    - High supplier concentration (gst.supplier_concentration_ratio > 0.7)
    
    **Bounces:**
    - Inward bounces > 3 in last 6 months: Moderate risk
    - Outward bounces > 2 in last 6 months: High risk
    """,
    
    """
    ## Financial Ratios and Thresholds
    
    **FOIR (Fixed Obligation to Income Ratio):**
    - Acceptable FOIR: Less than 0.5 (50%)
    - Maximum FOIR for approval: 0.7 (70%)
    
    **Debt to Income:**
    - Healthy debt-to-income: Less than 0.4
    - Maximum acceptable: 0.6
    
    **Banking Analysis:**
    - ABB (Average Bank Balance) should be positive
    - Avg monthly turnover should be consistent with declared income
    - Total credits should reasonably exceed total debits for healthy cash flow
    """,
    
    """
    ## GST Compliance Requirements
    
    GST data provides valuable insights into business health:
    
    - **Missed returns**: More than 2 missed returns is a red flag
    - **Turnover growth**: Negative turnover growth rate requires investigation
    - **High risk suppliers**: Count > 3 indicates supply chain risk
    
    Customer concentration ratio above 0.8 indicates over-dependence on 
    single customers, which is a business continuity risk.
    
    GST turnover should align with banking turnover (within 20% variance).
    """
]


POLICY_SNIPPETS = [
    "Minimum bureau score for approval is 600 points.",
    "Business must be operational for at least 2 years (vintage >= 2).",
    "Applicant age must be between 21 and 65 years.",
    "Wilful defaulters are automatically rejected.",
    "DPD greater than 90 days indicates severe credit risk.",
    "FOIR should not exceed 70% for loan approval.",
    "Monthly income minimum is ₹25,000 for standard products.",
    "More than 3 inward bounces is a red flag.",
    "Bureau enquiries above 5 in recent months signals credit hunger.",
    "Commercial CIBIL score below 500 requires rejection.",
]


def get_all_policies() -> list:
    return POLICY_DOCUMENTS + POLICY_SNIPPETS


def get_detailed_policies() -> list:
    return POLICY_DOCUMENTS


def get_quick_snippets() -> list:
    return POLICY_SNIPPETS