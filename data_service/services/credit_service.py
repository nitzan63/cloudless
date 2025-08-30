import uuid
from datetime import datetime
from typing import List, Optional
from db.postgres_db import PostgresDB

class CreditService:
    def __init__(self):
        self.db = PostgresDB()

    def spend_credits(self, user_id: str, amount: int, task_id: str, description: str) -> dict:
        """Spend credits on a task"""
        try:
            # Check if user has enough credits
            current_balance = self.get_credit_balance(user_id)
            if current_balance['credits'] < amount:
                raise Exception(f"Insufficient credits. Current balance: {current_balance['credits']}, Required: {amount}")

            # Deduct credits
            new_balance = current_balance['credits'] - amount
            
            # Update user credits
            self.db.execute(
                "UPDATE users SET credits = %s, updated_at = %s WHERE id = %s",
                (new_balance, datetime.utcnow(), user_id)
            )
            
            # Record the transaction
            transaction_id = str(uuid.uuid4())
            self.db.execute(
                """
                INSERT INTO credit_transactions (id, user_id, amount, type, description, task_id, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (transaction_id, user_id, -amount, 'spend', description, task_id, datetime.utcnow())
            )

            return {
                'userId': user_id,
                'credits': new_balance,
                'lastUpdated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            raise e

    def earn_credits(self, user_id: str, amount: int, job_id: str, description: str) -> dict:
        """Earn credits from processing a job"""
        try:
            # Get current balance
            current_balance = self.get_credit_balance(user_id)
            new_balance = current_balance['credits'] + amount
            
            # Update user credits
            self.db.execute(
                "UPDATE users SET credits = %s, updated_at = %s WHERE id = %s",
                (new_balance, datetime.utcnow(), user_id)
            )
            
            # Record the transaction
            transaction_id = str(uuid.uuid4())
            self.db.execute(
                """
                INSERT INTO credit_transactions (id, user_id, amount, type, description, job_id, timestamp)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """,
                (transaction_id, user_id, amount, 'earn', description, job_id, datetime.utcnow())
            )

            return {
                'userId': user_id,
                'credits': new_balance,
                'lastUpdated': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            raise e

    def get_credit_balance(self, user_id: str) -> dict:
        """Get user's current credit balance"""
        try:
            result = self.db.execute(
                "SELECT id, credits, updated_at FROM users WHERE id = %s",
                (user_id,)
            )
            
            if not result or not result[0]:
                raise Exception("User not found")
            
            row = result[0]
            return {
                'userId': row[0],
                'credits': row[1] or 0,
                'lastUpdated': row[2].isoformat() if row[2] else datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            raise e

    def get_transaction_history(self, user_id: str) -> List[dict]:
        """Get user's credit transaction history"""
        try:
            results = self.db.execute(
                """
                SELECT id, user_id, amount, type, description, task_id, job_id, timestamp
                FROM credit_transactions 
                WHERE user_id = %s 
                ORDER BY timestamp DESC
                """,
                (user_id,)
            )
            
            if not results:
                return []
            
            transactions = []
            for row in results:
                transactions.append({
                    'id': row[0],
                    'userId': row[1],
                    'amount': row[2],
                    'type': row[3],
                    'description': row[4],
                    'taskId': row[5],
                    'jobId': row[6],
                    'timestamp': row[7].isoformat() if row[7] else datetime.utcnow().isoformat()
                })
            
            return transactions
            
        except Exception as e:
            raise e
