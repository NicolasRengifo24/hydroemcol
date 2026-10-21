import type {
  HistorialComponenteSeguimiento,
  PasoPublico,
} from "../../services/api";

export const PASOS_PUBLICOS = [
  "Recibido",
  "Revisión y cotización",
  "Pruebas",
  "Finalizado",
] as const satisfies readonly PasoPublico[];

export type Paso = (typeof PASOS_PUBLICOS)[number];

export function nivelDePaso(paso: string): number {
  const indice = PASOS_PUBLICOS.indexOf(paso as Paso);
  return indice >= 0 ? indice : 0;
}

export function comentarioPorPaso(
  historial: HistorialComponenteSeguimiento[],
): Partial<Record<PasoPublico, HistorialComponenteSeguimiento>> {
  const porPaso: Partial<Record<PasoPublico, HistorialComponenteSeguimiento>> =
    {};
  for (const registro of historial) {
    porPaso[registro.paso_publico] = registro;
  }
  return porPaso;
}
