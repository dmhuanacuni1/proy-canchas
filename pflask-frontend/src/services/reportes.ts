import axiosClient from "../api/axiosClient";

export const reportesService = {
  obtener: async (tipo: string, fechaInicio: string, fechaFin: string) => {
    const { data } = await axiosClient.get("/api/reportes/datos/" + tipo, {
      params: { fecha_inicio: fechaInicio, fecha_fin: fechaFin },
    });
    return data;
  },

  urlExportar: (tipo: string, fechaInicio: string, fechaFin: string, formato: "pdf" | "excel") => {
    const base = (import.meta.env.VITE_API_URL as string) || "http://localhost:5000";
    const params = new URLSearchParams({
      fecha_inicio: fechaInicio,
      fecha_fin: fechaFin,
      formato,
    });
    return `${base}/api/reportes/exportar/${tipo}?${params.toString()}`;
  },
};