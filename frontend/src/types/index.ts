// ============================================================
// TypeScript interfaces mirroring NLAMS backend Pydantic schemas
// ============================================================

// ---------- Auth ----------
export interface User {
  id: string;
  full_name: string;
  email: string;
  phone: string;
  role_id: string;
  role_name: string;
  state_id?: string;
  state_name?: string;
  district_id?: string;
  district_name?: string;
  agency_name?: string;
  is_active: boolean;
  created_at: string;
}

export interface LoginRequest {
  email: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  user: User;
}

// ---------- Pagination ----------
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  page_size: number;
}

// ---------- State / District / Village ----------
export interface State {
  id: string;
  name: string;
  code: string;
  region?: string;
}

export interface District {
  id: string;
  state_id: string;
  name: string;
  code: string;
}

export interface Village {
  id: string;
  district_id: string;
  tehsil?: string;
  name: string;
  code: string;
}

// ---------- Project ----------
export type ProjectStage =
  | 'proposal'
  | 'dpr_upload'
  | 'land_requirement'
  | 'state_review'
  | 'district_verification'
  | 'gis_mapping'
  | 'legal_notification'
  | 'objection_handling'
  | 'compensation_assessment'
  | 'award_declaration'
  | 'payment_disbursement'
  | 'physical_possession'
  | 'rehabilitation_resettlement'
  | 'project_completion';

export type ProjectStatus =
  | 'draft'
  | 'submitted'
  | 'under_review'
  | 'approved'
  | 'rejected'
  | 'active'
  | 'delayed'
  | 'completed';

export type Priority = 'low' | 'medium' | 'high' | 'critical';

export interface Project {
  id: string;
  name: string;
  description?: string;
  ministry_name?: string;
  category_name?: string;
  implementing_agency_id?: string;
  state_id?: string;
  state_name?: string;
  district_id?: string;
  district_name?: string;
  estimated_budget: number;
  estimated_land_required_hectares: number;
  priority: Priority;
  current_stage: ProjectStage;
  status: ProjectStatus;
  start_date?: string;
  target_completion_date?: string;
  created_by: string;
  created_at: string;
  updated_at: string;
  parcel_count?: number;
  owner_count?: number;
}

// ---------- Milestone ----------
export type MilestoneStatus = 'pending' | 'in_progress' | 'completed' | 'delayed';

export interface Milestone {
  id: string;
  project_id: string;
  stage: ProjectStage;
  title: string;
  planned_date?: string;
  actual_date?: string;
  status: MilestoneStatus;
  responsible_officer_id?: string;
  remarks?: string;
  created_at: string;
}

// ---------- Land Parcel ----------
export type LandType = 'agricultural' | 'residential' | 'commercial' | 'forest' | 'govt' | 'other';
export type OwnershipStatus = 'private' | 'govt' | 'disputed' | 'common';
export type VerificationStatus = 'pending' | 'verified' | 'disputed' | 'acquired';

export interface LandParcel {
  id: string;
  project_id?: string;
  survey_number: string;
  village_id?: string;
  village_name?: string;
  district_id?: string;
  district_name?: string;
  state_id?: string;
  state_name?: string;
  area_hectares: number;
  land_type: LandType;
  ownership_status: OwnershipStatus;
  verification_status: VerificationStatus;
  geom?: any; // GeoJSON geometry
  created_at: string;
}

// ---------- Land Owner ----------
export interface LandOwner {
  id: string;
  parcel_id: string;
  full_name: string;
  aadhaar_masked?: string;
  phone?: string;
  email?: string;
  bank_account_masked?: string;
  ifsc?: string;
  share_percentage: number;
  user_id?: string;
  created_at: string;
}

// ---------- Survey Record ----------
export type SurveyStatus = 'scheduled' | 'completed' | 'flagged';

export interface SurveyRecord {
  id: string;
  parcel_id: string;
  surveyed_by?: string;
  survey_date?: string;
  geo_lat?: number;
  geo_lng?: number;
  condition_notes?: string;
  status: SurveyStatus;
  created_at: string;
}

// ---------- Legal ----------
export interface LegalNotification {
  id: string;
  project_id: string;
  section_type: string;
  notification_number?: string;
  issued_date?: string;
  status: 'draft' | 'issued' | 'challenged';
  created_at: string;
}

export type ObjectionStatus = 'filed' | 'under_review' | 'resolved' | 'rejected';

export interface Objection {
  id: string;
  parcel_id: string;
  filed_by?: string;
  filer_name: string;
  filer_contact?: string;
  objection_text: string;
  hearing_date?: string;
  status: ObjectionStatus;
  resolution_remarks?: string;
  resolved_by?: string;
  created_at: string;
}

// ---------- Compensation ----------
export type CompensationStatus = 'draft' | 'assessed' | 'approved' | 'disputed';

export interface Compensation {
  id: string;
  parcel_id: string;
  market_value: number;
  solatium: number;
  additional_compensation: number;
  total_award: number;
  assessed_by?: string;
  assessment_date?: string;
  status: CompensationStatus;
  created_at: string;
}

// ---------- Payment ----------
export type BankVerificationStatus = 'pending' | 'verified' | 'failed';
export type PaymentStatus = 'pending' | 'processing' | 'disbursed' | 'failed';

export interface Payment {
  id: string;
  compensation_id: string;
  land_owner_id?: string;
  amount: number;
  pfms_reference?: string;
  bank_verification_status: BankVerificationStatus;
  payment_status: PaymentStatus;
  disbursed_date?: string;
  created_at: string;
}

// ---------- Possession ----------
export type PossessionType = 'physical' | 'symbolic';

export interface Possession {
  id: string;
  parcel_id: string;
  possession_date?: string;
  taken_by?: string;
  possession_type: PossessionType;
  remarks?: string;
  document_id?: string;
  created_at: string;
}

// ---------- R&R ----------
export type DisplacedStatus = 'not_displaced' | 'partially' | 'fully';
export type BenefitStatus = 'not_started' | 'in_progress' | 'provided';
export type RRStage = 'identification' | 'verification' | 'benefit_disbursement' | 'resettled';

export interface RRFamily {
  id: string;
  project_id: string;
  family_head_name: string;
  family_id_number?: string;
  member_count: number;
  displaced_status: DisplacedStatus;
  housing_benefit_status: BenefitStatus;
  employment_benefit_status: BenefitStatus;
  monetary_benefit_amount: number;
  current_stage: RRStage;
  progress_percentage: number;
  created_at: string;
}

// ---------- Document ----------
export type DocType = 'dpr' | 'survey_report' | 'notification' | 'award' | 'geojson' | 'photo' | 'other';

export interface Document {
  id: string;
  project_id?: string;
  parcel_id?: string;
  uploaded_by?: string;
  doc_type: DocType;
  file_name: string;
  file_path: string;
  file_size?: number;
  mime_type?: string;
  version: number;
  parent_document_id?: string;
  created_at: string;
}

// ---------- Notification ----------
export type NotificationType = 'info' | 'success' | 'warning' | 'alert';
export type NotificationChannel = 'in_app' | 'email' | 'sms';

export interface Notification {
  id: string;
  user_id: string;
  title: string;
  body: string;
  type: NotificationType;
  channel: NotificationChannel;
  is_read: boolean;
  related_entity_type?: string;
  related_entity_id?: string;
  created_at: string;
}

// ---------- Audit Log ----------
export interface AuditLog {
  id: string;
  entity_type: string;
  entity_id: string;
  action: string;
  performed_by?: string;
  old_value?: Record<string, any>;
  new_value?: Record<string, any>;
  remarks?: string;
  ip_address?: string;
  created_at: string;
}

// ---------- Dashboard ----------
export interface KPICard {
  label: string;
  value: string | number;
  change?: number;
  change_label?: string;
  icon?: string;
}

export interface ChartData {
  name: string;
  data: { name: string; value: number }[];
}

export interface NationalDashboardData {
  kpis: KPICard[];
  charts: ChartData[];
  state_progress: StateProgress[];
}

export interface StateProgress {
  state_id: string;
  state_name: string;
  code: string;
  total_projects: number;
  completed: number;
  progress_pct: number;
}

// ---------- AI Insights ----------
export interface DelayPrediction {
  project_id: string;
  risk_label: 'On Track' | 'At Risk' | 'Delayed';
  color: 'green' | 'orange' | 'red';
  estimated_delay_days: number;
  total_milestones: number;
  completed_milestones: number;
  at_risk_milestones: number;
  avg_historical_delay_days: number;
  reasoning: string;
}

export interface RiskScore {
  project_id: string;
  score: number;
  color: 'green' | 'orange' | 'red';
  label: 'Low Risk' | 'Medium Risk' | 'High Risk';
  factors: {
    open_objections: number;
    disputed_parcels: number;
    total_parcels: number;
    days_since_last_update: number;
    current_status: string;
  };
}

export interface MissingDocuments {
  project_id: string;
  current_stage: string;
  uploaded_doc_types: string[];
  missing_documents: string[];
  completeness_pct: number;
}

export interface CompensationEstimate {
  land_type: string;
  area_hectares: number;
  base_value: number;
  solatium: number;
  estimated_range_min: number;
  estimated_range_max: number;
  currency: string;
  note: string;
}

// ---------- GIS GeoJSON ----------
export interface GeoJSONFeature {
  type: 'Feature';
  geometry: {
    type: 'Polygon';
    coordinates: number[][][];
  };
  properties: {
    id: string;
    survey_number: string;
    area_hectares: number;
    land_type: string;
    verification_status: string;
    village_name?: string;
    district_name?: string;
    state_name?: string;
    project_id?: string;
  };
}

export interface GeoJSONFeatureCollection {
  type: 'FeatureCollection';
  features: GeoJSONFeature[];
}
