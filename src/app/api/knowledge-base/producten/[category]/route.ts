import { head } from "@vercel/blob";
import { NextResponse } from "next/server";

export const runtime = "edge";

const VALID_CATEGORIES = [
  "trampolines",
  "zwembaden",
  "speelhuisjes",
  "sport",
  "getset",
  "zandbak",
  "schommel",
  "onderdelen",
  "overig",
] as const;

type Category = (typeof VALID_CATEGORIES)[number];

function isValidCategory(value: string): value is Category {
  return (VALID_CATEGORIES as readonly string[]).includes(value);
}

export async function GET(
  _request: Request,
  { params }: { params: Promise<{ category: string }> }
) {
  const { category } = await params;

  if (!isValidCategory(category)) {
    return NextResponse.json(
      {
        error: `Onbekende categorie: ${category}`,
        valid: VALID_CATEGORIES,
      },
      { status: 404 }
    );
  }

  const blobFilename = `producten-${category}.json`;

  try {
    const blobMeta = await head(blobFilename);
    const blobResponse = await fetch(blobMeta.url);

    if (!blobResponse.ok) {
      return NextResponse.json(
        { error: `Kon producten-${category} niet laden vanuit storage` },
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
        error: `Categorie ${category} nog niet beschikbaar. De eerste crawl moet nog draaien.`,
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
