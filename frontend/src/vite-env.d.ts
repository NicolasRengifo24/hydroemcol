/// <reference types="vite/client" />

interface ImportMetaEnv {
  readonly VITE_META_PIXEL_ID?: string
}

interface ImportMeta {
  readonly env: ImportMetaEnv
}

type Fbq = ((...argumentos: unknown[]) => void) & {
  queue?: unknown[][]
}

interface Window {
  fbq?: Fbq
}
