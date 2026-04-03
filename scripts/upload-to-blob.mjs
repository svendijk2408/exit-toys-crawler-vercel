/**
 * Upload crawler output naar Vercel Blob Storage.
 *
 * Verwacht dat BLOB_READ_WRITE_TOKEN als environment variable is gezet.
 * Leest de knowledge base JSON bestanden uit /tmp/crawler-output/.
 */

import { put } from "@vercel/blob";
import { readFileSync, statSync } from "fs";

const OUTPUT_DIR = "/tmp/crawler-output";

const CATEGORY_SLUGS = [
  "trampolines",
  "zwembaden",
  "speelhuisjes",
  "sport",
  "getset",
  "zandbak",
  "schommel",
  "onderdelen",
  "overig",
];

const FILES = [
  { name: "exittoys_knowledge_base.json", key: "combined" },
  { name: "producten.json", key: "producten" },
  { name: "faqs.json", key: "faqs" },
  { name: "paginas.json", key: "paginas" },
  ...CATEGORY_SLUGS.map((slug) => ({
    name: `producten-${slug}.json`,
    key: `producten-${slug}`,
  })),
];

async function main() {
  const uploadResults = {};

  for (const { name, key } of FILES) {
    const filePath = `${OUTPUT_DIR}/${name}`;
    console.log(`Lezen: ${filePath}`);

    const data = readFileSync(filePath, "utf-8");
    const entries = JSON.parse(data);
    const sizeBytes = statSync(filePath).size;

    console.log(`  ${name}: ${entries.length} entries, ${(sizeBytes / (1024 * 1024)).toFixed(2)} MB`);

    console.log(`  Uploaden...`);
    const blob = await put(name, data, {
      access: "public",
      contentType: "application/json",
      addRandomSuffix: false,
      allowOverwrite: true,
    });
    console.log(`  URL: ${blob.url}`);

    uploadResults[key] = {
      entries: entries.length,
      fileSizeBytes: sizeBytes,
      fileSizeMB: (sizeBytes / (1024 * 1024)).toFixed(2),
      blobUrl: blob.url,
    };
  }

  // Tel entry-types uit het gecombineerde bestand
  const combinedPath = `${OUTPUT_DIR}/exittoys_knowledge_base.json`;
  const combinedData = JSON.parse(readFileSync(combinedPath, "utf-8"));

  // Bouw categoryFiles object uit upload results
  const categoryFiles = {};
  for (const slug of CATEGORY_SLUGS) {
    const key = `producten-${slug}`;
    if (uploadResults[key]) {
      categoryFiles[slug] = uploadResults[key];
    }
  }

  // Maak en upload metadata
  const metadata = {
    lastUpdated: new Date().toISOString(),
    entries: {
      total: combinedData.length,
      producten: uploadResults.producten.entries,
      faqs: uploadResults.faqs.entries,
      paginas: uploadResults.paginas.entries,
    },
    fileSizeBytes: uploadResults.combined.fileSizeBytes,
    fileSizeMB: uploadResults.combined.fileSizeMB,
    blobUrl: uploadResults.combined.blobUrl,
    files: {
      producten: uploadResults.producten,
      faqs: uploadResults.faqs,
      paginas: uploadResults.paginas,
    },
    categoryFiles,
  };

  console.log("Uploaden: metadata JSON...");
  const metaBlob = await put(
    "exittoys_metadata.json",
    JSON.stringify(metadata, null, 2),
    {
      access: "public",
      contentType: "application/json",
      addRandomSuffix: false,
      allowOverwrite: true,
    }
  );
  console.log(`Metadata URL: ${metaBlob.url}`);

  console.log("Upload voltooid!");
}

main().catch((err) => {
  console.error("Upload gefaald:", err);
  process.exit(1);
});
