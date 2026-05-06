import pandas as pd

class DataProcessor:

    def __init__(self, file_path):
        self.file_path = file_path

    def load_data(self):
        df = pd.read_csv(self.file_path)
        return df

    def preprocess(self, df):

        # Standardize column names
        df.columns = df.columns.str.lower().str.strip().str.replace(" ", "_")

        # Convert dates
        df["date_of_purchase"] = pd.to_datetime(df["date_of_purchase"], errors='coerce')
        if "first_response_time" in df.columns:
            df["first_response_time"] = pd.to_datetime(df["first_response_time"], errors='coerce')
        if "time_to_resolution" in df.columns:
            df["time_to_resolution"] = pd.to_datetime(df["time_to_resolution"], errors='coerce')

        # Create month and week column based on purchase date (spans multiple years)
        date_col = "date_of_purchase"
        df["month"] = df[date_col].dt.to_period("M").astype(str)
        df["week"] = df[date_col].dt.to_period("W").astype(str)

        return df

    def create_kpi_table(self, df):
        # Basic aggregation for KPI
        kpi = df.groupby('month').agg(
            total_tickets=('ticket_id', 'count'),
            avg_satisfaction=('customer_satisfaction_rating', 'mean')
        ).reset_index()
        return kpi
