import { head } from "@vercel/blob";

const METADATA_FILENAME = "exittoys_metadata.json";

interface KBMetadata {
  lastUpdated: string;
  entries: {
    total: number;
    products: number;
    faqs: number;
    blogs: number;
    pages: number;
  };
  fileSizeBytes: number;
  fileSizeMB: string;
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
          <div className="mb-8 grid grid-cols-2 gap-4 sm:grid-cols-3 lg:grid-cols-5">
            <StatCard label="Totaal entries" value={meta.entries.total} />
            <StatCard label="Producten" value={meta.entries.products} />
            <StatCard label="FAQs" value={meta.entries.faqs} />
            <StatCard label="Blogs" value={meta.entries.blogs} />
            <StatCard label="Pagina's" value={meta.entries.pages} />
          </div>

          {/* Info cards */}
          <div className="mb-8 grid gap-4 sm:grid-cols-2">
            <InfoCard
              label="Laatste update"
              value={formatDate(meta.lastUpdated)}
            />
            <InfoCard label="Bestandsgrootte" value={`${meta.fileSizeMB} MB`} />
          </div>
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

      {/* API endpoint info */}
      <div className="mb-8 rounded-lg border border-gray-200 bg-white p-6">
        <h2 className="mb-3 text-lg font-semibold">API Endpoint</h2>
        <div className="rounded-md bg-gray-900 p-4">
          <code className="text-sm text-green-400 font-[family-name:var(--font-mono)]">
            GET /api/knowledge-base
          </code>
        </div>
        <p className="mt-3 text-sm text-gray-600">
          Retourneert de volledige kennisbank als JSON array met{" "}
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
            description="Data wordt omgezet naar trigger/content format voor de AI-chatbot."
          />
          <PipelineStep
            step={4}
            title="Upload naar Blob Storage"
            description="De JSON wordt geupload naar Vercel Blob Storage."
          />
          <PipelineStep
            step={5}
            title="CM Halo sync"
            description="CM Halo haalt de kennisbank op via /api/knowledge-base."
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
