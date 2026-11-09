
import os
import json
import time

from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.5-flash-lite"
)


def evaluate_answer(
    question,
    answer,
    category="Python",
    difficulty="Medium"
):

    if not GEMINI_API_KEY:
        raise ValueError("Gemini API key is missing.")

    if not answer or not answer.strip():
        raise ValueError("Please provide an answer.")

    client = genai.Client(
        api_key=GEMINI_API_KEY,
        http_options=types.HttpOptions(timeout=60000)
    )

    prompt = f"""
You are an experienced technical and HR interview evaluator.

Evaluate the candidate's answer fairly.

Category: {category}
Difficulty: {difficulty}

Interview Question:
{question}

Candidate Answer:
{answer}

Evaluate these areas:
1. Correctness
2. Relevance to the question
3. Completeness
4. Technical understanding
5. Clarity of explanation

Important rules:
- Give marks based on the actual answer.
- Do not give high marks for irrelevant answers.
- Do not invent facts.
- Be constructive and encouraging.
- Match expectations to the selected difficulty.
- Give a better sample answer.

Return valid JSON only in this format:

{{
    "score": 7,
    "summary": "Short overall assessment",
    "strengths": [
        "Strength 1"
    ],
    "improvements": [
        "Improvement 1"
    ],
    "ideal_answer": "A clear and correct sample answer",
    "verdict": "Good"
}}

Score must be between 0 and 10.

Verdict must be one of:
Excellent, Good, Average, Needs Improvement.
"""

    start = time.perf_counter()

    response = None

    # Retry temporary Gemini errors
    for attempt in range(3):

        try:

            response = client.models.generate_content(
                model=GEMINI_MODEL,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2,
                    max_output_tokens=550,
                    response_mime_type="application/json"
                )
            )

            break

        except Exception as error:

            error_message = str(error)

            temporary_error = any(
                code in error_message
                for code in ["503", "429", "500", "UNAVAILABLE"]
            )

            if temporary_error and attempt < 2:

                wait_time = 2 ** (attempt + 1)

                print(
                    f"Gemini temporarily unavailable. "
                    f"Retrying in {wait_time} seconds..."
                )

                time.sleep(wait_time)

            elif temporary_error:

                raise RuntimeError(
                    "Gemini is temporarily busy. "
                    "Please try again in a minute."
                ) from error

            else:

                raise

    print(
        "Gemini response time:",
        round(time.perf_counter() - start, 2),
        "seconds"
    )

    if response is None or not response.text:
        raise ValueError("Gemini returned an empty response.")

    try:
        result = json.loads(response.text)

    except json.JSONDecodeError as error:
        raise ValueError(
            "Gemini returned an invalid evaluation response. "
            "Please try again."
        ) from error

    required_fields = [
        "score",
        "summary",
        "strengths",
        "improvements",
        "ideal_answer",
        "verdict"
    ]

    for field in required_fields:
        if field not in result:
            raise ValueError(
                f"Gemini response is missing: {field}"
            )

    score = float(result["score"])

    if not 0 <= score <= 10:
        raise ValueError("Invalid score returned.")

    if result["verdict"] not in [
        "Excellent",
        "Good",
        "Average",
        "Needs Improvement"
    ]:
        raise ValueError("Invalid verdict returned.")

    result["score"] = score

    return result
