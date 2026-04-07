import { corsOptions, serveBlobFile } from "../../_lib/blob-proxy";

export const runtime = "edge";

export async function GET() {
  return serveBlobFile("paginas.json", "pagina's");
}

export async function OPTIONS() {
  return corsOptions();
}
