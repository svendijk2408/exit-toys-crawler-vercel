/**
 * Upload crawler output naar Vercel Blob Storage.
 *
 * Verwacht dat BLOB_READ_WRITE_TOKEN als environment variable is gezet.
 * Leest de knowledge base JSON uit /tmp/crawler-output/.
 */

import { put } from "@vercel/blob";
import { readFileSync, statSync } from "fs";

const OUTPUT_DIR = "/tmp/crawler-output";
const KB_FILE = `${OUTPUT_DIR}/exittoys_knowledge_base.json`;

async function main() {
  // Lees de knowledge base
  console.log(`Lezen: ${KB_FILE}`);
  const kbData = readFileSync(KB_FILE, "utf-8");
  const entries = JSON.parse(kbData);
  const fileSizeBytes = statSync(KB_FILE).size;

  // Tel entry-types
  const stats = {
    total: entries.length,
    products: 0,
    faqs: 0,
    blogs: 0,
    pages: 0,
  };

  for (const entry of entries) {
    const content = entry.content || "";
    if (content.startsWith("Product:") || content.startsWith("Onderdeel:")) {
      stats.products++;
    } else if (content.startsWith("Vraag:")) {
      stats.faqs++;
    } else if (content.includes("Type: Blog")) {
      stats.blogs++;
    } else {
      stats.pages++;
    }
  }

  console.log(`Entries: ${stats.total} (${stats.products} producten, ${stats.faqs} FAQs, ${stats.blogs} blogs, ${stats.pages} pagina's)`);

  // Upload knowledge base JSON
  console.log("Uploaden: knowledge base JSON...");
  const kbBlob = await put("exittoys_knowledge_base.json", kbData, {
    access: "public",
    contentType: "application/json",
    addRandomSuffix: false,
  });
  console.log(`Knowledge base URL: ${kbBlob.url}`);

  // Maak en upload metadata
  const metadata = {
    lastUpdated: new Date().toISOString(),
    entries: stats,
    fileSizeBytes,
    fileSizeMB: (fileSizeBytes / (1024 * 1024)).toFixed(2),
    blobUrl: kbBlob.url,
  };

  console.log("Uploaden: metadata JSON...");
  const metaBlob = await put(
    "exittoys_metadata.json",
    JSON.stringify(metadata, null, 2),
    {
      access: "public",
      contentType: "application/json",
      addRandomSuffix: false,
    }
  );
  console.log(`Metadata URL: ${metaBlob.url}`);

  console.log("Upload voltooid!");
}

main().catch((err) => {
  console.error("Upload gefaald:", err);
  process.exit(1);
});
