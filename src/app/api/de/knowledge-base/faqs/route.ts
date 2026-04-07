import { corsOptions, serveBlobFile } from "../../../_lib/blob-proxy";

export const runtime = "edge";

export async function GET() {
  return serveBlobFile("de/faqs.json", "FAQs");
}

export async function OPTIONS() {
  return corsOptions();
}
