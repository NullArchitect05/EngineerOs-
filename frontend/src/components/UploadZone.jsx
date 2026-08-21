import { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, Github, FileArchive, ArrowRight, Loader2 } from 'lucide-react';
import api from '../api/api';

export default function UploadZone({ onAnalysisStart, onAnalysisComplete }) {
  const [githubUrl, setGithubUrl] = useState('');
  const [mode, setMode] = useState('upload');
  const [loading, setLoading] = useState(false);
  const [progress, setProgress] = useState(0);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');

  const onDrop = useCallback(async (acceptedFiles) => {
    const file = acceptedFiles[0];
    if (!file) return;
    if (!file.name.endsWith('.zip')) { setError('Only ZIP files are supported.'); return; }
    setLoading(true); setError(''); setProgress(10); setMessage('Uploading...');
    onAnalysisStart?.();
    try {
      const formData = new FormData();
      formData.append('file', file);
      const uploadRes = await api.post('/upload/', formData);
      const fileId = uploadRes.data.file_id;
      setProgress(25); setMessage('Starting analysis...');
      const analyzeRes = await api.post('/analyze/', { file_id: fileId });
      if (analyzeRes.data.status === 'completed') {
        setProgress(100); setMessage('Analysis complete!');
        setLoading(false);
        onAnalysisComplete?.(analyzeRes.data.result, analyzeRes.data.task_id);
      } else {
        await pollResults(analyzeRes.data.task_id);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'Analysis failed. Is the backend running?');
      setLoading(false);
    }
  }, [onAnalysisStart, onAnalysisComplete]);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop, accept: { 'application/zip': ['.zip'] }, maxFiles: 1, disabled: loading,
  });

  async function pollResults(taskId) {
    let complete = false;
    while (!complete) {
      try {
        const res = await api.get('/results/' + taskId);
        const data = res.data;
        if (data.status === 'completed') {
          setProgress(100); setMessage('Analysis complete!'); complete = true;
          onAnalysisComplete?.(data.result, taskId);
        } else if (data.status === 'failed') {
          setError(data.error || 'Analysis failed.'); complete = true;
        } else {
          setProgress(data.progress || 50);
          setMessage(data.message || 'Analyzing...');
        }
      } catch (err) {
        const msg = err.response?.data?.detail || err.message || 'Failed to fetch results.';
        setError('Failed to fetch results. ' + msg);
        complete = true;
      }
      if (!complete) await new Promise((r) => setTimeout(r, 1500));
    }
    setLoading(false);
  }

  async function handleGithubAnalyze() {
    const url = githubUrl.trim();
    if (!url || !url.startsWith('https://github.com/')) {
      setError('Please enter a valid GitHub URL.'); return;
    }
    setLoading(true); setError(''); setProgress(15); setMessage('Connecting to GitHub...');
    onAnalysisStart?.();
    try {
      const res = await api.post('/analyze/github/', { repo_url: url });
      if (res.data.status === 'completed') {
        setProgress(100); setMessage('Analysis complete!');
        setLoading(false);
        onAnalysisComplete?.(res.data.result, res.data.task_id);
      } else {
        await pollResults(res.data.task_id);
      }
    } catch (err) {
      setError(err.response?.data?.detail || 'GitHub analysis failed.');
      setLoading(false);
    }
  }

  const btnClass = (active) => 'flex items-center gap-2 px-4 py-2 rounded-xl text-sm font-medium transition-all ' + (active ? 'bg-slate-800 text-slate-100' : 'text-slate-400 hover:text-slate-200');

  return (
    <div className='mb-12'>
      <div className='flex items-center gap-2 mb-6'>
        <button onClick={() => setMode('upload')} className={btnClass(mode === 'upload')}>
          <FileArchive className='w-4 h-4' /> Upload ZIP
        </button>
        <button onClick={() => setMode('github')} className={btnClass(mode === 'github')}>
          <Github className='w-4 h-4' /> GitHub URL
        </button>
      </div>

      {mode === 'upload' && (
        <div {...getRootProps()}
          className={'p-10 md:p-12 rounded-2xl border-2 border-dashed text-center cursor-pointer transition-all ' + (loading ? 'border-slate-700 bg-slate-900/40' : isDragActive ? 'border-cyan-400 bg-cyan-500/5' : 'border-slate-700 bg-slate-900/60 hover:border-slate-500 hover:bg-slate-900/80')}>
          <input {...getInputProps()} />
          {loading ? (
            <div className='flex flex-col items-center gap-4'>
              <Loader2 className='w-10 h-10 text-cyan-400 animate-spin' />
              <p className='text-slate-300 font-medium'>{message}</p>
            </div>
          ) : (
            <div className='flex flex-col items-center gap-4'>
              <div className='w-16 h-16 rounded-2xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center'>
                <Upload className='w-8 h-8 text-cyan-400' />
              </div>
              <div>
                <p className='text-slate-200 text-lg font-medium'>{isDragActive ? 'Drop your ZIP here' : 'Drop repository ZIP here'}</p>
                <p className='text-slate-500 text-sm mt-1'>or click to browse files</p>
              </div>
            </div>
          )}
        </div>
      )}

      {mode === 'github' && (
        <div className='p-8 md:p-10 rounded-2xl border border-slate-800 bg-slate-900/60 backdrop-blur-xl'>
          <div className='flex flex-col gap-4'>
            <label className='text-sm font-medium text-slate-300'>Paste a GitHub repository URL</label>
            <div className='flex gap-3'>
              <input type='text' value={githubUrl} onChange={(e) => setGithubUrl(e.target.value)}
                placeholder='https://github.com/user/repository' disabled={loading}
                className='flex-1 px-4 py-3 rounded-xl bg-slate-800/80 border border-slate-700 text-slate-100 placeholder-slate-500 text-sm focus:outline-none focus:ring-2 focus:ring-cyan-500/40' />
              <button onClick={handleGithubAnalyze} disabled={loading || !githubUrl.trim()}
                className='flex items-center gap-2 px-6 py-3 rounded-xl bg-gradient-to-r from-cyan-500 to-emerald-500 text-white font-medium text-sm hover:shadow-lg hover:shadow-cyan-500/25 transition-all disabled:opacity-50 disabled:cursor-not-allowed'>
                {loading ? <><Loader2 className='w-4 h-4 animate-spin' /> {message}</> : <>Analyze <ArrowRight className='w-4 h-4' /></>}
              </button>
            </div>
          </div>
        </div>
      )}

      {loading && (
        <div className='mt-6 p-5 rounded-xl bg-slate-900/60 border border-slate-800'>
          <div className='flex items-center justify-between mb-3'>
            <span className='text-sm text-slate-400'>{message}</span>
            <span className='text-sm font-medium text-cyan-400'>{progress}%</span>
          </div>
          <div className='h-2 rounded-full bg-slate-800 overflow-hidden'>
            <div className='h-full rounded-full bg-gradient-to-r from-cyan-500 to-emerald-500 transition-all duration-500 ease-out' style={{ width: progress + '%' }} />
          </div>
        </div>
      )}

      {error && <div className='mt-6 p-4 rounded-xl bg-red-500/10 border border-red-500/20 text-red-400 text-sm'>{error}</div>}
    </div>
  );
}

