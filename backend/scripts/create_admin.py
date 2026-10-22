"""CLI command to securely provision an Administrator account for FarmerDirect."""

import asyncio
import getpass
import sys

from sqlalchemy import select
from app.db.base import async_session_factory, engine, Base
from app.core.security import hash_password
from app.models.user import User, UserRole


async def create_admin():
    print("🌾 FarmerDirect - Administrator Account Provisioning")
    print("====================================================")

    # Ensure tables exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    # Prompt or take arguments
    if len(sys.argv) >= 3:
        email = sys.argv[1]
        password = sys.argv[2]
        full_name = sys.argv[3] if len(sys.argv) > 3 else "Administrator"
    else:
        email = input("Admin Email: ").strip()
        if not email:
            print("Error: Email cannot be empty")
            return
        full_name = input("Full Name (e.g. Lead Officer): ").strip() or "Administrator"
        password = getpass.getpass("Password (min 8 chars): ")
        if len(password) < 8:
            print("Error: Password must be at least 8 characters")
            return

    async with async_session_factory() as db:
        res = await db.execute(select(User).where(User.email == email))
        existing = res.scalar_one_or_none()
        if existing:
            print(f"User with email '{email}' already exists. Updating role to ADMIN...")
            existing.role = UserRole.ADMIN
            existing.hashed_password = hash_password(password)
            existing.is_active = True
            existing.is_verified = True
        else:
            admin_user = User(
                email=email,
                full_name=full_name,
                role=UserRole.ADMIN,
                hashed_password=hash_password(password),
                is_active=True,
                is_verified=True,
            )
            db.add(admin_user)

        await db.commit()
        print(f"✅ Administrator '{email}' successfully provisioned!")


if __name__ == "__main__":
    asyncio.run(create_admin())
