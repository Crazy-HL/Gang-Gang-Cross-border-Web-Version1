export type DetectionType = 'trademark' | 'design' | 'copyright'
export type RiskLevel = 'high' | 'medium' | 'low' | 'pending'
export type JobStatus = 'queued' | 'processing' | 'done' | 'failed'
export type UserRole = 'user' | 'admin'

export interface SelectOption { value: string; label: string }
export interface AuthUser { id: number; mobile: string; name: string; role: UserRole }
export interface DetectionFormInput { detectionType: DetectionType | ''; brand: string; category: string; market: string; productLink: string; title: string; hasFile: boolean; file?: { name: string; type: string; size: number } }
export interface EvidenceItem { id: string; category: DetectionType; matched: string; source: string; similarity: number; description: string; imageUrl: string }
export interface CategoryScore { type: DetectionType; label: string; score: number; hits: number }
export interface DetectionJob { id: string; type: DetectionType; title: string; brand: string; category: string; market: string; status: JobStatus; riskLevel: RiskLevel; riskScore: number | null; createdAt: string; ownerName: string }
export interface DetectionReport { id: string; jobId: string; title: string; generatedAt: string; riskLevel: RiskLevel; riskScore: number; summary: string; categoryScores: CategoryScore[]; evidence: EvidenceItem[]; suggestions: string[] }
export interface AdminStats { totalJobs: number; totalUsers: number; completedJobs: number; highRiskRate: number }
