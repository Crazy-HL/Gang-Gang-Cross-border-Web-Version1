from typing import Literal

from pydantic import BaseModel

DetectionType = Literal['trademark', 'design', 'copyright']
RiskLevel = Literal['high', 'medium', 'low', 'pending']
JobStatus = Literal['queued', 'processing', 'done', 'failed']
UserRole = Literal['user', 'admin']


class SelectOption(BaseModel):
    value: str
    label: str


class FileInfo(BaseModel):
    name: str
    type: str
    size: int


class DetectionFormInput(BaseModel):
    detectionType: DetectionType | Literal['']
    brand: str
    category: str
    market: str
    productLink: str
    title: str
    hasFile: bool
    file: FileInfo | None = None


class EvidenceItem(BaseModel):
    id: str
    category: DetectionType
    matched: str
    source: str
    similarity: float
    description: str
    imageUrl: str


class CategoryScore(BaseModel):
    type: DetectionType
    label: str
    score: int
    hits: int


class DetectionJob(BaseModel):
    id: str
    type: DetectionType
    title: str
    brand: str
    category: str
    market: str
    status: JobStatus
    riskLevel: RiskLevel
    riskScore: int | None
    createdAt: str
    ownerName: str
    reviewStatus: str = 'none'
    reviewNote: str = ''


class JobStatusResponse(BaseModel):
    id: str
    status: JobStatus
    riskLevel: RiskLevel
    riskScore: int | None
    reviewStatus: str = 'none'
    reviewNote: str = ''
    createdAt: str


class ModelConfigItem(BaseModel):
    id: int
    provider: str
    modelName: str
    baseUrl: str
    temperature: float
    maxTokens: int
    enabled: bool


class ModelConfigUpdateRequest(BaseModel):
    provider: str
    modelName: str
    apiKey: str = ''
    baseUrl: str = ''
    temperature: float = 0.2
    maxTokens: int = 2048
    enabled: bool = True


class ModelConfigResponse(BaseModel):
    config: ModelConfigItem | None


class DetectionReport(BaseModel):
    id: str
    jobId: str
    title: str
    generatedAt: str
    riskLevel: RiskLevel
    riskScore: int
    summary: str
    categoryScores: list[CategoryScore]
    evidence: list[EvidenceItem]
    suggestions: list[str]
    reviewStatus: str = 'none'
    reviewNote: str = ''


class NotificationItem(BaseModel):
    id: int
    title: str
    content: str
    type: str
    isRead: bool
    createdAt: str


class NotificationListResponse(BaseModel):
    unreadCount: int
    notifications: list[NotificationItem]


class UnreadCountResponse(BaseModel):
    unreadCount: int


class MarkNotificationReadResponse(BaseModel):
    ok: bool


class AdminStats(BaseModel):
    totalJobs: int
    totalUsers: int
    completedJobs: int
    highRiskRate: float


class CreateJobResponse(BaseModel):
    jobId: str
    input: DetectionFormInput


class UploadResponse(BaseModel):
    jobId: str
    fileUrl: str


class RunJobResponse(BaseModel):
    jobId: str
    status: Literal['queued']


class ReviewRequest(BaseModel):
    note: str = ''


class ReviewResponse(BaseModel):
    ok: bool
    jobId: str
    reviewStatus: str


class AdminReviewRequest(BaseModel):
    reviewStatus: Literal['approved', 'rejected']
    reviewNote: str = ''


class MobileRequest(BaseModel):
    mobile: str


class PasswordLoginRequest(BaseModel):
    mobile: str
    password: str


class CodeLoginRequest(BaseModel):
    mobile: str
    code: str


class RegisterRequest(BaseModel):
    mobile: str
    code: str
    password: str


class AuthCodeResponse(BaseModel):
    ok: bool
    debugCode: str | None = None


class AuthUser(BaseModel):
    id: int
    mobile: str
    name: str
    role: UserRole


class AuthLoginResponse(BaseModel):
    ok: bool
    token: str
    user: AuthUser | None


class AuthRegisterResponse(BaseModel):
    ok: bool
    userId: int | None = None
    token: str = ''
    user: AuthUser | None = None


class AuthMeResponse(BaseModel):
    id: int
    mobile: str
    name: str
    role: UserRole


class LogoutResponse(BaseModel):
    ok: bool
