export type DetectionType = 'trademark' | 'design' | 'copyright'
export type RiskLevel = 'high' | 'medium' | 'low' | 'pending'
export type JobStatus = 'queued' | 'processing' | 'done' | 'failed'
export type UserRole = 'user' | 'admin'
export type ReviewStatus = 'none' | 'pending' | 'approved' | 'rejected'
export type ServiceRequestType = 'appeal' | 'tro_settlement'
export type ServiceRequestStatus = 'pending' | 'reviewing' | 'waiting_user' | 'processing' | 'done'
export type UnifiedReportType = 'ip_detection' | 'appeal' | 'tro_settlement'

export interface SelectOption { value: string; label: string }
export interface AuthUser { id: number; mobile: string; name: string; role: UserRole }
export interface DetectionFormInput { detectionType: DetectionType | ''; brand: string; category: string; market: string; productLink: string; title: string; hasFile: boolean; file?: { name: string; type: string; size: number } }
export interface EvidenceItem { id: string; category: DetectionType; matched: string; source: string; similarity: number; description: string; imageUrl: string }
export interface CategoryScore { type: DetectionType; label: string; score: number; hits: number }
export interface DetectionJob { id: string; type: DetectionType; title: string; brand: string; category: string; market: string; status: JobStatus; riskLevel: RiskLevel; riskScore: number | null; createdAt: string; ownerName: string; ownerMobile: string; reviewStatus?: ReviewStatus; reviewNote?: string; fileUrl?: string }
export interface DetectionReport { id: string; jobId: string; title: string; generatedAt: string; riskLevel: RiskLevel; riskScore: number | null; summary: string; categoryScores: CategoryScore[]; evidence: EvidenceItem[]; suggestions: string[]; reviewStatus?: ReviewStatus; reviewNote?: string; reportType?: UnifiedReportType; typeLabel?: string; sourceLabel?: string; sections?: AdviceReportSection[]; nextActions?: string[] }
export interface ServiceRequestInput { requestType: ServiceRequestType; platform: string; contact: string; title?: string; issueType?: string; caseStatus?: string; storeName?: string; frozenAmount?: string; caseNumber?: string; claimant?: string; reference?: string; description?: string; fileNames?: string[] }
export interface AdviceReportSection { title: string; items: string[] }
export interface ServiceAdviceReport { title: string; summary: string; riskLevel: 'high' | 'medium' | 'low'; sections: AdviceReportSection[]; nextActions: string[]; contactHint: string; source?: 'model' | 'fallback' }
export interface ServiceRequestItem { id: string; requestType: ServiceRequestType; title: string; platform: string; status: ServiceRequestStatus; contact: string; reference: string; description: string; issueType: string; caseStatus: string; storeName: string; frozenAmount: string; caseNumber: string; claimant: string; fileNames: string[]; adviceReport?: ServiceAdviceReport | null; createdAt: string }
export interface ModelConfigItem { id: number; provider: string; modelName: string; baseUrl: string; temperature: number; maxTokens: number; enabled: boolean }
export interface ModelConfigResponse { config: ModelConfigItem | null }
export interface NotificationItem { id: number; title: string; content: string; type: string; isRead: boolean; createdAt: string }
export interface NotificationListResponse { unreadCount: number; notifications: NotificationItem[] }
export interface AdminStats { totalJobs: number; totalUsers: number; completedJobs: number; highRiskRate: number }
export interface AdminOverview extends AdminStats { totalReports: number; totalServiceRequests: number; unreadNotifications: number; pendingReviews: number }
export interface AdminUserRow { id: number; mobile: string; name: string; role: UserRole; createdAt: string; jobCount: number; reportCount: number; serviceRequestCount: number; loginCount: number; lastLoginAt: string }
export interface AdminLoginRecordRow { id: number; userId: number; mobile: string; name: string; role: UserRole; loginMethod: string; ipAddress: string; userAgent: string; createdAt: string }
export interface AdminReportRow { id: string; reportType: UnifiedReportType; typeLabel: string; title: string; ownerName: string; ownerMobile: string; riskLevel: RiskLevel; riskScore: number | null; generatedAt: string; linkId: string }
export interface AdminServiceRequestRow { id: string; requestType: ServiceRequestType; typeLabel: string; title: string; platform: string; status: ServiceRequestStatus; contact: string; ownerName: string; ownerMobile: string; createdAt: string; linkId: string }
export interface AdminNotificationRow { id: number; title: string; content: string; type: string; isRead: boolean; ownerName: string; ownerMobile: string; createdAt: string }
