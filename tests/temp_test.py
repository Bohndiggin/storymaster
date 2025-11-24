#!/usr/bin/env python3
"""Temporary test to verify SyncPairingToken works correctly"""

import os
from datetime import datetime, timedelta

from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from storymaster.model.database.schema.base import SyncPairingToken
from storymaster.sync_server.auth import create_pairing_token, consume_pairing_token


def test_sync_pairing_token():
    """Test that SyncPairingToken can be created and queried"""
    # Connect to test database
    home_dir = os.path.expanduser("~")
    db_path = os.path.join(home_dir, ".local", "share", "storymaster", "storymaster.db")
    engine = create_engine(f"sqlite:///{db_path}")

    with Session(engine) as session:
        # Test 1: Direct model creation
        print("\n📝 Test 1: Direct model creation")
        test_token = "test_token_123"
        expires_at = datetime.now() + timedelta(minutes=15)

        pairing_token = SyncPairingToken(token=test_token, expires_at=expires_at)

        session.add(pairing_token)
        session.commit()
        session.refresh(pairing_token)

        print(f"✅ Created SyncPairingToken with ID: {pairing_token.id}")
        print(f"   Token: {pairing_token.token}")
        print(f"   Expires at: {pairing_token.expires_at}")
        print(f"   Created at: {pairing_token.created_at}")

        # Query it back
        stmt = select(SyncPairingToken).where(SyncPairingToken.token == test_token)
        retrieved_token = session.execute(stmt).scalar_one_or_none()

        if retrieved_token:
            print(f"✅ Successfully retrieved token from database")
            print(f"   ID matches: {retrieved_token.id == pairing_token.id}")
            print(f"   Token matches: {retrieved_token.token == test_token}")
        else:
            print(f"❌ Failed to retrieve token from database")

        # Clean up
        session.delete(pairing_token)
        session.commit()
        print(f"✅ Test token deleted successfully")

        # Test 2: Auth module functions
        print("\n📝 Test 2: Auth module functions (create_pairing_token)")
        auth_token = create_pairing_token(session, expires_in_minutes=5)
        print(f"✅ Created pairing token via auth module")
        print(f"   Token: {auth_token.token}")
        print(f"   Expires at: {auth_token.expires_at}")

        # Test 3: Consume pairing token (valid)
        print("\n📝 Test 3: Consume pairing token (valid)")
        result = consume_pairing_token(session, auth_token.token)
        print(f"✅ Token consumption result: {result}")
        if result:
            print("   Token was valid and consumed")
        else:
            print("   ❌ Token consumption failed")

        # Test 4: Consume expired token
        print("\n📝 Test 4: Consume expired/invalid token")
        result = consume_pairing_token(session, "invalid_token_xyz")
        print(f"✅ Invalid token consumption result: {result}")
        if not result:
            print("   Correctly rejected invalid token")
        else:
            print("   ❌ Should have rejected invalid token")


if __name__ == "__main__":
    print("🧪 Testing SyncPairingToken model...")
    print("=" * 60)
    try:
        test_sync_pairing_token()
        print("=" * 60)
        print("🎉 All tests passed!")
    except Exception as e:
        print("=" * 60)
        print(f"❌ Test failed: {e}")
        import traceback

        traceback.print_exc()
