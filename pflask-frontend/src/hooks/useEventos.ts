import { useState, useEffect, useCallback } from "react";
import type { Evento, CreateEventoDTO } from "../types/evento.types";
import { eventoService } from "../services/eventoService";

export const useEventos = () => {
  const [eventos, setEventos] = useState<Evento[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const fetchEventos = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await eventoService.getAll();
      setEventos(data);
    } catch (err: any) {
      setError("No se pudo conectar con el servidor para obtener los eventos.");
    } finally {
      setLoading(false);
    }
  }, []);

  useEffect(() => {
    fetchEventos();
  }, [fetchEventos]);

  const crearEvento = async (data: CreateEventoDTO) => {
    await eventoService.create(data);
    await fetchEventos();
  };

  const actualizarEvento = async (id: number, data: CreateEventoDTO) => {
    await eventoService.update(id, data);
    await fetchEventos();
  };

  const eliminarEvento = async (id: number) => {
    await eventoService.delete(id);
    await fetchEventos();
  };

  return {
    eventos,
    loading,
    error,
    refetch: fetchEventos,
    crearEvento,
    actualizarEvento,
    eliminarEvento,
  };
};
