import { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import { CheckCircle2, Cpu, Zap, Shield, Download, Brain } from 'lucide-react';
import api from '../api/api';

const plans = [
  { name: 'Free', price: '$0', period: 'forever', scans: '3 scans / month',
    features: ['Full repo analysis', 'Code metrics & smells', 'Architecture detection', 'Compare 2 repos'],
    cta: 'Current Plan', popular: false },
  { name: 'Pro', price: '$5.99', period: '/ month', scans: 'Unlimited scans',
    features: ['Everything in Free', 'AI-powered analysis', 'Downloadable reports', 'Unlimited repo scans', 'Priority support'],
    cta: 'Get Pro', popular: true },
  { name: 'Team', price: '$14.99', period: '/ month', scans: 'Unlimited scans',
    features: ['Everything in Pro', 'Team dashboard', 'API access', 'Custom integrations', 'Dedicated support'],
    cta: 'Coming Soon', popular: false },
];

export default function PricingPage() {
  const [usage, setUsage] = useState(null);

  useEffect(() => {
    api.get('/pricing/status').then(res => setUsage(res.data)).catch(() => {});
  }, []);

  return (
    <div className='max-w-6xl mx-auto px-6 py-8 md:py-12'>
      <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} className='text-center mb-12'>
        <div className='w-16 h-16 rounded-2xl bg-gradient-to-br from-purple-500 to-cyan-500 mx-auto flex items-center justify-center shadow-xl shadow-purple-500/20 mb-6'>
          <Zap className='w-8 h-8 text-white' />
        </div>
        <h1 className='text-4xl md:text-5xl font-bold text-slate-100 mb-4'>
          Simple, <span className='text-transparent bg-clip-text bg-gradient-to-r from-purple-400 to-cyan-400'>developer-friendly</span> pricing
        </h1>
        <p className='text-slate-400 text-lg'>Start with 3 free scans. Upgrade to Pro for unlimited scanning.</p>
      </motion.div>

      {usage && (
        <motion.div initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }}
          className='p-6 rounded-2xl bg-slate-900/60 border border-slate-800 mb-10 max-w-md mx-auto text-center'>
          <p className='text-sm text-slate-400 mb-2'>Your Usage</p>
          {usage.is_paid ? (
            <p className='text-emerald-400 font-semibold'>Pro Plan - Unlimited scans</p>
          ) : (
            <>
              <p className='text-3xl font-bold text-slate-100'>{usage.remaining} <span className='text-lg text-slate-400'>/ {usage.free_limit}</span></p>
              <p className='text-sm text-slate-500 mt-1'>free scans remaining</p>
              {(usage.remaining || 0) <= 0 && <p className='text-amber-400 text-xs mt-2'>All free scans used. Upgrade to Pro!</p>}
            </>
          )}
        </motion.div>
      )}

      <div className='grid grid-cols-1 md:grid-cols-3 gap-6 mb-16'>
        {plans.map((plan, i) => (
          <motion.div key={plan.name} initial={{ opacity: 0, y: 20 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: 0.1 * i }}
            className={'p-8 rounded-2xl border relative ' + (plan.popular ? 'bg-gradient-to-b from-purple-900/30 to-slate-900/60 border-purple-500/30' : 'bg-slate-900/60 border-slate-800')}>
            {plan.popular && <div className='absolute -top-3 left-1/2 -translate-x-1/2 px-4 py-1 rounded-full bg-gradient-to-r from-purple-500 to-cyan-500 text-white text-xs font-semibold'>Most Popular</div>}
            <h3 className='text-lg font-semibold text-slate-200 mb-2'>{plan.name}</h3>
            <div className='mb-4'>
              <span className='text-4xl font-bold text-slate-100'>{plan.price}</span>
              <span className='text-slate-400 text-sm ml-1'>{plan.period}</span>
            </div>
            <p className='text-sm text-cyan-400 mb-6 font-medium'>{plan.scans}</p>
            <ul className='space-y-3 mb-8'>
              {plan.features.map(f => (
                <li key={f} className='flex items-start gap-2 text-sm text-slate-300'>
                  <CheckCircle2 className='w-4 h-4 text-emerald-400 flex-shrink-0 mt-0.5' />{f}
                </li>
              ))}
            </ul>
            <button disabled={plan.name === 'Free' || plan.name === 'Team'}
              className={'w-full py-3 rounded-xl text-sm font-semibold transition-all ' + (plan.popular ? 'bg-gradient-to-r from-purple-500 to-cyan-500 text-white' : 'bg-slate-800 text-slate-300') + (plan.name === 'Team' ? ' opacity-50 cursor-not-allowed' : '')}>
              {plan.cta}
            </button>
            {plan.name === 'Pro' && <p className='text-xs text-slate-500 text-center mt-2'>Less than $7/month!</p>}
          </motion.div>
        ))}
      </div>

      <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} className='grid grid-cols-1 md:grid-cols-4 gap-6 text-center'>
        {[{ icon: Cpu, label: 'Smart Scanning', desc: 'Skip binaries, large files' },
          { icon: Shield, label: 'Health Score', desc: 'AI-graded A-F health' },
          { icon: Brain, label: 'AI Insights', desc: 'LLM-powered review' },
          { icon: Download, label: 'Reports', desc: 'Downloadable HTML' }
        ].map(({ icon: Icon, label, desc }) => (
          <div key={label} className='p-5 rounded-2xl bg-slate-900/40 border border-slate-800/50'>
            <div className='w-10 h-10 rounded-xl bg-cyan-500/10 border border-cyan-500/20 mx-auto flex items-center justify-center mb-3'>
              <Icon className='w-5 h-5 text-cyan-400' />
            </div>
            <p className='text-sm font-medium text-slate-200'>{label}</p>
            <p className='text-xs text-slate-500 mt-1'>{desc}</p>
          </div>
        ))}
      </motion.div>
    </div>
  );
}