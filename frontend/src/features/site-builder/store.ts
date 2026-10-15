import { create } from "zustand";

type DraftState = {
  template: string;
  setTemplate: (t: string) => void;
};

export const useSiteDraftStore = create<DraftState>((set) => ({
  template: "minimal",
  setTemplate: (template) => set({ template }),
}));
