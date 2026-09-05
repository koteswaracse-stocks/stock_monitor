import { useEffect, useState } from 'react';

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

async function fetchJson(url) {
  try {
    const response = await fetch(url);
    const text = await response.text();
    let parsed = null;

    if (text) {
      try {
        parsed = JSON.parse(text);
      } catch {
        parsed = text;
      }
    }

    if (!response.ok) {
      const detail = parsed && typeof parsed === 'object' && parsed.detail ? `: ${parsed.detail}` : ` (HTTP ${response.status})`;
      throw new Error(`The API is unavailable at ${url}${detail}. Please make sure the backend is running on ${API_URL}.`);
    }

    return parsed;
  } catch (err) {
    if (err instanceof Error && err.message.includes('API is unavailable')) {
      throw err;
    }
    throw new Error(`Unable to reach the backend at ${API_URL}. Please start the FastAPI server before opening the dashboard.`);
  }
}

export default function App() {
  const [stocks, setStocks] = useState([]);
  const [opportunities, setOpportunities] = useState([]);
  const [selectedSymbol, setSelectedSymbol] = useState('AAPL');
  const [comparisonSymbols, setComparisonSymbols] = useState(['AAPL', 'MSFT', 'NVDA']);
  const [comparisonItems, setComparisonItems] = useState([]);
  const [portfolio, setPortfolio] = useState(null);
  const [broker, setBroker] = useState(null);
  const [analyst, setAnalyst] = useState(null);
  const [ragQuery, setRagQuery] = useState('momentum and volume');
  const [ragResults, setRagResults] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    async function loadDashboardData() {
      try {
        const [stocksData, opportunitiesData] = await Promise.all([
          fetchJson(`${API_URL}/api/stocks`),
          fetchJson(`${API_URL}/api/opportunities?limit=5`),
        ]);

        setStocks(stocksData);
        setOpportunities(opportunitiesData);
        if (stocksData.length > 0) {
          setSelectedSymbol(stocksData[0].symbol);
        }
      } catch (err) {
        setError(err.message || 'Unable to fetch market data');
      } finally {
        setLoading(false);
      }
    }

    loadDashboardData();
  }, []);

  useEffect(() => {
    if (!selectedSymbol) return;

    async function loadAnalyst() {
      try {
        const data = await fetchJson(`${API_URL}/api/analyst/${selectedSymbol}`);
        setAnalyst(data);
      } catch (err) {
        setError(err.message || 'Unable to fetch analyst insight');
      }
    }

    loadAnalyst();
  }, [selectedSymbol]);

  useEffect(() => {
    async function loadBroker() {
      try {
        const data = await fetchJson(`${API_URL}/api/broker/account`);
        setBroker(data);
      } catch (err) {
        setBroker({ broker: 'demo', status: 'demo_mode', message: 'Broker access is not configured in this environment.' });
      }
    }

    loadBroker();
  }, []);

  useEffect(() => {
    async function loadRag() {
      try {
        const data = await fetchJson(`${API_URL}/api/rag/search?query=${encodeURIComponent(ragQuery)}&limit=3`);
        setRagResults(data);
      } catch (err) {
        setError(err.message || 'Unable to fetch RAG results');
      }
    }

    loadRag();
  }, [ragQuery]);

  useEffect(() => {
    async function loadPortfolioComparison() {
      try {
        const data = await fetchJson(`${API_URL}/api/compare?${comparisonSymbols.map((symbol) => `symbols=${encodeURIComponent(symbol)}`).join('&')}`);
        setComparisonItems(data);

        const summary = await fetchJson(`${API_URL}/api/portfolio?${comparisonSymbols.map((symbol) => `symbols=${encodeURIComponent(symbol)}`).join('&')}`);
        setPortfolio(summary);
      } catch (err) {
        setError(err.message || 'Unable to fetch comparison data');
      }
    }

    if (comparisonSymbols.length > 0) {
      loadPortfolioComparison();
    }
  }, [comparisonSymbols]);

  if (loading) {
    return <div className="page">Loading market data...</div>;
  }

  if (error) {
    return <div className="page"><div className="alert">{error}</div></div>;
  }

  return (
    <div className="page">
      <header className="topbar">
        <div>
          <p className="eyebrow">AI Trading Intelligence</p>
          <h1>Stock Monitor</h1>
        </div>
        <div className="topbar-badge">{broker ? `${broker.broker.toUpperCase()} • ${broker.status}` : 'Broker demo mode'}</div>
      </header>

      <main className="grid">
        <section className="panel panel-large">
          <div className="section-header">
            <h2>Market watchlist</h2>
            <span>{stocks.length} symbols</span>
          </div>

          <div className="stock-list">
            {stocks.map((stock) => (
              <button
                key={stock.symbol}
                type="button"
                className={`stock-item ${selectedSymbol === stock.symbol ? 'selected' : ''}`}
                onClick={() => setSelectedSymbol(stock.symbol)}
              >
                <div>
                  <strong>{stock.symbol}</strong>
                  <span>{stock.name}</span>
                </div>
                <div className="stock-price">
                  <strong>${stock.price.toFixed(2)}</strong>
                  <span className={stock.day_change_pct >= 0 ? 'positive' : 'negative'}>
                    {stock.day_change_pct >= 0 ? '+' : ''}{stock.day_change_pct.toFixed(2)}%
                  </span>
                </div>
              </button>
            ))}
          </div>
        </section>

        <aside className="panel">
          <div className="section-header">
            <h2>Top opportunities</h2>
            <span>Ranked</span>
          </div>

          <div className="opportunity-list">
            {opportunities.map((opportunity) => (
              <div key={opportunity.symbol} className="opportunity-card">
                <div className="opportunity-row">
                  <strong>{opportunity.symbol}</strong>
                  <span className="score-pill">{opportunity.score.toFixed(1)}</span>
                </div>
                <p>{opportunity.name}</p>
                <small>{opportunity.reason}</small>
              </div>
            ))}
          </div>
        </aside>

        <section className="panel panel-wide">
          <div className="section-header">
            <h2>AI analyst</h2>
            <span>{selectedSymbol}</span>
          </div>

          {analyst ? (
            <>
              <h3>{analyst.symbol} — {analyst.signal}</h3>
              <div className="analyst-score">Score: {analyst.score.toFixed(1)}/100</div>
              <p>{analyst.summary}</p>
              <ul className="bullet-points">
                {analyst.bullet_points.map((point) => (
                  <li key={point}>{point}</li>
                ))}
              </ul>
            </>
          ) : (
            <p>Loading analyst summary...</p>
          )}
        </section>

        <section className="panel panel-wide">
          <div className="section-header">
            <h2>Portfolio comparison</h2>
            <span>Multi-stock view</span>
          </div>

          <div className="comparison-toolbar">
            {stocks.slice(0, 8).map((stock) => (
              <button
                key={stock.symbol}
                type="button"
                className={`chip ${comparisonSymbols.includes(stock.symbol) ? 'active' : ''}`}
                onClick={() => {
                  setComparisonSymbols((current) => {
                    if (current.includes(stock.symbol)) {
                      return current.filter((symbol) => symbol !== stock.symbol);
                    }
                    if (current.length >= 4) {
                      return [...current.slice(1), stock.symbol];
                    }
                    return [...current, stock.symbol];
                  });
                }}
              >
                {stock.symbol}
              </button>
            ))}
          </div>

          {portfolio && (
            <div className="portfolio-summary">
              <div>
                <small>Average score</small>
                <strong>{portfolio.average_score}</strong>
              </div>
              <div>
                <small>Top signal</small>
                <strong>{portfolio.top_signal}</strong>
              </div>
              <div>
                <small>Total value</small>
                <strong>${portfolio.total_value.toFixed(2)}</strong>
              </div>
              <div>
                <small>Best pick</small>
                <strong>{portfolio.best_symbol}</strong>
              </div>
            </div>
          )}

          <div className="comparison-grid">
            {comparisonItems.map((item) => (
              <div key={item.symbol} className="comparison-card">
                <div className="opportunity-row">
                  <strong>{item.symbol}</strong>
                  <span className="score-pill">{item.score.toFixed(1)}</span>
                </div>
                <p>{item.name}</p>
                <small>Price: ${item.price.toFixed(2)}</small>
                <small>Signal: {item.signal}</small>
                <small>Day change: {item.day_change_pct >= 0 ? '+' : ''}{item.day_change_pct.toFixed(2)}%</small>
              </div>
            ))}
          </div>
        </section>

        <section className="panel panel-wide">
          <div className="section-header">
            <h2>RAG research</h2>
            <span>Context retrieval</span>
          </div>

          <div className="rag-search-box">
            <input
              type="text"
              value={ragQuery}
              onChange={(event) => setRagQuery(event.target.value)}
              placeholder="Search trading context..."
            />
          </div>

          <div className="rag-results">
            {ragResults.map((result) => (
              <div key={`${result.title}-${result.score}`} className="rag-card">
                <div className="rag-header">
                  <strong>{result.title}</strong>
                  <span>{result.score}</span>
                </div>
                <p>{result.content}</p>
              </div>
            ))}
          </div>
        </section>
      </main>
    </div>
  );
}
