
import { useEffect, useState } from "react";
import {
  ResponsiveContainer,
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  Legend,
} from "recharts";
import {
  Wind,
  TrendingUp,
  Activity,
  Clock,
  Target,
  CheckCircle2,
} from "lucide-react";
import "./App.css";
import { getJanuaryAnalysis } from "./api";


function formatNumber(value, decimals = 0) {
  if (typeof value !== "number" || !Number.isFinite(value)) {
    return "—";
  }

  return value.toLocaleString("en-GB", {
    minimumFractionDigits: decimals,
    maximumFractionDigits: decimals,
  });
}

function formatInterval(timestamp) {
  const date = new Date(timestamp);

  if (Number.isNaN(date.getTime())) {
    return timestamp;
  }

  return date.toLocaleString("en-GB", {
    timeZone: "UTC",
    day: "2-digit",
    month: "short",
    hour: "2-digit",
    minute: "2-digit",
    hour12: false,
  });
}

function App() {
  const [analysis, setAnalysis] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    let cancelled = false;

    async function loadAnalysis() {
      try {
        setLoading(true);
        setError("");

        const data = await getJanuaryAnalysis();

        if (data.error) {
          throw new Error(data.error);
        }

        if (!cancelled) {
          setAnalysis(data);
        }
      } catch (err) {
        if (!cancelled) {
          setError(
            err.message ||
              "Unable to connect to the analysis API."
          );
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    }

    loadAnalysis();

    return () => {
      cancelled = true;
    };
  }, []);

  const metrics = analysis
    ? [
        {
          label: "Mean absolute error",
          value: analysis.metrics?.mae_mw,
          unit: "MW",
          description: "Average absolute forecast error",
          Icon: Activity,
          decimals: 2,
        },
        {
          label: "Root mean square error",
          value: analysis.metrics?.rmse_mw,
          unit: "MW",
          description: "Penalizes larger errors",
          Icon: TrendingUp,
          decimals: 2,
        },
        {
          label: "Forecast bias",
          value: analysis.metrics?.bias_mw,
          unit: "MW",
          description:
            "Positive means overforecasting; negative means underforecasting",
          Icon: Wind,
          decimals: 2,
        },
        {
          label: "Data coverage",
          value: analysis.coverage_percent,
          unit: "%",
          description: `${formatNumber(
            analysis.matched_intervals
          )} of ${formatNumber(
            analysis.expected_january_intervals
          )} hourly intervals matched`,
          Icon: Target,
          decimals: 1,
        },
      ]
    : [];

  const chartData = (analysis?.rows || []).map((row) => ({
    time: formatInterval(row.startTime),
    timestamp: row.startTime,
    actual_mw: row.actual_mw,
    forecast_mw: row.forecast_mw,
    error_mw: row.error_mw,
  }));

  const coverageComplete =
    analysis &&
    analysis.coverage_percent === 100 &&
    analysis.matched_intervals === analysis.expected_january_intervals;

  return (
    <main className="app">
      <header className="topbar">
        <div className="brand">
          <div className="brand-icon">
            <Wind size={23} />
          </div>
          <div>
            <h1>WindScope</h1>
            <p>UK WIND GENERATION ANALYTICS</p>
          </div>
        </div>

        <span className="demo-badge">
          HISTORICAL ANALYSIS
        </span>
      </header>

      <section className="intro">
        <p className="eyebrow">GENERATION INTELLIGENCE</p>
        <h2>Wind forecast performance</h2>
        <p>
          Compare forecast wind generation against actual output,
          quantify forecast error, and assess the quality of the
          available data.
        </p>
      </section>

      {loading && (
        <p role="status">Loading January 2026 analysis from Elexon...</p>
      )}

      {error && (
        <div className="notice" role="alert">
          <strong>Unable to load the analysis.</strong>
          <p>{error}</p>
          <p>
            Check that the Flask backend is running and that
            /api/analysis/january-2026 works in your browser.
          </p>
        </div>
      )}

      {!loading && !error && analysis && (
        <>
          <section className="metrics">
            {metrics.map(
              ({ label, value, unit, description, Icon, decimals }) => (
                <article className="metric" key={label}>
                  <div className="metric-heading">
                    <span>{label}</span>
                    <Icon size={19} />
                  </div>

                  <strong>
                    {formatNumber(value, decimals)}{" "}
                    <small>{unit}</small>
                  </strong>

                  <p>{description}</p>
                </article>
              )
            )}
          </section>

          <section className="chart-card">
            <div className="chart-heading">
              <div>
                <h3>Actual vs forecast generation</h3>
                <p>
                  January 2026 · Hourly values · MW · UTC
                </p>
              </div>
            </div>

            {chartData.length > 0 ? (
              <div className="chart">
                <ResponsiveContainer width="100%" height="100%">
                  <LineChart
                    data={chartData}
                    margin={{
                      top: 10,
                      right: 20,
                      left: 10,
                      bottom: 5,
                    }}
                  >
                    <CartesianGrid
                      strokeDasharray="3 3"
                      stroke="#e8edf2"
                    />

                    <XAxis
                      dataKey="time"
                      interval={47}
                      minTickGap={25}
                      tick={{ fontSize: 11 }}
                    />

                    <YAxis
                      width={75}
                      tick={{ fontSize: 11 }}
                      tickFormatter={(value) =>
                        `${(value / 1000).toFixed(0)}k`
                      }
                      label={{
                        value: "Generation (MW)",
                        angle: -90,
                        position: "insideLeft",
                        style: { textAnchor: "middle" },
                      }}
                    />

                    <Tooltip
                      labelFormatter={(label) => `UTC: ${label}`}
                      formatter={(value, name) => [
                        `${formatNumber(value, 2)} MW`,
                        name,
                      ]}
                    />

                    <Legend />

                    <Line
                      type="monotone"
                      dataKey="actual_mw"
                      name="Actual generation"
                      stroke="#087f8c"
                      strokeWidth={2}
                      dot={false}
                      isAnimationActive={false}
                      connectNulls={false}
                    />

                    <Line
                      type="monotone"
                      dataKey="forecast_mw"
                      name="Forecast generation"
                      stroke="#e7a23b"
                      strokeWidth={2}
                      strokeDasharray="6 4"
                      dot={false}
                      isAnimationActive={false}
                      connectNulls={false}
                    />
                  </LineChart>
                </ResponsiveContainer>
              </div>
            ) : (
              <p>No matched forecast data is available to chart.</p>
            )}

            <p className="notice">
              Each point compares one hourly forecast with the hourly
              average of two half-hourly actual readings.
            </p>
          </section>

          <section className="chart-card">
            <div className="chart-heading">
              <div>
                <h3>Analysis details</h3>
                <p>Data quality and evaluation assumptions</p>
              </div>
              {coverageComplete && (
                <CheckCircle2 size={22} />
              )}
            </div>

            <div className="analysis-details">
              <p>
                <strong>Analysis period:</strong>{" "}
                {analysis.period}
              </p>

              <p>
                <strong>Matched intervals:</strong>{" "}
                {formatNumber(analysis.matched_intervals)} of{" "}
                {formatNumber(analysis.expected_january_hours ?? 744)}
              </p>

              <p>
                <strong>Forecast publication cutoff:</strong>{" "}
                {formatNumber(analysis.cutoff_hour_utc)}:00 UTC on
                the previous day
              </p>

              <p>
                <strong>Actual data intervals:</strong>{" "}
                {formatNumber(analysis.actual_hourly_intervals ?? 744)}
              </p>

              <p>
                <strong>Forecast target intervals:</strong>{" "}
                {formatNumber(analysis.forecast_target_hours ?? 744)}
              </p>
            </div>

            <p className="notice">
              {analysis.warning ||
                "Forecast selection and hourly aggregation assumptions should be validated before operational use."}
            </p>
          </section>
        </>
      )}

      <footer>
        WindScope · January 2026 historical analysis · Elexon datasets
      </footer>
    </main>
  );
}

export default App;
