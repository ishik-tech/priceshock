'use client';

import { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { api, Product, DashboardResponse } from '../lib/api';

export default function Home() {
  const [products, setProducts] = useState<Product[]>([]);
  const [dashboard, setDashboard] = useState<DashboardResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string>('All');

  const loadData = useCallback(async () => {
    try {
      setLoading(true);
      setError(null);

      // Load products
      const category = selectedCategory === 'All' ? undefined : selectedCategory;
      const productsData = await api.getProducts(category);
      setProducts(productsData);

      // Load dashboard
      try {
        const dashboardData = await api.getDashboard();
        setDashboard(dashboardData);
      } catch (err) {
        console.error('Dashboard load error:', err);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load data');
    } finally {
      setLoading(false);
    }
  }, [selectedCategory]);

  useEffect(() => {
    loadData();
  }, [loadData]);

  const categories = ['All', 'Food', 'Energy', 'Construction'];

  if (loading) {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-xl text-gray-600">Loading PriceShock...</div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-gray-900 mb-2">PriceShock</h1>
          <p className="text-lg text-gray-600">Product Price Forecasting & Inflation Early-Warning System</p>
        </div>

        {/* Error Message */}
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {error}
          </div>
        )}

        {/* Dashboard Stats */}
        {dashboard && (
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-sm font-medium text-gray-500 mb-2">Total Products</h3>
              <p className="text-3xl font-bold text-gray-900">{dashboard.total_products}</p>
            </div>
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-sm font-medium text-gray-500 mb-2">Total Forecasts</h3>
              <p className="text-3xl font-bold text-gray-900">{dashboard.total_forecasts}</p>
            </div>
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-sm font-medium text-gray-500 mb-2">High Risk Products</h3>
              <p className="text-3xl font-bold text-red-600">{dashboard.high_risk_products}</p>
            </div>
            <div className="bg-white rounded-lg shadow-md p-6">
              <h3 className="text-sm font-medium text-gray-500 mb-2">Avg Model MAE</h3>
              <p className="text-3xl font-bold text-gray-900">{dashboard.average_model_mae.toFixed(2)}</p>
            </div>
          </div>
        )}

        {/* Category Filter */}
        <div className="mb-6">
          <div className="flex gap-2 flex-wrap">
            {categories.map(cat => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={`px-4 py-2 rounded-lg transition ${
                  selectedCategory === cat
                    ? 'bg-blue-600 text-white'
                    : 'bg-white text-gray-700 hover:bg-gray-100'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        </div>

        {/* Products Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {products.map(product => (
            <Link
              key={product.id}
              href={`/products/${product.id}`}
              className="bg-white rounded-lg shadow-md p-6 hover:shadow-lg transition"
            >
              <div className="flex justify-between items-start mb-4">
                <div>
                  <h3 className="text-xl font-semibold text-gray-900 mb-1">{product.name}</h3>
                  <span className="inline-block px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full">
                    {product.category}
                  </span>
                </div>
                <span className="text-sm text-gray-500">{product.unit}</span>
              </div>
              <p className="text-gray-600 text-sm mb-4 line-clamp-2">{product.description || 'No description'}</p>
              <div className="flex justify-between items-center text-sm">
                <span className="text-gray-500">{product.region}</span>
                <span className="text-blue-600 font-medium">View Details →</span>
              </div>
            </Link>
          ))}
        </div>

        {/* Data Notice */}
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4 mt-8">
          <p className="text-sm text-yellow-800">
            <strong>Note:</strong> All data shown is <strong>DEMO / SYNTHETIC</strong> and generated for demonstration purposes only.
          </p>
        </div>
      </div>
    </div>
  );
}
