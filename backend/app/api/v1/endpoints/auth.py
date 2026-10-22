"""Authentication endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password, create_access_token
from app.db.base import get_db
from app.models.user import User, UserRole
from app.models.farmer_profile import FarmerProfile, VerificationStatus
from app.models.buyer_profile import BuyerProfile
from app.schemas.auth import LoginRequest, TokenResponse
from app.schemas.user import UserCreate, UserRead, UserUpdate
from app.middleware.auth import get_current_user

router = APIRouter()


@router.post("/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def register(user_in: UserCreate, db: AsyncSession = Depends(get_db)):
    """Register a new user. Self-assignment to ADMIN role is forbidden."""
    if user_in.role == UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Cannot self-register as an administrator. Admin accounts require system provisioning.",
        )

    # Check if email is taken
    existing = await db.execute(select(User).where(User.email == user_in.email))
    if existing.scalar_one_or_none():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email address already exists.",
        )

    # Check phone if provided
    if user_in.phone:
        existing_phone = await db.execute(select(User).where(User.phone == user_in.phone))
        if existing_phone.scalar_one_or_none():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="A user with this phone number already exists.",
            )

    user = User(
        email=user_in.email,
        phone=user_in.phone,
        full_name=user_in.full_name,
        role=user_in.role,
        hashed_password=hash_password(user_in.password),
        is_active=True,
        is_verified=False,
    )
    db.add(user)
    await db.flush()

    # Automatically create the corresponding role profile
    if user.role == UserRole.FARMER:
        profile = FarmerProfile(
            user_id=user.id,
            verification_status=VerificationStatus.PENDING,
        )
        db.add(profile)
    elif user.role == UserRole.BUYER:
        b_profile = BuyerProfile(
            user_id=user.id,
            verification_status=VerificationStatus.PENDING,
        )
        db.add(b_profile)

    await db.flush()
    return user


@router.post("/login", response_model=TokenResponse)
async def login(credentials: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Authenticate user and return JWT bearer token."""
    result = await db.execute(
        select(User)
        .options(selectinload(User.farmer_profile), selectinload(User.buyer_profile))
        .where(User.email == credentials.email)
    )
    user = result.scalar_one_or_none()

    if not user or not verify_password(credentials.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    if not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account has been deactivated. Please contact support.",
        )

    token = create_access_token(
        data={
            "sub": str(user.id),
            "email": user.email,
            "role": user.role.value,
            "name": user.full_name,
        }
    )
    return TokenResponse(access_token=token, token_type="bearer")


@router.get("/me")
async def get_me(current_user: User = Depends(get_current_user), db: AsyncSession = Depends(get_db)):
    """Retrieve details and profile for the authenticated user."""
    stmt = (
        select(User)
        .options(selectinload(User.farmer_profile), selectinload(User.buyer_profile))
        .where(User.id == current_user.id)
    )
    result = await db.execute(stmt)
    user = result.scalar_one()

    resp = {
        "id": user.id,
        "email": user.email,
        "phone": user.phone,
        "full_name": user.full_name,
        "role": user.role.value,
        "is_active": user.is_active,
        "is_verified": user.is_verified,
        "created_at": user.created_at.isoformat(),
        "farmer_profile": None,
        "buyer_profile": None,
    }

    if user.farmer_profile:
        fp = user.farmer_profile
        resp["farmer_profile"] = {
            "id": fp.id,
            "farm_name": fp.farm_name,
            "farm_location": fp.farm_location,
            "district": fp.district.value if fp.district else None,
            "taluk": fp.taluk,
            "village": fp.village,
            "farm_size_acres": float(fp.farm_size_acres) if fp.farm_size_acres else None,
            "primary_crops": fp.primary_crops,
            "description": fp.description,
            "verification_status": fp.verification_status.value,
            "bank_account_verified": fp.bank_account_verified,
        }

    if user.buyer_profile:
        bp = user.buyer_profile
        resp["buyer_profile"] = {
            "id": bp.id,
            "business_name": bp.business_name,
            "business_type": bp.business_type.value if bp.business_type else None,
            "district": bp.district,
            "taluk": bp.taluk,
            "description": bp.description,
            "verification_status": bp.verification_status.value,
            "gst_number": bp.gst_number,
        }

    return resp


@router.put("/me", response_model=UserRead)
async def update_me(
    user_in: UserUpdate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """Update profile details of the authenticated user."""
    if user_in.full_name is not None:
        current_user.full_name = user_in.full_name
    if user_in.phone is not None:
        current_user.phone = user_in.phone
    await db.flush()
    return current_user
