class ReportingAgent:
    def __init__(self):
        pass

    def generate_summary(self, actionable_reports):
        """
        Creates an executive summary email payload from the actionable reports.
        """
        if not actionable_reports:
            return None
            
        subject = f"[ALERT] {len(actionable_reports)} Customer Support Anomalies Detected"
        
        body = "Hello Team,\n\n"
        body += "The AI monitoring system has detected significant anomalies in our customer support metrics that require your attention.\n\n"
        body += "=" * 50 + "\n"
        body += "EXECUTIVE SUMMARY\n"
        body += "=" * 50 + "\n\n"
        
        for idx, r in enumerate(actionable_reports, 1):
            body += f"[{idx}] WEEK: {r['week']}\n"
            body += f"    Ticket Volume: {r['ticket_volume']}\n"
            body += f"    Flag Reason: {', '.join(r['decision_reason'])}\n"
            body += f"    Details:\n"
            
            # Extract bullet points from the report text
            details = r['report_text'].split("Root Cause Analysis:\n")[-1]
            for line in details.split('\n'):
                if line.strip():
                    body += f"    {line}\n"
            body += "\n"
            
        body += "=" * 50 + "\n"
        body += "Please investigate these issues immediately.\n\n"
        body += "Regards,\nAI Support Monitor"
        
        return {
            'subject': subject,
            'body': body
        }

    def generate_mom_summary(self, mom_analysis):
        """
        Generates an executive summary based on the Month-over-Month analysis.
        """
        if not mom_analysis or not mom_analysis.get('metrics'):
            return None
            
        curr_month = mom_analysis['current_month']
        prev_month = mom_analysis['prev_month']
        metrics = mom_analysis['metrics']
        
        subject = f"[MONTHLY REPORT] Customer Support Summary: {curr_month}"
        
        body = "Hello Team,\n\n"
        body += f"Here is the Month-over-Month (MoM) support summary comparing {curr_month} to {prev_month}.\n\n"
        
        body += "[OVERALL METRICS]\n"
        
        # Volume formatting
        vol_dir = "Up" if metrics['vol_pct'] > 0 else "Down" if metrics['vol_pct'] < 0 else "Flat"
        body += f"- Ticket Volume: {metrics['curr_vol']} ({vol_dir} {abs(metrics['vol_pct']):.1f}% vs last month)\n"
        
        # CSAT formatting
        csat_dir = "Rose" if metrics['csat_change'] > 0 else "Dropped" if metrics['csat_change'] < 0 else "Flat"
        body += f"- Average CSAT: {metrics['curr_csat']:.2f} ({csat_dir} by {abs(metrics['csat_change']):.2f} points)\n"
        
        # Resolution formatting
        res_dir = "Up" if metrics['res_change'] > 0 else "Down" if metrics['res_change'] < 0 else "Flat"
        body += f"- Avg Resolution Time: {metrics['curr_res']:.1f} days ({res_dir} {abs(metrics['res_change']):.1f} days)\n\n"
        
        if mom_analysis['spikes']:
            body += "[KEY SPIKES & ACTIONABLE INSIGHTS]\n"
            for spike in mom_analysis['spikes']:
                body += f"- Spike Detected: {spike}\n"
            body += "\n"
            
        if mom_analysis.get('csat_drop_reason'):
            body += "[WHY DID CSAT DROP?]\n"
            for reason in mom_analysis['csat_drop_reason']:
                body += f"- {reason}\n"
            body += "\n"
            
        if mom_analysis.get('csat_rise_reason'):
            body += "[WHY DID CSAT RISE?]\n"
            for reason in mom_analysis['csat_rise_reason']:
                body += f"- {reason}\n"
            body += "\n"
            
        if mom_analysis.get('weekly_anomalies'):
            body += "[WEEKLY ANOMALIES]\n"
            for anomaly in mom_analysis['weekly_anomalies']:
                body += f"- {anomaly}\n"
            body += "\n"
            
        body += "=" * 50 + "\n"
        body += "Regards,\nAI Support Monitor"
        
        return {
            'subject': subject,
            'body': body
        }
