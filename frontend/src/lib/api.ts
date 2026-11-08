import { offlineDemo, offlinePacks } from "./offlineDemo";
export async function api<T>(path: string, init?: RequestInit): Promise<T> {
  if (offlineDemo) {
    if (path === "/api/v1/meta")
      return {
        version: "0.1.0",
        mock: true,
        mode: "offline",
        max_input_chars: 6000,
      } as T;
    if (path === "/api/v1/packs") return offlinePacks as T;
    throw new Error(
      "This free offline demo has no backend. Run the full Docker app for live checking.",
    );
  }
  try {
    const response = await fetch(path, init);
    const data = await response.json();
    if (!response.ok) throw new Error(data.error?.message || "Request failed");
    return data as T;
  } catch (e) {
    throw new Error(
      e instanceof Error
        ? e.message
        : "Unable to connect. Check your connection and retry.",
    );
  }
}
export const safeUrl = (url: string) => {
  try {
    const u = new URL(url);
    return ["https:", "http:"].includes(u.protocol) && !u.username
      ? u.href
      : undefined;
  } catch {
    return undefined;
  }
};
