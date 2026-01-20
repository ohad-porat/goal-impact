import { Nation } from "../../lib/types";
import { api } from "../../lib/api";
import { tableStyles } from "../../lib/tableStyles";
import { ErrorDisplay } from "../../components/ErrorDisplay";
import Link from "next/link";

async function getNations(): Promise<Nation[]> {
  const response = await fetch(api.nations, {
    next: { revalidate: 86400 },
  });

  if (!response.ok) {
    throw new Error("Failed to fetch nations");
  }

  const data = await response.json();
  return data.nations;
}

export default async function NationsPage() {
  let nations: Nation[] = [];
  try {
    nations = await getNations();
  } catch (error) {
    return <ErrorDisplay message="Failed to load nations." />;
  }

  const styles = tableStyles.standard;

  return (
    <div className="min-h-screen">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="mb-6">
          <h1 className="text-2xl sm:text-3xl md:text-4xl font-bold text-white">
            Nations
          </h1>
        </div>

        <div className="bg-gray-800 rounded-lg shadow-lg overflow-hidden">
          <div className="overflow-x-auto">
            <table className="min-w-full divide-y divide-gray-700">
              <thead className="bg-gray-700">
                <tr>
                  <th className={styles.header}>Nation</th>
                  <th className={`${styles.header} text-center`}>FIFA Code</th>
                  <th className={`${styles.header} text-center`}>
                    Governing Body
                  </th>
                  <th className={`${styles.header} text-center`}>Players</th>
                </tr>
              </thead>
              <tbody className="bg-gray-800 divide-y divide-gray-700">
                {nations.length === 0 ? (
                  <tr>
                    <td colSpan={4} className={styles.text.center}>
                      No nations found
                    </td>
                  </tr>
                ) : (
                  nations.map((nation) => (
                    <tr
                      key={nation.id}
                      className="hover:bg-slate-700 transition-colors"
                    >
                      <td className={styles.cell}>
                        <div className={styles.text.primary}>
                          <Link
                            href={`/nations/${nation.id}`}
                            className={`${styles.text.primary} hover:text-orange-400 transition-colors`}
                          >
                            {nation.name}
                          </Link>
                        </div>
                      </td>
                      <td className={`${styles.cell} text-center`}>
                        <div className={styles.text.secondary}>
                          {nation.country_code}
                        </div>
                      </td>
                      <td className={`${styles.cell} text-center`}>
                        <div className={styles.text.secondary}>
                          {nation.governing_body}
                        </div>
                      </td>
                      <td className={`${styles.cell} text-center`}>
                        <div className={styles.text.secondary}>
                          {nation.player_count}
                        </div>
                      </td>
                    </tr>
                  ))
                )}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}
