import pandas as pd

class RootCauseAgent:
    def __init__(self):
        pass

    def analyze_root_cause(self, df, anomalous_weeks_df):
        """
        For each anomalous week, analyzes the raw data to find the root cause.
        Returns a list of dictionaries with detailed analysis.
        """
        reports = []
        
        total_tickets = len(df)
        if total_tickets == 0 or anomalous_weeks_df.empty:
            return reports
            
        overall_product_dist = df['product_purchased'].value_counts(normalize=True)
        overall_type_dist = df['ticket_type'].value_counts(normalize=True)
        
        for _, row in anomalous_weeks_df.iterrows():
            week = row['week']
            week_df = df[df['week'] == week]
            
            if len(week_df) == 0:
                continue
                
            week_vol = row['ticket_volume']
            vol_z = row.get('vol_z_score', 0)
            is_iforest = row.get('anomaly_iforest', False)
            
            report = f"Week {week}: Anomaly Detected (Volume: {week_vol}, Z-Score: {vol_z:.2f}, IsolationForest: {is_iforest})\n"
            report += "Root Cause Analysis:\n"
            
            has_definitive_cause = False
            
            # Check for product spikes
            week_product_dist = week_df['product_purchased'].value_counts(normalize=True)
            for product, pct in week_product_dist.items():
                overall_pct = overall_product_dist.get(product, 0)
                if pct > (overall_pct + 0.20): # Spiked by 20% compared to average
                    report += f"  - Spike in Product: '{product}' accounted for {pct*100:.1f}% of tickets this week (vs {overall_pct*100:.1f}% avg).\n"
                    has_definitive_cause = True
                    
            # Check for ticket type spikes
            week_type_dist = week_df['ticket_type'].value_counts(normalize=True)
            for ttype, pct in week_type_dist.items():
                overall_pct = overall_type_dist.get(ttype, 0)
                if pct > (overall_pct + 0.20):
                    report += f"  - Spike in Ticket Type: '{ttype}' accounted for {pct*100:.1f}% of tickets this week (vs {overall_pct*100:.1f}% avg).\n"
                    has_definitive_cause = True
                    
            # Check if satisfaction was extremely low
            avg_sat = row['avg_satisfaction']
            if avg_sat > 0 and avg_sat < 2.5:
                report += f"  - Poor Customer Satisfaction: {avg_sat:.2f} (below acceptable threshold of 2.5).\n"
                has_definitive_cause = True
                
            # Check if resolution time was extremely high
            avg_res_days = row['avg_resolution_days']
            if avg_res_days > 5: # Taking longer than 5 days average
                report += f"  - High Resolution Time: {avg_res_days:.1f} days average.\n"
                has_definitive_cause = True
                
            # If no obvious spike was found
            if not has_definitive_cause:
                report += "  - No single dominating factor found. Anomaly might be due to general high volume across all products/types.\n"
                
            reports.append({
                'week': week,
                'ticket_volume': week_vol,
                'vol_z_score': vol_z,
                'anomaly_iforest': is_iforest,
                'report_text': report,
                'has_definitive_cause': has_definitive_cause
            })
            
        return reports

    def analyze_mom_changes(self, df, current_month, prev_month, monthly_trends, weekly_anomalies_df=None):
        """
        Analyzes Month-over-Month changes and finds root causes for drops/spikes.
        """
        analysis = {
            'current_month': current_month,
            'prev_month': prev_month,
            'metrics': {},
            'spikes': [],
            'csat_drop_reason': [],
            'csat_rise_reason': [],
            'weekly_anomalies': []
        }
        
        curr_row = monthly_trends[monthly_trends['month'] == current_month]
        prev_row = monthly_trends[monthly_trends['month'] == prev_month]
        
        if curr_row.empty or prev_row.empty:
            return analysis
            
        curr_row = curr_row.iloc[0]
        prev_row = prev_row.iloc[0]
        
        # Calculate MoM differences
        vol_change = curr_row['ticket_volume'] - prev_row['ticket_volume']
        vol_pct = (vol_change / prev_row['ticket_volume']) * 100 if prev_row['ticket_volume'] > 0 else 0
        
        csat_change = curr_row['avg_satisfaction'] - prev_row['avg_satisfaction']
        res_change = curr_row['avg_resolution_days'] - prev_row['avg_resolution_days']
        
        analysis['metrics'] = {
            'curr_vol': curr_row['ticket_volume'],
            'prev_vol': prev_row['ticket_volume'],
            'vol_pct': vol_pct,
            'curr_csat': curr_row['avg_satisfaction'],
            'prev_csat': prev_row['avg_satisfaction'],
            'csat_change': csat_change,
            'curr_res': curr_row['avg_resolution_days'],
            'prev_res': prev_row['avg_resolution_days'],
            'res_change': res_change
        }
        
        curr_df = df[df['month'] == current_month]
        prev_df = df[df['month'] == prev_month]
        
        if len(curr_df) == 0 or len(prev_df) == 0:
            return analysis
            
        # Identify Spikes
        curr_product_dist = curr_df['product_purchased'].value_counts(normalize=True)
        prev_product_dist = prev_df['product_purchased'].value_counts(normalize=True)
        
        for product, pct in curr_product_dist.items():
            prev_pct = prev_product_dist.get(product, 0)
            if pct > (prev_pct + 0.15): # Spiked by 15% absolute compared to last month
                analysis['spikes'].append(f"'{product}' tickets surged to {pct*100:.1f}% of volume (was {prev_pct*100:.1f}%).")
                
        # Diagnose CSAT Drop
        if csat_change < -0.1:
            overall_curr_csat = curr_row['avg_satisfaction']
            total_curr_vol = curr_row['ticket_volume']
            
            # Calculate impact for each product
            product_stats = curr_df.groupby('product_purchased').agg(
                prod_csat=('customer_satisfaction_rating', 'mean'),
                prod_vol=('ticket_id', 'count')
            ).reset_index()
            
            # Impact = (Overall_CSAT - Product_CSAT) * (Product_Vol / Total_Vol)
            # Higher impact means it dragged the score down more
            product_stats['csat_impact'] = (overall_curr_csat - product_stats['prod_csat']) * (product_stats['prod_vol'] / total_curr_vol)
            
            # Filter to products that actually dragged it down
            negative_impacts = product_stats[product_stats['csat_impact'] > 0].sort_values('csat_impact', ascending=False)
            
            if not negative_impacts.empty:
                top_3 = negative_impacts.head(3)
                for _, p_row in top_3.iterrows():
                    drop_explained = (p_row['csat_impact'] / abs(csat_change)) * 100 if abs(csat_change) > 0 else 0
                    if drop_explained > 100: drop_explained = 100 # cap at 100% just in case
                    analysis['csat_drop_reason'].append(
                        f"'{p_row['product_purchased']}': CSAT {p_row['prod_csat']:.2f} (Responsible for ~{drop_explained:.1f}% of the total drop)"
                    )
                
            # Check if resolution time was the cause
            if res_change > 1.0: # If it increased by more than 1 day
                analysis['csat_drop_reason'].append(f"Average resolution time increased significantly by {res_change:.1f} days.")
                
            if not analysis['csat_drop_reason']:
                 analysis['csat_drop_reason'].append("General drop in satisfaction across multiple products.")

        elif csat_change > 0.1:
            overall_curr_csat = curr_row['avg_satisfaction']
            total_curr_vol = curr_row['ticket_volume']
            
            # Check resolution time improvement
            if res_change < -0.5:
                analysis['csat_rise_reason'].append(f"Average resolution time improved significantly by {abs(res_change):.1f} days.")
                
            # Check ticket volume drop
            if vol_pct < -5.0:
                analysis['csat_rise_reason'].append(f"Ticket volume dropped by {abs(vol_pct):.1f}%, reducing agent backlog and improving quality.")
                
            # Check positive product drivers
            product_stats = curr_df.groupby('product_purchased').agg(
                prod_csat=('customer_satisfaction_rating', 'mean'),
                prod_vol=('ticket_id', 'count')
            ).reset_index()
            
            # Impact = (Product_CSAT - Overall_CSAT) * (Product_Vol / Total_Vol)
            product_stats['csat_impact'] = (product_stats['prod_csat'] - overall_curr_csat) * (product_stats['prod_vol'] / total_curr_vol)
            
            positive_impacts = product_stats[product_stats['csat_impact'] > 0].sort_values('csat_impact', ascending=False)
            
            if not positive_impacts.empty:
                top_3 = positive_impacts.head(3)
                for _, p_row in top_3.iterrows():
                    rise_explained = (p_row['csat_impact'] / abs(csat_change)) * 100 if abs(csat_change) > 0 else 0
                    if rise_explained > 100: rise_explained = 100
                    analysis['csat_rise_reason'].append(
                        f"'{p_row['product_purchased']}': High CSAT of {p_row['prod_csat']:.2f} (Drove ~{rise_explained:.1f}% of the total increase)"
                    )
                 
        # Include Weekly Anomalies
        if weekly_anomalies_df is not None and not weekly_anomalies_df.empty:
            for _, w_row in weekly_anomalies_df.iterrows():
                if current_month in str(w_row['week']):
                    reason = []
                    if abs(w_row.get('vol_z_score', 0)) > 1.5:
                        reason.append(f"Z-Score {w_row['vol_z_score']:.2f}")
                    if w_row.get('anomaly_iforest', False):
                        reason.append("Isolation Forest Flag")
                    
                    if not reason:
                        reason.append("Flagged")
                        
                    analysis['weekly_anomalies'].append(
                        f"Week {w_row['week']} | Volume: {w_row['ticket_volume']} | Flags: {', '.join(reason)}"
                    )
                 
        return analysis
