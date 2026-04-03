import { head } from "@vercel/blob";

const METADATA_FILENAME = "exittoys_metadata.json";

interface FileInfo {
  entries: number;
  fileSizeBytes: number;
  fileSizeMB: string;
  blobUrl: string;
}

interface KBMetadata {
  lastUpdated: string;
  entries: {
    total: number;
    // Nieuw format
    producten?: number;
    faqs?: number;
    paginas?: number;
    // Oud format (backward compat)
    products?: number;
    blogs?: number;
    pages?: number;
  };
  fileSizeBytes: number;
  fileSizeMB: string;
  files?: {
    producten: FileInfo;
    faqs: FileInfo;
    paginas: FileInfo;
  };
  categoryFiles?: Record<string, FileInfo>;
}

const BASE_URL = "https://exit-toys-crawler-vercel.vercel.app";

const CATEGORY_LABELS: Record<string, string> = {
  trampolines: "Trampolines",
  zwembaden: "Zwembaden",
  speelhuisjes: "Speelhuisjes",
  sport: "Sport",
  getset: "GetSet",
  zandbak: "Zandbak",
  schommel: "Schommel",
  onderdelen: "Onderdelen",
  overig: "Overig",
};

/** Normaliseer entries naar nieuw format, ongeacht of metadata oud of nieuw is. */
function normalizeEntries(entries: KBMetadata["entries"]) {
  return {
    total: entries.total,
    producten: entries.producten ?? entries.products ?? 0,
    faqs: entries.faqs ?? 0,
    paginas: entries.paginas ?? ((entries.blogs ?? 0) + (entries.pages ?? 0)),
  };
}

async function getMetadata(): Promise<KBMetadata | null> {
  try {
    const blobMeta = await head(METADATA_FILENAME);
    const response = await fetch(blobMeta.url, { next: { revalidate: 300 } });
    if (!response.ok) return null;
    return response.json();
  } catch {
    return null;
  }
}

function formatDate(iso: string): string {
  return new Date(iso).toLocaleString("nl-NL", {
    dateStyle: "long",
    timeStyle: "short",
    timeZone: "Europe/Amsterdam",
  });
}

export default async function Dashboard() {
  const meta = await getMetadata();

  return (
    <main className="mx-auto max-w-4xl px-4 py-12 font-[family-name:var(--font-sans)]">
      {/* Header */}
      <div className="mb-10">
        <h1 className="text-3xl font-bold text-gray-900">
          EXIT Toys Kennisbank
        </h1>
        <p className="mt-2 text-gray-600">
          Automatische crawler voor de CM Halo AI-chatbot kennisbank.
        </p>
      </div>

      {meta ? (
        <>
          {/* Stats grid */}
          {(() => {
            const e = normalizeEntries(meta.entries);
            return (
              <div className="mb-8 grid grid-cols-2 gap-4 sm:grid-cols-4">
                <StatCard label="Totaal entries" value={e.total} />
                <StatCard label="Producten" value={e.producten} />
                <StatCard label="FAQs" value={e.faqs} />
                <StatCard label="Pagina&apos;s" value={e.paginas} />
              </div>
            );
          })()}

          {/* Info cards */}
          <div className="mb-8 grid gap-4 sm:grid-cols-2">
            <InfoCard
              label="Laatste update"
              value={formatDate(meta.lastUpdated)}
            />
            <InfoCard label="Totale grootte" value={`${meta.fileSizeMB} MB`} />
          </div>

          {/* Per-bestand grootte */}
          {meta.files && (
            <div className="mb-8 rounded-lg border border-gray-200 bg-white p-6">
              <h2 className="mb-3 text-lg font-semibold">Bestanden</h2>
              <div className="space-y-2 text-sm">
                {[
                  { label: "producten.json", info: meta.files.producten },
                  { label: "faqs.json", info: meta.files.faqs },
                  { label: "paginas.json", info: meta.files.paginas },
                ].map(({ label, info }) => (
                  <div
                    key={label}
                    className="flex items-center justify-between rounded-md bg-gray-50 px-4 py-2"
                  >
                    <code className="text-xs font-[family-name:var(--font-mono)]">
                      {label}
                    </code>
                    <span className="text-gray-500">
                      {info.entries.toLocaleString("nl-NL")} entries &middot;{" "}
                      {info.fileSizeMB} MB
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Producten per categorie */}
          {meta.categoryFiles && Object.keys(meta.categoryFiles).length > 0 && (
            <div className="mb-8 rounded-lg border border-gray-200 bg-white p-6">
              <h2 className="mb-3 text-lg font-semibold">Producten per categorie</h2>
              <div className="space-y-2 text-sm">
                {Object.entries(meta.categoryFiles).map(([slug, info]) => (
                  <div
                    key={slug}
                    className="flex items-center justify-between rounded-md bg-gray-50 px-4 py-2"
                  >
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-gray-700">
                        {CATEGORY_LABELS[slug] ?? slug}
                      </span>
                      <code className="text-xs text-gray-400 font-[family-name:var(--font-mono)]">
                        producten-{slug}.json
                      </code>
                    </div>
                    <span className="text-gray-500">
                      {info.entries.toLocaleString("nl-NL")} entries &middot;{" "}
                      {info.fileSizeMB} MB
                    </span>
                  </div>
                ))}
              </div>
            </div>
          )}
        </>
      ) : (
        <div className="mb-8 rounded-lg border border-yellow-200 bg-yellow-50 p-6">
          <p className="font-medium text-yellow-800">
            Nog geen data beschikbaar
          </p>
          <p className="mt-1 text-sm text-yellow-700">
            De eerste crawl moet nog draaien via GitHub Actions. Trigger deze
            handmatig of wacht op het dagelijkse schema (06:00 NL).
          </p>
        </div>
      )}

      {/* API endpoints info */}
      <div className="mb-8 rounded-lg border border-gray-200 bg-white p-6">
        <h2 className="mb-3 text-lg font-semibold">API Endpoints</h2>
        <div className="space-y-2">
          {[
            {
              endpoint: `${BASE_URL}/api/knowledge-base`,
              desc: "Volledige kennisbank (alle entries)",
            },
            {
              endpoint: `${BASE_URL}/api/knowledge-base/producten`,
              desc: "Alle producten + onderdelen",
            },
            {
              endpoint: `${BASE_URL}/api/knowledge-base/faqs`,
              desc: "Alleen veelgestelde vragen",
            },
            {
              endpoint: `${BASE_URL}/api/knowledge-base/paginas`,
              desc: "Alleen pagina\u2019s + blogs",
            },
          ].map(({ endpoint, desc }) => (
            <div key={endpoint}>
              <div className="rounded-md bg-gray-900 px-4 py-2 overflow-x-auto">
                <code className="text-sm text-green-400 font-[family-name:var(--font-mono)]">
                  GET {endpoint}
                </code>
              </div>
              <p className="mt-1 mb-3 text-xs text-gray-500">{desc}</p>
            </div>
          ))}
        </div>

        <h3 className="mt-4 mb-2 text-sm font-semibold text-gray-700">Per categorie</h3>
        <div className="space-y-2">
          {Object.entries(CATEGORY_LABELS).map(([slug, label]) => (
            <div key={slug}>
              <div className="rounded-md bg-gray-900 px-4 py-2 overflow-x-auto">
                <code className="text-sm text-green-400 font-[family-name:var(--font-mono)]">
                  GET {BASE_URL}/api/knowledge-base/producten/{slug}
                </code>
              </div>
              <p className="mt-1 mb-3 text-xs text-gray-500">{label}</p>
            </div>
          ))}
        </div>

        <p className="mt-2 text-sm text-gray-600">
          Retourneert JSON arrays met{" "}
          <code className="rounded bg-gray-100 px-1.5 py-0.5 text-xs font-[family-name:var(--font-mono)]">
            trigger
          </code>{" "}
          en{" "}
          <code className="rounded bg-gray-100 px-1.5 py-0.5 text-xs font-[family-name:var(--font-mono)]">
            content
          </code>{" "}
          velden. Compatibel met CM Halo API Connection.
        </p>
      </div>

      {/* Pipeline uitleg */}
      <div className="rounded-lg border border-gray-200 bg-white p-6">
        <h2 className="mb-4 text-lg font-semibold">Crawl Pipeline</h2>
        <ol className="space-y-3 text-sm text-gray-700">
          <PipelineStep
            step={1}
            title="GitHub Actions"
            description="Dagelijks om 06:00 NL start de crawler automatisch."
          />
          <PipelineStep
            step={2}
            title="Website crawlen"
            description="Python crawler haalt alle producten, FAQs, blogs en pagina's op van exittoys.nl."
          />
          <PipelineStep
            step={3}
            title="Kennisbank genereren"
            description="Data wordt omgezet naar trigger/content format en opgesplitst in 3 bestanden + 1 gecombineerd."
          />
          <PipelineStep
            step={4}
            title="Upload naar Blob Storage"
            description="Alle JSON bestanden worden geupload naar Vercel Blob Storage."
          />
          <PipelineStep
            step={5}
            title="CM Halo sync"
            description="CM Halo haalt de kennisbank op via de individuele endpoints."
          />
        </ol>
      </div>
    </main>
  );
}

function StatCard({ label, value }: { label: string; value: number }) {
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4">
      <p className="text-2xl font-bold text-gray-900">
        {value.toLocaleString("nl-NL")}
      </p>
      <p className="text-sm text-gray-500">{label}</p>
    </div>
  );
}

function InfoCard({ label, value }: { label: string; value: string }) {
  return (
    <div className="rounded-lg border border-gray-200 bg-white p-4">
      <p className="text-sm text-gray-500">{label}</p>
      <p className="mt-1 font-medium text-gray-900">{value}</p>
    </div>
  );
}

function PipelineStep({
  step,
  title,
  description,
}: {
  step: number;
  title: string;
  description: string;
}) {
  return (
    <li className="flex gap-3">
      <span className="flex h-6 w-6 shrink-0 items-center justify-center rounded-full bg-gray-900 text-xs font-bold text-white">
        {step}
      </span>
      <div>
        <span className="font-medium text-gray-900">{title}</span>
        <span className="text-gray-500"> &mdash; {description}</span>
      </div>
    </li>
  );
}
