from datetime import datetime
from enum import Enum

from sqlalchemy import Boolean, DateTime, Float, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class UserRole(str, Enum):
    user = 'user'
    admin = 'admin'


class DetectionType(str, Enum):
    trademark = 'trademark'
    design = 'design'
    copyright = 'copyright'


class JobStatus(str, Enum):
    queued = 'queued'
    processing = 'processing'
    done = 'done'
    failed = 'failed'


class RiskLevel(str, Enum):
    high = 'high'
    medium = 'medium'
    low = 'low'
    pending = 'pending'


class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    mobile: Mapped[str] = mapped_column(String(32), unique=True, index=True)
    name: Mapped[str] = mapped_column(String(80))
    password_hash: Mapped[str] = mapped_column(String(255), default='')
    role: Mapped[str] = mapped_column(String(20), default=UserRole.user.value)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    jobs: Mapped[list['Job']] = relationship(back_populates='owner')
    notifications: Mapped[list['Notification']] = relationship(back_populates='user')
    service_requests: Mapped[list['ServiceRequest']] = relationship(back_populates='owner')


class Notification(Base):
    __tablename__ = 'notifications'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)
    title: Mapped[str] = mapped_column(String(255))
    content: Mapped[str] = mapped_column(Text)
    type: Mapped[str] = mapped_column(String(32), default='system')
    is_read: Mapped[bool] = mapped_column(Boolean, default=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    user: Mapped[User] = relationship(back_populates='notifications')


class ModelConfig(Base):
    __tablename__ = 'model_configs'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    provider: Mapped[str] = mapped_column(String(32), default='openai')
    model_name: Mapped[str] = mapped_column(String(120), default='gpt-4.1-mini')
    api_key: Mapped[str] = mapped_column(Text, default='')
    base_url: Mapped[str] = mapped_column(Text, default='')
    temperature: Mapped[float] = mapped_column(Float, default=0.2)
    max_tokens: Mapped[int] = mapped_column(Integer, default=2048)
    enabled: Mapped[bool] = mapped_column(Boolean, default=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())


class VerificationCode(Base):
    __tablename__ = 'verification_codes'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    mobile: Mapped[str] = mapped_column(String(32), index=True)
    code: Mapped[str] = mapped_column(String(12))
    expires_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), index=True)
    used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class Job(Base):
    __tablename__ = 'jobs'

    id: Mapped[str] = mapped_column(String(64), primary_key=True, index=True)
    owner_id: Mapped[int | None] = mapped_column(ForeignKey('users.id'), nullable=True)
    type: Mapped[str] = mapped_column(String(32))
    title: Mapped[str] = mapped_column(String(255))
    brand: Mapped[str] = mapped_column(String(120))
    category: Mapped[str] = mapped_column(String(80))
    market: Mapped[str] = mapped_column(String(40))
    product_link: Mapped[str] = mapped_column(Text, default='')
    status: Mapped[str] = mapped_column(String(32), default=JobStatus.queued.value)
    risk_level: Mapped[str] = mapped_column(String(32), default=RiskLevel.pending.value)
    risk_score: Mapped[int | None] = mapped_column(Integer, nullable=True)
    review_status: Mapped[str] = mapped_column(String(32), default='none')
    review_note: Mapped[str] = mapped_column(Text, default='')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    owner: Mapped[User | None] = relationship(back_populates='jobs')
    files: Mapped[list['JobFile']] = relationship(back_populates='job', cascade='all, delete-orphan')
    report: Mapped['Report | None'] = relationship(back_populates='job', cascade='all, delete-orphan')


class ServiceRequest(Base):
    __tablename__ = 'service_requests'

    id: Mapped[str] = mapped_column(String(64), primary_key=True, index=True)
    owner_id: Mapped[int] = mapped_column(ForeignKey('users.id'), index=True)
    request_type: Mapped[str] = mapped_column(String(32), index=True)
    title: Mapped[str] = mapped_column(String(255))
    platform: Mapped[str] = mapped_column(String(80), index=True)
    status: Mapped[str] = mapped_column(String(32), default='pending', index=True)
    contact: Mapped[str] = mapped_column(String(80))
    reference: Mapped[str] = mapped_column(Text, default='')
    description: Mapped[str] = mapped_column(Text, default='')
    details_json: Mapped[str] = mapped_column(Text, default='{}')
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), index=True)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())

    owner: Mapped[User] = relationship(back_populates='service_requests')


class JobFile(Base):
    __tablename__ = 'job_files'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    job_id: Mapped[str] = mapped_column(ForeignKey('jobs.id'), index=True)
    filename: Mapped[str] = mapped_column(String(255))
    content_type: Mapped[str] = mapped_column(String(120), default='')
    size: Mapped[int] = mapped_column(Integer, default=0)
    file_url: Mapped[str] = mapped_column(Text)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    job: Mapped[Job] = relationship(back_populates='files')


class Report(Base):
    __tablename__ = 'reports'

    id: Mapped[str] = mapped_column(String(64), primary_key=True, index=True)
    job_id: Mapped[str] = mapped_column(ForeignKey('jobs.id'), unique=True, index=True)
    title: Mapped[str] = mapped_column(String(255))
    generated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    risk_level: Mapped[str] = mapped_column(String(32))
    risk_score: Mapped[int] = mapped_column(Integer)
    summary: Mapped[str] = mapped_column(Text)
    suggestions_json: Mapped[str] = mapped_column(Text, default='[]')

    job: Mapped[Job] = relationship(back_populates='report')
    category_scores: Mapped[list['CategoryScore']] = relationship(back_populates='report', cascade='all, delete-orphan')
    evidence: Mapped[list['Evidence']] = relationship(back_populates='report', cascade='all, delete-orphan')


class CategoryScore(Base):
    __tablename__ = 'category_scores'

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    report_id: Mapped[str] = mapped_column(ForeignKey('reports.id'), index=True)
    type: Mapped[str] = mapped_column(String(32))
    label: Mapped[str] = mapped_column(String(80))
    score: Mapped[int] = mapped_column(Integer)
    hits: Mapped[int] = mapped_column(Integer)

    report: Mapped[Report] = relationship(back_populates='category_scores')


class Evidence(Base):
    __tablename__ = 'evidence'

    id: Mapped[str] = mapped_column(String(64), primary_key=True, index=True)
    report_id: Mapped[str] = mapped_column(ForeignKey('reports.id'), index=True)
    category: Mapped[str] = mapped_column(String(32))
    matched: Mapped[str] = mapped_column(String(255))
    source: Mapped[str] = mapped_column(String(120))
    similarity: Mapped[float] = mapped_column(Float)
    description: Mapped[str] = mapped_column(Text)
    image_url: Mapped[str] = mapped_column(Text)

    report: Mapped[Report] = relationship(back_populates='evidence')
