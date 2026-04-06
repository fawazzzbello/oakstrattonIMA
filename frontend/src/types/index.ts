// ============================================================
// OakstrattonIMA — Shared TypeScript Types
// ============================================================

export interface PaginatedResponse<T> {
  items: T[]
  total: number
  skip: number
  limit: number
}

// --- Auth ---
export type UserRole = 'admin' | 'manager' | 'client' | 'influencer'

export interface User {
  id: number
  email: string
  full_name: string
  role: UserRole
  is_active: boolean
  is_verified: boolean
  avatar_url?: string
  phone?: string
  timezone: string
  created_at: string
  updated_at: string
  influencer_id?: number
}

export interface TokenResponse {
  access_token: string
  refresh_token: string
  token_type: string
}

// --- Influencer ---
export type InfluencerStatus = 'pending' | 'active' | 'inactive' | 'suspended'
export type SocialPlatform = 'instagram' | 'tiktok' | 'youtube' | 'twitter' | 'facebook' | 'pinterest' | 'linkedin' | 'snapchat' | 'twitch'

export interface SocialAccount {
  id: number
  platform: SocialPlatform
  username: string
  profile_url?: string
  profile_picture_url?: string
  follower_count?: number
  following_count?: number
  post_count?: number
  avg_likes?: number
  avg_comments?: number
  avg_views?: number
  engagement_rate?: number
  fake_follower_score?: number
  is_verified: boolean
  is_primary: boolean
  metrics_updated_at?: string
}

export interface PortfolioImage {
  url: string
  caption: string
  image_type: string
  setting?: string
  mood?: string
}

export interface Influencer {
  id: number
  user_id: number
  status: InfluencerStatus
  bio?: string
  location?: string
  country_code?: string
  language: string
  niches?: string[]
  tags?: string[]
  rate_per_post?: number
  rate_per_story?: number
  rate_per_reel?: number
  rate_per_video?: number
  currency: string
  trust_score?: number
  social_accounts: SocialAccount[]
  total_followers?: number
  avg_engagement_rate?: number
  primary_platform?: string
  ai_generated?: boolean
  physical_attributes?: Record<string, any>
  portfolio_images?: PortfolioImage[]
  appearance_prompt?: string
  created_at: string
  updated_at: string
}

export interface GenerateInfluencerRequest {
  gender?: string
  age_range?: string
  niche?: string
  ethnicity?: string
  extra_instructions?: string
}

export interface GenerateInfluencerResponse {
  influencer_id: number
  user_id: number
  full_name: string
  bio?: string
  location?: string
  niches: string[]
  physical_attributes?: Record<string, any>
  appearance_prompt?: string
  portfolio_images: PortfolioImage[]
  social_accounts_created: number
  model_used: string
}

// --- Client ---
export type ClientStatus = 'lead' | 'active' | 'paused' | 'churned'

export interface Client {
  id: number
  user_id: number
  company_name: string
  company_website?: string
  industry?: string
  status: ClientStatus
  monthly_budget?: number
  currency: string
  billing_email?: string
  logo_url?: string
  account_manager_id?: number
  notes?: string
}

export interface Brand {
  id: number
  client_id: number
  name: string
  description?: string
  website?: string
  industry?: string
  is_active: boolean
  logo_url?: string
}

// --- Campaign ---
export type CampaignStatus = 'draft' | 'planning' | 'active' | 'paused' | 'completed' | 'cancelled'
export type CampaignType = 'brand_awareness' | 'product_launch' | 'event_promotion' | 'lead_generation' | 'app_install' | 'sales' | 'content_creation' | 'affiliate'

export interface Campaign {
  id: number
  name: string
  description?: string
  campaign_type: CampaignType
  status: CampaignStatus
  client_id: number
  brand_id?: number
  manager_id?: number
  start_date?: string
  end_date?: string
  content_deadline?: string
  total_budget?: number
  influencer_budget?: number
  agency_fee?: number
  currency: string
  target_reach?: number
  target_impressions?: number
  target_engagement_rate?: number
  tracking_hashtags?: string[]
  brief_text?: string
  ftc_disclosure_required: boolean
  influencer_count?: number
  created_at: string
  updated_at: string
}

export type DeliverableStatus = 'pending' | 'in_progress' | 'submitted' | 'revision_requested' | 'approved' | 'published' | 'rejected'
export type DeliverableType = 'instagram_post' | 'instagram_story' | 'instagram_reel' | 'tiktok_video' | 'youtube_video' | 'youtube_short' | 'twitter_post' | 'facebook_post' | 'blog_post' | 'podcast_mention'

export interface Deliverable {
  id: number
  campaign_influencer_id: number
  deliverable_type: DeliverableType
  status: DeliverableStatus
  description?: string
  due_date?: string
  publish_date?: string
  content_url?: string
  live_url?: string
  caption?: string
  review_notes?: string
  revision_count: number
  post_metrics?: Record<string, number>
  created_at: string
}

export interface CampaignInfluencer {
  id: number
  campaign_id: number
  influencer_id: number
  status: string
  proposed_fee?: number
  agreed_fee?: number
  currency: string
  deliverables: Deliverable[]
  created_at: string
}

export interface CampaignMetrics {
  id: number
  campaign_id: number
  total_reach?: number
  total_impressions?: number
  total_likes?: number
  total_comments?: number
  total_shares?: number
  total_views?: number
  avg_engagement_rate?: number
  total_clicks?: number
  total_conversions?: number
  total_spend?: number
  cpm?: number
  roas?: number
  influencer_count?: number
  deliverable_count?: number
  last_synced_at?: string
}

// --- Payments ---
export type InvoiceStatus = 'draft' | 'sent' | 'viewed' | 'partial' | 'paid' | 'overdue' | 'void'

export interface Invoice {
  id: number
  invoice_number: string
  client_id: number
  campaign_id?: number
  status: InvoiceStatus
  subtotal: number
  tax_amount: number
  total_amount: number
  amount_paid: number
  currency: string
  issue_date: string
  due_date: string
  line_items: LineItem[]
  notes?: string
}

export interface LineItem {
  description: string
  quantity: number
  unit_price: number
  amount: number
}

// --- Notifications ---
export interface Notification {
  id: number
  notification_type: string
  title: string
  body?: string
  is_read: boolean
  action_url?: string
  created_at: string
}

// --- Analytics ---
export interface AgencyOverview {
  total_campaigns: number
  active_campaigns: number
  completed_campaigns: number
  total_influencers: number
  active_influencers: number
  total_revenue_ytd: number
  total_payout_ytd: number
  pending_invoices: number
  overdue_invoices: number
  avg_campaign_roi?: number
}

// --- AI Types ---
export interface AIMatchResult {
  influencer_id: number
  name: string
  match_score: number
  reasoning: string
  strengths: string[]
  concerns: string[]
}

export interface AIMatchResponse {
  matches: AIMatchResult[]
  model_used: string
}

export interface AIBriefRequest {
  product_name: string
  product_description: string
  target_audience: string
  budget_range: string
  campaign_type: string
  platforms: string[]
  duration_weeks: number
}

export interface AIBriefResponse {
  brief_markdown: string
  suggested_influencer_count: number
  suggested_budget_split: Record<string, number>
  model_used: string
}

export interface AIContentAnalysis {
  brand_safety_score: number
  quality_score: number
  engagement_prediction: number
  issues: string[]
  suggestions: string[]
}

export interface AIInsightReport {
  id: number
  report_type: string
  period_start: string
  period_end: string
  report_markdown: string
  key_metrics: Record<string, any>
  recommendations: any[]
  status: string
  created_at: string
}

export interface AIChatSession {
  id: number
  session_name: string
  context_type: string | null
  context_id: number | null
  is_active: boolean
  created_at: string
}

export interface AIChatMessage {
  id: number
  session_id: number
  role: 'user' | 'assistant'
  content: string
  created_at: string
}

// --- Admin Types ---

export interface FooterLink {
  label: string
  url: string
}

export interface SocialLink {
  platform: 'twitter' | 'instagram' | 'linkedin' | 'tiktok' | 'youtube' | 'facebook'
  url: string
}

export interface LandingStatItem {
  value: string
  label: string
}

/** Stored inside features_config.footer */
export interface FooterConfig {
  copyright?: string
  tagline?: string
  links?: FooterLink[]
  social?: SocialLink[]
}

/** Stored inside features_config.landing */
export interface LandingConfig {
  hero_headline?: string
  hero_subtitle?: string
  cta_primary_text?: string
  cta_secondary_text?: string
  stats?: LandingStatItem[]
  show_directory_cta?: boolean
  show_features?: boolean
}

export interface PlatformFeaturesConfig {
  landing?: LandingConfig
  footer?: FooterConfig
  [key: string]: unknown
}

export interface PlatformSettings {
  id: number
  agency_name: string
  agency_tagline: string | null
  agency_logo_url: string | null
  primary_color: string
  accent_color: string
  bg_base_color: string
  surface_color: string
  font_heading: string
  font_body: string
  support_email: string | null
  terms_url: string | null
  privacy_url: string | null
  custom_css: string | null
  features_config: PlatformFeaturesConfig | null
  max_ai_requests_per_day: number
  ai_provider_override: string | null
  ai_model_override: string | null
}

export interface AIProviderInfo {
  id: string
  name: string
  is_configured: boolean
  models: string[]
  default_model: string
}

export interface AIProvidersResponse {
  providers: AIProviderInfo[]
  active_provider: string
  active_model: string
}

/** Returned by GET /directory/public-settings — no auth required */
export interface PublicSiteSettings {
  agency_name: string
  agency_tagline: string | null
  agency_logo_url: string | null
  primary_color: string
  accent_color: string
  support_email: string | null
  terms_url: string | null
  privacy_url: string | null
  landing_config: LandingConfig | null
  footer_config: FooterConfig | null
}

export interface FeatureFlag {
  id: number
  flag_key: string
  flag_name: string
  description: string | null
  is_enabled: boolean
  enabled_for_roles: Record<string, boolean> | string[] | null
  created_at: string
  updated_at: string
}

export interface AuditLogEntry {
  id: number
  user_email: string
  action: string
  resource_type: string | null
  resource_id: string | null
  ip_address: string | null
  extra_data: Record<string, any> | null
  created_at: string
}

export interface AdminStats {
  total_users: number
  total_campaigns: number
  total_influencers: number
  total_clients: number
  active_campaigns: number
  total_revenue: number
  pending_invoices: number
  users_by_role: Record<string, number>
  campaigns_by_status: Record<string, number>
}
