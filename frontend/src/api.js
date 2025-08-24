const BASE = import.meta.env.VITE_API_BASE || 'http://localhost:8000'

export async function fetchProducts() {
  const r = await fetch(`${BASE}/api/products`)
  return await r.json()
}

export async function recommendPrice(payload) {
  const r = await fetch(`${BASE}/api/recommend`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  })
  return await r.json()
}
