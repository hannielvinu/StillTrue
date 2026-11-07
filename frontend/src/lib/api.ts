export async function api<T>(path: string, init?: RequestInit): Promise<T> {
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
