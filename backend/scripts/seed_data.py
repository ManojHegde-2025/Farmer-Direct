"""Seed demonstration data for FarmerDirect.

Idempotent: Safe to run multiple times without duplicating records.
All benchmark prices are strictly categorized as DEMO_DATA.
"""

import asyncio
from datetime import date, datetime, timedelta, timezone
from decimal import Decimal

from sqlalchemy import select
from app.db.base import async_session_factory, engine, Base
from app.core.security import hash_password
from app.models.user import User, UserRole
from app.models.farmer_profile import FarmerProfile, District, VerificationStatus
from app.models.buyer_profile import BuyerProfile, BusinessType
from app.models.commodity import Commodity, CommodityUnit
from app.models.listing import Listing, QualityGrade, ListingStatus
from app.models.buyer_requirement import BuyerRequirement
from app.models.reference_price import ReferencePrice, PriceClassification
from app.models.offer import Offer, OfferStatus
from app.models.order import Order, OrderStatus, FulfilmentMethod
from app.models.payment import Payment, PaymentMethod, PaymentStatus
from app.models.delivery import Delivery, DeliveryMethod, DeliveryStatus, CostBorneBy
from app.models.review import Review


async def seed():
    print("🌱 Seeding FarmerDirect demonstration data...")

    # Ensure tables exist
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with async_session_factory() as db:
        # 1. ADMIN USER
        admin_email = "admin@farmerdirect.kar.gov.in"
        res = await db.execute(select(User).where(User.email == admin_email))
        admin = res.scalar_one_or_none()
        if not admin:
            admin = User(
                email=admin_email,
                phone="+919845012345",
                full_name="District Agriculture Officer (Admin)",
                role=UserRole.ADMIN,
                hashed_password=hash_password("Admin@FarmerDirect2026"),
                is_active=True,
                is_verified=True,
            )
            db.add(admin)
            await db.flush()
            print("  Created Admin user")

        # 2. COMMODITIES
        commodities_data = [
            {
                "name": "Arecanut",
                "name_kn": "ಅಡಿಕೆ",
                "category": "Commercial Plantation",
                "unit": CommodityUnit.KG,
                "description": "Chali, Rashi, and whole processed betel nut cultivated extensively in coastal Karnataka.",
                "icon": "nut",
            },
            {
                "name": "Coconut",
                "name_kn": "ತೆಂಗಿನಕಾಯಿ",
                "category": "Plantation Produce",
                "unit": CommodityUnit.COUNT,
                "description": "Mature dry dehusked coconuts and tender coconuts from coastal groves.",
                "icon": "palmtree",
            },
            {
                "name": "Paddy / Rice",
                "name_kn": "ಭತ್ತ / ಅಕ್ಕಿ",
                "category": "Cereal Grain",
                "unit": CommodityUnit.QUINTAL,
                "description": "Coastal varieties including Jyothi, Jaya, and red boiled rice (Kaje Akki).",
                "icon": "wheat",
            },
            {
                "name": "Banana",
                "name_kn": "ಬಾಳೆಹಣ್ಣು",
                "category": "Fruit Crop",
                "unit": CommodityUnit.KG,
                "description": "Robusta, Cavendish, Nendran, and Elakki varieties harvested directly from plantations.",
                "icon": "banana",
            },
            {
                "name": "Black Pepper",
                "name_kn": "ಕರಿಮೆಣಸು",
                "category": "Spices",
                "unit": CommodityUnit.KG,
                "description": "High-piperine garbled black pepper intercropped with arecanut.",
                "icon": "flame",
            },
            {
                "name": "Cashew Nut",
                "name_kn": "ಗೋಡಂಬಿ",
                "category": "Cash Crop",
                "unit": CommodityUnit.KG,
                "description": "Raw unpeeled cashew nuts sourced from Dakshina Kannada and Udupi orchards.",
                "icon": "sun",
            },
            {
                "name": "Vegetables (Coastal Assortment)",
                "name_kn": "ತರಕಾರಿ",
                "category": "Fresh Produce",
                "unit": CommodityUnit.KG,
                "description": "Local seasonal vegetables including ridge gourd, brinjal, okra, and green chillies.",
                "icon": "carrot",
            },
        ]

        commodities = {}
        for c_data in commodities_data:
            res = await db.execute(select(Commodity).where(Commodity.name == c_data["name"]))
            c = res.scalar_one_or_none()
            if not c:
                c = Commodity(**c_data, is_active=True)
                db.add(c)
                await db.flush()
            commodities[c.name] = c
        print(f"  Configured {len(commodities)} commodities")

        # 3. FARMERS
        farmers_data = [
            {
                "email": "mahabaleshwara.bhat@agri.in",
                "phone": "+919845111001",
                "full_name": "Mahabaleshwara Bhat",
                "farm_name": "Ganesh Kripa Farm",
                "farm_location": "Miyar Post, Karkala",
                "district": District.UDUPI,
                "taluk": "Karkala",
                "village": "Miyar",
                "farm_size_acres": Decimal("4.5"),
                "primary_crops": "Arecanut, Black Pepper, Banana",
                "description": "Practicing multi-tier natural intercropping for over 22 years in Karkala taluk.",
                "verification_status": VerificationStatus.APPROVED,
                "is_verified": True,
            },
            {
                "email": "sanjeeva.shetty@agri.in",
                "phone": "+919845111002",
                "full_name": "Sanjeeva Shetty",
                "farm_name": "Netravati Bio Plantation",
                "farm_location": "Ujire, Belthangady",
                "district": District.DAKSHINA_KANNADA,
                "taluk": "Belthangady",
                "village": "Ujire",
                "farm_size_acres": Decimal("8.0"),
                "primary_crops": "Coconut, Arecanut, Cashew",
                "description": "Dedicated plantation producer along the foothills of Western Ghats.",
                "verification_status": VerificationStatus.APPROVED,
                "is_verified": True,
            },
            {
                "email": "ramesh.poojary@agri.in",
                "phone": "+919845111003",
                "full_name": "Ramesh Poojary",
                "farm_name": "Varahi Riverfront Fields",
                "farm_location": "Basrur, Kundapura",
                "district": District.UDUPI,
                "taluk": "Kundapura",
                "village": "Basrur",
                "farm_size_acres": Decimal("3.2"),
                "primary_crops": "Paddy / Rice, Seasonal Vegetables",
                "description": "Cultivating traditional red boiled paddy with river basin canal irrigation.",
                "verification_status": VerificationStatus.APPROVED,
                "is_verified": True,
            },
            {
                "email": "dayananda.nayak@agri.in",
                "phone": "+919845111004",
                "full_name": "Dayananda Nayak",
                "farm_name": "Kumaradhara Orchards",
                "farm_location": "Bettampady, Puttur",
                "district": District.DAKSHINA_KANNADA,
                "taluk": "Puttur",
                "village": "Bettampady",
                "farm_size_acres": Decimal("5.0"),
                "primary_crops": "Cashew Nut, Cocoa",
                "description": "Smallholder farmer focusing on rainfed organic cashew nut harvest.",
                "verification_status": VerificationStatus.SUBMITTED,
                "is_verified": False,
            },
        ]

        farmers = {}
        for f_info in farmers_data:
            res = await db.execute(select(User).where(User.email == f_info["email"]))
            u = res.scalar_one_or_none()
            if not u:
                u = User(
                    email=f_info["email"],
                    phone=f_info["phone"],
                    full_name=f_info["full_name"],
                    role=UserRole.FARMER,
                    hashed_password=hash_password("Farmer@123456"),
                    is_active=True,
                    is_verified=f_info["is_verified"],
                )
                db.add(u)
                await db.flush()

                prof = FarmerProfile(
                    user_id=u.id,
                    farm_name=f_info["farm_name"],
                    farm_location=f_info["farm_location"],
                    district=f_info["district"],
                    taluk=f_info["taluk"],
                    village=f_info["village"],
                    farm_size_acres=f_info["farm_size_acres"],
                    primary_crops=f_info["primary_crops"],
                    description=f_info["description"],
                    verification_status=f_info["verification_status"],
                    bank_account_verified=f_info["is_verified"],
                )
                db.add(prof)
                await db.flush()
            farmers[f_info["full_name"]] = u
        print(f"  Configured {len(farmers)} farmer accounts")

        # 4. BUYERS
        buyers_data = [
            {
                "email": "procurement@mangalorespices.com",
                "phone": "+919845222001",
                "full_name": "Anand Prabhu (Mangalore Spices)",
                "business_name": "Mangalore Spices & Trading Co.",
                "business_type": BusinessType.WHOLESALER,
                "district": "DAKSHINA_KANNADA",
                "taluk": "Mangaluru",
                "gst_number": "29ABCDE1234F1Z5",
                "description": "Licensed bulk procurement firm sourcing regional arecanut and pepper for national distribution.",
                "is_verified": True,
            },
            {
                "email": "sourcing@coastaloils.com",
                "phone": "+919845222002",
                "full_name": "Kishore Hegde (Coastal Agro Processing)",
                "business_name": "Coastal Agro Mills & Processing Ltd",
                "business_type": BusinessType.PROCESSOR,
                "district": "UDUPI",
                "taluk": "Udupi",
                "gst_number": "29XYZAB5678C1Z2",
                "description": "Oil extraction and copra processing mill requiring regular supplies of mature coconut.",
                "is_verified": True,
            },
            {
                "email": "retail@krishnaorganics.in",
                "phone": "+919845222003",
                "full_name": "Ganesh Shenoy (Krishna Retail Mart)",
                "business_name": "Krishna Retail Mart",
                "business_type": BusinessType.RETAILER,
                "district": "UDUPI",
                "taluk": "Kundapura",
                "gst_number": "29QWERT9876A1Z9",
                "description": "Direct fresh produce supermarkets in Kundapura and Brahmavara.",
                "is_verified": True,
            },
        ]

        buyers = {}
        for b_info in buyers_data:
            res = await db.execute(select(User).where(User.email == b_info["email"]))
            u = res.scalar_one_or_none()
            if not u:
                u = User(
                    email=b_info["email"],
                    phone=b_info["phone"],
                    full_name=b_info["full_name"],
                    role=UserRole.BUYER,
                    hashed_password=hash_password("Buyer@123456"),
                    is_active=True,
                    is_verified=b_info["is_verified"],
                )
                db.add(u)
                await db.flush()

                b_prof = BuyerProfile(
                    user_id=u.id,
                    business_name=b_info["business_name"],
                    business_type=b_info["business_type"],
                    district=b_info["district"],
                    taluk=b_info["taluk"],
                    description=b_info["description"],
                    verification_status=VerificationStatus.APPROVED if b_info["is_verified"] else VerificationStatus.PENDING,
                    gst_number=b_info["gst_number"],
                )
                db.add(b_prof)
                await db.flush()
            buyers[b_info["full_name"]] = u
        print(f"  Configured {len(buyers)} commercial buyer accounts")

        # 5. MARKET REFERENCE PRICES (All marked DEMO_DATA)
        today = date.today()
        ref_prices = [
            {
                "commodity_id": commodities["Arecanut"].id,
                "variety": "Chali / White Betel Nut",
                "market": "APMC Karkala",
                "locality": "Karkala Town, Udupi",
                "price": Decimal("460.00"),
                "unit": CommodityUnit.KG,
                "observation_date": today - timedelta(days=2),
                "source": "APMC Mandi Daily Bulletin (Indicative Demo Record)",
                "source_url": "https://agmarknet.gov.in",
                "classification": PriceClassification.DEMO_DATA,
                "quality_grade": "Grade A",
            },
            {
                "commodity_id": commodities["Arecanut"].id,
                "variety": "Rashi / Red Betel Nut",
                "market": "CAMPCO Mangalore",
                "locality": "Mangaluru, DK",
                "price": Decimal("485.00"),
                "unit": CommodityUnit.KG,
                "observation_date": today - timedelta(days=1),
                "source": "CAMPCO Price Circular (Demo Benchmark)",
                "source_url": "https://campco.org",
                "classification": PriceClassification.DEMO_DATA,
                "quality_grade": "Standard",
            },
            {
                "commodity_id": commodities["Coconut"].id,
                "variety": "Mature Dehusked",
                "market": "APMC Kundapura",
                "locality": "Kundapura, Udupi",
                "price": Decimal("28.50"),
                "unit": CommodityUnit.COUNT,
                "observation_date": today - timedelta(days=1),
                "source": "Coconut Development Board Regional Tracker (Demo Data)",
                "source_url": "https://coconutboard.gov.in",
                "classification": PriceClassification.DEMO_DATA,
                "quality_grade": "Grade A",
            },
            {
                "commodity_id": commodities["Paddy / Rice"].id,
                "variety": "Jaya Paddy (Boiled)",
                "market": "APMC Kundapura",
                "locality": "Basrur Market Yard",
                "price": Decimal("2250.00"),
                "unit": CommodityUnit.QUINTAL,
                "observation_date": today - timedelta(days=3),
                "source": "Department of Agricultural Marketing Karnataka (Demo Data)",
                "source_url": "https://agrimarketing.kar.nic.in",
                "classification": PriceClassification.DEMO_DATA,
                "quality_grade": "Fair Average Quality",
            },
            {
                "commodity_id": commodities["Black Pepper"].id,
                "variety": "Garbled Bold",
                "market": "APMC Mangalore",
                "locality": "Bunder, Mangaluru",
                "price": Decimal("595.00"),
                "unit": CommodityUnit.KG,
                "observation_date": today - timedelta(days=2),
                "source": "Spices Board India Regional Indicative (Demo Data)",
                "source_url": "https://indianspices.com",
                "classification": PriceClassification.DEMO_DATA,
                "quality_grade": "Grade A",
            },
        ]

        for rp in ref_prices:
            res = await db.execute(
                select(ReferencePrice).where(
                    ReferencePrice.commodity_id == rp["commodity_id"],
                    ReferencePrice.market == rp["market"],
                    ReferencePrice.variety == rp["variety"],
                )
            )
            if not res.scalar_one_or_none():
                ref = ReferencePrice(**rp)
                db.add(ref)
                await db.flush()
        print(f"  Configured {len(ref_prices)} market reference price benchmarks")

        # 6. PRODUCE LISTINGS
        listings_data = [
            {
                "farmer_id": farmers["Mahabaleshwara Bhat"].id,
                "commodity_id": commodities["Arecanut"].id,
                "title": "Sun-Dried Chali Arecanut - 100 kg Lot (Grade A)",
                "description": "Naturally cured under coastal sun, free from moisture damage or fungus. Sorted manually.",
                "variety": "Chali Whole Dried",
                "quality_grade": QualityGrade.A,
                "quantity": Decimal("100.00"),
                "available_quantity": Decimal("100.00"),
                "unit": CommodityUnit.KG,
                "price_per_unit": Decimal("450.00"),
                "min_order_quantity": Decimal("25.00"),
                "status": ListingStatus.ACTIVE,
                "harvest_date": today - timedelta(days=20),
                "available_from": today - timedelta(days=5),
                "available_until": today + timedelta(days=45),
                "pickup_location": "Miyar Farm Depot, Karkala Taluk",
                "delivery_available": True,
                "delivery_radius_km": 50,
            },
            {
                "farmer_id": farmers["Sanjeeva Shetty"].id,
                "commodity_id": commodities["Coconut"].id,
                "title": "Mature High-Oil Coconuts (500 Count Fresh Harvest)",
                "description": "Large-size coastal tall coconuts with thick meat. Ideal for oil processing and dry retail.",
                "variety": "West Coast Tall",
                "quality_grade": QualityGrade.A,
                "quantity": Decimal("500.00"),
                "available_quantity": Decimal("500.00"),
                "unit": CommodityUnit.COUNT,
                "price_per_unit": Decimal("28.00"),
                "min_order_quantity": Decimal("100.00"),
                "status": ListingStatus.ACTIVE,
                "harvest_date": today - timedelta(days=4),
                "available_from": today,
                "available_until": today + timedelta(days=30),
                "pickup_location": "Ujire Estate Gate, Belthangady",
                "delivery_available": True,
                "delivery_radius_km": 60,
            },
            {
                "farmer_id": farmers["Ramesh Poojary"].id,
                "commodity_id": commodities["Paddy / Rice"].id,
                "title": "Kundapura Jaya Red Paddy - 20 Quintals",
                "description": "Recently harvested monsoon crop, well dried, free of chaff. Traditional staple boiled variety.",
                "variety": "Jaya Paddy",
                "quality_grade": QualityGrade.A,
                "quantity": Decimal("20.00"),
                "available_quantity": Decimal("20.00"),
                "unit": CommodityUnit.QUINTAL,
                "price_per_unit": Decimal("2200.00"),
                "min_order_quantity": Decimal("5.00"),
                "status": ListingStatus.ACTIVE,
                "harvest_date": today - timedelta(days=15),
                "available_from": today,
                "available_until": today + timedelta(days=60),
                "pickup_location": "Basrur Village Center, Kundapura",
                "delivery_available": False,
            },
            {
                "farmer_id": farmers["Mahabaleshwara Bhat"].id,
                "commodity_id": commodities["Black Pepper"].id,
                "title": "Estate Grown Black Pepper (Garbled Grade A) - 50 kg",
                "description": "High aroma and pungency. Intercropped on areca palms, hand-picked and cleaned.",
                "variety": "Panniyur-1",
                "quality_grade": QualityGrade.A,
                "quantity": Decimal("50.00"),
                "available_quantity": Decimal("50.00"),
                "unit": CommodityUnit.KG,
                "price_per_unit": Decimal("580.00"),
                "min_order_quantity": Decimal("10.00"),
                "status": ListingStatus.ACTIVE,
                "harvest_date": today - timedelta(days=30),
                "available_from": today,
                "available_until": today + timedelta(days=90),
                "pickup_location": "Miyar Post, Karkala",
                "delivery_available": True,
                "delivery_radius_km": 40,
            },
            {
                "farmer_id": farmers["Dayananda Nayak"].id,
                "commodity_id": commodities["Cashew Nut"].id,
                "title": "Raw Unpeeled Cashew Nuts - 200 kg Lot",
                "description": "Direct orchard harvest awaiting administrative review.",
                "variety": "Vengurla-4",
                "quality_grade": QualityGrade.B,
                "quantity": Decimal("200.00"),
                "available_quantity": Decimal("200.00"),
                "unit": CommodityUnit.KG,
                "price_per_unit": Decimal("120.00"),
                "min_order_quantity": Decimal("50.00"),
                "status": ListingStatus.PENDING_REVIEW,
                "harvest_date": today - timedelta(days=10),
                "available_from": today,
                "available_until": today + timedelta(days=30),
                "pickup_location": "Bettampady, Puttur",
                "delivery_available": False,
            },
        ]

        listings = {}
        for l_data in listings_data:
            res = await db.execute(select(Listing).where(Listing.title == l_data["title"]))
            l = res.scalar_one_or_none()
            if not l:
                l = Listing(**l_data)
                db.add(l)
                await db.flush()
            listings[l_data["title"]] = l
        print(f"  Configured {len(listings)} produce listings")

        # 7. BUYER PROCUREMENT REQUIREMENTS
        reqs_data = [
            {
                "buyer_id": buyers["Anand Prabhu (Mangalore Spices)"].id,
                "commodity_id": commodities["Arecanut"].id,
                "variety_preference": "Chali Whole Dried",
                "quality_preference": "A",
                "quantity_needed": Decimal("80.00"),
                "max_price_per_unit": Decimal("470.00"),
                "delivery_location": "Bunder Warehouse, Mangaluru",
                "delivery_district": "DAKSHINA_KANNADA",
                "needed_by": today + timedelta(days=25),
                "is_active": True,
            },
            {
                "buyer_id": buyers["Kishore Hegde (Coastal Agro Processing)"].id,
                "commodity_id": commodities["Coconut"].id,
                "variety_preference": "West Coast Tall",
                "quality_preference": "A",
                "quantity_needed": Decimal("300.00"),
                "max_price_per_unit": Decimal("30.00"),
                "delivery_location": "Manipal Industrial Area, Udupi",
                "delivery_district": "UDUPI",
                "needed_by": today + timedelta(days=15),
                "is_active": True,
            },
        ]

        for r_data in reqs_data:
            res = await db.execute(
                select(BuyerRequirement).where(
                    BuyerRequirement.buyer_id == r_data["buyer_id"],
                    BuyerRequirement.commodity_id == r_data["commodity_id"],
                )
            )
            if not res.scalar_one_or_none():
                req = BuyerRequirement(**r_data)
                db.add(req)
                await db.flush()
        print(f"  Configured {len(reqs_data)} buyer procurement requirements")

        await db.commit()
        print("✅ Demonstration database seeded successfully!")


if __name__ == "__main__":
    asyncio.run(seed())
