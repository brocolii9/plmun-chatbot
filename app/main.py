import os
import uuid
from datetime import datetime
from contextlib import asynccontextmanager
from typing import cast

from .seed import seed_if_empty, seed_admin_if_empty
from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from . import nlp
from .auth import create_token, get_principal, hash_password, verify_password
from .config import (
    CONFIDENCE_THRESHOLD,
    REGISTRAR_REFERRAL_EN,
    REGISTRAR_REFERRAL_FIL,
)
from .database import SessionLocal, get_db, init_db
from .models import Conversation, Intent, KnowledgeBase, Message, User
from .schemas import (
    ChatRequest,
    ChatResponse,
    ConversationOut,
    ConversationDetail,
    LoginRequest,
    MessageOut,
    RegisterRequest,
    TokenResponse,
)
from .seed import seed_if_empty


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    db = SessionLocal()
    try:
        seeded = seed_if_empty(db)
        seed_admin_if_empty(db)
        n = nlp.retrain_from_db(db)
        print(
            "[startup] seeded=%s nlp_samples=%d threshold=%.2f"
            % (seeded, n, CONFIDENCE_THRESHOLD)
        )
    finally:
        db.close()
    yield


app = FastAPI(
    title="PLMun Chatbot API",
    version="1.0.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://127.0.0.1:8000",
        "http://localhost:8000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.post(
    "/api/auth/register",
    response_model=TokenResponse,
    status_code=201,
)
def register(
    payload: RegisterRequest,
    db: Session = Depends(get_db),
):
    email = payload.email.lower().strip()

    if db.query(User).filter(User.email == email).first():
        raise HTTPException(
            status_code=409,
            detail="An account with this email already exists.",
        )

    user = User(
        full_name=payload.full_name.strip(),
        email=email,
        password_hash=hash_password(payload.password),
        role="student",
    )

    db.add(user)
    db.commit()
    db.refresh(user)

    user_id = str(user.id)
    full_name = cast(str, user.full_name)

    token = create_token(
        user_id,
        kind="student",
        role="student",
        full_name=full_name,
    )

    return TokenResponse(
        access_token=token,
        kind="student",
        role="student",
        full_name=full_name,
    )


@app.post("/api/auth/login", response_model=TokenResponse)
def login(
    payload: LoginRequest,
    db: Session = Depends(get_db),
):
    email = payload.email.lower().strip()

    user = (
        db.query(User)
        .filter(User.email == email)
        .first()
    )

    if not user:
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password.",
        )

    password_hash = cast(str, user.password_hash)

    if not verify_password(payload.password, password_hash):
        raise HTTPException(
            status_code=401,
            detail="Invalid email or password.",
        )

    user_id = str(user.id)
    full_name = cast(str, user.full_name)

    token = create_token(
        user_id,
        kind="student",
        role="student",
        full_name=full_name,
    )

    return TokenResponse(
        access_token=token,
        kind="student",
        role="student",
        full_name=full_name,
    )


@app.post("/api/auth/guest", response_model=TokenResponse)
def guest():
    session_id = uuid.uuid4().hex

    token = create_token(
        session_id,
        kind="guest",
        role=None,
        full_name="Guest",
    )

    return TokenResponse(
        access_token=token,
        kind="guest",
        role=None,
        full_name="Guest",
    )


@app.get("/api/auth/me")
def me(principal: dict = Depends(get_principal)):
    return {
        "kind": principal.get("kind"),
        "role": principal.get("role"),
        "full_name": principal.get("full_name"),
    }


def _conv_belongs_to(
    conv: Conversation,
    principal: dict,
) -> bool:
    if principal["kind"] == "student":
        user_id = cast(int, conv.user_id)
        return user_id == int(principal["sub"])

    if principal["kind"] == "guest":
        session_id = cast(str, conv.session_id)
        return session_id == principal["sub"]

    return False


def _new_conversation(
    db: Session,
    principal: dict,
    title: str = "New chat",
) -> Conversation:

    if principal["kind"] == "student":
        conv = Conversation(
            title=title,
            channel="web",
            user_id=int(principal["sub"]),
        )
    else:
        conv = Conversation(
            title=title,
            channel="web",
            session_id=principal["sub"],
        )

    db.add(conv)
    db.commit()
    db.refresh(conv)

    return conv


@app.get("/api/chat/suggestions")
def suggestions():
    return {
        "suggestions": [
            "How do I enroll?",
            "Where can I check my grades?",
            "How do I request a document?",
        ]
    }


@app.post(
    "/api/chat/message",
    response_model=ChatResponse,
)
def send_message(
    payload: ChatRequest,
    db: Session = Depends(get_db),
    principal: dict = Depends(get_principal),
):
    text = payload.message.strip()

    if not text:
        raise HTTPException(
            status_code=400,
            detail="Message cannot be empty.",
        )

    if payload.conversation_id:
        conv = (
            db.query(Conversation)
            .filter(
                Conversation.id == payload.conversation_id
            )
            .first()
        )

        if not conv or not _conv_belongs_to(conv, principal):
            raise HTTPException(
                status_code=404,
                detail="Conversation not found.",
            )
    else:
        title = text[:60] + (
            "..." if len(text) > 60 else ""
        )
        conv = _new_conversation(
            db,
            principal,
            title=title,
        )

    lang = nlp.detect_language(text)

    # SQLAlchemy/Pylance typing workaround
    setattr(conv, "language_used", lang)

    intent_name, confidence, passed = nlp.classify(text)
    entities = nlp.extract_entities(text)

    conversation_id = cast(int, conv.id)

    student_msg = Message(
        conversation_id=conversation_id,
        sender="student",
        text=text,
        intent_matched=intent_name,
        confidence_score=confidence,
    )

    db.add(student_msg)

    out_of_scope = False

    if passed and intent_name:
        intent_row = (
            db.query(Intent)
            .filter(Intent.name == intent_name)
            .first()
        )

        kb = None

        if intent_row:
            kb = (
                db.query(KnowledgeBase)
                .filter(
                    KnowledgeBase.id
                    == intent_row.kb_entry_id
                )
                .first()
            )

        if kb:
            answer_fil = cast(str, kb.answer_fil)
            answer_en = cast(str, kb.answer_en)

            reply = (
                answer_fil
                if lang == "fil"
                else answer_en
            )
        else:
            out_of_scope = True

            reply = (
                REGISTRAR_REFERRAL_FIL
                if lang == "fil"
                else REGISTRAR_REFERRAL_EN
            )
    else:
        out_of_scope = True

        reply = (
            REGISTRAR_REFERRAL_FIL
            if lang == "fil"
            else REGISTRAR_REFERRAL_EN
        )

    bot_msg = Message(
        conversation_id=conversation_id,
        sender="bot",
        text=reply,
        intent_matched=None,
        confidence_score=None,
    )

    db.add(bot_msg)
    db.commit()

    return ChatResponse(
        conversation_id=conversation_id,
        reply=reply,
        intent_matched=intent_name,
        confidence_score=round(confidence, 4),
        out_of_scope=out_of_scope,
        entities=entities,
    )


@app.get("/api/chat/conversations")
def list_conversations(
    db: Session = Depends(get_db),
    principal: dict = Depends(get_principal),
):
    q = db.query(Conversation)

    if principal["kind"] == "student":
        q = q.filter(
            Conversation.user_id
            == int(principal["sub"])
        )
    else:
        q = q.filter(
            Conversation.session_id
            == principal["sub"]
        )

    rows = (
        q.order_by(
            Conversation.started_at.desc()
        )
        .limit(50)
        .all()
    )

    return [
        {
            "id": cast(int, r.id),
            "title": cast(str, r.title),
            "started_at": r.started_at.isoformat(),
        }
        for r in rows
    ]


@app.get("/api/chat/conversations/{conv_id}")
def get_conversation(
    conv_id: int,
    db: Session = Depends(get_db),
    principal: dict = Depends(get_principal),
):
    conv = (
        db.query(Conversation)
        .filter(Conversation.id == conv_id)
        .first()
    )

    if not conv or not _conv_belongs_to(conv, principal):
        raise HTTPException(
            status_code=404,
            detail="Conversation not found.",
        )

    conversation_id = cast(int, conv.id)

    msgs = (
        db.query(Message)
        .filter(
            Message.conversation_id
            == conversation_id
        )
        .order_by(Message.id)
        .all()
    )

    return {
        "id": conversation_id,
        "title": cast(str, conv.title),
        "messages": [
            {
                "id": cast(int, m.id),
                "sender": cast(str, m.sender),
                "text": cast(str, m.text),
                "intent_matched": m.intent_matched,
                "confidence_score": m.confidence_score,
                "timestamp": m.timestamp.isoformat(),
            }
            for m in msgs
        ],
    }


@app.post(
    "/api/chat/conversations",
    status_code=201,
)
def new_conversation(
    db: Session = Depends(get_db),
    principal: dict = Depends(get_principal),
):
    conv = _new_conversation(db, principal)

    return {
        "id": cast(int, conv.id),
        "title": cast(str, conv.title),
        "started_at": conv.started_at.isoformat(),
    }


class RenameConversationRequest(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)


@app.put("/api/chat/conversations/{conv_id}")
def rename_conversation(
    conv_id: int,
    payload: RenameConversationRequest,
    db: Session = Depends(get_db),
    principal: dict = Depends(get_principal),
):
    conv = (
        db.query(Conversation)
        .filter(Conversation.id == conv_id)
        .first()
    )

    if not conv or not _conv_belongs_to(conv, principal):
        raise HTTPException(
            status_code=404,
            detail="Conversation not found.",
        )

    conv.title = payload.title.strip()
    db.commit()

    return {
        "id": cast(int, conv.id),
        "title": cast(str, conv.title),
    }


@app.delete("/api/chat/conversations/{conv_id}", status_code=204)
def delete_conversation(
    conv_id: int,
    db: Session = Depends(get_db),
    principal: dict = Depends(get_principal),
):
    conv = (
        db.query(Conversation)
        .filter(Conversation.id == conv_id)
        .first()
    )

    if not conv or not _conv_belongs_to(conv, principal):
        raise HTTPException(
            status_code=404,
            detail="Conversation not found.",
        )

    db.delete(conv)
    db.commit()

    return None


def _require_admin_principal(principal: dict = Depends(get_principal)) -> dict:
    if principal.get("kind") != "admin":
        raise HTTPException(status_code=403, detail="Admin access required.")
    return principal


@app.post("/api/admin/retrain")
def retrain(
    db: Session = Depends(get_db),
    principal: dict = Depends(_require_admin_principal),
):
    n = nlp.retrain_from_db(db)

    return {
        "samples_used": n,
        "trained": nlp.classifier.is_trained,
    }

@app.get("/api/admin/analytics")
def analytics(
    db: Session = Depends(get_db),
    principal: dict = Depends(_require_admin_principal),
):
    """
    Returns usage analytics computed from the messages table.
    """
    from sqlalchemy import func, desc
    from datetime import datetime, timedelta, date

    # --- Top intents (from student messages only) ---
    top_intents_rows = (
        db.query(
            Message.intent_matched,
            func.count(Message.id).label("count"),
            func.avg(Message.confidence_score).label("avg_confidence"),
        )
        .filter(Message.sender == "student")
        .filter(Message.intent_matched.isnot(None))
        .group_by(Message.intent_matched)
        .order_by(desc("count"))
        .all()
    )

    top_intents = [
        {
            "intent": row.intent_matched,
            "count": row.count,
            "avg_confidence": round(row.avg_confidence or 0, 4),
        }
        for row in top_intents_rows
    ]

    # --- Out-of-scope rate ---
    total_student_msgs = (
        db.query(func.count(Message.id))
        .filter(Message.sender == "student")
        .scalar() or 0
    )
    out_of_scope = (
        db.query(func.count(Message.id))
        .filter(Message.sender == "student")
        .filter(Message.intent_matched.is_(None))
        .scalar() or 0
    )

    # --- Total conversations ---
    total_conversations = db.query(func.count(Conversation.id)).scalar() or 0

    # --- Total users ---
    total_users = db.query(func.count(User.id)).scalar() or 0

    # --- Daily volume for last 7 days ---
    seven_days_ago = datetime.utcnow() - timedelta(days=7)
    daily_rows = (
        db.query(
            func.date(Message.timestamp).label("day"),
            func.count(Message.id).label("count"),
        )
        .filter(Message.sender == "student")
        .filter(Message.timestamp >= seven_days_ago)
        .group_by(func.date(Message.timestamp))
        .order_by("day")
        .all()
    )

    daily_volume = [
        {"date": str(row.day), "count": row.count} for row in daily_rows
    ]

    # --- Average confidence across all matched intents ---
    avg_conf = (
        db.query(func.avg(Message.confidence_score))
        .filter(Message.sender == "student")
        .filter(Message.confidence_score.isnot(None))
        .scalar()
    )

    return {
        "summary": {
            "total_conversations": total_conversations,
            "total_users": total_users,
            "total_student_messages": total_student_msgs,
            "out_of_scope_messages": out_of_scope,
            "out_of_scope_rate": round(out_of_scope / total_student_msgs, 4) if total_student_msgs else 0,
            "average_confidence": round(avg_conf or 0, 4),
        },
        "top_intents": top_intents,
        "daily_volume": daily_volume,
    }




STATIC_DIR = os.path.join(
    os.path.dirname(__file__),
    "static",
)

# =============================================================================
# ADMIN ROUTES
# =============================================================================

@app.post("/api/admin/login")
def admin_login(payload: LoginRequest, db: Session = Depends(get_db)):
    from .models import AdminUser

    email = payload.email.lower().strip()
    admin = db.query(AdminUser).filter(AdminUser.email == email).first()

    if not admin or not verify_password(payload.password, admin.password_hash):
        raise HTTPException(status_code=401, detail="Invalid admin credentials.")

    token = create_token(
        str(admin.id),
        kind="admin",
        role=admin.role,
        full_name=admin.full_name,
    )
    return TokenResponse(
        access_token=token,
        kind="admin",
        role=admin.role,
        full_name=admin.full_name,
    )


@app.get("/api/admin/me")
def admin_me(principal: dict = Depends(_require_admin_principal)):
    return {
        "id": principal.get("sub"),
        "role": principal.get("role"),
        "full_name": principal.get("full_name"),
        "kind": principal.get("kind"),
    }


# ---------- KB CRUD ----------

@app.get("/api/admin/kb")
def admin_list_kb(
    db: Session = Depends(get_db),
    principal: dict = Depends(_require_admin_principal),
):
    entries = db.query(KnowledgeBase).order_by(KnowledgeBase.id.desc()).all()
    return [
        {
            "id": e.id,
            "category": e.category,
            "question": e.question,
            "answer_en": e.answer_en,
            "answer_fil": e.answer_fil,
            "last_updated_at": e.last_updated_at.isoformat() if e.last_updated_at else None,
        }
        for e in entries
    ]


class KBPayload(BaseModel):
    category: str
    question: str
    answer_en: str
    answer_fil: str


@app.post("/api/admin/kb", status_code=201)
def admin_create_kb(
    payload: KBPayload,
    db: Session = Depends(get_db),
    principal: dict = Depends(_require_admin_principal),
):
    entry = KnowledgeBase(
        category=payload.category,
        question=payload.question,
        answer_en=payload.answer_en,
        answer_fil=payload.answer_fil,
        last_updated_at=datetime.utcnow(),
    )
    db.add(entry)
    db.commit()
    db.refresh(entry)
    return {"id": entry.id, "message": "KB entry created."}


@app.put("/api/admin/kb/{entry_id}")
def admin_update_kb(
    entry_id: int,
    payload: KBPayload,
    db: Session = Depends(get_db),
    principal: dict = Depends(_require_admin_principal),
):
    entry = db.query(KnowledgeBase).filter(KnowledgeBase.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="KB entry not found.")

    entry.category = payload.category
    entry.question = payload.question
    entry.answer_en = payload.answer_en
    entry.answer_fil = payload.answer_fil
    entry.last_updated_at = datetime.utcnow()

    db.commit()
    return {"message": "KB entry updated."}


@app.delete("/api/admin/kb/{entry_id}")
def admin_delete_kb(
    entry_id: int,
    db: Session = Depends(get_db),
    principal: dict = Depends(_require_admin_principal),
):
    entry = db.query(KnowledgeBase).filter(KnowledgeBase.id == entry_id).first()
    if not entry:
        raise HTTPException(status_code=404, detail="KB entry not found.")

    db.delete(entry)
    db.commit()
    return {"message": "KB entry deleted."}


# ---------- Conversation logs ----------

@app.get("/api/admin/logs")
def admin_logs(
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db),
    principal: dict = Depends(_require_admin_principal),
):
    total = db.query(Message).count()
    rows = (
        db.query(Message)
        .order_by(Message.id.desc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return {
        "total": total,
        "limit": limit,
        "offset": offset,
        "messages": [
            {
                "id": m.id,
                "conversation_id": m.conversation_id,
                "sender": m.sender,
                "text": m.text[:300],
                "intent_matched": m.intent_matched,
                "confidence_score": m.confidence_score,
                "timestamp": m.timestamp.isoformat(),
            }
            for m in rows
        ],
    }


# ---------- Admin page routes ----------

@app.get("/admin/login")
def admin_login_page():
    return FileResponse(os.path.join(STATIC_DIR, "admin", "login.html"))


@app.get("/admin/dashboard")
def admin_dashboard_page():
    return FileResponse(os.path.join(STATIC_DIR, "admin", "dashboard.html"))


@app.get("/admin/kb")
def admin_kb_page():
    return FileResponse(os.path.join(STATIC_DIR, "admin", "kb.html"))


@app.get("/admin/logs")
def admin_logs_page():
    return FileResponse(os.path.join(STATIC_DIR, "admin", "logs.html"))

@app.get("/")
def root():
    return FileResponse(os.path.join(STATIC_DIR, "sign_in.html"))

@app.get("/sign_in.html")
def sign_in_page():
    return FileResponse(os.path.join(STATIC_DIR, "sign_in.html"))

@app.get("/admin/analytics")
def analytics_page():
    return FileResponse(os.path.join(STATIC_DIR, "admin_analytics.html"))

app.mount(
    "/",
    StaticFiles(
        directory=STATIC_DIR,
        html=True,
    ),
    name="static",
)