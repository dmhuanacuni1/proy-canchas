import axiosClient from "../api/axiosClient";

export interface Pago {
  id_pago: number;
  metodo_pago: string;
  estado_pago: string;
  monto: number | null;
  fecha_pago: string | null;
  id_reserva: number;
  id_empleado: number | null;
  reserva?: {
    id_reserva: number;
    fecha_reserva: string | null;
    hora_inicio: string | null;
    estado_reserva: string;
    cancha?: string;
    cliente?: string;
  };
}

export interface ReservaParaPago {
  id_reserva: number;
  fecha_reserva: string | null;
  hora_inicio: string | null;
  monto_total: number | null;
  estado_reserva: string;
  cancha: string;
  tipo_deporte: string;
  cliente: string;
}

export interface RespPago {
  mensaje: string;
  pago: Pago;
}

export const pagosService = {
  listar: async (params: { estado?: string; detalle?: boolean } = {}) => {
    const { data } = await axiosClient.get<Pago[]>("/api/pagos", {
      params: {
        estado: params.estado || undefined,
        detalle: params.detalle ? "1" : undefined,
      },
    });
    return data;
  },

  obtener: async (id: number) => {
    const { data } = await axiosClient.get<Pago>(`/api/pagos/${id}`);
    return data;
  },

  crear: async (datos: {
    id_reserva: number;
    metodo_pago: string;
    monto: number;
    estado_pago?: string;
    id_empleado?: number;
  }) => {
    const { data } = await axiosClient.post<RespPago>("/api/pagos", datos);
    return data;
  },

  cambiarEstado: async (id: number, estado_pago: string) => {
    const { data } = await axiosClient.patch<RespPago>(`/api/pagos/${id}/estado`, {
      estado_pago,
    });
    return data;
  },

  eliminar: async (id: number) => {
    const { data } = await axiosClient.delete(`/api/pagos/${id}`);
    return data;
  },

  listarReservasParaPago: async () => {
    const { data } = await axiosClient.get<ReservaParaPago[]>("/api/pagos/reservas-para-pago");
    return data;
  },
};