from app.analyzer.engine import analyze_ticket


def test_billing_refund_ticket_classification():
    result = analyze_ticket("I was charged twice and need a refund for last month invoice.")
    assert result["category"] == "Billing"
    assert result["priority"] in {"P1", "P2", "P3"}
    assert result["confidence"] >= 0.5


def test_technical_outage_priority():
    result = analyze_ticket("Production is down, outage is affecting all users. urgent")
    assert result["category"] == "Technical"
    assert result["priority"] == "P0"
    assert result["urgency"] == "High"


def test_account_login_issue():
    result = analyze_ticket("I cannot login to my account after resetting password.")
    assert result["category"] == "Account"
    assert result["priority"] in {"P1", "P2"}


def test_custom_security_override_rule():
    result = analyze_ticket("We suspect unauthorized access and possible data leak.")
    assert result["category"] == "Technical"
    assert result["priority"] == "P0"
    assert "custom:security_override" in result["signals"]


def test_other_category_fallback():
    result = analyze_ticket("Thanks for the good work, just sharing appreciation.")
    assert result["category"] == "Other"
    assert result["priority"] in {"P2", "P3"}
