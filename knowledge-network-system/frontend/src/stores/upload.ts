import { defineStore } from "pinia";

type UploadStage = "idle" | "uploading" | "parsing" | "generating" | "done" | "error";

export const useUploadStore = defineStore("upload", {
  state: () => ({
    filename: "",
    progress: 0,
    status: "idle" as UploadStage,
    errorMessage: "",
    parseStatus: "idle" as "idle" | "processing" | "completed" | "failed",
    graphStatus: "idle" as "idle" | "processing" | "completed" | "failed",
    textLength: 0,
    extractedTextPreview: "",
    documentId: 0,
    graphSnapshotId: 0,
  }),
  actions: {
    reset() {
      this.filename = "";
      this.progress = 0;
      this.status = "idle";
      this.errorMessage = "";
      this.parseStatus = "idle";
      this.graphStatus = "idle";
      this.textLength = 0;
      this.extractedTextPreview = "";
      this.documentId = 0;
      this.graphSnapshotId = 0;
    },
  },
});
