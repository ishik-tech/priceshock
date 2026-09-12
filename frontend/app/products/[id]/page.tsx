'use client';

import { useState, useEffect } from 'react';
import Link from 'next/link';
import { api, Product, PriceObservation, ForecastResponse } from '../../../lib/api';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

interface Props {
  params: { id: string };
}

export default function ProductDetail({ params }: Props) {
  const [product, setProduct] = useState<Product | null>(null);
  const [history, setHistory] = useState<PriceObservation[]>([]);
  const [forecast, setForecast] = useState<ForecastResponse | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [generatingForecast, setGeneratingForecast] = useState(false);
  const [horizonDays, setHorizonDays] = useState(30);
  const productId = parseInt(params.id);

  useEffect(() => { loadData(); }, [productId]);

  const loadData = async () => {
    try {
      setLoading(true);
      setError(null);
      const [productData, historyData] = await Promise.all([
        api.getProduct(productId),
        api.getProductHistory(productId, 365),
      ]);
      setProduct(productData);
      setHistory(historyData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load');
    } finally {
      setLoading(false);
    }
  };

  const handleGenerateForecast = async () => {
    try {
      setGeneratingForecast(true);
      const forecastData = await api.generateForecast(productId, horizonDays);
      setForecast(forecastData);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to generate');
    } finally {
      setGeneratingForecast(false);
    }
  };

  if (loading) {
    return <div className="min-h-screen flex items-center justify-center"><div className="text-xl text-gray-600">Loading...</div></div>;
  }

  if (!product) {
    return <div className="min-h-screen flex items-center justify-center"><div className="text-xl text-red-600">Product not found</div></div>;
  }
  return (
    <div className="min-h-screen bg-gray-50">
      <div className="container mx-auto px-4 py-8">
        <Link href="/" className="text-blue-600 hover:text-blue-800 mb-4 inline-block">
          ← Back to Dashboard
        </Link>
        
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h1 className="text-3xl font-bold text-gray-900 mb-2">{product.name}</h1>
          <span className="inline-block px-3 py-1 bg-blue-100 text-blue-800 text-sm rounded-full">
            {product.category}
          </span>
          <p className="text-gray-600 mt-4">{product.description || 'No description'}</p>
        </div>
        
        {error && (
          <div className="mb-6 p-4 bg-red-50 border border-red-200 rounded-lg text-red-700">
            {error}
          </div>
        )}
        
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Price History</h2>
          {history.length > 0 ? (
            <ResponsiveContainer width="100%" height={400}>
              <LineChart data={history.map(h => ({ date: new Date(h.date).toLocaleDateString(), price: h.price }))}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="date" />
                <YAxis />
                <Tooltip />
                <Line type="monotone" dataKey="price" stroke="#2563eb" strokeWidth={2} dot={false} />
              </LineChart>
            </ResponsiveContainer>
          ) : (
            <p className="text-gray-500">No price history available</p>
          )}
        </div>
        
        <div className="bg-white rounded-lg shadow-md p-6 mb-6">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">Generate Forecast</h2>
          <div className="flex gap-4 mb-4">
            <select
              value={horizonDays}
              onChange={(e) => setHorizonDays(Number(e.target.value))}
              className="px-4 py-2 border border-gray-300 rounded-lg"
            >
              <option value={7}>7 days</option>
              <option value={30}>30 days</option>
              <option value={90}>90 days</option>
              <option value={180}>180 days</option>
            </select>
            <button
              onClick={handleGenerateForecast}
              disabled={generatingForecast}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:bg-gray-400"
            >
              {generatingForecast ? 'Generating...' : 'Generate Forecast'}
            </button>
          </div>
          
          {forecast && (
            <div className="grid grid-cols-1 md:grid-cols-4 gap-4 p-4 bg-blue-50 rounded-lg">
              <div>
                <p className="text-sm text-gray-600">Current Price</p>
                <p className="text-2xl font-bold">₹{forecast.current_price.toFixed(2)}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Expected Change</p>
                <p className={`text-2xl font-bold ${forecast.expected_change_pct >= 0 ? 'text-red-600' : 'text-green-600'}`}>
                  {forecast.expected_change_pct >= 0 ? '+' : ''}{forecast.expected_change_pct.toFixed(2)}%
                </p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Model Used</p>
                <p className="text-lg font-semibold capitalize">{forecast.model_used.replace('_', ' ')}</p>
              </div>
              <div>
                <p className="text-sm text-gray-600">Data Quality</p>
                <p className="text-lg font-semibold">{forecast.data_quality_score.toFixed(1)}/100</p>
              </div>
            </div>
          )}
        </div>
        
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-4">
          <p className="text-sm text-yellow-800">
            <strong>Note:</strong> All data shown is <strong>DEMO / SYNTHETIC</strong> and generated for demonstration purposes only.
          </p>
        </div>
      </div>
    </div>
  );
}