import uuid
from .. import database

def create_task(tool_name: str) -> str:
    """
    Creates a new task in the database with a 'pending' status.

    Args:
        tool_name: The name of the tool initiating the task.

    Returns:
        The unique ID of the newly created task.
    """
    task_id = str(uuid.uuid4())
    with database.get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO tasks (task_id, tool_name, status) VALUES (?, ?, ?)",
            (task_id, tool_name, 'pending')
        )
        conn.commit()
    return task_id

def update_task_progress(task_id: str, progress: int):
    """
    Updates the progress of a specific task.

    Args:
        task_id: The ID of the task to update.
        progress: The new progress percentage (0-100).
    """
    with database.get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE tasks SET progress = ?, status = ? WHERE task_id = ?",
            (progress, 'processing', task_id)
        )
        conn.commit()

def complete_task(task_id: str, result_path: str):
    """
    Marks a task as 'completed' and stores the path to the result file.

    Args:
        task_id: The ID of the task to complete.
        result_path: The path to the generated result file.
    """
    with database.get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE tasks SET status = ?, progress = 100, result_path = ? WHERE task_id = ?",
            ('completed', result_path, task_id)
        )
        conn.commit()

def fail_task(task_id: str, error_message: str):
    """
    Marks a task as 'failed' and stores the error message.

    Args:
        task_id: The ID of the task to fail.
        error_message: The reason for the failure.
    """
    with database.get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE tasks SET status = ?, error_message = ? WHERE task_id = ?",
            ('failed', error_message, task_id)
        )
        conn.commit()

def get_task_status(task_id: str):
    """
    Retrieves the current status and details of a task.

    Args:
        task_id: The ID of the task to query.

    Returns:
        A dictionary containing the task's details, or None if not found.
    """
    with database.get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM tasks WHERE task_id = ?", (task_id,))
        task = cursor.fetchone()
        if task:
            return dict(task)
        return None

def update_task_result_path(task_id: str, result_path: str):
    """
    Updates the result_path of a specific task without changing its status.
    Useful for iterative processes like image editing.
    """
    with database.get_db() as conn:
        cursor = conn.cursor()
        cursor.execute(
            "UPDATE tasks SET result_path = ? WHERE task_id = ?",
            (result_path, task_id)
        )
        conn.commit()