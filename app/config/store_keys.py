SAMPLE_STORE_KEYS = [
    {
        "value": "business.address.pincode",
        "label": "Business Pincode",
        "group": "business",
    },
    {"value": "business.address.state", "label": "Business State", "group": "business"},
    {
        "value": "business.vintage_in_years",
        "label": "Business Vintage In Years",
        "group": "business",
    },
    {
        "value": "business.commercial_cibil_score",
        "label": "Commercial Cibil Score",
        "group": "business",
    },
    {
        "value": "primary_applicant.age",
        "label": "Primary Applicant Age",
        "group": "primary_applicant",
    },
    {
        "value": "primary_applicant.monthly_income",
        "label": "Primary Applicant Monthly Income",
        "group": "primary_applicant",
    },
    {
        "value": "primary_applicant.tags",
        "label": "Primary Applicant Tags",
        "group": "primary_applicant",
    },
    {"value": "bureau.score", "label": "Bureau Score", "group": "bureau"},
    {"value": "bureau.is_ntc", "label": "Is New to Credit?", "group": "bureau"},
    {"value": "bureau.overdue_amount", "label": "Overdue Amount", "group": "bureau"},
    {"value": "bureau.dpd", "label": "DPD", "group": "bureau"},
    {"value": "bureau.active_accounts", "label": "Active Accounts", "group": "bureau"},
    {"value": "bureau.enquiries", "label": "Enquiries", "group": "bureau"},
    {"value": "bureau.suit_filed", "label": "Suit Filed", "group": "bureau"},
    {"value": "bureau.wilful_default", "label": "Wilful Default", "group": "bureau"},
    {"value": "banking.abb", "label": "ABB", "group": "banking"},
    {
        "value": "banking.avg_monthly_turnover",
        "label": "Avg Monthly Turnover",
        "group": "banking",
    },
    {"value": "banking.total_credits", "label": "Total Credits", "group": "banking"},
    {"value": "banking.total_debits", "label": "Total Debits", "group": "banking"},
    {"value": "banking.inward_bounces", "label": "Inward Bounces", "group": "banking"},
    {
        "value": "banking.outward_bounces",
        "label": "Outward Bounces",
        "group": "banking",
    },
    {
        "value": "gst.registration_age_months",
        "label": "Registration Age Months",
        "group": "gst",
    },
    {
        "value": "gst.place_of_supply_count",
        "label": "Place Of Supply Count",
        "group": "gst",
    },
    {"value": "gst.is_gstin", "label": "Is GSTIN", "group": "gst"},
    {"value": "gst.filing_amount", "label": "Filing Amount", "group": "gst"},
    {"value": "gst.missed_returns", "label": "Missed Returns", "group": "gst"},
    {
        "value": "gst.monthly_turnover_avg",
        "label": "Monthly Turnover Avg",
        "group": "gst",
    },
    {"value": "gst.turnover", "label": "Turnover", "group": "gst"},
    {
        "value": "gst.turnover_growth_rate",
        "label": "Turnover Growth Rate",
        "group": "gst",
    },
    {
        "value": "gst.output_tax_liability",
        "label": "Output Tax Liability",
        "group": "gst",
    },
    {
        "value": "gst.tax_paid_cash_vs_credit_ratio",
        "label": "Tax Paid Cash Vs Credit Ratio",
        "group": "gst",
    },
    {
        "value": "gst.high_risk_suppliers_count",
        "label": "High Risk Suppliers Count",
        "group": "gst",
    },
    {
        "value": "gst.supplier_concentration_ratio",
        "label": "Supplier Concentration Ratio",
        "group": "gst",
    },
    {
        "value": "gst.customer_concentration_ratio",
        "label": "Customer Concentration Ratio",
        "group": "gst",
    },
    {"value": "itr.years_filed", "label": "Years Filed", "group": "itr"},
    {"value": "foir", "label": "FOIR", "group": "metrics"},
    {"value": "debt_to_income", "label": "Debt To Income", "group": "metrics"},
]


def get_keys_by_group(group: str) -> list:
    return [key for key in SAMPLE_STORE_KEYS if key["group"] == group]


def get_all_values() -> list:
    return [key["value"] for key in SAMPLE_STORE_KEYS]


def get_key_by_value(value: str) -> dict | None:
    for key in SAMPLE_STORE_KEYS:
        if key["value"] == value:
            return key
    return None


VALID_KEY_VALUES = set(get_all_values())


def is_valid_key(value: str) -> bool:
    return value in VALID_KEY_VALUES
