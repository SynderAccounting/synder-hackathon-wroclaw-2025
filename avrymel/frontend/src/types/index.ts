// User & Authentication Types
export type UserRole = 'admin' | 'user' | 'viewer';

export interface User {
  id: string;
  email: string;
  username: string;
  role: UserRole;
  full_name?: string;
  is_active: boolean;
  created_at: string;
  updated_at: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  username: string;
  password: string;
  full_name?: string;
}

export interface AuthResponse {
  access_token: string;
  token_type: string;
  user: User;
}

export interface PasswordResetRequest {
  email: string;
}

export interface PasswordResetConfirm {
  token: string;
  new_password: string;
}

// Transaction Types
export interface Transaction {
  id: string;
  order_id: string;
  platform: string;
  customer_email: string;
  customer_name: string;
  amount: number;
  currency: string;
  status: string;
  items: TransactionItem[];
  created_at: string;
  updated_at: string;
  metadata?: Record<string, any>;
}

export interface TransactionItem {
  id: string;
  sku: string;
  name: string;
  quantity: number;
  price: number;
  total: number;
}

export interface TransactionFilter {
  platform?: string;
  status?: string;
  date_from?: string;
  date_to?: string;
  min_amount?: number;
  max_amount?: number;
  search?: string;
}

export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  page: number;
  size: number;
  pages: number;
}

// Connector Types
export interface Connector {
  id: string;
  name: string;
  platform: string;
  description: string;
  status: 'active' | 'inactive' | 'error';
  last_sync?: string;
  config: Record<string, any>;
  created_at: string;
  updated_at: string;
}

export interface IngestionJob {
  id: string;
  connector_id: string;
  connector_name: string;
  status: 'pending' | 'running' | 'completed' | 'failed';
  records_processed: number;
  records_failed: number;
  started_at?: string;
  completed_at?: string;
  error_message?: string;
}

export interface TriggerIngestionRequest {
  connector_id: string;
  date_from?: string;
  date_to?: string;
}

// Health & System Types
export interface HealthStatus {
  status: 'healthy' | 'degraded' | 'unhealthy';
  api: ComponentHealth;
  database: ComponentHealth;
  workers: ComponentHealth;
  timestamp: string;
}

export interface ComponentHealth {
  status: 'up' | 'down' | 'degraded';
  latency_ms?: number;
  details?: string;
}

// Dashboard Types
export interface DashboardMetrics {
  total_transactions: number;
  total_revenue: number;
  active_connectors: number;
  pending_jobs: number;
  transactions_today: number;
  revenue_today: number;
  transactions_trend: TrendData[];
  revenue_trend: TrendData[];
  platform_distribution: PlatformStats[];
}

export interface TrendData {
  date: string;
  value: number;
}

export interface PlatformStats {
  platform: string;
  count: number;
  revenue: number;
}

// Settings Types
export interface UserSettings {
  theme: 'light' | 'dark' | 'system';
  notifications_enabled: boolean;
  email_notifications: boolean;
  language: string;
}

export interface UpdateProfileRequest {
  full_name?: string;
  email?: string;
}

export interface ChangePasswordRequest {
  current_password: string;
  new_password: string;
}

// Admin Types
export interface CreateUserRequest {
  email: string;
  username: string;
  password: string;
  role: UserRole;
  full_name?: string;
}

export interface UpdateUserRequest {
  email?: string;
  full_name?: string;
  role?: UserRole;
  is_active?: boolean;
}

// API Error Types
export interface ApiError {
  detail: string;
  status?: number;
  errors?: Record<string, string[]>;
}
