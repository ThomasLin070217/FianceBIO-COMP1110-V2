from src.visualizer import Visualizer


def test_health_score_no_transactions_is_full():
    assert Visualizer.health_score(["any alert"], []) == 100


def test_health_score_deducts_per_alert_and_clamps():
    score = Visualizer.health_score(["a", "b", "c"], [{"amount": 10}])
    assert score == 55

    clamped = Visualizer.health_score(["a"] * 20, [{"amount": 10}])
    assert clamped == 0


def test_wealth_tree_flourishing_tier():
    tree = Visualizer.wealth_tree([], [{"amount": 10}])
    assert ".-~~~~~~~~~-." in tree
    assert "Health Score: 100/100" in tree


def test_wealth_tree_growing_tier():
    tree = Visualizer.wealth_tree(["a", "b"], [{"amount": 10}])  # 70
    assert ".-~~~~-." in tree
    assert "Health Score: 70/100" in tree


def test_wealth_tree_sapling_tier():
    tree = Visualizer.wealth_tree(["a", "b", "c", "d"], [{"amount": 10}])  # 40
    assert "Health Score: 40/100" in tree
    assert "/..\\" in tree


def test_wealth_tree_withering_tier():
    tree = Visualizer.wealth_tree(["a"] * 7, [{"amount": 10}])  # clamped to 0
    assert "Health Score: 0/100" in tree
    assert "x" in tree


def test_animated_wealth_tree_frame_changes_shape_position():
    frame0 = Visualizer.animated_wealth_tree(["a", "b"], [{"amount": 10}], frame=0)
    frame2 = Visualizer.animated_wealth_tree(["a", "b"], [{"amount": 10}], frame=2)
    assert frame0 != frame2
    assert "Health Score: 70/100" in frame0
