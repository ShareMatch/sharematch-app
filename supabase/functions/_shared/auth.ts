// auth.ts
import { createClient } from "https://esm.sh/@supabase/supabase-js@2";
import { jwtVerify } from "https://deno.land/x/jose@v5.2.0/index.ts";

// ---------- Types ----------
export type EntityType = "subscriber" | "lp";

export interface AuthContext {
  entityType: EntityType;
  entityId: string;
  apiKeyId: string;
}

// ---------- Supabase Client ----------
const supabase = createClient(
  Deno.env.get("SUPABASE_URL")!,
  Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!
);

// ---------- Helpers ----------
async function sha256(value: string): Promise<string> {
  const encoder = new TextEncoder();
  const data = encoder.encode(value + Deno.env.get("API_KEY_SALT"));
  const hash = await crypto.subtle.digest("SHA-256", data);
  return Array.from(new Uint8Array(hash))
    .map(b => b.toString(16).padStart(2, "0"))
    .join("");
}

// ---------- Main Auth Middleware ----------
export async function authenticateRequest(
  req: Request
): Promise<AuthContext> {

  const authHeader = req.headers.get("authorization");
  const apiKey = req.headers.get("x-api-key");

  if (!authHeader || !authHeader.startsWith("Bearer ")) {
    throw new Response("Missing or invalid Authorization header", { status: 401 });
  }

  if (!apiKey) {
    throw new Response("Missing x-api-key header", { status: 401 });
  }

  const token = authHeader.replace("Bearer ", "");

  // ---------- Verify JWT ----------
  let jwtPayload: any;
  try {
    const secret = new TextEncoder().encode(
      Deno.env.get("API_JWT_SECRET")
    );

    const { payload } = await jwtVerify(token, secret);
    jwtPayload = payload;
  } catch {
    throw new Response("Invalid or expired JWT", { status: 401 });
  }

  // ---------- Hash API Key ----------
  const apiKeyHash = await sha256(apiKey);

  // ---------- Lookup API Key ----------
  const { data, error } = await supabase
    .from("api_keys")
    .select("id, entity_type, entity_id, status")
    .eq("key_hash", apiKeyHash)
    .single();

  if (error || !data) {
    throw new Response("Invalid API key", { status: 401 });
  }

  if (data.status !== "active") {
    throw new Response("API key is inactive", { status: 403 });
  }

  // ---------- Cross-check JWT ↔ API Key ----------
  if (
    jwtPayload.entity_id !== data.entity_id ||
    jwtPayload.sub !== data.entity_type
  ) {
    throw new Response("Token does not match API key", { status: 403 });
  }

  // ---------- Success ----------
  return {
    entityType: data.entity_type,
    entityId: data.entity_id,
    apiKeyId: data.id
  };
}
