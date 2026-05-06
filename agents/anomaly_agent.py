import pandas as pd
import numpy as np
from sklearn.ensemble import IsolationForest

class AnomalyAgent:
    def __init__(self, z_threshold=2.0):
        self.z_threshold = z_threshold

    def detect_anomalies(self, weekly_trends_df):
        """
        Detects anomalies in weekly trends using Z-Score and Isolation Forest.
        Returns a DataFrame of anomalous weeks.
        """
        if weekly_trends_df.empty:
            return pd.DataFrame()
            
        df = weekly_trends_df.copy()
        
        # 1. Z-Score method for ticket volume
        mean_vol = df['ticket_volume'].mean()
        std_vol = df['ticket_volume'].std()
        
        if std_vol > 0:
            df['vol_z_score'] = (df['ticket_volume'] - mean_vol) / std_vol
        else:
            df['vol_z_score'] = 0
            
        df['anomaly_zscore'] = np.abs(df['vol_z_score']) > self.z_threshold
        
        # 2. Isolation Forest method (Multivariate)
        features = ['ticket_volume', 'avg_satisfaction', 'avg_resolution_days']
        
        # Isolation Forest requires at least a few samples to work properly
        if len(df) > 5:
            X = df[features].fillna(0)
            clf = IsolationForest(contamination=0.1, random_state=42)
            preds = clf.fit_predict(X)
            df['anomaly_iforest'] = preds == -1
        else:
            df['anomaly_iforest'] = False
            
        # Combine flags
        df['is_anomaly'] = df['anomaly_zscore'] | df['anomaly_iforest']
        
        anomalies = df[df['is_anomaly']]
        return anomalies
