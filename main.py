from fastapi import FastAPI
from db import get_connection
from pydantic import BaseModel
from datetime import datetime
from fastapi import HTTPException

class ExpenseCreate(BaseModel):
    amount:float
    cat_id:str
    date_time:datetime


app =  FastAPI(title="Student Expense Tracker API")

@app.get("/")
def home():
    return {"message":"Expense Tracker API is running!"}


@app.get("/expenses")
def get_expenses():
    connection = get_connection()

    try:
        cursor = connection.cursor()
        cursor.execute("""
                        SELECT
                            e.exp_id,
                            e.date_time,
                            e.amount,
                            e.cat_id,
                            c.cat_name
                        FROM EXPENSE AS e
                        JOIN CATEGORY AS c
                            ON e.cat_id = c.cat_id
                        ORDER BY e.date_time DESC;
                    """)

        expenses = cursor.fetchall()

        return [
            {
                "exp_id": row[0],
                "date_time": row[1].isoformat(),
                "amount": float(row[2]),
                "cat_id": row[3],
                "cat_name": row[4]
            }
            for row in expenses
        ]

    finally:
        cursor.close()
        connection.close()


@app.post("/expenses")
def create_expense(expense: ExpenseCreate):
    connection = get_connection()

    try:
        cursor = connection.cursor()

        cursor.execute(
            """
            INSERT INTO EXPENSE (date_time, amount, cat_id)
            VALUES (%s, %s, %s)
            RETURNING exp_id, date_time, amount, cat_id;
            """,
            (expense.date_time, expense.amount, expense.cat_id)
        )

        row = cursor.fetchone()
        connection.commit()

        return {
            "exp_id": row[0],
            "date_time": row[1].isoformat(),
            "amount": float(row[2]),
            "cat_id": row[3]
        }

    except Exception as error:
        connection.rollback()
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )

    finally:
        cursor.close()
        connection.close()



@app.get("/categories")
def get_categories():
    connection = get_connection()

    try:
        cursor = connection.cursor()
        cursor.execute("""
            SELECT cat_id, cat_name
            FROM CATEGORY
            ORDER BY cat_id;
        """)

        rows = cursor.fetchall()

        return [
            {"cat_id": row[0], "cat_name": row[1]}
            for row in rows
        ]

    finally:
        cursor.close()
        connection.close()


@app.get("/summary")
def get_summary():
    connection = get_connection()

    try:
        cursor = connection.cursor()
        cursor.execute("""
                SELECT bud_amount
                FROM BUDGET
                WHERE bud_date >= '2026-10-01'
                  AND bud_date < '2026-11-01';
            """)

        budget_result = cursor.fetchone()
        budget = float(budget_result[0] or 0.0)

        cursor.execute("""
                select sum(amount)
                from expense
                where date_time>='2026-10-01'
                    and date_time <'2026-11-01';
            """)
        total_result = cursor.fetchone()
        total = float(total_result[0])

        remaining = budget-total

        return{
            "budget": budget,
            "total_expenses" : total,
            "remaining_budget": remaining
        }

    finally:
        cursor.close()
        connection.close()