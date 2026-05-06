import argparse
from utils.data_processing import DataProcessor
from agents.monitoring_agent import MonitoringAgent
from agents.anomaly_agent import AnomalyAgent
from agents.root_cause_agent import RootCauseAgent
from agents.reporting_agent import ReportingAgent
from agents.action_agent import ActionAgent


def main():
    parser = argparse.ArgumentParser(description="Multi-Agent Support Ticket Analysis")
    parser.add_argument(
        "--month",
        type=str,
        help="Target month in YYYY-MM format (e.g., 2021-05). Defaults to the latest month.",
    )
    args = parser.parse_args()

    print("Initializing Enhanced MoM Executive Report Pipeline...")

    # 1. Data Processing
    print("\n[DataProcessor] Loading and cleaning data...")
    processor = DataProcessor("data/raw/customer_support_tickets.csv")
    df = processor.load_data()
    df = processor.preprocess(df)
    print(f"Data loaded successfully. Total records: {len(df)}")

    # 2. Monitoring Agent
    print("\n[MonitoringAgent] Extracting trends...")
    monitor = MonitoringAgent()
    monthly_trends = monitor.get_monthly_trends(df)
    weekly_trends = monitor.get_weekly_trends(df)

    if len(monthly_trends) < 2:
        print("Not enough monthly data to perform Month-over-Month comparison.")
        return

    # 3. Anomaly Agent (Weekly)
    print("\n[AnomalyAgent] Detecting weekly anomalies...")
    anomaly_detector = AnomalyAgent(z_threshold=1.5)
    weekly_anomalies = anomaly_detector.detect_anomalies(weekly_trends)

    # Determine Target Month
    if args.month:
        if args.month not in monthly_trends["month"].values:
            print(
                f"Error: Month {args.month} not found in dataset. Available months range from {monthly_trends['month'].iloc[0]} to {monthly_trends['month'].iloc[-1]}."
            )
            return

        target_idx = monthly_trends[monthly_trends["month"] == args.month].index[0]
        if target_idx == 0:
            print(
                f"Error: Cannot perform MoM analysis for {args.month} because it is the first month in the dataset (no previous month available)."
            )
            return

        current_month = monthly_trends.iloc[target_idx]["month"]
        prev_month = monthly_trends.iloc[target_idx - 1]["month"]
    else:
        # Default to latest two months
        current_month = monthly_trends.iloc[-1]["month"]
        prev_month = monthly_trends.iloc[-2]["month"]

    print(
        f"\nComparing Current Month ({current_month}) with Previous Month ({prev_month})..."
    )

    # 4. Root Cause Agent (MoM Analysis)
    print(
        "\n[RootCauseAgent] Analyzing MoM spikes, CSAT drops, and embedding weekly anomalies..."
    )
    root_cause_analyst = RootCauseAgent()
    mom_analysis = root_cause_analyst.analyze_mom_changes(
        df, current_month, prev_month, monthly_trends, weekly_anomalies
    )

    if not mom_analysis or not mom_analysis.get("metrics"):
        print("Failed to perform MoM Analysis.")
        return

    # 5. Reporting Agent
    print("\n[ReportingAgent] Generating executive summary...")
    reporting_agent = ReportingAgent()
    summary = reporting_agent.generate_mom_summary(mom_analysis)

    # 6. Action Agent
    print("\n[ActionAgent] Dispatching report via email...")
    action_agent = ActionAgent()  # Will use dry_run by default
    action_agent.send_email(summary, dry_run=True)


if __name__ == "__main__":
    main()
