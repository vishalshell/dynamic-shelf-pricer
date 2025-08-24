import React, { useEffect, useState } from 'react'
import { fetchProducts, recommendPrice } from './api'

export default function App() {
  const [products, setProducts] = useState([])
  const [ctx, setCtx] = useState({ days_to_expiry: 2, inventory: 40, competitor_price: '', promo_flag: false, weather_score: 0.0 })
  const [recs, setRecs] = useState({})

  useEffect(() => {
    fetchProducts().then(setProducts).catch(console.error)
  }, [])

  const handleRecommend = async (pid) => {
    const payload = {
      product_id: pid,
      context: {
        days_to_expiry: Number(ctx.days_to_expiry),
        inventory: Number(ctx.inventory),
        competitor_price: ctx.competitor_price === '' ? null : Number(ctx.competitor_price),
        promo_flag: Boolean(ctx.promo_flag),
        weather_score: Number(ctx.weather_score || 0)
      }
    }
    const r = await recommendPrice(payload)
    setRecs(prev => ({...prev, [pid]: r}))
  }

  return (
    <div style={{ fontFamily: 'sans-serif', padding: 16, maxWidth: 1000, margin: '0 auto' }}>
      <h1>Dynamic Shelf Pricer</h1>
      <p>Minimal UI to test pricing recommendations.</p>

      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(5, 1fr)', gap: 8, marginBottom: 12 }}>
        <label>Days to Expiry <input type="number" value={ctx.days_to_expiry} onChange={e => setCtx({...ctx, days_to_expiry: e.target.value})} /></label>
        <label>Inventory <input type="number" value={ctx.inventory} onChange={e => setCtx({...ctx, inventory: e.target.value})} /></label>
        <label>Competitor Price <input type="number" value={ctx.competitor_price} onChange={e => setCtx({...ctx, competitor_price: e.target.value})} /></label>
        <label>Promo <input type="checkbox" checked={ctx.promo_flag} onChange={e => setCtx({...ctx, promo_flag: e.target.checked})} /></label>
        <label>Weather (0..1) <input type="number" min="0" max="1" step="0.1" value={ctx.weather_score} onChange={e => setCtx({...ctx, weather_score: e.target.value})} /></label>
      </div>

      <table border="1" cellPadding="6" style={{ borderCollapse: 'collapse', width: '100%' }}>
        <thead>
          <tr>
            <th>Product</th>
            <th>Base Price</th>
            <th>Cost</th>
            <th>TTL (days)</th>
            <th>Action</th>
            <th>Recommendation</th>
          </tr>
        </thead>
        <tbody>
          {products.map(p => (
            <tr key={p.id}>
              <td>{p.name}</td>
              <td>{Number(p.base_price).toFixed(2)}</td>
              <td>{Number(p.cost).toFixed(2)}</td>
              <td>{p.ttl_days}</td>
              <td><button onClick={() => handleRecommend(p.id)}>Recommend</button></td>
              <td style={{ whiteSpace: 'pre-wrap' }}>{recs[p.id] ? (`RM ${recs[p.id].recommended_price}\n${recs[p.id].explanation}`) : '-'}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
