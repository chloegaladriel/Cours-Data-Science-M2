from airflow.decorators import dag, task
from datetime import datetime


@dag(
    dag_id="hello_world",
    start_date=datetime(2024, 1, 1),
    schedule="@daily",
    catchup=False,
    tags=["demo", "beginner"],
    description="My first Airflow DAG using decorators"
)
def hello_workflow():
    @task
    def say_hello():
        """Simple task that says hello"""
        print("👋 Hello from Airflow!")
        print("✅ My first DAG is working perfectly!")
        return "Hello task completed"

    @task
    def display_date():
        """Task that displays current date and time"""
        now = datetime.now()
        print(f"📅 Current date and time: {now}")
        print(f"🕐 Timestamp: {now.timestamp()}")
        return now.strftime("%Y-%m-%d %H:%M:%S")

    @task
    def combine_results(hello_msg: str, date_str: str):
        """Task that combines results from previous tasks"""
        print(f"🔗 Combining results:")
        print(f"   - {hello_msg}")
        print(f"   - Date: {date_str}")
        return f"Workflow completed at {date_str}"

    # Define task dependencies
    say_hello() >> display_date()


# Create the DAG instance
dag = hello_workflow()
