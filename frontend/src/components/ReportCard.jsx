import { motion } from 'framer-motion';
import { CheckCircle2, AlertTriangle, ArrowRight, Lightbulb, FileText, Activity, Layout, Brain, Download, Sparkles } from 'lucide-react';
import HealthGauge from './HealthGauge';
import LanguageChart from './LanguageChart';
import { useState } from 'react';
import api from '../api/api';

export default function ReportCard({ data, taskId }) {
  if (!data) return null;
  const { summary, project, metrics, architecture, ai_analysis, refactoring_suggestions } = data;
  const [aiLoading, setAiLoading] = useState(false);
  const [aiData, setAiData] = useState(ai_analysis || null);
  const [aiError, setAiError] = useState('');

  async function handleAiAnalysis() {
    if (aiData) return; // Already loaded
    if (!taskId) { setAiError('No task ID available for AI analysis.'); return; }
    setAiLoading(true);
    setAiError('');
    try {
      const res = await api.post(`/analyze/ai/${taskId}`);
      const result = res.data.result;
      if (result?.ai_analysis) {
        setAiData(result.ai_analysis);
      } else {
        setAiError('AI analysis returned no data. Check your LLM_API_KEY in .env');
      }
    } catch (err) {
      setAiError(err.response?.data?.detail || 'AI analysis failed. Is the API key configured?');
    }
    setAiLoading(false);
  }

  async function handleDownloadReport() {
    if (!taskId) return;
    const a = document.createElement('a');
    a.href = api.defaults.baseURL + '/report/' + taskId;
    a.download = `engineeros-report-${taskId.slice(0, 8)}.html`;
    a.click();
  }
  return (
    <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }} className='space-y-6'>
      <div className='grid grid-cols-1 md:grid-cols-4 gap-6'>
        <div className='p-6 md:p-8 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-xl flex items-center justify-center'>
          <HealthGauge score={data.health_score} grade={data.grade} size='lg' />
        </div>
        {[
          { icon: FileText, label: 'Files', value: metrics?.total_files || project?.total_files || 0, sub: 'code files scanned', color: 'cyan' },
          { icon: Activity, label: 'Lines', value: (metrics?.total_code_lines || 0).toLocaleString(), sub: 'lines of code', color: 'emerald' },
          { icon: Layout, label: 'Architecture', value: architecture?.architecture_type || '—', sub: project?.repository_type || '—', color: 'amber' },
        ].map(({ icon: Icon, label, value, sub, color }) => {
          const c = color === 'cyan' ? 'cyan' : color === 'emerald' ? 'emerald' : 'amber';
          return (
            <div key={label} className={'p-6 md:p-8 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-xl'}>
              <div className='flex items-center gap-3 mb-4'>
                <div className={'w-10 h-10 rounded-xl bg-' + c + '-500/10 border border-' + c + '-500/20 flex items-center justify-center'}>
                  <Icon className={'w-5 h-5 text-' + c + '-400'} />
                </div>
                <span className='text-sm font-semibold text-slate-400 uppercase tracking-wider'>{label}</span>
              </div>
              <p className='text-3xl font-bold text-slate-100'>{value}</p>
              <p className='text-sm text-slate-500 mt-1'>{sub}</p>
            </div>
          );
        })}
      </div>

      <LanguageChart extensionCounts={metrics?.extension_counts || project?.extensions} />

      <div className='grid grid-cols-1 md:grid-cols-3 gap-6'>
        {[
          { title: 'Strengths', icon: CheckCircle2, items: summary?.strengths || [], color: 'emerald', placeholder: 'No strengths identified' },
          { title: 'Risks', icon: AlertTriangle, items: summary?.risks || [], color: 'amber', placeholder: 'No risks identified' },
          { title: 'Recommendations', icon: Lightbulb, items: summary?.recommendations || [], color: 'cyan', placeholder: 'No recommendations' },
        ].map(({ title, icon: Icon, items, color, placeholder }) => (
          <div key={title} className={'p-6 md:p-8 rounded-2xl bg-' + color + '-500/5 border border-' + color + '-500/10 backdrop-blur-xl'}>
            <div className='flex items-center gap-3 mb-4'>
              <Icon className={'w-5 h-5 text-' + color + '-400'} />
              <h3 className='text-sm font-semibold text-slate-300 uppercase tracking-wider'>{title}</h3>
            </div>
            <ul className='space-y-3'>
              {items.length === 0 ? (
                <li className='text-sm text-slate-500'>{placeholder}</li>
              ) : items.map((item, i) => (
                <motion.li key={i} initial={{ opacity: 0, x: -10 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.05 }}
                  className='flex items-start gap-2 text-sm text-slate-300'>
                  <span className={'mt-0.5 w-1.5 h-1.5 rounded-full bg-' + color + '-400 flex-shrink-0'} />
                  {item}
                </motion.li>
              ))}
            </ul>
          </div>
        ))}
      </div>

      <div className='p-6 md:p-8 rounded-2xl bg-slate-900/60 border border-slate-800 backdrop-blur-xl'>
        <h3 className='text-sm font-semibold text-slate-400 uppercase tracking-wider mb-3'>Executive Summary</h3>
        <p className='text-slate-300 leading-relaxed'>{summary?.executive_summary || 'No summary available.'}</p>
      </div>

      {/* AI Analysis Section */}
      <div className='p-6 md:p-8 rounded-2xl bg-gradient-to-br from-purple-900/30 to-cyan-900/20 border border-purple-500/20 backdrop-blur-xl'>
        <div className='flex items-center justify-between mb-4'>
          <div className='flex items-center gap-3'>
            <div className='w-10 h-10 rounded-xl bg-purple-500/10 border border-purple-500/20 flex items-center justify-center'>
              <Brain className='w-5 h-5 text-purple-400' />
            </div>
            <h3 className='text-sm font-semibold text-purple-300 uppercase tracking-wider'>AI-Powered Analysis</h3>
          </div>
          <div className='flex gap-2'>
            {taskId && (
              <button onClick={handleDownloadReport}
                className='flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800 text-slate-300 text-xs font-medium hover:bg-slate-700 transition-all'>
                <Download className='w-3.5 h-3.5' /> Download Report
              </button>
            )}
            <button onClick={handleAiAnalysis} disabled={aiLoading || !!aiData}
              className='flex items-center gap-2 px-3 py-1.5 rounded-lg bg-gradient-to-r from-purple-500 to-cyan-500 text-white text-xs font-medium hover:shadow-lg hover:shadow-purple-500/25 transition-all disabled:opacity-50'>
              {aiLoading ? 'Analyzing...' : aiData ? 'AI Done' : <><Sparkles className='w-3.5 h-3.5' /> Run AI Analysis</>}
            </button>
          </div>
        </div>

        {aiError && (
          <div className='p-3 rounded-lg bg-amber-500/10 border border-amber-500/20 text-amber-400 text-xs mb-3'>
            {aiError}
          </div>
        )}

        {aiLoading && (
          <div className='flex items-center gap-3 text-sm text-slate-400'>
            <div className='w-4 h-4 rounded-full border-2 border-purple-400 border-t-transparent animate-spin' />
            Calling LLM for intelligent analysis... (may take 30-60s)
          </div>
        )}

        {aiData && (
          <div className='space-y-4 mt-2'>
            <p className='text-sm text-slate-300 leading-relaxed'>{aiData.executive_summary}</p>
            <div className='grid grid-cols-1 md:grid-cols-3 gap-4'>
              <div>
                <h4 className='text-xs font-semibold text-emerald-400 uppercase tracking-wider mb-2'>Strengths</h4>
                <ul className='space-y-1.5'>
                  {(aiData.strengths || []).map((s, i) => (
                    <li key={i} className='flex items-start gap-2 text-xs text-slate-300'>
                      <span className='mt-1 w-1.5 h-1.5 rounded-full bg-emerald-400 flex-shrink-0' />{s}
                    </li>
                  ))}
                </ul>
              </div>
              <div>
                <h4 className='text-xs font-semibold text-amber-400 uppercase tracking-wider mb-2'>Risks</h4>
                <ul className='space-y-1.5'>
                  {(aiData.risks || []).map((s, i) => (
                    <li key={i} className='flex items-start gap-2 text-xs text-slate-300'>
                      <span className='mt-1 w-1.5 h-1.5 rounded-full bg-amber-400 flex-shrink-0' />{s}
                    </li>
                  ))}
                </ul>
              </div>
              <div>
                <h4 className='text-xs font-semibold text-cyan-400 uppercase tracking-wider mb-2'>Recommendations</h4>
                <ul className='space-y-1.5'>
                  {(aiData.recommendations || []).map((s, i) => (
                    <li key={i} className='flex items-start gap-2 text-xs text-slate-300'>
                      <span className='mt-1 w-1.5 h-1.5 rounded-full bg-cyan-400 flex-shrink-0' />{s}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
            {(aiData.refactoring_suggestions || []).length > 0 && (
              <div>
                <h4 className='text-xs font-semibold text-purple-400 uppercase tracking-wider mb-2'>Refactoring Suggestions</h4>
                <div className='grid grid-cols-1 md:grid-cols-2 gap-2'>
                  {aiData.refactoring_suggestions.map((s, i) => (
                    <div key={i} className='p-3 rounded-lg bg-slate-800/50 border border-slate-700/50'>
                      <div className='flex items-center justify-between mb-1'>
                        <span className='text-xs font-medium text-purple-300'>{s.area}</span>
                        <span className={'text-[10px] px-1.5 py-0.5 rounded-full ' + (s.priority === 'high' ? 'bg-red-500/20 text-red-400' : s.priority === 'medium' ? 'bg-amber-500/20 text-amber-400' : 'bg-green-500/20 text-green-400')}>
                          {s.priority}
                        </span>
                      </div>
                      <p className='text-xs text-slate-400'>{s.description}</p>
                    </div>
                  ))}
                </div>
              </div>
            )}
            <p className='text-[10px] text-slate-500'>Powered by {aiData.model_used || 'LLM'}</p>
          </div>
        )}

        {!aiData && !aiLoading && !aiError && (
          <p className='text-xs text-slate-500'>Click "Run AI Analysis" to get LLM-powered insights (requires API key in .env)</p>
        )}
      </div>
    </motion.div>
  );
}
