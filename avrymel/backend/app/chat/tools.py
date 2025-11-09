"""LangChain tools for the AI assistant."""

from langchain_core.runnables import RunnableConfig
from langchain_core.tools import tool
from sqlalchemy.sql import text
from datetime import datetime
import random


@tool
async def query_database(query: str, config: RunnableConfig) -> str:
    """
    Runs a SELECT query on the database.
    Use this to get information from the user's data.

    Args:
        query: PostgreSQL SELECT query

    Returns:
        The result of the query as a string
    """
    session = config["configurable"]["db"]

    # Set tenant context for multi-tenancy
    await session.execute(text("SELECT set_tenant(1)"))

    try:  # FIXME(ginal): we might need to remove these
        result = await session.execute(text(query))
        rows = result.fetchall()
        return str(rows)
    except Exception as e:
        return f"Error executing query: {str(e)}"


@tool
async def calculator(expression: str, config: RunnableConfig) -> str:
    """
    Performs basic math calculations.
    Use this for any arithmetic operations.

    Args:
        expression: A mathematical expression like "2 + 2" or "10 * 5"

    Returns:
        The result of the calculation
    """
    try:
        # Safe eval with limited scope
        result = eval(expression, {"__builtins__": {}}, {})
        return f"The result is: {result}"
    except Exception as e:
        return f"Error calculating: {str(e)}"


@tool
async def get_current_time() -> str:
    """
    Returns the current date and time.
    Use this when the user asks about the current time, date, or day.

    Returns:
        Current date and time as a formatted string
    """
    now = datetime.now()
    return f"Current date and time: {now.strftime('%Y-%m-%d %H:%M:%S')}"


@tool
async def random_number(min_val: int, max_val: int) -> str:
    """
    Generates a random number between min and max values (inclusive).

    Args:
        min_val: Minimum value (inclusive)
        max_val: Maximum value (inclusive)

    Returns:
        A random number in the specified range
    """
    number = random.randint(min_val, max_val)
    return f"Random number between {min_val} and {max_val}: {number}"


@tool
async def word_counter(text: str) -> str:
    """
    Counts the number of words in a given text.

    Args:
        text: The text to count words in

    Returns:
        The number of words
    """
    words = text.split()
    return f"Word count: {len(words)} words"


@tool
async def pie_chart_from_sql_query(query: str, config: RunnableConfig, description: str) -> str:
    """
    Use output of provided sql to generate pie chart plot. The query MUST return two columns,
    first one with the labels, second one with values for each label

    Args:
        query: sql query that returns two columns, first one with labels, second with values for each label
        description: What description will be shown above the graph
    """
    session = config["configurable"]["db"]

    await session.execute(text("SELECT set_tenant(1)"))

    try:
        result = await session.execute(text(query))
        rows = result.fetchall()

    except Exception as e:
        return f"Error executing query: {str(e)}"

    try:
        if not rows:
            return "Error: Query returned no data."

        column_count = len(rows[0])
        if column_count != 2:
            raise ValueError(f"Query results must return exactly 2 columns (labels, values) but returned {column_count} columns.")

        pie_data = []
        for row in rows:
            label = row[0]
            value = row[1]
            try:
                numeric_value = float(value)
                pie_data.append((label, numeric_value))
            except (ValueError, TypeError):
                raise TypeError(f"The second column (values) must contain numeric data suitable for a pie chart. Found non-numeric value: '{value}'")

        config["configurable"]["put_plot_here"]["plot"] = {"type": "pie", "data": pie_data, "description": description}
        return "The plot was generated and give to the user, thanks a lot:)"

    except (ValueError, TypeError) as e:
        # Catch 2: Errors during data validation
        return f"Error validating data for pie chart: {str(e)}"

@tool
async def horizontal_bar_chart_from_query(query: str, config: RunnableConfig) -> str:
    """
    Use output of provided sql to generate a horizontal bar chart. The query MUST return two columns,
    first one with the labels, second one with values for each label

    Args:
        query: sql query that returns two columns, first one with labels, second with values for each label
    """
    session = config["configurable"]["db"]

    await session.execute(text("SELECT set_tenant(1)"))

    try:
        result = await session.execute(text(query))
        rows = result.fetchall()

    except Exception as e:
        return f"Error executing query: {str(e)}"

    try:
        if not rows:
            return "Error: Query returned no data."

        column_count = len(rows[0])
        if column_count != 2:
            raise ValueError(f"Query results must return exactly 2 columns (labels, values) but returned {column_count} columns.")

        bar_data = []
        for row in rows:
            label = row[0]
            value = row[1]
            try:
                numeric_value = float(value)
                bar_data.append((label, numeric_value))
            except (ValueError, TypeError):
                raise TypeError(f"The second column (values) must contain numeric data suitable for a pie chart. Found non-numeric value: '{value}'")

        config["configurable"]["put_plot_here"]["plot"] = {"type": "horizontal_bar", "data": bar_data}
        return "The plot was generated and give to the user, thanks a lot:)"

    except (ValueError, TypeError) as e:
        # Catch 2: Errors during data validation
        return f"Error validating data for pie chart: {str(e)}"

def get_tools():
    """Returns a list of all available tools."""
    return [horizontal_bar_chart_from_query, pie_chart_from_sql_query, query_database, calculator, get_current_time, random_number, word_counter]
