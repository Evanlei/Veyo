import { useEffect, useState } from "react";
import { request } from "../lib/api";

export function usePrivateImage(path?: string) {
  const [result, setResult] = useState<{
    path: string;
    url: string;
    error: boolean;
  }>();
  useEffect(() => {
    if (!path) return;
    const controller = new AbortController();
    let objectUrl: string | undefined;
    request<Blob>(path, { signal: controller.signal })
      .then((blob) => {
        if (controller.signal.aborted) return;
        objectUrl = URL.createObjectURL(blob);
        setResult({ path, url: objectUrl, error: false });
      })
      .catch((error) => {
        if (error instanceof DOMException && error.name === "AbortError")
          return;
        if (!controller.signal.aborted)
          setResult({ path, url: "", error: true });
      });
    return () => {
      controller.abort();
      if (objectUrl) URL.revokeObjectURL(objectUrl);
    };
  }, [path]);
  return result?.path === path ? result : undefined;
}
