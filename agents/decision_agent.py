class DecisionAgent:
    def __init__(self, high_z_threshold=2.5):
        self.high_z_threshold = high_z_threshold

    def filter_reports(self, root_cause_reports):
        """
        Filters anomalies to determine which ones are worth reporting.
        An anomaly is reported if:
        1. It has a definitive root cause (e.g. spike in product, poor satisfaction).
        2. OR its Z-Score is extremely high (> 2.5) or very low (< -2.5).
        """
        actionable_reports = []
        
        for r in root_cause_reports:
            # Check conditions
            is_extreme_z = abs(r['vol_z_score']) >= self.high_z_threshold
            has_cause = r['has_definitive_cause']
            
            if is_extreme_z or has_cause:
                r['decision_reason'] = []
                if is_extreme_z:
                    r['decision_reason'].append(f"Extreme Volume Deviation (Z={r['vol_z_score']:.2f})")
                if has_cause:
                    r['decision_reason'].append("Clear Root Cause Identified")
                
                actionable_reports.append(r)
                
        return actionable_reports
