# JSON Logic Rule Generator

An AI-powered API that converts natural language prompts into valid JSON Logic rules using embeddings and RAG (Retrieval-Augmented Generation).

## 🎯 What It Does

This API takes plain English descriptions like:

> "Approve if bureau score > 700 and business vintage at least 3 years and applicant age between 25 and 60"

And generates valid JSON Logic:

```json
{
  "and": [
    { ">": [{ "var": "bureau.score" }, 700] },
    { ">=": [{ "var": "business.vintage_in_years" }, 3] },
    {
      "and": [
        { ">=": [{ "var": "primary_applicant.age" }, 25] },
        { "<=": [{ "var": "primary_applicant.age" }, 60] }
      ]
    }
  ]
}
```

## 🚀 Features

- **Natural Language to JSON Logic**: Convert human-readable rules to machine-executable format
- **Semantic Key Mapping**: Uses embeddings to understand that "credit score" means `bureau.score`
- **RAG-Enhanced Generation**: Policy documents provide context for threshold values
- **Validation**: Ensures only allowed fields are used
- **Confidence Scoring**: Know how reliable the generated rule is

## 📁 Project Structure

```
json-logic-generator/
├── app/
│   ├── main.py                 # FastAPI application & endpoints
│   ├── config/
│   │   ├── store_keys.py       # Allowed field definitions
│   │   └── policy_docs.py      # RAG policy documents
│   └── services/
│       ├── embedding_service.py # Key matching with embeddings
│       ├── rag_service.py      # Policy retrieval
│       └── rule_generator.py   # LLM-based rule generation
├── tests/
│   ├── test_examples.py        # Integration tests
│   └── test_embedding_service.py # Unit tests
├── requirements.txt
├── .env.example
└── README.md
```

## 🛠️ Setup

### Prerequisites

- Python 3.10+
- Gemini API key

### Installation

1. **Clone and enter the directory**
   ```bash
   cd json-logic-generator
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env and add your GEMINI_API_KEY
   ```

### Running the Server

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at `http://localhost:8000`

**Interactive docs**: `http://localhost:8000/docs`

## 📡 API Endpoints

### POST /generate-rule

Generate a JSON Logic rule from natural language.

**Request:**
```bash
curl -X POST http://localhost:8000/generate-rule \
  -H "Content-Type: application/json" \
  -d '{
    "prompt": "Approve if bureau score > 700 and business vintage at least 3 years and applicant age between 25 and 60.",
    "context_docs": ["Optional additional policy context"]
  }'
```

**Response:**
```json
{
  "json_logic": {
    "and": [
      { ">": [{ "var": "bureau.score" }, 700] },
      { ">=": [{ "var": "business.vintage_in_years" }, 3] },
      {
        "and": [
          { ">=": [{ "var": "primary_applicant.age" }, 25] },
          { "<=": [{ "var": "primary_applicant.age" }, 60] }
        ]
      }
    ]
  },
  "explanation": "This rule approves applicants with a bureau score above 700, a business vintage of at least 3 years, and an age between 25 and 60 years.",
  "used_keys": ["bureau.score", "business.vintage_in_years", "primary_applicant.age"],
  "key_mappings": [
    { "user_phrase": "bureau score", "mapped_to": "bureau.score", "similarity": 0.9234 },
    { "user_phrase": "business vintage", "mapped_to": "business.vintage_in_years", "similarity": 0.8912 },
    { "user_phrase": "applicant age", "mapped_to": "primary_applicant.age", "similarity": 0.9156 }
  ],
  "confidence_score": 0.9101
}
```

### GET /keys

List all available fields.

```bash
curl http://localhost:8000/keys
```

### POST /find-keys

Debug endpoint to see key mappings without generating a rule.

```bash
curl -X POST "http://localhost:8000/find-keys?prompt=credit%20score%20above%20700&top_k=5"
```

## 🧪 Running Tests

**Unit tests:**
```bash
pytest tests/test_embedding_service.py -v
```

**Integration tests (server must be running):**
```bash
python tests/test_examples.py
```

## 📋 Example Prompts

### Example 1: Basic AND Conditions
```
Approve if bureau score > 700 and business vintage at least 3 years and applicant age between 25 and 60.
```

### Example 2: OR Conditions for Risk
```
Flag as high risk if wilful default is true OR overdue amount > 50000 OR bureau.dpd >= 90.
```

### Example 3: Tag Check
```
Prefer applicants with tag 'veteran' OR with monthly_income > 1,00,000.
```

### Example 4: GST Compliance
```
Reject if GST missed returns > 2 or high risk suppliers count > 3.
```

### Example 5: Financial Ratios
```
Approve if FOIR is less than 0.5 and debt to income ratio below 0.4.
```

## 🔑 Supported Fields

| Group | Field | Description |
|-------|-------|-------------|
| **bureau** | bureau.score | Bureau/CIBIL Score |
| | bureau.dpd | Days Past Due |
| | bureau.wilful_default | Wilful Default Flag |
| | bureau.overdue_amount | Overdue Amount |
| | bureau.is_ntc | New to Credit Flag |
| | bureau.enquiries | Credit Enquiries |
| | bureau.suit_filed | Suit Filed Flag |
| | bureau.active_accounts | Active Accounts Count |
| **business** | business.vintage_in_years | Business Age in Years |
| | business.commercial_cibil_score | Commercial CIBIL Score |
| | business.address.state | Business State |
| | business.address.pincode | Business Pincode |
| **primary_applicant** | primary_applicant.age | Applicant Age |
| | primary_applicant.monthly_income | Monthly Income |
| | primary_applicant.tags | Applicant Tags (array) |
| **banking** | banking.abb | Average Bank Balance |
| | banking.avg_monthly_turnover | Monthly Turnover |
| | banking.inward_bounces | Inward Bounces |
| | banking.outward_bounces | Outward Bounces |
| **gst** | gst.turnover | GST Turnover |
| | gst.missed_returns | Missed GST Returns |
| | gst.registration_age_months | GST Registration Age |
| **metrics** | foir | Fixed Obligation to Income Ratio |
| | debt_to_income | Debt to Income Ratio |

See `app/config/store_keys.py` for the complete list.


## 🔧 Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Your Gemini API key | Required |
| `GEMINI_MODEL` | Model to use | gemini-2.5-flash |

### Customization

- **Add new fields**: Edit `app/config/store_keys.py`
- **Add policy documents**: Edit `app/config/policy_docs.py`
- **Adjust embedding model**: Change `model_name` in `EmbeddingService`

## 📝 License

MIT

## 🤝 Contributing

Feel free to open issues or submit PRs!