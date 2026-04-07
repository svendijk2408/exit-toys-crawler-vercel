import { corsOptions, serveBlobFile } from "../../_lib/blob-proxy";

export const runtime = "edge";

export async function GET() {
  return serveBlobFile("producten.json", "producten");
}

export async function OPTIONS() {
  return corsOptions();
}
