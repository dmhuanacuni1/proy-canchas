export interface Evento {
  id_evento: number;
  nombre_evento: string;
  tipo_evento?: string;
  fecha_evento: string; // YYYY-MM-DD
  hora_inicio: string;  // HH:MM
  hora_fin: string;     // HH:MM
  cupo_maximo?: number;
  organizador?: string;
  descripcion?: string;
  id_cancha: number;
  nombre_cancha?: string;
}

export interface CreateEventoDTO {
  nombre_evento: string;
  tipo_evento?: string;
  fecha_evento: string;
  hora_inicio: string;
  hora_fin: string;
  cupo_maximo?: number;
  organizador?: string;
  descripcion?: string;
  id_cancha: number;
}

export interface UpdateEventoDTO extends Partial<CreateEventoDTO> {}
