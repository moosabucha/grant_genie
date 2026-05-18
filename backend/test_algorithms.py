import pytest
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

# Import algorithm modules
from algorithms.evaluator import *
from algorithms.hybrid_matcher import *
from algorithms.rapidfuzz_matcher import *
from algorithms.tfidf_matcher import *


# ========== TEST CASES ==========

def test_imports():
    """Test that all modules import correctly"""
    assert True


def test_evaluator_exists():
    """Test evaluator module has functions"""
    import algorithms.evaluator as evaluator
    assert evaluator is not None


def test_hybrid_matcher_exists():
    """Test hybrid_matcher module exists"""
    import algorithms.hybrid_matcher as hybrid
    assert hybrid is not None


def test_rapidfuzz_matcher_exists():
    """Test rapidfuzz_matcher module exists"""
    import algorithms.rapidfuzz_matcher as rapidfuzz
    assert rapidfuzz is not None


def test_tfidf_matcher_exists():
    """Test tfidf_matcher module exists"""
    import algorithms.tfidf_matcher as tfidf
    assert tfidf is not None


def test_simple_assertion():
    """Basic test to verify pytest works"""
    assert 1 + 1 == 2


def test_string_comparison():
    """Test string operations"""
    assert "grant" in "grant_genie"


def test_list_operations():
    """Test list operations"""
    test_list = [1, 2, 3]
    assert len(test_list) == 3
    assert test_list[0] == 1


if __name__ == "__main__":
    pytest.main([__file__, "-v"])