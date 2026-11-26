export interface PiezaHero {
  imagen: string
  tipo: string
  nombre: string
  referencia: string
  descripcion: string
  estado: string
  aplicacion?: string
  stock: boolean
  oem: boolean
}

export const PIEZAS_HERO: PiezaHero[] = [
  {
    imagen: '/img/productos/Bombas-remanofacturadas.jpeg',
    tipo: 'Bombas hidráulicas',
    nombre: 'Bombas remanufacturadas',
    referencia: '',
    descripcion: 'Bombas hidráulicas preparadas para evaluación técnica y reparación según su condición.',
    estado: '',
    aplicacion: '',
    stock: false,
    oem: false,
  },
  {
    imagen: '/img/productos/Bombas-de-piñones-piloto-y-de-pre-carga-para-todas-las-aplicaciones.jpeg',
    tipo: 'Bombas hidráulicas',
    nombre: 'Bombas de piñones, piloto y pre-carga',
    referencia: '',
    descripcion: 'Bombas hidráulicas para aplicaciones que requieren alimentación piloto y control de pre-carga.',
    estado: '',
    aplicacion: '',
    stock: false,
    oem: false,
  },
  {
    imagen: '/img/productos/Controles-y-válvulas-de-regulación.jpeg',
    tipo: 'Control hidráulico',
    nombre: 'Controles y válvulas de regulación',
    referencia: '',
    descripcion: 'Componentes destinados al control y regulación de sistemas hidráulicos.',
    estado: '',
    aplicacion: '',
    stock: false,
    oem: false,
  },
  {
    imagen: '/img/productos/Piezas-internas-para-reparación-de-bombas-y-motores.jpeg',
    tipo: 'Piezas internas',
    nombre: 'Piezas internas para bombas y motores',
    referencia: '',
    descripcion: 'Repuestos internos destinados a mantenimiento y reparación de bombas y motores hidráulicos.',
    estado: '',
    aplicacion: '',
    stock: false,
    oem: false,
  },
  {
    imagen: '/img/productos/Retenedores-hidráulicos-de-alta-presión-para-bombas-y-motores.jpeg',
    tipo: 'Sellado hidráulico',
    nombre: 'Retenedores de alta presión',
    referencia: '',
    descripcion: 'Retenedores hidráulicos para aplicaciones con requerimientos de sellado a alta presión.',
    estado: '',
    aplicacion: '',
    stock: false,
    oem: false,
  },
]
