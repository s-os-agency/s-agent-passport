/** Shared Node 20+/Worker client. No model download or GPU is needed by clients. */
export async function generateOmni({
  baseURL, token, prompt, media = [], audioOutput = false,
  useAudioInVideo = false, maxTokens = 256, timeoutMs = 180000,
}) {
  if (!baseURL) throw new Error("The approved Omni gateway URL is required.");
  const base = new URL(baseURL);
  const local = ["127.0.0.1", "localhost", "[::1]"].includes(base.hostname);
  if (base.username || base.password || base.search || base.hash) {
    throw new Error("Gateway URL must not include credentials, query parameters, or fragments.");
  }
  if (base.protocol !== "https:" && !(local && base.protocol === "http:")) {
    throw new Error("Remote Omni gateways require HTTPS.");
  }
  if (!local && !token) throw new Error("Use the existing gateway's scoped authorization token.");
  const url = new URL(`${base.pathname.replace(/\/$/, "")}/v1/generate`, base.origin);
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    body: JSON.stringify({
      prompt, media, audio_output: audioOutput,
      use_audio_in_video: useAudioInVideo, max_tokens: maxTokens,
    }),
    signal: AbortSignal.timeout(timeoutMs),
    redirect: "error",
  });
  if (!response.ok) throw new Error(`Omni gateway returned HTTP ${response.status}.`);
  const result = await response.json();
  if (result.model !== "Qwen/Qwen2.5-Omni-7B" ||
      result.revision !== "ae9e1690543ffd5c0221dc27f79834d0294cba00" ||
      typeof result.text !== "string" || !result.id) {
    throw new Error("Gateway response does not match the pinned model contract.");
  }
  return result;
}

/** Explicit adapter for callers using the existing routeLLM return shape. */
export async function routeOmni(options) {
  const result = await generateOmni(options);
  return {
    success: true, provider: "self_hosted_huggingface", model: result.model,
    text: result.text, audio: result.audio, requestId: result.id,
    revision: result.revision, fallbacksUsed: 0,
  };
}
