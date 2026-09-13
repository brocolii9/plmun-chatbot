import os
import uuid
from contextlib import asynccontextmanager
from typing import cast

from fastapi import Depends, FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session

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
    allow_origins=["*"],
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


@app.post("/api/admin/retrain")
def retrain(db: Session = Depends(get_db)):
    n = nlp.retrain_from_db(db)

    return {
        "samples_used": n,
        "trained": nlp.classifier.is_trained,
    }

@app.get("/api/admin/analytics")
def analytics(db: Session = Depends(get_db)):
    """
    Returns usage analytics computed from the messages table.
    No auth required for now — add admin auth in a later sprint.
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