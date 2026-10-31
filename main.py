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
def get_expenses(category:str | None = None):
    connection = get_connection()

    try:
        cursor = connection.cursor()
        if category is None:
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
        else:
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
                            WHERE e.cat_id = %s
                            ORDER BY e.date_time DESC; 
                        """,(category,))    

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
    today = datetime.now()
    start_date = datetime(today.year, today.month, 1)

    if today.month == 12:
        next_month = 1
        next_year = today.year + 1
    else:
        next_month = today.month + 1
        next_year = today.year

    next_date = datetime(next_year, next_month, 1)

    try:
        cursor = None
        try:
            cursor = connection.cursor()
            cursor.execute("""
                    SELECT bud_amount
                    FROM BUDGET
                    WHERE bud_date >= %s
                      AND bud_date < %s;
                """,(start_date.date(), next_date.date()))

            budget_result = cursor.fetchone()

            if budget_result is None:
                budget = 0.0    
            else:
                budget = float(budget_result[0] or 0.0)


            cursor.execute("""
                    select sum(amount)
                    from expense
                    where date_time >=%s
                        and date_time < %s;
                """,(start_date,next_date))
        
            total_result = cursor.fetchone()
            total = float(total_result[0] or 0.0)

            if budget_result is None:
                remaining = None
            else:
                remaining = budget - total

            return{
                "budget": budget,
                "total_expenses" : total,
                "remaining_budget": remaining
            }

        finally:
            if cursor is not None:
                cursor.close()
    finally:
        connection.close()