import os
import base64
from typing import Generic, TypeVar

from dotenv import load_dotenv
from pydantic import BaseModel, Field
from langchain_google_genai import ChatGoogleGenerativeAI


# ==========================================================
# 1. Load environment variables
# ==========================================================

load_dotenv()

GOOGLE_API_KEY = os.getenv("GEMINI_API_KEY")

if not GOOGLE_API_KEY:
    raise ValueError("GEMINI_API_KEY is not set.")


# ==========================================================
# 2. Pydantic base schema
# ==========================================================

T = TypeVar("T")


class ConfidenceScore(BaseModel, Generic[T]):
    reason: str = Field(
        description="reason of finding on each field"
    )
    # value: T = Field(description="Extracted value")
    confidence: float = Field(
        ge=0,
        le=100,
        description="Confidence score between 00 and 100",
    )


class ConfidenceScore(BaseModel, Generic[T]):
    confidence: float = Field(
        ge=0,
        le=100,
        description="Confidence score between 00 and 100",
    )



# ==========================================================
# 3. Initialize Gemini
# ==========================================================

llm = ChatGoogleGenerativeAI(
    model="gemini-3.5-flash",
    temperature=0,
    google_api_key=GOOGLE_API_KEY,
    # top_k=1
)


# ==========================================================
# 4. System prompt
# ==========================================================

system_prompt = """

# ■ CONFIDENCE SCORE RULES

If a field has no value, don't give it a confidence score. Leave it blank. Never write 0 for an empty field — 0 means something was read poorly, not that nothing is there.

If a field has a value, score it by going through the 5 checks below, one at a time. Each check has its own point deduction. Add up all 5 deductions and subtract the total from 100 to get the final confidence score.

---

## Check 1 — Look at the image quality

Look at this field's own region in the image. Is it sharp, or does it have blur, glare, shadow, or low resolution?

- Clean and sharp → deduct 0
- A little soft or slightly unclear, still readable → deduct 10
- Noticeably blurry, glare, or shadow, harder to read → deduct 20
- Very blurry or badly obscured, only readable with real effort → deduct 30

---

## Check 2 — Look for faded characters

Go through the value character by character. Count how many characters look faded, light, or low-contrast compared to the rest.

- No faded characters → deduct 0
- 1 faded character → deduct 10
- 2 faded characters → deduct 20
- 3 or more faded characters → deduct 30

---

## Check 3 — Look for characters that could be mistaken for a different character

Go through the value again. This time, count how many characters could plausibly be read as a different character (similar shape, similar stroke pattern).

- No ambiguous characters → deduct 0
- 1 ambiguous character → deduct 10
- 2 ambiguous characters → deduct 20
- 3 or more ambiguous characters → deduct 40

---

## Check 4 — Check if the value stays inside its box

Look at the field's border or box outline. Does the value stay fully inside it, or does part of it sit on or outside the border?

- Fully inside, no issue → deduct 0
- Touches the border but doesn't cross it → deduct 30
- Clearly extends outside or across the border → deduct 60

---

## Final Score

Add up the 4 deductions from Checks 1 through 4. Subtract that total from 100.

Confidence = 100 − (Check 1 + Check 2 + Check 3 + Check 4 )

Don't let the score go below 0. Don't let it go above 99.

Write out each check's deduction before writing the final number, so the score is traceable, for example:
"check-1(image quality): 0, Check 2 (faded characters): 8, Check 3 (ambiguous character): 0, Check 4(box/border check): 10 → 100 − 18 = 82"

Do this separately for every field. A field's score should come only from what you actually found for that field in the 5 checks above — don't copy a score from one field to another.


"""



# ==========================================================
# 5. Convert image to Base64
# ==========================================================

def image_to_base64(image_path: str) -> str:
    with open(image_path, "rb") as image_file:
        return base64.b64encode(
            image_file.read()
        ).decode("utf-8")


# ==========================================================
# 6. Build schema from the latest DB record
# ==========================================================

def get_latest_schema_data() -> dict:
    from .models import OcrSchemaRecord

    record = OcrSchemaRecord.objects.last()
    if record is None:
        raise ValueError(
            "No schema record found in the database. "
            "Create one first via POST /api/schema-records/."
        )
    return record.schema_data



def get_ocr_schema(data: dict):

    class ApplicantInfo(BaseModel):
        client_code: ConfidenceScore = Field(description=data["applicant_info"]["fields"]["client_code"]["description"])
        consignor_name: ConfidenceScore = Field(description=data["applicant_info"]["fields"]["consignor_name"]["description"])
        applicant_name: ConfidenceScore = Field(description=data["applicant_info"]["fields"]["applicant_name"]["description"])
        application_number: ConfidenceScore = Field(description=data["applicant_info"]["fields"]["application_number"]["description"])
        contract_holder: ConfidenceScore = Field(description=data["applicant_info"]["fields"]["contract_holder"]["description"])
        contract_holder_kana: ConfidenceScore = Field(description=data["applicant_info"]["fields"]["contract_holder_kana"]["description"])

    class BankAccountInfo(BaseModel):
        bank_type: ConfidenceScore = Field(description=data["bank_accounts"]["fields"]["bank_type"]["description"])
        account_holder_type: ConfidenceScore = Field(description=data["bank_accounts"]["fields"]["account_holder_type"]["description"])
        account_name_kana: ConfidenceScore = Field(description=data["bank_accounts"]["fields"]["account_name_kana"]["description"])
        account_name: ConfidenceScore = Field(description=data["bank_accounts"]["fields"]["account_name"]["description"])
        financial_institution_name: ConfidenceScore = Field(description=data["bank_accounts"]["fields"]["financial_institution_name"]["description"])
        financial_institution_type: ConfidenceScore = Field(description=data["bank_accounts"]["fields"]["financial_institution_type"]["description"])
        financial_institution_code: ConfidenceScore = Field(description=data["bank_accounts"]["fields"]["financial_institution_code"]["description"])
        branch_name: ConfidenceScore = Field(description=data["bank_accounts"]["fields"]["branch_name"]["description"])
        branch_name_type: ConfidenceScore = Field(description=data["bank_accounts"]["fields"]["branch_name_type"]["description"])
        branch_name_code: ConfidenceScore = Field(description=data["bank_accounts"]["fields"]["branch_name_code"]["description"])
        account_type: ConfidenceScore = Field(description=data["bank_accounts"]["fields"]["account_type"]["description"])
        account_number: ConfidenceScore = Field(description=data["bank_accounts"]["fields"]["account_number"]["description"])
        account_symbol: ConfidenceScore = Field(description=data["bank_accounts"]["fields"]["account_symbol"]["description"])

    class OcrSchema(BaseModel):
        title: str = Field(description=data["title"]["description"])
        applicant_info: ApplicantInfo = Field(description=data["applicant_info"]["description"])
        bank_accounts: BankAccountInfo = Field(description=data["bank_accounts"]["description"])

    return OcrSchema


# ==========================================================
# 7. Analyze image
# ==========================================================

def analyze_image(image_path: str):

    image_base64 = image_to_base64(image_path)

    schema_data = get_latest_schema_data()
    ocr_schema = get_ocr_schema(schema_data)
    structured_llm = llm.with_structured_output(ocr_schema)

    response = structured_llm.invoke(
        [
            (
                "system",
                system_prompt,
            ),
            (
                "human",
                [
                    {
                        "type": "text",
                        "text": (
                            "Analyze this image and extract all "
                            "required information according to the schema."
                        ),
                    },
                    {
                        "type": "image_url",
                        "image_url": (
                            f"data:image/png;base64,{image_base64}"
                        ),
                    },
                ],
            ),
        ]
    )

    return response


# # ==========================================================
# # 8. Run
# # ==========================================================

# if __name__ == "__main__":

#     # image_path = "/Users/alamin/contract-checker-backend/notebooks/test_images/makara_03_bank.jpg"
#     image_path = "/Users/alamin/contract-checker-backend/notebooks/test_images/new blur2.png"

#     result = analyze_image(image_path)

#     # # Pydantic object
#     # print("Pydantic result:")
#     # print(result)

#     # # Dictionary
#     # print("\nDictionary:")
#     # print(result.model_dump())

#     # JSON
#     print("\nJSON:")
#     print(result.model_dump_json(indent=2))
