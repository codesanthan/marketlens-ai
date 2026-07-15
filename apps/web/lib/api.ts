const base = process.env.API_BASE_URL || process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
export async function api<T>(path:string):Promise<T> { const response = await fetch(`${base}${path}`, { cache:"no-store" }); if (!response.ok) throw new Error(`Market data unavailable (${response.status})`); return response.json() as Promise<T>; }
