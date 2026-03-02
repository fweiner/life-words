"""Unit tests for plan constants."""
from app.constants.plans import PLAN_DETAILS


def test_plan_details_has_required_plans():
    """Test PLAN_DETAILS contains monthly and yearly plans."""
    assert "monthly" in PLAN_DETAILS
    assert "yearly" in PLAN_DETAILS


def test_plan_details_structure():
    """Test each plan has required fields."""
    for plan_key, plan in PLAN_DETAILS.items():
        assert "name" in plan
        assert "price" in plan
        assert "interval" in plan
        assert "description" in plan
        assert isinstance(plan["price"], (int, float))
        assert plan["price"] > 0
