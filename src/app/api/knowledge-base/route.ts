import { corsOptions, serveBlobFile } from "../_lib/blob-proxy";

export const runtime = "edge";

export async function GET() {
  return serveBlobFile("exittoys_knowledge_base.json", "kennisbank");
}

export async function OPTIONS() {
  return corsOptions();
}
