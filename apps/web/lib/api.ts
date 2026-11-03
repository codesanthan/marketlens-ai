const base = process.env.API_BASE_URL || process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8000";
export class ApiError extends Error { constructor(message:string, readonly status:number) { super(message); } }
export async function api<T>(path:string):Promise<T> { const response = await fetch(`${base}${path}`, { cache:"no-store" }); if (!response.ok) throw new ApiError(`Market data unavailable (${response.status})`, response.status); return response.json() as Promise<T>; }
