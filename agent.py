# ruff: noqa
# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import datetime
from zoneinfo import ZoneInfo

from google.adk.workflow import Workflow, START
from google.adk.agents import LlmAgent
from google.adk.events.event import Event
from google.adk.models import Gemini
from google.adk.apps import App
from google.adk.agents.context import Context
from google.genai import types
from pydantic import BaseModel, Field

import os
import google.auth
from google.auth.exceptions import DefaultCredentialsError

try:
    from dotenv import load_dotenv
    load_dotenv()
except ImportError:
    pass

try:
    _, project_id = google.auth.default()
    os.environ["GOOGLE_CLOUD_PROJECT"] = project_id or "dummy-project"
    os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "True"
except Exception:
    os.environ["GOOGLE_CLOUD_PROJECT"] = "dummy-project"
    # Fallback to AI Studio if no GCP credentials found
    if "GEMINI_API_KEY" in os.environ:
        os.environ["GOOGLE_GENAI_USE_VERTEXAI"] = "False"

os.environ["GOOGLE_CLOUD_LOCATION"] = "global"


class Classification(BaseModel):
    is_shipping_related: bool = Field(
        description="True if the user query is related to shipping (rates, tracking, delivery, returns), False otherwise"
    )


def save_query(node_input: types.Content) -> Event:
    query_text = ""
    if node_input and node_input.parts:
        query_text = "".join([part.text for part in node_input.parts if part.text])
    return Event(
        output=query_text,
        state={"user_query": query_text},  # type: ignore
    )


classifier_agent = LlmAgent(
    name="classifier_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=(
        "You are an assistant for a shipping company. "
        "Your task is to classify whether the user query is related to shipping (rates, tracking, delivery, returns) or unrelated. "
        "Set `is_shipping_related` to True if it is shipping-related, and False if it is unrelated."
    ),
    output_schema=Classification,
)


def router(ctx: Context, node_input: dict) -> Event:
    is_shipping = node_input.get("is_shipping_related", False)
    user_query = ctx.state.get("user_query", "")
    if is_shipping:
        return Event(
            output=user_query,
            route="shipping",  # type: ignore
        )
    return Event(
        output=user_query,
        route="unrelated",  # type: ignore
    )


shipping_faq_agent = LlmAgent(
    name="shipping_faq_agent",
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(attempts=3),
    ),
    instruction=(
        "You are a helpful customer support representative for a shipping company. "
        "Answer the user's question about shipping (rates, tracking, delivery, returns) politely and accurately."
    ),
)


def decline_node(node_input: str):
    response_text = "I'm sorry, but I can only assist with shipping-related inquiries such as rates, tracking, delivery, and returns. How can I help you with your shipping needs today?"
    yield Event(
        content=types.Content(
            role="model", parts=[types.Part.from_text(text=response_text)]
        )
    )
    yield Event(output=response_text)


root_agent = Workflow(
    name="customer_support_agent",
    edges=[
        (START, save_query),
        (save_query, classifier_agent),
        (classifier_agent, router),
        (router, {"shipping": shipping_faq_agent, "unrelated": decline_node}),
    ],
)

app = App(
    root_agent=root_agent,
    name="app",
)
