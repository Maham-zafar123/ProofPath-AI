
# ProofPath AI — MVP

ProofPath AI helps students and fresh graduates prepare to defend the claims on their CV during interviews.

## MVP Features

- Demo login
- Upload CV in PDF, DOCX, or TXT format
- Detect common technical skills
- Highlight risky / important CV claims
- Generate personalized interview questions
- Let the user practice an answer
- Give simple actionable feedback
- Generate adaptive follow-up questions and feedback with the open-source `google/flan-t5-small` model

## Demo Credentials

Email: `demo@proofpath.ai`  
Password: `demo123`

## Run locally

```bash
pip install -r requirements.txt
streamlit run app.py
```

## Deploy on Streamlit Community Cloud

1. Create a GitHub repository.
2. Upload `app.py` and `requirements.txt`.
3. Go to Streamlit Community Cloud.
4. Click **Create app**.
5. Select your repository and `app.py`.
6. Deploy.
7. Copy the generated public URL into your Dafinitiq application.

## Product Roadmap

The MVP already uses the open-source `google/flan-t5-small` model for adaptive follow-up questions and answer feedback. A production version could later upgrade to a stronger open-source model such as Qwen.

## Suggested application text

**Product name:** ProofPath AI

**One-line pitch:**  
An AI-powered CV defense assistant that helps fresh graduates prepare to explain every skill, project, metric, and experience they claim on their CV.
