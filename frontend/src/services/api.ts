export interface RequestOptions extends RequestInit {
  idempotencyKey?: string
}

export async function apiRequest<T = unknown>(
  endpoint: string,
  options: RequestOptions = {},
): Promise<T> {
  const { idempotencyKey, headers: customHeaders, ...rest } = options
  const headers = new Headers(customHeaders)

  if (!headers.has('Content-Type') && rest.body && !(rest.body instanceof FormData)) {
    headers.set('Content-Type', 'application/json')
  }

  if (idempotencyKey && !headers.has('Idempotency-Key')) {
    headers.set('Idempotency-Key', idempotencyKey)
  }

  const res = await fetch(endpoint, {
    ...rest,
    headers,
  })

  if (!res.ok) {
    let data: unknown
    try {
      data = await res.json()
    } catch {
      data = { detail: await res.text() }
    }
    const error = new Error('API error') as Error & { status: number; data: unknown }
    error.status = res.status
    error.data = data
    throw error
  }

  if (res.status === 204) {
    return {} as T
  }

  const ct = res.headers.get('content-type') || ''
  if (ct.includes('application/json')) {
    return (await res.json()) as T
  }
  return (await res.text()) as unknown as T
}