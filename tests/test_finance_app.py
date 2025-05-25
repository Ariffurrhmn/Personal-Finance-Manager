"""
Unit tests for the Finance Management Application
"""

import unittest
import tempfile
import os
from datetime import datetime
from models import User, Account, Category, Transaction, ValidationError
from database import Database, DatabaseError

class TestModels(unittest.TestCase):
    """Test the data models"""
    
    def test_user_validation(self):
        """Test user validation"""
        # Valid user
        user = User(name="John Doe", email="john@example.com", password="password123")
        user.validate()  # Should not raise
        
        # Invalid email
        user.email = "invalid-email"
        with self.assertRaises(ValidationError):
            user.validate()
        
        # Empty name
        user.email = "john@example.com"
        user.name = ""
        with self.assertRaises(ValidationError):
            user.validate()
        
        # Short password
        user.name = "John Doe"
        user.password = "123"
        with self.assertRaises(ValidationError):
            user.validate()
    
    def test_account_validation(self):
        """Test account validation"""
        # Valid account
        account = Account(user_id=1, name="My Bank", balance=100.0, account_type="Bank")
        account.validate()  # Should not raise
        
        # Invalid account type
        account.account_type = "Invalid"
        with self.assertRaises(ValidationError):
            account.validate()
        
        # Negative balance
        account.account_type = "Bank"
        account.balance = -50.0
        with self.assertRaises(ValidationError):
            account.validate()
        
        # Empty name
        account.balance = 100.0
        account.name = ""
        with self.assertRaises(ValidationError):
            account.validate()
    
    def test_category_validation(self):
        """Test category validation"""
        # Valid category
        category = Category(user_id=1, name="Food", category_type="Expense")
        category.validate()  # Should not raise
        
        # Invalid category type
        category.category_type = "Invalid"
        with self.assertRaises(ValidationError):
            category.validate()
        
        # Empty name
        category.category_type = "Expense"
        category.name = ""
        with self.assertRaises(ValidationError):
            category.validate()
    
    def test_transaction_validation(self):
        """Test transaction validation"""
        # Valid transaction
        transaction = Transaction(
            user_id=1, account_id=1, category_id=1, 
            amount=100.0, transaction_type="Expense"
        )
        transaction.validate()  # Should not raise
        
        # Negative amount
        transaction.amount = -50.0
        with self.assertRaises(ValidationError):
            transaction.validate()
        
        # Invalid transaction type
        transaction.amount = 100.0
        transaction.transaction_type = "Invalid"
        with self.assertRaises(ValidationError):
            transaction.validate()
        
        # Transfer without destination
        transaction.transaction_type = "Transfer"
        transaction.to_account_id = None
        with self.assertRaises(ValidationError):
            transaction.validate()
        
        # Transfer to same account
        transaction.to_account_id = transaction.account_id
        with self.assertRaises(ValidationError):
            transaction.validate()

class TestDatabase(unittest.TestCase):
    """Test database operations"""
    
    def setUp(self):
        """Set up test database"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False)
        self.temp_db.close()
        self.db = Database(self.temp_db.name)
    
    def tearDown(self):
        """Clean up test database"""
        self.db.close()
        os.unlink(self.temp_db.name)
    
    def test_user_operations(self):
        """Test user CRUD operations"""
        # Create user
        user = User(name="Test User", email="test@example.com", password="password123")
        user_id = self.db.create_user(user)
        self.assertIsNotNone(user_id)
        
        # Authenticate user
        auth_user = self.db.authenticate_user("test@example.com", "password123")
        self.assertIsNotNone(auth_user)
        self.assertEqual(auth_user.name, "Test User")
        
        # Wrong password
        auth_user = self.db.authenticate_user("test@example.com", "wrongpassword")
        self.assertIsNone(auth_user)
        
        # Get user by ID
        retrieved_user = self.db.get_user(user_id)
        self.assertIsNotNone(retrieved_user)
        self.assertEqual(retrieved_user.name, "Test User")
        
        # Duplicate email should fail
        duplicate_user = User(name="Another User", email="test@example.com", password="password123")
        with self.assertRaises(ValidationError):
            self.db.create_user(duplicate_user)
    
    def test_account_operations(self):
        """Test account CRUD operations"""
        # Create user first
        user = User(name="Test User", email="test@example.com", password="password123")
        user_id = self.db.create_user(user)
        
        # Create account
        account = Account(user_id=user_id, name="Test Account", balance=100.0, account_type="Bank")
        account_id = self.db.create_account(account)
        self.assertIsNotNone(account_id)
        
        # Get user accounts (should include default accounts + new one)
        accounts = self.db.get_user_accounts(user_id)
        self.assertGreaterEqual(len(accounts), 2)  # 2 default + 1 new
        
        # Get specific account
        retrieved_account = self.db.get_account(account_id, user_id)
        self.assertIsNotNone(retrieved_account)
        self.assertEqual(retrieved_account.name, "Test Account")
        
        # Update account
        retrieved_account.name = "Updated Account"
        success = self.db.update_account(retrieved_account)
        self.assertTrue(success)
        
        # Verify update
        updated_account = self.db.get_account(account_id, user_id)
        self.assertEqual(updated_account.name, "Updated Account")
        
        # Delete account
        success = self.db.delete_account(account_id, user_id)
        self.assertTrue(success)
        
        # Verify deletion
        deleted_account = self.db.get_account(account_id, user_id)
        self.assertIsNone(deleted_account)
    
    def test_category_operations(self):
        """Test category CRUD operations"""
        # Create user first
        user = User(name="Test User", email="test@example.com", password="password123")
        user_id = self.db.create_user(user)
        
        # Create category
        category = Category(user_id=user_id, name="Test Category", category_type="Expense")
        category_id = self.db.create_category(category)
        self.assertIsNotNone(category_id)
        
        # Get user categories (should include default categories + new one)
        categories = self.db.get_user_categories(user_id)
        self.assertGreater(len(categories), 5)  # 5 default + 1 new
        
        # Delete category
        success = self.db.delete_category(category_id, user_id)
        self.assertTrue(success)
    
    def test_transaction_operations(self):
        """Test transaction CRUD operations"""
        # Create user first
        user = User(name="Test User", email="test@example.com", password="password123")
        user_id = self.db.create_user(user)
        
        # Get default accounts and categories
        accounts = self.db.get_user_accounts(user_id)
        categories = self.db.get_user_categories(user_id)
        
        expense_category = next(c for c in categories if c.category_type == "Expense")
        income_category = next(c for c in categories if c.category_type == "Income")
        account = accounts[0]
        
        # Test income transaction first (since account starts with 0 balance)
        income_transaction = Transaction(
            user_id=user_id,
            account_id=account.account_id,
            category_id=income_category.category_id,
            amount=100.0,
            description="Test income",
            transaction_type="Income"
        )
        
        # Get initial balance (should be 0)
        initial_balance = account.balance
        self.assertEqual(initial_balance, 0.0)
        
        # Create income transaction
        self.db.create_transaction(income_transaction)
        
        # Verify balance was updated
        updated_account = self.db.get_account(account.account_id, user_id)
        self.assertEqual(updated_account.balance, initial_balance + 100.0)
        
        # Now test expense transaction
        expense_transaction = Transaction(
            user_id=user_id,
            account_id=account.account_id,
            category_id=expense_category.category_id,
            amount=50.0,
            description="Test expense",
            transaction_type="Expense"
        )
        
        transaction_id = self.db.create_transaction(expense_transaction)
        self.assertIsNotNone(transaction_id)
        
        # Verify balance was updated (100 - 50 = 50)
        final_account = self.db.get_account(account.account_id, user_id)
        self.assertEqual(final_account.balance, 50.0)
        
        # Test transfer transaction
        if len(accounts) >= 2:
            to_account = accounts[1]
            initial_to_balance = to_account.balance
            
            transfer_transaction = Transaction(
                user_id=user_id,
                account_id=account.account_id,
                amount=25.0,
                description="Test transfer",
                transaction_type="Transfer",
                to_account_id=to_account.account_id
            )
            
            self.db.create_transaction(transfer_transaction)
            
            # Verify both accounts were updated
            from_account_updated = self.db.get_account(account.account_id, user_id)
            to_account_updated = self.db.get_account(to_account.account_id, user_id)
            
            self.assertEqual(from_account_updated.balance, 25.0)  # 50 - 25
            self.assertEqual(to_account_updated.balance, initial_to_balance + 25.0)  # 0 + 25
        
        # Get transactions
        transactions = self.db.get_user_transactions(user_id)
        self.assertGreaterEqual(len(transactions), 2)  # At least income and expense
        
        # Test balance summary
        summary = self.db.get_user_balance_summary(user_id)
        self.assertIn('total_balance', summary)
        self.assertIn('monthly_income', summary)
        self.assertIn('monthly_expense', summary)
        self.assertIn('monthly_cashflow', summary)

    def test_account_limit(self):
        """Test account creation limit"""
        # Create user first
        user = User(name="Test User", email="test@example.com", password="password123")
        user_id = self.db.create_user(user)
        
        # User starts with 2 default accounts, can add 3 more (total 5)
        for i in range(3):
            account = Account(user_id=user_id, name=f"Test Account {i+1}", 
                            balance=0.0, account_type="Cash")
            account_id = self.db.create_account(account)
            self.assertIsNotNone(account_id)
        
        # Now we should have 5 accounts total, trying to add 6th should fail
        excess_account = Account(user_id=user_id, name="Excess Account", 
                               balance=0.0, account_type="Bank")
        
        with self.assertRaises(ValidationError) as context:
            self.db.create_account(excess_account)
        
        self.assertIn("Maximum 5 accounts allowed", str(context.exception))

class TestIntegration(unittest.TestCase):
    """Integration tests"""
    
    def setUp(self):
        """Set up test database"""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False)
        self.temp_db.close()
        self.db = Database(self.temp_db.name)
    
    def tearDown(self):
        """Clean up test database"""
        self.db.close()
        os.unlink(self.temp_db.name)
    
    def test_complete_user_workflow(self):
        """Test complete user workflow"""
        # 1. Register user
        user = User(name="Integration Test", email="integration@test.com", password="password123")
        user_id = self.db.create_user(user)
        
        # 2. Login user
        auth_user = self.db.authenticate_user("integration@test.com", "password123")
        self.assertIsNotNone(auth_user)
        
        # 3. User should have default accounts and categories
        accounts = self.db.get_user_accounts(user_id)
        categories = self.db.get_user_categories(user_id)
        self.assertGreaterEqual(len(accounts), 2)
        self.assertGreaterEqual(len(categories), 5)
        
        # 4. Add custom account
        custom_account = Account(user_id=user_id, name="Custom Account", balance=0.0, account_type="Cash")
        custom_account_id = self.db.create_account(custom_account)
        
        # 5. Add custom category
        custom_category = Category(user_id=user_id, name="Custom Category", category_type="Expense")
        custom_category_id = self.db.create_category(custom_category)
        
        # 6. Make transactions
        income_category = next(c for c in categories if c.category_type == "Income")
        
        # Add income
        income_transaction = Transaction(
            user_id=user_id,
            account_id=custom_account_id,
            category_id=income_category.category_id,
            amount=1000.0,
            description="Initial income",
            transaction_type="Income"
        )
        self.db.create_transaction(income_transaction)
        
        # Add expense
        expense_transaction = Transaction(
            user_id=user_id,
            account_id=custom_account_id,
            category_id=custom_category_id,
            amount=200.0,
            description="Test expense",
            transaction_type="Expense"
        )
        self.db.create_transaction(expense_transaction)
        
        # 7. Verify final state
        updated_account = self.db.get_account(custom_account_id, user_id)
        self.assertEqual(updated_account.balance, 800.0)  # 1000 - 200
        
        transactions = self.db.get_user_transactions(user_id)
        self.assertGreaterEqual(len(transactions), 2)
        
        summary = self.db.get_user_balance_summary(user_id)
        self.assertGreater(summary['total_balance'], 0)
        self.assertGreater(summary['monthly_income'], 0)
        self.assertGreater(summary['monthly_expense'], 0)

if __name__ == '__main__':
    # Run tests using the modern approach
    unittest.main(verbosity=2) 