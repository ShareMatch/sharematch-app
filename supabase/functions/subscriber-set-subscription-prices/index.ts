import { serve } from "https://deno.land/std/http/server.ts";
import { authenticateRequest } from "../_shared/auth.ts";
import { createClient } from "https://esm.sh/@supabase/supabase-js";

const supabase = createClient(
  Deno.env.get("SUPABASE_URL")!,
  Deno.env.get("SUPABASE_SERVICE_ROLE_KEY")!
);

serve(async (req) => {
  try {
    const auth = await authenticateRequest(req);

    if (auth.entity_type !== "subscriber") {
      return new Response("Forbidden", { status: 403 });
    }

    if (!auth.scopes.includes("subscriber:write:subscription_prices")) {
      return new Response("Insufficient scope", { status: 403 });
    }

    const body = await req.json();

    for (const asset of body.assets) {
      await supabase
        .from("subscriber_index_assets")
        .update({
          subscription_price: asset.subscription_price,
          updated_at: new Date().toISOString()
        })
        .eq("external_ref_code", asset.subscriber_asset_code)
        .eq("subscriber_id", auth.entity_id);
    }

    return new Response(JSON.stringify({ status: "ok" }), {
      headers: { "Content-Type": "application/json" }
    });
  } catch (err) {
    return new Response(err.message, { status: 401 });
  }
});
