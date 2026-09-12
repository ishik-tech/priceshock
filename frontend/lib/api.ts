const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export async function apiFetch<T>(
  endpoint: string,
  options: RequestInit = {}
): Promise<T> {
  const url = `${API_BASE_URL}${endpoint}`;
  
  const response = await fetch(url, {
    ...options,
    headers: {
      'Content-Type': 'application/json',
      ...options.headers,
    },
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({ detail: 'Unknown error' }));
    throw new Error(error.detail || `HTTP ${response.status}`);
  }

  return response.json();
}

export const api = {
  // Health
  health: () => apiFetch<{ status: string; timestamp: string }>('/api/health'),

  // Products
  getProducts: (category?: string) =>
    apiFetch<Product[]>('/api/products' + (category ? `?category=${category}` : '')),

  getProduct: (id: number) =>
    apiFetch<Product>('/api/products/' + id),

  getProductHistory: (id: number, days: number = 365) =>
    apiFetch<PriceObservation[]>(`/api/products/${id}/history?days=${days}`),

  // Forecasts
  generateForecast: (productId: number, horizonDays: number = 30, modelName?: string) =>
    apiFetch<ForecastResponse>('/api/products/' + productId + '/forecast', {
      method: 'POST',
      body: JSON.stringify({ product_id: productId, horizon_days: horizonDays, model_name: modelName }),
    }),

  // Risk
  getProductRisk: (productId: number, horizonDays: number = 90) =>
    apiFetch<RiskResponse>('/api/products/' + productId + `/risk?horizon_days=${horizonDays}`),

  getTopRiskProducts: (limit: number = 10, horizonDays: number = 90) =>
    apiFetch<{ products: any[]; horizon_days: number }>(`/api/risk/top?limit=${limit}&horizon_days=${horizonDays}`),

  // Dashboard
  getDashboard: () =>
    apiFetch<DashboardResponse>('/api/dashboard'),
};

// Types
export interface Product {
  id: number;
  name: string;
  category: string;
  unit: string;
  region: string;
  description?: string;
  created_at: string;
  updated_at?: string;
}

export interface PriceObservation {
  id: number;
  product_id: number;
  date: string;
  price: number;
  currency: string;
  unit: string;
  region: string;
  source: string;
  is_synthetic: boolean;
  created_at: string;
}

export interface ForecastPrediction {
  forecast_date: string;
  predicted_price: number;
  lower_bound?: number;
  upper_bound?: number;
  horizon_days: number;
}

export interface ForecastResponse {
  product_id: number;
  product_name: string;
  model_used: string;
  horizon_days: number;
  current_price: number;
  predictions: ForecastPrediction[];
  expected_change_pct: number;
  data_quality_score: number;
  forecast_generated_at: string;
  is_synthetic_data: boolean;
}

export interface RiskResponse {
  product_id: number;
  product_name: string;
  horizon_days: number;
  risk_level: string;
  probability_5pct: number;
  probability_10pct: number;
  probability_20pct: number;
  expected_change_pct: number;
  confidence: number;
  calculated_at: string;
}

export interface DashboardResponse {
  generated_at: string;
  total_products: number;
  total_forecasts: number;
  high_risk_products: number;
  average_model_mae: number;
  data_source: string;
  last_updated: string;
  data_quality_score: number;
  top_risk_products: ProductSummary[];
  top_uncertainty_products: ProductSummary[];
}

export interface ProductSummary {
  product_id: number;
  product_name: string;
  category: string;
  current_price: number;
  expected_30d_change_pct?: number;
  risk_level?: string;
}