import { api } from "./api";
import type { UploadProcessResponse } from "../types/api";

export async function uploadFile(file: File): Promise<unknown> {
  const formData = new FormData();
  formData.append("file", file);
  const { data } = await api.post("/upload", formData, {
    headers: { "Content-Type": "multipart/form-data" },
  });
  return data;
}

export async function uploadAndProcessFile(
  file: File,
  onProgress?: (percent: number) => void
): Promise<UploadProcessResponse> {
  const formData = new FormData();
  formData.append("file", file);
  const { data } = await api.post<UploadProcessResponse>("/upload/process", formData, {
    headers: { "Content-Type": "multipart/form-data" },
    onUploadProgress: (event) => {
      if (!event.total || !onProgress) return;
      const percent = Math.min(100, Math.round((event.loaded * 100) / event.total));
      onProgress(percent);
    },
  });
  return data;
}
