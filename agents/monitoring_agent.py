import pandas as pd

class MonitoringAgent:
    def __init__(self):
        pass

    def get_weekly_trends(self, df):
        """
        Calculates weekly trends for ticket volume, avg resolution time, and avg satisfaction.
        """
        # Ensure we have a valid time series by week
        if 'week' not in df.columns:
            return pd.DataFrame()
            
        trends = df.groupby('week').agg(
            ticket_volume=('ticket_id', 'count'),
            avg_satisfaction=('customer_satisfaction_rating', 'mean')
        ).reset_index()
        
        # Calculate time to resolution in days if the columns exist
        if 'time_to_resolution' in df.columns and 'first_response_time' in df.columns:
            resolution_times = (df['time_to_resolution'] - df['first_response_time']).dt.total_seconds() / (3600 * 24)
            df['resolution_days'] = resolution_times
            
            resolution_trend = df.groupby('week').agg(
                avg_resolution_days=('resolution_days', 'mean')
            ).reset_index()
            
            trends = pd.merge(trends, resolution_trend, on='week', how='left')
        else:
            trends['avg_resolution_days'] = float('nan')
            
        # Fill missing values for metrics
        trends.fillna(0, inplace=True)
        
        # Sort by week
        trends = trends.sort_values('week').reset_index(drop=True)
        return trends

    def get_monthly_trends(self, df):
        """
        Calculates monthly trends for ticket volume, avg resolution time, and avg satisfaction.
        """
        if 'month' not in df.columns:
            return pd.DataFrame()
            
        trends = df.groupby('month').agg(
            ticket_volume=('ticket_id', 'count'),
            avg_satisfaction=('customer_satisfaction_rating', 'mean')
        ).reset_index()
        
        if 'time_to_resolution' in df.columns and 'first_response_time' in df.columns:
            # Recompute resolution_days in case it hasn't been computed
            if 'resolution_days' not in df.columns:
                df['resolution_days'] = (df['time_to_resolution'] - df['first_response_time']).dt.total_seconds() / (3600 * 24)
                
            resolution_trend = df.groupby('month').agg(
                avg_resolution_days=('resolution_days', 'mean')
            ).reset_index()
            
            trends = pd.merge(trends, resolution_trend, on='month', how='left')
        else:
            trends['avg_resolution_days'] = float('nan')
            
        trends.fillna(0, inplace=True)
        trends = trends.sort_values('month').reset_index(drop=True)
        return trends
