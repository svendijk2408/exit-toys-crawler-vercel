import { head } from "@vercel/blob";
import { NextResponse } from "next/server";

export const runtime = "edge";

const BLOB_FILENAME = "exittoys_knowledge_base.json";

export async function GET() {
  try {
    // Haal blob metadata op om de URL te vinden
    const blobMeta = await head(BLOB_FILENAME);

    // Fetch de JSON vanuit Blob Storage en stream door
    const blobResponse = await fetch(blobMeta.url);

    if (!blobResponse.ok) {
      return NextResponse.json(
        { error: "Kon kennisbank niet laden vanuit storage" },
        { status: 502 }
      );
    }

    return new NextResponse(blobResponse.body, {
      status: 200,
      headers: {
        "Content-Type": "application/json",
        "Cache-Control": "public, s-maxage=3600, stale-while-revalidate=600",
        "Access-Control-Allow-Origin": "*",
        "Access-Control-Allow-Methods": "GET, OPTIONS",
      },
    });
  } catch {
    return NextResponse.json(
      {
        error: "Kennisbank nog niet beschikbaar. De eerste crawl moet nog draaien.",
      },
      { status: 503 }
    );
  }
}

export async function OPTIONS() {
  return new NextResponse(null, {
    status: 204,
    headers: {
      "Access-Control-Allow-Origin": "*",
      "Access-Control-Allow-Methods": "GET, OPTIONS",
      "Access-Control-Allow-Headers": "Content-Type",
    },
  });
}
