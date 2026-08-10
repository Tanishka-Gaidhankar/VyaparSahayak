from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from sqlalchemy import (
    create_engine, Column, Integer, Float, String, ForeignKey
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
import os
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Initialize FastAPI app
app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# -----------------------
# DATABASE SETUP
# -----------------------
DATABASE_URL = os.getenv("SUPABASE_DB_URL")

# Fallback to SQLite if no Supabase URL is provided
if not DATABASE_URL:
    DATABASE_URL = "sqlite:///./app.db"
    connect_args = {"check_same_thread": False}
else:
    # Ensure correct protocol for SQLAlchemy (postgres:// -> postgresql://)
    if DATABASE_URL.startswith("postgres://"):
        DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    connect_args = {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


# -----------------------
# DATABASE MODELS
# -----------------------
class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True)
    startup_profile_id = Column(Integer, ForeignKey("startup_profiles.id"), nullable=True)  # Link to profile
    name = Column(String, nullable=False)
    category = Column(String, nullable=True)
    cost_price = Column(Float, default=0.0)
    selling_price = Column(Float, default=0.0)
    inventory = Column(Integer, default=0)
    units_per_batch = Column(Integer, nullable=True)
    production_cost = Column(Float, nullable=True)
    production_time = Column(Float, nullable=True)


class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True)
    startup_profile_id = Column(Integer, ForeignKey("startup_profiles.id"), nullable=True)  # Link to profile
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    channel = Column(String, nullable=True)
    quantity = Column(Integer, default=0)
    selling_price = Column(Float, default=0.0)
    customer_ref = Column(String, nullable=True)
    date = Column(String, nullable=True)


class ProductionBatch(Base):
    __tablename__ = "production_batches"

    id = Column(Integer, primary_key=True)
    startup_profile_id = Column(Integer, ForeignKey("startup_profiles.id"), nullable=True)  # Link to profile
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    units_produced = Column(Integer, default=0)
    production_cost = Column(Float, default=0.0)
    production_time = Column(Float, nullable=True)
    date = Column(String, nullable=True)


class StartupProfile(Base):
    __tablename__ = "startup_profiles"

    id = Column(Integer, primary_key=True)
    business_name = Column(String, nullable=False)
    business_type = Column(String, nullable=True)
    industry = Column(String, nullable=True)
    location = Column(String, nullable=True)
    growth_stage = Column(String, nullable=True)
    msme_registered = Column(Integer, default=0)
    annual_revenue = Column(Float, default=0.0)


class Scheme(Base):
    __tablename__ = "schemes"

    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False)
    description = Column(String, nullable=True)
    eligibility_json = Column(String, nullable=True)
    benefits = Column(String, nullable=True)
    source = Column(String, nullable=True)


class RiskReport(Base):
    __tablename__ = "risk_reports"

    id = Column(Integer, primary_key=True)
    startup_profile_id = Column(Integer, ForeignKey("startup_profiles.id"), nullable=False)
    risk_level = Column(String, nullable=True)  # Low, Medium, High
    risks_json = Column(String, nullable=True)  # JSON array of detected risks
    ai_actions_json = Column(String, nullable=True)  # JSON array of AI recommendations
    timestamp = Column(String, nullable=True)
    api_key_hash = Column(String, nullable=True)  # Hash of OpenAI API key used


Base.metadata.create_all(bind=engine)


# -----------------------
# SCHEMAS
# -----------------------
class ProductCreate(BaseModel):
    name: str
    cost_price: float = 0.0
    selling_price: float = 0.0
    inventory: int = 0
    category: str | None = None
    units_per_batch: int | None = None
    production_cost: float | None = None
    production_time: float | None = None
    startup_profile_id: int | None = None


class ProductionBatchCreate(BaseModel):
    units_produced: int
    production_cost: float
    production_time: float | None = None
    date: str | None = None
    startup_profile_id: int | None = None


class StartupProfileCreate(BaseModel):
    business_name: str
    business_type: str
    industry: str
    location: str
    growth_stage: str | None = None
    msme_registered: bool = False
    annual_revenue: float = 0.0


class SchemeOut(BaseModel):
    id: int
    name: str
    description: str | None
    benefits: str | None
    source: str | None

    class Config:
        from_attributes = True


class RiskDetectionRequest(BaseModel):
    startup_profile_id: int
    groq_api_key: str | None = None  # Optional - backend uses env vars if not provided


class RiskReportOut(BaseModel):
    id: int
    startup_profile_id: int
    risk_level: str
    risks_json: str | None
    ai_actions_json: str | None
    timestamp: str | None

    class Config:
        from_attributes = True


class ProductOut(BaseModel):
    id: int
    startup_profile_id: int | None
    name: str
    category: str | None
    cost_price: float
    selling_price: float
    inventory: int

    class Config:
        from_attributes = True


class OrderCreate(BaseModel):
    product_id: int
    channel: str
    quantity: int
    customer_ref: str | None = None
    startup_profile_id: int | None = None


# -----------------------
# PRODUCT ENDPOINTS
# -----------------------
@app.post("/products", response_model=ProductOut)
def create_product(product: ProductCreate):
    db = SessionLocal()

    new_product = Product(
        name=product.name,
        cost_price=product.cost_price,
        selling_price=product.selling_price,
        inventory=product.inventory,
        category=product.category,
        units_per_batch=product.units_per_batch,
        production_cost=product.production_cost,
        production_time=product.production_time,
        startup_profile_id=product.startup_profile_id,
    )

    db.add(new_product)
    db.commit()
    db.refresh(new_product)
    db.close()

    return new_product



@app.get("/products")
def list_products(profile_id: int | None = None):
    db = SessionLocal()
    query = db.query(Product)
    if profile_id:
        query = query.filter(Product.startup_profile_id == profile_id)
    products = query.all()
    db.close()
    return products


# -----------------------
# PRODUCTION BATCHES & INSIGHTS
# -----------------------
@app.post("/products/{product_id}/production_batches")
def create_production_batch(product_id: int, batch: ProductionBatchCreate):
    db = SessionLocal()
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        db.close()
        raise HTTPException(status_code=404, detail="Product not found")

    new_batch = ProductionBatch(
        product_id=product_id,
        units_produced=batch.units_produced,
        production_cost=batch.production_cost,
        production_time=batch.production_time,
        date=batch.date,
        startup_profile_id=batch.startup_profile_id,
    )

    db.add(new_batch)
    db.commit()
    db.refresh(new_batch)
    db.close()

    return {
        "message": "Production batch recorded",
        "batch_id": new_batch.id,
    }



@app.get("/products/{product_id}/production_insights")
def production_insights(product_id: int):
    db = SessionLocal()
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        db.close()
        raise HTTPException(status_code=404, detail="Product not found")

    batches = db.query(ProductionBatch).filter(ProductionBatch.product_id == product_id).all()

    # Aggregate batch metrics
    total_units = sum(b.units_produced for b in batches)
    total_prod_cost = sum(b.production_cost for b in batches)
    total_prod_time = sum((b.production_time or 0) for b in batches)

    # Fallbacks if no batches
    if total_units == 0:
        # Use product-level defaults when available
        total_units = product.units_per_batch or 0
        total_prod_cost = (product.production_cost or 0) if product.units_per_batch else 0
        total_prod_time = product.production_time or 0

    production_cost_per_unit = (total_prod_cost / total_units) if total_units > 0 else 0
    units_per_hour = (total_units / total_prod_time) if total_prod_time > 0 else 0

    # Cost leakage heuristic: production cost per unit significantly higher than product cost_price
    cost_leakage = False
    leakage_factor = None
    if product.cost_price and production_cost_per_unit > 0:
        leakage_factor = production_cost_per_unit / (product.cost_price or 1)
        cost_leakage = leakage_factor > 1.1

    # Margin impact: include production cost per unit into total unit cost
    unit_total_cost = (product.cost_price or 0) + production_cost_per_unit
    margin = (product.selling_price or 0) - unit_total_cost
    margin_percent = (margin / (product.selling_price or 1)) * 100 if product.selling_price else 0

    db.close()

    return {
        "product_id": product.id,
        "name": product.name,
        "production_cost_per_unit": production_cost_per_unit,
        "units_per_hour": units_per_hour,
        "total_units_produced": total_units,
        "total_production_cost": total_prod_cost,
        "cost_leakage": cost_leakage,
        "leakage_factor": leakage_factor,
        "unit_total_cost": unit_total_cost,
        "margin": margin,
        "margin_percent": margin_percent,
    }


# -----------------------
# ORDER ENDPOINTS (MASTER MODULE)
# -----------------------
# -----------------------
# ORDER ENDPOINTS (MASTER MODULE)
# -----------------------
@app.post("/orders")
def create_order(order: OrderCreate):
    db = SessionLocal()

    product = db.query(Product).filter(Product.id == order.product_id).first()

    if not product:
        db.close()
        raise HTTPException(status_code=404, detail="Product not found")

    if product.inventory < order.quantity:
        db.close()
        raise HTTPException(status_code=400, detail="Insufficient inventory")

    # Create order
    new_order = Order(
        product_id=order.product_id,
        channel=order.channel,
        quantity=order.quantity,
        selling_price=product.selling_price,
        customer_ref=order.customer_ref,
        startup_profile_id=order.startup_profile_id,
    )

    # Update inventory (master write)
    product.inventory -= order.quantity

    db.add(new_order)
    db.commit()
    db.refresh(new_order)
    remaining = product.inventory
    db.close()

    return {
        "message": "Order created successfully",
        "order_id": new_order.id,
        "remaining_inventory": remaining
    }


# -----------------------
# DASHBOARD METRICS (READ-ONLY, DERIVED)
# -----------------------
@app.get("/dashboard")
def dashboard_metrics(profile_id: int | None = None):
    """Enhanced dashboard: aggregate revenue, orders, inventory, best/worst products, channels."""
    db = SessionLocal()

    orders_query = db.query(Order)
    products_query = db.query(Product)
    
    if profile_id:
        orders_query = orders_query.filter(Order.startup_profile_id == profile_id)
        products_query = products_query.filter(Product.startup_profile_id == profile_id)
        
    orders = orders_query.all()
    products = products_query.all()

    total_revenue = sum(o.quantity * o.selling_price for o in orders)
    total_orders = len(orders)
    total_inventory = sum(p.inventory for p in products)
    total_units_sold = sum(o.quantity for o in orders)

    # Calculate profit (all products' cost price vs actual selling price)
    total_profit = 0
    for order in orders:
        product = next((p for p in products if p.id == order.product_id), None)
        if product:
            cost = (product.cost_price or 0) * order.quantity
            revenue_item = order.quantity * order.selling_price
            total_profit += (revenue_item - cost)

    # Best & worst products by revenue
    product_revenue = {}
    for order in orders:
        product_revenue.setdefault(order.product_id, 0)
        product_revenue[order.product_id] += order.quantity * order.selling_price

    best_product = None
    worst_product = None
    if product_revenue:
        best_id = max(product_revenue, key=product_revenue.get)
        worst_id = min(product_revenue, key=product_revenue.get)
        best_product = next((p for p in products if p.id == best_id), None)
        worst_product = next((p for p in products if p.id == worst_id), None)

    db.close()

    return {
        "summary": {
            "total_revenue": total_revenue,
            "total_profit": total_profit,
            "total_orders": total_orders,
            "total_units_sold": total_units_sold,
            "total_inventory": total_inventory,
        },
        "best_product": {
            "id": best_product.id,
            "name": best_product.name,
            "revenue": product_revenue.get(best_product.id, 0),
        } if best_product else None,
        "worst_product": {
            "id": worst_product.id,
            "name": worst_product.name,
            "revenue": product_revenue.get(worst_product.id, 0),
        } if worst_product else None,
    }


@app.get("/dashboard/channel-wise")
def dashboard_channel_wise(profile_id: int | None = None):
    """Channel-wise revenue, order count, and units sold breakdown."""
    db = SessionLocal()
    
    query = db.query(Order)
    if profile_id:
        query = query.filter(Order.startup_profile_id == profile_id)
        
    orders = query.all()

    channel_data = {}
    for order in orders:
        channel = order.channel or "unknown"
        if channel not in channel_data:
            channel_data[channel] = {
                "revenue": 0,
                "orders": 0,
                "units": 0,
            }
        channel_data[channel]["revenue"] += order.quantity * order.selling_price
        channel_data[channel]["orders"] += 1
        channel_data[channel]["units"] += order.quantity

    db.close()

    # Convert to array format expected by frontend
    channel_array = [
        {
            "channel": channel,
            "revenue": data["revenue"],
            "orders": data["orders"],
        }
        for channel, data in channel_data.items()
    ]

    return channel_array


@app.get("/dashboard/products")
def dashboard_products(profile_id: int | None = None):
    """Product-wise performance summary: revenue, profit, inventory, velocity."""
    db = SessionLocal()
    
    products_query = db.query(Product)
    orders_query = db.query(Order)
    
    if profile_id:
        products_query = products_query.filter(Product.startup_profile_id == profile_id)
        orders_query = orders_query.filter(Order.startup_profile_id == profile_id)
        
    products = products_query.all()
    orders = orders_query.all()

    product_stats = []
    for product in products:
        product_orders = [o for o in orders if o.product_id == product.id]
        revenue = sum(o.quantity * o.selling_price for o in product_orders)
        units_sold = sum(o.quantity for o in product_orders)
        cost = units_sold * (product.cost_price or 0)
        profit = revenue - cost
        velocity = units_sold / (len(product_orders) if product_orders else 1)

        # Calculate margin percentage
        margin = (profit / revenue * 100) if revenue > 0 else 0
        orders_count = len(product_orders)

        product_stats.append({
            "id": product.id,
            "name": product.name,
            "category": product.category,
            "revenue": revenue,
            "units_sold": units_sold,
            "profit": profit,
            "margin": margin,
            "orders": orders_count,
            "inventory": product.inventory,
            "velocity": velocity,
        })

    db.close()

    return product_stats




@app.get("/dashboard/sales-summary")
def dashboard_sales_summary(profile_id: int | None = None):
    """Sales summary: total revenue, profit margin, average order value, inventory health."""
    db = SessionLocal()
    
    orders_query = db.query(Order)
    products_query = db.query(Product)
    
    if profile_id:
        orders_query = orders_query.filter(Order.startup_profile_id == profile_id)
        products_query = products_query.filter(Product.startup_profile_id == profile_id)
        
    orders = orders_query.all()
    products = products_query.all()

    total_revenue = sum(o.quantity * o.selling_price for o in orders)
    total_cost = sum(
        (next((p.cost_price or 0 for p in products if p.id == o.product_id), 0)) * o.quantity
        for o in orders
    )
    total_profit = total_revenue - total_cost
    profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0

    avg_order_value = (total_revenue / len(orders)) if orders else 0

    # Inventory health: percentage of inventory still available
    total_possible_inventory = sum(
        (p.inventory + sum(o.quantity for o in orders if o.product_id == p.id))
        for p in products
    )
    current_inventory = sum(p.inventory for p in products)
    inventory_health = (current_inventory / total_possible_inventory * 100) if total_possible_inventory > 0 else 0

    db.close()

    # Convert inventory health to descriptive string
    if inventory_health >= 70:
        inventory_health_status = "Good"
    elif inventory_health >= 40:
        inventory_health_status = "Medium"
    else:
        inventory_health_status = "Low"

    return {
        "total_revenue": total_revenue,
        "total_profit": total_profit,
        "margin_percent": profit_margin,
        "avg_order_value": avg_order_value,
        "total_orders": len(orders),
        "inventory_health": inventory_health_status,
    }



@app.get("/products/{product_id}/performance")
def product_performance(product_id: int):
    db = SessionLocal()
    product = db.query(Product).filter(Product.id == product_id).first()
    if not product:
        db.close()
        raise HTTPException(status_code=404, detail="Product not found")

    orders = db.query(Order).filter(Order.product_id == product_id).all()

    revenue = sum(o.quantity * o.selling_price for o in orders)
    units_sold = sum(o.quantity for o in orders)
    profit = revenue - (units_sold * (product.cost_price or 0))
    velocity = units_sold / (1 if len(orders) == 0 else len(orders))

    db.close()

    return {
        "product_id": product.id,
        "name": product.name,
        "revenue": revenue,
        "units_sold": units_sold,
        "profit": profit,
        "velocity": velocity,
        "inventory": product.inventory,
    }


@app.get("/favicon.ico")
async def favicon():
    return FileResponse("frontend/favicon.ico")


# -----------------------
# SCHEMES & OPPORTUNITIES (PROFILE-DRIVEN MATCHING)
# -----------------------
import json
import os


def init_schemes_db():
    """Load schemes from schemes.json into database if not already loaded."""
    db = SessionLocal()
    existing_count = db.query(Scheme).count()
    if existing_count > 0:
        db.close()
        return

    scheme_file = os.path.join(os.path.dirname(__file__), "schemes.json")
    if not os.path.exists(scheme_file):
        db.close()
        return

    with open(scheme_file, "r") as f:
        schemes_data = json.load(f)

    for scheme_data in schemes_data:
        scheme = Scheme(
            name=scheme_data.get("name"),
            description=scheme_data.get("description"),
            eligibility_json=json.dumps(scheme_data.get("eligibility", {})),
            benefits=scheme_data.get("benefits"),
            source=scheme_data.get("source"),
        )
        db.add(scheme)

    db.commit()
    db.close()


# Initialize schemes on startup
init_schemes_db()


@app.post("/startup-profile")
def create_startup_profile(profile: StartupProfileCreate):
    """Create or update startup profile for scheme matching."""
    db = SessionLocal()

    # For now, create a new profile (in production, upsert based on user)
    startup = StartupProfile(
        business_name=profile.business_name,
        business_type=profile.business_type,
        industry=profile.industry,
        location=profile.location,
        growth_stage=profile.growth_stage,
        msme_registered=1 if profile.msme_registered else 0,
        annual_revenue=profile.annual_revenue,
    )

    db.add(startup)
    db.commit()
    db.refresh(startup)
    db.close()

    return {
        "id": startup.id,
        "business_name": startup.business_name,
        "message": "Startup profile created",
    }


@app.get("/startup-profile/{profile_id}")
def get_startup_profile(profile_id: int):
    """Retrieve a startup profile by ID."""
    db = SessionLocal()
    profile = db.query(StartupProfile).filter(StartupProfile.id == profile_id).first()
    if not profile:
        db.close()
        raise HTTPException(status_code=404, detail="Startup profile not found")
    
    db.close()
    
    return {
        "id": profile.id,
        "business_name": profile.business_name,
        "business_type": profile.business_type,
        "industry": profile.industry,
        "location": profile.location,
        "growth_stage": profile.growth_stage,
        "msme_registered": bool(profile.msme_registered),
        "annual_revenue": profile.annual_revenue,
    }



@app.get("/schemes")
def list_schemes():
    """List all available government schemes."""
    db = SessionLocal()
    schemes = db.query(Scheme).all()
    db.close()

    return [
        {
            "id": s.id,
            "name": s.name,
            "description": s.description,
            "benefits": s.benefits,
            "source": s.source,
        }
        for s in schemes
    ]



@app.get("/startup-profile/{profile_id}/matched-schemes")
def match_schemes(profile_id: int):
    """Match schemes based on startup profile eligibility."""
    db = SessionLocal()

    profile = db.query(StartupProfile).filter(StartupProfile.id == profile_id).first()
    if not profile:
        db.close()
        raise HTTPException(status_code=404, detail="Startup profile not found")

    schemes = db.query(Scheme).all()

    matched_schemes = []
    for scheme in schemes:
        try:
            eligibility = json.loads(scheme.eligibility_json or "{}")
        except:
            eligibility = {}

        # Matching logic: revenue range, business type, MSME status
        matches = True

        # Check revenue range
        min_revenue = eligibility.get("min_revenue", 0)
        max_revenue = eligibility.get("max_revenue", float("inf"))
        if not (min_revenue <= profile.annual_revenue <= max_revenue):
            matches = False

        # Check business type
        allowed_types = eligibility.get("business_types", ["all"])
        if "all" not in allowed_types and profile.business_type not in allowed_types:
            matches = False

        # Check MSME registration requirement
        require_msme = eligibility.get("msme_registered", False)
        if require_msme and profile.msme_registered == 0:
            matches = False

        if matches:
            matched_schemes.append(
                {
                    "scheme_id": scheme.id,
                    "name": scheme.name,
                    "description": scheme.description,
                    "benefits": scheme.benefits,
                    "source": scheme.source,
                    "eligibility_met": True,
                    "relevance": "Your profile matches this scheme",
                }
            )

    db.close()

    return matched_schemes



# -----------------------
# AI RISK & ACTION PLANNER (SKELETON)
# -----------------------


def calculate_risks(startup_profile_id: int, db) -> dict:
    """
    Analyze business data and detect risks (rule-based, no AI yet).
    Returns: {risk_level: str, risks: [list of detected risks]}
    """
    profile = db.query(StartupProfile).filter(StartupProfile.id == startup_profile_id).first()
    if not profile:
        return {"risk_level": "unknown", "risks": []}

    orders = db.query(Order).all()
    products = db.query(Product).all()
    batches = db.query(ProductionBatch).all()

    risks = []
    
    # Create lookup dictionaries for O(1) access
    from collections import defaultdict
    product_dict = {p.id: p for p in products}
    
    # Pre-aggregate data for efficiency
    product_sales = defaultdict(int)  # product_id -> units_sold
    batch_by_product = defaultdict(list)  # product_id -> [batches]

    # --- RISK 1: CHANNEL DEPENDENCY ---
    channel_revenue = {}
    for order in orders:
        channel = order.channel or "unknown"
        channel_revenue.setdefault(channel, 0)
        channel_revenue[channel] += order.quantity * order.selling_price
        
        # Track sales per product
        product_sales[order.product_id] += order.quantity

    total_revenue = sum(channel_revenue.values())
    if total_revenue > 0:
        for channel, revenue in channel_revenue.items():
            pct = (revenue / total_revenue) * 100
            if pct > 60:
                risks.append({
                    "type": "channel_dependency",
                    "severity": "high",
                    "message": f"{pct:.1f}% revenue from '{channel}' channel. Diversify to reduce risk.",
                })
            elif pct > 40:
                risks.append({
                    "type": "channel_concentration",
                    "severity": "medium",
                    "message": f"{pct:.1f}% revenue from '{channel}'. Consider expanding channels.",
                })

    # Pre-aggregate batches by product
    for batch in batches:
        batch_by_product[batch.product_id].append(batch)

    # --- RISK 2: LOW INVENTORY TURNOVER ---
    for product in products:
        units_sold = product_sales.get(product.id, 0)
        if product.inventory > 0 and units_sold == 0:
            risks.append({
                "type": "dead_stock",
                "severity": "medium",
                "message": f"Product '{product.name}' has {product.inventory} units with no sales. Consider markdowns or discontinuation.",
            })

    # --- RISK 3: PRODUCTION COST LEAKAGE ---
    for product in products:
        product_batches = batch_by_product.get(product.id, [])
        if product_batches:
            total_units = sum(b.units_produced for b in product_batches)
            total_cost = sum(b.production_cost for b in product_batches)
            cost_per_unit = (total_cost / total_units) if total_units > 0 else 0
            if cost_per_unit > (product.cost_price or 0) * 1.1:
                risks.append({
                    "type": "production_leakage",
                    "severity": "high",
                    "message": f"Production cost per unit ({cost_per_unit:.2f}) exceeds expected ({product.cost_price:.2f}). Review batch efficiency.",
                })

    # --- RISK 4: LOW PROFIT MARGIN ---
    total_profit = 0
    for order in orders:
        product = product_dict.get(order.product_id)
        if product:
            cost = (product.cost_price or 0) * order.quantity
            revenue_item = order.quantity * order.selling_price
            total_profit += (revenue_item - cost)

    if total_revenue > 0:
        margin_pct = (total_profit / total_revenue) * 100
        if margin_pct < 10:
            risks.append({
                "type": "low_margin",
                "severity": "high",
                "message": f"Overall profit margin is {margin_pct:.1f}%. Target 20-30% for sustainability.",
            })
        elif margin_pct < 15:
            risks.append({
                "type": "thin_margin",
                "severity": "medium",
                "message": f"Profit margin is {margin_pct:.1f}%. Increase prices or reduce costs.",
            })

    # Determine overall risk level
    high_count = sum(1 for r in risks if r.get("severity") == "high")
    medium_count = sum(1 for r in risks if r.get("severity") == "medium")

    if high_count >= 2:
        risk_level = "high"
    elif high_count >= 1 or medium_count >= 3:
        risk_level = "medium"
    else:
        risk_level = "low"

    return {
        "risk_level": risk_level,
        "risks": risks,
        "summary": f"Detected {len(risks)} risks: {high_count} high, {medium_count} medium.",
    }


# -----------------------
# AI RISK & ACTION PLANNER
# -----------------------
try:
    import cohere
    Cohere = cohere.ClientV2
except ImportError:
    cohere = None
    Cohere = None

async def generate_ai_action_plan(profile_name: str, risks_data: dict, business_snapshot: dict) -> dict:
    """
    Generate actionable advice using Cohere API.
    """
    cohere_key = os.getenv("COHERE_API_KEY")

    # Construct Prompt
    snapshot_text = json.dumps(business_snapshot, indent=2)
    risks_text = json.dumps(risks_data.get('risks', []), indent=2)
    
    prompt = f"""
    You are a strategic business advisor for an Indian MSME/Startup named '{profile_name}'.
    
    ## Business Snapshot (ACTUAL DATA - USE THESE EXACT NUMBERS)
    {snapshot_text}

    ## Identified Risks (BASED ON ACTUAL DATA)
    {risks_text}
    
    ## Task
    Provide a concise, data-driven Action Plan (3-5 items) based on the ACTUAL numbers above.
    
    CRITICAL REQUIREMENTS:
    1. Reference SPECIFIC numbers from the Business Snapshot (e.g., "Your current margin is {business_snapshot.get('margin_percent', 0):.1f}%")
    2. Mention actual channel names and their revenue if available
    3. Reference specific product names and inventory levels
    4. Base all recommendations on the actual data provided, not generic advice
    
    Format each action as:
    **[Action Title]** (Impact: High/Medium, Timeline: X weeks)
    - [Specific step with actual numbers/names from the data]
    - [Expected outcome with quantified target]
    
    Example format:
    **Diversify Revenue Channels** (Impact: High, Timeline: 3-4 weeks)
    - Currently 65% of ₹50,000 revenue comes from Amazon channel - reduce to <40%
    - Target: Add 2 new channels to generate ₹15,000 additional monthly revenue
    """

    # Try Cohere
    if cohere_key and Cohere:
        try:
            print(f"[DEBUG] Using Cohere API with key: {cohere_key[:10]}...")
            client = Cohere(api_key=cohere_key)
            
            response = client.chat(
                model="command-r-plus-08-2024",
                messages=[
                    {"role": "system", "content": "You are a helpful business advisor for Indian MSMEs."},
                    {"role": "user", "content": prompt}
                ]
            )
            
            content = response.message.content[0].text
            print(f"[DEBUG] Cohere response received: {len(content)} chars")
            return {
                "success": True,
                "actions": content,
                "model": "command-r-plus-08-2024"
            }
        except Exception as e:
            print(f"[ERROR] Cohere Error: {e}")
            import traceback
            traceback.print_exc()

    # Fallback Mock
    print(f"[WARNING] No Cohere API key found or API failed. Cohere key exists: {bool(cohere_key)}")
    return {
        "success": False,
        "actions": """
        **AI SERVICE UNAVAILABLE - SHOWING MOCK INSIGHTS**
        
        1. **Diversify Channels** (Impact: High)
           - Your production data shows reliance on single channels. Expand to local retail.
           
        2. **Optimize Inventory** (Impact: Medium)
           - Inventory levels need balancing against current sales velocity.
           
        *(To enable real AI, please set COHERE_API_KEY in backend environment)*
        """,
        "model": "mock-fallback"
    }


@app.post("/risk-analysis")
async def analyze_risks_and_plan(request: RiskDetectionRequest):
    """
    Detect risks + Call AI with full Context
    """
    db = SessionLocal()

    # 1. Calculate Rule-Based Risks
    risk_analysis = calculate_risks(request.startup_profile_id, db)
    
    # 2. Gather Business Snapshot (Re-using existing logic functions would be ideal, but for now we inline simple fetches)
    # Fetch aggregates to pass to AI
    profile = db.query(StartupProfile).filter(StartupProfile.id == request.startup_profile_id).first()
    if not profile:
        db.close()
        raise HTTPException(status_code=404, detail="Startup profile not found")

    # Reuse dashboard logic for snapshot
    # Note: efficient way is to refactor dashboard_metrics into a helper, but we'll do a quick fetch here
    orders = db.query(Order).filter(Order.startup_profile_id == request.startup_profile_id).all()
    products = db.query(Product).filter(Product.startup_profile_id == request.startup_profile_id).all()
    
    total_rev = sum(o.quantity * o.selling_price for o in orders)
    total_profit = 0
    
    # Optimize: Create product lookup dictionary
    product_dict = {p.id: p for p in products}
    
    # Simple profit approx
    for o in orders:
        p = product_dict.get(o.product_id)
        if p:
            total_profit += (o.selling_price - (p.cost_price or 0)) * o.quantity

    # Channel breakdown
    channel_revenue = {}
    for order in orders:
        channel = order.channel or "unknown"
        channel_revenue.setdefault(channel, 0)
        channel_revenue[channel] += order.quantity * order.selling_price
    
    # Top products by revenue
    product_revenue = {}
    for order in orders:
        product_revenue.setdefault(order.product_id, 0)
        product_revenue[order.product_id] += order.quantity * order.selling_price
    
    top_products = []
    if product_revenue:
        sorted_products = sorted(product_revenue.items(), key=lambda x: x[1], reverse=True)[:3]
        for prod_id, rev in sorted_products:
            prod = product_dict.get(prod_id)
            if prod:
                top_products.append({"name": prod.name, "revenue": rev})
    
    # Inventory status
    low_inventory_products = [p.name for p in products if p.inventory < 10]
    total_inventory = sum(p.inventory for p in products)

    snapshot = {
        "business_name": profile.business_name,
        "industry": profile.industry,
        "annual_revenue": profile.annual_revenue,
        "current_total_sales": total_rev,
        "estimated_profit": total_profit,
        "margin_percent": round((total_profit / total_rev * 100) if total_rev else 0, 2),
        "total_orders": len(orders),
        "products_count": len(products),
        "total_inventory_units": total_inventory,
        "channel_breakdown": channel_revenue,
        "top_products": top_products,
        "low_inventory_products": low_inventory_products[:5]  # Top 5 low stock items
    }

    # 3. Call AI (now async)
    ai_response = await generate_ai_action_plan(
        profile.business_name,
        risk_analysis,
        snapshot
    )

    # 4. Save Report
    import datetime
    
    # Create simple hash if key was passed (legacy) or just "env"
    key_hash = "env-managed"
    if request.groq_api_key and request.groq_api_key != "mock-key":
         import hashlib
         key_hash = hashlib.sha256(request.groq_api_key.encode()).hexdigest()[:8]

    report = RiskReport(
        startup_profile_id=request.startup_profile_id,
        risk_level=risk_analysis.get("risk_level"),
        risks_json=json.dumps(risk_analysis.get("risks", [])),
        ai_actions_json=json.dumps(ai_response),
        timestamp=datetime.datetime.now().isoformat(),
        api_key_hash=key_hash,
    )

    db.add(report)
    db.commit()
    db.refresh(report)
    db.close()

    return {
        "report_id": report.id,
        "startup_profile_id": request.startup_profile_id,
        "risk_level": risk_analysis.get("risk_level"),
        "risks": risk_analysis.get("risks", []),
        "risks_summary": risk_analysis.get("summary"),
        "ai_action_plan": ai_response.get("actions"),
        "ai_model": ai_response.get("model"),
    }


@app.get("/risk-analysis/{report_id}")
def get_risk_report(report_id: int):
    """Retrieve a stored risk analysis report."""
    db = SessionLocal()
    report = db.query(RiskReport).filter(RiskReport.id == report_id).first()
    if not report:
        db.close()
        raise HTTPException(status_code=404, detail="Risk report not found")

    db.close()

    return {
        "id": report.id,
        "startup_profile_id": report.startup_profile_id,
        "risk_level": report.risk_level,
        "risks": json.loads(report.risks_json or "[]"),
        "ai_action_plan": json.loads(report.ai_actions_json or "{}"),
        "timestamp": report.timestamp,
    }


# -----------------------
# AI AUDIENCE & PLATFORM MATCHING
# -----------------------
class AudienceMatchingRequest(BaseModel):
    product_name: str
    category: str
    price_range: str
    description: str
    target_country: str = "India"


class ContentOptimizationRequest(BaseModel):
    product_name: str
    product_details: str
    selected_platform: str
    target_audience: str
    category: str


@app.post("/ai/audience-matching")
async def ai_audience_matching(request: AudienceMatchingRequest):
    """
    AI-powered audience identification and platform recommendation.
    Uses SerpAPI for market research and Cohere AI for intelligent recommendations.
    """
    cohere_api_key = os.getenv("COHERE_API_KEY")
    serpapi_key = os.getenv("SERPAPI_KEY")
    
    if not cohere_api_key:
        raise HTTPException(status_code=500, detail="Cohere API key not configured")
    
    # Optional: Use SerpAPI for market research if key is available
    market_trends = ""
    if serpapi_key and serpapi_key != "your_serpapi_key_here":
        try:
            from serpapi import GoogleSearch
            params = {
                "q": f"{request.product_name} {request.category} market trends {request.target_country}",
                "api_key": serpapi_key,
                "num": 5
            }
            search = GoogleSearch(params)
            results = search.get_dict()
            
            # Extract organic results for context
            if "organic_results" in results:
                market_trends = "\n".join([
                    f"- {r.get('title', '')}: {r.get('snippet', '')}"
                    for r in results["organic_results"][:3]
                ])
        except Exception as e:
            # Continue without market trends if SerpAPI fails
            market_trends = "Market trends data unavailable"
    
    # Build AI prompt
    prompt = f"""You are an AI Product Growth Agent specializing in audience identification and platform recommendations.

Product Information:
- Name: {request.product_name}
- Category: {request.category}
- Price Range: {request.price_range}
- Description: {request.description}
- Target Country: {request.target_country}

Market Context:
{market_trends if market_trends else "No market trends data available"}

Task:
1. Identify the ideal target audience (age range, interests, buying intent, demographics)
2. Recommend the top 5 websites/platforms where this product should be promoted or listed
3. Explain WHY each platform is suitable for this specific product
4. Assign a confidence score (0-100%) for each platform recommendation
5. Suggest key keywords to use on each platform

Provide your response in the following JSON format:
{{
  "target_audience": {{
    "age_range": "18-35",
    "interests": ["fitness", "health"],
    "buying_intent": "high/medium/low",
    "demographics": "description",
    "summary": "brief summary"
  }},
  "platform_recommendations": [
    {{
      "platform": "Platform Name",
      "reason": "Why this platform is suitable",
      "confidence_score": 85,
      "keywords": ["keyword1", "keyword2", "keyword3"]
    }}
  ],
  "overall_strategy": "Brief strategy summary"
}}

Respond ONLY with valid JSON, no additional text."""

    try:
        import cohere
        client = cohere.ClientV2(api_key=cohere_api_key)
        
        response = client.chat(
            model="command-r-plus-08-2024",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert product marketing and growth strategist. Always respond with valid JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        ai_response_text = response.message.content[0].text.strip()
        
        # Parse JSON response
        try:
            ai_response = json.loads(ai_response_text)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            import re
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', ai_response_text, re.DOTALL)
            if json_match:
                ai_response = json.loads(json_match.group(1))
            else:
                raise HTTPException(status_code=500, detail="AI response was not valid JSON")
        
        return {
            "success": True,
            "product": request.product_name,
            "target_audience": ai_response.get("target_audience", {}),
            "platform_recommendations": ai_response.get("platform_recommendations", []),
            "overall_strategy": ai_response.get("overall_strategy", ""),
            "market_trends_used": bool(market_trends and market_trends != "Market trends data unavailable")
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI processing failed: {str(e)}")


@app.post("/ai/content-optimization")
async def ai_content_optimization(request: ContentOptimizationRequest):
    """
    AI-powered content generation and distribution strategy.
    Creates platform-specific optimized content and posting strategies.
    """
    cohere_api_key = os.getenv("COHERE_API_KEY")
    
    if not cohere_api_key:
        raise HTTPException(status_code=500, detail="Cohere API key not configured")
    
    # Build AI prompt
    prompt = f"""You are an AI Marketing & Distribution Assistant specializing in platform-specific content optimization.

Product Information:
- Name: {request.product_name}
- Details: {request.product_details}
- Category: {request.category}

Platform: {request.selected_platform}
Target Audience: {request.target_audience}

Task:
1. Generate optimized content for {request.selected_platform} (title, description, call-to-action)
2. Suggest the best posting/listing strategy (timing, format, frequency)
3. Highlight any compliance or risk warnings specific to this platform and product category
4. Recommend 3 specific actions to improve reach and conversion on this platform

Provide your response in the following JSON format:
{{
  "optimized_content": {{
    "title": "Platform-optimized title",
    "description": "Compelling description with keywords",
    "call_to_action": "Strong CTA",
    "hashtags_or_tags": ["tag1", "tag2"]
  }},
  "posting_strategy": {{
    "best_timing": "Specific time recommendations",
    "format": "Recommended content format",
    "frequency": "How often to post",
    "additional_tips": ["tip1", "tip2"]
  }},
  "compliance_warnings": [
    "Warning 1",
    "Warning 2"
  ],
  "action_recommendations": [
    {{
      "action": "Specific action to take",
      "expected_impact": "What this will achieve",
      "priority": "high/medium/low"
    }}
  ]
}}

Respond ONLY with valid JSON, no additional text."""

    try:
        import cohere
        client = cohere.ClientV2(api_key=cohere_api_key)
        
        response = client.chat(
            model="command-r-plus-08-2024",
            messages=[
                {
                    "role": "system",
                    "content": "You are an expert content marketing strategist with deep knowledge of platform-specific optimization. Always respond with valid JSON only."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )
        
        ai_response_text = response.message.content[0].text.strip()
        
        # Parse JSON response
        try:
            ai_response = json.loads(ai_response_text)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            import re
            json_match = re.search(r'```(?:json)?\s*(\{.*?\})\s*```', ai_response_text, re.DOTALL)
            if json_match:
                ai_response = json.loads(json_match.group(1))
            else:
                raise HTTPException(status_code=500, detail="AI response was not valid JSON")
        
        return {
            "success": True,
            "platform": request.selected_platform,
            "optimized_content": ai_response.get("optimized_content", {}),
            "posting_strategy": ai_response.get("posting_strategy", {}),
            "compliance_warnings": ai_response.get("compliance_warnings", []),
            "action_recommendations": ai_response.get("action_recommendations", [])
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"AI processing failed: {str(e)}")


# -----------------------
# FRONTEND STATIC SERVING
# -----------------------
frontend_path = os.path.join(os.path.dirname(__file__), "..", "frontend")
if os.path.exists(frontend_path):
    app.mount("/static", StaticFiles(directory=frontend_path), name="static")


@app.get("/")
async def serve_root():
    """Serve the frontend root."""
    frontend_index = os.path.join(frontend_path, "index.html")
    if os.path.exists(frontend_index):
        return FileResponse(frontend_index)
    return {"message": "VyaaparSahayak API is running. Frontend not found."}
