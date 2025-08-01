Of course. Here is a plan to refactor your application to more easily handle state changes for your tasks.

### Goal

The goal is to centralize the state transition logic. Currently, this logic (the `UPDATE` SQL statements) is spread throughout `tasks.py`. By creating a dedicated `StateManager`, we can make the code more readable, maintainable, and easier to modify when you need to add or change states in the future.

### The Plan

We will create a new `StateManager` class responsible for all database state updates. The task functions in `tasks.py` will then use this manager instead of writing raw SQL for status changes.

**Step 1: Create a `StateManager` to handle state transitions**

First, we'll create a new file to house our state management logic. This separates the "what" (the task logic) from the "how" (updating the state in the database).

Create a new file: `src/monitor_app/state_manager.py`

```python
# src/monitor_app/state_manager.py

import logging
from enum import Enum
from psycopg2.extensions import cursor

# Moving the Status Enum here to centralize all state-related definitions.
class Status(str, Enum):
    """Represents the status of a record in the key_points table."""
    NEW = "NEW"
    PROCESSING = "PROCESSING"
    COMPLETED = "COMPLETED"
    FAILED = "FAILED"


class StateManager:
    """Handles all state transitions for key_points records."""

    def __init__(self, db_cursor: cursor):
        """
        Initializes the StateManager with a database cursor.

        Args:
            db_cursor: An active psycopg2 cursor.
        """
        self.cursor = db_cursor

    def mark_as_processing(self, record_id: int, provider_job_id: str):
        """Transitions a record's state to PROCESSING."""
        logging.info(f"Updating record {record_id} to PROCESSING with job ID {provider_job_id}")
        self.cursor.execute(
            """
            UPDATE key_points
            SET status          = %s,
                provider_job_id = %s,
                ai_result       = NULL,
                retry_count     = 0,
                updated_at      = NOW()
            WHERE id = %s
            """,
            (Status.PROCESSING, provider_job_id, record_id)
        )

    def mark_as_completed(self, record_id: int, ai_result: str):
        """Transitions a record's state to COMPLETED."""
        logging.info(f"Updating record {record_id} to COMPLETED.")
        self.cursor.execute(
            """
            UPDATE key_points
            SET status     = %s,
                ai_result  = %s,
                updated_at = NOW()
            WHERE id = %s
            """,
            (Status.COMPLETED, ai_result, record_id)
        )

    def mark_as_failed(self, record_id: int):
        """Transitions a record's state to FAILED after exhausting retries."""
        logging.error(f"Updating record {record_id} to FAILED.")
        self.cursor.execute(
            """
            UPDATE key_points
            SET status     = %s,
                updated_at = NOW()
            WHERE id = %s
            """,
            (Status.FAILED, record_id)
        )

    def retry_processing(self, record_id: int, new_provider_job_id: str):
        """Handles the logic for retrying a failed job, keeping it in PROCESSING state."""
        logging.info(f"Retrying record {record_id} with new job ID {new_provider_job_id}.")
        self.cursor.execute(
            """
            UPDATE key_points
            SET provider_job_id = %s,
                retry_count     = retry_count + 1,
                updated_at      = NOW()
            WHERE id = %s
            """,
            (new_provider_job_id, record_id)
        )

```

**Step 2: Refactor `tasks.py` to use the new `StateManager`**

Now, we will update `tasks.py` to use our new `StateManager`. This will simplify the task functions significantly.

Update the file: `src/monitor_app/tasks.py`

```python
# src/monitor_app/tasks.py

import psycopg2
import os
import logging
from dotenv import load_dotenv
from monitor_app.db_config import db_config
from monitor_app.reseracher import openai_research, client
# Import the new StateManager and Status enum
from monitor_app.state_manager import StateManager, Status

load_dotenv()
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')


# The Status Enum is now in state_manager.py, so it's removed from here.


def process_monitored_data():
    """
    Finds 'new' records and 'completed' records older than a defined interval,
    sends them to the AI for processing, and updates their status.
    """
    logging.info("Starting job: process_monitored_data")

    try:
        reprocess_interval_days = int(os.environ.get("REPROCESS_INTERVAL_DAYS", 5))
        interval_string = f"{reprocess_interval_days} days"
    except ValueError:
        logging.error("Invalid REPROCESS_INTERVAL_DAYS. Must be an integer. Using default of 5 days.")
        interval_string = "5 days"

    select_sql = """
                 SELECT id, name
                 FROM key_points
                 WHERE status = %s
                    OR status = %s
                    OR (status = %s AND updated_at < NOW() - INTERVAL %s) LIMIT 10
                 FOR UPDATE SKIP LOCKED \
                 """

    try:
        with psycopg2.connect(**db_config) as conn:
            with conn.cursor() as cursor:
                # Instantiate the state manager with the current cursor
                state_manager = StateManager(cursor)

                cursor.execute(select_sql, (Status.NEW, Status.FAILED, Status.COMPLETED, interval_string))
                records_to_process = cursor.fetchall()

                if not records_to_process:
                    logging.info("No new or re-processable records to dispatch.")
                    return

                logging.info(f"Found {len(records_to_process)} records to dispatch.")

                for record_id, record_name in records_to_process:
                    try:
                        response = openai_research(record_name, record_id)
                        provider_job_id = response.id
                        logging.info(f"Dispatched record ID {record_id}. Provider job ID: {provider_job_id}")

                        # Use the state manager to handle the state transition
                        state_manager.mark_as_processing(record_id, provider_job_id)

                    except Exception as e:
                        logging.error(f"Failed to dispatch job for record {record_id}: {e}")

    except Exception as e:
        logging.error(f"An unexpected error occurred in dispatcher: {e}")


def check_ai_job_status():
    """
    Finds 'processing' records, polls the AI provider for their status.
    If completed, stores the result. If failed, retries the job up to a limit.
    """
    logging.info("Starting job: check_ai_job_status")

    try:
        max_retries = int(os.environ.get("MAX_RETRIES", 3))
    except ValueError:
        logging.error("Invalid MAX_RETRIES. Must be an integer. Using default of 3.")
        max_retries = 3

    select_sql = """SELECT id, name, provider_job_id, retry_count
                    FROM key_points
                    WHERE status = %s LIMIT 20 
                    FOR
    UPDATE SKIP LOCKED"""

    try:
        with psycopg2.connect(**db_config) as conn:
            with conn.cursor() as cursor:
                # Instantiate the state manager with the current cursor
                state_manager = StateManager(cursor)

                cursor.execute(select_sql, (Status.PROCESSING,))
                records_to_check = cursor.fetchall()

                if not records_to_check:
                    logging.info("No processing records to check.")
                    return

                logging.info(f"Found {len(records_to_check)} records to check.")

                for record_id, record_name, provider_job_id, retry_count in records_to_check:
                    try:
                        job_status = client.responses.retrieve(provider_job_id)

                        if job_status.status == 'completed':
                            ai_result = job_status.output_text
                            # Use the state manager
                            state_manager.mark_as_completed(record_id, ai_result)

                        elif job_status.status in ['failed', 'cancelled', 'expired']:
                            logging.warning(
                                f"Job {provider_job_id} for record {record_id} failed with status: {job_status.status}. Retry count: {retry_count}")

                            if retry_count < max_retries:
                                response = openai_research(record_name, record_id)
                                new_provider_job_id = response.id
                                # Use the state manager
                                state_manager.retry_processing(record_id, new_provider_job_id)
                            else:
                                logging.error(
                                    f"Job for record {record_id} exceeded max retry limit of {max_retries}. Marking as FAILED.")
                                # Use the state manager
                                state_manager.mark_as_failed(record_id)
                        else:
                            logging.info(f"Job {provider_job_id} is still in progress (status: {job_status.status}).")

                    except Exception as e:
                        logging.error(f"Error checking status for job {provider_job_id}: {e}")

    except Exception as e:
        logging.error(f"An unexpected error occurred in checker: {e}")
```

### Why This Is Better

1.  **Single Responsibility Principle:** `tasks.py` now focuses on orchestrating the workflow (getting records, calling the AI), while `state_manager.py` is solely responsible for how state is persisted in the database.
2.  **Readability:** The business logic in `tasks.py` is clearer. `state_manager.mark_as_completed(...)` is more descriptive and intention-revealing than a block of SQL.
3.  **Maintainability:** If you need to add a new status or change the logic for a transition (e.g., also update a `notes` field when a task fails), you only need to modify the corresponding method in `StateManager`. You don't have to hunt for all the places that `UPDATE` the status.
4.  **Reduced Errors:** By centralizing the state update logic, you eliminate the risk of introducing inconsistencies or bugs from copy-pasting SQL queries.
5.  **Easier Testing:** You can test the `StateManager` in isolation by providing a mock database cursor. You can also test the functions in `tasks.py` by mocking the `StateManager` itself.

No other files in your project need to be changed. This refactoring is contained and significantly improves the structure for future development.