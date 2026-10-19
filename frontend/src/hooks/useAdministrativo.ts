import {
  useMutation,
  useQuery,
  useQueryClient,
  type UseMutationOptions,
} from '@tanstack/react-query'
import {
  actualizarComponente,
  actualizarCotizacion,
  actualizarFotografia,
  actualizarObservacionesServicio,
  actualizarRegistroTecnico,
  cambiarEstadoComponente,
  cancelarServicio,
  clavesAdministrativas,
  crearComponente,
  crearCotizacion,
  crearFotografia,
  crearRegistroTecnico,
  eliminarComponente,
  eliminarFotografia,
  finalizarServicio,
  listarServiciosAdministrativos,
  obtenerDashboardAdministrativo,
  obtenerServicioAdministrativo,
  reenviarCotizacion,
  registrarAprobacionExterna,
  responderCotizacion,
  type AccionCambiarEstadoComponente,
  type DatosAprobacionExterna,
  type DatosComponente,
  type DatosCotizacion,
  type DatosFotografia,
  type DatosRegistroTecnico,
  type ErrorApi,
  type ParametrosListadoServicios,
  type RespuestaCotizacion,
} from '../services/api'

export function useDashboardAdministrativo() {
  return useQuery({ queryKey: clavesAdministrativas.dashboard(), queryFn: obtenerDashboardAdministrativo })
}

export function useServiciosAdministrativos(parametros: ParametrosListadoServicios = {}) {
  return useQuery({
    queryKey: clavesAdministrativas.servicios(parametros),
    queryFn: () => listarServiciosAdministrativos(parametros),
  })
}

export function useServicioAdministrativo(id: number) {
  return useQuery({
    queryKey: clavesAdministrativas.servicio(id),
    queryFn: () => obtenerServicioAdministrativo(id),
    enabled: Number.isInteger(id) && id > 0,
  })
}

function invalidarDespuesDeMutacion(queryClient: ReturnType<typeof useQueryClient>) {
  void queryClient.invalidateQueries({ queryKey: clavesAdministrativas.dashboard() })
  void queryClient.invalidateQueries({ queryKey: ['administrativo', 'servicios'] })
  void queryClient.invalidateQueries({ queryKey: ['administrativo', 'servicio'] })
}

function opcionesMutacion<TVariables, TResult>(
  queryClient: ReturnType<typeof useQueryClient>,
  opciones?: UseMutationOptions<TResult, ErrorApi, TVariables>,
): UseMutationOptions<TResult, ErrorApi, TVariables> {
  return {
    ...opciones,
    onSuccess: (data, variables, contexto, contextoMutacion) => {
      invalidarDespuesDeMutacion(queryClient)
      opciones?.onSuccess?.(data, variables, contexto, contextoMutacion)
    },
    onError: (error, variables, contexto, contextoMutacion) => {
      if (error.status === 409) invalidarDespuesDeMutacion(queryClient)
      opciones?.onError?.(error, variables, contexto, contextoMutacion)
    },
  }
}

export function useActualizarObservacionesServicio() {
  const queryClient = useQueryClient()
  return useMutation({
    mutationFn: ({ id, observaciones_internas }: { id: number; observaciones_internas: string }) =>
      actualizarObservacionesServicio(id, observaciones_internas),
    ...opcionesMutacion(queryClient),
  })
}

export function useMutacionesAdministrativas(servicioId: number) {
  const queryClient = useQueryClient()
  const opciones = <TVariables, TResult>(extra?: UseMutationOptions<TResult, ErrorApi, TVariables>) =>
    opcionesMutacion(queryClient, extra)

  return {
    crearComponente: useMutation({ mutationFn: (datos: DatosComponente) => crearComponente(servicioId, datos), ...opciones() }),
    actualizarComponente: useMutation({ mutationFn: ({ id, datos }: { id: number; datos: DatosComponente }) => actualizarComponente(servicioId, id, datos), ...opciones() }),
    eliminarComponente: useMutation({ mutationFn: (id: number) => eliminarComponente(servicioId, id), ...opciones() }),
    responderCotizacion: useMutation({ mutationFn: ({ componenteId, datos }: { componenteId: number; datos: RespuestaCotizacion }) => responderCotizacion(servicioId, componenteId, datos), ...opciones() }),
    finalizarServicio: useMutation({ mutationFn: (comentario?: string) => finalizarServicio(servicioId, comentario), ...opciones() }),
    cancelarServicio: useMutation({ mutationFn: (comentario: string) => cancelarServicio(servicioId, comentario), ...opciones() }),
    cambiarEstadoComponente: useMutation({
      mutationFn: ({ componenteId, datos }: { componenteId: number; datos: AccionCambiarEstadoComponente }) =>
        cambiarEstadoComponente(servicioId, componenteId, datos),
      ...opciones(),
    }),
    crearRegistroTecnico: useMutation({ mutationFn: (datos: DatosRegistroTecnico) => crearRegistroTecnico(servicioId, datos), ...opciones() }),
    actualizarRegistroTecnico: useMutation({ mutationFn: (datos: DatosRegistroTecnico) => actualizarRegistroTecnico(servicioId, datos), ...opciones() }),
    crearFotografia: useMutation({ mutationFn: (datos: DatosFotografia | FormData) => crearFotografia(servicioId, datos), ...opciones() }),
    actualizarFotografia: useMutation({ mutationFn: ({ id, datos }: { id: number; datos: Partial<DatosFotografia> }) => actualizarFotografia(servicioId, id, datos), ...opciones() }),
    eliminarFotografia: useMutation({ mutationFn: (id: number) => eliminarFotografia(servicioId, id), ...opciones() }),
  }
}

export function useMutacionesCotizacion(servicioId: number) {
  const queryClient = useQueryClient()
  void servicioId
  const opciones = <TVariables, TResult>(extra?: UseMutationOptions<TResult, ErrorApi, TVariables>) =>
    opcionesMutacion(queryClient, extra)

  return {
    crear: useMutation({ mutationFn: (datos: DatosCotizacion) => crearCotizacion(datos), ...opciones() }),
    actualizar: useMutation({ mutationFn: ({ id, datos }: { id: number; datos: Partial<DatosCotizacion> }) => actualizarCotizacion(id, datos), ...opciones() }),
    reenviar: useMutation({ mutationFn: ({ id, datos }: { id: number; datos: Parameters<typeof reenviarCotizacion>[1] }) => reenviarCotizacion(id, datos), ...opciones() }),
    registrarAprobacion: useMutation({ mutationFn: ({ id, datos }: { id: number; datos: DatosAprobacionExterna }) => registrarAprobacionExterna(id, datos), ...opciones() }),
  }
}
