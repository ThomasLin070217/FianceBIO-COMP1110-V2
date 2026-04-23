"""
ASCII visualizer for finance health status.
"""


class Visualizer:
    ALERT_PENALTY = 15
    RESET = "\033[0m"
    GREEN = "\033[92m"
    YELLOW = "\033[93m"
    BROWN = "\033[33m"
    RED = "\033[91m"
    TRUNK_BROWN = "\033[38;5;94m"
    WITHERED_BROWN = "\033[38;5;136m"

    @staticmethod
    def _trunk(text):
        return f"{Visualizer.TRUNK_BROWN}{text}{Visualizer.RESET}"

    @staticmethod
    def _leaf(text, healthy=True):
        color = Visualizer.GREEN if healthy else Visualizer.WITHERED_BROWN
        return f"{color}{text}{Visualizer.RESET}"

    @staticmethod
    def health_score(alerts, transactions):
        """
        Calculate health score (0-100) from alerts and transactions.
        If no transactions exist, return 100.
        """
        if not transactions:
            return 100

        alert_count = len(alerts) if alerts else 0
        score = 100 - (alert_count * Visualizer.ALERT_PENALTY)
        return max(0, min(100, score))

    @staticmethod
    def wealth_tree(alerts, transactions):
        """
        Return an ASCII tree that reflects financial health.
        """
        score = Visualizer.health_score(alerts, transactions)
        lines = Visualizer.tree_lines_by_score(score, frame=0)
        color = Visualizer.color_by_score(score)
        tree = "\n".join([f"Health Score: {score}/100", *lines])
        return f"{color}{tree}{Visualizer.RESET}"

    @staticmethod
    def animated_wealth_tree(alerts, transactions, frame=0):
        """
        Return one animation frame of the ASCII tree.
        Increasing frame value creates a gentle side-to-side sway.
        """
        score = Visualizer.health_score(alerts, transactions)
        lines = Visualizer.tree_lines_by_score(score, frame=frame)
        color = Visualizer.color_by_score(score)
        tree = "\n".join([f"Health Score: {score}/100", *lines])
        return f"{color}{tree}{Visualizer.RESET}"

    @staticmethod
    def tree_lines_by_score(score, frame=0):
        """Return symbol-only tree lines for dashboard display."""
        sway = [-1, 0, 1, 0][frame % 4]
        indent = lambda n: " " * max(0, n + sway)

        if score >= 80:
            return [
                f"{indent(8)} {Visualizer._leaf('.-~~~~~~~~~-.', healthy=True)}",
                f"{indent(6)}{Visualizer._leaf('/~~~~~~~~~~~~~\\', healthy=True)}",
                f"{indent(5)}{Visualizer._leaf('/~~~~~~~~~~~~~~~\\', healthy=True)}",
                f"{indent(7)}{Visualizer._leaf('\\~~~~~', healthy=True)}{Visualizer._trunk('###')}{Visualizer._leaf('~~~~~/', healthy=True)}",
                f"{indent(10)}{Visualizer._trunk('###')}",
                f"{indent(10)}{Visualizer._trunk('###')}",
            ]
        if score >= 50:
            return [
                f"{indent(9)} {Visualizer._leaf('.-~~~~-.', healthy=True)}",
                f"{indent(7)}{Visualizer._leaf('/~~~~~~~~\\', healthy=True)}",
                f"{indent(8)}{Visualizer._leaf('\\~~~~~~~/', healthy=True)}",
                f"{indent(10)}{Visualizer._trunk('###')}",
                f"{indent(10)}{Visualizer._trunk('###')}",
                f"{indent(9)}{Visualizer._trunk('_#####_')}",
            ]
        if score >= 20:
            return [
                f"{indent(10)} {Visualizer._leaf('/\\', healthy=False)}",
                f"{indent(9)} {Visualizer._leaf('/..\\', healthy=False)}",
                f"{indent(8)} {Visualizer._leaf('/....\\', healthy=False)}",
                f"{indent(10)}{Visualizer._trunk('###')}",
                f"{indent(10)}{Visualizer._trunk('###')}",
                f"{indent(9)}{Visualizer._trunk('_###_')}",
            ]
        return [
            f"{indent(10)} {Visualizer._leaf('xx', healthy=False)}",
            f"{indent(10)}{Visualizer._trunk('###')}",
            f"{indent(10)}{Visualizer._trunk('###')}",
            f"{indent(10)}{Visualizer._trunk('###')}",
            f"{indent(9)}{Visualizer._trunk('/####\\')}",
            f"{indent(8)}{Visualizer._trunk('/______\\')}",
        ]

    @staticmethod
    def color_by_score(score):
        if score >= 80:
            return Visualizer.GREEN
        if score >= 50:
            return Visualizer.YELLOW
        if score >= 20:
            return Visualizer.BROWN
        return Visualizer.RED
