import { useState } from 'react';
import { Cpu, BarChart3, Shield } from 'lucide-react';
import { motion } from 'framer-motion';
import UploadZone from '../components/UploadZone';
import ReportCard from '../components/ReportCard';
import LoadingSkeleton from '../components/LoadingSkeleton';

export default function Dashboard() {
  const [loading, setLoading] = useState(false);
  const [report, setReport] = useState(null);
  const [showReport, setShowReport] = useState(false);
  const [taskId, setTaskId] = useState(null);

  function handleAnalysisStart() {
    setLoading(true);
    setReport(null);
    setShowReport(false);
    setTaskId(null);
  }

  function handleAnalysisComplete(result, id) {
    setReport(result);
    setLoading(false);
    setShowReport(true);
    setTaskId(id || null);
  }

  function handleReset() {
    setReport(null);
    setLoading(false);
    setShowReport(false);
  }

  return (
    <div className='max-w-6xl mx-auto px-6 py-8 md:py-12'>
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5 }}
        className='text-center mb-12 md:mb-16'>
        <div className='w-16 h-16 rounded-2xl bg-gradient-to-br from-cyan-500 to-emerald-500 mx-auto flex items-center justify-center shadow-xl shadow-cyan-500/20 mb-6'>
          <Cpu className='w-8 h-8 text-white' />
        </div>
        <h1 className='text-4xl md:text-5xl font-bold text-slate-100 mb-4 tracking-tight'>
          Analyze your repository's{' '}
          <span className='text-transparent bg-clip-text bg-gradient-to-r from-cyan-400 to-emerald-400'>engineering health</span>
        </h1>
        <p className='text-slate-400 text-lg max-w-2xl mx-auto leading-relaxed'>
          Upload a ZIP or enter a GitHub URL to get an instant engineering audit with code quality metrics,
          architecture analysis, and actionable recommendations.
        </p>
      </motion.div>

      {!showReport && !loading && (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.5, delay: 0.2 }}
          className='grid grid-cols-1 md:grid-cols-3 gap-6 mb-10'>
          {[
            { icon: Shield, label: 'Health Score', desc: 'Comprehensive engineering audit' },
            { icon: BarChart3, label: 'Code Metrics', desc: 'Lines, complexity, ratios' },
            { icon: Cpu, label: 'Stack Detection', desc: 'Frameworks & architecture' },
          ].map(({ icon: Icon, label, desc }, i) => (
            <div key={i} className='p-5 rounded-2xl bg-slate-900/40 border border-slate-800/50 backdrop-blur-xl flex items-center gap-4'>
              <div className='w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/20 flex items-center justify-center flex-shrink-0'>
                <Icon className='w-5 h-5 text-cyan-400' />
              </div>
              <div>
                <p className='text-sm font-medium text-slate-200'>{label}</p>
                <p className='text-xs text-slate-500 mt-0.5'>{desc}</p>
              </div>
            </div>
          ))}
        </motion.div>
      )}

      <UploadZone onAnalysisStart={handleAnalysisStart} onAnalysisComplete={handleAnalysisComplete} />

      {loading && <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }}><LoadingSkeleton /></motion.div>}

      {showReport && report && (
        <>
          <div className='flex items-center justify-between mb-6'>
            <h2 className='text-xl font-semibold text-slate-200'>Analysis Report</h2>
            <div className='flex gap-3'>
              <button onClick={handleReset}
                className='px-4 py-2 rounded-xl bg-slate-800 text-slate-300 text-sm font-medium hover:bg-slate-700 transition-all'>
                Analyze Another
              </button>
            </div>
          </div>
          <ReportCard data={report} taskId={taskId} />
        </>
      )}
    </div>
  );
}
