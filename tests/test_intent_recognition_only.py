"""
Focused tests for intent recognition that add `src` to sys.path so imports work in CI/dev.
"""
import sys
import asyncio
import pytest

# Ensure 'src' is on sys.path so modules import correctly
import pathlib
ROOT = pathlib.Path(__file__).resolve().parents[1]
SRC = str(ROOT / 'src')
if SRC not in sys.path:
    sys.path.insert(0, SRC)

from nlp.intent_recognition import IntentRecognizer
from models import IntentType


def test_rule_based_greeting():
    recognizer = IntentRecognizer()
    pred = asyncio.run(recognizer.recognize_intent("Hello there, good morning!"))
    assert pred.intent in [IntentType.GREETING, IntentType.UNKNOWN]
    assert 0.0 <= pred.confidence <= 1.0


def test_rule_based_question():
    recognizer = IntentRecognizer()
    pred = asyncio.run(recognizer.recognize_intent("What can you do?"))
    assert pred.intent in [IntentType.QUESTION, IntentType.UNKNOWN]
    assert 0.0 <= pred.confidence <= 1.0
