import { useState } from 'react';
import { GitCompare, Upload, Github, Loader2, ArrowRight } from 'lucide-react';
import api from '../api/api';
import HealthGauge from '../components/HealthGauge';

export default function ComparePage() {
  const [mode, setMode] = useState('upload');
  const [fileA, setFileA] = useState(null);
  const [fileB, setFileB] = useState(null);
  const [urlA, setUrlA] = useState('');
  const [urlB, setUrlB] = useState('');
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState(null);
  const [error, setError] = useState('');

  async function handleCompare() {
    setLoading(true); setError(''); setResult(null);
    try {
      if (mode === 'upload') {
        if (!fileA || !fileB) { setError('Please select both ZIP files.'); setLoading(false); return; }
        const fd = new FormData(); fd.append('file', fileA);
        const rA = await api.post('/upload/', fd);
        const fd2 = new FormData(); fd2.append('file', fileB);
        const rB = await api.post('/upload/', fd2);
        const cmp = await api.post('/compare/zip', { file_id_a: rA.data.file_id, file_id_b: rB.data.file_id });
        await pollCompare(cmp.data.task_id);
      } else {
        if (!urlA.startsWith('https://github.com/') || !urlB.startsWith('https://github.com/')) {
          setError('Both URLs must be valid GitHub URLs.'); setLoading(false); return;
        }
        const cmp = await api.post('/compare/github', { repo_url_a: urlA, repo_url_b: urlB });
        await pollCompare(cmp.data.task_id);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Comparison failed.');
      setLoading(false);
    }
  }

  async function pollCompare(taskId) {
    let complete = false;
    while (!complete) {
      const res = await api.get('/results/' + taskId);
      const data = res.data;
      if (data.status === 'completed') { setResult(data.result); complete = true; }
      else if (data.status === 'failed') { setError(data.error || 'Comparison failed.'); complete = true; }
      if (!complete) await new Promise(r => setTimeout(r, 1500));
    }
    setLoading(false);
  }

  const btnClass = (active) => 'flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all ' + (active ? 'bg-slate-800 text-slate-100' : 'text-slate-400 hover:text-slate-200');

  return (
    <div className='max-w-6xl mx-auto px-6 py-8 md:py-12'>
      <div className='text-center mb-10'>
        <div className='w-14 h-14 rounded-2xl bg-purple-500/10 border border-purple-500/20 mx-auto flex items-center justify-center mb-4'>
          <GitCompare className='w-7 h-7 text-purple-400' />
        </div>
        <h1 className='text-3xl md:text-4xl font-bold text-slate-100 mb-3'>Compare Repositories</h1>
        <p className='text-slate-400 text-lg max-w-2xl mx-auto leading-relaxed'>Analyze two repositories side-by-side and see which one scores higher</p>
      </div>

      <div className='flex items-center gap-2 mb-6'>
        <button onClick={() => setMode('upload')} className={btnClass(mode === 'upload')}>
          <Upload className='w-4 h-4' /> Upload ZIPs
        </button>
        <button onClick={() => setMode('github')} className={btnClass(mode === 'github')}>
          <Github className='w-4 h-4' /> GitHub URLs
        </button>
      </div>

      {mode === 'upload' ? (
        <div className='grid grid-cols-1 md:grid-cols-2 gap-6 mb-6'>
          {['A', 'B'].map((label) => (
            <div key={label} className='p-6 rounded-2xl border border-dashed border-slate-700 bg-slate-900/40 text-center cursor-pointer hover:border-slate-500 transition-all'
              onClick={() => document.getElementById('f' + label).click()}>
              <input id={'f' + label} type='file' accept='.zip' hidden
                onChange={e => label === 'A' ? setFileA(e.target.files[0]) : setFileB(e.target.files[0])} />
              <p className='text-sm text-slate-400'>Repository {label}</p>
              <p className='text-sm text-slate-300 mt-1 font-medium'>
                {(label === 'A' ? fileA : fileB) ? (label === 'A' ? fileA : fileB).name : 'Click to select ZIP'}
              </p>
            </div>
          ))}
        </div>
      ) : (
        <div className='grid grid-cols-1 md:grid-cols-2 gap-6 mb-6'>
          <input type='text' value={urlA} onChange={e => setUrlA(e.target.value)} placeholder='https://github.com/user/repo-a'
            className='px-4 py-3 rounded-xl bg-slate-800/80 border border-slate-700 text-slate-100 placeholder-slate-500 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500/40' />
          <input type='text' value={urlB} onChange={e => setUrlB(e.target.value)} placeholder='https://github.com/user/repo-b'
            className='px-4 py-3 rounded-xl bg-slate-800/80 border border-slate-700 text-slate-100 placeholder-slate-500 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500/40' />
        </div>
      )}

      <button onClick={handleCompare} disabled={loading}
        className='w-full flex items-center justify-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-purple-500 to-pink-500 text-white font-medium text-sm hover:shadow-lg hover:shadow-purple-500/25 transition-all disabled:opacity-50 mb-8'>
        {loading ? <><Loader2 className='w-4 h-4 animate-spin' /> Comparing...</> : <>Compare <ArrowRight className='w-4 h-4' /></>}
      </button>

      {error && <div className='p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm mb-6'>{error}</div>}

      {result && (
        <div className='grid grid-cols-1 md:grid-cols-2 gap-6'>
          {['repo_a', 'repo_b'].map((key, i) => {
            const repo = result[key];
            const label = i === 0 ? 'Repository A' : 'Repository B';
            const isWinner = result.comparison?.winner === key;
            return (
              <div key={key} className={'p-6 md:p-8 rounded-2xl border backdrop-blur-xl ' + (isWinner ? 'bg-emerald-500/5 border-emerald-500/20' : 'bg-slate-900/60 border-slate-800')}>
                <div className='flex items-center justify-between mb-4'>
                  <h3 className='text-sm font-semibold text-slate-400 uppercase tracking-wider'>{label}</h3>
                  {isWinner && <span className='text-xs font-medium text-emerald-400 bg-emerald-500/10 px-2.5 py-1 rounded-full'>WINNER</span>}
                </div>
                <HealthGauge score={repo?.health_score || 0} grade={repo?.grade || 'N/A'} size='sm' />
                <div className='mt-4 space-y-2 text-sm'>
                  <div className='flex justify-between'><span className='text-slate-400'>Files</span><span className='text-slate-200 font-medium'>{repo?.project?.total_files || 0}</span></div>
                  <div className='flex justify-between'><span className='text-slate-400'>Language</span><span className='text-slate-200 font-medium'>{repo?.project?.primary_language || '—'}</span></div>
                  <div className='flex justify-between'><span className='text-slate-400'>Frameworks</span><span className='text-slate-200 font-medium'>{(repo?.project?.frameworks || []).join(', ') || '—'}</span></div>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </div>
  );
}
