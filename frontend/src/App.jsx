import { useState, useEffect } from 'react';

export default function App() {
  const [orders, setOrders] = useState([]);
  const [logs, setLogs] = useState([]);

  const fetchData = async () => {
    try {
      const [ordersRes, logsRes] = await Promise.all([
        fetch('http://localhost:8080/api/orders'),
        fetch('http://localhost:8080/api/audit')
      ]);
      setOrders(await ordersRes.json());
      setLogs(await logsRes.json());
    } catch (e) {
      console.error("Backend not reachable");
    }
  };

  useEffect(() => {
    fetchData();
    const interval = setInterval(fetchData, 2000);
    return () => clearInterval(interval);
  }, []);

  const handleAction = async (orderId, action) => {
    await fetch(`http://localhost:8080/api/orders/${orderId}/${action}`, { method: 'POST' });
    fetchData(); 
  };

  const pendingCount = orders.filter(o => o.status === 'pending_approval').length;
  const blockedCount = orders.filter(o => o.status === 'blocked').length;
  const approvedVolume = orders.filter(o => o.status === 'auto_captured' || o.status === 'approved')
                               .reduce((sum, o) => sum + (o.total_amount_paise / 100), 0);

  return (
    <div className="min-h-screen bg-[#02042B] font-sans selection:bg-blue-500/30 pb-12">
      
      {/* Top Navigation Bar */}
      <nav className="bg-[#050A30] border-b border-blue-900/30 px-8 py-4 flex items-center justify-between sticky top-0 z-50">
        <div className="flex items-center gap-3">
          <svg width="28" height="28" viewBox="0 0 24 24" fill="none" stroke="#2B66FF" strokeWidth="2.5" strokeLinecap="round" strokeLinejoin="round">
            <path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/>
          </svg>
          <span className="text-white text-xl font-bold tracking-tight">AI Guard</span>
        </div>
        <div className="flex items-center gap-4">
          <div className="text-blue-400 text-xs font-semibold tracking-widest uppercase px-3 py-1 bg-blue-500/10 rounded-full border border-blue-500/20">
            Test Mode
          </div>
          <div className="w-8 h-8 rounded-full bg-blue-900/50 border border-blue-700/30 flex items-center justify-center text-white text-sm font-medium">
            M
          </div>
        </div>
      </nav>

      <main className="max-w-7xl mx-auto px-8 pt-8 space-y-10">
        
        {/* Header & Metrics */}
        <header className="flex flex-col md:flex-row md:items-end justify-between gap-6">
          <div>
            <h1 className="text-3xl text-white font-semibold">Command Center</h1>
            <p className="text-slate-400 text-sm mt-1">Monitor and control autonomous AI transactions in real-time.</p>
          </div>
          
          <div className="flex gap-4">
            <div className="bg-[#050A30] border border-blue-900/40 px-6 py-4 rounded-xl shadow-lg min-w-[160px]">
              <div className="text-xs text-slate-400 mb-1 uppercase tracking-wider font-medium">Approved Vol</div>
              <div className="text-2xl text-white font-semibold tracking-tight">₹{approvedVolume.toLocaleString()}</div>
            </div>
            <div className="bg-[#050A30] border border-blue-900/40 px-6 py-4 rounded-xl shadow-lg min-w-[160px] relative overflow-hidden">
              <div className="absolute top-0 left-0 w-1 h-full bg-amber-500"></div>
              <div className="text-xs text-slate-400 mb-1 uppercase tracking-wider font-medium pl-2">Pending</div>
              <div className="text-2xl text-amber-400 font-semibold tracking-tight pl-2">{pendingCount}</div>
            </div>
            <div className="bg-[#050A30] border border-blue-900/40 px-6 py-4 rounded-xl shadow-lg min-w-[160px] relative overflow-hidden">
              <div className="absolute top-0 left-0 w-1 h-full bg-red-500"></div>
              <div className="text-xs text-slate-400 mb-1 uppercase tracking-wider font-medium pl-2">Blocked</div>
              <div className="text-2xl text-red-400 font-semibold tracking-tight pl-2">{blockedCount}</div>
            </div>
          </div>
        </header>

        {/* Intervention Queue */}
        <section>
          <div className="flex items-center gap-3 mb-4">
            <div className="w-2 h-2 rounded-full bg-blue-500 animate-pulse"></div>
            <h2 className="text-sm text-slate-200 font-semibold uppercase tracking-widest">Live Order Queue</h2>
          </div>
          
          <div className="bg-[#050A30] border border-blue-900/30 rounded-xl shadow-xl overflow-hidden">
            <table className="w-full text-sm text-left">
              <thead className="bg-[#03061C] text-slate-400 border-b border-blue-900/30 text-xs uppercase tracking-wider">
                <tr>
                  <th className="px-6 py-4 font-medium">Order ID</th>
                  <th className="px-6 py-4 font-medium">Amount</th>
                  <th className="px-6 py-4 font-medium">Status</th>
                  <th className="px-6 py-4 font-medium w-2/5">Policy Engine Decision</th>
                  <th className="px-6 py-4 font-medium">Razorpay Link</th>
                  <th className="px-6 py-4 font-medium text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-blue-900/20">
                {orders.map(o => (
                  <tr key={o.id} className="hover:bg-[#080D3A] transition-colors group">
                    <td className="px-6 py-5 font-mono text-slate-300">{o.id}</td>
                    <td className="px-6 py-5 font-medium text-white">₹{(o.total_amount_paise / 100).toLocaleString()}</td>
                    <td className="px-6 py-5">
                      <span className={`whitespace-nowrap px-3 py-1 text-[11px] font-bold tracking-wider border rounded-full ${
                        o.status === 'pending_approval' ? 'border-amber-500/30 text-amber-400 bg-amber-500/10' :
                        o.status === 'blocked' || o.status === 'rejected' ? 'border-red-500/30 text-red-400 bg-red-500/10' :
                        'border-emerald-500/30 text-emerald-400 bg-emerald-500/10'
                      }`}>
                        {o.status.replace('_', ' ').toUpperCase()}
                      </span>
                    </td>
                    <td className="px-6 py-5 text-slate-400 text-xs leading-relaxed">{o.policy_reason}</td>
                    <td className="px-6 py-5 font-mono text-xs">
                      {o.razorpay_payment_link ? (
                        <a 
                          href={o.razorpay_payment_link} 
                          target="_blank" 
                          rel="noopener noreferrer"
                          className="text-blue-400 hover:text-blue-300 underline inline-flex items-center gap-1 font-semibold"
                        >
                          <span>Open Link</span>
                          <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"/>
                          </svg>
                        </a>
                      ) : (
                        <span className="text-slate-600">—</span>
                      )}
                    </td>
                    <td className="px-6 py-5 text-right">
                      {o.status === 'pending_approval' ? (
                        <div className="flex justify-end gap-2 opacity-90 group-hover:opacity-100 transition-opacity">
                          <button onClick={() => handleAction(o.id, 'approve')} className="px-4 py-2 bg-[#02042B] text-emerald-400 border border-emerald-500/30 hover:bg-emerald-500/10 hover:border-emerald-500/50 rounded transition-all text-xs font-bold cursor-pointer">
                            Approve
                          </button>
                          <button onClick={() => handleAction(o.id, 'reject')} className="px-4 py-2 bg-[#02042B] text-red-400 border border-red-500/30 hover:bg-red-500/10 hover:border-red-500/50 rounded transition-all text-xs font-bold cursor-pointer">
                            Reject
                          </button>
                        </div>
                      ) : (
                        <span className="text-slate-600 font-mono text-xs">—</span>
                      )}
                    </td>
                  </tr>
                ))}
                {orders.length === 0 && (
                  <tr>
                    <td colSpan="6" className="px-6 py-12 text-center text-slate-500 text-sm">
                      No orders processed yet. Waiting for AI agent activity...
                    </td>
                  </tr>
                )}
              </tbody>
            </table>
          </div>
        </section>

        {/* Audit Log */}
        <section>
          <h2 className="text-sm text-slate-400 font-semibold mb-4 uppercase tracking-widest mt-12">Raw Audit Log</h2>
          <div className="bg-[#050A30] border border-blue-900/30 rounded-xl overflow-hidden shadow-lg">
            <table className="w-full text-xs text-left">
              <thead className="bg-[#03061C] text-slate-500 border-b border-blue-900/30 uppercase tracking-wider">
                <tr>
                  <th className="px-6 py-3 font-medium">Timestamp</th>
                  <th className="px-6 py-3 font-medium">Action</th>
                  <th className="px-6 py-3 font-medium">AI Reasoning / Payload</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-blue-900/20 text-slate-400">
                {logs.map(l => (
                  <tr key={l.id} className="hover:bg-[#080D3A] transition-colors">
                    <td className="px-6 py-4 w-48 text-slate-500 font-mono">
                      {new Date(l.timestamp).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit', second:'2-digit'})}
                    </td>
                    <td className="px-6 py-4 text-blue-400 font-semibold font-mono w-40">{l.action}()</td>
                    <td className="px-6 py-4 opacity-90 leading-relaxed text-[13px]">
                      {l.payload?.agent_reasoning || JSON.stringify(l.payload)}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </section>

      </main>
    </div>
  );
}