import axiosClient from "../api/axiosClient";

export const api = {
  get: <T = any>(url: string) => axiosClient.get<T>(url.startsWith("/api") ? url : `/api${url}`),
  post: <T = any>(url: string, data?: any) => axiosClient.post<T>(url.startsWith("/api") ? url : `/api${url}`, data),
  put: <T = any>(url: string, data?: any) => axiosClient.put<T>(url.startsWith("/api") ? url : `/api${url}`, data),
  delete: <T = any>(url: string) => axiosClient.delete<T>(url.startsWith("/api") ? url : `/api${url}`),
};
